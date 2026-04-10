/* shopping.js – v4 Bring-style card grid */
/* global CURRENT_USER, USERS, ShopEmoji */
(function () {
  'use strict';

  let shopPanel   = null;
  let lists       = [];
  let activeList  = null;
  let pollTimer   = null;
  let itemHistory = [];

  window.initShopping = function(panel) {
    shopPanel = panel;
    injectStyles();
    renderShell();
    loadLists();
    loadHistory();
  };

  function esc(s) { return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function $q(s)  { return shopPanel.querySelector(s); }

  // ── Styles ────────────────────────────────────────────────────────────────
  function injectStyles() {
    if (document.getElementById('shop-styles')) return;
    const s = document.createElement('style');
    s.id = 'shop-styles';
    s.textContent = `
      .shop-root { max-width:980px; margin:0 auto; }
      .shop-split { display:grid; grid-template-columns:200px 1fr; gap:20px; }
      @media(max-width:640px){ .shop-split { grid-template-columns:1fr; } }

      /* Sidebar list rows */
      .shop-list-row { padding:10px 12px; border-radius:10px; margin-bottom:6px; cursor:pointer;
        border:1px solid var(--border); background:var(--surface2); transition:all .15s;
        display:flex; align-items:center; gap:8px; }
      .shop-list-row:hover { border-color:var(--brand); background:rgba(26,107,255,.05); }
      .shop-list-row.active { border-color:var(--brand); background:rgba(26,107,255,.1); }

      /* Add-item bar */
      .shop-add-bar { display:flex; gap:8px; margin-bottom:20px; flex-wrap:wrap; align-items:flex-start; }
      .shop-add-bar input { background:var(--surface2); border:1px solid var(--border); border-radius:10px;
        color:inherit; font-size:14px; padding:9px 13px; outline:none; transition:border-color .15s; }
      .shop-add-bar input:focus { border-color:var(--brand); }

      /* Card grid */
      .shop-grid { display:grid;
        grid-template-columns:repeat(auto-fill,minmax(100px,1fr));
        gap:10px; margin-bottom:4px; }
      @media(max-width:400px){ .shop-grid { grid-template-columns:repeat(3,1fr); } }

      /* Individual card */
      .shop-card {
        aspect-ratio:1; border-radius:16px;
        border:1.5px solid var(--border);
        background:var(--surface2);
        display:flex; flex-direction:column;
        align-items:center; justify-content:center;
        gap:6px; padding:10px 6px;
        cursor:pointer; transition:transform .12s, opacity .2s, background .2s, border-color .2s;
        position:relative; overflow:hidden; user-select:none;
        -webkit-tap-highlight-color:transparent;
      }
      .shop-card:hover { transform:scale(1.04); border-color:rgba(255,255,255,.25); }
      .shop-card:active { transform:scale(.96); }
      .shop-card.bought {
        background:rgba(255,255,255,.04);
        border-color:rgba(255,255,255,.07);
        opacity:.45;
      }
      .shop-card.bought .shop-card-icon { filter:grayscale(1); }
      .shop-card-icon { font-size:32px; line-height:1; flex-shrink:0; }
      .shop-card-icon.fallback {
        width:44px; height:44px; border-radius:12px;
        display:flex; align-items:center; justify-content:center;
        font-size:20px; font-weight:800; color:#fff; flex-shrink:0;
      }
      .shop-card-name { font-size:11px; font-weight:700; text-align:center;
        line-height:1.2; color:var(--text); word-break:break-word;
        max-width:100%; overflow:hidden;
        display:-webkit-box; -webkit-line-clamp:2; -webkit-box-orient:vertical; }
      .shop-card.bought .shop-card-name { text-decoration:line-through; color:var(--muted); }
      .shop-card-qty { font-size:10px; color:var(--muted); }
      .shop-card-check {
        position:absolute; top:5px; right:5px;
        width:16px; height:16px; border-radius:50%;
        background:#34d399; display:flex; align-items:center; justify-content:center;
        opacity:0; transition:opacity .2s;
      }
      .shop-card.bought .shop-card-check { opacity:1; }
      /* Section divider */
      .shop-section-hdr { font-size:10px; font-weight:700; color:var(--muted);
        text-transform:uppercase; letter-spacing:.7px; margin:20px 0 10px; }

      /* Autocomplete dropdown */
      .shop-ac { position:absolute; top:calc(100% + 4px); left:0; right:0; z-index:300;
        background:var(--surface); border:1px solid var(--border); border-radius:10px;
        box-shadow:0 10px 32px rgba(0,0,0,.5); max-height:200px; overflow-y:auto; display:none; }
      .shop-ac-row { padding:8px 12px; cursor:pointer; font-size:13px;
        display:flex; align-items:center; gap:10px;
        border-bottom:1px solid rgba(255,255,255,.04); }
      .shop-ac-row:hover { background:rgba(255,255,255,.06); }
      .shop-ac-row:last-child { border-bottom:none; }

      /* Share panel */
      .shop-share { display:none; margin-top:16px; padding:14px;
        border:1px solid var(--border); border-radius:12px; background:var(--surface2); }
      .shop-share.open { display:block; }
    `;
    document.head.appendChild(s);
  }

  // ── History ───────────────────────────────────────────────────────────────
  async function loadHistory() {
    try {
      const r = await fetch('/api/shopping/history');
      const j = await r.json();
      if (j.success) itemHistory = j.history || [];
    } catch(e){}
  }

  // ── Shell ─────────────────────────────────────────────────────────────────
  function renderShell() {
    shopPanel.innerHTML = `
      <div class="shop-root">
        <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px;flex-wrap:wrap;">
          <div style="font-size:20px;font-weight:800;flex:1;">🛒 Alışveriş</div>
          <input id="shopNewName" class="priv-new-input" placeholder="Yeni liste adı…" style="width:150px;">
          <button class="btn primary" id="shopCreateBtn" style="white-space:nowrap;">+ Liste Oluştur</button>
        </div>
        <div class="shop-split">
          <div>
            <div style="font-size:10px;font-weight:700;color:var(--muted);letter-spacing:.8px;text-transform:uppercase;margin-bottom:8px;">Listelerim</div>
            <div id="shopSidebar"></div>
          </div>
          <div id="shopMain">
            <div style="color:var(--muted);font-size:13px;text-align:center;padding:50px 20px;">
              <div style="font-size:36px;margin-bottom:12px;">🛒</div>
              Bir liste seçin veya yeni oluşturun
            </div>
          </div>
        </div>
      </div>`;

    $q('#shopCreateBtn').addEventListener('click', createList);
    $q('#shopNewName').addEventListener('keydown', e => { if (e.key==='Enter') createList(); });
  }

  // ── Sidebar ───────────────────────────────────────────────────────────────
  async function loadLists() {
    try {
      const r = await fetch('/api/shopping/lists');
      const j = await r.json();
      lists = j.success ? j.lists : [];
      renderSidebar();
      if (activeList) {
        const still = lists.find(l => l.id === activeList.id);
        if (still) selectList(still);
      }
    } catch(e){}
  }

  function renderSidebar() {
    const sb = $q('#shopSidebar');
    if (!sb) return;
    if (!lists.length) {
      sb.innerHTML = '<div style="color:var(--muted);font-size:12px;padding:4px 2px;">Henüz liste yok.</div>';
      return;
    }
    sb.innerHTML = lists.map(l => {
      const act = activeList && activeList.id === l.id;
      return `<div data-lid="${l.id}" class="shop-list-row${act?' active':''}">
        <span style="font-size:16px;">🛒</span>
        <div style="flex:1;min-width:0;">
          <div style="font-weight:700;font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;">${esc(l.name)}</div>
          <div style="font-size:10px;color:var(--muted);">${l.is_owner?'Sahibi':'Davetli'}</div>
        </div>
        ${l.is_owner?`<button data-del-list="${l.id}" style="border:none;background:transparent;color:var(--muted);cursor:pointer;font-size:16px;flex-shrink:0;padding:0;">×</button>`:''}
      </div>`;
    }).join('');

    sb.querySelectorAll('[data-lid]').forEach(el => {
      el.addEventListener('click', e => {
        if (e.target.dataset.delList) return;
        selectList(lists.find(l => l.id === parseInt(el.dataset.lid)));
      });
    });
    sb.querySelectorAll('[data-del-list]').forEach(btn => {
      btn.addEventListener('click', async e => {
        e.stopPropagation();
        const lid = parseInt(btn.dataset.delList);
        if (!confirm('Bu listeyi silmek istiyor musunuz?')) return;
        await fetch(`/api/shopping/list/${lid}`, {method:'DELETE'});
        if (activeList && activeList.id === lid) {
          activeList = null; clearInterval(pollTimer);
          $q('#shopMain').innerHTML = '<div style="color:var(--muted);font-size:13px;text-align:center;padding:50px;"><div style="font-size:36px;margin-bottom:12px;">🛒</div>Bir liste seçin</div>';
        }
        loadLists();
      });
    });
  }

  async function createList() {
    const inp  = $q('#shopNewName');
    const name = inp.value.trim();
    if (!name) { inp.focus(); return; }
    await fetch('/api/shopping/list', {
      method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({name})
    });
    inp.value = '';
    await loadLists();
  }

  function selectList(list) {
    if (!list) return;
    activeList = list;
    renderSidebar();
    renderMain(list);
    clearInterval(pollTimer);
    loadItems(list.id);
    pollTimer = setInterval(() => loadItems(list.id), 8000);
  }

  // ── Main panel ────────────────────────────────────────────────────────────
  function renderMain(list) {
    $q('#shopMain').innerHTML = `
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px;flex-wrap:wrap;">
        <span style="font-size:17px;font-weight:800;">${esc(list.name)}</span>
        <span id="shopCount" style="font-size:11px;color:var(--muted);background:var(--surface2);
              padding:2px 8px;border-radius:8px;"></span>
        <div style="margin-left:auto;display:flex;gap:6px;">
          <button class="btn" id="shopClearBtn" style="font-size:11px;padding:4px 10px;display:none;">
            🗑 Satın Alınanları Temizle
          </button>
          ${list.is_owner?'<button class="btn" id="shopShareBtn" style="font-size:11px;padding:4px 10px;">👥 Paylaş</button>':''}
        </div>
      </div>

      <!-- Add bar -->
      <div class="shop-add-bar">
        <div style="flex:2;min-width:140px;position:relative;">
          <input id="shopItemName" class="priv-new-input" placeholder="Ürün ekle… (örn: Domates)"
                 style="width:100%;font-size:14px;" autocomplete="off">
          <div id="shopAcDrop" class="shop-ac"></div>
        </div>
        <input id="shopItemQty" class="priv-new-input" placeholder="Miktar"
               style="flex:0 0 80px;font-size:14px;">
        <button class="btn primary" id="shopAddBtn" style="padding:9px 18px;font-weight:700;white-space:nowrap;">
          + Ekle
        </button>
      </div>

      <!-- Active items grid -->
      <div id="shopActiveGrid" class="shop-grid"></div>

      <!-- Bought section -->
      <div id="shopBoughtSection" style="display:none;">
        <div class="shop-section-hdr">
          ✓ Sepete Alındı
          <span id="shopBoughtCount" style="font-weight:400;margin-left:4px;"></span>
        </div>
        <div id="shopBoughtGrid" class="shop-grid"></div>
      </div>

      <!-- Share panel -->
      ${list.is_owner?`
      <div id="shopSharePanel" class="shop-share">
        <div style="font-size:12px;font-weight:700;color:var(--muted);margin-bottom:10px;">👥 Listeyi Paylaş</div>
        <div style="display:flex;gap:8px;">
          <select id="shopInviteSel" class="invite-select" style="flex:1;">
            <option value="">— Kullanıcı seç —</option>
            ${(USERS||[]).filter(u=>u.id!==CURRENT_USER.id).map(u=>`<option value="${u.id}">${esc(u.username)}</option>`).join('')}
          </select>
          <button class="btn primary" id="shopInviteBtn" style="font-size:12px;white-space:nowrap;">Davet Et</button>
        </div>
      </div>`:''}`;

    // Events
    $q('#shopAddBtn').addEventListener('click', addItem);
    $q('#shopItemName').addEventListener('keydown', e => { if (e.key==='Enter') addItem(); });
    $q('#shopClearBtn').addEventListener('click', clearBought);

    if (list.is_owner) {
      $q('#shopShareBtn')?.addEventListener('click', () => {
        $q('#shopSharePanel').classList.toggle('open');
      });
      $q('#shopInviteBtn')?.addEventListener('click', async () => {
        const uid = parseInt($q('#shopInviteSel').value);
        if (!uid) return;
        await fetch(`/api/shopping/list/${list.id}/invite`, {
          method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({user_id:uid})
        });
      });
    }

    // Autocomplete
    const nameInp = $q('#shopItemName');
    const acDrop  = $q('#shopAcDrop');
    nameInp.addEventListener('input', () => {
      const val = nameInp.value.trim().toLowerCase();
      if (!val) { acDrop.style.display='none'; return; }
      const hits = itemHistory.filter(h => h.name.toLowerCase().includes(val)).slice(0,8);
      if (!hits.length) { acDrop.style.display='none'; return; }
      acDrop.innerHTML = hits.map(h => `
        <div class="shop-ac-row" data-name="${esc(h.name)}">
          <span style="font-size:18px;">${(window.ShopEmoji&&ShopEmoji.resolveEmoji(h.name))||'•'}</span>
          <span style="flex:1;">${esc(h.name)}</span>
        </div>`).join('');
      acDrop.style.display = 'block';
      acDrop.querySelectorAll('.shop-ac-row').forEach(el => {
        el.addEventListener('mousedown', e => {
          e.preventDefault();
          nameInp.value = el.dataset.name;
          acDrop.style.display = 'none';
        });
      });
    });
    nameInp.addEventListener('blur', () => setTimeout(() => acDrop.style.display='none', 150));
  }

  // ── Items ─────────────────────────────────────────────────────────────────
  async function loadItems(lid) {
    try {
      const r = await fetch(`/api/shopping/list/${lid}/items`);
      const j = await r.json();
      if (!j.success) return;
      renderItems(j.items);
    } catch(e){}
  }

  // Emoji + fallback card icon HTML
  function cardIcon(name) {
    const emoji = window.ShopEmoji ? ShopEmoji.resolveEmoji(name) : null;
    if (emoji) return `<span class="shop-card-icon">${emoji}</span>`;
    const COLORS = ['#3b82f6','#8b5cf6','#ec4899','#f59e0b','#10b981','#ef4444','#06b6d4','#f97316'];
    const color  = COLORS[(name||'').charCodeAt(0) % COLORS.length];
    return `<div class="shop-card-icon fallback" style="background:${color};">${(name||'?')[0].toUpperCase()}</div>`;
  }

  function renderItems(items) {
    const activeGrid  = $q('#shopActiveGrid');
    const boughtGrid  = $q('#shopBoughtGrid');
    const boughtSec   = $q('#shopBoughtSection');
    const countEl     = $q('#shopCount');
    const clearBtn    = $q('#shopClearBtn');
    const boughtCount = $q('#shopBoughtCount');
    if (!activeGrid) return;

    const unchecked = items.filter(i => !i.checked);
    const checked   = items.filter(i =>  i.checked);

    if (countEl) countEl.textContent = `${unchecked.length} ürün`;
    if (boughtSec) boughtSec.style.display = checked.length ? 'block' : 'none';
    if (clearBtn)  clearBtn.style.display  = checked.length ? 'inline-flex' : 'none';
    if (boughtCount) boughtCount.textContent = `(${checked.length})`;

    const makeCard = (i, isBought) => {
      const card = document.createElement('div');
      card.className = 'shop-card' + (isBought ? ' bought' : '');
      card.dataset.iid = i.id;
      card.innerHTML = `
        ${cardIcon(i.name)}
        <span class="shop-card-name">${esc(i.name)}</span>
        ${i.quantity ? `<span class="shop-card-qty">${esc(i.quantity)}</span>` : ''}
        <div class="shop-card-check">
          <svg width="9" height="9" viewBox="0 0 12 10" fill="none" stroke="#fff"
               stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
            <polyline points="1,5 4,9 11,1"/>
          </svg>
        </div>`;

      card.addEventListener('click', async () => {
        // Prevent double-tap spam
        if (card.dataset.busy) return;
        card.dataset.busy = '1';
        card.style.opacity = '.4';
        await fetch(`/api/shopping/item/${i.id}/toggle`, {method:'POST'});
        await loadItems(activeList.id);
      });
      return card;
    };

    // Active grid
    activeGrid.innerHTML = '';
    if (unchecked.length === 0) {
      activeGrid.innerHTML = `
        <div style="grid-column:1/-1;text-align:center;padding:30px;color:var(--muted);">
          <div style="font-size:32px;margin-bottom:8px;">✨</div>
          <div style="font-size:13px;">Liste boş. Yukarıdan ürün ekleyin.</div>
        </div>`;
    } else {
      unchecked.forEach(i => activeGrid.appendChild(makeCard(i, false)));
    }

    // Bought grid
    if (boughtGrid) {
      boughtGrid.innerHTML = '';
      checked.forEach(i => boughtGrid.appendChild(makeCard(i, true)));
    }
  }

  async function addItem() {
    if (!activeList) return;
    const nameInp = $q('#shopItemName');
    const qtyInp  = $q('#shopItemQty');
    const name    = nameInp.value.trim();
    if (!name) { nameInp.focus(); return; }

    // Prevent duplicates — check active items
    try {
      const r = await fetch(`/api/shopping/list/${activeList.id}/items`);
      const j = await r.json();
      if (j.success) {
        const active = (j.items||[]).filter(i => !i.checked);
        const dup = active.find(i => i.name.trim().toLowerCase() === name.toLowerCase());
        if (dup) {
          nameInp.value='';
          nameInp.focus();
          // Flash existing card
          const existing = shopPanel.querySelector(`[data-iid="${dup.id}"]`);
          if (existing) {
            existing.style.transform='scale(1.15)';
            existing.style.borderColor='var(--brand)';
            setTimeout(()=>{ existing.style.transform=''; existing.style.borderColor=''; }, 500);
          }
          return;
        }
      }
    } catch(e){}

    const qty = qtyInp.value.trim();
    nameInp.value=''; qtyInp.value='';
    nameInp.focus();
    if ($q('#shopAcDrop')) $q('#shopAcDrop').style.display='none';

    await fetch(`/api/shopping/list/${activeList.id}/item`, {
      method:'POST', headers:{'Content-Type':'application/json'},
      body: JSON.stringify({name, quantity:qty, category:'', qty_num:parseFloat(qty)||1})
    });
    await loadItems(activeList.id);
    await loadHistory();
  }

  async function clearBought() {
    if (!activeList) return;
    if (!confirm('Sepete alınan ürünler listeden silinsin mi?')) return;
    try {
      const r = await fetch(`/api/shopping/list/${activeList.id}/items`);
      const j = await r.json();
      const chk = (j.items||[]).filter(i => i.checked);
      await Promise.all(chk.map(i => fetch(`/api/shopping/item/${i.id}`, {method:'DELETE'})));
      await loadItems(activeList.id);
    } catch(e){}
  }

  window.shopModule = {
    toggleItem: async (iid, lid) => {
      await fetch(`/api/shopping/item/${iid}/toggle`, {method:'POST'});
      await loadItems(lid);
    },
    deleteItem: async (iid, lid) => {
      await fetch(`/api/shopping/item/${iid}`, {method:'DELETE'});
      await loadItems(lid);
    }
  };
})();
