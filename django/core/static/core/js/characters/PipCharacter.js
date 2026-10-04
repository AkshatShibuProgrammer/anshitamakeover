/**
 * PipCharacter (v1.0.0)
 * Standalone 3D Procedural Celestial Finch Mascot ("Pip") for Anshita Makeover
 * Featuring jewel feathers, splaying crest plumes, floating halo crown, wing flutter, and emotion engine.
 */
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['three'], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory(require('three'));
  } else {
    root.PipCharacter = factory(root.THREE);
  }
}(typeof self !== 'undefined' ? self : this, function (THREE) {
  'use strict';

  if (!THREE) {
    console.error('PipCharacter requires Three.js (r128+).');
    return null;
  }

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
  function tube(parent, points, radius, material, radialSegments = 8) {
    const curve = new THREE.CatmullRomCurve3(points.map(p => vec(p[0], p[1], p[2])));
    return addMesh(parent, new THREE.TubeGeometry(curve, Math.max(18, points.length * 8), radius, radialSegments, false), material);
  }

  function eyePair(parent, options = {}) {
    const settings = Object.assign({ x: .165, y: .06, z: .352, radius: .115 }, options);
    const eyes = [];
    const G = window.gsap || null;
    [-1, 1].forEach(side => {
      const eye = new THREE.Group();
      eye.position.set(side * settings.x, settings.y, settings.z);
      eye.rotation.y = side * 0.07;
      parent.add(eye);

      const r = settings.radius;
      const irisGroup = new THREE.Group();
      eye.add(irisGroup);

      // Oversized glossy dark eye with paired sparkles
      sphere(irisGroup, colorMat(0x101018, { roughness: .04, clearcoat: 1, envMapIntensity: 2.0 }), [0, 0, 0.01], [r * 1.22, r * 1.28, 0.18], 22);
      const catchMat = colorMat(0xffffff, { roughness: .01, clearcoat: 1, emissive: 0xffffff, emissiveIntensity: 1.0 });
      const c1 = sphere(irisGroup, catchMat, [-r * 0.42, r * 0.45, 0.18], [r * 0.42, r * 0.45, 0.11], 14);
      c1.castShadow = false;
      const c2 = sphere(irisGroup, catchMat, [r * 0.40, -r * 0.30, 0.17], [r * 0.20, r * 0.20, 0.09], 12);
      c2.castShadow = false;
      const c3 = sphere(irisGroup, catchMat, [r * 0.28, r * 0.48, 0.17], [r * 0.12, r * 0.12, 0.07], 10);
      c3.castShadow = false;

      eyes.push({ eye: eye, iris: irisGroup, baseY: eye.scale.y });
    });

    const api = { moodValue: 1, eyes: eyes };
    return Object.assign(api, {
      gaze(x, y) { eyes.forEach(e => { e.iris.position.x = x * .018; e.iris.position.y = -y * .014; }); },
      blink() {
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
      }
    });
  }

  function eyeBrows(parent, hairMat, options = {}) {
    const y = options.y || .235, z = options.z || .340, x = options.x || .165;
    const bw = options.w || .060, bh = options.h || .030, br = options.r || .011;
    const brows = [];
    const G = window.gsap || null;
    [-1, 1].forEach(side => {
      const pivot = new THREE.Group();
      pivot.position.set(side * x, y, z);
      if (options.ry) pivot.rotation.y = side * options.ry;
      parent.add(pivot);
      tube(pivot, [[-bw, 0, 0], [0, bh, .004], [bw, 0, 0]], br, hairMat, 7);
      brows.push({ pivot: pivot, side: side });
    });
    return {
      // Exposed so the draw-call optimiser can treat the brow pivots as motion
      // nodes (they lift/tilt on emotion changes).
      pivots: brows.map(b => b.pivot),
      set(raise, tilt) {
        brows.forEach(b => {
          const dy = (raise || 0) * .024;
          const rz = (tilt || 0) * b.side * .36;
          if (G) {
            G.to(b.pivot.position, { y: dy, duration: .5, ease: 'power2.out', overwrite: true });
            G.to(b.pivot.rotation, { z: rz, duration: .5, ease: 'power2.out', overwrite: true });
          } else { b.pivot.position.y = dy; b.pivot.rotation.z = rz; }
        });
      }
    };
  }

  function blush(parent, x, y, z, radius, material) {
    return sphere(parent, material, [x, y, z], [radius, radius * .63, radius * .22], 16);
  }

  class PipCharacter {
    constructor(options = {}) {
      this.canvas = typeof options.canvas === 'string'
        ? document.querySelector(options.canvas)
        : (options.canvas || options.target);

      if (!this.canvas) {
        throw new Error('PipCharacter: A valid canvas must be provided.');
      }

      this.width = options.width || this.canvas.clientWidth || 240;
      this.height = options.height || this.canvas.clientHeight || 240;
      this.interactiveCursor = options.interactiveCursor !== false;
      this.autoBlink = options.autoBlink !== false;

      this.wings = [];
      this.tickers = [];
      this.gaze = { x: 0, y: 0 };
      this.gazeTarget = { x: 0, y: 0 };
      this.headTarget = { x: 0, y: 0, z: 0 };
      this.emotion = options.initialEmotion || 'welcome';
      this.jump = 0;
      this.blinkTimer = 2.2 + Math.random() * 2.5;
      this.blinkElapsed = 0;
      this.breath = 1;
      this.squash = 1;
      this.stanceY = 0;
      this.hipBase = 0;
      this.wiggle = 0;
      this.spin = 0;
      this.flap = 1;
      this.plumeLift = 0;
      this.plumeTarget = 0.5;
      this.phase = Math.random() * Math.PI * 2;

      // ── Scroll-scrubbed walk state (mascot-scroll-engine.js) ────────────
      this.walk = {
        progress: 0,
        gaitPhase: 0,
        locomotion: 0,
        speed: 0,
        direction: 1,
        docked: false,
        phase: 'hidden',
        hopAmplitude: 0.20,
        wingFlutter: 0.05
      };
      this.paused = false;

      this.initScene();
      this.build();
      this.setupListeners();
      this.start();
    }

    initScene() {
      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(34, this.width / this.height, 0.1, 50);
      this.camera.position.set(0, 1.25, 4.0);
      this.camera.lookAt(0, 1.05, 0);

      this.renderer = new THREE.WebGLRenderer({
        canvas: this.canvas,
        alpha: true,
        antialias: true,
        powerPreference: 'high-performance'
      });
      this.renderer.setSize(this.width, this.height, false);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

      // ── Studio treatment (parity with Mochi) ─────────────────────────
      const studio = window.StudioTreatment;
      if (studio) {
        studio.applyRendererPipeline(this.renderer, { exposure: 1.05 });
        this.envMap = studio.buildStudioEnvironment(this.renderer);
        if (this.envMap) this.scene.environment = this.envMap;
        this.lights = studio.createStudioLights(this.scene, { scale: 1 });
        this.shadowCatcher = studio.createShadowCatcher({ size: 8, y: 0, opacity: 0.32 });
        this.scene.add(this.shadowCatcher);
      } else {
        const ambient = new THREE.AmbientLight(0xf0fbf9, 1.15);
        this.scene.add(ambient);
        const keyLight = new THREE.DirectionalLight(0xfff1e0, 1.35);
        keyLight.position.set(2.4, 3.8, 3.2);
        this.scene.add(keyLight);
        const fillLight = new THREE.DirectionalLight(0xd4f5f1, 0.75);
        fillLight.position.set(-2.4, 1.8, 2.2);
        this.scene.add(fillLight);
        const rimLight = new THREE.DirectionalLight(0xc8a96a, 0.95);
        rimLight.position.set(0, 3.2, -2.5);
        this.scene.add(rimLight);
      }
    }

    build() {
      this.root = new THREE.Group();
      this.root.position.y = 0.10;
      this.scene.add(this.root);

      this.bodyGroup = new THREE.Group();
      this.root.add(this.bodyGroup);

      this.headRig = new THREE.Group();
      this.root.add(this.headRig);

      const teal = colorMat(0x48aeb1, { roughness: .38, metalness: .08, clearcoat: .68, clearcoatRoughness: .24, sheen: new THREE.Color(0xb8f3dc) });
      const tealDeep = colorMat(0x267679, { roughness: .4, metalness: .12, clearcoat: .65, sheen: new THREE.Color(0x8ce2d2) });
      const belly = colorMat(0xf5dfca, { roughness: .58, sheen: new THREE.Color(0xffecd9) });
      const beakMat = colorMat(0xf49a68, { roughness: .28, clearcoat: .6, clearcoatRoughness: .2 });
      const gold = goldMat(), coral = gemMat(0xe77773);

      // Feather palette merged into one vertex-coloured material after the
      // build (audit §8.2 draw-call budget). The transparent cheek blush is
      // deliberately excluded.
      this.palette = { teal: teal, tealDeep: tealDeep, belly: belly, beak: beakMat };

      // Body & belly
      sphere(this.bodyGroup, teal, [0, .72, -.02], [.45, .48, .4], 32);
      sphere(this.bodyGroup, belly, [0, .68, .313], [.31, .34, .13], 28);

      // Head
      this.headRig.position.y = 1.29;
      sphere(this.headRig, teal, [0, 0, 0], [.46, .47, .4], 32);
      sphere(this.headRig, belly, [0, -.13, .318], [.3, .235, .13], 24);

      // Big glossy eyes
      this.eyes = eyePair(this.headRig, { x: .165, y: .06, z: .352, radius: .115 });

      // Feather brow tufts
      const browMat = colorMat(0x2e7f80, { roughness: .42, metalness: .06, clearcoat: .55 });
      this.brows = eyeBrows(this.headRig, browMat, { y: .235, z: .340, x: .165, w: .060, h: .030, r: .011, ry: .5 });

      // Soft apricot cheeks
      const cheekMat = colorMat(0xf08f85, { roughness: .58, transparent: true, opacity: .55 });
      blush(this.headRig, -.29, -.13, .324, .075, cheekMat);
      blush(this.headRig, .29, -.13, .324, .075, cheekMat);

      // Split beak
      const beak = new THREE.Group();
      beak.position.set(0, -.12, .441);
      this.headRig.add(beak);
      this.beak = beak;
      sphere(beak, beakMat, [0, 0, 0], [.105, .075, .105], 20);
      const beakTip = addMesh(beak, new THREE.ConeGeometry(.092, .17, 7), beakMat);
      beakTip.rotation.x = Math.PI / 2;
      beakTip.position.set(0, -.05, .049);
      // The tip opens on mood changes — never weld it to the beak sphere.
      beakTip.userData.noMerge = true;
      sphere(this.headRig, colorMat(0x8f5148, { roughness: .65 }), [0, -.265, .396], [.035, .012, .012], 12);

      const G = window.gsap || null;
      this.mouth = {
        setMood: function (c, o, d) {
          const open = Math.PI / 2 + Math.max(0, o || 0) * .26;
          const cc = Math.max(-1.2, Math.min(1.8, c || 0));
          if (G) {
            G.to(beakTip.rotation, { x: open, duration: d || .45, ease: 'power2.out', overwrite: true });
            G.to(beak.scale, { x: 1 + cc * .07, y: 1 - cc * .045, duration: d || .45, ease: 'power2.out' });
          } else {
            beakTip.rotation.x = open;
            beak.scale.set(1 + cc * .07, 1 - cc * .045, 1);
          }
        }
      };

      // Three soft crest plumes
      const plumeM = colorMat(0x65c2bb, { roughness: .38, metalness: .08, clearcoat: .65, sheen: new THREE.Color(0xffc8b7) });
      const plumes = [];
      for (let i = 0; i < 3; i++) {
        const plume = addMesh(this.headRig, new THREE.ConeGeometry(.07, .23, 12), i === 1 ? coral : plumeM);
        plume.position.set((i - 1) * .085, .43 + Math.abs(i - 1) * .015, -.005);
        plume.rotation.z = (i - 1) * -.25;
        plumes.push({ mesh: plume, baseZ: (i - 1) * -.25 });
      }
      this.plumes = plumes;

      // Floating halo crown
      const crown = new THREE.Group();
      crown.position.set(0, .535, 0);
      crown.scale.set(1, 1, .87);
      this.headRig.add(crown);
      this.crown = crown;

      const pearlMat = colorMat(0xfff7e8, { roughness: .14, clearcoat: 1, clearcoatRoughness: .08 });
      const mint = gemMat(0x8dd4c0);
      const band = addMesh(crown, new THREE.TorusGeometry(.285, .026, 12, 40), gold);
      band.rotation.x = Math.PI / 2;
      const bandTop = addMesh(crown, new THREE.TorusGeometry(.265, .010, 10, 36), gold);
      bandTop.rotation.x = Math.PI / 2;
      bandTop.position.y = .042;

      for (let i = 0; i < 7; i++) {
        const a = (i + .5) / 7 * Math.PI * 2, sx = Math.sin(a) * .280, sz = Math.cos(a) * .280;
        const pivot = new THREE.Group();
        pivot.position.set(sx, .02, sz);
        pivot.rotation.y = a;
        crown.add(pivot);
        const lean = new THREE.Group();
        lean.rotation.x = -.08;
        pivot.add(lean);
        const spike = addMesh(lean, new THREE.ConeGeometry(.046, .095, 4), gold);
        spike.position.y = .0475;
        spike.rotation.y = Math.PI / 4;
        sphere(lean, pearlMat, [0, .105, 0], [.022, .026, .022], 14);
        sphere(crown, i % 2 ? coral : mint, [sx, .033, sz], [.015, .015, .015], 12);
      }
      this.tickers.push(t => { crown.position.y = .535 + Math.sin(t * 1.15) * .014; crown.rotation.y = Math.sin(t * .42) * .10; });

      // Feathered wings
      const wings = [];
      [-1, 1].forEach(side => {
        const wing = new THREE.Group();
        wing.position.set(side * .36, .78, -.01);
        this.root.add(wing);
        sphere(wing, tealDeep, [side * .015, 0, 0], [.19, .28, .13], 22);
        for (let i = 0; i < 3; i++) {
          const feather = sphere(wing, i === 1 ? teal : plumeM, [side * (.045 + i * .035), -.13 - i * .015, .045], [.07, .16, .06], 16);
          feather.rotation.z = side * (.22 + i * .12);
        }
        wings.push({ group: wing, side: side });
      });
      this.wings = wings;

      // Soft lathed tail (kept on the instance: it fans during the walk cycle)
      const tail = new THREE.Group();
      this.tail = tail;
      this.tailFeathers = [];
      tail.position.set(0, .58, -.30);
      tail.rotation.x = .20;
      this.root.add(tail);
      const FEATHER = [[.007, 0], [.026, .045], [.033, .105], [.031, .165], [.024, .215], [.018, .250], [.0156, .259], [.009, .2656], [0, .268]];
      const featherGeo = new THREE.LatheGeometry(FEATHER.map(p => new THREE.Vector2(p[0], p[1])), 12);
      for (let i = 0; i < 5; i++) {
        const spread = (i - 2) * .20, len = 1 - Math.abs(i - 2) * .07;
        const feather = addMesh(tail, featherGeo, i === 2 ? coral : tealDeep);
        feather.rotation.set(-Math.PI / 2, 0, spread);
        feather.scale.set(.95, len, .40);
        feather.position.set(Math.sin(spread) * .055, 0, -.055 - Math.abs(i - 2) * .008);
        this.tailFeathers.push({ mesh: feather, baseSpread: spread, index: i });
      }

      // Gold collar & pendant
      const collar = addMesh(this.root, new THREE.TorusGeometry(.25, .022, 10, 32), gold);
      collar.position.set(0, 1.02, .05);
      collar.rotation.x = Math.PI / 2;
      const pendant = addMesh(this.root, new THREE.OctahedronGeometry(.045), gemMat(0x9f71bd));
      pendant.position.set(0, .99, .29);
      pendant.scale.y = 1.25;

      // Orange toes — grouped so the walk scrub can step them alternately
      this.feet = [];
      for (let side of [-1, 1]) {
        const leg = new THREE.Group();
        leg.position.set(side * .14, .18, .03);
        this.root.add(leg);
        cylinder(leg, beakMat, [0, 0, 0], .027, .03, .17, 12);
        sphere(leg, beakMat, [0, -.075, .06], [.08, .045, .13], 12);
        this.feet.push({ group: leg, side: side, baseY: .18, baseZ: .03, phase: side < 0 ? 0 : Math.PI });
      }

      // Crest plumes rebuild neither geometry nor material but are animated
      // per-mesh, so the optimizer must treat each one as a motion node.
      (this.plumes || []).forEach(p => { if (p.mesh) p.mesh.userData.noMerge = true; });
      (this.brows && this.brows.pivots ? this.brows.pivots : []).forEach(p => { p.userData.noMerge = true; });
      if (this.tailFeathers) this.tailFeathers.forEach(f => { if (f.mesh) f.mesh.userData.noMerge = true; });

      this.optimizeDrawCalls();
    }

    /**
     * Bake static decorations into merged geometries (audit §8.2: <25 draw
     * calls for the whole mascot). Motion nodes — wings, plumes, tail
     * feathers, beak, feet, eyes — are declared so nothing that moves gets
     * welded to something that does not.
     */
    optimizeDrawCalls() {
      const opt = window.AnshitaRigOptimizer;
      if (!opt || !this.root) return 0;
      const animated = [this.root, this.bodyGroup, this.headRig, this.tail, this.crown];
      if (this.eyes && this.eyes.eyes) {
        this.eyes.eyes.forEach(e => { animated.push(e.eye); animated.push(e.iris); });
      }
      (this.wings || []).forEach(w => animated.push(w.group));
      (this.feet || []).forEach(f => animated.push(f.group));
      (this.plumes || []).forEach(p => animated.push(p.mesh));
      (this.tailFeathers || []).forEach(f => animated.push(f.mesh));
      (this.brows && this.brows.pivots ? this.brows.pivots : []).forEach(p => animated.push(p));
      if (this.beak) animated.push(this.beak);
      (this.extraMotionNodes || []).forEach(n => animated.push(n));
      this.drawCallMergeSaved = opt.mergeStaticByMaterial(this.root, animated);
      if (this.palette && opt.mergeMaterialFamily) {
        const family = Object.keys(this.palette).map(k => this.palette[k]);
        this.drawCallMergeSaved += opt.mergeMaterialFamily(
          this.root, family, animated, { name: 'feathers' });
      }
      if (window.StudioTreatment && window.StudioTreatment.lineariseMaterials) {
        window.StudioTreatment.lineariseMaterials(this.scene);
      }
      return this.drawCallMergeSaved;
    }

    setupListeners() {
      this._listeners = this._listeners || [];
      const add = (type, fn, opts) => {
        window.addEventListener(type, fn, opts);
        this._listeners.push({ type: type, fn: fn, opts: opts });
      };

      if (this.interactiveCursor) {
        add('mousemove', (e) => {
          const rect = this.canvas.getBoundingClientRect();
          const cx = rect.left + rect.width / 2;
          const cy = rect.top + rect.height / 2;
          this.gazeTarget.x = Math.max(-1, Math.min(1, (e.clientX - cx) / (window.innerWidth / 2)));
          this.gazeTarget.y = Math.max(-1, Math.min(1, (e.clientY - cy) / (window.innerHeight / 2)));
        }, { passive: true });
      }

      add('resize', () => {
        if (!this.canvas) return;
        // The scroll engine owns sizing while the rig is on the walk stage.
        if (this.walkOwner) return;
        const w = this.canvas.clientWidth || 240;
        const h = this.canvas.clientHeight || 240;
        if (w !== this.width || h !== this.height) {
          this.width = w;
          this.height = h;
          this.camera.aspect = w / h;
          this.camera.updateProjectionMatrix();
          this.renderer.setSize(w, h, false);
        }
      });
    }

    setEmotion(moodName) {
      this.emotion = moodName;
      const G = window.gsap || null;
      if (moodName === 'happy' || moodName === 'excited') {
        this.flap = 1.8;
        this.plumeTarget = 1.1;
        if (this.eyes) this.eyes.mood(0.5);
        if (this.mouth && this.mouth.setMood) this.mouth.setMood(1.5, 0.45);
        if (G) G.to(this, { jump: 0.15, duration: 0.18, repeat: 1, yoyo: true, ease: 'power2.out' });
      } else if (moodName === 'sad' || moodName === 'hesitant') {
        this.flap = 0.4;
        this.plumeTarget = 0.1;
        if (this.eyes) this.eyes.mood(0.8);
        if (this.mouth && this.mouth.setMood) this.mouth.setMood(0.2, 0.1);
      } else {
        this.flap = 0.8;
        this.plumeTarget = 0.5;
        if (this.eyes) this.eyes.mood(1.0);
        if (this.mouth && this.mouth.setMood) this.mouth.setMood(1.0, 0);
      }
    }

    start() {
      this.isRunning = true;
      this.clock = new THREE.Clock();
      const animate = () => {
        if (!this.isRunning) return;
        this._rafId = requestAnimationFrame(animate);
        const dt = Math.min(this.clock.getDelta(), 0.1);
        const time = this.clock.getElapsedTime();

        // Battery gate (audit §3): hidden tabs and paused rigs cost zero GPU.
        if (this.paused || (typeof document !== 'undefined' && document.hidden)) return;

        this.applyWalkPose(dt);

        const breath = Math.sin(time * 1.85 + this.phase) * .009;
        this.bodyGroup.scale.set(this.squash, (1 + breath) / Math.sqrt(this.squash), this.squash);
        this.root.position.y = 0.10 + Math.sin(time * 1.35 + this.phase) * .012 + this.jump +
          this.stanceY + (this.walkAerial || 0);
        this.root.rotation.x = this.walkLean || 0;
        this.root.rotation.y = this.spin + (this.walkYaw || 0);

        // Wing flutter (emotion-driven, plus the walk-cycle flutter channel)
        const flutterRate = this.emotion === 'happy' ? 12 : 2.2;
        this.wings.forEach(w => {
          w.group.rotation.x = Math.sin(time * flutterRate + w.side) *
            (.035 + this.flap * .03 + (this.walkWingFlutter || 0));
          w.group.rotation.z = w.side * ((this.walkWingSpread || 0) * .28);
        });

        // Crest plume animation
        this.plumeLift += (this.plumeTarget - this.plumeLift) * .09;
        this.plumes.forEach(p => {
          p.mesh.rotation.z = p.baseZ * (1 + this.plumeLift * .5);
          const s = 1 + this.plumeLift * .12;
          p.mesh.scale.set(s, s, s);
        });

        this.gaze.x += (this.gazeTarget.x - this.gaze.x) * Math.min(1, dt * 4);
        this.gaze.y += (this.gazeTarget.y - this.gaze.y) * Math.min(1, dt * 4);
        this.headRig.rotation.x = this.headTarget.x + this.gaze.y * .11;
        this.headRig.rotation.y = this.headTarget.y + this.gaze.x * .18;

        if (this.eyes) this.eyes.gaze(this.gaze.x, this.gaze.y);

        this.blinkElapsed += dt;
        if (this.blinkElapsed >= this.blinkTimer) {
          if (this.eyes && this.autoBlink) this.eyes.blink();
          this.blinkElapsed = 0;
          this.blinkTimer = 2.2 + Math.random() * 3.5;
        }

        this.tickers.forEach(fn => fn(time, dt));
        this.renderer.render(this.scene, this.camera);
      };
      animate();
    }

    /* ══════════════════════════════════════════════════════════════════════
       SCROLL-SCRUBBED AVIAN LOCOMOTION  (spec §4.2 / §6)
       Pip walks with a bobbing strut instead of a hop: alternating toe steps,
       wing flutter that rises with scroll velocity, tail fan spread while
       travelling, and the same landing squash.
       ══════════════════════════════════════════════════════════════════════ */

    scrub(progress, opts) {
      opts = opts || {};
      const w = this.walk;
      w.progress = Math.max(0, Math.min(1, Number(progress) || 0));
      if (typeof opts.gaitPhase === 'number') w.gaitPhase = opts.gaitPhase;
      if (typeof opts.direction === 'number') w.direction = opts.direction;
      if (typeof opts.speed === 'number') w.speed = opts.speed;
      if (typeof opts.phase === 'string') w.phase = opts.phase;
      if (typeof opts.docked === 'boolean') w.docked = opts.docked;
      if (typeof opts.hopAmplitudePx === 'number') {
        w.hopAmplitude = Math.max(.10, Math.min(.40, opts.hopAmplitudePx / 130));
      }
      const target = (typeof opts.locomotion === 'number' ? opts.locomotion : 1) * (w.docked ? 0 : 1);
      w.locomotion += (target - w.locomotion) * .25;
      return this;
    }

    applyWalkPose(dt) {
      const w = this.walk;
      const loco = w.locomotion;
      const gait = w.gaitPhase;

      if (loco < .0005) {
        this.walkAerial = (this.walkAerial || 0) * Math.max(0, 1 - dt * 8);
        this.walkLean = (this.walkLean || 0) * Math.max(0, 1 - dt * 8);
        this.walkYaw = (this.walkYaw || 0) * Math.max(0, 1 - dt * 8);
        this.walkWingFlutter = (this.walkWingFlutter || 0) * Math.max(0, 1 - dt * 6);
        this.walkWingSpread = (this.walkWingSpread || 0) * Math.max(0, 1 - dt * 6);
        this.squash = 1 + (this.squash - 1) * Math.max(0, 1 - dt * 8);
        if (this.feet) {
          this.feet.forEach(f => {
            f.group.position.y += (f.baseY - f.group.position.y) * Math.min(1, dt * 8);
            f.group.rotation.x *= Math.max(0, 1 - dt * 8);
          });
        }
        if (this.tailFeathers) {
          this.tailFeathers.forEach(f => {
            f.mesh.rotation.z += (f.baseSpread - f.mesh.rotation.z) * Math.min(1, dt * 5);
          });
        }
        return;
      }

      const bob = Math.abs(Math.sin(gait));      // double-support strut
      const stride = Math.sin(gait);

      // 1. Avian bob: smaller aerial arc than the bunny hop.
      this.walkAerial = loco * bob * w.hopAmplitude;
      this.squash = 1 - loco * (1 - bob) * .04 + loco * bob * .02;

      // 2. Wing flutter couples to scroll velocity (§2.2 direct velocity coupling).
      this.walkWingFlutter = loco * (.05 + w.speed * .12);
      this.walkWingSpread = loco * (.35 + bob * .4);

      // 3. Alternating toe steps with a slight forward push.
      if (this.feet) {
        this.feet.forEach(f => {
          const local = Math.sin(gait + f.phase);
          f.group.position.y = f.baseY + Math.max(0, local) * .045 * loco;
          f.group.position.z = f.baseZ + local * .035 * loco;
          f.group.rotation.x = local * .30 * loco;
        });
      }

      // 4. Tail fan opens as Pip travels, closing when it settles.
      if (this.tailFeathers) {
        this.tailFeathers.forEach(f => {
          const fan = f.baseSpread + (f.index - 2) * .12 * loco;
          f.mesh.rotation.z += (fan - f.mesh.rotation.z) * Math.min(1, dt * 6);
        });
      }
      if (this.tail) this.tail.rotation.x = .20 + Math.sin(gait * 1.6) * .05 * loco;

      // 5. Forward lean + facing the direction of travel.
      this.walkLean = -.045 * loco;
      const facing = w.phase === 'docking' ? 0 : (w.direction >= 0 ? -.16 : .16);
      this.walkYaw = facing * loco * (w.phase === 'walking' ? 1 : .5);
    }

    dock() {
      this.walk.docked = true;
      this.walk.locomotion = 0;
      this.walkAerial = 0;
      this.walkLean = 0;
      this.walkYaw = 0;
      this.walkWingFlutter = 0;
      this.walkWingSpread = 0;
      this.squash = 1;
      return this;
    }

    undock() {
      this.walk.docked = false;
      return this;
    }

    pause() {
      this.paused = true;
      return this;
    }

    resume() {
      this.paused = false;
      if (this.clock) this.clock.getDelta();
      return this;
    }

    destroy() {
      this.isRunning = false;
      this.paused = true;
      if (this._rafId) cancelAnimationFrame(this._rafId);
      if (this._listeners) {
        this._listeners.forEach(l => {
          try { window.removeEventListener(l.type, l.fn, l.opts); } catch (e) { /* noop */ }
        });
        this._listeners = [];
      }
      if (this.scene) {
        const seenGeo = new Set(), seenMat = new Set(), seenTex = new Set();
        this.scene.traverse(node => {
          if (node.geometry && !seenGeo.has(node.geometry)) {
            seenGeo.add(node.geometry);
            node.geometry.dispose();
          }
          const materials = Array.isArray(node.material) ? node.material : (node.material ? [node.material] : []);
          materials.forEach(mat => {
            if (seenMat.has(mat)) return;
            seenMat.add(mat);
            ['map', 'alphaMap', 'normalMap', 'roughnessMap', 'metalnessMap',
              'emissiveMap', 'envMap', 'sheenColorMap', 'clearcoatMap'].forEach(slot => {
                const tex = mat[slot];
                if (tex && tex.isTexture && !seenTex.has(tex)) {
                  seenTex.add(tex);
                  tex.dispose();
                }
              });
            mat.dispose();
          });
        });
        while (this.scene.children.length) this.scene.remove(this.scene.children[0]);
      }
      if (this.envMap && this.envMap.dispose) this.envMap.dispose();
      if (this.renderer) {
        this.renderer.dispose();
        if (this.renderer.forceContextLoss) {
          try { this.renderer.forceContextLoss(); } catch (e) { /* noop */ }
        }
      }
      this.eyes = this.mouth = this.tickers = this.wings = this.feet = this.tailFeathers = null;
      this.destroyed = true;
      return this;
    }
  }

  return PipCharacter;
}));
