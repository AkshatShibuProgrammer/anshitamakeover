/**
 * PixarBridalGirlCharacter (v1.0.0)
 * Standalone 3D Procedural Pixar Indian Little Girl Bride Mascot & Concierge
 */
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['three'], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory(require('three'));
  } else {
    root.PixarBridalGirlCharacter = factory(root.THREE);
  }
}(typeof self !== 'undefined' ? self : this, function (THREE) {
  'use strict';

  if (!THREE) {
    console.error('PixarBridalGirlCharacter requires Three.js (r128+).');
  }

  class PixarBridalGirlCharacter {
    constructor(options = {}) {
      this.canvas = typeof options.canvas === 'string' 
        ? document.querySelector(options.canvas) 
        : (options.canvas || options.target);
      
      if (!this.canvas) {
        throw new Error('PixarBridalGirlCharacter: A valid canvas or target container must be provided.');
      }

      this.autoBlink = options.autoBlink !== false;
      this.interactiveCursor = options.interactiveCursor !== false;
      this.onEmotionChange = typeof options.onEmotionChange === 'function' ? options.onEmotionChange : null;

      this.width = options.width || this.canvas.clientWidth || 240;
      this.height = options.height || this.canvas.clientHeight || 240;

      this.emotions = {
        welcoming: { headTilt: 0.04, headPitch: 0.02, brushWaveFreq: 2.2, brushAmp: 0.18, blushOpacity: 0.75, eyeOpen: 1.0 },
        ram_ram: { headTilt: 0.0, headPitch: 0.14, brushWaveFreq: 1.2, brushAmp: 0.08, blushOpacity: 0.85, eyeOpen: 0.82 },
        happy_deal: { headTilt: -0.06, headPitch: -0.04, brushWaveFreq: 4.8, brushAmp: 0.35, blushOpacity: 0.95, eyeOpen: 1.1 },
        sad_hesitant: { headTilt: 0.03, headPitch: 0.16, brushWaveFreq: 0.8, brushAmp: 0.05, blushOpacity: 0.35, eyeOpen: 0.72 },
        thinking_coupon: { headTilt: -0.14, headPitch: -0.10, brushWaveFreq: 2.6, brushAmp: 0.14, blushOpacity: 0.75, eyeOpen: 0.95 }
      };

      this.currentEmotion = options.initialEmotion || 'welcoming';
      this.targetState = Object.assign({}, this.emotions[this.currentEmotion]);
      this.currentState = Object.assign({}, this.targetState);

      this.mouse = { x: 0, y: 0, targetX: 0, targetY: 0 };
      this.clock = new THREE.Clock();
      this.blinkTimer = 0;
      this.isBlinking = false;
      this.isRunning = false;

      this.initScene();
      this.buildModel();
      this.setupListeners();
      this.start();
    }

    initScene() {
      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(38, this.width / this.height, 0.1, 100);
      this.camera.position.set(0, 0.08, 3.1);

      this.renderer = new THREE.WebGLRenderer({
        canvas: this.canvas,
        alpha: true,
        antialias: true,
        powerPreference: 'high-performance'
      });
      this.renderer.setSize(this.width, this.height, false);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

      const ambient = new THREE.AmbientLight(0xFFEFE2, 0.85);
      this.scene.add(ambient);

      const keyLight = new THREE.DirectionalLight(0xFFF0DD, 1.25);
      keyLight.position.set(2.0, 3.0, 3.5);
      this.scene.add(keyLight);

      const softFill = new THREE.DirectionalLight(0xE0ECFF, 0.6);
      softFill.position.set(-2.0, 1.5, 2.0);
      this.scene.add(softFill);

      const goldRim = new THREE.DirectionalLight(0xD4AF37, 1.1);
      goldRim.position.set(0, 2.8, -2.5);
      this.scene.add(goldRim);
    }

    buildModel() {
      this.characterGroup = new THREE.Group();
      this.scene.add(this.characterGroup);

      const skinMat = new THREE.MeshStandardMaterial({
        color: 0xBA7742,
        roughness: 0.72,
        metalness: 0.04
      });

      const hairMat = new THREE.MeshStandardMaterial({
        color: 0x0D080A,
        roughness: 0.82
      });

      const goldMat = new THREE.MeshStandardMaterial({
        color: 0xE8B838,
        roughness: 0.28,
        metalness: 0.88
      });

      const rubyMat = new THREE.MeshStandardMaterial({
        color: 0x9B111E,
        roughness: 0.32,
        metalness: 0.4
      });

      const jasmineMat = new THREE.MeshStandardMaterial({
        color: 0xFFFFF5,
        roughness: 0.65
      });

      const choliMat = new THREE.MeshStandardMaterial({
        color: 0x82121E,
        roughness: 0.75
      });

      // Upper body
      const choliGeo = new THREE.CylinderGeometry(0.38, 0.48, 0.52, 28);
      choliGeo.scale(1.15, 1.0, 0.75);
      this.choli = new THREE.Mesh(choliGeo, choliMat);
      this.choli.position.set(0, -0.62, -0.04);
      this.characterGroup.add(this.choli);

      const zariGeo = new THREE.TorusGeometry(0.38, 0.032, 16, 32);
      const zari = new THREE.Mesh(zariGeo, goldMat);
      zari.rotation.x = Math.PI / 2;
      zari.position.set(0, -0.38, -0.02);
      this.characterGroup.add(zari);

      const neckGeo = new THREE.CylinderGeometry(0.18, 0.22, 0.22, 24);
      this.neck = new THREE.Mesh(neckGeo, skinMat);
      this.neck.position.set(0, -0.30, 0);
      this.characterGroup.add(this.neck);

      const chokerGeo = new THREE.TorusGeometry(0.20, 0.028, 16, 28);
      const choker = new THREE.Mesh(chokerGeo, goldMat);
      choker.rotation.x = Math.PI / 2;
      choker.position.set(0, -0.28, 0);
      this.characterGroup.add(choker);

      // Arm & Brush
      this.armGroup = new THREE.Group();
      this.armGroup.position.set(0.44, -0.46, 0.1);
      this.characterGroup.add(this.armGroup);

      const armGeo = new THREE.CylinderGeometry(0.08, 0.065, 0.36, 18);
      const arm = new THREE.Mesh(armGeo, skinMat);
      arm.rotation.z = -Math.PI / 3.8;
      this.armGroup.add(arm);

      const handGeo = new THREE.SphereGeometry(0.075, 16, 16);
      const hand = new THREE.Mesh(handGeo, skinMat);
      hand.position.set(0.22, 0.12, 0.12);
      this.armGroup.add(hand);

      this.brushGroup = new THREE.Group();
      this.brushGroup.position.set(0.25, 0.16, 0.14);
      this.brushGroup.rotation.z = -Math.PI / 5;
      this.armGroup.add(this.brushGroup);

      const handleGeo = new THREE.CylinderGeometry(0.02, 0.028, 0.42, 16);
      const handle = new THREE.Mesh(handleGeo, goldMat);
      this.brushGroup.add(handle);

      const bristleGeo = new THREE.ConeGeometry(0.065, 0.16, 18);
      const bristleMat = new THREE.MeshStandardMaterial({ color: 0x1A1016, roughness: 0.95 });
      const bristle = new THREE.Mesh(bristleGeo, bristleMat);
      bristle.position.set(0, 0.28, 0);
      this.brushGroup.add(bristle);

      // Head
      this.headGroup = new THREE.Group();
      this.headGroup.position.set(0, 0.05, 0);
      this.characterGroup.add(this.headGroup);

      const headGeo = new THREE.SphereGeometry(0.55, 32, 28);
      headGeo.scale(1.06, 0.96, 0.92);
      this.head = new THREE.Mesh(headGeo, skinMat);
      this.headGroup.add(this.head);

      const cheekGeo = new THREE.SphereGeometry(0.24, 20, 18);
      cheekGeo.scale(1.05, 0.8, 0.6);

      this.leftCheek = new THREE.Mesh(cheekGeo, new THREE.MeshStandardMaterial({
        color: 0xCF5A50,
        roughness: 0.92,
        transparent: true,
        opacity: 0.75
      }));
      this.leftCheek.position.set(-0.31, -0.10, 0.42);
      this.headGroup.add(this.leftCheek);

      this.rightCheek = this.leftCheek.clone();
      this.rightCheek.position.set(0.31, -0.10, 0.42);
      this.headGroup.add(this.rightCheek);

      // Eyes
      this.leftEyeGroup = new THREE.Group();
      this.leftEyeGroup.position.set(-0.19, 0.06, 0.48);
      this.headGroup.add(this.leftEyeGroup);

      const scleraGeo = new THREE.SphereGeometry(0.12, 24, 20);
      const scleraMat = new THREE.MeshStandardMaterial({ color: 0xFFFDF8, roughness: 0.3 });
      const leftSclera = new THREE.Mesh(scleraGeo, scleraMat);
      this.leftEyeGroup.add(leftSclera);

      const irisGeo = new THREE.SphereGeometry(0.075, 20, 20);
      const irisMat = new THREE.MeshStandardMaterial({ color: 0x4A2511, roughness: 0.1, metalness: 0.2 });
      this.leftIris = new THREE.Mesh(irisGeo, irisMat);
      this.leftIris.position.set(0, 0, 0.055);
      this.leftEyeGroup.add(this.leftIris);

      const glintGeo = new THREE.SphereGeometry(0.026, 12, 12);
      const glintMat = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });
      const glint1 = new THREE.Mesh(glintGeo, glintMat);
      glint1.position.set(0.025, 0.028, 0.07);
      this.leftIris.add(glint1);

      this.rightEyeGroup = new THREE.Group();
      this.rightEyeGroup.position.set(0.19, 0.06, 0.48);
      this.headGroup.add(this.rightEyeGroup);

      const rightSclera = leftSclera.clone();
      this.rightEyeGroup.add(rightSclera);

      this.rightIris = this.leftIris.clone();
      this.rightEyeGroup.add(this.rightIris);

      // Bindi & Tikka
      const bindiGeo = new THREE.SphereGeometry(0.038, 16, 16);
      bindiGeo.scale(1.0, 1.0, 0.25);
      const bindi = new THREE.Mesh(bindiGeo, rubyMat);
      bindi.position.set(0, 0.18, 0.54);
      this.headGroup.add(bindi);

      const tikkaPendantGeo = new THREE.ConeGeometry(0.06, 0.11, 16);
      const tikkaPendant = new THREE.Mesh(tikkaPendantGeo, goldMat);
      tikkaPendant.rotation.z = Math.PI;
      tikkaPendant.position.set(0, 0.32, 0.51);
      this.headGroup.add(tikkaPendant);

      const tikkaRuby = new THREE.Mesh(new THREE.SphereGeometry(0.03, 12, 12), rubyMat);
      tikkaRuby.position.set(0, 0.30, 0.53);
      this.headGroup.add(tikkaRuby);

      // Gajra Buns
      this.leftBun = new THREE.Group();
      this.leftBun.position.set(-0.52, 0.28, 0);
      this.headGroup.add(this.leftBun);

      const bunGeo = new THREE.SphereGeometry(0.24, 20, 18);
      const leftBunMesh = new THREE.Mesh(bunGeo, hairMat);
      this.leftBun.add(leftBunMesh);

      const gajraGeo = new THREE.TorusGeometry(0.23, 0.05, 16, 24);
      const leftGajra = new THREE.Mesh(gajraGeo, jasmineMat);
      this.leftBun.add(leftGajra);

      this.rightBun = new THREE.Group();
      this.rightBun.position.set(0.52, 0.28, 0);
      this.headGroup.add(this.rightBun);

      const rightBunMesh = leftBunMesh.clone();
      this.rightBun.add(rightBunMesh);

      const rightGajra = leftGajra.clone();
      this.rightBun.add(rightGajra);

      // Jhumkas
      const jhumkaGeo = new THREE.ConeGeometry(0.07, 0.12, 16);
      const leftJhumka = new THREE.Mesh(jhumkaGeo, goldMat);
      leftJhumka.position.set(-0.46, -0.16, 0.08);
      this.headGroup.add(leftJhumka);

      const rightJhumka = leftJhumka.clone();
      rightJhumka.position.set(0.46, -0.16, 0.08);
      this.headGroup.add(rightJhumka);
    }

    setupListeners() {
      if (this.interactiveCursor) {
        window.addEventListener('mousemove', (e) => {
          const rect = this.canvas.getBoundingClientRect();
          const cx = rect.left + rect.width / 2;
          const cy = rect.top + rect.height / 2;
          this.mouse.targetX = Math.max(-1, Math.min(1, (e.clientX - cx) / (window.innerWidth / 2)));
          this.mouse.targetY = Math.max(-1, Math.min(1, (e.clientY - cy) / (window.innerHeight / 2)));
        }, { passive: true });
      }

      window.addEventListener('resize', () => {
        if (!this.canvas) return;
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

    setEmotion(emotionName) {
      if (!this.emotions[emotionName]) {
        console.warn(`PixarBridalGirlCharacter: Unknown emotion "${emotionName}". Available:`, Object.keys(this.emotions));
        return;
      }
      this.currentEmotion = emotionName;
      this.targetState = Object.assign({}, this.emotions[emotionName]);
      if (this.onEmotionChange) {
        this.onEmotionChange(emotionName);
      }
    }

    update() {
      const delta = this.clock.getDelta();
      const elapsed = this.clock.getElapsedTime();

      const lerpFactor = 0.12;
      for (const key in this.targetState) {
        this.currentState[key] += (this.targetState[key] - this.currentState[key]) * lerpFactor;
      }

      this.mouse.x += (this.mouse.targetX - this.mouse.x) * 0.08;
      this.mouse.y += (this.mouse.targetY - this.mouse.y) * 0.08;

      const breath = Math.sin(elapsed * 1.8) * 0.015;
      this.headGroup.position.y = 0.05 + breath;
      this.headGroup.rotation.y = this.mouse.x * 0.32 + this.currentState.headTilt;
      this.headGroup.rotation.x = -this.mouse.y * 0.22 + this.currentState.headPitch;

      const pupilX = this.mouse.x * 0.025;
      const pupilY = -this.mouse.y * 0.020;
      this.leftIris.position.x = pupilX;
      this.leftIris.position.y = pupilY;
      this.rightIris.position.x = pupilX;
      this.rightIris.position.y = pupilY;

      const brushWave = Math.sin(elapsed * this.currentState.brushWaveFreq) * this.currentState.brushAmp;
      this.brushGroup.rotation.z = -Math.PI / 5 + brushWave;

      if (this.autoBlink) {
        this.blinkTimer += delta;
        if (!this.isBlinking && this.blinkTimer > 3.6 + Math.sin(elapsed) * 1.4) {
          this.isBlinking = true;
          this.blinkTimer = 0;
        }

        if (this.isBlinking) {
          const blinkProgress = this.blinkTimer / 0.16;
          if (blinkProgress >= 1.0) {
            this.isBlinking = false;
            this.leftEyeGroup.scale.y = 1.0;
            this.rightEyeGroup.scale.y = 1.0;
          } else {
            const eyeSquash = Math.sin(blinkProgress * Math.PI);
            const scaleY = Math.max(0.08, 1.0 - eyeSquash * 0.92);
            this.leftEyeGroup.scale.y = scaleY * this.currentState.eyeOpen;
            this.rightEyeGroup.scale.y = scaleY * this.currentState.eyeOpen;
          }
        }
      }

      this.leftCheek.material.opacity = this.currentState.blushOpacity;
      this.rightCheek.material.opacity = this.currentState.blushOpacity;
    }

    start() {
      this.isRunning = true;
      const animate = () => {
        if (!this.isRunning) return;
        requestAnimationFrame(animate);
        this.update();
        this.renderer.render(this.scene, this.camera);
      };
      animate();
    }

    stop() {
      this.isRunning = false;
    }

    destroy() {
      this.stop();
      if (this.renderer) {
        this.renderer.dispose();
      }
      if (this.scene) {
        this.scene.traverse((obj) => {
          if (obj.geometry) obj.geometry.dispose();
          if (obj.material) {
            if (Array.isArray(obj.material)) obj.material.forEach(m => m.dispose());
            else obj.material.dispose();
          }
        });
      }
    }
  }

  return PixarBridalGirlCharacter;
}));
