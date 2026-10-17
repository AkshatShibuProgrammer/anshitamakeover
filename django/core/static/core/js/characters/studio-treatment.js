/*!
 * studio-treatment.js — the rendering treatment that makes the concierge rigs
 * look like the reference studio instead of flat primitives.
 *
 * The Mochi/Pip geometry is already the studio's own (ported from their
 * index-expressions.html — their patch_mochi_pip.py fixes are in our rigs).
 * What was missing was everything *around* the geometry:
 *
 *   1. linear-space colour      — every authored sRGB hex must pass through
 *                                 convertSRGBToLinear(), or surfaces wash out
 *                                 (three r128 has no colour management);
 *   2. a filmic pipeline        — ACES tone mapping + sRGB output, otherwise
 *                                 highlights clip and the velvet reads chalky;
 *   3. an environment           — PMREM-probed studio env so MeshPhysical
 *                                 clearcoat/sheen have something to reflect;
 *   4. a real 6-light rig       — warm key (shadow-casting) + cool fill +
 *                                 hot rim + cool rim + floor bounce + hemi;
 *   5. contact shadows          — a soft shadow catcher so the character sits
 *                                 on the runway instead of floating.
 *
 * Everything here is defensive: a missing capability (no PMREM, no WebGL2,
 * no shadow support) degrades to the next best thing rather than throwing.
 */
