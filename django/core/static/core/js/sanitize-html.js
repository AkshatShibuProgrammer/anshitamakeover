/**
 * ═══════════════════════════════════════════════════════════════════════
 * Anshita Makeover — Strict DOM sanitiser (XSS defence, audit §7.1)
 * File: django/core/static/core/js/sanitize-html.js
 * ═══════════════════════════════════════════════════════════════════════
 *
 * Zero dependencies (DOMPurify is not a project requirement). Everything that
 * is derived from AI output, user input or a URL parameter must pass through
 * `AnshitaSanitizer` before it is written with innerHTML.
 *
 * Allow-list philosophy:
 *   • only a small set of formatting tags survive;
 *   • attributes are filtered per tag;
 *   • `on*` handlers, `style`, `srcdoc`, `xlink:href` are always dropped;
 *   • href/src must be http(s), mailto, tel or a relative path;
 *   • the parser runs against an inert document so nothing executes/loads.
 */
(function (root) {
  'use strict';

  var ALLOWED_TAGS = {
    A: ['href', 'title', 'target', 'rel'],
    B: [], STRONG: [], EM: [], I: [], U: [], S: [], BR: [],
    P: ['class'], SPAN: ['class'], DIV: ['class'], SMALL: ['class'],
    UL: ['class'], OL: ['class'], LI: ['class'],
    TABLE: ['class'], THEAD: [], TBODY: [], TR: [], TH: [], TD: [],
    CODE: [], PRE: []
  };

  var ALLOWED_CLASSES = {
    wave: 1, 'csb-tag': 1, 'csb-text': 1, 'msg-table-wrap': 1, 'msg-table': 1,
    'cc-log-msg': 1, user: 1, bot: 1, 'cb-code': 1, 'cb-badge': 1
  };

  var SAFE_URL = /^(?:https?:|mailto:|tel:|\/|#|\?|\.\/|\.\.\/)/i;
  var BAD_URL = /^\s*(?:javascript|vbscript|data|file|blob):/i;

  function escapeHtml(value) {
    return String(value === undefined || value === null ? '' : value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function isSafeUrl(url) {
    if (!url) return false;
    var trimmed = String(url).trim();
    if (!trimmed) return false;
    // Strip control/zero-width characters used to smuggle `java\nscript:`.
    trimmed = trimmed.replace(/[\u0000-\u001f\u200b-\u200f\u202a-\u202e\ufeff]/g, '');
    if (BAD_URL.test(trimmed)) return false;
    return SAFE_URL.test(trimmed);
  }

  function cleanClassList(value) {
    var kept = String(value || '').split(/\s+/).filter(function (cls) {
      return cls && ALLOWED_CLASSES[cls];
    });
    return kept.join(' ');
  }

  function sanitizeNode(node) {
    // Depth-first: sanitise children, then decide the node's own fate.
    var child = node.firstChild;
    while (child) {
      var next = child.nextSibling;
      if (child.nodeType === 1) sanitizeNode(child);
      child = next;
    }

    if (node.nodeType === 8) { // comment
      node.parentNode && node.parentNode.removeChild(node);
      return;
    }
    if (node.nodeType !== 1) return;

    var tag = node.tagName ? node.tagName.toUpperCase() : '';
    if (!ALLOWED_TAGS[tag]) {
      // Unknown tag: keep its (already sanitised) text content, drop the tag.
      var parent = node.parentNode;
      if (!parent) return;
      while (node.firstChild) parent.insertBefore(node.firstChild, node);
      parent.removeChild(node);
      return;
    }

    var allowedAttrs = ALLOWED_TAGS[tag];
    var attrs = Array.prototype.slice.call(node.attributes || []);
    attrs.forEach(function (attr) {
      var name = attr.name.toLowerCase();
      if (allowedAttrs.indexOf(name) === -1) {
        node.removeAttribute(attr.name);
        return;
      }
      if (name === 'class') {
        var cleaned = cleanClassList(attr.value);
        if (cleaned) node.setAttribute('class', cleaned);
        else node.removeAttribute('class');
        return;
      }
      if (name === 'href' || name === 'src') {
        if (!isSafeUrl(attr.value)) node.removeAttribute(attr.name);
      }
    });

    if (tag === 'A') {
      node.setAttribute('rel', 'noopener noreferrer nofollow');
      node.setAttribute('target', '_blank');
    }
  }

  function sanitize(html) {
    if (html === undefined || html === null) return '';
    if (typeof html !== 'string') html = String(html);
    if (!html) return '';
    if (typeof document === 'undefined') return escapeHtml(html); // non-browser

    var doc = document.implementation.createHTMLDocument('sanitize');
    // <template> parsing keeps scripts inert even in old WebKit builds.
    var holder = doc.createElement('div');
    holder.innerHTML = html;
    // Kill never-allowed containers outright with their content.
    ['script', 'style', 'iframe', 'object', 'embed', 'form', 'input',
     'link', 'meta', 'base', 'svg', 'math', 'video', 'audio', 'source'].forEach(function (tag) {
      var nodes = holder.getElementsByTagName(tag);
      while (nodes.length) {
        var n = nodes[0];
        n.parentNode && n.parentNode.removeChild(n);
      }
    });
    sanitizeNode(holder);
    return holder.innerHTML;
  }

  function setText(el, text) {
    if (!el) return;
    el.textContent = text === undefined || text === null ? '' : String(text);
  }

  function setHtml(el, html) {
    if (!el) return;
    el.innerHTML = sanitize(html);
  }

  root.AnshitaSanitizer = {
    escapeHtml: escapeHtml,
    sanitize: sanitize,
    setText: setText,
    setHtml: setHtml,
    isSafeUrl: isSafeUrl,
    ALLOWED_TAGS: ALLOWED_TAGS
  };

  if (typeof module === 'object' && module.exports) {
    module.exports = root.AnshitaSanitizer;
  }
})(typeof self !== 'undefined' ? self : this);
