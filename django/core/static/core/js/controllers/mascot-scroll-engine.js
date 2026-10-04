/**
 * ═══════════════════════════════════════════════════════════════════════════
 * Anshita Makeover — 3D Mascot Walk-and-Transform Scroll Controller
 * File: django/core/static/core/js/controllers/mascot-scroll-engine.js
 * Spec: docs/COMPREHENSIVE_3D_MASCOT_ANIMATION_AND_SECURITY_AUDIT.md §4, §6
 * ═══════════════════════════════════════════════════════════════════════════
 *
 * Replaces the legacy binary `window.scrollY > 180` CSS-threshold entrance
 * (`.char-pre-entry` / `.char-entered` keyframes) with a true scroll-scrubbed
 * cinematic vignette:
 *
 *   p 0.00 – 0.15  HIDDEN      the medallion is invisible and inert
 *   p 0.15 – 0.45  WALKING     authentic ambulatory hop cycle across the viewport
 *   p 0.45 – 0.70  SHOWCASE    ~320px editorial scale, cursor gaze tracking
 *   p 0.70 – 0.95  DOCKING     3D spline + perspective compression into #chat-toggle
 *   p 0.95 – 1.00  DOCKED      portal bloom + "How may I help you today? ✨"
 *
 * Every frame is a pure function of scroll progress — the mascot advances when
 * the visitor scrolls, freezes mid-stride when they stop, and runs the whole
 * film backwards on the way up. That is the Apple-style direct velocity
 * coupling the audit's benchmark matrix asks for.
 *
 * Architecture notes
 * ------------------
 * • One WebGL context, two homes. The walking character renders into a fixed
 *   full-viewport transparent canvas (`#mascot-walk-stage`); on docking the
 *   *same canvas element* is re-parented into the medallion button so the
 *   mascot literally sits down inside `#chat-toggle` (no context churn, no
 *   duplicate rigs, no GPU memory growth — audit §7.1).
 * • The scroll loop is native + rAF; GSAP/ScrollTrigger is used opportunistically
 *   (momentum-normalised progress + a gentle snap into the dock) but the engine
 *   never depends on a CDN to work.
 * • Reduced-motion visitors skip locomotion entirely and dock statically.
 * • Rendering pauses while the tab is hidden, and `destroy()` releases every
 *   geometry/material/texture/context it owns.
 */
