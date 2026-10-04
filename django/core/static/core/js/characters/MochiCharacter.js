/**
 * MochiCharacter (v1.0.0)
 * Standalone 3D Procedural Haute Velvet Mascot ("Mochi") for Anshita Makeover
 * Featuring luxury velvet fur, emerald royal brooch, big glossy boba eyes with triple sparkles, and emotion engine.
 */
(function (root, factory) {
  if (typeof define === 'function' && define.amd) {
    define(['three'], factory);
  } else if (typeof module === 'object' && module.exports) {
    module.exports = factory(require('three'));
  } else {
    root.MochiCharacter = factory(root.THREE);
  }
}(typeof self !== 'undefined' ? self : this, function (THREE) {
  'use strict';

  if (!THREE) {
    console.error('MochiCharacter requires Three.js (r128+).');
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
  function ribbon(parent, points, width, material, segments = 40) {
    const curve = new THREE.CatmullRomCurve3(points.map(p => vec(p[0], p[1], p[2])));
    const samples = curve.getPoints(segments);
    const positions = [];
    const indices = [];
    for (let i = 0; i < samples.length; i++) {
      const tangent = (i < samples.length - 1 ? samples[i + 1].clone().sub(samples[i]) : samples[i].clone().sub(samples[i - 1])).normalize();
      let side = new THREE.Vector3().crossVectors(tangent, vec(0, 0, 1));
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
    const settings = Object.assign({ x: .147, y: .045, z: .323, radius: .095 }, options);
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

      // Boba plush eye for Mochi with big glossy catchlights
      sphere(irisGroup, colorMat(0x101018, { roughness: .04, clearcoat: 1, envMapIntensity: 2.0 }), [0, 0, 0.01], [r * 1.25, r * 1.32, 0.18], 22);
      const bobaCatch = colorMat(0xffffff, { roughness: .01, clearcoat: 1, emissive: 0xffffff, emissiveIntensity: 1.0 });
      const bc1 = sphere(irisGroup, bobaCatch, [-r * 0.45, r * 0.48, 0.18], [r * 0.45, r * 0.48, 0.12], 14);
      bc1.castShadow = false;
      const bc2 = sphere(irisGroup, bobaCatch, [r * 0.45, -r * 0.32, 0.17], [r * 0.22, r * 0.22, 0.10], 12);
      bc2.castShadow = false;
      const bc3 = sphere(irisGroup, bobaCatch, [r * 0.32, r * 0.52, 0.17], [r * 0.13, r * 0.13, 0.08], 10);
      bc3.castShadow = false;

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
    const G = window.gsap || null;
    function surfaceZ(x, y) {
      if (!face) return null;
      const a = (x - face.c[0]) / face.r[0];
      const b = (y - face.c[1]) / face.r[1];
      const k = 1 - a * a - b * b;
      const z = face.c[2] + face.r[2] * Math.sqrt(k > 0 ? k : 0) - position[2] + .006;
      return Math.max(-.075, Math.min(.075, z));
    }
    function build(cAmt, oAmt) {
      const c = cAmt, o = Math.max(0, oAmt);
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
    return group;
  }

  function blush(parent, x, y, z, radius, material) {
    return sphere(parent, material, [x, y, z], [radius, radius * .63, radius * .22], 16);
  }

  function createArms(parent, options) {
    const config = Object.assign({ x: .39, y: .82, z: .02, upper: .2, fore: .18, radius: .082, skinRadius: .105, sleeve: null, skin: null }, options);
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

  class MochiCharacter {
    constructor(options = {}) {
      this.canvas = typeof options.canvas === 'string'
        ? document.querySelector(options.canvas)
        : (options.canvas || options.target);

      if (!this.canvas) {
        throw new Error('MochiCharacter: A valid canvas must be provided.');
      }

      this.width = options.width || this.canvas.clientWidth || 240;
      this.height = options.height || this.canvas.clientHeight || 240;
      this.interactiveCursor = options.interactiveCursor !== false;
      this.autoBlink = options.autoBlink !== false;

      this.earParts = [];
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
      this.armSwingX = 0;
      this.phase = Math.random() * Math.PI * 2;

      this.initScene();
      this.build();
      this.setupListeners();
      this.start();
    }

    initScene() {
      this.scene = new THREE.Scene();
      this.camera = new THREE.PerspectiveCamera(34, this.width / this.height, 0.1, 50);
      this.camera.position.set(0, 1.15, 3.8);
      this.camera.lookAt(0, 0.95, 0);

      this.renderer = new THREE.WebGLRenderer({
        canvas: this.canvas,
        alpha: true,
        antialias: true,
        powerPreference: 'high-performance'
      });
      this.renderer.setSize(this.width, this.height, false);
      this.renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));

      const ambient = new THREE.AmbientLight(0xfff3e5, 1.15);
      this.scene.add(ambient);

      const keyLight = new THREE.DirectionalLight(0xffecd6, 1.35);
      keyLight.position.set(2.4, 3.8, 3.2);
      this.scene.add(keyLight);

      const fillLight = new THREE.DirectionalLight(0xe4f2ff, 0.7);
      fillLight.position.set(-2.4, 1.8, 2.2);
      this.scene.add(fillLight);

      const rimLight = new THREE.DirectionalLight(0xc8a96a, 0.95);
      rimLight.position.set(0, 3.2, -2.5);
      this.scene.add(rimLight);
    }

    build() {
      this.root = new THREE.Group();
      this.root.position.y = 0.10;
      this.scene.add(this.root);

      this.bodyGroup = new THREE.Group();
      this.root.add(this.bodyGroup);

      this.headRig = new THREE.Group();
      this.root.add(this.headRig);

      const fur = colorMat(0xf0e7d9, { roughness: .88, sheen: new THREE.Color(0xffddce) });
      const cream = colorMat(0xfff9ee, { roughness: .82, sheen: new THREE.Color(0xffe7d8) });
      const chestFur = colorMat(0xf8f1e6, { roughness: .87, sheen: new THREE.Color(0xfff3e4) });
      const pink = colorMat(0xef9dab, { roughness: .6, sheen: new THREE.Color(0xffc7cf) });
      const blushMat = colorMat(0xe995a6, { roughness: .7, transparent: true, opacity: .42 });
      const sash = colorMat(0x5b1428, { roughness: .31, sheen: new THREE.Color(0xbf6674) });
      const gold = goldMat(), emerald = gemMat(0x1b9869);

      sphere(this.bodyGroup, fur, [0, .67, 0], [.48, .54, .43], 30);
      sphere(this.bodyGroup, chestFur, [0, .62, .345], [.24, .28, .10], 24);

      // Pom-pom tail
      const tail = new THREE.Group();
      tail.position.set(0, .47, -.375);
      this.bodyGroup.add(tail);
      sphere(tail, fur, [0, 0, -.02], [.125, .13, .115], 20);
      for (let i = 0; i < 14; i++) {
        const y = 1 - (i / 13) * 2, rr = Math.sqrt(Math.max(0, 1 - y * y)), a = i * 2.39996, d = .072;
        const rad = .052 + (i % 3) * .009;
        sphere(tail, i % 4 === 0 ? chestFur : fur, [Math.cos(a) * rr * d, y * .085, -.035 + Math.sin(a) * rr * d], [rad, rad, rad], 12);
      }
      this.tickers.push(t => { tail.rotation.y = Math.sin(t * 1.35) * .11; tail.rotation.x = Math.sin(t * .95) * .05; });

      // Feet
      [-1, 1].forEach(side => {
        sphere(this.bodyGroup, fur, [side * .22, .14, .08], [.18, .12, .22], 18);
        sphere(this.bodyGroup, pink, [side * .22, .13, .24], [.1, .04, .025], 14);
      });

      // Head
      this.headRig.position.y = 1.28;
      sphere(this.headRig, fur, [0, 0, 0], [.405, .405, .37], 32);
      sphere(this.headRig, cream, [0, -.14, .291], [.245, .17, .13], 22);

      // Long bunny ears
      [-1, 1].forEach(side => {
        const ear = new THREE.Group();
        ear.position.set(side * .155, .30, -.005);
        ear.rotation.z = -side * .13;
        this.headRig.add(ear);

        sphere(ear, fur, [0, .16, 0], [.072, .13, .062], 18);
        sphere(ear, fur, [0, .34, 0], [.098, .19, .075], 20);
        sphere(ear, fur, [0, .52, 0], [.082, .13, .062], 18);

        sphere(ear, pink, [0, .17, .042], [.040, .095, .026], 14);
        sphere(ear, pink, [0, .35, .051], [.056, .150, .030], 16);
        sphere(ear, pink, [0, .51, .044], [.040, .095, .024], 14);
        this.earParts.push({ group: ear, side: side });
      });

      // Big glossy boba eyes with catchlights
      this.eyes = eyePair(this.headRig, { x: .147, y: .045, z: .323, radius: .095 });
      sphere(this.headRig, pink, [0, -.072, .402], [.045, .033, .027], 16);
      this.mouth = smile(this.headRig, [0, -.158, .418], .100, colorMat(0x9c5662, { roughness: .4 }), { c: [0, -.14, .291], r: [.245, .17, .13] });
      blush(this.headRig, -.25, -.1, .29, .075, blushMat);
      blush(this.headRig, .25, -.1, .29, .075, blushMat);

      // Velvet sash & emerald royal brooch
      ribbon(this.bodyGroup, [[-.43, .92, .12], [-.25, .81, .35], [0, .74, .45], [.24, .81, .35], [.43, .92, .12]], .135, sash, 30);
      tube(this.bodyGroup, [[-.43, .92, .13], [-.25, .81, .36], [0, .74, .46], [.24, .81, .36], [.43, .92, .13]], .007, gold);
      addMesh(this.bodyGroup, new THREE.TorusGeometry(.068, .012, 10, 24), gold).position.set(0, .76, .46);
      const jewel = addMesh(this.bodyGroup, new THREE.OctahedronGeometry(.05), emerald);
      jewel.position.set(0, .76, .48);
      jewel.scale.y = 1.3;

      const arms = createArms(this.root, { x: .39, y: .82, z: .02, upper: .2, fore: .18, radius: .082, skinRadius: .105, sleeve: fur, skin: fur });
      this.armL = arms.L;
      this.armR = arms.R;

      this.tickers.push((t) => this.earParts.forEach(e => {
        e.group.rotation.x = Math.sin(t * 1.55 + e.side) * .075;
        e.group.rotation.z = -e.side * (.13 + Math.sin(t * .7 + e.side) * .05);
      }));
    }

    setupListeners() {
      if (this.interactiveCursor) {
        window.addEventListener('mousemove', (e) => {
          const rect = this.canvas.getBoundingClientRect();
          const cx = rect.left + rect.width / 2;
          const cy = rect.top + rect.height / 2;
          this.gazeTarget.x = Math.max(-1, Math.min(1, (e.clientX - cx) / (window.innerWidth / 2)));
          this.gazeTarget.y = Math.max(-1, Math.min(1, (e.clientY - cy) / (window.innerHeight / 2)));
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

    setEmotion(moodName) {
      this.emotion = moodName;
      const G = window.gsap || null;
      if (moodName === 'happy' || moodName === 'excited') {
        if (this.eyes) this.eyes.mood(0.5);
        if (this.mouth && this.mouth.setMood) this.mouth.setMood(1.6, 0.4);
        if (G) G.to(this, { jump: 0.12, duration: 0.2, repeat: 1, yoyo: true, ease: 'power2.out' });
      } else if (moodName === 'sad' || moodName === 'hesitant') {
        if (this.eyes) this.eyes.mood(0.85);
        if (this.mouth && this.mouth.setMood) this.mouth.setMood(0.2, 0.1);
      } else {
        if (this.eyes) this.eyes.mood(1.0);
        if (this.mouth && this.mouth.setMood) this.mouth.setMood(1.0, 0);
      }
    }

    start() {
      this.isRunning = true;
      const clock = new THREE.Clock();
      const animate = () => {
        if (!this.isRunning) return;
        requestAnimationFrame(animate);
        const dt = Math.min(clock.getDelta(), 0.1);
        const time = clock.getElapsedTime();

        const breath = Math.sin(time * 1.85 + this.phase) * .009;
        this.bodyGroup.scale.set(this.squash, (1 + breath) / Math.sqrt(this.squash), this.squash);
        this.root.position.y = 0.10 + Math.sin(time * 1.35 + this.phase) * .012 + this.jump + this.stanceY;

        const st = time * .55 + this.phase;
        this.root.rotation.z = this.hipBase + this.wiggle + Math.sin(st * 1.15) * .012;
        this.root.rotation.y = this.spin + Math.sin(st * .42) * .035;

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
  }

  return MochiCharacter;
}));
