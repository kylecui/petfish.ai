/**
 * market-data.js — Shared market pack fetcher and renderer for petfish.ai website.
 * Fetches pack data from petfish-market index.json with 1h localStorage cache.
 * Falls back to static HTML (via <noscript>) when fetch fails.
 *
 * Auto-detects page type by container IDs:
 *   #market-packs         → market.html (card grid)
 *   #featured-market-packs→ index.html  (3 featured cards)
 *   #market-packs-table   → pitch.html  (table rows)
 */
(function () {
  'use strict';

  var MARKET_URL = 'https://raw.githubusercontent.com/kylecui/petfish-market/main/index.json';
  var CACHE_KEY = 'petfish_market';
  var CACHE_TTL = 3600000; // 1 hour

  /* Accent color map by alias (hex) */
  var PACK_COLORS = {
    research:       '#79c0ff',
    course:         '#58a6ff',
    deploy:         '#f0883e',
    context:        '#58a6ff',
    trust:          '#f0883e',
    calibrate:      '#a371f7',
    'petfish-style':'#f778ba',
    petfish:        '#f778ba',
    testdocs:       '#39d353',
    ppt:            '#39d353',
    reflect:        '#79c0ff',
    'fish-trail':   '#58a6ff'
  };

  /* Bilingual display names: { zh, en } */
  var PACK_NAMES = {
    research:       { zh:'鱼渊',        en:'Fish Depth' },
    course:         { zh:'鱼课',        en:'Fish Course' },
    deploy:         { zh:'鱼 Deploy',   en:'Fish Deploy' },
    context:        { zh:'鱼迹',        en:'Fish Trail' },
    'fish-trail':   { zh:'鱼迹',        en:'Fish Trail' },
    trust:          { zh:'鱼鳞',        en:'Fish Scale' },
    calibrate:      { zh:'鱼刺',        en:'Fishbone' },
    'petfish-style':{ zh:'鱼话',        en:'Fish Talk' },
    petfish:        { zh:'鱼话',        en:'Fish Talk' },
    testdocs:       { zh:'',            en:'' },
    ppt:            { zh:'演示',        en:'Slides' },
    reflect:        { zh:'鱼思',        en:'Fish Reflect' }
  };

  /* ── helpers ── */

  function esc(s) {
    var d = document.createElement('div');
    d.textContent = (s == null ? '' : String(s));
    return d.innerHTML;
  }

  function getColor(alias) {
    return PACK_COLORS[alias] || '#8b949e';
  }

  /**
   * Map hex color → CSS data-accent class name used by existing stylesheets.
   */
  function getAccentClass(alias) {
    var c = getColor(alias);
    switch (c) {
      case '#79c0ff': return 'cyan';
      case '#58a6ff': return 'blue';
      case '#f0883e': return 'orange';
      case '#a371f7': return 'purple';
      case '#f778ba': return 'pink';
      case '#39d353': return 'green';
      default:        return '';
    }
  }

  /* ── fetch with cache ── */

  /**
   * Fetch market index. Returns Promise<indexJson>.
   * Cache strategy: fresh (<1h) → network → stale cache → throw.
   */
  function fetchMarketPacks() {
    // 1) fresh localStorage cache
    try {
      var raw = localStorage.getItem(CACHE_KEY);
      if (raw) {
        var cached = JSON.parse(raw);
        if (cached.ts && (Date.now() - cached.ts) < CACHE_TTL && cached.data && cached.data.packs) {
          return Promise.resolve(cached.data);
        }
      }
    } catch (_) { /* ignore */ }

    // 2) network
    return fetch(MARKET_URL).then(function (resp) {
      if (!resp.ok) throw new Error('HTTP ' + resp.status);
      return resp.json();
    }).then(function (data) {
      try {
        localStorage.setItem(CACHE_KEY, JSON.stringify({ ts: Date.now(), data: data }));
      } catch (_) {}
      return data;
    }).catch(function (err) {
      // 3) stale cache fallback
      try {
        var stale = localStorage.getItem(CACHE_KEY);
        if (stale) {
          var d = JSON.parse(stale);
          if (d.data && d.data.packs) return d.data;
        }
      } catch (_) {}
      throw err;
    });
  }

  /* ── render helpers ── */

  /**
   * Build a pack card <div> matching existing CSS classes.
   * Used by: market.html (#market-packs) and index.html (#featured-market-packs).
   */
  function renderPackCard(pack) {
    var alias = (pack.alias && pack.alias[0]) || '';
    var color = getColor(alias);
    var accent = getAccentClass(alias);
    var skillCount = pack.skill_count || 0;
    var desc = esc(pack.description || '');

    // bilingual name line
    var names = PACK_NAMES[alias];
    var nameHTML;
    if (names && names.zh !== '') {
      nameHTML = esc(alias) + ' · <span class="copy-zh">' + esc(names.zh) + '</span><span class="copy-en">' + esc(names.en) + '</span>';
    } else {
      nameHTML = esc(alias);
    }

    var da = accent ? ' data-accent="' + accent + '"' : '';
    return '<div class="pack-card"' + da + ' style="border-color:' + color + ';">' +
      '<div class="pack-name">' + nameHTML + '</div>' +
      '<div class="pack-desc"><span class="copy-zh">' + desc + '</span><span class="copy-en">' + desc + '</span></div>' +
      '<div class="pack-meta">' + skillCount + ' skills</div>' +
      '</div>';
  }

  /**
   * Build a table row <tr> for pitch.html.
   */
  function renderPackTableRow(pack) {
    var alias = (pack.alias && pack.alias[0]) || '';
    var skillCount = pack.skill_count || 0;
    var desc = esc(pack.description || '');
    var names = PACK_NAMES[alias];

    var zhDesc, enDesc;
    if (names && names.zh !== '') {
      zhDesc = names.zh + ' — ' + desc;
      enDesc = names.en + ' — ' + desc;
    } else {
      zhDesc = enDesc = desc;
    }

    return '<tr>' +
      '<td><code>' + esc(alias) + '</code></td>' +
      '<td><span class="copy-zh">' + zhDesc + '</span><span class="copy-en">' + enDesc + '</span></td>' +
      '<td>' + skillCount + ' skill' + (skillCount !== 1 ? 's' : '') + '</td>' +
      '</tr>';
  }

  function sortPacks(packs) {
    return packs.slice().sort(function (a, b) {
      return (b.skill_count || 0) - (a.skill_count || 0);
    });
  }

  /**
   * Update all elements with data-pack-count attribute with the given number.
   */
  function updateCount(count) {
    var els = document.querySelectorAll('[data-pack-count]');
    for (var i = 0; i < els.length; i++) {
      els[i].textContent = count;
    }
  }

  /**
   * Replace container content with its sibling <noscript> fallback HTML.
   */
  function useFallback(containerId) {
    var el = document.getElementById(containerId);
    if (!el) return;
    var noscript = el.querySelector('noscript');
    if (noscript) {
      el.innerHTML = noscript.textContent;
    }
  }

  /* ── page init functions ── */

  function initMarketPage() {
    fetchMarketPacks().then(function (data) {
      var packs = sortPacks(data.packs || []);
      var html = '';
      for (var i = 0; i < packs.length; i++) {
        html += renderPackCard(packs[i]);
      }
      document.getElementById('market-packs').innerHTML = html;
      updateCount(data.pack_count || packs.length);
    }).catch(function (e) {
      console.warn('[market-data] fetch failed for market.html:', e.message);
      useFallback('market-packs');
    });
  }

  function initFeaturedPacks() {
    fetchMarketPacks().then(function (data) {
      var packs = sortPacks(data.packs || []).slice(0, 3);
      var html = '';
      for (var i = 0; i < packs.length; i++) {
        html += renderPackCard(packs[i]);
      }
      document.getElementById('featured-market-packs').innerHTML = html;
      updateCount(data.pack_count || (data.packs ? data.packs.length : 0));
    }).catch(function (e) {
      console.warn('[market-data] fetch failed for index.html featured:', e.message);
      useFallback('featured-market-packs');
    });
  }

  function initPitchTable() {
    fetchMarketPacks().then(function (data) {
      var packs = sortPacks(data.packs || []);
      var html = '';
      for (var i = 0; i < packs.length; i++) {
        html += renderPackTableRow(packs[i]);
      }
      document.getElementById('market-packs-table').innerHTML = html;
      updateCount(data.pack_count || packs.length);
    }).catch(function (e) {
      console.warn('[market-data] fetch failed for pitch.html:', e.message);
      useFallback('market-packs-table');
    });
  }

  /* ── auto-detect and init ── */

  function autoInit() {
    if (document.getElementById('market-packs'))       { initMarketPage(); }
    if (document.getElementById('featured-market-packs')) { initFeaturedPacks(); }
    if (document.getElementById('market-packs-table'))  { initPitchTable(); }
  }

  /* ── export global ── */
  window.PetfishMarket = {
    fetch:       fetchMarketPacks,
    renderCard:  renderPackCard,
    renderRow:   renderPackTableRow,
    sortPacks:   sortPacks,
    initMarket:  initMarketPage,
    initFeatured:initFeaturedPacks,
    initPitch:   initPitchTable,
    autoInit:    autoInit
  };

  /* auto-run when DOM is ready */
  if (document.readyState === 'complete' || document.readyState === 'interactive') {
    setTimeout(autoInit, 1);
  } else {
    document.addEventListener('DOMContentLoaded', autoInit);
  }
})();
