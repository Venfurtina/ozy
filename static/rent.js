/* rent.js – v4: visual redesign, card layout, "Ödendi" CTA */
(function () {
  'use strict';

  let rentPanel    = null;
  let properties   = [];
  let selectedPid  = null;
  let selectedYear = new Date().getFullYear();

  window.initRent = function(panel) {
    rentPanel = panel;
    injectStyles();
    renderShell();
    loadAll();
  };

  function esc(s) { return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function $q(s)  { return rentPanel.querySelector(s); }
  function fmt(n) { return Number(n||0).toLocaleString('tr-TR'); }

  // ── Styles ────────────────────────────────────────────────────────────────
  function injectStyles() {
    if (document.getElementById('rent-styles')) return;
    const s = document.createElement('style');
    s.id = 'rent-styles';
    s.textContent = `
      .rent-root { max-width:1000px; margin:0 auto; }

      /* ── Stat bar ── */
      .rent-stats { display:grid; grid-template-columns:repeat(4,1fr); gap:10px; margin-bottom:24px; }
      @media(max-width:600px){ .rent-stats { grid-template-columns:repeat(2,1fr); } }
      .rent-stat-card {
        background:var(--surface2); border:1px solid var(--border); border-radius:14px;
        padding:14px 16px; display:flex; flex-direction:column; gap:3px;
      }
      .rent-stat-val { font-size:20px; font-weight:800; line-height:1; }
      .rent-stat-lbl { font-size:10px; color:var(--muted); text-transform:uppercase;
                       letter-spacing:.6px; font-weight:600; }

      /* ── Notification banner ── */
      .rent-alert { display:none; align-items:center; gap:10px; padding:10px 14px;
        border-radius:10px; margin-bottom:16px; font-size:12px; font-weight:600;
        background:rgba(248,113,113,.08); border:1px solid rgba(248,113,113,.25); color:#fca5a5; }
      .rent-alert.show { display:flex; }

      /* ── Layout ── */
      .rent-layout { display:grid; grid-template-columns:300px 1fr; gap:20px; }
      @media(max-width:700px){ .rent-layout { grid-template-columns:1fr; } }

      /* ── Property cards ── */
      .rent-prop-list { display:flex; flex-direction:column; gap:8px; }
      .rent-prop-card {
        border:1.5px solid var(--border); border-radius:14px;
        overflow:hidden; cursor:pointer; transition:all .18s;
        background:var(--surface2);
      }
      .rent-prop-card:hover  { border-color:rgba(255,255,255,.25); transform:translateX(2px); }
      .rent-prop-card.active { border-color:var(--brand); background:rgba(26,107,255,.07); }
      .rent-prop-card-top { display:flex; align-items:stretch; }
      .rent-prop-stripe { width:5px; flex-shrink:0; }
      .rent-prop-body { flex:1; padding:12px 14px; min-width:0; }
      .rent-prop-name { font-size:14px; font-weight:800; margin-bottom:2px;
        overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
      .rent-prop-addr { font-size:11px; color:var(--muted); margin-bottom:6px; }
      .rent-prop-tenant { font-size:11px; color:var(--muted);
        display:flex; align-items:center; gap:5px; margin-bottom:4px; }
      .rent-prop-foot { display:flex; align-items:center; justify-content:space-between;
        gap:6px; flex-wrap:wrap; }
      .rent-chip { font-size:10px; font-weight:700; padding:2px 8px;
        border-radius:8px; background:rgba(255,255,255,.07);
        border:1px solid rgba(255,255,255,.1); }
      .rent-chip.green { background:rgba(52,211,153,.1); border-color:rgba(52,211,153,.2); color:#34d399; }
      .rent-chip.red   { background:rgba(248,113,113,.1); border-color:rgba(248,113,113,.2); color:#f87171; }
      .rent-chip.amber { background:rgba(251,191,36,.1);  border-color:rgba(251,191,36,.2);  color:#fbbf24; }
      .rent-prop-actions { display:flex; gap:4px; margin-top:8px; }

      /* ── Pay panel ── */
      .rent-pay-header { display:flex; align-items:center; flex-wrap:wrap; gap:10px;
        margin-bottom:18px; padding-bottom:16px; border-bottom:1px solid var(--border); }
      .rent-pay-mini-stats { display:grid; grid-template-columns:repeat(3,1fr);
        gap:8px; margin-bottom:18px; }
      .rent-mini { border-radius:10px; padding:10px 12px; }
      .rent-mini-val { font-size:15px; font-weight:800; line-height:1; margin-bottom:2px; }
      .rent-mini-lbl { font-size:9px; text-transform:uppercase; letter-spacing:.5px;
        font-weight:600; color:var(--muted); }

      /* ── Timeline rows ── */
      .rent-timeline { display:flex; flex-direction:column; gap:6px; }
      .pay-row {
        display:grid;
        grid-template-columns:12px 1fr auto auto;
        align-items:center; gap:12px;
        padding:12px 14px;
        border-radius:12px; border:1px solid var(--border);
        background:var(--surface2); transition:background .15s;
      }
      .pay-row.paid    { background:rgba(52,211,153,.04); border-color:rgba(52,211,153,.15); }
      .pay-row.overdue { background:rgba(248,113,113,.04); border-color:rgba(248,113,113,.15); }
      .pay-dot { width:10px; height:10px; border-radius:50%; flex-shrink:0; }
      .pay-dot.paid    { background:#34d399; box-shadow:0 0 6px #34d39966; }
      .pay-dot.overdue { background:#f87171; box-shadow:0 0 6px #f8717166; }
      .pay-dot.pending { background:#fbbf24; }
      .pay-date { font-size:13px; font-weight:700; }
      .pay-sub  { font-size:11px; color:var(--muted); margin-top:1px; }
      .pay-badge { font-size:10px; font-weight:700; padding:3px 10px;
        border-radius:20px; white-space:nowrap; }
      .pay-badge.paid    { background:#064e3b; color:#34d399; }
      .pay-badge.overdue { background:#450a0a; color:#f87171; }
      .pay-badge.pending { background:#78350f; color:#fbbf24; }

      /* "Ödendi" CTA button — prominent green */
      .btn-paid {
        font-size:12px; font-weight:700; padding:6px 14px;
        border-radius:20px; border:none; cursor:pointer;
        background:linear-gradient(135deg,#059669,#10b981);
        color:#fff; box-shadow:0 2px 8px rgba(16,185,129,.35);
        transition:all .15s; white-space:nowrap;
      }
      .btn-paid:hover { transform:scale(1.05); box-shadow:0 4px 14px rgba(16,185,129,.5); }
      .btn-paid:active { transform:scale(.97); }
      .btn-del-pay { font-size:13px; padding:4px 7px; border-radius:8px;
        border:1px solid var(--border); background:transparent;
        color:var(--muted); cursor:pointer; transition:all .15s; }
      .btn-del-pay:hover { background:rgba(239,68,68,.1); border-color:#ef4444; color:#ef4444; }

      /* ── Modals ── */
      .rent-modal-bg { display:none; position:fixed; inset:0; background:rgba(0,0,0,.75);
        backdrop-filter:blur(8px); z-index:9000; align-items:center; justify-content:center;
        padding:16px; }
      .rent-modal-bg.open { display:flex; }
      .rent-modal-box { background:var(--surface); border:1px solid rgba(255,255,255,.12);
        border-radius:18px; padding:26px; width:100%; max-width:440px;
        box-shadow:0 24px 64px rgba(0,0,0,.7); }
      .rent-modal-title { font-size:17px; font-weight:800; margin-bottom:20px; }
      .rent-field-lbl { font-size:11px; color:var(--muted); margin-bottom:5px;
        font-weight:600; text-transform:uppercase; letter-spacing:.4px; display:block; }
      .rent-field { display:block; width:100%; margin-bottom:14px; }
      .rent-grid-2 { display:grid; grid-template-columns:1fr 1fr; gap:12px; margin-bottom:14px; }
      .rent-modal-footer { display:flex; gap:8px; justify-content:flex-end; margin-top:6px; }

      /* Empty state */
      .rent-empty { text-align:center; padding:40px 20px; color:var(--muted); }
      .rent-empty-icon { font-size:42px; margin-bottom:12px; }
    `;
    document.head.appendChild(s);
  }

  // ── Shell ─────────────────────────────────────────────────────────────────
  function renderShell() {
    rentPanel.innerHTML = `
      <div class="rent-root">

        <!-- Header -->
        <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;
                    gap:10px;margin-bottom:20px;">
          <div style="font-size:19px;font-weight:800;">🏠 Kira Takibi</div>
          <button class="btn primary" id="rentAddBtn" style="font-size:13px;padding:7px 18px;">
            + Daire Ekle
          </button>
        </div>

        <!-- Alert -->
        <div class="rent-alert" id="rentAlert">
          <span style="font-size:18px;">⚠️</span>
          <span id="rentAlertTxt"></span>
        </div>

        <!-- Stat bar -->
        <div class="rent-stats">
          <div class="rent-stat-card">
            <div class="rent-stat-val" id="sSumIncome">—</div>
            <div class="rent-stat-lbl">Aylık Toplam</div>
          </div>
          <div class="rent-stat-card">
            <div class="rent-stat-val" id="sPropCount">—</div>
            <div class="rent-stat-lbl">Daire</div>
          </div>
          <div class="rent-stat-card">
            <div class="rent-stat-val" id="sPaid" style="color:#34d399;">—</div>
            <div class="rent-stat-lbl">Tahsil (Yıl)</div>
          </div>
          <div class="rent-stat-card">
            <div class="rent-stat-val" id="sOverdue" style="color:#f87171;">—</div>
            <div class="rent-stat-lbl">Gecikmiş</div>
          </div>
        </div>

        <!-- Main layout -->
        <div class="rent-layout">
          <div>
            <div style="font-size:10px;font-weight:700;color:var(--muted);
                        text-transform:uppercase;letter-spacing:.6px;margin-bottom:10px;">
              Dairelerim
            </div>
            <div class="rent-prop-list" id="rentPropList"></div>
          </div>
          <div id="rentPayPanel">
            <div class="rent-empty">
              <div class="rent-empty-icon">🏘️</div>
              <div>Sol taraftan bir daire seçin</div>
            </div>
          </div>
        </div>
      </div>

      <!-- Property modal -->
      <div class="rent-modal-bg" id="propModal">
        <div class="rent-modal-box">
          <div class="rent-modal-title" id="propModalTitle">Daire Ekle</div>
          <label class="rent-field-lbl">Daire Adı *</label>
          <input id="rpName" class="priv-new-input rent-field" placeholder="örn: Bodrum Daire 1">
          <label class="rent-field-lbl">Adres</label>
          <input id="rpAddress" class="priv-new-input rent-field" placeholder="Cadde, Mahalle…">
          <div class="rent-grid-2">
            <div>
              <label class="rent-field-lbl">Kiracı Adı</label>
              <input id="rpTenant" class="priv-new-input" style="width:100%;" placeholder="Ad Soyad">
            </div>
            <div>
              <label class="rent-field-lbl">Kiracı Telefon</label>
              <input id="rpPhone" class="priv-new-input" style="width:100%;" placeholder="05xx…">
            </div>
          </div>
          <div class="rent-grid-2">
            <div>
              <label class="rent-field-lbl">Aylık Kira (₺) *</label>
              <input id="rpRent" class="priv-new-input" type="number" style="width:100%;">
            </div>
            <div>
              <label class="rent-field-lbl">Ödeme Günü</label>
              <input id="rpDay"  class="priv-new-input" type="number" min="1" max="31"
                     style="width:100%;" value="1">
            </div>
          </div>
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:14px;">
            <label class="rent-field-lbl" style="margin:0;">Renk</label>
            <input id="rpColor" type="color" value="#3b82f6"
              style="height:36px;width:52px;border-radius:8px;border:1px solid var(--border);cursor:pointer;">
          </div>
          <label class="rent-field-lbl">Notlar</label>
          <textarea id="rpNotes" class="priv-new-input rent-field" rows="2"
            style="resize:vertical;font-family:inherit;"
            placeholder="Sözleşme bitiş tarihi, tesisat, diğer notlar…"></textarea>
          <div class="rent-modal-footer">
            <button class="btn" id="propModalCancel">İptal</button>
            <button class="btn primary" id="propModalSave">Kaydet</button>
          </div>
        </div>
      </div>

      <!-- Payment modal -->
      <div class="rent-modal-bg" id="payModal">
        <div class="rent-modal-box">
          <div class="rent-modal-title">Ödeme Ekle</div>
          <div class="rent-grid-2">
            <div>
              <label class="rent-field-lbl">Vade Tarihi *</label>
              <input id="pmDue" class="priv-new-input" type="date" style="width:100%;">
            </div>
            <div>
              <label class="rent-field-lbl">Tutar (₺) *</label>
              <input id="pmAmt" class="priv-new-input" type="number" style="width:100%;">
            </div>
          </div>
          <label class="rent-field-lbl">Not (opsiyonel)</label>
          <input id="pmNote" class="priv-new-input rent-field" placeholder="Opsiyonel not">
          <div class="rent-modal-footer">
            <button class="btn" id="payModalCancel">İptal</button>
            <button class="btn primary" id="payModalSave">Ekle</button>
          </div>
        </div>
      </div>`;

    $q('#rentAddBtn').addEventListener('click', () => openPropModal());
    $q('#propModalCancel').addEventListener('click', closePropModal);
    $q('#propModalSave').addEventListener('click', saveProp);
    $q('#payModalCancel').addEventListener('click', closePayModal);
    $q('#payModalSave').addEventListener('click', savePayment);

    // Close on backdrop click
    ['propModal','payModal'].forEach(id => {
      rentPanel.querySelector('#'+id).addEventListener('click', e => {
        if (e.target.id === id) rentPanel.querySelector('#'+id).classList.remove('open');
      });
    });
  }

  // ── Data ──────────────────────────────────────────────────────────────────
  async function loadAll() {
    await loadProperties();
    loadNotifications();
  }

  async function loadProperties() {
    try {
      const r = await fetch('/api/rent/properties');
      const j = await r.json();
      properties = j.success ? j.properties : [];
      renderStats();
      renderPropList();
      if (selectedPid && properties.find(p=>p.id===selectedPid)) loadPayments(selectedPid);
    } catch(e){}
  }

  async function loadNotifications() {
    try {
      const r = await fetch('/api/rent/notifications');
      const j = await r.json();
      if (j.success && j.items && j.items.length) {
        const today = new Date().toISOString().slice(0,10);
        const late  = j.items.filter(i => i.due_date <= today);
        $q('#rentAlertTxt').textContent =
          `${j.items.length} yaklaşan/gecikmiş ödeme` +
          (late.length ? ` · ${late.length} vadesi geçmiş!` : '');
        $q('#rentAlert').classList.add('show');
      }
    } catch(e){}
  }

  // ── Stats ─────────────────────────────────────────────────────────────────
  function renderStats() {
    const total = properties.reduce((s,p)=>s+(p.monthly_rent||0),0);
    $q('#sSumIncome').textContent = '₺'+fmt(total);
    $q('#sPropCount').textContent = properties.length;
    updateYearStats();
  }

  async function updateYearStats() {
    let paid=0, late=0;
    const today = new Date().toISOString().slice(0,10);
    try {
      await Promise.all(properties.map(async p => {
        const r = await fetch(`/api/rent/property/${p.id}/payments?year=${selectedYear}`);
        const j = await r.json();
        if (!j.success) return;
        j.payments.forEach(pm => {
          if (pm.status==='paid') paid += pm.amount;
          else if (pm.due_date < today) late++;
        });
      }));
    } catch(e){}
    $q('#sPaid').textContent    = '₺'+fmt(paid);
    $q('#sOverdue').textContent = late || '—';
  }

  // ── Property list ─────────────────────────────────────────────────────────
  function renderPropList() {
    const el = $q('#rentPropList');
    if (!properties.length) {
      el.innerHTML = `<div class="rent-empty" style="padding:30px 10px;">
        <div class="rent-empty-icon" style="font-size:36px;">🏘️</div>
        <div style="font-size:13px;">Henüz daire yok.<br>Yukarıdan ekleyin.</div>
      </div>`;
      return;
    }
    el.innerHTML = '';
    properties.forEach(p => {
      const isActive = p.id === selectedPid;
      const card = document.createElement('div');
      card.className = 'rent-prop-card' + (isActive ? ' active' : '');
      card.dataset.pid = p.id;
      card.innerHTML = `
        <div class="rent-prop-card-top">
          <div class="rent-prop-stripe" style="background:${esc(p.color||'#3b82f6')};"></div>
          <div class="rent-prop-body">
            <div class="rent-prop-name">${esc(p.name)}</div>
            ${p.address ? `<div class="rent-prop-addr">📍 ${esc(p.address)}</div>` :
              '<div class="rent-prop-addr">Adres belirtilmemiş</div>'}
            ${p.tenant_name ? `
              <div class="rent-prop-tenant">
                <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                  <circle cx="12" cy="7" r="4"/>
                </svg>
                ${esc(p.tenant_name)}${p.tenant_phone?` · ${esc(p.tenant_phone)}`:''}
              </div>` : ''}
            <div class="rent-prop-foot">
              <span class="rent-chip">₺${fmt(p.monthly_rent)}/ay</span>
              <span class="rent-chip">Her ayın ${p.payment_day}. günü</span>
            </div>
            <div class="rent-prop-actions">
              <button class="btn" data-edit="${p.id}"
                style="font-size:11px;padding:3px 10px;">✎ Düzenle</button>
              <button class="btn" data-del="${p.id}"
                style="font-size:11px;padding:3px 10px;color:var(--muted);">✕ Sil</button>
            </div>
          </div>
        </div>`;

      card.addEventListener('click', e => {
        if (e.target.closest('[data-edit],[data-del]')) return;
        selectProp(p.id);
      });
      card.querySelector('[data-edit]').addEventListener('click', e => {
        e.stopPropagation(); openPropModal(p.id);
      });
      card.querySelector('[data-del]').addEventListener('click', async e => {
        e.stopPropagation();
        if (!confirm('Bu daire ve tüm ödemeler silinsin mi?')) return;
        await fetch(`/api/rent/property/${p.id}`, {method:'DELETE'});
        if (selectedPid===p.id) { selectedPid=null; showEmptyPay(); }
        loadProperties();
      });
      el.appendChild(card);
    });
  }

  function selectProp(pid) {
    selectedPid = pid;
    renderPropList();
    loadPayments(pid);
  }

  function showEmptyPay() {
    $q('#rentPayPanel').innerHTML = `<div class="rent-empty">
      <div class="rent-empty-icon">🏠</div><div>Sol taraftan bir daire seçin</div></div>`;
  }

  // ── Payments ─────────────────────────────────────────────────────────────
  async function loadPayments(pid) {
    const prop = properties.find(p=>p.id===pid);
    if (!prop) return;
    try {
      const r = await fetch(`/api/rent/property/${pid}/payments?year=${selectedYear}`);
      const j = await r.json();
      renderPayPanel(prop, j.success ? j.payments : []);
    } catch(e){}
  }

  function renderPayPanel(prop, payments) {
    const panel   = $q('#rentPayPanel');
    const today   = new Date().toISOString().slice(0,10);
    const MONTHS  = ['Oca','Şub','Mar','Nis','May','Haz','Tem','Ağu','Eyl','Eki','Kas','Ara'];

    const paidSum  = payments.filter(p=>p.status==='paid').reduce((s,p)=>s+p.amount,0);
    const pendSum  = payments.filter(p=>p.status!=='paid').reduce((s,p)=>s+p.amount,0);
    const lateN    = payments.filter(p=>p.status!=='paid' && p.due_date<today).length;

    panel.innerHTML = `
      <!-- Property header card -->
      <div style="border:1.5px solid var(--border);border-radius:14px;
                  overflow:hidden;margin-bottom:18px;">
        <div style="height:5px;background:${esc(prop.color||'#3b82f6')};"></div>
        <div style="padding:16px 18px;">
          <div style="display:flex;align-items:flex-start;justify-content:space-between;gap:10px;">
            <div>
              <div style="font-size:18px;font-weight:800;margin-bottom:3px;">${esc(prop.name)}</div>
              ${prop.address?`<div style="font-size:12px;color:var(--muted);">📍 ${esc(prop.address)}</div>`:''}
              ${prop.tenant_name?`<div style="font-size:12px;color:var(--muted);margin-top:2px;">👤 ${esc(prop.tenant_name)}${prop.tenant_phone?' · '+esc(prop.tenant_phone):''}</div>`:''}
            </div>
            <div style="text-align:right;flex-shrink:0;">
              <div style="font-size:20px;font-weight:800;color:var(--brand);">₺${fmt(prop.monthly_rent)}</div>
              <div style="font-size:10px;color:var(--muted);">/ ay</div>
            </div>
          </div>
          ${prop.notes?`<div style="margin-top:10px;font-size:12px;color:var(--muted);
            background:rgba(255,255,255,.04);border-radius:8px;padding:8px 10px;">
            📝 ${esc(prop.notes)}</div>`:''}
        </div>
      </div>

      <!-- Mini stats -->
      <div class="rent-pay-mini-stats">
        <div class="rent-mini" style="background:rgba(52,211,153,.07);border:1px solid rgba(52,211,153,.18);">
          <div class="rent-mini-val" style="color:#34d399;">₺${fmt(paidSum)}</div>
          <div class="rent-mini-lbl">${selectedYear} Tahsil</div>
        </div>
        <div class="rent-mini" style="background:rgba(251,191,36,.07);border:1px solid rgba(251,191,36,.18);">
          <div class="rent-mini-val" style="color:#fbbf24;">₺${fmt(pendSum)}</div>
          <div class="rent-mini-lbl">Bekleyen</div>
        </div>
        <div class="rent-mini" style="background:${lateN?'rgba(248,113,113,.07)':'rgba(0,0,0,.08)'};
          border:1px solid ${lateN?'rgba(248,113,113,.18)':'var(--border)'};">
          <div class="rent-mini-val" style="color:${lateN?'#f87171':'var(--muted)'};">${lateN||'—'}</div>
          <div class="rent-mini-lbl">Gecikmiş</div>
        </div>
      </div>

      <!-- Year nav + actions -->
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:16px;flex-wrap:wrap;">
        <button class="btn" id="yearPrev" style="padding:5px 10px;">◀</button>
        <span style="font-weight:800;font-size:15px;min-width:44px;text-align:center;">${selectedYear}</span>
        <button class="btn" id="yearNext" style="padding:5px 10px;">▶</button>
        <div style="margin-left:auto;display:flex;gap:6px;">
          <button class="btn" id="genBtn" style="font-size:12px;padding:5px 13px;"
            title="Bu yıl için 12 aylık ödemeleri otomatik oluştur">
            📅 Otomatik Oluştur
          </button>
          <button class="btn primary" id="addPayBtn" style="font-size:12px;padding:5px 13px;">
            + Ödeme Ekle
          </button>
        </div>
      </div>

      <!-- Timeline -->
      <div class="rent-timeline" id="payTimeline">
        ${!payments.length
          ? `<div class="rent-empty" style="padding:30px 0;">
              <div class="rent-empty-icon" style="font-size:32px;">📋</div>
              <div>Bu yıl için kayıt yok.<br>
                <small style="font-size:11px;">Otomatik Oluştur ile 12 aylık ödeme ekleyebilirsiniz.</small>
              </div>
            </div>`
          : payments.map(p => {
              const isPaid    = p.status === 'paid';
              const isOverdue = !isPaid && p.due_date < today;
              const dotCls    = isPaid?'paid':isOverdue?'overdue':'pending';
              const rowCls    = isPaid?'paid':isOverdue?'overdue':'';
              const parts     = p.due_date.split('-');
              const label     = (MONTHS[parseInt(parts[1])-1]||'') + ' ' + parts[0];

              return `<div class="pay-row ${rowCls}">
                <div class="pay-dot ${dotCls}"></div>
                <div>
                  <div class="pay-date">${label}
                    ${isOverdue?`<span style="font-size:10px;color:#f87171;font-weight:700;
                      margin-left:6px;"> VADESİ GEÇTİ</span>`:''}
                  </div>
                  <div class="pay-sub">
                    ₺${fmt(p.amount)}
                    ${p.note?` · ${esc(p.note)}`:''}
                    ${isPaid&&p.paid_date?`<span style="color:#34d399;margin-left:4px;">· Ödendi: ${p.paid_date}</span>`:''}
                  </div>
                </div>
                ${isPaid
                  ? `<span class="pay-badge paid">✓ Ödendi</span>`
                  : `<button class="btn-paid"
                       data-mark="${p.id}" data-pid="${prop.id}"
                       data-amount="${p.amount}" data-due="${esc(p.due_date)}"
                       data-note="${esc(p.note||'')}">
                       ✓ Ödendi
                     </button>`}
                <button class="btn-del-pay" data-delpay="${p.id}" data-pid="${prop.id}"
                  title="Sil">✕</button>
              </div>`;
            }).join('')}
      </div>`;

    // Nav
    $q('#yearPrev').addEventListener('click', () => { selectedYear--; loadPayments(prop.id); });
    $q('#yearNext').addEventListener('click', () => { selectedYear++; loadPayments(prop.id); });

    // Auto-generate
    $q('#genBtn').addEventListener('click', async () => {
      if (!confirm(`${selectedYear} için 12 aylık ödeme kayıtları oluşturulsun mu?`)) return;
      const r = await fetch(`/api/rent/property/${prop.id}/generate_payments`, {
        method:'POST', headers:{'Content-Type':'application/json'},
        body:JSON.stringify({months:12, from_date:`${selectedYear}-01-01`})
      });
      const j = await r.json();
      if (j.success) { loadPayments(prop.id); updateYearStats(); }
    });

    // Add payment
    $q('#addPayBtn').addEventListener('click', () => {
      $q('#pmDue').value  = '';
      $q('#pmAmt').value  = prop.monthly_rent || '';
      $q('#pmNote').value = '';
      openPayModal(prop.id);
    });

    // Mark as Ödendi — prominent green CTA
    panel.querySelectorAll('[data-mark]').forEach(btn => {
      btn.addEventListener('click', async () => {
        const pmid    = parseInt(btn.dataset.mark);
        const pid     = parseInt(btn.dataset.pid);
        const amount  = parseFloat(btn.dataset.amount)||0;
        const dueDate = btn.dataset.due||'';
        const note    = btn.dataset.note||'';
        const today2  = new Date().toISOString().slice(0,10);
        const paidDate = prompt('Ödeme tarihi (YYYY-MM-DD):', today2);
        if (!paidDate) return;
        await fetch(`/api/rent/payment/${pmid}`, {
          method:'PUT', headers:{'Content-Type':'application/json'},
          body:JSON.stringify({amount, due_date:dueDate, paid_date:paidDate, status:'paid', note})
        });
        loadPayments(pid);
        updateYearStats();
      });
    });

    // Delete payment
    panel.querySelectorAll('[data-delpay]').forEach(btn => {
      btn.addEventListener('click', async () => {
        if (!confirm('Bu ödeme silinsin mi?')) return;
        await fetch(`/api/rent/payment/${parseInt(btn.dataset.delpay)}`, {method:'DELETE'});
        loadPayments(parseInt(btn.dataset.pid));
        updateYearStats();
      });
    });
  }

  // ── Property modal ────────────────────────────────────────────────────────
  let editPid = null;
  function openPropModal(pid) {
    editPid = pid || null;
    $q('#propModalTitle').textContent = pid ? 'Daireyi Düzenle' : 'Daire Ekle';
    if (pid) {
      const p = properties.find(x=>x.id===pid)||{};
      $q('#rpName').value    = p.name||'';
      $q('#rpAddress').value = p.address||'';
      $q('#rpTenant').value  = p.tenant_name||'';
      $q('#rpPhone').value   = p.tenant_phone||'';
      $q('#rpRent').value    = p.monthly_rent||'';
      $q('#rpDay').value     = p.payment_day||1;
      $q('#rpColor').value   = p.color||'#3b82f6';
      $q('#rpNotes').value   = p.notes||'';
    } else {
      ['rpName','rpAddress','rpTenant','rpPhone','rpRent','rpNotes'].forEach(id=>$q('#'+id).value='');
      $q('#rpDay').value='1'; $q('#rpColor').value='#3b82f6';
    }
    $q('#propModal').classList.add('open');
  }
  function closePropModal() { $q('#propModal').classList.remove('open'); }
  async function saveProp() {
    const data = {
      name: $q('#rpName').value.trim(), address:$q('#rpAddress').value.trim(),
      tenant_name:$q('#rpTenant').value.trim(), tenant_phone:$q('#rpPhone').value.trim(),
      monthly_rent:parseFloat($q('#rpRent').value)||0,
      payment_day:parseInt($q('#rpDay').value)||1,
      color:$q('#rpColor').value, notes:$q('#rpNotes').value.trim()
    };
    if (!data.name) return alert('Daire adı zorunlu.');
    await fetch(editPid?`/api/rent/property/${editPid}`:'/api/rent/property', {
      method:editPid?'PUT':'POST',
      headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)
    });
    closePropModal();
    await loadProperties();
    if (editPid) loadPayments(editPid);
  }

  // ── Payment modal ─────────────────────────────────────────────────────────
  let payPropId = null;
  function openPayModal(pid) { payPropId=pid; $q('#payModal').classList.add('open'); }
  function closePayModal()   { $q('#payModal').classList.remove('open'); }
  async function savePayment() {
    const due = $q('#pmDue').value;
    const amt = parseFloat($q('#pmAmt').value);
    if (!due||!amt) return alert('Tarih ve tutar zorunlu.');
    await fetch('/api/rent/payment', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({property_id:payPropId, amount:amt, due_date:due, note:$q('#pmNote').value})
    });
    closePayModal();
    loadPayments(payPropId);
    updateYearStats();
  }
})();
