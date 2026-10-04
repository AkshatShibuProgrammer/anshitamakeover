/**
 * GltfWalkCharacter (v1.0.0)
 * Real-model concierge rig for Anshita Makeover — the "authentic locomotion"
 * path described by the audit (§6/§8.1).
 *
 * Mochi (models/mochi.glb, a skinned fox with native Walk/Run/Survey clips) and
 * Pip (models/pip.glb, a parrot with a flap clip) are loaded with GLTFLoader and
 * driven *entirely by scroll progress*: the walk clip's timeline is scrubbed —
 * never played in real time — so the gait is locked to scroll pixels exactly
 * like a scrubbed video. Stopping mid-scroll freezes mid-stride.
 *
 * Contract parity with MochiCharacter/PipCharacter (engine + regression suite):
 *   scrub(progress, opts) · applyWalkPose(dt) · dock() · undock()
 *   pause() · resume() · destroy() · setEmotion() · start()
 *   .root .camera .renderer .scene .canvas .walk .gazeTarget .headTarget
 *
 * Everything the rig allocates is released in destroy() (audit §7.1 WebGL
 * memory discipline): geometries, materials, textures, the mixer and finally
 * the GL context via forceContextLoss().
 */
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['three'], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory(require('three'));
  } else {
    root.GltfWalkCharacter = factory(root.THREE);
  }
}(typeof self !== 'undefined' ? self : this, function (THREE) {
  'use strict';

  if (!THREE) {
    console.error('GltfWalkCharacter requires Three.js (r128+).');
    return null;
  }

  // Preferred clip names per phase, first match wins.
  var CLIP_PREFS = {
    idle: ['Survey', 'Idle', 'idle', 'parrot_A_', 'flamingo_flyA_'],
    walk: ['Walk', 'walk', 'Run', 'run', 'parrot_A_'],
    run: ['Run', 'run', 'Walk', 'walk']
  };

  function pickClip(clips, prefs) {
    if (!clips || !clips.length) return null;
    for (var i = 0; i < prefs.length; i++) {
      for (var j = 0; j < clips.length; j++) {
        if (clips[j].name === prefs[i]) return clips[j];
      }
    }
    return clips[0];
  }

  function hexToLinearColor(hex) {
    // three r128 has no colour management: authored sRGB needs the conversion
    // or every surface desaturates (the reference studio's LC() helper).
    return new THREE.Color(hex).convertSRGBToLinear();
  }

  class GltfWalkCharacter {

    constructor(options = {}) {
      this.canvas = typeof options.canvas === 'string'
        ? document.querySelector(options.canvas)
        : (options.canvas || options.target);

      if (!this.canvas) throw new Error('GltfWalkCharacter: a valid canvas is required.');

      this.modelUrl = options.modelUrl;
      if (!this.modelUrl) throw new Error('GltfWalkCharacter: modelUrl is required.');

      this.id = options.id || 'mascot';
      this.width = options.width || this.canvas.clientWidth || 240;
      this.height = options.height || this.canvas.clientHeight || 240;
      this.interactiveCursor = options.interactiveCursor !== false;
      this.durationScale = options.durationScale || 1;
      this.groundOffset = options.groundOffset || 0;

      // Motion state (mutated by the scroll engine via scrub()).
      this.walk = {
        progress: 0, gaitPhase: 0, locomotion: 0, speed: 0,
        direction: 1, docked: false, phase: 'hidden', hopAmplitude: 0
      };
      this.walkAerial = 0;
      this.walkLean = 0;
      this.walkYaw = 0;
      this.stanceY = 0;
      this.squash = 1;
      this.jump = 0;
      this.emotion = options.initialEmotion || 'welcome';
      this.phase = Math.random() * Math.PI * 2;

      this.gaze = { x: 0, y: 0 };
      this.gazeTarget = { x: 0, y: 0 };
      this.headTarget = { x: 0, y: 0, z: 0 };

      this.tickers = [];
      this.paused = false;
      this.isRunning = false;
      this.destroyed = false;
      this.ready = false;
      this.model = null;
      this.mixer = null;
      this.actions = {};
      this.activeAction = null;
      this.clipLength = 0;
      this.showcaseBlend = 0;
      this.drawCallMergeSaved = 0;

      this._initRenderer();
      this._initScene();
      this._load();

      if (typeof options.onReady === 'function') {
        this.readyCallback = options.onReady;
      }
    }

    /* ── Setup ─────────────────────────────────────────────────────────── */

    _initRenderer() {
      this.renderer = new THREE.WebGLRenderer({
        canvas: this.canvas,
        antialias: true,
        alpha: true,
        powerPreference: 'high-performance'
      });
      // Audit §8.2: clamp the pixel ratio — never render more than 2x.
      this.renderer.setPixelRatio(Math.min((typeof window !== 'undefined' && window.devicePixelRatio) || 1, 2));
      this.renderer.setSize(this.width, this.height, false);
      this.renderer.outputEncoding = THREE.sRGBEncoding;
      if (THREE.ACESFilmicToneMapping !== undefined) {
        this.renderer.toneMapping = THREE.ACESFilmicToneMapping;
        this.renderer.toneMappingExposure = 1.05;
      }
      this.renderer.shadowMap.enabled = true;
      this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
      if (this.renderer.physicallyCorrectLights !== undefined) {
        this.renderer.physicallyCorrectLights = true;
      }
    }

    _initScene() {
      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(34, this.width / Math.max(1, this.height), 0.1, 60);
      this.camera.position.set(0, 1.05, 3.9);
      this.camera.lookAt(0, 1.0, 0);

      var hemi = new THREE.HemisphereLight(0xfff2e2, 0x1a0b14, 0.62);
      this.scene.add(hemi);

      var keyLight = new THREE.DirectionalLight(0xfff0d8, 1.45);
      keyLight.position.set(2.6, 4.4, 3.2);
      keyLight.castShadow = true;
      if (keyLight.shadow) {
        keyLight.shadow.mapSize.set(1024, 1024);
        keyLight.shadow.camera.near = 0.5;
        keyLight.shadow.camera.far = 18;
      }
      this.scene.add(keyLight);

      var fillLight = new THREE.DirectionalLight(0xd8ecff, 0.55);
      fillLight.position.set(-2.8, 2.0, 2.4);
      this.scene.add(fillLight);

      var rimLight = new THREE.DirectionalLight(0xc8a96a, 1.0);
      rimLight.position.set(-0.6, 3.2, -3.0);
      this.scene.add(rimLight);
    }

    _load() {
      var self = this;
      var Loader = (window.GLTFLoader) || THREE.GLTFLoader;
      if (!Loader) {
        console.error('GltfWalkCharacter: GLTFLoader not found (load js/vendor/GLTFLoader.js first).');
        return this;
      }
      this.loader = new Loader();
      this.loader.load(this.modelUrl, function (gltf) {
        if (self.destroyed) return;
        self._install(gltf);
      }, undefined, function (err) {
        console.error('GltfWalkCharacter: failed to load ' + self.modelUrl, err);
      });
      return this;
    }

    _install(gltf) {
      var model = gltf.scene || (gltf.scenes && gltf.scenes[0]);
      if (!model) return;

      // Normalise: feet on y = 0, centred on x/z, scaled to charHeightWorld so
      // the engine's screen-space placement maths is rig-independent.
      var box = new THREE.Box3().setFromObject(model);
      var size = new THREE.Vector3();
      var centre = new THREE.Vector3();
      box.getSize(size);
      box.getCenter(centre);

      var targetHeight = this.charHeightWorld || 2.12;
      var k = targetHeight / Math.max(0.0001, size.y);

      var pivot = new THREE.Group();
      model.position.set(-centre.x, -box.min.y, -centre.z);
      pivot.add(model);
      pivot.scale.setScalar(k);

      this.root = new THREE.Group();
      this.root.add(pivot);
      this.scene.add(this.root);
      this.model = model;
      this.modelPivot = pivot;

      model.traverse(function (o) {
        if (o.isMesh || o.isSkinnedMesh) {
          o.castShadow = true;
          o.receiveShadow = true;
          o.frustumCulled = false;   // skinned bounds change with the pose
        }
      });

      this._setupAnimation(gltf.animations || []);
      this.applyWalkPose(0.016);
      this.ready = true;
      if (this.readyCallback) this.readyCallback(this);
      if (this.isRunning === false) this.start();
    }

    _setupAnimation(clips) {
      if (!clips.length) return;
      this.mixer = new THREE.AnimationMixer(this.model);
      this.idleClip = pickClip(clips, CLIP_PREFS.idle);
      this.walkClip = pickClip(clips, CLIP_PREFS.walk);
      this.runClip = pickClip(clips, CLIP_PREFS.run);
      // A single clip drives both phases when the model ships only one.
      if (this.walkClip) {
        this.actions.walk = this.mixer.clipAction(this.walkClip);
        this.actions.walk.setLoop(THREE.LoopRepeat, Infinity);
        this.actions.walk.play();
        this.actions.walk.paused = true;      // scrubbed, never played
        this.clipLength = this.walkClip.duration || 1;
      }
      if (this.idleClip && this.idleClip !== this.walkClip) {
        this.actions.idle = this.mixer.clipAction(this.idleClip);
        this.actions.idle.setLoop(THREE.LoopRepeat, Infinity);
        this.actions.idle.play();
        this.actions.idle.paused = true;
        this.idleLength = this.idleClip.duration || 1;
      }
    }

    /* ── Render loop ───────────────────────────────────────────────────── */

    start() {
      if (this.isRunning || this.destroyed) return this;
      this.isRunning = true;
      this.clock = new THREE.Clock();
      var self = this;
      var animate = function () {
        if (!self.isRunning || self.destroyed) return;
        self._rafId = requestAnimationFrame(animate);
        var dt = Math.min(self.clock.getDelta(), 0.1);
        var time = self.clock.getElapsedTime();

        // Battery gate (audit §3): a hidden tab or paused rig costs zero GPU.
        if (self.paused || (typeof document !== 'undefined' && document.hidden)) return;

        self.applyWalkPose(dt);
        self.applyIdleLife(time);
        for (var i = 0; i < self.tickers.length; i++) self.tickers[i](time);
        self.render(dt);
      };
      this._rafId = requestAnimationFrame(animate);
      return this;
    }

    pause() { this.paused = true; return this; }

    resume() {
      this.paused = false;
      if (this.clock) this.clock.getDelta();   // drop the paused interval
      return this;
    }

    render() {
      if (!this.renderer || !this.scene || !this.camera) return;
      this.renderer.render(this.scene, this.camera);
    }

    /* ── Scroll scrubbing (the heart of the system) ────────────────────── */

    /**
     * Position the rig for a normalised scroll progress. The engine calls this
     * on every frame with `opts.gaitPhase` already accumulated from scroll
     * distance, so the walk cycle is a pure function of how far the visitor
     * has scrolled — forward and backward both work by construction.
     */
    scrub(progress, opts) {
      opts = opts || {};
      var w = this.walk;
      w.progress = progress;
      w.phase = opts.phase || 'walking';
      w.direction = opts.direction === undefined ? 1 : opts.direction;
      w.locomotion = opts.locomotion === undefined ? 0 : opts.locomotion;
      w.speed = opts.speed || 0;
      w.docked = !!opts.docked;
      w.hopAmplitude = opts.hopAmplitudePx || 26;
      if (typeof opts.gaitPhase === 'number') w.gaitPhase = opts.gaitPhase;
      this.gaitPhase = w.gaitPhase;
      return this;
    }

    /**
     * Translate the scrubbed state into the mixer timeline. Because both the
     * hop arc and the clip phase derive from the same gait angle, the feet
     * touch down when the body is at the bottom of its arc — the standard
     * "video-scrubbed locomotion" lock.
     */
    applyWalkPose(dt) {
      dt = dt || 0.016;
      var w = this.walk;
      var loco = Math.max(0, Math.min(1, w.locomotion || 0));

      if (this.mixer) {
        if (w.phase === 'docked' || w.phase === 'hidden') {
          // Settle onto the idle pose.
          if (this.actions.idle) {
            var idleT = (this.idleLength || 1) * 0.25;   // a composed resting beat
            this.mixer.setTime(0);
            this.actions.idle.time = idleT;
          }
          if (this.actions.walk) this.actions.walk.setEffectiveWeight(0);
          if (this.actions.idle) this.actions.idle.setEffectiveWeight(1);
          if (!this.actions.idle && this.actions.walk) {
            this.actions.walk.setEffectiveWeight(1);
            this.actions.walk.time = (this.clipLength || 1) * 0.5;
          }
          this.mixer.update(0);
        } else {
          if (this.actions.walk) {
            this.actions.walk.setEffectiveWeight(1);
            var cycle = (w.gaitPhase % (Math.PI * 2) + Math.PI * 2) % (Math.PI * 2);
            this.actions.walk.time = (cycle / (Math.PI * 2)) * (this.clipLength || 1);
          }
          if (this.actions.idle) {
            this.actions.idle.setEffectiveWeight(1 - loco);
          }
          this.mixer.update(0);   // timeline position set above; no real-time advance
        }
      }

      // Aerial hop arc: |sin| gives an authentic double-support gait where the
      // body is lowest when a foot is planted.
      var aerial = loco * Math.abs(Math.sin(w.gaitPhase)) * (w.hopAmplitude / 100) * 0.42;
      this.walkAerial = aerial;
      this.squash = 1 - loco * (1 - Math.abs(Math.sin(w.gaitPhase))) * 0.045;

      // Forward lean + facing the direction of travel.
      this.walkLean = loco * (w.phase === 'showcase' ? -0.02 : -0.05);
      var facing = w.phase === 'docking' ? 0 : (w.direction >= 0 ? 0.14 : -0.14);
      this.walkYaw = facing * loco;

      if (this.root) {
        this.root.position.y = this.stanceY + this.walkAerial;
        this.root.rotation.x = this.walkLean;
        this.root.rotation.y = this.walkYaw;
        if (this.modelPivot) {
          this.modelPivot.scale.y = this.modelPivot.scale.x * (2 - this.squash);
        }
      }

      // Gaze: head + eyes track the cursor while on stage.
      var ch = this;
      if (this.headRig) {
        this.headRig.rotation.y = (this.headTarget.y || 0) + this.gaze.x * 0.28 * (this.gazeInfluence || 1);
        this.headRig.rotation.x = (this.headTarget.x || 0) - this.gaze.y * 0.18 * (this.gazeInfluence || 1);
      }
      this.gaze.x += ((this.gazeTarget.x || 0) - this.gaze.x) * Math.min(1, dt * 4);
      this.gaze.y += ((this.gazeTarget.y || 0) - this.gaze.y) * Math.min(1, dt * 4);
      void ch;
      return this;
    }

    /** Idle life the walk clip cannot provide: breath + a slow sway. */
    applyIdleLife(time) {
      if (!this.modelPivot) return;
      var breath = 1 + Math.sin(time * 1.85 + this.phase) * 0.012;
      var sway = Math.sin(time * 0.85 + this.phase) * 0.018;
      this.modelPivot.scale.x = breath * (this._basePivotScale || (this._basePivotScale = this.modelPivot.scale.x));
      this.modelPivot.scale.z = this.modelPivot.scale.x;
      this.modelPivot.rotation.z = sway * 0.35;
    }

    /* ── Engine-facing API parity ──────────────────────────────────────── */

    dock() {
      this.walk.docked = true;
      this.walk.phase = 'docked';
      this.walk.locomotion = 0;
      this.walkAerial = 0;
      this.walkLean = 0;
      this.walkYaw = 0;
      this.squash = 1;
      return this;
    }

    undock() {
      this.walk.docked = false;
      return this;
    }

    setEmotion(moodName) {
      this.emotion = moodName;
      var G = window.gsap || null;
      if (moodName === 'happy' || moodName === 'excited' || moodName === 'celebrating') {
        this.jump = 0.12;
        if (G) G.to(this, { jump: 0, duration: 0.6, ease: 'power2.out', overwrite: true });
      } else if (moodName === 'sad' || moodName === 'hesitant') {
        this.walkLean = 0.06;
      }
      return this;
    }

    resize(w, h) {
      if (!this.renderer) return this;
      this.width = w;
      this.height = h;
      if (this.camera) {
        this.camera.aspect = w / Math.max(1, h);
        this.camera.updateProjectionMatrix();
      }
      this.renderer.setSize(w, h, false);
      return this;
    }

    /** Release every GPU resource this rig owns (audit §7.1). */
    destroy() {
      if (this.destroyed) return this;
      this.isRunning = false;
      if (this._rafId) cancelAnimationFrame(this._rafId);

      if (this.mixer) {
        this.mixer.stopAllAction();
        this.mixer.uncacheRoot ? this.mixer.uncacheRoot(this.model) : null;
        this.mixer = null;
      }
      if (this.scene) {
        var seenGeo = new Set(), seenMat = new Set();
        this.scene.traverse(function (o) {
          if (o.isMesh || o.isSkinnedMesh || o.isPoints || o.isLine) {
            if (o.geometry && !seenGeo.has(o.geometry.uuid)) {
              seenGeo.add(o.geometry.uuid);
              o.geometry.dispose();
            }
            var mats = Array.isArray(o.material) ? o.material : [o.material];
            mats.forEach(function (mat) {
              if (!mat || seenMat.has(mat.uuid)) return;
              seenMat.add(mat.uuid);
              ['map', 'normalMap', 'roughnessMap', 'metalnessMap', 'emissiveMap',
               'aoMap', 'alphaMap', 'envMap', 'sheenColorMap', 'clearcoatMap',
               'specularMap'].forEach(function (slot) {
                if (mat[slot] && mat[slot].dispose) mat[slot].dispose();
              });
              mat.dispose();
            });
          }
        });
        while (this.scene.children.length) this.scene.remove(this.scene.children[0]);
      }
      if (this.renderer) {
        this.renderer.dispose();
        if (this.renderer.forceContextLoss) {
          try { this.renderer.forceContextLoss(); } catch (e) { /* noop */ }
        }
      }
      this.model = null;
      this.root = null;
      this.tickers = [];
      this.destroyed = true;
      return this;
    }
  }

  GltfWalkCharacter.hexToLinearColor = hexToLinearColor;
  return GltfWalkCharacter;
}));