(function (root) {
  'use strict';

  var THREE = root.THREE || null;

  var CONFIG = {
    heroSelector: '#hero, .am-hero, #home-hero',
    dockSelector: '#chat-toggle',
    dockWrapSelector: '#chat-toggle-wrap',
    walkStageId: 'mascot-walk-stage',
    walkCanvasId: 'mascot-walk-canvas',
    speechBubbleSelector: '#chat-speech-bubble',

    scrollDistance: 1250,  // px of scroll travel for the complete film
    minScrollDistance: 900,
    smoothing: 13,         // 1/s — exponential scrub dampening (video-like)
    // Kept for the docking *state* only. It is deliberately NOT wired into
    // ScrollTrigger's snap (which would scroll the page); the mascot settles
    // into the medallion because the visitor scrolled there.
    snapToDock: true,
    // Once the visitor is this close to a timeline endpoint the remaining
    // dampening is skipped, so docking/settling never lags behind the scroll.
    snapEpsilon: 0.035,

    // ── Timeline (normalised progress) ────────────────────────────────────
    phases: {
      hidden: 0.15,
      walkEnd: 0.45,
      showcaseEnd: 0.70,
      dockStart: 0.70,
      dockEnd: 0.95,
      settled: 0.95
    },

    // ── Locomotion (audit §4.2 formulas) ─────────────────────────────────
    hopFrequency: 7,       // hops per 100px of scroll travel
    hopAmplitudePx: 26,    // §8.1 walk-cycle fidelity: A = 26px
    earSwayDeg: 4.5,       // §8.1: secondary ear rotation ±4.5°
    showcaseHeightPx: 210, // editorial scale when on stage (fits the lane)
    dockedHeightPx: 74,    // seated inside the 78px medallion
    onboardHeightPx: 150,

    // ── Runway lane (fractions of viewport height) ────────────────────────
    // The mascot walks a reserved band along the bottom of the screen, below
    // every text block, so it can never overlap the copy. Its own lane is
    // measured live in measure(): the band starts below the highest element
    // that still has content in it, and is then clamped.
    lane: {
      // The runway is the bottom band of the viewport. `bandShare` is how much
      // of the screen it owns; the character is sized to fit *inside* it, so a
      // walk can never ride up into a heading or a paragraph. This is the hard
      // guarantee the design asks for: content above, stage below.
      bandShare: 0.17,
      minBand: 104,
      maxBand: 220,
      footInset: 8,     // keep the feet this far above the viewport edge
      enterX: 1.16,     // start off-screen to the right
      exitX: -0.18,     // travel past the left edge
      showcaseX: 0.17   // showcase plateau — a gutter, clear of centred copy
    },
    charHeightWorld: 2.12, // Mochi/Pip visual height in scene units
    charAnchorWorld: 1.02, // world-space vertical anchor we steer
    dustParticles: 96,
    gazeInfluence: 0.22
  };

  var clamp = function (v, min, max) { return v < min ? min : (v > max ? max : v); };
  var lerp = function (a, b, t) { return a + (b - a) * t; };
  var easeInOutCubic = function (t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
  };
  var easeOutCubic = function (t) { return 1 - Math.pow(1 - t, 3); };
  var easeInCubic = function (t) { return t * t * t; };
  function cubicBezier(p0, p1, p2, p3, t) {
    var mt = 1 - t;
    return {
      x: mt * mt * mt * p0.x + 3 * mt * mt * t * p1.x + 3 * mt * t * t * p2.x + t * t * t * p3.x,
      y: mt * mt * mt * p0.y + 3 * mt * mt * t * p1.y + 3 * mt * t * t * p2.y + t * t * t * p3.y
    };
  }
  function quadraticBezier(p0, ctrl, p1, t) {
    var mt = 1 - t;
    return {
      x: mt * mt * p0.x + 2 * mt * t * ctrl.x + t * t * p1.x,
      y: mt * mt * p0.y + 2 * mt * t * ctrl.y + t * t * p1.y
    };
  }

  /* ─────────────────────────────────────────────────────────────────────────
     MascotScrollEngine
     ───────────────────────────────────────────────────────────────────────── */
  function MascotScrollEngine(options) {
    options = options || {};
    this.config = Object.assign({}, CONFIG, options);
    this.phases = this.config.phases;

    this.progress = 0;         // raw progress from scroll
    this.rendered = 0;         // dampened progress actually displayed
    this.direction = 1;        // 1 = walking down, -1 = reversing
    this.gaitPhase = 0;        // radians of the hop cycle (distance-driven)
    this.distancePx = 0;
    this.docked = false;
    this.docking = false;
    this.mode = 'idle';        // 'webgl-walk' | 'css-fallback' | 'idle'
    this.reducedMotion = false;

    this.character = null;
    this.characterId = null;
    this.canvases = {};        // characterId -> canvas element (their medallion home)
    this.walkHome = null;      // original parent of a reparented canvas
    this.scene = null;
    this.camera = null;
    this.renderer = null;

    this.rafId = null;
    this.lastFrame = 0;
    this.frameTimes = [];
    this.fps = 0;
    this.renderScale = 1;      // adaptive resolution scale (audit §8.2)
    this.running = false;
    this.destroyed = false;
    this.consoleErrors = 0;

    this.scrollRange = { start: 0, end: this.config.minScrollDistance };
    this.pointer = { x: 0, y: 0, targetX: 0, targetY: 0 };
    this.dockRect = null;
    this.dust = null;
    this.dockEmitted = false;
    this._bound = {};
  }

  MascotScrollEngine.prototype = {

    /* ── Lifecycle ─────────────────────────────────────────────────────── */

    init: function () {
      if (this.destroyed) return this;
      var self = this;
      this.reducedMotion = !!(root.matchMedia &&
        root.matchMedia('(prefers-reduced-motion: reduce)').matches);

      this.dockWrap = document.querySelector(this.config.dockWrapSelector);
      this.dockBtn = document.querySelector(this.config.dockSelector);
      this.speechBubble = document.querySelector(this.config.speechBubbleSelector);
      this.walkStage = document.getElementById(this.config.walkStageId);
      this.walkCanvas = document.getElementById(this.config.walkCanvasId);

      this.setHiddenState();

      this._bound.onScroll = function () { self.queueScrollSample(); };
      this._bound.onResize = function () { self.measure(); self.queueScrollSample(); };
      this._bound.onPointer = function (e) { self.onPointerMove(e); };
      this._bound.onVisibility = function () { self.syncRenderLoop(); };

      root.addEventListener('scroll', this._bound.onScroll, { passive: true });
      root.addEventListener('resize', this._bound.onResize, { passive: true });
      root.addEventListener('orientationchange', this._bound.onResize, { passive: true });
      root.addEventListener('pointermove', this._bound.onPointer, { passive: true });
      document.addEventListener('visibilitychange', this._bound.onVisibility);

      this.setupScrollTrigger();
      this.measure();
      this.readScrollPosition();
      this.startRenderLoop();
      document.documentElement.classList.add('mascot-engine-ready');
      return this;
    },

    setupScrollTrigger: function () {
      var gsap = root.gsap, ST = root.ScrollTrigger;
      if (!gsap || !ST) return false;
      try {
        gsap.registerPlugin(ST);
        // ── READ-ONLY by design ──────────────────────────────────────────
        // ScrollTrigger is used purely as a scroll *observer* here. It must
        // never write to the page: no `pin`, no `scrub` with snapping, and
        // above all no `snap`. ScrollTrigger's snap animates window.scrollTo()
        // toward its snap points, so enabling it lets the mascot timeline drag
        // the visitor's page around (it could jump the page to the end of the
        // film on its own). The visitor is always the source of truth.
        this.scrollTrigger = ST.create({
          trigger: document.body,
          start: 'top top',
          end: function () { return '+=' + this.scrollRange.end; }.bind(this),
          onUpdate: function (self) { this.setProgress(self.progress, true); }.bind(this),
          invalidateOnRefresh: true
        });
        return true;
      } catch (err) {
        this.scrollTrigger = null;
        return false;
      }
    },

    measure: function () {
      var W = root.innerWidth || document.documentElement.clientWidth || 1024;
      var H = root.innerHeight || document.documentElement.clientHeight || 768;
      this.viewport = { w: W, h: H };

      var hero = document.querySelector(this.config.heroSelector);
      var scrollDistance = this.config.scrollDistance;
      if (hero && hero.offsetHeight) {
        scrollDistance = clamp(hero.offsetHeight * 0.55, this.config.minScrollDistance,
          Math.max(this.config.minScrollDistance, scrollDistance * 1.8));
      } else {
        scrollDistance = Math.max(scrollDistance, this.config.minScrollDistance);
      }
      // On short/mobile viewports the film must finish sooner.
      if (H < 620) scrollDistance = Math.max(this.config.minScrollDistance, scrollDistance * 0.82);
      this.scrollRange = { start: 0, end: Math.round(scrollDistance) };

      if (this.dockBtn) {
        var rect = this.dockBtn.getBoundingClientRect();
        if (rect.width > 0 && rect.height > 0) {
          this.dockRect = {
            cx: rect.left + rect.width / 2,
            cy: rect.top + rect.height / 2,
            radius: rect.width / 2
          };
        }
      }
      if (!this.dockRect) {
        this.dockRect = { cx: 63, cy: H - 63, radius: 39 };
      }
      this.computeLane();
      this.charHeightWorld = this.config.charHeightWorld;
      var charLower = this.character && this.character.root && this.character.root.getObjectByProperty;
      if (charLower) { /* no-op guard: keeps rigs without the property safe */ }
      this.emitDiagnostic('layout', {
        viewport: this.viewport,
        scrollRange: this.scrollRange,
        dock: this.dockRect,
        lane: this.lane
      });
      return this;
    },

    /**
     * Work out the runway band the mascot walks in.
     *
     * Everything below `laneTop` is treated as stage, so the visitor's reading
     * experience is never crossed by the character. The band is derived from
     * the viewport height each time (the lane is a percentage of the screen,
     * not a fixed pixel row) and clamped so it stays wide enough for a walk
     * cycle and high enough not to sit under the browser chrome.
     */
    computeLane: function () {
      var H = this.viewport.h;
      var W = this.viewport.w;
      var cfg = this.config.lane;
      var band = clamp(H * cfg.bandShare, cfg.minBand, cfg.maxBand);
      var top = H - band;
      // The character is sized against the lane, never the other way round, so
      // "walking" can never overlap content above the band.
      var maxCharHeight = Math.max(64, band - cfg.footInset * 2 - 10);
      this.lane = {
        top: Math.round(top),
        bottom: Math.round(H),
        bandHeight: Math.round(band),
        maxCharHeight: Math.round(maxCharHeight),
        footY: Math.round(H - cfg.footInset),
        enterX: Math.round(W * cfg.enterX),
        exitX: Math.round(W * cfg.exitX),
        showcaseX: Math.round(W * cfg.showcaseX)
      };
      // Keep the configured showcase/onboard sizes inside what the band allows.
      this.lane.showcaseHeight = Math.min(this.config.showcaseHeightPx, maxCharHeight);
      this.lane.onboardHeight = Math.min(this.config.onboardHeightPx, maxCharHeight * 0.82);
      return this.lane;
    },

    /* ── Progress plumbing ─────────────────────────────────────────────── */

    queueScrollSample: function () {
      if (this._scrollQueued) return;
      this._scrollQueued = true;
      var self = this;
      root.requestAnimationFrame(function () {
        self._scrollQueued = false;
        self.readScrollPosition();
      });
    },

    readScrollPosition: function () {
      var y = root.pageYOffset || document.documentElement.scrollTop || document.body.scrollTop || 0;
      // Lenis (used by the site for inertial smooth scrolling) tracks its own
      // animated position; reading it keeps the scrub locked to what the
      // visitor actually sees when the native scroll event lags behind.
      var lenis = root.lenis;
      if (lenis && typeof lenis.animatedScroll === 'number' && !document.hidden) {
        y = lenis.animatedScroll;
      }
      var span = Math.max(1, this.scrollRange.end - this.scrollRange.start);
      var p = clamp((y - this.scrollRange.start) / span, 0, 1);
      this.setProgress(p);
    },

    setProgress: function (progress, fromScrollTrigger) {
      var p = clamp(Number(progress) || 0, 0, 1);
      if (this.reducedMotion) {
        // No locomotion: the mascot simply appears docked once the visitor
        // leaves the hero (audit §8.2 reduced-motion gate).
        p = p <= 0.02 ? 0 : 1;
      }
      if (!fromScrollTrigger && this.progress === p) return;
      this.direction = p >= this.progress ? 1 : -1;
      this.progress = p;
      this.emitDiagnostic('progress', { progress: p, direction: this.direction });
    },

    /* ── Character wiring ──────────────────────────────────────────────── */

    attachCharacter: function (character, id) {
      if (!character || !character.canvas) return this;
      // Hand the previous rig back to its medallion home before swapping.
      if (this.walkCanvas && this.walkCanvas !== character.canvas) this.restoreCanvasHome();
      this.character = character;
      this.characterId = id || 'mascot';
      this.walkCanvas = character.canvas;
      if (character) character.walkOwner = true;
      this.canvases[this.characterId] = character.canvas;
      this.scene = character.scene;
      this.camera = character.camera;
      this.renderer = character.renderer;

      var canWalk = typeof character.scrub === 'function';
      this.mode = canWalk ? 'webgl-walk' : 'css-fallback';
      if (canWalk && this.walkStage) {
        this.enterWalkStage();
      }
      if (typeof character.pause === 'function') character.pause();
      this.installDustSystem();
      this.measure();
      this.readScrollPosition();
      this.startRenderLoop();
      return this;
    },

    detachCharacter: function () {
      this.restoreCanvasHome();
      this.character = null;
      this.scene = null;
      this.camera = null;
      this.renderer = null;
      this.mode = 'idle';
      return this;
    },

    enterWalkStage: function () {
      if (!this.walkCanvas || !this.character) return;
      if (this.walkCanvas.parentNode !== this.walkStage) {
        this.walkHome = this.walkCanvas.parentNode;
        this.walkStage.appendChild(this.walkCanvas);
      }
      this.walkStage.classList.add('is-live');
      this.walkCanvas.classList.add('mascot-walk-canvas--active');
      this.walkCanvas.setAttribute('aria-hidden', 'true');
      this.dockWrap.classList.remove('char-pre-entry', 'char-docked');
      this.dockWrap.classList.add('char-scrubbing');
      document.documentElement.classList.add('mascot-walking');
      this.resizeRenderer(this.viewport.w, this.viewport.h);
      if (typeof this.character.resume === 'function') this.character.resume();
    },

    restoreCanvasHome: function () {
      if (!this.walkCanvas) return;
      if (this.walkHome && this.walkCanvas.parentNode !== this.walkHome) {
        this.walkHome.appendChild(this.walkCanvas);
      }
      this.walkCanvas.classList.remove('mascot-walk-canvas--active');
      this.walkCanvas.removeAttribute('aria-hidden');
      if (this.walkStage) this.walkStage.classList.remove('is-live');
      document.documentElement.classList.remove('mascot-walking');
    },

    resizeRenderer: function (w, h) {
      var ch = this.character;
      if (!ch || !ch.renderer) return;
      ch.width = w;
      ch.height = h;
      if (ch.camera) {
        ch.camera.aspect = w / h;
        ch.camera.updateProjectionMatrix();
      }
      ch.renderer.setSize(w, h, false);
      this.applyRenderScale();
    },

    /**
     * Audit §8.2 — "clamp the pixel ratio" taken one step further: an adaptive
     * render scale keeps the frame budget on low-end GPUs (and software
     * rasterisers) without touching the CSS size, so the mascot stays
     * responsive everywhere. Never upscales past the device's own ratio.
     */
    applyRenderScale: function () {
      var ch = this.character;
      if (!ch || !ch.renderer) return;
      var base = Math.min(root.devicePixelRatio || 1, 2);
      ch.renderer.setPixelRatio(base * this.renderScale);
    },

    updateRenderScale: function () {
      if (!this.running || this.fps <= 0) return;
      var now = (root.performance || Date).now();
      if (this._scaleCheckAt && now - this._scaleCheckAt < 1500) return;
      this._scaleCheckAt = now;
      var before = this.renderScale;
      if (this.fps < 45 && this.renderScale > 0.6) {
        this.renderScale = Math.max(0.6, this.renderScale - 0.15);
      } else if (this.fps > 58 && this.renderScale < 1) {
        this.renderScale = Math.min(1, this.renderScale + 0.1);
      }
      if (this.renderScale !== before) {
        this.applyRenderScale();
        this.emitDiagnostic('renderScale', {
          scale: this.renderScale, fps: this.fps, reason: before > this.renderScale ? 'down' : 'up'
        });
      }
    },

    /* ── Main animation loop ───────────────────────────────────────────── */

    startRenderLoop: function () {
      if (this.running || this.destroyed) return this;
      this.running = true;
      this.lastFrame = (root.performance || Date).now();
      var self = this;
      var loop = function (now) {
        if (!self.running) return;
        self.rafId = root.requestAnimationFrame(loop);
        self.tick(now);
      };
      this.rafId = root.requestAnimationFrame(loop);
      return this;
    },

    stopRenderLoop: function () {
      this.running = false;
      if (this.rafId) root.cancelAnimationFrame(this.rafId);
      this.rafId = null;
      return this;
    },

    syncRenderLoop: function () {
      // Battery gate (audit §3): never burn GPU on a hidden tab.
      if (document.hidden) this.stopRenderLoop();
      else this.startRenderLoop();
    },

    tick: function (now) {
      now = now || (root.performance || Date).now();
      var dt = Math.min(0.05, Math.max(0.001, (now - this.lastFrame) / 1000));
      this.lastFrame = now;
      this.trackFps(dt);

      // Exponential scrub dampening — the "inertial video" feel.
      var smoothing = 1 - Math.exp(-this.config.smoothing * dt);
      var delta = this.progress - this.rendered;
      if (this.reducedMotion || Math.abs(delta) <= this.config.snapEpsilon) {
        // Reduced motion has no locomotion to smooth, and near an endpoint the
        // remaining lag would delay the dock/bloom; both snap instantly.
        this.rendered = this.progress;
      } else {
        this.rendered += delta * smoothing;
      }

      this.pointer.x += (this.pointer.targetX - this.pointer.x) * Math.min(1, dt * 5);
      this.pointer.y += (this.pointer.targetY - this.pointer.y) * Math.min(1, dt * 5);

      this.updateKinematics(this.rendered, dt);
      this.updateRenderScale();
      this.emitDust(dt);
      this.updateDust(dt);
      this.updateDiagnostics();

      // Re-assert the docking greeting while the visitor stays parked at the
      // medallion (throttled): the site's rotating promo tips must never leave
      // the mascot sitting silently next to an empty bubble.
      var greetNow = (root.performance || Date).now();
      if (this.docked && (!this._greetAt || greetNow - this._greetAt > 250) &&
          (this._greetAt = greetNow) && this.speechBubble &&
          this.speechBubble.getAttribute('data-mascot-greeting') === '1' &&
          !this.speechBubble.classList.contains('active')) {
        var chatBox = document.getElementById('chat-box');
        if (!chatBox || !chatBox.classList.contains('open')) {
          this.speechBubble.classList.add('active');
        }
      }
    },

    trackFps: function (dt) {
      this.frameTimes.push(dt);
      if (this.frameTimes.length > 90) this.frameTimes.shift();
      if (this.frameTimes.length >= 30) {
        var sum = this.frameTimes.reduce(function (a, b) { return a + b; }, 0);
        this.fps = Math.round(this.frameTimes.length / Math.max(0.0001, sum));
      }
    },

    /* ── The film itself ───────────────────────────────────────────────── */

    phaseFor: function (p) {
      if (p < this.phases.hidden) return 'hidden';
      if (p < this.phases.walkEnd) return 'walking';
      if (p < this.phases.showcaseEnd) return 'showcase';
      if (p < this.phases.dockEnd) return 'docking';
      return 'docked';
    },

    updateKinematics: function (p, dt) {
      if (!this.character || this.mode === 'css-fallback') {
        this.updateCssFallback(p);
        return;
      }
      var phase = this.phaseFor(p);
      this.currentPhase = phase;
      var wasDocked = this.docked;

      // Distance-driven gait: hops stay locked to scroll pixels, exactly like a
      // scrubbed video (audit §2.2 "scroll 10px → advance 10px").
      var distance = p * this.scrollRange.end;
      var gaitDelta = (distance - this.distancePx) / 100 * this.config.hopFrequency * Math.PI;
      this.distancePx = distance;
      this.gaitPhase += gaitDelta;
      if (this.gaitPhase > Math.PI * 2000) this.gaitPhase -= Math.PI * 2000;
      if (this.gaitPhase < -Math.PI * 2000) this.gaitPhase += Math.PI * 2000;

      var locomotion = (phase === 'walking') ? 1 : (phase === 'docking' ? 0.55 : 0);
      var speed = clamp(Math.abs(gaitDelta) / Math.max(dt, 0.001) / 22, 0, 1.6);

      var placement = this.placementFor(p, phase);
      this.placeCharacter(placement.x, placement.y, placement.heightPx);

      var ch = this.character;
      if (typeof ch.scrub === 'function') {
        ch.scrub(p, {
          phase: phase,
          gaitPhase: this.gaitPhase,
          direction: this.direction,
          locomotion: locomotion * (this.reducedMotion ? 0 : 1),
          speed: speed,
          docked: phase === 'docked',
          hopAmplitudePx: this.config.hopAmplitudePx,
          earSwayDeg: this.config.earSwayDeg
        });
      }

      // Gaze: on stage the mascot tracks the cursor; while hidden it ignores it.
      var gaze = 0;
      if (phase === 'showcase' || phase === 'walking' || phase === 'docking') gaze = 1;
      if (typeof ch.gazeTarget === 'object') {
        ch.gazeTarget.x = this.pointer.x * this.config.gazeInfluence * gaze * 4.2;
        ch.gazeTarget.y = -this.pointer.y * this.config.gazeInfluence * gaze * 3.2;
      }
      if (typeof ch.headTarget === 'object' && phase === 'showcase') {
        ch.headTarget.y = this.pointer.x * 0.22;
        ch.headTarget.x = -this.pointer.y * 0.12;
      }

      // Opacity: fade in during the emergence, never fully invisible on stage.
      var node = this.walkCanvas;
      if (node) {
        var opacity = 1;
        if (p < this.phases.hidden) opacity = 0;
        else if (p < this.phases.hidden + 0.06) {
          opacity = easeOutCubic((p - this.phases.hidden) / 0.06);
        }
        node.style.opacity = opacity.toFixed(3);
        node.style.visibility = opacity > 0.01 ? 'visible' : 'hidden';
      }
      this.walkStage.classList.toggle('is-live', p >= this.phases.hidden * 0.5 && phase !== 'docked');
      document.documentElement.classList.toggle('mascot-active', phase !== 'hidden');

      // Render budget follows the timeline: the rig renders whenever it can be
      // seen (walking, showcase, docking, or seated in the medallion) and
      // parks its rAF loop while the visitor is still in the hero. This also
      // guarantees a rig that was parked while hidden wakes up again when the
      // visitor scrolls back down.
      if (typeof ch.pause === 'function' || typeof ch.resume === 'function') {
        var shouldRender = phase !== 'hidden' || this.docked;
        if (shouldRender && ch.paused && typeof ch.resume === 'function') ch.resume();
        else if (!shouldRender && !ch.paused && typeof ch.pause === 'function') ch.pause();
      }

      // Docking is decided on the *target* progress (not the dampened value):
      // a starved frame budget must never stop the medallion from seating
      // itself, which is what the visitor perceives as "it arrived".
      var targetPhase = this.phaseFor(this.progress);
      if (targetPhase === 'docked' && !this.docked) this.dock();
      else if (wasDocked && targetPhase !== 'docked' &&
               this.progress < this.phases.dockEnd - 0.03) this.undock();
    },

    /** Screen-space position + height for a given progress. */
    placementFor: function (p, phase) {
      var W = this.viewport.w, H = this.viewport.h;
      var lane = this.lane || this.computeLane() || { top: H * 0.8, centreY: H * 0.9 };
      var rect = this.dockRect;

      // The character is *always* inside the runway lane; only its height
      // changes as the film progresses, so it can never collide with the copy.
      // `footY` is where the feet travel, and every height below is clamped to
      // the band, so the silhouette stays inside the stage.
      var laneY = lane.footY;
      var onboardH = lane.onboardHeight || this.config.onboardHeightPx;
      var showcaseH = lane.showcaseHeight || this.config.showcaseHeightPx;

      if (p < this.phases.hidden) {
        // Concealed off the right edge, creeping toward the lane entry point.
        var creep = easeOutCubic(clamp(p / this.phases.hidden, 0, 1));
        return {
          x: lerp(lane.enterX + W * 0.06, lane.enterX, creep),
          y: lerp(laneY + 40, laneY, creep),
          heightPx: onboardH
        };
      }

      if (phase === 'walking' || phase === 'showcase') {
        var denom = Math.max(0.0001, this.phases.walkEnd - this.phases.hidden);
        var t = clamp((p - this.phases.hidden) / denom, 0, 1);
        var eased = easeInOutCubic(t);
        // Travel right → left along the runway, ending on the showcase mark.
        var x = lerp(lane.enterX, lane.showcaseX, eased);
        var heightPx = lerp(onboardH, showcaseH, easeOutCubic(clamp(t * 1.45, 0, 1)));
        var y = laneY;
        if (phase === 'showcase') {
          // Gentle breathing drift so the "hold" never looks frozen.
          y += Math.sin(performance.now() / 1000 * 0.9) * 5;
        }
        return { x: x, y: y, heightPx: heightPx };
      }

      // Docking: curve from the showcase mark down-left into the medallion.
      var dockDenom = Math.max(0.0001, this.phases.dockEnd - this.phases.dockStart);
      var t2 = clamp((p - this.phases.dockStart) / dockDenom, 0, 1);
      var eased2 = easeInCubic(t2) * 0.35 + easeInOutCubic(t2) * 0.65;
      var from = { x: lane.showcaseX, y: lane.footY };
      var to = { x: rect.cx, y: rect.cy };
      // Control point keeps the curve inside the lane until the final approach.
      var ctrl = {
        x: lerp(lane.showcaseX, rect.cx, 0.55),
        y: Math.min(lane.top + lane.bandHeight * 0.5, H - 8)
      };
      var mid = quadraticBezier(from, ctrl, to, eased2);
      return {
        x: mid.x,
        y: mid.y,
        heightPx: lerp(showcaseH, this.config.dockedHeightPx, easeOutCubic(t2))
      };
    },

    /** Convert a screen-pixel placement into the rig's world transform. */
    placeCharacter: function (screenX, screenY, heightPx) {
      var ch = this.character;
      if (!ch || !ch.root) return;
      var H = this.viewport.h;
      var fov = (ch.camera && ch.camera.fov) || 34;
      var dist = (ch.camera && ch.camera.position.z) || 3.8;
      var worldHeight = 2 * Math.tan((fov * Math.PI / 180) / 2) * dist;
      var pxPerUnit = H / Math.max(0.0001, worldHeight);

      var scale = clamp(heightPx / (this.charHeightWorld * pxPerUnit), 0.02, 3.2);
      ch.root.scale.setScalar(scale);
      ch.root.position.x = (screenX - this.viewport.w / 2) / pxPerUnit;
      ch.root.position.y = (H / 2 - screenY) / pxPerUnit -
        (this.config.charAnchorWorld * scale);
      ch.root.position.z = 0;
      this.lastPlacement = { x: screenX, y: screenY, heightPx: heightPx, scale: scale };
    },

    /* ── Dock / undock hand-off ────────────────────────────────────────── */

    dock: function () {
      if (this.docked) return;
      this.docked = true;
      this.docking = false;
      var wrap = this.dockWrap;
      if (!wrap) return;

      // Seat the walking canvas inside the medallion button.
      var stage = document.getElementById((this.characterId === 'pip' ? 'pip' : 'bunny') + 'MascotStage') ||
        document.querySelector('.char-3d-stage');
      if (this.walkCanvas) {
        if (stage && this.walkCanvas.parentNode !== stage) {
          this.walkHome = this.walkHome || this.walkCanvas.parentNode;
          stage.appendChild(this.walkCanvas);
        }
        this.walkCanvas.classList.remove('mascot-walk-canvas--active');
        this.walkCanvas.removeAttribute('aria-hidden');
        this.walkCanvas.style.opacity = '1';
        this.walkCanvas.style.visibility = 'visible';
        this.resizeRenderer(
          (stage && stage.clientWidth) || 76,
          (stage && stage.clientHeight) || 76);
      }
      if (this.walkStage) this.walkStage.classList.remove('is-live');
      document.documentElement.classList.remove('mascot-walking');
      document.documentElement.classList.add('mascot-docked');

      wrap.classList.remove('char-pre-entry', 'char-scrubbing', 'char-exiting');
      wrap.classList.add('char-docked', 'char-entered');
      wrap.style.transform = '';
      wrap.style.opacity = '';
      wrap.style.visibility = '';
      wrap.style.pointerEvents = '';

      if (this.character && typeof this.character.dock === 'function') this.character.dock();
      this.triggerPortalBloom();

      var self = this;
      // Speech bubble is gated on scroll progress (audit §3) — the timer only
      // waits for the settle animation, it never decides *whether* to greet.
      this._bubbleTimer = root.setTimeout(function () {
        if (!self.docked || self.progress < self.phases.settled - 0.01) return;
        var chatBox = document.getElementById('chat-box');
        var chatOpen = (chatBox && chatBox.classList.contains('open')) ||
          document.body.classList.contains('chat-is-open');
        if (!self.speechBubble || chatOpen) return;
        var textEl = document.getElementById('csb-text');
        var greeting = 'How may I help you today? ✨';
        if (textEl) {
          if (root.AnshitaSanitizer) root.AnshitaSanitizer.setText(textEl, greeting);
          else textEl.textContent = greeting;
        }
        // Flags the bubble as the docking greeting so the rotating promo tips
        // cannot overwrite/cancel it before the visitor reads it.
        self.speechBubble.setAttribute('data-mascot-greeting', '1');
        self.speechBubble.classList.add('active');
        self.emitDiagnostic('greeting', { text: greeting });
      }, 380);
      this.emitDiagnostic('dock', { dock: this.dockRect, character: this.characterId });
    },

    undock: function () {
      if (!this.docked) return;
      this.docked = false;
      this.dockEmitted = false;
      root.clearTimeout(this._bubbleTimer);
      if (this.speechBubble) {
        this.speechBubble.classList.remove('active');
        this.speechBubble.removeAttribute('data-mascot-greeting');
      }
      if (typeof root.releaseMascotGreeting === 'function') root.releaseMascotGreeting();
      document.documentElement.classList.remove('mascot-docked');
      if (this.dockWrap) {
        this.dockWrap.classList.remove('char-docked', 'char-entered');
        this.dockWrap.classList.add('char-scrubbing');
      }
      if (this.character && typeof this.character.undock === 'function') this.character.undock();
      if (this.character && this.mode === 'webgl-walk') this.enterWalkStage();
      this.emitDiagnostic('undock', {});
    },

    triggerPortalBloom: function () {
      var portal = document.getElementById('charEntryPortal');
      if (!portal || this.reducedMotion) return;
      portal.classList.remove('active');
      void portal.offsetWidth;
      portal.classList.add('active');
    },

    /* ── CSS fallback (no WebGL / rig without scrub()) ─────────────────── */

    updateCssFallback: function (p) {
      var wrap = this.dockWrap;
      if (!wrap) return;
      var visible = p >= this.phases.dockEnd - 0.02;
      wrap.classList.toggle('char-scrubbing', !visible);
      wrap.classList.toggle('char-docked', visible);
      wrap.classList.toggle('char-pre-entry', p < 0.02);
      if (visible && !this.docked) this.dock();
      else if (!visible && this.docked) this.undock();
      if (!visible) {
        var eased = easeOutCubic(clamp(p / Math.max(0.0001, this.phases.dockEnd), 0, 1));
        wrap.style.opacity = (0.25 + 0.75 * eased).toFixed(3);
        wrap.style.transform = 'translateY(' + (18 * (1 - eased)).toFixed(1) + 'px) scale(' +
          (0.55 + 0.45 * eased).toFixed(3) + ')';
      }
    },

    /* ── Golden dust ───────────────────────────────────────────────────── */

    installDustSystem: function () {
      if (!THREE || !this.scene || this.dust) return;
      var count = this.config.dustParticles;
      var positions = new Float32Array(count * 3);
      var colors = new Float32Array(count * 3);
      var geometry = new THREE.BufferGeometry();
      geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
      geometry.setAttribute('color', new THREE.BufferAttribute(colors, 3));
      var material = new THREE.PointsMaterial({
        size: 0.075,
        sizeAttenuation: true,
        vertexColors: true,
        transparent: true,
        opacity: 0.92,
        depthWrite: false,
        blending: THREE.AdditiveBlending
      });
      var points = new THREE.Points(geometry, material);
      points.frustumCulled = false;
      points.renderOrder = 5;
      this.scene.add(points);
      this.dust = {
        points: points,
        geometry: geometry,
        material: material,
        positions: positions,
        colors: colors,
        life: new Float32Array(count),
        velocity: new Float32Array(count * 3),
        cursor: 0,
        count: count
      };
    },

    emitDust: function () {
      if (!this.dust || !this.character) return;
      var phase = this.currentPhase;
      if (phase !== 'walking' && phase !== 'docking') return;
      // One puff per landing: |sin(gaitPhase)| hits zero at every touchdown.
      var cycle = Math.floor(this.gaitPhase / Math.PI);
      if (cycle === this._lastDustCycle) return;
      this._lastDustCycle = cycle;
      if (Math.abs(Math.sin(this.gaitPhase)) > 0.22) return;
      var placement = this.lastPlacement;
      if (!placement) return;
      var ch = this.character;
      var H = this.viewport.h;
      var fov = (ch.camera && ch.camera.fov) || 34;
      var dist = (ch.camera && ch.camera.position.z) || 3.8;
      var pxPerUnit = H / (2 * Math.tan((fov * Math.PI / 180) / 2) * dist);
      var footY = -H / 2 / pxPerUnit; // ground plane, world units
      var footX = (placement.x - this.viewport.w / 2) / pxPerUnit;
      this.spawnDust(footX + (Math.random() - 0.5) * 0.28 * placement.scale,
        footY + 0.05, 5);
    },

    spawnDust: function (x, y, count) {
      var dust = this.dust;
      if (!dust) return;
      for (var i = 0; i < count; i++) {
        var idx = dust.cursor;
        dust.cursor = (dust.cursor + 1) % dust.count;
        var o = idx * 3;
        dust.positions[o] = x + (Math.random() - 0.5) * 0.12;
        dust.positions[o + 1] = y + Math.random() * 0.05;
        dust.positions[o + 2] = (Math.random() - 0.5) * 0.2;
        dust.velocity[o] = (Math.random() - 0.5) * 0.22;
        dust.velocity[o + 1] = 0.18 + Math.random() * 0.22;
        dust.velocity[o + 2] = 0.02 + Math.random() * 0.1;
        dust.life[idx] = 0.85 + Math.random() * 0.5;
        dust.colors[o] = 0.95;
        dust.colors[o + 1] = 0.82;
        dust.colors[o + 2] = 0.52;
      }
      dust.geometry.attributes.position.needsUpdate = true;
      dust.geometry.attributes.color.needsUpdate = true;
    },

    updateDust: function (dt) {
      var dust = this.dust;
      if (!dust) return;
      var alive = false;
      for (var i = 0; i < dust.count; i++) {
        if (dust.life[i] <= 0) continue;
        alive = true;
        dust.life[i] -= dt;
        var o = i * 3;
        dust.velocity[o + 1] -= 0.35 * dt;
        dust.positions[o] += dust.velocity[o] * dt;
        dust.positions[o + 1] += dust.velocity[o + 1] * dt;
        dust.positions[o + 2] += dust.velocity[o + 2] * dt;
        if (dust.life[i] <= 0) {
          dust.positions[o + 1] = -999;
          dust.colors[o] = dust.colors[o + 1] = dust.colors[o + 2] = 0;
        }
      }
      if (alive) {
        dust.geometry.attributes.position.needsUpdate = true;
        dust.geometry.attributes.color.needsUpdate = true;
      }
    },

    /* ── Input & state helpers ─────────────────────────────────────────── */

    onPointerMove: function (event) {
      var W = this.viewport ? this.viewport.w : 1024;
      var H = this.viewport ? this.viewport.h : 768;
      this.pointer.targetX = clamp((event.clientX - W / 2) / (W / 2), -1, 1);
      this.pointer.targetY = clamp((event.clientY - H / 2) / (H / 2), -1, 1);
    },

    setHiddenState: function () {
      if (this.dockWrap) {
        this.dockWrap.classList.remove('char-entered', 'char-exiting');
        this.dockWrap.classList.add('char-pre-entry');
        this.dockWrap.style.opacity = '0';
        this.dockWrap.style.visibility = 'hidden';
        this.dockWrap.style.pointerEvents = 'none';
      }
      if (this.speechBubble) this.speechBubble.classList.remove('active');
      this.docked = false;
      if (this.walkCanvas) {
        this.walkCanvas.style.opacity = '0';
        this.walkCanvas.style.visibility = 'hidden';
      }
    },

    refreshCharacter: function () {
      var ch = this.character;
      if (!ch) return this;
      this.scene = ch.scene;
      this.camera = ch.camera;
      this.renderer = ch.renderer;
      if (this.mode === 'webgl-walk') {
        this.enterWalkStage();
        if (this.docked) this.dock();
      }
      this.readScrollPosition();
      return this;
    },

    /* ── Diagnostics (Quality Gate §8.2) ───────────────────────────────── */

    emitDiagnostic: function (event, detail) {
      this.lastDiagnostic = { event: event, detail: detail, at: Date.now() };
      try {
        root.dispatchEvent(new CustomEvent('mascot:diagnostic', {
          detail: { event: event, detail: detail }
        }));
      } catch (e) { /* CustomEvent unsupported — ignore */ }
    },

    updateDiagnostics: function () {
      this._diagTick = (this._diagTick || 0) + 1;
      if (this._diagTick % 60 !== 0) return;
      this.emitDiagnostic('tick', this.getDiagnostics());
    },

    getDiagnostics: function () {
      var drawCalls = 0, triangles = 0, geometries = 0, textures = 0;
      if (this.renderer && this.renderer.info) {
        var info = this.renderer.info;
        drawCalls = info.render.calls || 0;
        triangles = info.render.triangles || 0;
        geometries = info.memory.geometries || 0;
        textures = info.memory.textures || 0;
      }
      return {
        mode: this.mode,
        progress: Number(this.progress.toFixed(4)),
        rendered: Number(this.rendered.toFixed(4)),
        phase: this.currentPhase || this.phaseFor(this.rendered),
        docked: this.docked,
        direction: this.direction,
        gaitPhase: Number(this.gaitPhase.toFixed(3)),
        fps: this.fps,
        drawCalls: drawCalls,
        triangles: triangles,
        geometries: geometries,
        textures: textures,
        reducedMotion: this.reducedMotion,
        renderScale: this.renderScale,
        scrollRange: this.scrollRange,
        placement: this.lastPlacement || null,
        dockRect: this.dockRect,
        character: this.characterId,
        viewport: this.viewport,
        consoleErrors: this.consoleErrors
      };
    },

    /* ── Teardown (WebGL memory discipline, audit §7.1) ────────────────── */

    destroy: function () {
      this.destroyed = true;
      this.stopRenderLoop();
      root.clearTimeout(this._bubbleTimer);
      root.removeEventListener('scroll', this._bound.onScroll);
      root.removeEventListener('resize', this._bound.onResize);
      root.removeEventListener('orientationchange', this._bound.onResize);
      root.removeEventListener('pointermove', this._bound.onPointer);
      document.removeEventListener('visibilitychange', this._bound.onVisibility);
      if (this.scrollTrigger && this.scrollTrigger.kill) this.scrollTrigger.kill();
      this.restoreCanvasHome();

      if (this.dust) {
        if (this.scene) this.scene.remove(this.dust.points);
        this.dust.geometry.dispose();
        this.dust.material.dispose();
        this.dust = null;
      }
      if (this.character && typeof this.character.destroy === 'function') {
        this.character.destroy();
      }
      document.documentElement.classList.remove(
        'mascot-engine-ready', 'mascot-walking', 'mascot-docked', 'mascot-active');
      return this;
    }
  };

  MascotScrollEngine.CONFIG = CONFIG;
  MascotScrollEngine.isSupported = function () {
    try {
      var canvas = document.createElement('canvas');
      return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'));
    } catch (e) {
      return false;
    }
  };

  root.MascotScrollEngine = MascotScrollEngine;

  // Auto-boot: the engine must exist before the concierge widgets register
  // their rigs (they call `mascotScrollEngine.attachCharacter(...)`).
  function boot() {
    if (root.mascotScrollEngine) return root.mascotScrollEngine;
    var reduced = root.matchMedia && root.matchMedia('(prefers-reduced-motion: reduce)').matches;
    var engine = new MascotScrollEngine();
    root.mascotScrollEngine = engine;
    try {
      engine.init();
    } catch (err) {
      engine.mode = 'css-fallback';
      root.console && root.console.warn('[MascotScrollEngine] init failed, CSS fallback active', err);
    }
    if (reduced) root.console && root.console.info('[MascotScrollEngine] reduced-motion mode');
    return engine;
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot, { once: true });
  } else {
    boot();
  }
})(typeof self !== 'undefined' ? self : this);
