/**
 * lumiere-characters.js
 * Extracted 3D procedural characters (Mochi, Pip, Asha) with lip-sync patches and emotion rigs for Anshita Makeover.
 */
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['three'], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory(require('three'));
  } else {
    root.LumiereCharacters = factory(root.THREE);
  }
}(typeof self !== 'undefined' ? self : this, function (THREE) {
  'use strict';
  if (!THREE) {
    console.error('LumiereCharacters requires Three.js r128.');
    return null;
  }

    const G = window.gsap || null;
    const REDUCED = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

    const GOLD = 0xc8a96a;
    const FLOOR_Y = 0.105;
    const lerp = (a, b, t) => a + (b - a) * t;
    const clamp = (v, a, b) => Math.max(a, Math.min(b, v));
    const vec = (x, y, z) => new THREE.Vector3(x, y, z);
    const colorMat = (color, options = {}) => new THREE.MeshPhysicalMaterial(Object.assign({
      color: color, roughness: .48, metalness: 0, clearcoat: .16, clearcoatRoughness: .48,
      envMapIntensity: .85
    }, options));
    const standardMat = (color, options = {}) => new THREE.MeshStandardMaterial(Object.assign({
      color: color, roughness: .55, metalness: 0, envMapIntensity: .7
    }, options));
    const goldMat = () => colorMat(0xc8a96a, { metalness: .95, roughness: .25, clearcoat: .8, clearcoatRoughness: .15 });
    const gemMat = (color) => colorMat(color, { metalness: .12, roughness: .12, clearcoat: 1, clearcoatRoughness: .06 });

    function addMesh(parent, geometry, material, position, scale) {
      const object = new THREE.Mesh(geometry, material);
      if (position) object.position.set(position[0], position[1], position[2]);
      if (scale) object.scale.set(scale[0], scale[1], scale[2]);
      object.castShadow = true;
      object.receiveShadow = true;
      parent.add(object);
      return object;
    }
    function sphere(parent, material, position, scale, segments = 24) {
      return addMesh(parent, new THREE.SphereGeometry(1, segments, Math.max(12, Math.floor(segments * .7))), material, position, scale);
    }
    function cylinder(parent, material, position, radiusTop, radiusBottom, height, segments = 20) {
      return addMesh(parent, new THREE.CylinderGeometry(radiusTop, radiusBottom, height, segments), material, position);
    }
    function lathe(parent, material, points, segments = 40) {
      const geometry = new THREE.LatheGeometry(points.map(p => new THREE.Vector2(p[0], p[1])), segments);
      return addMesh(parent, geometry, material);
    }
    function tube(parent, points, radius, material, radialSegments = 8) {
      const curve = new THREE.CatmullRomCurve3(points.map(p => vec(p[0], p[1], p[2])));
      return addMesh(parent, new THREE.TubeGeometry(curve, Math.max(18, points.length * 8), radius, radialSegments, false), material);
    }
    function ribbon(parent, points, width, material, segments = 40) {
      const curve = new THREE.CatmullRomCurve3(points.map(p => vec(p[0], p[1], p[2])));
      const samples = curve.getPoints(segments);
      const positions = [];
      const indices = [];
      for (let i = 0; i < samples.length; i++) {
        const tangent = (i < samples.length - 1 ? samples[i + 1].clone().sub(samples[i]) : samples[i].clone().sub(samples[i - 1])).normalize();
        const side = new THREE.Vector3().crossVectors(tangent, vec(0, 0, 1));
        if (side.lengthSq() < .0001) side.set(1, 0, 0);
        side.normalize().multiplyScalar(width / 2);
        positions.push(samples[i].x - side.x, samples[i].y - side.y, samples[i].z - side.z);
        positions.push(samples[i].x + side.x, samples[i].y + side.y, samples[i].z + side.z);
      }
      for (let i = 0; i < samples.length - 1; i++) {
        const a = i * 2;
        indices.push(a, a + 1, a + 2, a + 1, a + 3, a + 2);
      }
      const geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
      geometry.setIndex(indices);
      geometry.computeVertexNormals();
      const cloth = material.clone();
      cloth.side = THREE.DoubleSide;
      return addMesh(parent, geometry, cloth);
    }
    function eyePair(parent, options = {}) {
      const settings = Object.assign({ x: .105, y: .035, z: .24, radius: .07, iris: 0x39251b, dark: false }, options);
      const eyes = [];
      [-1, 1].forEach(side => {
        const eye = new THREE.Group();
        eye.position.set(side * settings.x, settings.y, settings.z);
        eye.rotation.y = side * 0.07;
        eye.rotation.z = side * -0.015;
        parent.add(eye);

        const r = settings.radius;
        // 1. Soft glossy porcelain sclera: wider than tall to prevent startled vertical oval look
        const baseMat = settings.dark
          ? colorMat(0x101018, { roughness: .04, clearcoat: 1, clearcoatRoughness: .02, envMapIntensity: 1.8 })
          : colorMat(0xfff8ee, { roughness: .14, clearcoat: 1, clearcoatRoughness: .04, envMapIntensity: 1.2 });
        sphere(eye, baseMat, [0, 0, 0], [r * 1.15, r * 0.98, r * 0.56], 28);

        const irisGroup = new THREE.Group();
        eye.add(irisGroup);
        irisGroup.position.set(0, -0.002, r * 0.44);

        if (!settings.dark) {
          // Large sweet doe-eyed iris occupying ~88% of vertical eye height
          const irR = r * 0.88;
          sphere(irisGroup, colorMat(settings.iris, { roughness: .10, clearcoat: 1, clearcoatRoughness: .03, envMapIntensity: 1.8 }), [0, 0, 0.008], [irR * 0.96, irR * 1.02, 0.04], 22);

          // Limbal ring (classic beauty mark in anime & Disney character art)
          const limbal = addMesh(irisGroup, new THREE.TorusGeometry(irR * 0.96, 0.004, 8, 32), standardMat(0x110b0e, { roughness: .2 }));
          limbal.position.z = 0.014;

          // Soft golden interior shimmer ring
          const irisRing = addMesh(irisGroup, new THREE.TorusGeometry(irR * 0.62, 0.0035, 8, 24), colorMat(0xe8c97a, { roughness: .1, emissive: 0xe8c97a, emissiveIntensity: 0.35 }));
          irisRing.position.z = 0.018;

          // Inner deep obsidian pupil
          sphere(irisGroup, standardMat(0x080608, { roughness: .05 }), [0, 0, 0.022], [irR * 0.52, irR * 0.55, 0.025], 18);

          // Triple high-contrast anime catchlights
          const catchMat = colorMat(0xffffff, { roughness: .01, clearcoat: 1, emissive: 0xffffff, emissiveIntensity: 1.0 });
          // Primary big sparkle (top-left)
          const c1 = sphere(irisGroup, catchMat, [-irR * 0.30, irR * 0.32, 0.038], [irR * 0.32, irR * 0.34, 0.018], 14);
          c1.castShadow = false;
          // Secondary soft sparkle (bottom-right)
          const c2 = sphere(irisGroup, catchMat, [irR * 0.32, -irR * 0.24, 0.035], [irR * 0.16, irR * 0.16, 0.014], 12);
          c2.castShadow = false;
          // Micro sparkle accent
          const c3 = sphere(irisGroup, catchMat, [irR * 0.22, irR * 0.38, 0.035], [irR * 0.09, irR * 0.09, 0.012], 10);
          c3.castShadow = false;

          // Lush soft upper lash line hugging top of eye
          const linerM = standardMat(0x140e12, { roughness: .3 });
          const topPts = [
            [-r * 1.18, -r * 0.15, r * 0.42],
            [-r * 0.62,  r * 0.72, r * 0.55],
            [ 0,         r * 0.88, r * 0.58],
            [ r * 0.62,  r * 0.72, r * 0.55],
            [ r * 1.18, -r * 0.12, r * 0.42]
          ];
          tube(eye, topPts, 0.007, linerM, 6);

          // Subtle winged flick
          const wingDir = side > 0 ? 1 : -1;
          const wingPts = [
            [wingDir * r * 1.12, -r * 0.05, r * 0.42],
            [wingDir * r * 1.38,  r * 0.18, r * 0.38],
            [wingDir * r * 1.60,  r * 0.35, r * 0.34]
          ];
          tube(eye, wingPts, 0.005, linerM, 6);
        } else {
          // Boba plush eye for Mochi with big glossy catchlights
          sphere(irisGroup, colorMat(0x101018, { roughness: .04, clearcoat: 1, envMapIntensity: 2.0 }), [0, 0, 0.01], [r * 1.25, r * 1.32, 0.18], 22);
          const bobaCatch = colorMat(0xffffff, { roughness: .01, clearcoat: 1, emissive: 0xffffff, emissiveIntensity: 1.0 });
          const bc1 = sphere(irisGroup, bobaCatch, [-r * 0.45, r * 0.48, 0.18], [r * 0.45, r * 0.48, 0.12], 14);
          bc1.castShadow = false;
          const bc2 = sphere(irisGroup, bobaCatch, [r * 0.45, -r * 0.32, 0.17], [r * 0.22, r * 0.22, 0.10], 12);
          bc2.castShadow = false;
          const bc3 = sphere(irisGroup, bobaCatch, [r * 0.32, r * 0.52, 0.17], [r * 0.13, r * 0.13, 0.08], 10);
          bc3.castShadow = false;
        }

        eyes.push({ eye: eye, iris: irisGroup, baseY: eye.scale.y });
      });
      const api = { moodValue: 1, eyes: eyes };
      return Object.assign(api, {
        gaze(x, y) { eyes.forEach(e => { e.iris.position.x = x * .018; e.iris.position.y = -y * .014; }); },
        blink() {
          /* reopen to the CURRENT mood, not 1 — blinking used to wipe the
             squint every couple of seconds */
          const restore = api.moodValue;
          eyes.forEach(e => {
            if (G) G.timeline()
              .to(e.eye.scale, { y: .09, duration: .075, ease: 'power2.in' })
              .to(e.eye.scale, { y: restore, duration: .14, ease: 'power2.out' });
            else e.eye.scale.y = restore;
          });
        },
        mood(value) {
          const v = (typeof value === 'number') ? value : (value ? .9 : 1);
          api.moodValue = v;
          eyes.forEach(e => {
            if (G) G.to(e.eye.scale, { y: v, duration: .4, ease: 'power2.out', overwrite: true });
            else e.eye.scale.y = v;
          });
        },
        /* One eye only. Reopens to the CURRENT mood so a wink does not wipe
           the squint the expression just set. */
        wink(side) {
          const e = eyes[side < 0 ? 0 : 1];
          if (!e || !G) return;
          G.timeline()
            .to(e.eye.scale, { y: .10, duration: .14, ease: 'power2.in', overwrite: true }, 0)
            .to(e.eye.scale, { y: api.moodValue, duration: .24, ease: 'power2.out' }, .62);
        }
      });
    }
    /* TubeGeometry can only sweep a CONSTANT radius, which makes a mouth read
       as a bent wire rather than as lips. This sweeps a variable radius so the
       smile is fat through the middle and drawn to a fine point at each
       corner -- that taper is most of what makes a smile look "cute". */
    function taperedTube(curve, tubularSegments, radiusFn, radialSegments) {
      const frames = curve.computeFrenetFrames(tubularSegments, false);
      const pos = [], nor = [], uvs = [], idx = [];
      const P = new THREE.Vector3(), N = new THREE.Vector3();
      for (let i = 0; i <= tubularSegments; i++) {
        const t = i / tubularSegments;
        curve.getPointAt(t, P);
        const r = Math.max(.0008, radiusFn(t));
        const Bi = frames.binormals[i], Ni = frames.normals[i];
        for (let j = 0; j <= radialSegments; j++) {
          const v = j / radialSegments * Math.PI * 2;
          const sn = Math.sin(v), cs = -Math.cos(v);
          N.set(cs * Ni.x + sn * Bi.x, cs * Ni.y + sn * Bi.y, cs * Ni.z + sn * Bi.z).normalize();
          pos.push(P.x + r * N.x, P.y + r * N.y, P.z + r * N.z);
          nor.push(N.x, N.y, N.z);
          uvs.push(t, j / radialSegments);
        }
      }
      for (let i = 1; i <= tubularSegments; i++) {
        for (let j = 1; j <= radialSegments; j++) {
          const a = (radialSegments + 1) * (i - 1) + (j - 1);
          const b = (radialSegments + 1) * i + (j - 1);
          const c = (radialSegments + 1) * i + j;
          const d = (radialSegments + 1) * (i - 1) + j;
          idx.push(a, b, d, b, c, d);
        }
      }
      const geo = new THREE.BufferGeometry();
      geo.setAttribute('position', new THREE.Float32BufferAttribute(pos, 3));
      geo.setAttribute('normal', new THREE.Float32BufferAttribute(nor, 3));
      geo.setAttribute('uv', new THREE.Float32BufferAttribute(uvs, 2));
      geo.setIndex(idx);
      return geo;
    }
    function smile(parent, position, width, material, face) {
      const group = new THREE.Group();
      group.position.set(position[0], position[1], position[2]);
      parent.add(group);
      const mesh = addMesh(group, new THREE.BufferGeometry(), material);
      const state = { c: 1, o: 0 };
      const SEGS = 12;
      /* Follow the curvature of the face (or the muzzle, for Mochi) so a wide
         grin wraps around the cheeks instead of floating out in front of the
         chin. `face` is { c:[cx,cy,cz], r:[rx,ry,rz] } in headRig space. */
      function surfaceZ(x, y) {
        if (!face) return null;
        const a = (x - face.c[0]) / face.r[0];
        const b = (y - face.c[1]) / face.r[1];
        const k = 1 - a * a - b * b;
        const z = face.c[2] + face.r[2] * Math.sqrt(k > 0 ? k : 0) - position[2] + .006;
        return Math.max(-.075, Math.min(.075, z));
      }
      let talk = 0;
      function build(cAmt, oAmt) {
        const c = cAmt, o = Math.max(0, oAmt) + talk;
        /* A cute smile is a wide, shallow bowl whose corners flick UP past the
           mouth line. Both depth and flick scale with the mouth width so the
           same code reads on a .10 bunny mouth and a .12 human one. */
        const w = width * (1 + Math.max(0, c - 1) * .14);
        const depth = c * width * .26;
        const flick = c * width * .18;
        const pts = [];
        for (let i = 0; i <= SEGS; i++) {
          const u = -1 + (2 * i) / SEGS;
          const bell = 1 - u * u;
          const x = u * w * .5;
          const y = depth * (u * u - 1) + flick * Math.pow(Math.abs(u), 3) - o * width * .34 * bell;
          const z = surfaceZ(x, position[1] + y);
          pts.push(vec(x, y, z === null ? .008 * bell : z));
        }
        const curve = new THREE.CatmullRomCurve3(pts);
        const thick = Math.max(.010, width * .125) * (1 + o * .5);
        const geo = taperedTube(curve, 32, function (t) {
          return thick * (.18 + .82 * Math.sqrt(Math.max(0, Math.sin(Math.PI * t))));
        }, 10);
        if (mesh.geometry) mesh.geometry.dispose();
        mesh.geometry = geo;
      }
      build(state.c, state.o);
      group.setMood = function (cAmt, oAmt, dur) {
        const toC = (cAmt === undefined) ? 1 : cAmt, toO = oAmt || 0;
        if (G && dur !== 0) G.to(state, { c: toC, o: toO, duration: dur || .45,
          ease: 'power2.out', onUpdate: function () { build(state.c, state.o); } });
        else { state.c = toC; state.o = toO; build(state.c, state.o); }
      };
      group.setTalk = function (v) {
        talk = Math.max(0, Math.min(1, v || 0)) * .85;
        build(state.c, state.o);
      };
      return group;
    }
    function blush(parent, x, y, z, radius, material) {
      return sphere(parent, material, [x, y, z], [radius, radius * .63, radius * .22], 16);
    }
    function createArms(parent, options) {
      const config = Object.assign({ x: .24, y: 1.35, z: .02, upper: .27, fore: .24, radius: .045, skinRadius: .05, sleeve: null, skin: null }, options);
      function make(side) {
        const shoulder = new THREE.Group();
        shoulder.position.set(side * config.x, config.y, config.z);
        shoulder.rotation.z = side * .12;
        parent.add(shoulder);
        const upperMat = config.sleeve || config.skin;
        cylinder(shoulder, upperMat, [0, -config.upper / 2, 0], config.radius, config.radius * .92, config.upper, 14);
        sphere(shoulder, upperMat, [0, -config.upper, 0], [config.radius, config.radius, config.radius], 14);
        const elbow = new THREE.Group();
        elbow.position.y = -config.upper;
        shoulder.add(elbow);
        cylinder(elbow, config.skin, [0, -config.fore / 2, 0], config.radius * .83, config.radius * .76, config.fore, 14);
        const hand = new THREE.Group();
        hand.position.set(0, -config.fore - config.skinRadius * .2, .008);
        elbow.add(hand);
        sphere(hand, config.skin, [0, -.025, 0], [config.skinRadius, config.skinRadius * 1.13, config.skinRadius * .74], 16);
        return { shoulder: shoulder, elbow: elbow, hand: hand, isWing: false };
      }
      return { L: make(-1), R: make(1) };
    }
    function eyeBrows(parent, skinMat, hairMat, options = {}) {
      const y = options.y || .14, z = options.z || .215, x = options.x || .1;
      const bw = options.w || .045, bh = options.h || .022, br = options.r || .009;
      const brows = [];
      [-1, 1].forEach(side => {
        const pivot = new THREE.Group();
        pivot.position.set(side * x, y, z);
        if (options.ry) pivot.rotation.y = side * options.ry;
        parent.add(pivot);
        tube(pivot, [[-bw, 0, 0], [0, bh, .004], [bw, 0, 0]], br, hairMat, 7);
        brows.push({ pivot: pivot, side: side });
      });
      return {
        set(raise, tilt) {
          brows.forEach(b => {
            const dy = (raise || 0) * .024;
            const rz = (tilt || 0) * b.side * .36;
            if (G) {
              G.to(b.pivot.position, { y: b.pivot.userData.y0 !== undefined ? b.pivot.userData.y0 + dy : dy,
                duration: .5, ease: 'power2.out', overwrite: true });
              G.to(b.pivot.rotation, { z: rz, duration: .5, ease: 'power2.out', overwrite: true });
            } else { b.pivot.position.y = dy; b.pivot.rotation.z = rz; }
          });
        }
      };
    }
    function pearl(parent, pos, radius = .014, material = null) {
      const m = material || colorMat(0xfff9ef, { roughness: .14, clearcoat: 1, metalness: .05 });
      const p = sphere(parent, m, pos, [radius, radius, radius], 12);
      p.castShadow = false;
      return p;
    }

    /* STANCE is how they HOLD themselves; the face alone is only half an
       expression. lean = pitch, stanceY = height, armX = arms forward/back,
       hip = hip cocked, squash = body volume. */
    const POSES = {
      neutral: { lean:  0,     stanceY:  0,     armX:   0,   hip:  0,     squash: 1     },
      slump:   { lean:  .055,  stanceY: -.035,  armX: -.10,  hip:  .02,   squash: .965  },
      wait:    { lean: -.015,  stanceY: -.012,  armX:  .04,  hip:  .11,   squash: 1.010 },
      offer:   { lean: -.070,  stanceY:  .022,  armX:  .58,  hip: -.03,   squash: 1.025 },
      proud:   { lean: -.035,  stanceY:  .012,  armX:  .12,  hip: -.075,  squash: 1.030 },
      startle: { lean:  .070,  stanceY:  .026,  armX: -.28,  hip:  0,     squash: .975  }
    };
    const MOODS = {
      welcome:  { left: -1.58, right: 1.58, leftElbow: -.48, rightElbow: -.48,  headZ: 0,     headY: 0,    headX:  0,    brow: .55, browTilt:  0,    eye: 1.00, mouthCurve:  1.00, mouthOpen: 0,    pose:'neutral' },
      happy:    { left: -2.25, right: 2.25, leftElbow: -.35, rightElbow: -.35,  headZ: -.035, headY: 0,    headX:  0,    brow: .95, browTilt: -.22, eye: .42,  mouthCurve:  1.70, mouthOpen: .60, pose:'proud'   },
      thinking: { left: -1.05, right: 2.72, leftElbow: -.35, rightElbow: -1.25, headZ: -.12,  headY: .12,  headX:  .03,  brow: .30, browTilt:  .60, eye: .78,  mouthCurve:  .30,  mouthOpen: 0,    pose:'neutral' },
      hesitant: { left: -.92,  right: .92,  leftElbow: -.2,  rightElbow: -.2,   headZ: .1,    headY: -.08, headX:  .045, brow: -.38, browTilt: -.48, eye: 1.14, mouthCurve: -.40,  mouthOpen: .18, pose:'slump'   },
      sad:      { left: -.48,  right: .48,  leftElbow: -.10, rightElbow: -.10,  headZ: .02,   headY: .05,  headX:  .12,  brow: -.95, browTilt: .35,  eye: .55,  mouthCurve: -1.20, mouthOpen: .06, pose:'slump'   },
      waiting:  { left: -1.15, right: 1.15, leftElbow: -.62, rightElbow: -.62,  headZ: .20,   headY: .06,  headX:  .02,  brow: .20, browTilt:  .70, eye: .95,  mouthCurve:  .12,  mouthOpen: .05, pose:'wait'    },
      coupon:   { left: -2.45, right: 2.45, leftElbow: -.85, rightElbow: -.85,  headZ: -.04,  headY: 0,    headX: -.05,  brow: .80, browTilt: -.10, eye: 1.15, mouthCurve:  1.55, mouthOpen: .30, pose:'offer'   },
      wink:     { left: -1.90, right: 1.90, leftElbow: -.50, rightElbow: -.50,  headZ: -.06,  headY: .04,  headX: -.02,  brow: .70, browTilt:  .15, eye: 1.00, mouthCurve:  1.25, mouthOpen: .10, pose:'proud', wink:true },
      surprised:{ left: -2.60, right: 2.60, leftElbow: -1.1, rightElbow: -1.1,  headZ: 0,     headY: 0,    headX: -.04,  brow: 1.15, browTilt: 0,    eye: 1.25, mouthCurve:  .20,  mouthOpen: .55, pose:'startle' }
    };

    class CharacterBase {
      constructor(name, role, blurb) {
        this.name = name;
        this.role = role;
        this.blurb = blurb;
        this.root = new THREE.Group();
        this.root.position.y = FLOOR_Y;
        this.bodyGroup = new THREE.Group();
        this.root.add(this.bodyGroup);
        this.headRig = new THREE.Group();
        this.root.add(this.headRig);
        this.armL = null;
        this.armR = null;
        this.eyes = null;
        this.mouth = null;
        this.brows = null;
        this.tickers = [];
        this.gaze = { x: 0, y: 0 };
        this.gazeTarget = { x: 0, y: 0 };
        this.headTarget = { x: 0, y: 0, z: 0 };
        this.emotion = 'welcome';
        this.jump = 0;
        this.blinkTimer = 2.2 + Math.random() * 2.5;
        this.blinkElapsed = 0;
        this.breath = 1;
        this.squash = 1;
        this.reactions = ['tickle', 'shy', 'bounce', 'spin', 'startle', 'pose'];
        this.stanceY = 0; this.stepLift = 0; this.stepX = 0;
        this.hipBase = 0; this.wiggle = 0; this.spin = 0; this.armSwingX = 0;
        this._stanceHip = 0; this._stanceArmX = 0;
        this.stepElapsed = 0; this.stepTimer = 4 + Math.random() * 6;
        this.phase = Math.random() * Math.PI * 2;
        this.onMood = null;
        this.onSpark = null;
      }
      mount(scene) { scene.add(this.root); return this; }
      update(dt, time) {
        const breath = Math.sin(time * 1.85 + this.phase) * .009 * this.breath;
        const sq = this.squash || 1;
        this.bodyGroup.scale.set(sq, (1 + breath) / Math.sqrt(sq), sq);
        this.root.position.y = FLOOR_Y + Math.sin(time * 1.35 + this.phase) * .012 + this.jump + this.stanceY + this.stepLift;
        /* Locomotion: slow weight shift, gentle body turn, slight drift and
           hanging arms that sway -- nobody is a static mannequin between poses. */
        const st = time * .55 + this.phase;
        this.root.rotation.z = this.hipBase + this.wiggle + Math.sin(st * 1.15) * .012;
        this.root.rotation.y = this.spin + Math.sin(st * .42) * .035;
        this.root.position.x = this.stepX + Math.sin(st * .55) * .010;
        [this.armL, this.armR].forEach((a, i) => { if (a && !a.isWing) a.shoulder.rotation.x = this.armSwingX + Math.sin(st * 1.1 + i * 1.6) * .022; });
        this.gaze.x = lerp(this.gaze.x, this.gazeTarget.x, Math.min(1, dt * 4));
        this.gaze.y = lerp(this.gaze.y, this.gazeTarget.y, Math.min(1, dt * 4));
        this.headRig.rotation.x = this.headTarget.x + this.gaze.y * .11 + Math.sin(time * .5 + this.phase) * .012;
        this.headRig.rotation.y = this.headTarget.y + this.gaze.x * .18 + Math.sin(time * .36 + this.phase) * .018;
        this.headRig.rotation.z = this.headTarget.z + Math.sin(time * .65 + this.phase) * .012;
        if (this.eyes) this.eyes.gaze(this.gaze.x, this.gaze.y);
        this.blinkElapsed += dt;
        if (this.blinkElapsed >= this.blinkTimer) {
          if (this.eyes) this.eyes.blink();
          this.blinkElapsed = 0;
          this.blinkTimer = 2.1 + Math.random() * 3.7;
        }
        this.stepElapsed += dt;
        if (this.stepElapsed >= this.stepTimer) {
          this.stepElapsed = 0; this.stepTimer = 5.5 + Math.random() * 6.5;
          if (!this._reactBusy) this.twoStep();
        }
        this.tickers.forEach(fn => fn(time, dt));
        if (this.animateExtra) this.animateExtra(time, dt);
      }
      poseArm(arm, angle, elbow) {
        if (!arm) return;
        if (G) {
          G.to(arm.shoulder.rotation, { z: angle, duration: .78, ease: 'power3.inOut', overwrite: true });
          if (arm.elbow) G.to(arm.elbow.rotation, { z: elbow, duration: .78, ease: 'power3.inOut', overwrite: true });
        } else {
          arm.shoulder.rotation.z = angle;
          if (arm.elbow) arm.elbow.rotation.z = elbow;
        }
      }
      flutter(tl, amount, reps) {
        [this.armL, this.armR].forEach((arm, i) => {
          if (!arm) return;
          const z0 = arm.shoulder.rotation.z;
          const to = arm.isWing ? z0 + amount * .3 : z0 + (arm === this.armL ? -1 : 1) * Math.abs(amount);
          tl.to(arm.shoulder.rotation, { z: to, duration: .085, repeat: reps, yoyo: true, ease: 'sine.inOut' }, 0);
        });
      }
      /* Poking the character: each tap runs a DIFFERENT reaction from the pool
         and never the same one twice in a row, so it never reads as a loop. */
      react() {
        if (this._reactBusy) return null;
        const pool = (this.reactions || ['tickle', 'shy', 'bounce']).filter(n => n !== this._lastReact);
        const name = pool[Math.floor(Math.random() * pool.length)] || 'tickle';
        this._lastReact = name;
        this._reactBusy = true;
        let dur = 1.2;
        try {
          const fn = this['react_' + name];
          dur = (fn ? fn.call(this) : this.react_tickle.call(this)) || 1.2;
        } catch (e) { dur = 1.2; }
        window.setTimeout(() => { this._reactBusy = false; }, dur * 1000);
        return name;
      }
      /* "gudi gudi" -- a shivery tickle: whole body wiggles, head lolls, eyes
         squeeze shut and it giggle-hops. */
      react_tickle() {
        const prev = this.emotion;
        const restore = () => this.setEmotion(prev, false);
        if (this.eyes) this.eyes.mood(.28);
        if (this.mouth) this.mouth.setMood(1.8, .45, .18);
        if (this.brows) this.brows.set(1, 0);
        if (!G) { window.setTimeout(restore, 900); return 1; }
        const tl = G.timeline({ onComplete: restore });
        tl.to(this, { wiggle: .085, duration: .085, repeat: 7, yoyo: true, ease: 'sine.inOut' }, 0)
          .to(this.headTarget, { z: .10, duration: .085, repeat: 7, yoyo: true, ease: 'sine.inOut' }, 0)
          .to(this, { squash: 1.06, jump: .05, duration: .085, repeat: 7, yoyo: true, ease: 'sine.inOut' }, 0)
          .to(this, { wiggle: 0, duration: .3, ease: 'power2.out' }, .74)
          .to(this.headTarget, { z: 0, duration: .3, ease: 'power2.out' }, .74)
          .to(this, { squash: 1, jump: 0, duration: .3, ease: 'power2.out' }, .74);
        this.flutter(tl, .55, 7);
        return 1.1;
      }
      react_shy() {
        const prev = this.emotion, gx = this.gazeTarget.x, gy = this.gazeTarget.y;
        if (this.eyes) this.eyes.mood(.82);
        if (this.mouth) this.mouth.setMood(1.05, .05, .3);
        if (this.brows) this.brows.set(.72, -.22);
        if (!G) { window.setTimeout(() => this.setEmotion(prev, false), 1100); return 1.2; }
        const tl = G.timeline({ onComplete: () => { G.to(this.gazeTarget, { x: gx, y: gy, duration: .5 }); this.setEmotion(prev, false); } });
        tl.to(this.headTarget, { x: .13, z: .14, duration: .45, ease: 'power2.out' }, 0)
          .to(this.gazeTarget, { x: -.6, y: -.45, duration: .45, ease: 'power2.out' }, 0)
          .to(this, { squash: 1.035, duration: .17, repeat: 5, yoyo: true, ease: 'sine.inOut' }, 0)
          .to(this.headTarget, { x: 0, z: 0, duration: .5, ease: 'power2.inOut' }, 1.1)
          .to(this.gazeTarget, { x: gx, y: gy, duration: .55, ease: 'power2.inOut' }, 1.1)
          .to(this, { squash: 1, duration: .35, ease: 'power2.out' }, 1.1);
        this.flutter(tl, .3, 5);
        return 1.7;
      }
      react_bounce() {
        const prev = this.emotion;
        if (this.eyes) this.eyes.mood(.45);
        if (this.mouth) this.mouth.setMood(1.6, .5, .15);
        if (!G) { window.setTimeout(() => this.setEmotion(prev, false), 700); return .8; }
        const tl = G.timeline({ onComplete: () => this.setEmotion(prev, false) });
        tl.to(this, { jump: .26, duration: .22, ease: 'power2.out' }, 0)
          .to(this, { jump: 0, duration: .3, ease: 'bounce.out' }, .22)
          .to(this, { squash: .93, duration: .12, ease: 'power2.out' }, 0)
          .to(this, { squash: 1.06, duration: .16, ease: 'power2.out' }, .26)
          .to(this, { squash: 1, duration: .45, ease: 'elastic.out' }, .42);
        this.flutter(tl, -.6, 3);
        return 1.05;
      }
      /* MOVEMENT: a little two-step shuffle so they shift their weight and
         take a step instead of standing frozen. stepLift/stepX are properties
         because update() rewrites root.position every frame. */
      twoStep() {
        if (!G) return;
        const dir = Math.random() < .5 ? -1 : 1;
        const d = .055 + Math.random() * .05;
        G.timeline()
          .to(this, { stepX: dir * d, duration: .32, ease: 'power2.inOut' }, 0)
          .to(this, { stepLift: .024, duration: .16, ease: 'power2.out' }, 0)
          .to(this, { stepLift: 0, duration: .22, ease: 'power2.in' }, .16)
          .to(this, { stepX: dir * d * .3, duration: .3, ease: 'power2.inOut' }, .34)
          .to(this, { stepLift: .02, duration: .15, ease: 'power2.out' }, .5)
          .to(this, { stepLift: 0, duration: .22, ease: 'power2.in' }, .65)
          .to(this, { stepX: 0, duration: .55, ease: 'power2.inOut' }, .85);
      }
      react_spin() {
        const prev = this.emotion, y0 = this.spin || 0;
        if (this.eyes) this.eyes.mood(.45);
        if (this.mouth) this.mouth.setMood(1.5, .3, .15);
        if (this.brows) this.brows.set(.85, 0);
        if (!G) { window.setTimeout(() => this.setEmotion(prev, false), 700); return .8; }
        const tl = G.timeline({ onComplete: () => { this.spin = y0; this.setEmotion(prev, false); } });
        tl.to(this, { spin: y0 + Math.PI * 2, duration: .85, ease: 'power2.inOut' }, 0)
          .to(this, { jump: .12, duration: .22, ease: 'power2.out' }, .1)
          .to(this, { jump: 0, duration: .3, ease: 'power2.out' }, .32);
        this.flutter(tl, -.8, 1);
        return 1.0;
      }
      react_startle() {
        const prev = this.emotion;
        if (this.eyes) this.eyes.mood(1.3);
        if (this.mouth) this.mouth.setMood(.2, .55, .12);
        if (this.brows) this.brows.set(1.1, 0);
        if (!G) { window.setTimeout(() => this.setEmotion(prev, false), 800); return .9; }
        const tl = G.timeline({ onComplete: () => this.setEmotion(prev, false) });
        tl.to(this, { stepLift: .09, duration: .13, ease: 'power2.out' }, 0)
          .to(this, { stepLift: 0, duration: .32, ease: 'bounce.out' }, .13)
          .to(this, { squash: .92, duration: .1, ease: 'power2.out' }, 0)
          .to(this, { squash: 1, duration: .5, ease: 'elastic.out' }, .18)
          .to(this, { wiggle: .07, duration: .07, repeat: 5, yoyo: true, ease: 'sine.inOut' }, 0)
          .to(this, { wiggle: 0, duration: .25, ease: 'power2.out' }, .5);
        this.flutter(tl, -1.15, 3);
        return 1.0;
      }
      react_pose() {
        const prev = this.emotion, gx = this.gazeTarget.x;
        if (this.eyes) this.eyes.mood(.62);
        if (this.mouth) this.mouth.setMood(1.25, .08, .3);
        if (this.brows) this.brows.set(.6, .1);
        if (!G) { window.setTimeout(() => this.setEmotion(prev, false), 1200); return 1.3; }
        const tl = G.timeline({ onComplete: () => { G.to(this.gazeTarget, { x: gx, duration: .5 }); this.setEmotion(prev, false); } });
        tl.to(this, { hipBase: -.13, duration: .4, ease: 'power2.out' }, 0)
          .to(this.headTarget, { x: -.07, y: .18, duration: .45, ease: 'power2.out' }, 0)
          .to(this.gazeTarget, { x: .5, duration: .45, ease: 'power2.out' }, 0)
          .to(this, { armSwingX: .24, duration: .4, ease: 'power2.out' }, 0)
          .to(this, { hipBase: this._stanceHip, duration: .5, ease: 'power2.inOut' }, 1.15)
          .to(this.headTarget, { x: 0, y: 0, duration: .5, ease: 'power2.inOut' }, 1.15)
          .to(this.gazeTarget, { x: gx, duration: .5, ease: 'power2.inOut' }, 1.15)
          .to(this, { armSwingX: this._stanceArmX, duration: .5, ease: 'power2.inOut' }, 1.15);
        return 1.75;
      }
      setEmotion(name, announce = true) {
        const pose = MOODS[name] || MOODS.welcome;
        this.emotion = name;
        this.poseArm(this.armL, pose.left, pose.leftElbow);
        this.poseArm(this.armR, pose.right, pose.rightElbow);
        this.headTarget.z = pose.headZ;
        this.headTarget.y = pose.headY;
        this.headTarget.x = pose.headX !== undefined ? pose.headX : 0;
        /* curvature + openness carry far more expression than width ever did */
        if (this.mouth && this.mouth.setMood) this.mouth.setMood(pose.mouthCurve, pose.mouthOpen);
        else if (this.mouth && G) G.to(this.mouth.scale, { x: pose.smile || 1, duration: .45, ease: 'power2.out' });
        /* Whole-body stance: the pose they hold, not just the face. */
        const stance = POSES[pose.pose] || POSES.neutral;
        this._stanceHip = stance.hip; this._stanceArmX = stance.armX;
        if (G) {
          G.to(this, { stanceY: stance.stanceY, hipBase: stance.hip, duration: .6, ease: 'power2.out' });
          G.to(this.root.rotation, { x: stance.lean, duration: .6, ease: 'power2.out' });
          G.to(this, { squash: stance.squash, duration: .6, ease: 'power2.out' });
        } else {
          this.stanceY = stance.stanceY; this.hipBase = stance.hip;
          this.root.rotation.x = stance.lean; this.squash = stance.squash;
        }
        this.armSwingX = stance.armX;
        /* brows are the strongest expression cue and were previously static */
        if (this.brows) this.brows.set(pose.brow, pose.browTilt);
        if (this.eyes) this.eyes.mood(pose.eye);
        if (pose.wink && this.eyes && this.eyes.wink) this.eyes.wink(1);
        if (name === 'happy') {
          if (G) G.to(this, { jump: .12, duration: .18, yoyo: true, repeat: 1, ease: 'power2.out' });
          else this.jump = 0;
        }
        if (this.onMood) this.onMood(name);
        if (announce && typeof announceEmotion === 'function') announceEmotion(this, name);
      }
      dispose() {
        this.root.traverse(object => {
          if (object.geometry) object.geometry.dispose();
          if (object.material) (Array.isArray(object.material) ? object.material : [object.material]).forEach(m => m.dispose());
        });
        if (this.root.parent) this.root.parent.remove(this.root);
      }
    }

    class AshaCharacter extends CharacterBase {
      constructor() { super('Asha', 'Royal Bridal Stylist', 'A warm welcome to a world of heirloom detail, velvet and gold.'); this.build(); }
      build() {
        const skin = colorMat(0xba7742, { roughness: .48, clearcoat: .34, clearcoatRoughness: .56, sheen: new THREE.Color(0xe7a578), emissive: 0x34170b, emissiveIntensity: .035 });
        const blushMat = colorMat(0xe88782, { roughness: .62, transparent: true, opacity: .48, sheen: new THREE.Color(0xffb3a5) });
        const crimson = colorMat(0x741729, { roughness: .62, sheen: new THREE.Color(0xc5515f), clearcoat: .23 });
        const hair = colorMat(0x241610, { roughness: .3, clearcoat: .8, clearcoatRoughness: .2 });
        const gold = goldMat(), ruby = gemMat(0x9f1239);
        lathe(this.bodyGroup, crimson, [[.03,.1],[.54,.12],[.57,.2],[.48,.42],[.35,.7],[.26,1.04],[.22,1.18]], 48);
        lathe(this.bodyGroup, crimson, [[.03,1.02],[.2,1.03],[.24,1.22],[.22,1.42],[.18,1.5]], 36);
        for (let i = 0; i < 3; i++) {
          const trim = addMesh(this.root, new THREE.TorusGeometry(.565 - i*.095, .009, 8, 56), gold);
          trim.rotation.x = Math.PI / 2;
          trim.position.y = .15 + i * .15;
        }
        for (let i = 0; i < 22; i++) {
          const a = i / 22 * Math.PI * 2;
          const bead = sphere(this.bodyGroup, gold, [Math.cos(a)*.49, .42 + (i%3)*.14, Math.sin(a)*.49], [.012,.018,.012], 8);
        }
        // The dupatta is built as a custom cloth ribbon with raised gold piping cascading over the shoulder.
        const drapePoints = [[-.24,1.86,.04],[-.34,1.65,.18],[-.31,1.35,.28],[-.24,.95,.36],[-.18,.58,.42]];
        ribbon(this.root, drapePoints, .20, crimson, 36);
        tube(this.root, drapePoints.map(p => [p[0]-.095,p[1],p[2]+.01]), .007, gold);
        tube(this.root, drapePoints.map(p => [p[0]+.095,p[1],p[2]+.01]), .007, gold);
        for (let i=0;i<7;i++) pearl(this.root, [-.28 + (i%2)*.05, 1.72-i*.16, .20+i*.028], .011, gold);

        cylinder(this.root, skin, [0,1.48,0], .075,.09,.25,18);
        this.headRig.position.y = 1.77;
        sphere(this.headRig, skin, [0,0,0], [.29,.34,.255], 32);
        sphere(this.headRig, hair, [0,.12,-.035], [.305,.26,.255], 28);
        sphere(this.headRig, hair, [0,.29,-.035], [.235,.13,.225], 22);
        // Long side locks frame the face beneath the bridal scarf.
        [-1,1].forEach(side => sphere(this.headRig, hair, [side*.252,-.18,-.015], [.07,.31,.09], 18));
        this.eyes = eyePair(this.headRig, {x:.105,y:.035,z:.218,radius:.071,iris:0x402319});
        this.brows = eyeBrows(this.headRig, skin, hair, {y:.145,z:.216,x:.105});
        sphere(this.headRig, skin, [0,-.065,.251], [.031,.038,.032], 16);
        this.mouth = smile(this.headRig, [0,-.198,.229], .122, colorMat(0x762332,{roughness:.38,clearcoat:.45}), {c:[0,0,0],r:[.29,.34,.255]});
        blush(this.headRig,-.178,-.085,.207,.058,blushMat); blush(this.headRig,.178,-.085,.207,.058,blushMat);
        // Maang tikka and ruby teardrop.
        const tikka = addMesh(this.headRig, new THREE.TorusGeometry(.042,.008,8,20), gold);
        tikka.position.set(0,.245,.237); tikka.rotation.x = .25;
        sphere(this.headRig, ruby, [0,.184,.255], [.021,.036,.018], 16);
        sphere(this.headRig, gold, [0,.141,.255], [.009,.013,.01], 10);
        tube(this.headRig,[[-.27,.17,.01],[-.2,.27,.11],[0,.31,.19],[.2,.27,.11],[.27,.17,.01]],.006,gold);
        const earringLeft = new THREE.Group(), earringRight = new THREE.Group();
        [earringLeft,earringRight].forEach((e,i)=>{ e.position.set(i? .28:-.28,-.12,-.01); this.headRig.add(e); sphere(e,gold,[0,-.025,.015],[.023,.04,.022],12); addMesh(e,new THREE.TorusGeometry(.023,.006,8,16),gold).position.set(0,-.075,.018); sphere(e,ruby,[0,-.085,.02],[.012,.018,.012],10); });
        this.tickers.push((t)=>{ earringLeft.rotation.x=Math.sin(t*1.35)*.13; earringRight.rotation.x=Math.sin(t*1.35+1)*.13; });
        const arms = createArms(this.root,{x:.235,y:1.37,z:.04,upper:.3,fore:.26,radius:.05,skinRadius:.052,sleeve:crimson,skin:skin});
        this.armL=arms.L; this.armR=arms.R;
      }
    }

    class MochiCharacter extends CharacterBase {
      constructor() { super('Mochi', 'Velvet Bunny Mascot', 'A cashmere-soft companion with a little emerald sparkle and a very big heart.'); this.earParts=[]; this.build(); }
      build() {
        const fur = colorMat(0xf0e7d9,{roughness:.88,sheen:new THREE.Color(0xffddce)});
        const cream = colorMat(0xfff9ee,{roughness:.82,sheen:new THREE.Color(0xffe7d8)});
        const chestFur = colorMat(0xf8f1e6,{roughness:.87,sheen:new THREE.Color(0xfff3e4)});
        const pink = colorMat(0xef9dab,{roughness:.6,sheen:new THREE.Color(0xffc7cf)});
        const blushMat = colorMat(0xe995a6,{roughness:.7,transparent:true,opacity:.42});
        const sash = colorMat(0x5b1428,{roughness:.31,sheen:new THREE.Color(0xbf6674)});
        const gold = goldMat(), emerald = gemMat(0x1b9869);
        sphere(this.bodyGroup,fur,[0,.67,0],[.48,.54,.43],30);
        sphere(this.bodyGroup,chestFur,[0,.62,.345],[.24,.28,.10],24);
        // Pom-pom tail: a core plus a shell of overlapping lobes so the
        // silhouette scallops like fur instead of reading as one hard ball.
        // Lobes on the front half sit inside the body, so only the back ones show.
        const tail=new THREE.Group(); tail.position.set(0,.47,-.375); this.bodyGroup.add(tail);
        sphere(tail,fur,[0,0,-.02],[.125,.13,.115],20);
        for(let i=0;i<14;i++){
          const y=1-(i/13)*2, rr=Math.sqrt(Math.max(0,1-y*y)), a=i*2.39996, d=.072;
          const rad=.052+(i%3)*.009;
          sphere(tail,i%4===0?chestFur:fur,[Math.cos(a)*rr*d, y*.085, -.035+Math.sin(a)*rr*d],[rad,rad,rad],12);
        }
        this.tickers.push(t=>{ tail.rotation.y=Math.sin(t*1.35)*.11; tail.rotation.x=Math.sin(t*.95)*.05; });
        [-1,1].forEach(side=>{
          const foot=sphere(this.bodyGroup,fur,[side*.22,.14,.08],[.18,.12,.22],18);
          sphere(this.bodyGroup,pink,[side*.22,.13,.24],[.1,.04,.025],14);
        });
        this.headRig.position.y=1.28;
        sphere(this.headRig,fur,[0,0,0],[.405,.405,.37],32);
        sphere(this.headRig,cream,[0,-.14,.291],[.245,.17,.13],22);
        [-1,1].forEach(side=>{
          const ear=new THREE.Group(); ear.position.set(side*.155,.30,-.005); ear.rotation.z=-side*.13; this.headRig.add(ear);
          // Outer shell: narrow at the base, fullest through the middle, softly
          // domed at the tip. A single ellipsoid reads as a flat leaf.
          sphere(ear,fur,[0,.16,0],[.072,.13,.062],18);
          sphere(ear,fur,[0,.34,0],[.098,.19,.075],20);
          sphere(ear,fur,[0,.52,0],[.082,.13,.062],18);
          // Inner cup follows the same taper. It stands ~.006 proud at the
          // centre line but sinks under the fur at its own edges, so it reads
          // as a hollow rather than a pink plate glued to the front.
          sphere(ear,pink,[0,.17,.042],[.040,.095,.026],14);
          sphere(ear,pink,[0,.35,.051],[.056,.150,.030],16);
          sphere(ear,pink,[0,.51,.044],[.040,.095,.024],14);
          this.earParts.push({group:ear,side:side});
        });
        this.eyes=eyePair(this.headRig,{x:.147,y:.045,z:.323,radius:.095,dark:true});
        sphere(this.headRig,pink,[0,-.072,.402],[.045,.033,.027],16);
        this.mouth=smile(this.headRig,[0,-.158,.418],.100,colorMat(0x9c5662,{roughness:.4}),{c:[0,-.14,.291],r:[.245,.17,.13]});
        blush(this.headRig,-.25,-.1,.29,.075,blushMat); blush(this.headRig,.25,-.1,.29,.075,blushMat);
        // Small velvet sash wraps the plump body and meets at an emerald brooch.
        // Parented to bodyGroup, NOT root: breathing scales bodyGroup every
        // frame, and a flat ribbon left on root slides against the fur.
        ribbon(this.bodyGroup,[[-.43,.92,.12],[-.25,.81,.35],[0,.74,.45],[.24,.81,.35],[.43,.92,.12]],.135,sash,30);
        tube(this.bodyGroup,[[-.43,.92,.13],[-.25,.81,.36],[0,.74,.46],[.24,.81,.36],[.43,.92,.13]],.007,gold);
        addMesh(this.bodyGroup,new THREE.TorusGeometry(.068,.012,10,24),gold).position.set(0,.76,.46);
        const jewel=addMesh(this.bodyGroup,new THREE.OctahedronGeometry(.05),emerald); jewel.position.set(0,.76,.48); jewel.scale.y=1.3;
        const arms=createArms(this.root,{x:.39,y:.82,z:.02,upper:.2,fore:.18,radius:.082,skinRadius:.105,sleeve:fur,skin:fur}); this.armL=arms.L; this.armR=arms.R;
        this.tickers.push((t)=>this.earParts.forEach(e=>{e.group.rotation.x=Math.sin(t*1.55+e.side)*.075; e.group.rotation.z=-e.side*(.13+Math.sin(t*.7+e.side)*.05);}));
      }
    }

    class NoorCharacter extends CharacterBase {
      constructor() { super('Noor', 'Parisian Glamour Artist', 'Sculpted liner, a satin-lapel blazer and a golden brush for the finishing touch.'); this.build(); }
      build() {
        const skin=colorMat(0xf0d4c0,{roughness:.39,clearcoat:.52,clearcoatRoughness:.38,sheen:new THREE.Color(0xf4bfa0),emissive:0x351913,emissiveIntensity:.025});
        const suit=colorMat(0x101017,{roughness:.4,metalness:.1,sheen:new THREE.Color(0x62617b),clearcoat:.32});
        const satin=colorMat(0x34333e,{roughness:.26,metalness:.12,sheen:new THREE.Color(0xc2bace)});
        const hair=colorMat(0x111116,{roughness:.2,clearcoat:1,clearcoatRoughness:.1});
        const gold=goldMat(), liner=standardMat(0x19131a,{roughness:.2});
        lathe(this.bodyGroup,suit,[[.19,.12],[.21,.42],[.25,.7],[.26,1.06],[.21,1.2]],38);
        cylinder(this.root,suit,[-.12,.29,0],.085,.095,.45,16); cylinder(this.root,suit,[.12,.29,0],.085,.095,.45,16);
        sphere(this.root,standardMat(0x17151c,{roughness:.25}),[-.12,.08,.08],[.115,.05,.18],16);
        sphere(this.root,standardMat(0x17151c,{roughness:.25}),[.12,.08,.08],[.115,.05,.18],16);
        // Angular lapels are tiny procedural satin panels, not image textures.
        const lapelMat=satin.clone(); lapelMat.side=THREE.DoubleSide;
        function panel(points, material) {
          const geo=new THREE.BufferGeometry(); geo.setAttribute('position',new THREE.Float32BufferAttribute(points.flat(),3)); geo.setIndex([0,1,2,0,2,3]); geo.computeVertexNormals(); return addMesh(this.bodyGroup,geo,material);
        }
        panel.call(this,[[-.03,1.91,.23],[-.21,1.83,.245],[-.16,1.46,.275],[0,1.61,.28]],lapelMat);
        panel.call(this,[[.03,1.91,.23],[.21,1.83,.245],[.16,1.46,.275],[0,1.61,.28]],lapelMat);
        cylinder(this.root,skin,[0,1.48,0],.07,.08,.24,16);
        this.headRig.position.y=1.78;
        sphere(this.headRig,skin,[0,0,0],[.275,.335,.245],32);
        sphere(this.headRig,hair,[0,.15,-.035],[.29,.24,.255],28);
        sphere(this.headRig,hair,[0,.3,.045],[.25,.115,.2],24);
        [-1,1].forEach(side=>sphere(this.headRig,hair,[side*.24,-.16,-.015],[.075,.28,.105],20));
        this.eyes=eyePair(this.headRig,{x:.096,y:.04,z:.218,radius:.064,iris:0x533b29});
        this.brows = eyeBrows(this.headRig,skin,hair,{y:.147,z:.216,x:.096});
        sphere(this.headRig,skin,[0,-.06,.24],[.025,.032,.027],14);
        this.mouth=smile(this.headRig,[0,-.188,.22],.104,colorMat(0x963c50,{roughness:.35,clearcoat:.4}),{c:[0,0,0],r:[.275,.335,.245]});
        const arms=createArms(this.root,{x:.245,y:1.38,z:.045,upper:.29,fore:.26,radius:.052,skinRadius:.05,sleeve:suit,skin:skin}); this.armL=arms.L; this.armR=arms.R;
        // The brush is assembled in the right hand and gets a warm emissive tip.
        const brush=new THREE.Group(); this.armR.hand.add(brush); brush.position.set(.015,-.02,.04); brush.rotation.z=-.58; brush.rotation.x=.2;
        cylinder(brush,gold,[0,-.17,0],.012,.009,.31,12);
        cylinder(brush,standardMat(0xe4d6c1,{metalness:.9,roughness:.2}),[0,.005,0],.016,.014,.055,12);
        const bristle=addMesh(brush,new THREE.ConeGeometry(.022,.105,12),standardMat(0x76543b,{roughness:.8})); bristle.position.y=.085;
        const tip=sphere(brush,colorMat(0xffd27d,{emissive:0xffa52a,emissiveIntensity:.05,roughness:.22}),[0,.135,0],[.025,.018,.025],12);
        const brushLight=new THREE.PointLight(0xffba56,0,1.15); brushLight.position.set(0,.14,.1); brush.add(brushLight);
        this.brush={tip:tip,light:brushLight};
        this.onMood=(mood)=>{
          const glow=mood==='thinking' ? 1.6 : (mood==='welcome' ? .55 : (mood==='happy' ? 1.1 : .12));
          if(G){G.to(tip.material,{emissiveIntensity:glow,duration:.45});G.to(brushLight,{intensity:glow*.65,duration:.45});}
          else {tip.material.emissiveIntensity=glow;brushLight.intensity=glow*.65;}
        };
      }
    }

    class TaraCharacter extends CharacterBase {
      constructor() { super('Tara', 'Heritage Drape & Henna Guru', 'Emerald silk, temple gold and jasmine flowers guide every graceful detail.'); this.build(); }
      build() {
        const skin=colorMat(0xb27a4a,{roughness:.48,clearcoat:.35,sheen:new THREE.Color(0xd59768),emissive:0x351a0d,emissiveIntensity:.03});
        const emerald=colorMat(0x0c634a,{roughness:.48,sheen:new THREE.Color(0x52bc8f),clearcoat:.25});
        const marigold=colorMat(0xe49619,{roughness:.5,sheen:new THREE.Color(0xffd28a)});
        const hair=colorMat(0x21150e,{roughness:.28,clearcoat:.65});
        const gold=goldMat(), ruby=gemMat(0xb30d3e);
        lathe(this.bodyGroup,emerald,[[.03,.1],[.57,.12],[.6,.22],[.49,.48],[.34,.75],[.24,1.06],[.2,1.2]],48);
        lathe(this.bodyGroup,emerald,[[.04,1.02],[.2,1.04],[.235,1.25],[.21,1.43],[.17,1.49]],36);
        // Marigold silk pallu and zari borders.
        ribbon(this.root,[[-.29,2.04,.02],[-.42,1.9,.14],[-.35,1.62,.29],[-.27,1.25,.41],[-.2,.83,.49]],.19,marigold,36);
        tube(this.root,[[-.39,1.99,.03],[-.51,1.83,.16],[-.43,1.58,.31],[-.35,1.22,.43],[-.28,.83,.5]],.008,gold);
        tube(this.root,[[-.2,2.05,.03],[-.31,1.92,.15],[-.25,1.64,.3],[-.18,1.27,.42],[-.12,.88,.5]],.008,gold);
        for(let i=0;i<24;i++){
          const a=i/24*Math.PI*2;
          sphere(this.bodyGroup,gold,[Math.sin(a)*.54,.3+(i%4)*.115,Math.cos(a)*.54],[.009,.014,.009],8);
        }
        const hem=addMesh(this.root,new THREE.TorusGeometry(.565,.012,8,64),gold); hem.rotation.x=Math.PI/2; hem.position.y=.14;
        cylinder(this.root,skin,[0,1.49,0],.072,.083,.25,16);
        this.headRig.position.y=1.78;
        sphere(this.headRig,skin,[0,0,0],[.285,.335,.25],30);
        sphere(this.headRig,hair,[0,.13,-.04],[.29,.25,.25],26);
        // Classic braided bun with a jasmine ring.
        sphere(this.headRig,hair,[0,.25,-.23],[.14,.15,.11],20);
        for(let i=0;i<6;i++) sphere(this.headRig,hair,[.12,.13-i*.09,-.23],[.044,.06,.045],12);
        const gajra=new THREE.Group(); gajra.position.set(0,.26,-.19); this.headRig.add(gajra);
        for(let i=0;i<12;i++){
          const a=i/12*Math.PI*2;
          const flowerGroup=new THREE.Group(); flowerGroup.position.set(Math.cos(a)*.145,Math.sin(a)*.105,.035); flowerGroup.rotation.z=a; gajra.add(flowerGroup);
          for(let k=0;k<5;k++){const b=k/5*Math.PI*2;sphere(flowerGroup,colorMat(0xfffcf4,{roughness:.48,sheen:new THREE.Color(0xffe6ed)}),[Math.cos(b)*.018,Math.sin(b)*.018,0],[.016,.011,.009],8);}
          sphere(flowerGroup,gold,[0,0,.009],[.006,.006,.006],8);
        }
        this.eyes=eyePair(this.headRig,{x:.102,y:.045,z:.218,radius:.068,iris:0x442619});
        this.brows = eyeBrows(this.headRig,skin,hair,{y:.15,z:.218,x:.102});
        sphere(this.headRig,ruby,[0,.245,.224],[.016,.024,.012],12);
        sphere(this.headRig,skin,[0,-.06,.245],[.026,.035,.026],14);
        this.mouth=smile(this.headRig,[0,-.188,.22],.122,colorMat(0x813041,{roughness:.36}),{c:[0,0,0],r:[.285,.335,.25]});
        const nath=addMesh(this.headRig,new THREE.TorusGeometry(.025,.005,8,18),gold); nath.position.set(.055,-.07,.245); nath.rotation.y=.25;
        tube(this.headRig,[[.07,-.07,.247],[.15,-.05,.2],[.22,-.02,.1],[.265,-.03,.015]],.0035,gold,6);
        const choker=addMesh(this.headRig,new THREE.TorusGeometry(.112,.017,10,32),gold); choker.rotation.x=Math.PI/2; choker.position.set(0,-.3,.005);
        sphere(this.headRig,ruby,[0,-.32,.113],[.015,.021,.013],12);
        const jL=new THREE.Group(),jR=new THREE.Group();
        [jL,jR].forEach((j,i)=>{j.position.set(i ? .26 : -.26,-.12,-.015);this.headRig.add(j);addMesh(j,new THREE.TorusGeometry(.023,.005,8,16),gold).rotation.x=Math.PI/2;sphere(j,ruby,[0,-.063,.01],[.014,.02,.012],10);});
        this.tickers.push(t=>{jL.rotation.x=Math.sin(t*1.2)*.12;jR.rotation.x=Math.sin(t*1.2+1.1)*.12;});
        const arms=createArms(this.root,{x:.24,y:1.37,z:.04,upper:.3,fore:.26,radius:.051,skinRadius:.05,sleeve:emerald,skin:skin});this.armL=arms.L;this.armR=arms.R;
      }
    }

    class GiaCharacter extends CharacterBase {
      constructor() { super('Gia', 'Crystal Beauty Icon', 'A high-voltage beauty muse in iridescent rose, pearl stickers and crystal nail art.'); this.shards=[]; this.build(); }
      build() {
        const skin=colorMat(0xf0d5ce,{roughness:.36,clearcoat:.58,sheen:new THREE.Color(0xffbfd5),emissive:0x2a1119,emissiveIntensity:.025});
        const hair=colorMat(0xe69abd,{roughness:.3,metalness:.12,clearcoat:.75,sheen:new THREE.Color(0xd8cbff)});
        const couture=colorMat(0x181421,{roughness:.3,metalness:.22,clearcoat:.48});
        const gold=goldMat(), crystal=colorMat(0xf7e6ff,{roughness:.06,metalness:.16,clearcoat:1,transparent:true,opacity:.92});
        lathe(this.bodyGroup,couture,[[.03,.11],[.51,.13],[.52,.21],[.4,.48],[.29,.77],[.23,1.08],[.2,1.19]],46);
        lathe(this.bodyGroup,couture,[[.03,1.02],[.2,1.04],[.235,1.28],[.2,1.43],[.17,1.49]],36);
        const necklace=addMesh(this.root,new THREE.TorusGeometry(.2,.009,8,28),gold); necklace.rotation.x=Math.PI/2; necklace.position.set(0,1.03,.04);
        sphere(this.root,crystal,[0,1.0,.23],[.025,.035,.012],12);
        cylinder(this.root,skin,[0,1.49,0],.064,.078,.25,16);
        this.headRig.position.y=1.79;
        sphere(this.headRig,skin,[0,0,0],[.27,.34,.235],30);
        // Twin buns and face-framing strands.
        [-1,1].forEach(side=>{
          sphere(this.headRig,hair,[side*.19,.34,-.035],[.13,.14,.12],22);
          const band=addMesh(this.headRig,new THREE.TorusGeometry(.09,.012,8,20),couture);band.position.set(side*.19,.3,-.035);band.rotation.x=1.25;
          tube(this.headRig,[[side*.12,.21,.14],[side*.16,.02,.16],[side*.2,-.19,.05]],.027,hair,8);
        });
        this.eyes=eyePair(this.headRig,{x:.09,y:.045,z:.203,radius:.06,iris:0x783a59});
        this.brows = eyeBrows(this.headRig,skin,standardMat(0x3e2534),{y:.15,z:.205,x:.09});
        sphere(this.headRig,skin,[0,-.07,.224],[.022,.03,.022],12);
        this.mouth=smile(this.headRig,[0,-.186,.208],.104,colorMat(0xd8517e,{roughness:.32,clearcoat:.55}),{c:[0,0,0],r:[.27,.34,.235]});
        const blushMat=colorMat(0xf0a4b9,{roughness:.55,transparent:true,opacity:.34});
        blush(this.headRig,-.15,-.085,.18,.045,blushMat);blush(this.headRig,.15,-.085,.18,.045,blushMat);
        // Pearls and tiny holographic facets are all individual procedural meshes.
        [[-.14,.11,.19],[.14,.11,.19],[0,.2,.211],[-.2,-.02,.11],[.2,-.02,.11],[0,-.03,.226]].forEach((p,i)=>pearl(this.headRig,p,i%2 ? .009 : .012));
        const shardMats=[0xf2d9ff,0xd4f6f0,0xffd8ea].map(c=>colorMat(c,{roughness:.055,metalness:.12,clearcoat:1,transparent:true,opacity:.9}));
        [[-.29,.12,.08],[.29,.12,.08],[-.2,.3,.04],[.2,.3,.04],[0,.39,.02]].forEach((p,i)=>{
          const shard=addMesh(this.headRig,new THREE.OctahedronGeometry(.025),shardMats[i%shardMats.length]);shard.position.set(p[0],p[1],p[2]);this.shards.push({mesh:shard,base:vec(p[0],p[1],p[2]),phase:i*1.4,speed:.7+i*.12});
        });
        const arms=createArms(this.root,{x:.24,y:1.4,z:.04,upper:.29,fore:.26,radius:.047,skinRadius:.05,sleeve:couture,skin:skin});this.armL=arms.L;this.armR=arms.R;
        // A raised display hand with four delicate crystal-tipped fingers.
        const displayHand=new THREE.Group();displayHand.position.set(0,-.035,.07);this.armR.hand.add(displayHand);
        sphere(displayHand,skin,[0,0,0],[.052,.067,.032],14);
        for(let i=0;i<4;i++){
          const finger=new THREE.Group();finger.position.set(-.036+i*.024,.04,.015);finger.rotation.z=(i-1.5)*.08;displayHand.add(finger);
          cylinder(finger,skin,[0,.047,0],.009,.008,.085,8);
          const nail=addMesh(finger,new THREE.OctahedronGeometry(.011),crystal);nail.position.set(0,.093,.003);nail.scale.y=1.45;
        }
        const thumb=cylinder(displayHand,skin,[.062,.01,.005],.01,.009,.065,8);thumb.rotation.z=-.8;
        this.animateExtra=(t)=>this.shards.forEach(s=>{
          const a=t*s.speed+s.phase;s.mesh.position.set(s.base.x+Math.cos(a)*.035,s.base.y+Math.sin(a*1.3)*.022,s.base.z+Math.sin(a)*.025);s.mesh.rotation.y=a*1.2;s.mesh.rotation.x=a*.7;
        });
      }
    }

    class PipCharacter extends CharacterBase {
      constructor() { super('Pip', 'Celestial Finch Muse', 'A tiny jewel-feathered friend, ready to add a little wonder to your bridal story.'); this.wings=[]; this.build(); }
      build() {
        const teal=colorMat(0x48aeb1,{roughness:.38,metalness:.08,clearcoat:.68,clearcoatRoughness:.24,sheen:new THREE.Color(0xb8f3dc)});
        const tealDeep=colorMat(0x267679,{roughness:.4,metalness:.12,clearcoat:.65,sheen:new THREE.Color(0x8ce2d2)});
        const belly=colorMat(0xf5dfca,{roughness:.58,sheen:new THREE.Color(0xffecd9)});
        const beakMat=colorMat(0xf49a68,{roughness:.28,clearcoat:.6,clearcoatRoughness:.2});
        const gold=goldMat(), coral=gemMat(0xe77773), eyeMat=colorMat(0x11131d,{roughness:.045,clearcoat:1,clearcoatRoughness:.025,envMapIntensity:1.5});
        // A round, collectible-creature silhouette with an original finch palette.
        sphere(this.bodyGroup,teal,[0,.72,-.02],[.45,.48,.4],32);
        sphere(this.bodyGroup,belly,[0,.68,.313],[.31,.34,.13],28);
        this.headRig.position.y=1.29;
        sphere(this.headRig,teal,[0,0,0],[.46,.47,.4],32);
        sphere(this.headRig,belly,[0,-.13,.318],[.3,.235,.13],24);
        // Oversized glossy eyes with paired glass catchlights.
        this.eyes=eyePair(this.headRig,{x:.165,y:.06,z:.352,radius:.115,dark:true});
        // Feather brow tufts. Pip had no brow channel at all, and brows carry
        // most of an expression -- that is why his face looked frozen.
        const browMat=colorMat(0x2e7f80,{roughness:.42,metalness:.06,clearcoat:.55});
        this.brows=eyeBrows(this.headRig,browMat,browMat,{y:.235,z:.340,x:.165,w:.060,h:.030,r:.011,ry:.5});
        // Soft apricot cheeks and a small split beak.
        const cheekMat=colorMat(0xf08f85,{roughness:.58,transparent:true,opacity:.55});
        blush(this.headRig,-.29,-.13,.324,.075,cheekMat);blush(this.headRig,.29,-.13,.324,.075,cheekMat);
        const beak=new THREE.Group(); beak.position.set(0,-.12,.441); this.headRig.add(beak);
        sphere(beak,beakMat,[0,0,0],[.105,.075,.105],20);
        const beakTip=addMesh(beak,new THREE.ConeGeometry(.092,.17,7),beakMat);beakTip.rotation.x=Math.PI/2;beakTip.position.set(0,-.05,.049);
        sphere(this.headRig,colorMat(0x8f5148,{roughness:.65}),[0,-.265,.396],[.035,.012,.012],12);
        // Birds have no lips, so Pip's "smile" IS the beak: the lower mandible
        // (the cone) drops as the mood opens up. Two little arcs on the cheeks
        // were tried first and read as a moustache, so they are gone.
        let beakTalk=0,beakC=0,beakO=0;
        const applyBeak=function(d){
          const open=Math.PI/2+(Math.max(0,beakO)+beakTalk)*.26;
          const cc=Math.max(-1.2,Math.min(1.8,beakC));
          if(G&&d!==0){
            G.to(beakTip.rotation,{x:open,duration:d||.45,ease:'power2.out',overwrite:true});
            G.to(beak.scale,{x:1+cc*.07,y:1-cc*.045,duration:d||.45,ease:'power2.out'});
          } else { beakTip.rotation.x=open; beak.scale.set(1+cc*.07,1-cc*.045,1); }
        };
        this.mouth={setMood:function(c,o,d){beakC=c||0;beakO=o||0;applyBeak(d);},
                    setTalk:function(v){beakTalk=Math.max(0,Math.min(1,v||0))*.9;applyBeak(0);}};
        // Three soft crest plumes and a real 3D crown.
        const plumeM=colorMat(0x65c2bb,{roughness:.38,metalness:.08,clearcoat:.65,sheen:new THREE.Color(0xffc8b7)});
        const plumes=[];
        for(let i=0;i<3;i++){
          const plume=addMesh(this.headRig,new THREE.ConeGeometry(.07,.23,12),i===1?coral:plumeM);
          plume.position.set((i-1)*.085,.43+Math.abs(i-1)*.015,-.005);plume.rotation.z=(i-1)*-.25;
          plumes.push({mesh:plume,baseZ:(i-1)*-.25});
        }
        this.plumes=plumes; this.plumeLift=0; this.plumeTarget=.5;
        // Floating crown, halo-style: it hovers clear of the skull with a real
        // gap and drifts, while the crest plumes reach up through the open
        // middle of the ring. Band underside sits .045 above the head top (.47).
        const CROWN_Y=.535;
        const crown=new THREE.Group(); crown.position.set(0,CROWN_Y,0); crown.scale.set(1,1,.87); this.headRig.add(crown);
        const pearlMat=colorMat(0xfff7e8,{roughness:.14,clearcoat:1,clearcoatRoughness:.08});
        const mint=gemMat(0x8dd4c0);
        const band=addMesh(crown,new THREE.TorusGeometry(.285,.026,12,40),gold); band.rotation.x=Math.PI/2;
        const bandTop=addMesh(crown,new THREE.TorusGeometry(.265,.010,10,36),gold); bandTop.rotation.x=Math.PI/2; bandTop.position.y=.042;
        const POINTS=7;
        for(let i=0;i<POINTS;i++){
          const a=(i+.5)/POINTS*Math.PI*2, sx=Math.sin(a)*.280, sz=Math.cos(a)*.280;
          const pivot=new THREE.Group(); pivot.position.set(sx,.02,sz); pivot.rotation.y=a; crown.add(pivot);
          const lean=new THREE.Group(); lean.rotation.x=-.08; pivot.add(lean);
          const spike=addMesh(lean,new THREE.ConeGeometry(.046,.095,4),gold); spike.position.y=.0475; spike.rotation.y=Math.PI/4;
          sphere(lean,pearlMat,[0,.105,0],[.022,.026,.022],14);
          sphere(crown,i%2?coral:mint,[sx,.033,sz],[.015,.015,.015],12);
        }
        const crownGem=addMesh(crown,new THREE.OctahedronGeometry(.036),mint); crownGem.position.set(0,.010,.320); crownGem.scale.set(.95,1.3,.6);
        this.crown=crown;
        this.tickers.push(t=>{ crown.position.y=CROWN_Y+Math.sin(t*1.15)*.014; crown.rotation.y=Math.sin(t*.42)*.10; });
        // Feathered wings and tail animate independently from the body.
        const wings=[];
        [-1,1].forEach(side=>{
          const wing=new THREE.Group();wing.position.set(side*.36,.78,-.01);this.root.add(wing);
          sphere(wing,tealDeep,[side*.015,0,0],[.19,.28,.13],22);
          for(let i=0;i<3;i++){
            const feather=sphere(wing,i===1?teal:plumeM,[side*(.045+i*.035),-.13-i*.015,.045],[.07,.16,.06],16);
            feather.rotation.z=side*(.22+i*.12);
          }
          wings.push({group:wing,side:side});
        });
        this.wings=wings;
        // Tail: five soft feathers. Each is a LATHED teardrop -- rounded at the
        // tip AND at the base -- flattened into a blade. Cones came to a hard
        // point, which is what made the tail look stabby.
        const tail=new THREE.Group(); tail.position.set(0,.58,-.30); tail.rotation.x=.20; this.root.add(tail);
        // Profile ends in a true hemispherical cap (last four points sweep a
        // quarter circle onto the axis) -- a profile that just runs to 0 still
        // revolves into a cone, which is the pointed look we are removing.
        const FEATHER=[[.007,0],[.026,.045],[.033,.105],[.031,.165],[.024,.215],[.018,.250],[.0156,.259],[.009,.2656],[0,.268]];
        const featherGeo=new THREE.LatheGeometry(FEATHER.map(p=>new THREE.Vector2(p[0],p[1])),12);
        for(let i=0;i<5;i++){
          const spread=(i-2)*.20, len=1-Math.abs(i-2)*.07;
          const feather=addMesh(tail,featherGeo,i===2?coral:tealDeep);
          feather.rotation.set(-Math.PI/2,0,spread);
          feather.scale.set(.95,len,.40);
          feather.position.set(Math.sin(spread)*.055,0,-.055-Math.abs(i-2)*.008);
        }
        // Gold collar, tiny amethyst pendant and orange toes.
        const collar=addMesh(this.root,new THREE.TorusGeometry(.25,.022,10,32),gold);collar.position.set(0,1.02,.05);collar.rotation.x=Math.PI/2;
        const pendant=addMesh(this.root,new THREE.OctahedronGeometry(.045),gemMat(0x9f71bd));pendant.position.set(0,.99,.29);pendant.scale.y=1.25;
        for(let side of [-1,1]){
          cylinder(this.root,beakMat,[side*.14,.18,.03],.027,.03,.17,12);
          sphere(this.root,beakMat,[side*.14,.105,.09],[.08,.045,.13],12);
          for(let toe=-1;toe<=1;toe++) tube(this.root,[[side*.14,.11,.1],[side*.14+toe*.035,.08,.17]],.012,beakMat,6);
        }
        const arms={L:{shoulder:wings[0].group,elbow:null,isWing:true},R:{shoulder:wings[1].group,elbow:null,isWing:true}};this.armL=arms.L;this.armR=arms.R;
        this.flap=1;
        this.animateExtra=(t)=>{
          // Wings also fold in the pose swing, so the "offering" stance reads on
          // a bird. update() deliberately skips wings, because animateExtra owns
          // their rotation.x -- so it has to be added here instead.
          wings.forEach(w=>{
            w.group.rotation.x=Math.sin(t*(this.emotion==='happy' ? 11 : 2.1)+w.side)*(.035+this.flap*(this.emotion==='happy' ? .18 : .025)) + this.armSwingX*.55;
          });
          // Crest: lifts and splays when bright, sweeps back and flattens when sad.
          this.plumeLift += (this.plumeTarget-this.plumeLift)*.09;
          this.plumes.forEach(p=>{
            p.mesh.rotation.z=p.baseZ*(1+this.plumeLift*.5);
            p.mesh.rotation.x=this.plumeLift<.3 ? (this.plumeLift-.3)*.55 : 0;
            const s=1+this.plumeLift*.13; p.mesh.scale.set(s,s,s);
          });
          tail.rotation.y=Math.sin(t*1.5)*.07;
        };
        /* Pip's own poke reaction: a burst of wing-beating and little hopped
           take-off attempts, head ducked and eyes sliding away = shy. */
        this.reactions=['shyFly','tickle','spin','startle'];
        this.react_shyFly=()=>{
          const prev=this.emotion, flap0=this.flap;
          this.flap=2.2; this.emotion='happy';
          if(this.eyes) this.eyes.mood(.5);
          if(this.onSpark) this.onSpark(vec(0,1.05,.25),10);
          const restore=()=>{ this.flap=flap0; this.setEmotion(prev,false); };
          if(!G){ window.setTimeout(restore,1300); return 1.4; }
          const tl=G.timeline({onComplete:restore});
          tl.to(this,{jump:.17,duration:.17,repeat:3,yoyo:true,ease:'power2.out'},0)
            .to(this,{wiggle:-.05,duration:.12,repeat:5,yoyo:true,ease:'sine.inOut'},0)
            .to(this.headTarget,{x:.15,z:.11,duration:.32,ease:'power2.out'},0)
            .to(this.gazeTarget,{x:-.45,y:-.5,duration:.32,ease:'power2.out'},0)
            .to(this.headTarget,{x:0,z:0,duration:.45,ease:'power2.inOut'},1.05)
            .to(this.gazeTarget,{x:0,y:0,duration:.45,ease:'power2.inOut'},1.05)
            .to(this,{jump:0,duration:.3,ease:'power2.out'},1.05)
            .to(this,{wiggle:0,duration:.3,ease:'power2.out'},1.05);
          return 1.55;
        };
        const PLUME_MOOD={happy:1.0,surprised:1.25,coupon:.85,welcome:.55,wink:.7,thinking:.3,waiting:.35,hesitant:.05,sad:-1.0};
        this.onMood=(mood)=>{
          this.flap=mood==='happy' ? 1.5 : (mood==='thinking' ? .25 : .65);
          this.plumeTarget=PLUME_MOOD[mood]!==undefined?PLUME_MOOD[mood]:.5;
          if((mood==='happy'||mood==='coupon')&&this.onSpark)this.onSpark(vec(.15,1.2,.4),mood==='coupon'?16:12);
        };
      }
    }

    const DEFINITIONS = [
      { id:'asha', name:'Asha', role:'Bridal Stylist', title:'Royal bridal stylist', blurb:'A warm welcome to a world of heirloom detail, velvet and gold.', color:'#db715b', Character:AshaCharacter, camera:[.2,1.53,5.35], target:[0,1.16,0] },
      { id:'mochi', name:'Mochi', role:'Velvet Bunny', title:'Luxury velvet mascot', blurb:'A cashmere-soft companion with a little emerald sparkle and a very big heart.', color:'#eee0cb', Character:MochiCharacter, camera:[.2,1.38,4.7], target:[0,1.21,0] },
      { id:'noor', name:'Noor', role:'Glamour Artist', title:'Parisian glamour artist', blurb:'Sculpted liner, a satin-lapel blazer and a golden brush for the finishing touch.', color:'#9c9bb7', Character:NoorCharacter, camera:[.22,1.56,5.25], target:[0,1.22,0] },
      { id:'tara', name:'Tara', role:'Heritage Guru', title:'Heritage drape & henna guru', blurb:'Emerald silk, temple gold and jasmine flowers guide every graceful detail.', color:'#4bb28a', Character:TaraCharacter, camera:[.25,1.57,5.45], target:[0,1.2,0] },
      { id:'gia', name:'Gia', role:'Crystal Icon', title:'Avant-garde crystal beauty icon', blurb:'A high-voltage beauty muse in iridescent rose, pearl stickers and crystal nail art.', color:'#ec9fc6', Character:GiaCharacter, camera:[.2,1.58,5.2], target:[0,1.24,0] },
      { id:'pip', name:'Pip', role:'Celestial Finch', title:'Celestial finch muse', blurb:'A tiny jewel-feathered friend, ready to add a little wonder to your bridal story.', color:'#76d4c2', Character:PipCharacter, camera:[.1,1.42,4.45], target:[0,1.18,0] }
    ];
    const WORDS = {
      welcome: {
        Asha:'Asha joins her palms. “Welcome, darling. Shall we begin?”',
        Mochi:'Mochi gives a little bunny bow and wiggles both ears.',
        Noor:'Noor offers the golden brush. “Ready when you are.”',
        Tara:'Tara lifts her palms. “May your day bloom beautifully.”',
        Gia:'Gia turns her crystal nails to the light. “Let us make it yours.”',
        Pip:'Pip flutters a tiny wing. A little wonder has arrived.'
      },
      happy: {
        Asha:'“Perfection. Absolutely perfection.”', Mochi:'Mochi bounces with pure bunny joy.', Noor:'Noor flashes a couture smile. The look is yours.',
        Tara:'Tara beams as her jasmine flowers sway.', Gia:'The crystals catch the light. Deal closed!', Pip:'Pip flaps with delight, crest feathers all a-twinkle.'
      },
      thinking: {
        Asha:'“Let me compare the heirloom details once more…”', Mochi:'Mochi tilts their head, paws hovering thoughtfully.', Noor:'“A touch more blend, then the perfect finish.”',
        Tara:'“One moment. The jasmine knows just where to begin.”', Gia:'“Considering every possible finish…”', Pip:'Pip studies the choices with one curious head tilt.'
      },
      hesitant: {
        Asha:'“Take all the time you need, dear.”', Mochi:'Mochi lowers their ears softly. There is no rush.', Noor:'Noor lowers the brush, patient and warm.',
        Tara:'Tara folds her hands and breathes with you.', Gia:'Gia softens her glow and listens.', Pip:'Pip settles close by. The choice can wait.'
      },
      sad: {
        Asha:'“Oh… that slot is gone. My heart sinks a little too.”', Mochi:'Mochi’s ears droop. A small cloud has passed by.',
        Noor:'“That shade is finished. I am so sorry, truly.”', Tara:'Tara lowers her eyes. “The season moved on without us.”',
        Gia:'Gia dims her crystals. “Not this time, sadly.”', Pip:'Pip’s crest flattens and the sparkle dims.'
      },
      waiting: {
        Asha:'“Shall I hold this look for you? No rush at all.”', Mochi:'Mochi waits, nose twitching, one ear half-cocked.',
        Noor:'“Take your time, darling. I will keep the brush warm.”', Tara:'Tara waits softly, jasmine steady in her hands.',
        Gia:'Gia tilts her head. “Still deciding? I have all day.”', Pip:'Pip hops once, then waits, head tilted.'
      },
      coupon: {
        Asha:'“For you — ten percent on the bridal package today.”', Mochi:'Mochi presents a tiny velvet coupon with both paws.',
        Noor:'“A little gift: a complimentary touch-up, on the house.”', Tara:'Tara offers a jasmine-wrapped coupon, smiling.',
        Gia:'“Your first glow-up session — fifteen percent off.”', Pip:'Pip holds up a shimmering coupon in one wing.'
      },
      wink: {
        Asha:'Asha winks. “Trust me, it will be stunning.”', Mochi:'Mochi winks one bright eye and flicks an ear.',
        Noor:'Noor winks. “That is the couturier’s promise.”', Tara:'Tara winks, and the jasmine seems to glow.',
        Gia:'Gia winks. “A little secret between us.”', Pip:'Pip winks a glossy eye, crest a-bounce.'
      },
      surprised: {
        Asha:'“Oh! What a bold, beautiful choice.”', Mochi:'Mochi’s ears shoot straight up in surprise.',
        Noor:'“Mon dieu — I did not see that coming!”', Tara:'Tara’s eyes widen. “What a wonderful turn.”',
        Gia:'Gia gasps, crystals flashing. “Unexpected. Perfect.”', Pip:'Pip’s crest shoots up with a startled cheep.'
      }
    };




    function makeEnvironment(targetRenderer) {
      if (!targetRenderer) return null;
      const canvas=document.createElement('canvas');canvas.width=512;canvas.height=256;
      const ctx=canvas.getContext('2d');
      const gradient=ctx.createLinearGradient(0,0,0,256);
      gradient.addColorStop(0,'#725638');gradient.addColorStop(.32,'#29221a');gradient.addColorStop(.64,'#121211');gradient.addColorStop(1,'#080809');
      ctx.fillStyle=gradient;ctx.fillRect(0,0,512,256);
      const boxes=[[85,55,42,130,'rgba(255,227,179,.9)'],[250,26,54,155,'rgba(190,205,255,.72)'],[410,75,38,118,'rgba(255,204,136,.8)'],[330,220,90,12,'rgba(255,244,220,.42)']];
      boxes.forEach(b=>{const gl=ctx.createLinearGradient(b[0],0,b[0]+b[2],0);gl.addColorStop(0,'rgba(255,255,255,0)');gl.addColorStop(.45,b[4]);gl.addColorStop(1,'rgba(255,255,255,0)');ctx.fillStyle=gl;ctx.fillRect(b[0],b[1],b[2],b[3]);});
      const texture=new THREE.CanvasTexture(canvas);texture.mapping=THREE.EquirectangularReflectionMapping;texture.encoding=THREE.sRGBEncoding;
      const pmrem=new THREE.PMREMGenerator(targetRenderer);pmrem.compileEquirectangularShader();
      const target=pmrem.fromEquirectangular(texture);texture.dispose();pmrem.dispose();
      return target.texture;
    }
    function makeSparkleTexture() {
      const c=document.createElement('canvas');c.width=c.height=64;
      const ctx=c.getContext('2d');const g=ctx.createRadialGradient(32,32,0,32,32,32);
      g.addColorStop(0,'rgba(255,255,255,1)');g.addColorStop(.24,'rgba(255,240,202,.9)');g.addColorStop(1,'rgba(255,210,128,0)');
      ctx.fillStyle=g;ctx.fillRect(0,0,64,64);const t=new THREE.CanvasTexture(c);t.encoding=THREE.sRGBEncoding;return t;
    }


  return {
    CharacterBase: CharacterBase,
    MochiCharacter: MochiCharacter,
    PipCharacter: PipCharacter,
    AshaCharacter: AshaCharacter,
    DEFINITIONS: DEFINITIONS,
    WORDS: WORDS,
    MOODS: MOODS,
    POSES: POSES,
    makeEnvironment: makeEnvironment,
    makeSparkleTexture: makeSparkleTexture,
    vec: vec
  };
}));
