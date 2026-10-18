/*
 * Pip's one-shot arrival for the active concierge widget.
 *
 * This deliberately lives beside the chatbot integration (base.html +
 * components/chatbot_modal.html), not in the unused concierge prototype.
 * The page's protected studio entrance remains the animation owner until its
 * GSAP timeline completes; only then does this controller borrow Pip's existing
 * WebGL canvas for a short, screen-space flight and return it to the launcher.
 */
(function (window, document) {
  'use strict';

  var STORAGE_KEY = 'anshita_active_char';
  var ARRIVAL_KEY = 'anshita_pip_arrival_v1';
  var SUBPAGE_GREETING_KEY = 'anshita_pip_subpage_greeting_v1';
  var GREETING = 'Namaste! I’m Pip, your friendly guide. Would you like to explore bridal looks or ask a question?';
  var GREETING_SUB = 'Pip · Anshita Makeover';
  var HOME_PATH = window.location && window.location.pathname === '/';
  var REDUCED_MOTION = !!(window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches);
  var originalToggle = window.toggleActiveConciergeCharacter;
  var originalSpeech = window.setConciergeSpeech;
  var originalScrollCheck = window.checkConciergeScrollPosition;
  var originalEntrance = window.triggerConciergeEntrance;
  var originalExit = window.triggerConciergeExit;

  var state = {
    active: 'pip',
    pipMode: false,
    booted: false,
    heroDone: false,
    heroHooked: false,
    arrivalSettled: false,
    welcomeShown: false,
    flight: null,
    flightTimer: 0,
    diagnostics: { state: 'idle', frames: 0, maxDrawCalls: 0, drawCalls: 0, budgetPassed: null }
  };

  function storageGet(key) {
    try { return window.localStorage.getItem(key); } catch (error) { return null; }
  }

  function storageSet(key, value) {
    try { window.localStorage.setItem(key, value); } catch (error) { /* private mode */ }
  }

  function sessionHasArrived() {
    try { return window.sessionStorage.getItem(ARRIVAL_KEY) === '1'; } catch (error) { return false; }
  }

  function sessionHasSubpageGreeting() {
    try { return window.sessionStorage.getItem(SUBPAGE_GREETING_KEY) === '1'; } catch (error) { return false; }
  }

  function markSubpageGreeting() {
    try { window.sessionStorage.setItem(SUBPAGE_GREETING_KEY, '1'); } catch (error) { /* private mode */ }
  }

  function markArrived() {
    try { window.sessionStorage.setItem(ARRIVAL_KEY, '1'); } catch (error) { /* private mode */ }
  }

  function normalizeCharacter(value) {
    if (value === 'mochi' || value === 'bunny') return 'mochi';
    return 'pip';
  }

  function activeCharacter() {
    return normalizeCharacter(window.activeConciergeChar || state.active || storageGet(STORAGE_KEY));
  }

  function setCharacterButton(next) {
    var icon = document.getElementById('charToggleIcon');
    var button = document.getElementById('chat-char-toggle-btn');
    if (icon) icon.textContent = next === 'pip' ? '🐰' : '🐦';
    if (button) {
      button.title = next === 'pip'
        ? 'Switch to Mochi (Velvet Mascot)'
        : 'Switch to Pip (Celestial Finch)';
      button.setAttribute('aria-label', button.title);
    }
  }

  function setPipMode(enabled) {
    state.pipMode = !!enabled;
    if (!state.pipMode) {
      if (originalScrollCheck) window.checkConciergeScrollPosition = originalScrollCheck;
      if (originalEntrance) window.triggerConciergeEntrance = originalEntrance;
      if (originalExit) window.triggerConciergeExit = originalExit;
      return;
    }

    // A one-shot fly-in is the only owner of Pip's screen-space transform.
    // Keep the existing scroll engine available for Mochi, but park its current
    // character while Pip is selected so the two systems never fight.
    window.checkConciergeScrollPosition = function () { return false; };
    window.triggerConciergeEntrance = function () { return false; };
    window.triggerConciergeExit = function () { return false; };

    var engine = window.mascotScrollEngine;
    if (engine) {
      try { if (typeof engine.detachCharacter === 'function') engine.detachCharacter(); } catch (error) {}
      engine.mode = 'idle';
    }
    var rig = window.pipMascotInstance;
    if (rig) rig.walkOwner = false;
    var bubble = document.getElementById('chat-speech-bubble');
    if (bubble) {
      bubble.classList.remove('active');
      bubble.removeAttribute('data-mascot-greeting');
    }
  }

  if (storageGet(STORAGE_KEY) === 'mochi' || storageGet(STORAGE_KEY) === 'bunny') {
    state.active = 'mochi';
    window.activeConciergeChar = 'mochi';
  } else {
    // Pip is the first-visit and invalid/legacy preference default. Asha is
    // intentionally not offered by the active mascot switcher.
    state.active = 'pip';
    window.activeConciergeChar = 'pip';
    storageSet(STORAGE_KEY, 'pip');
  }

  if (typeof originalToggle === 'function') {
    window.toggleActiveConciergeCharacter = function (requested) {
      var previous = activeCharacter();
      var next = requested === 'mochi' || requested === 'bunny'
        ? 'mochi'
        : requested === 'pip'
          ? 'pip'
          : previous === 'pip' ? 'mochi' : 'pip';

      if (previous === 'pip' && next !== 'pip') abortFlight();
      var result = originalToggle.call(this, next);
      state.active = next;
      window.activeConciergeChar = next;
      storageSet(STORAGE_KEY, next);
      setCharacterButton(next);

      if (next === 'pip') {
        state.welcomeShown = sessionHasArrived();
        if (!sessionHasArrived()) state.arrivalSettled = false;
        setPipMode(true);
        if (state.booted && state.heroDone) schedulePipArrival(80);
      } else {
        updateFallbackBird(false);
        setPipMode(false);
        if (state.booted && state.heroDone && !state.arrivalSettled) revealDocked(false);
      }
      return result;
    };
  }

  // Hide any older scheduled concierge line until the requested landing
  // greeting. Calls made after docking continue through the original handler.
  if (typeof originalSpeech === 'function') {
    window.setConciergeSpeech = function () {
      if (state.pipMode && !state.welcomeShown) return;
      return originalSpeech.apply(this, arguments);
    };
  }

  function getStage() {
    var stage = document.getElementById('pip-flight-stage');
    if (stage) return stage;
    stage = document.createElement('div');
    stage.id = 'pip-flight-stage';
    stage.setAttribute('aria-hidden', 'true');
    stage.style.cssText = [
      'position:fixed', 'inset:0', 'width:100vw', 'height:100vh',
      'overflow:hidden', 'pointer-events:none', 'z-index:9401',
      'visibility:hidden', 'opacity:0', 'contain:strict'
    ].join(';');
    document.body.appendChild(stage);
    return stage;
  }

  function getRigParts() {
    var rig = window.pipMascotInstance;
    if (!rig || !rig.canvas || !rig.scene || !rig.camera || !rig.renderer || !rig.root) return null;
    return {
      rig: rig,
      character: rig.character || rig,
      root: rig.root,
      scene: rig.scene,
      camera: rig.camera,
      renderer: rig.renderer,
      canvas: rig.canvas
    };
  }

  function updateFallbackBird(show) {
    var button = document.getElementById('chat-toggle');
    if (!button) return;
    var fallback = button.querySelector('.pip-flight-fallback');
    if (!show) {
      if (fallback) fallback.remove();
      return;
    }
    if (fallback) return;
    fallback = document.createElement('span');
    fallback.className = 'pip-flight-fallback';
    fallback.setAttribute('aria-hidden', 'true');
    fallback.textContent = '🐦';
    fallback.style.cssText = 'position:relative;z-index:2;font-size:34px;line-height:1;filter:drop-shadow(0 2px 8px rgba(0,0,0,.45))';
    button.appendChild(fallback);
  }

  function pushObject(target, value) {
    if (value && value.isObject3D) target.push(value);
  }

  function pushListObjects(target, list, field) {
    if (!Array.isArray(list)) return;
    list.forEach(function (item) {
      if (field && item && item[field]) pushObject(target, item[field]);
      else if (item && item.isObject3D) pushObject(target, item);
    });
  }

  function animatedNodesFor(character, root) {
    var nodes = [];
    [
      character.root, character.bodyGroup, character.headRig, character.crown,
      character.tail, character.beak, character.beakTip, character.sash, character.halo
    ].forEach(function (node) { pushObject(nodes, node); });

    if (character.eyes && Array.isArray(character.eyes.eyes)) {
      character.eyes.eyes.forEach(function (eye) {
        pushObject(nodes, eye.eye);
        pushObject(nodes, eye.iris);
      });
    }
    if (character.brows && Array.isArray(character.brows.pivots)) {
      pushListObjects(nodes, character.brows.pivots);
    }
    pushListObjects(nodes, character.wings, 'group');
    if (character.feetRoot && character.feetRoot.isObject3D) pushObject(nodes, character.feetRoot);
    pushListObjects(nodes, character.feet, 'group');
    pushListObjects(nodes, character.plumes, 'mesh');

    // Preserve individually animated accessories without guessing by name.
    root.traverse(function (object) {
      if (object.userData && object.userData.pipFlightAnimated) pushObject(nodes, object);
    });
    return nodes;
  }

  function flightAnimatedNodes(character, root) {
    var nodes = [];
    pushObject(nodes, root);
    pushObject(nodes, character.headRig);
    pushObject(nodes, character.tail);
    pushObject(nodes, character.feetRoot);
    pushListObjects(nodes, character.wings, 'group');
    if (!character.feetRoot) pushListObjects(nodes, character.feet, 'group');
    return nodes;
  }

  function optimizePipDrawCalls(parts, freezeIdle) {
    var optimizer = window.AnshitaRigOptimizer;
    var character = parts.character;
    var root = character.root || parts.root;
    var animated = freezeIdle
      ? flightAnimatedNodes(character, root)
      : animatedNodesFor(character, root);
    var restores = [];
    var temporarilyMergeable = [];
    var saved = 0;
    var restored = false;
    var flagged = new Set();

    function allowStaticMerge(node) {
      if (!node || !node.userData || !node.userData.noMerge || flagged.has(node)) return;
      flagged.add(node);
      temporarilyMergeable.push({ node: node, value: node.userData.noMerge });
      delete node.userData.noMerge;
    }

    function recordMerge(result) {
      if (result && typeof result === 'object') {
        saved += Number(result.saved) || 0;
        if (typeof result.restore === 'function') restores.push(result.restore);
      } else {
        saved += Number(result) || 0;
      }
    }

    if (freezeIdle) {
      (character.tailFeathers || []).forEach(function (part) {
        allowStaticMerge(part && (part.mesh || part));
      });
      (character.plumes || []).forEach(function (part) {
        allowStaticMerge(part && (part.mesh || part));
      });
      if (character.brows && Array.isArray(character.brows.pivots)) {
        character.brows.pivots.forEach(allowStaticMerge);
      }
      allowStaticMerge(character.beakTip);
    }

    if (root && optimizer) {
      root.updateMatrixWorld(true);
      try {
        if (typeof optimizer.mergeStaticByMaterial === 'function') {
          recordMerge(optimizer.mergeStaticByMaterial(root, animated, { reversible: true }));
        }

        if (typeof optimizer.mergeMaterialFamily === 'function') {
          function mergePalette(hexColors, name) {
            var allowed = new Set(hexColors);
            var materials = [];
            root.traverse(function (object) {
              if (!object.isMesh || Array.isArray(object.material)) return;
              var material = object.material;
              if (!material || (material.isMeshStandardMaterial === undefined && material.isMeshPhysicalMaterial === undefined)) return;
              if (material.transparent || material.map || material.normalMap || material.roughnessMap || material.alphaMap) return;
              if (material.emissive && material.emissive.getHex()) return;
              var hex = material.color && material.color.getHex ? material.color.getHex() : 0;
              if (allowed.has(hex) && materials.indexOf(material) === -1) materials.push(material);
            });
            if (materials.length > 1) {
              recordMerge(optimizer.mergeMaterialFamily(root, materials, animated, {
                name: name,
                reversible: true
              }));
            }
          }

          // During the short flight, only Pip's close teal feather shades and
          // same-finish jewels share vertex-colour materials. Gold, beak, belly,
          // transparent blush and pearls retain their authored PBR treatment.
          mergePalette([0x48aeb1, 0x267679, 0x65c2bb], 'pip-teal-flight');
          mergePalette([0xe77773, 0x8dd4c0, 0x9f71bd], 'pip-jewels-flight');
        }
      } catch (error) {
        if (window.console && window.console.warn) window.console.warn('[PipFlight] draw-call merge skipped', error);
        for (var r = restores.length - 1; r >= 0; r--) restores[r]();
        restores = [];
        temporarilyMergeable.forEach(function (entry) { entry.node.userData.noMerge = entry.value; });
        temporarilyMergeable = [];
      }
    }

    return {
      saved: saved,
      animatedNodes: animated.length,
      restore: function () {
        if (restored) return;
        restored = true;
        for (var i = restores.length - 1; i >= 0; i--) restores[i]();
        temporarilyMergeable.forEach(function (entry) { entry.node.userData.noMerge = entry.value; });
        if (root) root.updateMatrixWorld(true);
      }
    };
  }

  function revealDocked(showWelcome) {
    var wrap = document.getElementById('chat-toggle-wrap');
    if (!wrap) return;
    wrap.classList.remove('char-pre-entry', 'char-entered', 'char-exiting', 'char-scrubbing');
    wrap.classList.add('char-docked');
    wrap.style.opacity = '1';
    wrap.style.visibility = 'visible';
    wrap.style.pointerEvents = 'auto';
    wrap.style.transform = 'none';
    wrap.style.animation = 'none';

    var stage = document.getElementById('pip-flight-stage');
    if (stage) {
      stage.style.visibility = 'hidden';
      stage.style.opacity = '0';
    }
    if (activeCharacter() === 'pip') updateFallbackBird(!getRigParts());
    state.arrivalSettled = true;
    state.diagnostics.state = 'docked';
    if (showWelcome && activeCharacter() === 'pip') showWelcomeBubble();
  }

  function showWelcomeBubble() {
    if (activeCharacter() !== 'pip') return;
    state.welcomeShown = true;
    var chatBox = document.getElementById('chat-box');
    if ((chatBox && chatBox.classList.contains('open')) || document.body.classList.contains('chat-is-open')) return;
    if (typeof originalSpeech === 'function') {
      originalSpeech.call(window, GREETING, GREETING_SUB, 7600);
      return;
    }
    var bubble = document.getElementById('chat-speech-bubble');
    var text = document.getElementById('csb-text');
    if (text) text.textContent = GREETING;
    if (bubble) bubble.classList.add('active');
  }

  function pulseLanding(button) {
    if (!button || REDUCED_MOTION) return;
    var rect = button.getBoundingClientRect();
    var stage = document.createElement('div');
    stage.setAttribute('aria-hidden', 'true');
    stage.style.cssText = 'position:fixed;inset:0;pointer-events:none;z-index:9402;overflow:visible';
    document.body.appendChild(stage);

    [0, 135].forEach(function (delay) {
      var ring = document.createElement('span');
      ring.style.cssText = [
        'position:fixed', 'left:' + (rect.left + rect.width / 2) + 'px',
        'top:' + (rect.top + rect.height / 2) + 'px',
        'width:' + Math.max(56, rect.width * 0.78) + 'px',
        'height:' + Math.max(56, rect.height * 0.78) + 'px',
        'box-sizing:border-box', 'border:1px solid rgba(226,190,103,.92)',
        'border-radius:50%', 'box-shadow:0 0 18px rgba(212,175,55,.26)',
        'opacity:.82', 'transform:translate(-50%,-50%) scale(.58)',
        'pointer-events:none'
      ].join(';');
      stage.appendChild(ring);
      if (typeof ring.animate === 'function') {
        var animation = ring.animate([
          { opacity: 0.82, transform: 'translate(-50%,-50%) scale(.58)' },
          { opacity: 0, transform: 'translate(-50%,-50%) scale(1.72)' }
        ], { duration: 730, delay: delay, easing: 'cubic-bezier(.18,.72,.24,1)', fill: 'forwards' });
        animation.onfinish = function () { if (ring.parentNode) ring.parentNode.removeChild(ring); };
      } else {
        window.setTimeout(function () {
          ring.style.transition = 'opacity .6s ease, transform .6s ease';
          ring.style.opacity = '0';
          ring.style.transform = 'translate(-50%,-50%) scale(1.72)';
        }, delay + 20);
        window.setTimeout(function () { if (ring.parentNode) ring.parentNode.removeChild(ring); }, delay + 700);
      }
    });
    window.setTimeout(function () { if (stage.parentNode) stage.parentNode.removeChild(stage); }, 1100);
  }

  function screenToWorld(parts, x, y, planeZ) {
    var THREE = window.THREE;
    var width = Math.max(1, window.innerWidth || document.documentElement.clientWidth);
    var height = Math.max(1, window.innerHeight || document.documentElement.clientHeight);
    var camera = parts.camera;
    camera.updateMatrixWorld(true);
    var point = new THREE.Vector3((x / width) * 2 - 1, 1 - (y / height) * 2, 0.5).unproject(camera);
    var direction = point.sub(camera.position).normalize();
    var dz = direction.z;
    if (Math.abs(dz) < 0.00001) return new THREE.Vector3(0, 0, planeZ || 0);
    var distance = ((planeZ || 0) - camera.position.z) / dz;
    return camera.position.clone().addScaledVector(direction, distance);
  }

  function bezier(points, t) {
    var u = 1 - t;
    var a = u * u * u;
    var b = 3 * u * u * t;
    var c = 3 * u * t * t;
    var d = t * t * t;
    return {
      x: a * points[0].x + b * points[1].x + c * points[2].x + d * points[3].x,
      y: a * points[0].y + b * points[1].y + c * points[2].y + d * points[3].y
    };
  }

  function createFlightPath(button) {
    var width = Math.max(1, window.innerWidth || document.documentElement.clientWidth);
    var height = Math.max(1, window.innerHeight || document.documentElement.clientHeight);
    var rect = button.getBoundingClientRect();
    var target = { x: rect.left + rect.width / 2, y: rect.top + rect.height / 2 };
    var fliesFromLeft = target.x < width / 2;
    var inward = fliesFromLeft ? 1 : -1;
    var side = fliesFromLeft ? -1 : 1;
    var arcX = Math.max(90, Math.min(220, width * 0.16));
    var arcY = Math.max(190, Math.min(300, height * 0.34));
    var nearX = Math.max(58, Math.min(112, width * 0.085));
    var nearY = Math.max(66, Math.min(112, height * 0.10));
    var offscreen = Math.max(74, Math.min(120, rect.width * 1.35));

    return {
      target: target,
      side: side,
      points: [
        { x: fliesFromLeft ? -offscreen : width + offscreen, y: target.y - Math.min(250, height * 0.28) },
        { x: target.x + inward * arcX, y: Math.max(height * 0.18, target.y - arcY) },
        { x: target.x + inward * nearX, y: target.y - nearY },
        target
      ]
    };
  }

  function makePivot(node, name) {
    if (!node || !node.parent || !window.THREE) return null;
    var parent = node.parent;
    var originalPosition = node.position.clone();
    var pivot = new window.THREE.Group();
    pivot.name = name;
    pivot.position.copy(originalPosition);
    parent.add(pivot);
    parent.remove(node);
    node.position.set(0, 0, 0);
    pivot.add(node);
    return { node: node, parent: parent, pivot: pivot, originalPosition: originalPosition };
  }

  function addFlightPivots(character) {
    var records = { wings: [], tail: null, feet: [] };
    (character.wings || []).forEach(function (wing, index) {
      var node = wing && (wing.group || wing);
      var record = makePivot(node, 'pip-flight-wing-' + index);
      if (record) {
        record.side = typeof wing.side === 'number' ? wing.side : (index === 0 ? -1 : 1);
        records.wings.push(record);
      }
    });
    if (character.tail && character.tail.isObject3D) {
      records.tail = makePivot(character.tail, 'pip-flight-tail');
    }
    if (character.feetRoot && character.feetRoot.isObject3D) {
      var pair = makePivot(character.feetRoot, 'pip-flight-foot-pair');
      if (pair) {
        pair.side = 0;
        records.feet.push(pair);
      }
    } else {
      (character.feet || []).forEach(function (foot, index) {
        var node = foot && (foot.group || foot);
        var record = makePivot(node, 'pip-flight-foot-' + index);
        if (record) {
          record.side = typeof foot.side === 'number' ? foot.side : (index === 0 ? -1 : 1);
          record.foot = foot;
          record.baseY = foot.baseY;
          record.baseZ = foot.baseZ;
          // Older standalone rigs update each foot in the character loop. Move
          // that local rest offset onto our flight pivot so it is not doubled.
          if (typeof foot.baseY === 'number') foot.baseY = 0;
          if (typeof foot.baseZ === 'number') foot.baseZ = 0;
          records.feet.push(record);
        }
      });
    }
    return records;
  }

  function restorePivot(record) {
    if (!record || !record.node || !record.parent) return;
    if (record.node.parent) record.node.parent.remove(record.node);
    record.parent.add(record.node);
    record.node.position.copy(record.originalPosition);
    if (record.foot) {
      if (typeof record.baseY === 'number') record.foot.baseY = record.baseY;
      if (typeof record.baseZ === 'number') record.foot.baseZ = record.baseZ;
    }
    if (record.pivot.parent) record.pivot.parent.remove(record.pivot);
  }

  function resizeRig(parts) {
    if (!parts || !parts.camera || !parts.renderer) return;
    var width = Math.max(1, window.innerWidth || document.documentElement.clientWidth);
    var height = Math.max(1, window.innerHeight || document.documentElement.clientHeight);
    parts.camera.aspect = width / height;
    parts.camera.updateProjectionMatrix();
    parts.renderer.setSize(width, height, false);
    parts.camera.updateMatrixWorld(true);
  }

  function resizeDockedRig(parts) {
    if (!parts || !parts.camera || !parts.renderer) return;
    var rect = parts.canvas.getBoundingClientRect();
    var button = document.getElementById('chat-toggle');
    var width = Math.max(1, Math.round(rect.width || (button && button.clientWidth) || 78));
    var height = Math.max(1, Math.round(rect.height || (button && button.clientHeight) || 78));
    if (typeof parts.rig.resize === 'function') {
      parts.rig.resize(width, height);
      return;
    }
    parts.rig.width = width;
    parts.rig.height = height;
    parts.camera.aspect = width / height;
    parts.camera.updateProjectionMatrix();
    parts.renderer.setSize(width, height, false);
  }

  function restoreFlight(flight) {
    if (!flight || flight.restored) return;
    flight.restored = true;
    if (flight.resizeHandler) window.removeEventListener('resize', flight.resizeHandler);

    if (flight.optimization && typeof flight.optimization.restore === 'function') {
      try { flight.optimization.restore(); } catch (error) {}
    }
    if (flight.shadowMap && typeof flight.shadowMapEnabled === 'boolean') {
      flight.shadowMap.enabled = flight.shadowMapEnabled;
    }
    if (flight.rendererInfo && typeof flight.infoAutoReset === 'boolean') {
      flight.rendererInfo.autoReset = flight.infoAutoReset;
    }
    if (flight.characterState) {
      var snapshot = flight.characterState;
      var character = flight.parts.character;
      if (snapshot.headRigRotation && character.headRig) {
        character.headRig.rotation.copy(snapshot.headRigRotation);
      }
      if (typeof snapshot.squash === 'number') character.squash = snapshot.squash;
      if (typeof snapshot.spin === 'number') character.spin = snapshot.spin;
      if (typeof snapshot.jump === 'number') character.jump = snapshot.jump;
    }

    if (flight.rootOffset && flight.rootOffset.parent) {
      if (flight.root && flight.root.parent) flight.root.parent.remove(flight.root);
      flight.homeParent.add(flight.root);
      if (flight.rootHome) {
        flight.root.position.copy(flight.rootHome.position);
        flight.root.rotation.copy(flight.rootHome.rotation);
        flight.root.scale.copy(flight.rootHome.scale);
      }
      if (flight.rootOffset.parent) flight.rootOffset.parent.remove(flight.rootOffset);
      if (flight.wrapper.parent) flight.wrapper.parent.remove(flight.wrapper);
      flight.rootOffset = null;
    }
    flight.pivots.wings.forEach(restorePivot);
    restorePivot(flight.pivots.tail);
    flight.pivots.feet.forEach(restorePivot);

    if (flight.canvasHome.parent) {
      var parent = flight.canvasHome.parent;
      if (flight.canvas.parentNode !== parent) {
        if (flight.canvasHome.nextSibling && flight.canvasHome.nextSibling.parentNode === parent) {
          parent.insertBefore(flight.canvas, flight.canvasHome.nextSibling);
        } else {
          parent.appendChild(flight.canvas);
        }
      }
      flight.canvas.style.cssText = flight.canvasHome.style;
      flight.canvas.className = flight.canvasHome.className;
      if (flight.canvasHome.ariaHidden === null) flight.canvas.removeAttribute('aria-hidden');
      else flight.canvas.setAttribute('aria-hidden', flight.canvasHome.ariaHidden);
    }

    var stage = document.getElementById('pip-flight-stage');
    if (stage) {
      stage.style.visibility = 'hidden';
      stage.style.opacity = '0';
    }
    flight.rig.walkOwner = false;
    resizeDockedRig(flight.parts);
    if (typeof flight.rig.dock === 'function') flight.rig.dock();
    if (typeof flight.rig.resume === 'function') flight.rig.resume();
  }

  function abortFlight() {
    var flight = state.flight;
    if (!flight) return;
    if (flight.timeline && typeof flight.timeline.kill === 'function') flight.timeline.kill();
    if (flight.raf) window.cancelAnimationFrame(flight.raf);
    if (flight.pulseTimer) window.clearTimeout(flight.pulseTimer);
    restoreFlight(flight);
    state.flight = null;
    state.diagnostics.state = 'docked';
    if (state.active === 'pip') revealDocked(false);
  }

  function finishFlight(flight) {
    if (!flight || state.flight !== flight || activeCharacter() !== 'pip') return;
    flight.pivots.wings.forEach(function (record) { record.pivot.rotation.set(0, 0, 0); });
    if (flight.pivots.tail) flight.pivots.tail.pivot.rotation.set(0, 0, 0);
    flight.pivots.feet.forEach(function (record) { record.pivot.rotation.set(0, 0, 0); });
    flight.wrapper.rotation.set(0, 0, 0);
    flight.wrapper.scale.setScalar(1);
    restoreFlight(flight);
    if (typeof flight.parts.rig.setEmotion === 'function') flight.parts.rig.setEmotion('welcome');
    else if (flight.parts.character && typeof flight.parts.character.setEmotion === 'function') {
      flight.parts.character.setEmotion('welcome');
    }
    state.flight = null;
    state.arrivalSettled = true;
    markArrived();
    revealDocked(false);

    var portal = document.getElementById('charEntryPortal');
    if (portal) {
      portal.classList.remove('active');
      void portal.offsetWidth;
      portal.classList.add('active');
    }
    pulseLanding(document.getElementById('chat-toggle'));
    state.diagnostics.state = 'landing';
    window.setTimeout(function () {
      if (activeCharacter() !== 'pip') return;
      state.diagnostics.state = 'docked';
      showWelcomeBubble();
    }, REDUCED_MOTION ? 120 : 920);
  }

  function updateFlight(flight, progress, elapsed) {
    if (!flight || state.flight !== flight || activeCharacter() !== 'pip') return;
    var points = flight.path.points;
    var screen = bezier(points, progress);
    var world = screenToWorld(flight.parts, screen.x, screen.y, 0);
    flight.wrapper.position.copy(world);

    var landing = Math.max(0, Math.min(1, (progress - 0.72) / 0.28));
    landing = landing * landing * (3 - 2 * landing);
    var dockScale = Math.max(0.06, Math.min(0.18, flight.dockHeight / Math.max(1, window.innerHeight)));
    var flightScale = Math.max(dockScale * 1.35, Math.min(0.20, dockScale + 0.075));
    flight.wrapper.scale.setScalar(flightScale + (dockScale - flightScale) * landing);

    var bank = Math.sin(progress * Math.PI) * 0.18 * flight.path.side;
    flight.wrapper.rotation.set(-0.10 * Math.sin(progress * Math.PI), 0.20 * flight.path.side * (1 - landing), bank);

    var glide = Math.max(0, Math.min(1, (progress - 0.68) / 0.32));
    var wingAmplitude = 0.56 * (1 - glide) + 0.055 * glide;
    var phase = elapsed * 17.5;
    flight.pivots.wings.forEach(function (record, index) {
      var flap = 0.20 + Math.sin(phase + index * Math.PI) * wingAmplitude;
      record.pivot.rotation.z = record.side * flap;
      record.pivot.rotation.x = Math.sin(phase * 0.5 + index) * 0.035 * (1 - glide);
    });
    if (flight.pivots.tail) {
      flight.pivots.tail.pivot.rotation.y = Math.sin(phase * 0.55) * 0.10 * (1 - landing);
      flight.pivots.tail.pivot.rotation.z = Math.sin(phase * 0.8) * 0.035 * (1 - landing);
    }
    flight.pivots.feet.forEach(function (record) {
      record.pivot.rotation.x = 0.30 * (1 - landing);
      record.pivot.rotation.z = record.side * 0.035 * (1 - landing);
    });

    var character = flight.parts.character;
    if (character.headRig && flight.characterState.headRigRotation) {
      var headRest = flight.characterState.headRigRotation;
      character.headRig.rotation.x = headRest.x - 0.035 * (1 - landing);
      character.headRig.rotation.y = headRest.y + flight.path.side * 0.16 * (1 - landing);
      character.headRig.rotation.z = headRest.z;
    }

    var renderer = flight.parts.renderer;
    if (flight.manualRender && renderer && typeof renderer.render === 'function') {
      try {
        renderer.render(flight.parts.scene, flight.parts.camera);
      } catch (error) {
        flight.manualRender = false;
        if (window.console && window.console.warn) window.console.warn('[PipFlight] manual render failed', error);
      }
    }
    if (renderer.info && renderer.info.render) {
      var calls = renderer.info.render.calls || 0;
      state.diagnostics.drawCalls = calls;
      state.diagnostics.maxDrawCalls = Math.max(state.diagnostics.maxDrawCalls, calls);
      state.diagnostics.budgetPassed = state.diagnostics.maxDrawCalls < 25;
      state.diagnostics.frames += 1;
      state.diagnostics.state = 'flying';
      window.__pipFlightDiagnostics = state.diagnostics;
    }
  }

  function startFlight() {
    if (state.flight || activeCharacter() !== 'pip') return;
    var button = document.getElementById('chat-toggle');
    var wrap = document.getElementById('chat-toggle-wrap');
    var parts = getRigParts();
    if (!button || !wrap) return;

    var alreadyArrived = sessionHasArrived();
    if (alreadyArrived || REDUCED_MOTION || !parts || !window.THREE) {
      state.arrivalSettled = true;
      state.welcomeShown = alreadyArrived;
      markArrived();
      revealDocked(!alreadyArrived);
      return;
    }

    var canvas = parts.canvas;
    var parent = canvas.parentNode;
    var root = parts.root;
    var homeParent = root.parent;
    if (!parent || !homeParent) {
      state.arrivalSettled = true;
      markArrived();
      revealDocked(true);
      return;
    }

    setPipMode(true);
    updateFallbackBird(false);
    if (parts.character.walk) {
      parts.character.walk.locomotion = 0;
      parts.character.walk.locomotionTarget = 0;
      parts.character.walk.docked = true;
      parts.character.walkLean = 0;
      parts.character.walkYaw = 0;
      parts.character.walkAerial = 0;
    }
    if (typeof parts.rig.dock === 'function') parts.rig.dock();
    if (typeof parts.rig.resume === 'function') parts.rig.resume();
    parts.rig.walkOwner = false;

    var rootHome = {
      position: root.position.clone(),
      rotation: root.rotation.clone(),
      scale: root.scale.clone()
    };
    var characterState = {
      headRigRotation: parts.character.headRig ? parts.character.headRig.rotation.clone() : null,
      squash: parts.character.squash,
      spin: parts.character.spin,
      jump: parts.character.jump
    };

    // The adapter's outer root is the flight-owned group; the standalone Pip
    // root is bobbed by its character loop. Pause before the reversible merge,
    // then render only from the flight tick until the original meshes return.
    if (parts.rig.character) {
      root.position.set(0, 0, 0);
      root.rotation.set(0, 0, 0);
      root.scale.set(1, 1, 1);
    } else {
      root.position.x = 0;
      root.rotation.set(0, 0, 0);
      root.scale.set(1, 1, 1);
      parts.character.spin = 0;
      parts.character.jump = 0;
    }
    var pauseTarget = null;
    if (typeof parts.rig.pause === 'function') {
      parts.rig.pause();
      pauseTarget = parts.rig;
    } else if (typeof parts.character.pause === 'function') {
      parts.character.pause();
      pauseTarget = parts.character;
    }
    var optimization = optimizePipDrawCalls(parts, !!pauseTarget);
    root.updateMatrixWorld(true);
    homeParent.updateMatrixWorld(true);

    var bounds = new window.THREE.Box3().setFromObject(root);
    var centreWorld = bounds.getCenter(new window.THREE.Vector3());
    var centreLocal = homeParent.worldToLocal(centreWorld.clone());

    var wrapper = new window.THREE.Group();
    wrapper.name = 'pip-flight-screen-anchor';
    var offset = new window.THREE.Group();
    offset.name = 'pip-flight-visual-centre';
    offset.position.copy(centreLocal).negate();
    homeParent.add(wrapper);
    homeParent.remove(root);
    wrapper.add(offset);
    offset.add(root);

    var pivots = addFlightPivots(parts.character);
    var path = createFlightPath(button);
    var rect = parent.getBoundingClientRect();
    var dockHeight = Math.max(44, rect.height || button.getBoundingClientRect().height || 78);
    var shadowMap = parts.renderer.shadowMap || null;
    var shadowMapEnabled = shadowMap ? !!shadowMap.enabled : null;
    var rendererInfo = parts.renderer.info || null;
    var infoAutoReset = rendererInfo && typeof rendererInfo.autoReset === 'boolean'
      ? rendererInfo.autoReset
      : null;
    // Shadow-map passes multiply draw calls. The merged flight is very short;
    // restore the studio shadow setting as soon as Pip docks again.
    if (shadowMap) shadowMap.enabled = false;
    if (rendererInfo && typeof rendererInfo.autoReset === 'boolean') rendererInfo.autoReset = true;

    var stage = getStage();
    var canvasHome = {
      parent: parent,
      nextSibling: canvas.nextSibling,
      style: canvas.style.cssText,
      className: canvas.className,
      ariaHidden: canvas.getAttribute('aria-hidden')
    };
    stage.style.visibility = 'visible';
    stage.style.opacity = '1';
    stage.appendChild(canvas);
    canvas.style.cssText = [
      'position:absolute', 'inset:0', 'width:100%', 'height:100%',
      'max-width:none', 'max-height:none', 'border-radius:0',
      'display:block', 'pointer-events:none', 'z-index:1'
    ].join(';');
    resizeRig(parts);

    var flight = {
      parts: parts,
      rig: parts.rig,
      root: root,
      rootHome: rootHome,
      characterState: characterState,
      optimization: optimization,
      shadowMap: shadowMap,
      shadowMapEnabled: shadowMapEnabled,
      rendererInfo: rendererInfo,
      infoAutoReset: infoAutoReset,
      manualRender: !!pauseTarget,
      homeParent: homeParent,
      wrapper: wrapper,
      rootOffset: offset,
      pivots: pivots,
      canvas: canvas,
      canvasHome: canvasHome,
      path: path,
      dockHeight: dockHeight,
      restored: false,
      startTime: window.performance && window.performance.now ? window.performance.now() : Date.now(),
      timeline: null,
      raf: 0,
      pulseTimer: 0,
      resizeHandler: null
    };
    flight.resizeHandler = function () {
      resizeRig(parts);
      flight.path = createFlightPath(button);
      flight.dockHeight = Math.max(44, parent.getBoundingClientRect().height || button.getBoundingClientRect().height || 78);
    };
    window.addEventListener('resize', flight.resizeHandler, { passive: true });
    state.flight = flight;
    state.diagnostics.state = 'flying';
    state.diagnostics.frames = 0;
    state.diagnostics.maxDrawCalls = 0;
    state.diagnostics.drawCalls = 0;
    state.diagnostics.budgetPassed = null;
    window.__pipFlightDiagnostics = state.diagnostics;
    updateFlight(flight, 0, 0);

    var gsap = window.gsap;
    if (gsap && typeof gsap.timeline === 'function') {
      var progressState = { value: 0 };
      flight.timeline = gsap.timeline({ onComplete: function () { finishFlight(flight); } });
      flight.timeline.to(progressState, {
        value: 1,
        duration: 1.55,
        ease: 'power1.inOut',
        onUpdate: function () {
          var now = window.performance && window.performance.now ? window.performance.now() : Date.now();
          updateFlight(flight, progressState.value, Math.max(0, (now - flight.startTime) / 1000));
        }
      });
    } else {
      var started = flight.startTime;
      var animate = function (now) {
        if (!state.flight || state.flight !== flight) return;
        var raw = Math.max(0, Math.min(1, (now - started) / 1550));
        var eased = raw < 0.5 ? 4 * raw * raw * raw : 1 - Math.pow(-2 * raw + 2, 3) / 2;
        updateFlight(flight, eased, (now - started) / 1000);
        if (raw < 1) flight.raf = window.requestAnimationFrame(animate);
        else finishFlight(flight);
      };
      flight.raf = window.requestAnimationFrame(animate);
    }
  }

  function schedulePipArrival(delay) {
    if (state.flightTimer) window.clearTimeout(state.flightTimer);
    if (!state.booted || !state.heroDone || activeCharacter() !== 'pip') return;
    if (!HOME_PATH) {
      state.arrivalSettled = true;
      var showSubpageGreeting = !sessionHasSubpageGreeting();
      if (showSubpageGreeting) markSubpageGreeting();
      state.welcomeShown = !showSubpageGreeting;
      revealDocked(showSubpageGreeting);
      return;
    }
    if (sessionHasArrived()) {
      state.welcomeShown = true;
      state.arrivalSettled = true;
      revealDocked(false);
      return;
    }
    state.flightTimer = window.setTimeout(startFlight, Math.max(0, delay || 0));
  }

  function onHeroComplete() {
    if (state.heroDone) return;
    state.heroDone = true;
    if (activeCharacter() === 'pip') schedulePipArrival(360);
  }

  function hookHeroEntrance() {
    if (state.heroHooked || !HOME_PATH || typeof window.triggerHeroEntrance !== 'function') return;
    state.heroHooked = true;
    var original = window.triggerHeroEntrance;
    window.triggerHeroEntrance = function () {
      var alreadyTriggered = !!window._heroEntranceTriggered;
      var gsap = window.gsap;
      var originalTimeline = gsap && gsap.timeline;
      var wrappedTimeline = null;
      var captured = null;
      var result;
      if (typeof originalTimeline === 'function') {
        wrappedTimeline = function () {
          var timeline = originalTimeline.apply(this, arguments);
          if (!captured) captured = timeline;
          return timeline;
        };
        try { gsap.timeline = wrappedTimeline; } catch (error) { wrappedTimeline = null; }
      }
      try {
        result = original.apply(this, arguments);
      } finally {
        if (wrappedTimeline && gsap.timeline === wrappedTimeline) gsap.timeline = originalTimeline;
      }

      var timeline = captured || (result && typeof result.eventCallback === 'function' ? result : null);
      if (timeline && typeof timeline.eventCallback === 'function') {
        var previousComplete = timeline.eventCallback('onComplete');
        timeline.eventCallback('onComplete', function () {
          if (typeof previousComplete === 'function') previousComplete.apply(this, arguments);
          onHeroComplete();
        });
      } else if (!alreadyTriggered) {
        window.setTimeout(onHeroComplete, 2700);
      }
      return result;
    };

    if (window._heroEntranceTriggered) window.setTimeout(onHeroComplete, 3600);
  }

  function boot() {
    if (state.booted) return;
    state.booted = true;
    state.active = activeCharacter();
    setCharacterButton(state.active);

    if (!HOME_PATH) {
      state.heroDone = true;
      if (state.active === 'pip') {
        setPipMode(true);
        if (sessionHasArrived() || sessionHasSubpageGreeting()) {
          state.welcomeShown = true;
          state.arrivalSettled = true;
          revealDocked(false);
        } else {
          state.welcomeShown = false;
          state.arrivalSettled = true;
          markSubpageGreeting();
          revealDocked(true);
        }
      }
      return;
    }

    hookHeroEntrance();
    if (state.active === 'pip') setPipMode(true);
    if (window._heroEntranceTriggered && !state.heroDone) window.setTimeout(onHeroComplete, 3600);

    // Defensive fallback for a page whose preloader/GSAP script was blocked.
    window.addEventListener('load', function () {
      window.setTimeout(function () {
        if (!state.heroDone) onHeroComplete();
      }, 5200);
    }, { once: true });
  }

  window.PipFlightController = {
    get state() { return state.diagnostics.state; },
    get diagnostics() { return state.diagnostics; },
    launch: function () { state.heroDone = true; schedulePipArrival(0); },
    cancel: abortFlight
  };

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', boot, { once: true });
  else boot();
})(window, document);