(function (window) {
  'use strict';

  var THREE = window.THREE;
  if (!THREE) return;

  /** Authored sRGB hex → linear colour (the studio's LC()). */
  function LC(hex) {
    return new THREE.Color(hex).convertSRGBToLinear();
  }

  /** Apply the filmic pipeline to a renderer (idempotent). */
  function applyRendererPipeline(renderer, options) {
    if (!renderer) return renderer;
    options = options || {};
    if (THREE.sRGBEncoding !== undefined) renderer.outputEncoding = THREE.sRGBEncoding;
    if (THREE.ACESFilmicToneMapping !== undefined) {
      renderer.toneMapping = THREE.ACESFilmicToneMapping;
      renderer.toneMappingExposure = options.exposure === undefined ? 1.05 : options.exposure;
    }
    if (renderer.shadowMap) {
      renderer.shadowMap.enabled = options.shadows !== false;
      if (THREE.PCFSoftShadowMap !== undefined) renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    }
    if (renderer.physicallyCorrectLights !== undefined) renderer.physicallyCorrectLights = true;
    return renderer;
  }

  /**
   * Build a procedural studio environment map.
   *
   * Painted as a canvas equirect (a warm overhead pool, a cool floor bounce and
   * a bright rim streak) then run through PMREMGenerator so roughness-mapped
   * materials get properly pre-filtered reflections. Returns null when the
   * browser cannot do it — callers then skip env assignment.
   */
  function buildStudioEnvironment(renderer) {
    if (!renderer || !THREE.PMREMGenerator) return null;
    try {
      var canvas = document.createElement('canvas');
      canvas.width = 512;
      canvas.height = 256;
      var ctx = canvas.getContext('2d');

      var sky = ctx.createLinearGradient(0, 0, 0, canvas.height);
      sky.addColorStop(0.00, '#241019');
      sky.addColorStop(0.42, '#150a12');
      sky.addColorStop(0.55, '#2a1a12');
      sky.addColorStop(1.00, '#0a0409');
      ctx.fillStyle = sky;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Overhead warm pool directly above the character.
      var pool = ctx.createRadialGradient(256, 42, 6, 256, 42, 150);
      pool.addColorStop(0, 'rgba(255, 226, 178, 0.98)');
      pool.addColorStop(0.45, 'rgba(255, 196, 132, 0.42)');
      pool.addColorStop(1, 'rgba(255, 180, 120, 0)');
      ctx.fillStyle = pool;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Cool bounce from camera-left, gold rim from behind.
      var cool = ctx.createRadialGradient(120, 150, 4, 120, 150, 130);
      cool.addColorStop(0, 'rgba(168, 198, 255, 0.45)');
      cool.addColorStop(1, 'rgba(168, 198, 255, 0)');
      ctx.fillStyle = cool;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      var rim = ctx.createRadialGradient(392, 120, 4, 392, 120, 110);
      rim.addColorStop(0, 'rgba(255, 214, 150, 0.62)');
      rim.addColorStop(1, 'rgba(255, 214, 150, 0)');
      ctx.fillStyle = rim;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      var texture = new THREE.CanvasTexture(canvas);
      texture.mapping = THREE.EquirectangularReflectionMapping;
      if (THREE.sRGBEncoding !== undefined) texture.encoding = THREE.sRGBEncoding;

      var pmrem = new THREE.PMREMGenerator(renderer);
      if (pmrem.compileEquirectangularShader) pmrem.compileEquirectangularShader();
      var target = pmrem.fromEquirectangular(texture);
      texture.dispose();
      pmrem.dispose();
      return target ? target.texture : null;
    } catch (err) {
      if (window.console) console.warn('[StudioTreatment] env probe failed, continuing without env', err);
      return null;
    }
  }

  /**
   * Install the studio light rig. Returns the live lights so callers can tune
   * them (and so destroy() can remove them).
   */
  function createStudioLights(scene, options) {
    options = options || {};
    var shadows = options.shadows !== false;
    var unit = options.scale || 1;      // rig is authored around a ~2m character
    var lights = {};

    lights.hemi = new THREE.HemisphereLight(LC(0x3a4763), LC(0x120c08), 0.38);
    lights.hemi.position.set(0, 3 * unit, 0);
    scene.add(lights.hemi);

    lights.key = new THREE.DirectionalLight(LC(0xffd7a2), 2.20);
    lights.key.position.set(2.7 * unit, 3.7 * unit, 3.3 * unit);
    lights.key.castShadow = shadows;
    if (shadows && lights.key.shadow) {
      lights.key.shadow.mapSize.set(1024, 1024);
      lights.key.shadow.camera.near = 0.5 * unit;
      lights.key.shadow.camera.far = 14 * unit;
      lights.key.shadow.bias = -0.0012;
      lights.key.shadow.normalBias = 0.02 * unit;
    }
    scene.add(lights.key);
    if (lights.key.target) { lights.key.target.position.set(0, unit, 0); scene.add(lights.key.target); }

    lights.fill = new THREE.DirectionalLight(LC(0x9fb4ff), 0.50);
    lights.fill.position.set(-3.4 * unit, 1.5 * unit, 2.6 * unit);
    scene.add(lights.fill);

    lights.rim = new THREE.DirectionalLight(LC(0xffb066), 1.15);
    lights.rim.position.set(-1.1 * unit, 2.6 * unit, -3.4 * unit);
    scene.add(lights.rim);

    lights.rimCool = new THREE.DirectionalLight(LC(0x8fd8ff), 0.42);
    lights.rimCool.position.set(2.9 * unit, 1.6 * unit, -2.4 * unit);
    scene.add(lights.rimCool);

    lights.bounce = new THREE.DirectionalLight(LC(0xffc9a0), 0.30);
    lights.bounce.position.set(0, -2.2 * unit, 1.6 * unit);
    scene.add(lights.bounce);

    return lights;
  }

  /**
   * A soft contact-shadow catcher: an invisible plane that only receives the
   * key light's shadow, giving the character a grounded pool of darkness.
   */
  function createShadowCatcher(options) {
    options = options || {};
    var size = options.size || 10;
    var geometry = new THREE.PlaneGeometry(size, size);
    var material = new THREE.ShadowMaterial({ opacity: options.opacity === undefined ? 0.34 : options.opacity });
    var mesh = new THREE.Mesh(geometry, material);
    mesh.rotation.x = -Math.PI / 2;
    mesh.position.y = options.y === undefined ? 0 : options.y;
    mesh.receiveShadow = true;
    mesh.name = 'studio-shadow-catcher';
    return mesh;
  }

  /**
   * Convert every authored colour on a scene graph to linear space.
   * Rig builders author plain sRGB hexes; without this pass every surface is
   * rendered as if it were already linear, which desaturates and blows out.
   */
  function lineariseMaterials(root, seen) {
    seen = seen || new Set();
    if (!root || !root.traverse) return 0;
    var converted = 0;
    root.traverse(function (object) {
      if (!(object.isMesh || object.isPoints || object.isLine)) return;
      var materials = Array.isArray(object.material) ? object.material : [object.material];
      materials.forEach(function (material) {
        if (!material || seen.has(material.uuid)) return;
        seen.add(material.uuid);
        // A vertex-coloured family material carries colour per-vertex, already
        // authored in the same space as its sources — leave both alone.
        if (material.vertexColors) return;
        ['color', 'emissive', 'sheenColor', 'specularColor'].forEach(function (slot) {
          if (material[slot] && material[slot].isColor) {
            material[slot].convertSRGBToLinear();
          }
        });
        material.needsUpdate = true;
        converted++;
      });
    });
    return converted;
  }

  window.StudioTreatment = {
    LC: LC,
    applyRendererPipeline: applyRendererPipeline,
    buildStudioEnvironment: buildStudioEnvironment,
    createStudioLights: createStudioLights,
    createShadowCatcher: createShadowCatcher,
    lineariseMaterials: lineariseMaterials
  };
})(typeof window !== 'undefined' ? window : this);
