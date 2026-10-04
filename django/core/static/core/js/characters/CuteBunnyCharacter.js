/**
 * CuteBunnyCharacter (v1.0.0)
 * Standalone 3D Procedural Cute Bunny Web Mascot & Emotion Engine
 * Inspired by the Sketchfab Cute Rabbit aesthetic
 */
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['three'], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory(require('three'));
  } else {
    root.CuteBunnyCharacter = factory(root.THREE);
  }
}(typeof self !== 'undefined' ? self : this, function (THREE) {
  'use strict';

  if (!THREE) {
    console.error('CuteBunnyCharacter requires Three.js (r128+).');
  }

  class CuteBunnyCharacter {
    constructor(options = {}) {
      this.canvas = typeof options.canvas === 'string' 
        ? document.querySelector(options.canvas) 
        : (options.canvas || options.target);
      
      if (!this.canvas) {
        throw new Error('CuteBunnyCharacter: A valid canvas or target container must be provided.');
      }

      this.theme = options.theme || 'festive';
      this.autoBlink = options.autoBlink !== false;
      this.interactiveCursor = options.interactiveCursor !== false;
      this.onEmotionChange = typeof options.onEmotionChange === 'function' ? options.onEmotionChange : null;

      this.width = options.width || this.canvas.clientWidth || 240;
      this.height = options.height || this.canvas.clientHeight || 240;

      this.emotions = {
        welcoming: { headTilt: 0.05, headPitch: 0.02, earL: 0.08, earR: -0.08, earPitch: -0.15, mouthScale: 1.0, blushOpacity: 0.7, eyeOpen: 1.0, bounceFreq: 1.8, bounceAmp: 0.03 },
        ram_ram: { headTilt: 0.0, headPitch: 0.16, earL: -0.05, earR: 0.05, earPitch: 0.08, mouthScale: 0.9, blushOpacity: 0.85, eyeOpen: 0.8, bounceFreq: 1.2, bounceAmp: 0.02 },
        happy_deal: { headTilt: -0.08, headPitch: -0.06, earL: 0.28, earR: -0.28, earPitch: -0.32, mouthScale: 1.4, blushOpacity: 0.95, eyeOpen: 1.1, bounceFreq: 4.5, bounceAmp: 0.08 },
        sad_hesitant: { headTilt: 0.04, headPitch: 0.18, earL: -0.35, earR: 0.35, earPitch: 0.42, mouthScale: 0.6, blushOpacity: 0.35, eyeOpen: 0.7, bounceFreq: 0.8, bounceAmp: 0.015 },
        thinking_coupon: { headTilt: -0.15, headPitch: -0.12, earL: 0.38, earR: -0.12, earPitch: -0.22, mouthScale: 0.8, blushOpacity: 0.75, eyeOpen: 0.95, bounceFreq: 2.2, bounceAmp: 0.04 }
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
      this.camera = new THREE.PerspectiveCamera(36, this.width / this.height, 0.1, 100);
      this.camera.position.set(0, 0.12, 3.6);

      this.renderer = new THREE.WebGLRenderer({
        canvas: this.canvas,
        alpha: true,
        antialias: true,
        powerPreference: 'high-performance'
      });
      this.renderer.setSize(this.width, this.height, false);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

      const ambient = new THREE.AmbientLight(0xFFF0E5, 0.9);
      this.scene.add(ambient);

      const keyLight = new THREE.DirectionalLight(0xFFE5CC, 1.2);
      keyLight.position.set(2.5, 3.5, 3.0);
      this.scene.add(keyLight);

      const fillLight = new THREE.DirectionalLight(0xE5F0FF, 0.65);
      fillLight.position.set(-2.5, 1.5, 2.0);
      this.scene.add(fillLight);

      const rimLight = new THREE.DirectionalLight(0xD4AF37, 0.8);
      rimLight.position.set(0, 3.0, -2.5);
      this.scene.add(rimLight);
    }

    buildModel() {
      this.bunnyGroup = new THREE.Group();
      this.scene.add(this.bunnyGroup);

      const furMaterial = new THREE.MeshStandardMaterial({
        color: 0xFFF7EE,
        roughness: 0.82,
        metalness: 0.05
      });

      const innerEarMaterial = new THREE.MeshStandardMaterial({
        color: 0xFFB3BA,
        roughness: 0.65
      });

      const eyeMaterial = new THREE.MeshStandardMaterial({
        color: 0x110C11,
        roughness: 0.1,
        metalness: 0.3
      });

      const noseMaterial = new THREE.MeshStandardMaterial({
        color: 0xFF758F,
        roughness: 0.4
      });

      const goldMaterial = new THREE.MeshStandardMaterial({
        color: 0xD4AF37,
        roughness: 0.25,
        metalness: 0.85
      });

      // Body
      const bodyGeo = new THREE.SphereGeometry(0.56, 32, 28);
      bodyGeo.scale(1.0, 0.95, 0.88);
      this.body = new THREE.Mesh(bodyGeo, furMaterial);
      this.body.position.set(0, -0.42, 0);
      this.bunnyGroup.add(this.body);

      // Head
      this.headGroup = new THREE.Group();
      this.headGroup.position.set(0, 0.18, 0);
      this.bunnyGroup.add(this.headGroup);

      const headGeo = new THREE.SphereGeometry(0.52, 32, 28);
      headGeo.scale(1.08, 0.96, 0.94);
      this.head = new THREE.Mesh(headGeo, furMaterial);
      this.headGroup.add(this.head);

      // Cheeks
      const cheekGeo = new THREE.SphereGeometry(0.24, 20, 18);
      cheekGeo.scale(1.1, 0.85, 0.8);
      
      this.leftCheek = new THREE.Mesh(cheekGeo, new THREE.MeshStandardMaterial({
        color: 0xFF85A1,
        roughness: 0.9,
        transparent: true,
        opacity: 0.75
      }));
      this.leftCheek.position.set(-0.30, -0.12, 0.36);
      this.headGroup.add(this.leftCheek);

      this.rightCheek = this.leftCheek.clone();
      this.rightCheek.position.set(0.30, -0.12, 0.36);
      this.headGroup.add(this.rightCheek);

      // Ears
      this.leftEarGroup = new THREE.Group();
      this.leftEarGroup.position.set(-0.25, 0.46, 0);
      this.headGroup.add(this.leftEarGroup);

      const earGeo = new THREE.CylinderGeometry(0.12, 0.08, 0.72, 24);
      earGeo.scale(1.0, 1.0, 0.45);
      const leftEarOuter = new THREE.Mesh(earGeo, furMaterial);
      leftEarOuter.position.set(0, 0.32, 0);
      this.leftEarGroup.add(leftEarOuter);

      const earInnerGeo = new THREE.CylinderGeometry(0.08, 0.05, 0.58, 20);
      earInnerGeo.scale(0.9, 1.0, 0.35);
      const leftEarInner = new THREE.Mesh(earInnerGeo, innerEarMaterial);
      leftEarInner.position.set(0, 0.32, 0.04);
      this.leftEarGroup.add(leftEarInner);

      this.rightEarGroup = new THREE.Group();
      this.rightEarGroup.position.set(0.25, 0.46, 0);
      this.headGroup.add(this.rightEarGroup);

      const rightEarOuter = leftEarOuter.clone();
      this.rightEarGroup.add(rightEarOuter);

      const rightEarInner = leftEarInner.clone();
      this.rightEarGroup.add(rightEarInner);

      // Eyes
      this.leftEyeGroup = new THREE.Group();
      this.leftEyeGroup.position.set(-0.19, 0.04, 0.44);
      this.headGroup.add(this.leftEyeGroup);

      const eyeBallGeo = new THREE.SphereGeometry(0.10, 24, 20);
      this.leftEye = new THREE.Mesh(eyeBallGeo, eyeMaterial);
      this.leftEyeGroup.add(this.leftEye);

      const glintGeo = new THREE.SphereGeometry(0.032, 12, 12);
      const glintMat = new THREE.MeshBasicMaterial({ color: 0xFFFFFF });
      const glint1 = new THREE.Mesh(glintGeo, glintMat);
      glint1.position.set(0.03, 0.035, 0.085);
      this.leftEyeGroup.add(glint1);

      this.rightEyeGroup = new THREE.Group();
      this.rightEyeGroup.position.set(0.19, 0.04, 0.44);
      this.headGroup.add(this.rightEyeGroup);

      this.rightEye = this.leftEye.clone();
      this.rightEyeGroup.add(this.rightEye);

      const glint2 = glint1.clone();
      glint2.position.set(0.03, 0.035, 0.085);
      this.rightEyeGroup.add(glint2);

      // Nose
      const noseGeo = new THREE.SphereGeometry(0.052, 18, 16);
      noseGeo.scale(1.2, 0.9, 0.9);
      this.nose = new THREE.Mesh(noseGeo, noseMaterial);
      this.nose.position.set(0, -0.04, 0.51);
      this.headGroup.add(this.nose);

      // Festive Accessories
      if (this.theme === 'festive') {
        const bindiGeo = new THREE.SphereGeometry(0.032, 16, 16);
        bindiGeo.scale(1.0, 1.0, 0.3);
        const bindi = new THREE.Mesh(bindiGeo, new THREE.MeshStandardMaterial({
          color: 0x9B111E,
          roughness: 0.35
        }));
        bindi.position.set(0, 0.16, 0.51);
        this.headGroup.add(bindi);

        const collarGeo = new THREE.TorusGeometry(0.36, 0.04, 16, 32);
        const collar = new THREE.Mesh(collarGeo, goldMaterial);
        collar.rotation.x = Math.PI / 2;
        collar.position.set(0, -0.16, 0);
        this.bunnyGroup.add(collar);
      }
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
        console.warn(`CuteBunnyCharacter: Unknown emotion "${emotionName}". Available:`, Object.keys(this.emotions));
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

      const bounce = Math.sin(elapsed * this.currentState.bounceFreq) * this.currentState.bounceAmp;
      this.bunnyGroup.position.y = bounce;

      this.headGroup.rotation.y = this.mouse.x * 0.38 + this.currentState.headTilt;
      this.headGroup.rotation.x = -this.mouse.y * 0.25 + this.currentState.headPitch;
      this.headGroup.rotation.z = -this.mouse.x * 0.12 + Math.sin(elapsed * 1.5) * 0.02;

      const earWiggle = Math.sin(elapsed * 3.5) * 0.04;
      this.leftEarGroup.rotation.z = this.currentState.earL + earWiggle;
      this.leftEarGroup.rotation.x = this.currentState.earPitch - this.mouse.y * 0.15;

      this.rightEarGroup.rotation.z = this.currentState.earR - earWiggle;
      this.rightEarGroup.rotation.x = this.currentState.earPitch - this.mouse.y * 0.15;

      const noseTwitch = Math.sin(elapsed * 8.0) * (this.currentEmotion === 'thinking_coupon' ? 0.03 : 0.012);
      this.nose.position.y = -0.04 + noseTwitch;

      if (this.autoBlink) {
        this.blinkTimer += delta;
        if (!this.isBlinking && this.blinkTimer > 3.8 + Math.sin(elapsed) * 1.2) {
          this.isBlinking = true;
          this.blinkTimer = 0;
        }

        if (this.isBlinking) {
          const blinkProgress = this.blinkTimer / 0.18;
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

  return CuteBunnyCharacter;
}));
