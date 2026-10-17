/*!
 * rig-optimize.js — draw-call budget for the Anshita mascot rigs (audit §8.2).
 *
 * A photoreal mascot is built from dozens of small primitives (ear shells,
 * pom-pom tufts, catchlights, sleeve trims…). Left alone those become one
 * draw call each and blow the <25-call gate. This module bakes every mesh that
 * shares a material *and* an identical animated-ancestor chain into a single
 * BufferGeometry, so the rig keeps its exact motion but renders in a fraction
 * of the calls.
 *
 * Safety rules (motion is never changed):
 *   - only meshes with the same material + the same chain of animated
 *     ancestors are candidates, so an ear is never welded to a foot;
 *   - geometry is transformed into the deepest common ancestor's space, so
 *     every parent transform still applies exactly as before;
 *   - skinned meshes, morph targets and anything flagged `userData.noMerge`
 *     (e.g. the mouth, whose geometry is rebuilt per mood) are left alone.
 */
(function (window) {
  'use strict';

  var THREE = window.THREE;
  if (!THREE) return;

  function chainToRoot(node) {
    var out = [];
    var n = node;
    while (n) { out.unshift(n); n = n.parent; }
    return out;
  }

  /** Deepest node that is an ancestor of (or equal to) every given node. */
  function deepestCommonAncestor(nodes) {
    if (!nodes.length) return null;
    var chains = nodes.map(chainToRoot);
    var depth = chains[0].length;
    var ancestor = chains[0][0];
    for (var d = 0; d < depth; d++) {
      var candidate = chains[0][d];
      for (var i = 1; i < chains.length; i++) {
        if (chains[i].length <= d || chains[i][d] !== candidate) return ancestor;
      }
      ancestor = candidate;
    }
    return ancestor;
  }

  /**
   * Merge a list of meshes (which must all be children of `parent`) sharing one
   * material into a single mesh. Used directly by rig builders for decorative
   * clusters.
   */
  function mergeMeshes(parent, meshes, material) {
    if (!parent || !meshes || meshes.length < 2 || !material) return null;
    var positions = [], normals = [], indices = [], vertexOffset = 0, hasNormals = true;
    var castShadow = false, receiveShadow = false;
    var seen = new Set();
    var normalMatrix = new THREE.Matrix3();
    var v = new THREE.Vector3();
    for (var m = 0; m < meshes.length; m++) {
      var mesh = meshes[m];
      var geom = mesh.geometry;
      if (!geom || !geom.attributes || !geom.attributes.position) return null;
      mesh.updateMatrix();
      var posAttr = geom.attributes.position;
      for (var i = 0; i < posAttr.count; i++) {
        v.fromBufferAttribute(posAttr, i).applyMatrix4(mesh.matrix);
        positions.push(v.x, v.y, v.z);
      }
      var nrmAttr = geom.attributes.normal;
      if (nrmAttr) {
        normalMatrix.getNormalMatrix(mesh.matrix);
        for (var j = 0; j < nrmAttr.count; j++) {
          v.fromBufferAttribute(nrmAttr, j).applyNormalMatrix(normalMatrix).normalize();
          normals.push(v.x, v.y, v.z);
        }
      } else {
        hasNormals = false;
      }
      var count = posAttr.count;
      if (geom.index) {
        for (var k = 0; k < geom.index.count; k++) indices.push(geom.index.array[k] + vertexOffset);
      } else {
        for (var f = 0; f < count; f++) indices.push(f + vertexOffset);
      }
      vertexOffset += count;
      castShadow = castShadow || mesh.castShadow;
      receiveShadow = receiveShadow || mesh.receiveShadow;
      parent.remove(mesh);
      if (!seen.has(geom.uuid)) { seen.add(geom.uuid); geom.dispose(); }
    }
    var merged = new THREE.BufferGeometry();
    merged.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
    if (hasNormals && normals.length === positions.length) {
      merged.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
    } else {
      merged.computeVertexNormals();
    }
    merged.setIndex(indices);
    merged.computeBoundingSphere();
    var out = new THREE.Mesh(merged, material);
    out.castShadow = castShadow;
    out.receiveShadow = receiveShadow;
    out.name = 'merged-' + (material.name || material.type || 'material');
    out.userData.mergedFrom = meshes.length;
    parent.add(out);
    return out;
  }

  /**
   * Merge meshes that belong to one *colour family* (e.g. the matte plush
   * palette: fur, cream, chest, pink) and share an animated-ancestor chain,
   * baking each mesh's colour into vertex colours so the palette survives.
   * PBR nuance between family members (a few percent of roughness) is
   * averaged into one shared material — invisible on matte plush surfaces,
   * worth several draw calls.
   */
  function mergeMaterialFamily(root, materials, animatedNodes, options) {
    if (!root || !materials || materials.length < 2) return 0;
    options = options || {};
    var family = new Set(materials);
    var animated = [];
    (animatedNodes || []).forEach(function (n) { if (n) animated.push(n); });
    var animatedSet = new Set(animated);
    var order = new Map();
    animated.forEach(function (n, i) { order.set(n, i); });

    function chainKey(mesh) {
      var ids = [];
      var node = mesh.parent;
      while (node) {
        if (animatedSet.has(node)) ids.push(order.get(node));
        node = node.parent;
      }
      return ids.reverse().join('.');
    }

    // Canonical material = the one covering the most vertices (keeps the
    // dominant surface reading identical to the un-merged rig).
    var weight = new Map();
    root.traverse(function (o) {
      if (!o.isMesh || animatedSet.has(o) || !family.has(o.material)) return;
      if (!o.geometry || !o.geometry.attributes.position) return;
      var w = o.geometry.attributes.position.count;
      weight.set(o.material, (weight.get(o.material) || 0) + w);
    });
    if (!weight.size) return 0;
    var canonical = materials[0], best = -1;
    weight.forEach(function (w, mat) { if (w > best) { best = w; canonical = mat; } });

    root.updateMatrixWorld(true);
    var buckets = new Map();
    root.traverse(function (o) {
      if (!o.isMesh || o.isSkinnedMesh || Array.isArray(o.material)) return;
      if (animatedSet.has(o) || !family.has(o.material)) return;
      if (!o.geometry || !o.geometry.attributes || !o.geometry.attributes.position) return;
      if (o.userData && o.userData.noMerge) return;
      if (o.material.transparent || o.material.emissive && o.material.emissive.getHex()) return;
      var key = chainKey(o);
      var bucket = buckets.get(key);
      if (!bucket) { bucket = { meshes: [] }; buckets.set(key, bucket); }
      bucket.meshes.push(o);
    });

    var shared = canonical.clone();
    shared.vertexColors = true;
    shared.color = new THREE.Color(0xffffff);
    if (canonical.transparent) shared.transparent = false;
    // Weighted-average the PBR nuance so no single family member's finish is
    // imposed on the others (sheen tint stays with the canonical material).
    var totalW = 0, acc = { roughness: 0, metalness: 0, clearcoat: 0, clearcoatRoughness: 0 };
    weight.forEach(function (w, mat) {
      totalW += w;
      ['roughness', 'metalness', 'clearcoat', 'clearcoatRoughness'].forEach(function (key) {
        if (typeof mat[key] === 'number') acc[key] += mat[key] * w;
      });
    });
    if (totalW > 0) {
      ['roughness', 'metalness', 'clearcoat', 'clearcoatRoughness'].forEach(function (key) {
        if (typeof shared[key] === 'number') shared[key] = acc[key] / totalW;
      });
    }
    shared.name = 'family-' + (options.name || 'merged');
    shared.needsUpdate = true;

    var inverse = new THREE.Matrix4();
    var normalMatrix = new THREE.Matrix3();
    var v = new THREE.Vector3();
    var saved = 0;

    buckets.forEach(function (bucket) {
      var meshes = bucket.meshes;
      if (meshes.length < 2) return;
      // Only merge when the family actually consolidates calls.
      var anchor = deepestCommonAncestor(meshes);
      if (!anchor) return;
      inverse.copy(anchor.matrixWorld).invert();

      var positions = [], normals = [], colors = [], indices = [], vertexOffset = 0, hasNormals = true;
      var castShadow = false, receiveShadow = false, seen = new Set(), removable = [];
      for (var m = 0; m < meshes.length; m++) {
        var mesh = meshes[m];
        var geom = mesh.geometry;
        var rel = new THREE.Matrix4().multiplyMatrices(inverse, mesh.matrixWorld);
        var posAttr = geom.attributes.position;
        for (var i = 0; i < posAttr.count; i++) {
          v.fromBufferAttribute(posAttr, i).applyMatrix4(rel);
          positions.push(v.x, v.y, v.z);
          colors.push(mesh.material.color.r, mesh.material.color.g, mesh.material.color.b);
        }
        var nrmAttr = geom.attributes.normal;
        if (nrmAttr) {
          normalMatrix.getNormalMatrix(rel);
          for (var j = 0; j < nrmAttr.count; j++) {
            v.fromBufferAttribute(nrmAttr, j).applyNormalMatrix(normalMatrix).normalize();
            normals.push(v.x, v.y, v.z);
          }
        } else { hasNormals = false; }
        var count = posAttr.count;
        if (geom.index) {
          for (var k = 0; k < geom.index.count; k++) indices.push(geom.index.array[k] + vertexOffset);
        } else {
          for (var f = 0; f < count; f++) indices.push(f + vertexOffset);
        }
        vertexOffset += count;
        castShadow = castShadow || mesh.castShadow;
        receiveShadow = receiveShadow || mesh.receiveShadow;
        removable.push(mesh);
      }

      var merged = new THREE.BufferGeometry();
      merged.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
      if (hasNormals && normals.length === positions.length) {
        merged.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
      } else {
        merged.computeVertexNormals();
      }
      merged.setAttribute('color', new THREE.Float32BufferAttribute(colors, 3));
      merged.setIndex(indices);
      merged.computeBoundingSphere();

      var out = new THREE.Mesh(merged, shared);
      out.castShadow = castShadow;
      out.receiveShadow = receiveShadow;
      out.name = 'family-' + meshes.length;
      out.userData.mergedFrom = meshes.length;
      anchor.add(out);

      removable.forEach(function (mesh) {
        if (mesh.parent) mesh.parent.remove(mesh);
        var g = mesh.geometry;
        if (g && !seen.has(g.uuid)) { seen.add(g.uuid); g.dispose(); }
      });
      saved += meshes.length - 1;
    });

    return saved;
  }

  /**
   * Merge every static mesh in `root` that shares a material and an identical
   * chain of animated ancestors.
   *
   * @param {THREE.Object3D} root
   * @param {THREE.Object3D[]} animatedNodes nodes the rig mutates each frame
   *        (root, body, head rig, ears, feet, eyes, arm pivots…). Meshes below
   *        different chains are never merged, so nothing visually moves
   *        differently afterwards.
   * @returns {number} how many draw calls were saved
   */
  function mergeStaticByMaterial(root, animatedNodes) {
    if (!root) return 0;
    var animated = [];
    (animatedNodes || []).forEach(function (n) { if (n) animated.push(n); });
    var animatedSet = new Set(animated);
    var order = new Map();
    animated.forEach(function (n, i) { order.set(n, i); });

    function chainKey(mesh) {
      var ids = [];
      var node = mesh.parent;
      while (node) {
        if (animatedSet.has(node)) ids.push(order.get(node));
        node = node.parent;
      }
      ids.reverse();
      return ids.join('.');
    }

    root.updateMatrixWorld(true);

    var buckets = new Map();
    root.traverse(function (o) {
      if (!o.isMesh || o.isSkinnedMesh || Array.isArray(o.material)) return;
      // A mesh the rig animates directly (tail feathers, crest plumes…) is
      // never a merge candidate.
      if (animatedSet.has(o)) return;
      if (!o.geometry || !o.geometry.attributes || !o.geometry.attributes.position) return;
      if (o.morphTargetInfluences && o.morphTargetInfluences.length) return;
      if (o.userData && o.userData.noMerge) return;
      var key = o.material.uuid + '|' + chainKey(o);
      var bucket = buckets.get(key);
      if (!bucket) { bucket = { material: o.material, meshes: [] }; buckets.set(key, bucket); }
      bucket.meshes.push(o);
    });

    var saved = 0;
    var inverse = new THREE.Matrix4();
    var normalMatrix = new THREE.Matrix3();
    var v = new THREE.Vector3();

    buckets.forEach(function (bucket) {
      var meshes = bucket.meshes;
      if (meshes.length < 2) return;

      var anchor = deepestCommonAncestor(meshes);
      if (!anchor) return;
      inverse.copy(anchor.matrixWorld).invert();

      var positions = [], normals = [], indices = [], vertexOffset = 0, hasNormals = true;
      var castShadow = false, receiveShadow = false;
      var seen = new Set();
      var removable = [];

      for (var m = 0; m < meshes.length; m++) {
        var mesh = meshes[m];
        var geom = mesh.geometry;
        var rel = new THREE.Matrix4().multiplyMatrices(inverse, mesh.matrixWorld);
        var posAttr = geom.attributes.position;
        for (var i = 0; i < posAttr.count; i++) {
          v.fromBufferAttribute(posAttr, i).applyMatrix4(rel);
          positions.push(v.x, v.y, v.z);
        }
        var nrmAttr = geom.attributes.normal;
        if (nrmAttr) {
          normalMatrix.getNormalMatrix(rel);
          for (var j = 0; j < nrmAttr.count; j++) {
            v.fromBufferAttribute(nrmAttr, j).applyNormalMatrix(normalMatrix).normalize();
            normals.push(v.x, v.y, v.z);
          }
        } else {
          hasNormals = false;
        }
        var count = posAttr.count;
        if (geom.index) {
          for (var k = 0; k < geom.index.count; k++) indices.push(geom.index.array[k] + vertexOffset);
        } else {
          for (var f = 0; f < count; f++) indices.push(f + vertexOffset);
        }
        vertexOffset += count;
        castShadow = castShadow || mesh.castShadow;
        receiveShadow = receiveShadow || mesh.receiveShadow;
        removable.push(mesh);
      }

      var merged = new THREE.BufferGeometry();
      merged.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
      if (hasNormals && normals.length === positions.length) {
        merged.setAttribute('normal', new THREE.Float32BufferAttribute(normals, 3));
      } else {
        merged.computeVertexNormals();
      }
      merged.setIndex(indices);
      merged.computeBoundingSphere();

      var out = new THREE.Mesh(merged, bucket.material);
      out.castShadow = castShadow;
      out.receiveShadow = receiveShadow;
      out.name = 'merged-' + meshes.length + '-' + (bucket.material.name || bucket.material.type || 'mesh');
      out.userData.mergedFrom = meshes.length;
      anchor.add(out);

      removable.forEach(function (mesh) {
        if (mesh.parent) mesh.parent.remove(mesh);
        var g = mesh.geometry;
        if (g && !seen.has(g.uuid)) { seen.add(g.uuid); g.dispose(); }
      });

      saved += meshes.length - 1;
      if (!root.userData.drawCallMerge) root.userData.drawCallMerge = { groups: 0, saved: 0 };
      root.userData.drawCallMerge.groups++;
      root.userData.drawCallMerge.saved += meshes.length - 1;
    });

    return saved;
  }

  window.AnshitaRigOptimizer = {
    mergeMeshes: mergeMeshes,
    mergeStaticByMaterial: mergeStaticByMaterial,
    mergeMaterialFamily: mergeMaterialFamily,
    deepestCommonAncestor: deepestCommonAncestor,
  };
})(typeof window !== 'undefined' ? window : this);
