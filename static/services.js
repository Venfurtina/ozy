/* services.js – Modular service tabs + popup management */
/* global CURRENT_USER, STRINGS */
(function () {
  'use strict';

  const DEFS = {}; // populated from API
  let activeServices = [];

  // ── Bootstrap ─────────────────────────────────────────────────────────────
  async function initServices() {
    try {
      const r = await fetch('/api/user/services');
      const j = await r.json();
      if (!j.success) return;
      activeServices = j.active || [];
      j.available.forEach(s => { DEFS[s.id] = s; });
      buildTabBar();
    } catch(e) { console.error('Services init error', e); }
  }

  // ── Tab bar ───────────────────────────────────────────────────────────────
  function buildTabBar() {
    const bar = document.getElementById('serviceTabBar');
    if (!bar) return;
    bar.innerHTML = '';
    activeServices.forEach(sid => {
      const def = DEFS[sid];
      if (!def) return;
      const btn = document.createElement('button');
      btn.className = 'page-tab';
      btn.dataset.svcTab = sid;
      btn.innerHTML = `${def.icon} ${def.title}`;
      btn.addEventListener('click', () => switchToServiceTab(sid));
      bar.appendChild(btn);
    });
  }

  function switchToServiceTab(sid) {
    // Deactivate main tabs
    document.querySelectorAll('.page-tab').forEach(b => b.classList.remove('active'));
    document.querySelectorAll('.page-tab-panel').forEach(p => p.classList.remove('active'));
    // Activate this service tab btn
    const btn = document.querySelector(`[data-svc-tab="${sid}"]`);
    if (btn) btn.classList.add('active');
    // Show/create panel
    let panel = document.getElementById(`svc-panel-${sid}`);
    if (!panel) {
      panel = document.createElement('div');
      panel.id = `svc-panel-${sid}`;
      panel.className = 'page-tab-panel';
      document.getElementById('svcPanels').appendChild(panel);
      loadServicePanel(sid, panel);
    }
    panel.classList.add('active');
  }

  function openServicePanel(sid) {
    switchToServiceTab(sid);
  }

  // ── Load service panel content ─────────────────────────────────────────────
  function loadServicePanel(sid, panel) {
    if (sid === 'personal_cal') {
      // Delegate to private_calendar.js
      panel.innerHTML = `
        <div class="priv-header">
          <div style="font-size:18px;font-weight:700;flex:1;">🔒 Kişisel Takvimler</div>
          <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center;">
            <input class="priv-new-input" id="newCalName" placeholder="Yeni takvim adı…" style="width:200px;" />
            <button class="btn primary" id="createCalBtn">+ Yeni Takvim</button>
          </div>
        </div>
        <div class="priv-subtabs" id="privSubtabs">
          <span style="font-size:12px;color:var(--muted)">Henüz takvim yok.</span>
        </div>
        <div id="privPanels"></div>`;
      if (window.initPrivateCalendar) window.initPrivateCalendar();
    } else if (sid === 'rent') {
      if (window.initRent) window.initRent(panel);
    } else if (sid === 'shopping') {
      if (window.initShopping) window.initShopping(panel);
    } else if (sid === 'ppl') {
      panel.innerHTML = `
        <div style="max-width:500px;margin:40px auto;text-align:center;padding:20px;">
          <div style="font-size:48px;margin-bottom:16px;">✈️</div>
          <h2 style="font-size:22px;font-weight:800;margin-bottom:10px;">PPL(A) Lernplattform</h2>
          <p style="color:var(--muted);font-size:14px;line-height:1.6;margin-bottom:24px;">
            EASA · LBA · ECQB-konform<br>Tüm PPL(A) teorik sınav konularını kapsayan öğrenme platformu.
          </p>
          <a href="/learn" class="btn primary"
             style="display:inline-flex;align-items:center;gap:8px;padding:12px 28px;font-size:15px;font-weight:700;text-decoration:none;">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5">
              <path d="M5 12h14M12 5l7 7-7 7"/>
            </svg>
            PPL Platformuna Git
          </a>
        </div>`;
    }
  }

  // ── Services Popup ─────────────────────────────────────────────────────────
  function openServicesPopup() {
    let overlay = document.getElementById('servicesOverlay');
    if (!overlay) {
      overlay = buildServicesOverlay();
      document.body.appendChild(overlay);
    }
    renderServicesGrid();
    overlay.classList.add('open');
  }

  function closeServicesPopup() {
    const ov = document.getElementById('servicesOverlay');
    if (ov) ov.classList.remove('open');
  }

  function buildServicesOverlay() {
    const div = document.createElement('div');
    div.id = 'servicesOverlay';
    div.className = 'svc-overlay';
    div.innerHTML = `
      <div class="svc-modal">
        <div class="svc-modal-header">
          <span class="svc-modal-title">⊞ Servisler</span>
          <button class="svc-modal-close" id="svcClose">×</button>
        </div>
        <p style="padding:0 20px 4px;font-size:12px;color:var(--muted)">
          Servisi seç → profiline sekme olarak eklenir. Tekrar tıkla → kaldırılır.
        </p>
        <div class="svc-grid" id="svcGrid"></div>
      </div>`;
    div.querySelector('#svcClose').addEventListener('click', closeServicesPopup);
    div.addEventListener('click', e => { if (e.target === div) closeServicesPopup(); });
    return div;
  }

  function renderServicesGrid() {
    const grid = document.getElementById('svcGrid');
    if (!grid) return;
    grid.innerHTML = '';
    Object.values(DEFS).forEach(def => {
      const isActive = activeServices.includes(def.id);
      const card = document.createElement('div');
      card.className = 'svc-card' + (isActive ? ' active' : '');
      card.innerHTML = `
        <div class="svc-card-icon">${def.icon}</div>
        <div class="svc-card-title">${def.title}</div>
        <div class="svc-card-desc">${def.desc}</div>
        <div class="svc-card-status">${isActive ? '✓ Aktif' : 'Ekle'}</div>`;
      card.addEventListener('click', () => toggleService(def.id, isActive));
      grid.appendChild(card);
    });
  }

  async function toggleService(sid, isActive) {
    if (isActive) {
      // Confirm removal with data deletion warning
      const def = DEFS[sid];
      const ok = confirm(
        `"${def.title}" servisini kaldırmak istediğinize emin misiniz?\n\n⚠️ Bu servisinize ait tüm veriler kalıcı olarak silinecektir.\n\nDevam etmek için Tamam'a basın.`
      );
      if (!ok) return;
      try {
        const r = await fetch(`/api/user/services/${sid}`, { method: 'DELETE' });
        const j = await r.json();
        if (j.success) {
          activeServices = activeServices.filter(s => s !== sid);
          // Remove tab and panel
          const btn = document.querySelector(`[data-svc-tab="${sid}"]`);
          if (btn) btn.remove();
          const panel = document.getElementById(`svc-panel-${sid}`);
          if (panel) panel.remove();
          // Switch to main tab
          document.querySelector('.page-tab[data-tab="main"]')?.click();
        }
      } catch(e) {}
    } else {
      try {
        const r = await fetch(`/api/user/services/${sid}`, { method: 'POST' });
        const j = await r.json();
        if (j.success) {
          activeServices.push(sid);
          buildTabBar();
          closeServicesPopup();
          setTimeout(() => switchToServiceTab(sid), 100);
        }
      } catch(e) {}
    }
    renderServicesGrid();
  }

  // ── DOMContentLoaded ───────────────────────────────────────────────────────
  document.addEventListener('DOMContentLoaded', () => {
    initServices();
    const addBtn = document.getElementById('addServiceBtn');
    if (addBtn) addBtn.addEventListener('click', openServicesPopup);

    // Wire "Ana Takvim" tab back to panel-main
    const mainTabBtn = document.querySelector('[data-tab="main"]');
    if (mainTabBtn) {
      mainTabBtn.addEventListener('click', () => {
        document.querySelectorAll('.page-tab').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.page-tab-panel').forEach(p => p.classList.remove('active'));
        mainTabBtn.classList.add('active');
        const mainPanel = document.getElementById('panel-main');
        if (mainPanel) mainPanel.classList.add('active');
      });
    }
  });

  // Expose for use by other modules
  window.servicesModule = { openServicesPopup, closeServicesPopup };
})();
