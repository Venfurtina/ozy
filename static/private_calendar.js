/* private_calendar.js – Kisisel takvim ozellikleri */
/* global CURRENT_USER */

(function () {
  'use strict';

  // ── Utilities ──────────────────────────────────────────────────────────────
  function esc(s) {
    return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
  }
  function $id(id) { return document.getElementById(id); }
  function pad2(n) { return String(n).padStart(2,'0'); }
  function dateStr(y,m,d) { return `${y}-${pad2(m)}-${pad2(d)}`; }
  function monthLabel(y,m) {
    return new Date(y,m-1,1).toLocaleString('tr-TR',{month:'long',year:'numeric'});
  }

  // ── State ──────────────────────────────────────────────────────────────────
  let allCalendars = [];          // [{id, name, owner_name, owner_id}, ...]
  let activeCalId  = null;        // currently open calendar id
  let calState     = {};          // calId -> {year, month, reservations, changes, members, allUsers, isOwner}
  let notifications = [];

  // ── Page-level tab switching ───────────────────────────────────────────────
  // Main tab click (data-tab="main" only - service tabs handled by services.js)
  document.querySelectorAll('.page-tab[data-tab="main"]').forEach(btn => {
    btn.addEventListener('click', () => {
      document.querySelectorAll('.page-tab').forEach(b => b.classList.remove('active'));
      document.querySelectorAll('.page-tab-panel').forEach(p => p.classList.remove('active'));
      btn.classList.add('active');
      const panel = $id('panel-main');
      if (panel) panel.classList.add('active');
    });
  });

  // ── Notifications ──────────────────────────────────────────────────────────
  async function loadNotifications() {
    try {
      const r = await fetch('/api/private/notifications');
      const j = await r.json();
      notifications = j.success ? j.notifications : [];
      renderNotifBadge();
      renderNotifDropdown();
    } catch(e) { /* ignore */ }
  }

  function renderNotifBadge() {
    const cnt = $id('notifCount');
    const btn = $id('notifBtn');
    if (!cnt) return;
    if (notifications.length > 0) {
      cnt.textContent = notifications.length;
      cnt.style.display = 'flex';
      if (btn) btn.classList.add('has-notif');
    } else {
      cnt.style.display = 'none';
      if (btn) btn.classList.remove('has-notif');
    }
  }

  function renderNotifDropdown() {
    const list = $id('notifList');
    if (!list) return;
    if (notifications.length === 0) {
      list.innerHTML = '<div class="notif-empty">Yeni bildirim yok.</div>';
      return;
    }
    list.innerHTML = '';
    notifications.forEach(n => {
      const item = document.createElement('div');
      item.className = 'notif-item';
      item.innerHTML = `
        <div class="notif-title">📬 Takvim Daveti</div>
        <div class="notif-sub"><strong>${esc(n.invited_by_name)}</strong> STRINGS.notif_invited_you + ' ' "<strong>${esc(n.calendar_name)}</strong>" STRINGS.notif_invited_to</div>
        <div class="notif-actions">
          <button class="notif-accept" data-id="${n.id}" data-calid="${n.calendar_id}">✓ Kabul Et</button>
          <button class="notif-dismiss" data-id="${n.id}">Reddet</button>
        </div>`;

      item.querySelector('.notif-accept').addEventListener('click', async (e) => {
        const nid = e.target.dataset.id;
        const r2  = await fetch(`/api/private/notification/${nid}/accept`, {method:'POST'});
        const j2  = await r2.json();
        if (j2.success) {
          // Remove notification locally
          notifications = notifications.filter(x => String(x.id) !== String(nid));
          renderNotifBadge();
          renderNotifDropdown();
          closeNotifModal();
          // Switch to private tab and open the new calendar
          document.querySelectorAll('.page-tab').forEach(b => b.classList.remove('active'));
          document.querySelectorAll('.page-tab-panel').forEach(p => p.classList.remove('active'));
          document.querySelector('.page-tab[data-tab="private"]').classList.add('active');
          $id('panel-private').classList.add('active');
          await loadPrivateCalendars(j2.calendar ? j2.calendar.id : null);
        }
      });

      item.querySelector('.notif-dismiss').addEventListener('click', async (e) => {
        const nid = e.target.dataset.id;
        await fetch(`/api/private/notification/${nid}`, {method:'DELETE'});
        notifications = notifications.filter(x => String(x.id) !== String(nid));
        renderNotifBadge();
        renderNotifDropdown();
        if (notifications.length === 0) closeNotifModal();
      });

      list.appendChild(item);
    });
  }

  // Notification bell → opens modal overlay
  function openNotifModal() {
    const overlay = $id('notifOverlay');
    if (overlay) overlay.classList.add('open');
  }
  function closeNotifModal() {
    const overlay = $id('notifOverlay');
    if (overlay) overlay.classList.remove('open');
  }
  document.addEventListener('DOMContentLoaded', () => {
    const btn = $id('notifBtn');
    if (btn) btn.addEventListener('click', (e) => {
      e.stopPropagation();
      openNotifModal();
    });
    const closeBtn = $id('notifClose');
    if (closeBtn) closeBtn.addEventListener('click', closeNotifModal);
    const overlay = $id('notifOverlay');
    if (overlay) overlay.addEventListener('click', (e) => {
      if (e.target === overlay) closeNotifModal();
    });
  });

  // ── Load & render private calendar list ───────────────────────────────────
  async function loadPrivateCalendars(openCalId) {
    try {
      const r = await fetch('/api/private/calendars');
      const j = await r.json();
      allCalendars = j.success ? j.calendars : [];
      renderSubtabs(openCalId);
    } catch(e) {
      $id('privSubtabs').innerHTML = '<span style="color:#ef4444;font-size:12px">Yüklenemedi.</span>';
    }
  }

  function renderSubtabs(openCalId) {
    const bar    = $id('privSubtabs');
    const panels = $id('privPanels');
    bar.innerHTML = '';
    panels.innerHTML = '';

    if (allCalendars.length === 0) {
      bar.innerHTML = `<span style="font-size:12px;color:var(--muted)">${STRINGS.priv_no_cal}</span>`;
      return;
    }

    // Choose which calendar to open
    let targetId = openCalId || activeCalId || allCalendars[0].id;
    if (!allCalendars.find(c => c.id === targetId)) targetId = allCalendars[0].id;
    activeCalId = targetId;

    allCalendars.forEach(cal => {
      const tab = document.createElement('button');
      tab.className = 'priv-subtab' + (cal.id === activeCalId ? ' active' : '');
      tab.textContent = cal.name;
      tab.dataset.calid = cal.id;
      tab.addEventListener('click', () => {
        activeCalId = cal.id;
        document.querySelectorAll('.priv-subtab').forEach(t => t.classList.remove('active'));
        tab.classList.add('active');
        document.querySelectorAll('.priv-subtab-panel').forEach(p => p.classList.remove('active'));
        const panel = $id(`priv-panel-${cal.id}`);
        if (panel) {
          panel.classList.add('active');
          if (!calState[cal.id]) loadCalendarData(cal.id);
        }
      });
      bar.appendChild(tab);

      // Panel placeholder
      const panel = document.createElement('div');
      panel.className = 'priv-subtab-panel' + (cal.id === activeCalId ? ' active' : '');
      panel.id = `priv-panel-${cal.id}`;
      panel.innerHTML = '<div style="padding:20px;color:var(--muted);font-size:13px">Yükleniyor…</div>';
      panels.appendChild(panel);
    });

    // Load the active calendar
    loadCalendarData(activeCalId);
  }

  // ── Load calendar data for a given month ──────────────────────────────────
  async function loadCalendarData(calId, year, month) {
    const now = new Date();
    const y   = year  || (calState[calId] ? calState[calId].year  : now.getFullYear());
    const m   = month || (calState[calId] ? calState[calId].month : now.getMonth()+1);
    try {
      const r = await fetch(`/api/private/calendar/${calId}/data?year=${y}&month=${m}`);
      const j = await r.json();
      if (!j.success) return;
      calState[calId] = {
        year: y, month: m,
        reservations: j.reservations || {},
        changes: {},
        members: j.members || [],
        allUsers: j.all_users || [],
        isOwner: j.is_owner,
        calendar: j.calendar
      };
      renderCalendarPanel(calId);
      loadPrivChat(calId);
    } catch(e) {
      const panel = $id(`priv-panel-${calId}`);
      if (panel) panel.innerHTML = '<div style="color:#ef4444;padding:20px">Yüklenemedi.</div>';
    }
  }

  // ── Render a single private calendar panel ────────────────────────────────
  function renderCalendarPanel(calId) {
    const state = calState[calId];
    if (!state) return;
    const panel = $id(`priv-panel-${calId}`);
    if (!panel) return;
    const cal = allCalendars.find(c => c.id === calId) || state.calendar || {};
    const isOwner = state.isOwner;

    panel.innerHTML = '';

    // ── Header ──
    const hdr = document.createElement('div');
    hdr.className = 'priv-cal-card';

    // Name + rename form
    let renameHtml = '';
    if (isOwner) {
      renameHtml = `
        <div class="rename-form" style="margin-top:6px;">
          <input class="rename-input" id="rename-${calId}" value="${esc(cal.name)}" />
          <button class="btn" style="font-size:11px;padding:5px 10px" data-rename="${calId}">✎ Yeniden Adlandır</button>
          <button class="btn" style="font-size:11px;padding:5px 10px;color:#ef4444;border-color:#ef4444" data-delete="${calId}">🗑 Sil</button>
        </div>`;
    }

    // Month nav
    const monthHtml = `
      <div style="display:flex;align-items:center;gap:8px;margin-bottom:14px;flex-wrap:wrap;">
        <button class="btn" data-prevmonth="${calId}">◀</button>
        <span style="font-weight:600;font-size:14px" id="priv-month-label-${calId}">${monthLabel(state.year,state.month)}</span>
        <button class="btn" data-nextmonth="${calId}">▶</button>
        <span class="badge" id="priv-dirty-${calId}" style="display:none">Kaydedilmemiş</span>
        <button class="btn primary" data-save="${calId}">💾 Kaydet</button>
      </div>`;

    // Calendar grid
    const gridHtml = `<div class="cal-grid" id="priv-grid-${calId}"></div>`;

    // Legend
    const legendHtml = `<div class="legend" id="priv-legend-${calId}" style="margin-top:12px;"></div>`;

    // Members / invite section (owner only)
    let membersHtml = '';
    if (isOwner) {
      const chips = state.members.map(m =>
        `<span class="member-chip">
          <span class="dot" style="background:${esc(m.color||'#4caf50')}"></span>
          ${esc(m.username)}
          ${m.id !== CURRENT_USER.id
            ? `<span class="member-remove" data-remove-member="${m.id}" data-calid="${calId}" title="Çıkar">×</span>`
            : '<span style="font-size:10px;color:var(--muted)">(sen)</span>'}
        </span>`
      ).join('');

      const opts = state.allUsers
        .filter(u => u.id !== CURRENT_USER.id && !state.members.find(m => m.id === u.id))
        .map(u => `<option value="${u.id}">${esc(u.username)}</option>`)
        .join('');

      membersHtml = `
        <div class="invite-section">
          <h4>👥 Üyeler</h4>
          <div class="member-list">${chips || '<span style="color:var(--muted);font-size:12px">Henüz üye yok.</span>'}</div>
          ${opts ? `
            <div class="invite-row" style="margin-top:12px;">
              <select class="invite-select" id="invite-sel-${calId}">
                <option value="">${STRINGS.priv_select_user}</option>${opts}
              </select>
              <button class="btn primary" style="font-size:12px" data-invite="${calId}">Davet Et</button>
            </div>` : '<p style="font-size:12px;color:var(--muted);margin-top:10px">Davet edilebilecek başka kullanıcı yok.</p>'}
        </div>`;
    }

    hdr.innerHTML = `
      <div class="priv-cal-header">
        <span class="priv-cal-name">${esc(cal.name)}</span>
        <span class="priv-cal-owner">👤 ${esc(cal.owner_name || '')}</span>
      </div>
      ${renameHtml}
      ${monthHtml}
      ${gridHtml}
      ${legendHtml}
      ${membersHtml}`;

    // ── Chat card ──
    const chatCard = document.createElement('div');
    chatCard.className = 'priv-cal-card';
    chatCard.style.cssText = 'margin-top:16px;display:flex;flex-direction:column;';
    chatCard.innerHTML = `
      <div style="font-size:13px;font-weight:700;color:var(--text);margin-bottom:10px;display:flex;align-items:center;gap:6px;">
        💬 <span>${STRINGS.cal_chat_title || 'Chat'}</span>
        <span style="font-size:11px;color:var(--muted);font-weight:400;">${monthLabel(state.year,state.month)}</span>
      </div>
      <div class="chat-messages" id="priv-chat-${calId}" style="min-height:120px;max-height:260px;overflow-y:auto;
           display:flex;flex-direction:column;gap:8px;padding:10px;background:rgba(255,255,255,0.02);
           border:1px solid var(--border);border-radius:8px;margin-bottom:10px;"></div>
      <div style="display:flex;gap:8px;">
        <input id="priv-chat-input-${calId}" class="priv-new-input" placeholder="${STRINGS.cal_chat_ph || 'Mesaj yazın…'}"
               style="flex:1;min-width:0;" />
        <button class="btn primary" style="flex-shrink:0;white-space:nowrap" data-chat-send="${calId}">
          ${STRINGS.cal_send || 'Gönder'}
        </button>
      </div>`;
    panel.appendChild(chatCard);

    panel.appendChild(hdr);

    // Wire up buttons
    panel.querySelectorAll('[data-prevmonth]').forEach(btn => {
      btn.addEventListener('click', () => goPrivMonth(calId, -1));
    });
    panel.querySelectorAll('[data-nextmonth]').forEach(btn => {
      btn.addEventListener('click', () => goPrivMonth(calId, 1));
    });
    panel.querySelectorAll('[data-save]').forEach(btn => {
      btn.addEventListener('click', () => savePrivCalendar(calId));
    });
    panel.querySelectorAll('[data-rename]').forEach(btn => {
      btn.addEventListener('click', () => renameCalendar(calId));
    });
    panel.querySelectorAll('[data-delete]').forEach(btn => {
      btn.addEventListener('click', () => deleteCalendar(calId));
    });
    panel.querySelectorAll('[data-invite]').forEach(btn => {
      btn.addEventListener('click', () => inviteUser(calId));
    });
    panel.querySelectorAll('[data-remove-member]').forEach(btn => {
      btn.addEventListener('click', () => removeMember(calId, parseInt(btn.dataset.removeMember)));
    });

    // Wire chat send
    panel.querySelectorAll('[data-chat-send]').forEach(btn => {
      const cid = parseInt(btn.dataset.chatSend);
      btn.addEventListener('click', () => sendPrivChat(cid));
    });
    const chatInput = $id(`priv-chat-input-${calId}`);
    if (chatInput) {
      chatInput.addEventListener('keydown', e => {
        if (e.key === 'Enter') sendPrivChat(calId);
      });
    }

    drawPrivGrid(calId);
    drawPrivLegend(calId);
  }

  // ── Draw calendar grid ────────────────────────────────────────────────────
  function drawPrivGrid(calId) {
    const state = calState[calId];
    if (!state) return;
    const grid = $id(`priv-grid-${calId}`);
    if (!grid) return;
    grid.innerHTML = '';

    const weekdays = ['Pzt','Sal','Çar','Per','Cum','Cmt','Paz'];
    weekdays.forEach(w => {
      const el = document.createElement('div');
      el.className = 'weekday';
      el.textContent = w;
      grid.appendChild(el);
    });

    const first = new Date(state.year, state.month-1, 1);
    const offset = (first.getDay()+6) % 7;
    const daysInMonth = new Date(state.year, state.month, 0).getDate();

    for (let i=0; i<offset; i++) {
      const blank = document.createElement('div');
      blank.className = 'cal-cell disabled';
      grid.appendChild(blank);
    }

    for (let day=1; day<=daysInMonth; day++) {
      const ds = dateStr(state.year, state.month, day);
      const existing = state.reservations[ds];
      const cell = document.createElement('div');
      cell.className = 'cal-cell';

      const dayEl = document.createElement('div');
      dayEl.className = 'cal-day';
      dayEl.textContent = String(day);
      cell.appendChild(dayEl);

      if (existing) {
        const isMine = existing.userId === CURRENT_USER.id;
        cell.style.background = existing.color || 'rgba(255,255,255,0.1)';
        const meta = document.createElement('div');
        meta.className = 'cal-meta';
        meta.textContent = existing.username || '';
        cell.appendChild(meta);
        if (!isMine) cell.classList.add('locked');
      }

      cell.addEventListener('click', () => {
        const cur = state.reservations[ds];
        if (cur && cur.userId !== CURRENT_USER.id) return;
        if (cur && cur.userId === CURRENT_USER.id) {
          delete state.reservations[ds];
          state.changes[ds] = null;
        } else {
          const entry = {
            userId: CURRENT_USER.id, username: CURRENT_USER.name,
            color: CURRENT_USER.color, timestamp: new Date().toISOString()
          };
          state.reservations[ds] = entry;
          state.changes[ds] = entry;
        }
        drawPrivGrid(calId);
        setPrivDirty(calId, true);
      });

      grid.appendChild(cell);
    }

    // trailing blanks
    const total = grid.children.length;
    const mod = total % 7;
    if (mod !== 0) {
      for (let i=0; i<7-mod; i++) {
        const blank = document.createElement('div');
        blank.className = 'cal-cell disabled';
        grid.appendChild(blank);
      }
    }
  }

  function drawPrivLegend(calId) {
    const state = calState[calId];
    if (!state) return;
    const wrap = $id(`priv-legend-${calId}`);
    if (!wrap) return;
    wrap.innerHTML = '';
    (state.members||[]).forEach(u => {
      const item = document.createElement('div');
      item.className = 'legend-item';
      const dot = document.createElement('div');
      dot.className = 'dot';
      dot.style.background = u.color || '#4caf50';
      const name = document.createElement('div');
      name.textContent = u.username;
      name.style.fontSize = '13px'; name.style.fontWeight = '700';
      item.appendChild(dot); item.appendChild(name);
      wrap.appendChild(item);
    });
  }

  function setPrivDirty(calId, isDirty) {
    const el = $id(`priv-dirty-${calId}`);
    if (el) el.style.display = isDirty ? 'inline-flex' : 'none';
  }

  function goPrivMonth(calId, delta) {
    const state = calState[calId];
    if (!state) return;
    if (Object.keys(state.changes).length) {
      if (!confirm(STRINGS.unsaved_changes)) return;
    }
    let {year,month} = state;
    month += delta;
    if (month <= 0)  { month=12; year--; }
    if (month >= 13) { month=1;  year++; }
    state.year=year; state.month=month; state.changes={};
    loadCalendarData(calId, year, month);
  }

  async function savePrivCalendar(calId) {
    const state = calState[calId];
    if (!state || !Object.keys(state.changes).length) {
      alert(STRINGS.no_changes);
      return;
    }
    try {
      const r = await fetch(`/api/private/calendar/${calId}/save`, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({changes: state.changes})
      });
      const j = await r.json();
      if (j.success) {
        state.changes = {};
        setPrivDirty(calId, false);
        alert(STRINGS.saved);
      } else {
        alert(j.error || STRINGS.priv_save_fail);
      }
    } catch(e) { alert(STRINGS.server_error); }
  }

  async function renameCalendar(calId) {
    const input = $id(`rename-${calId}`);
    const name  = (input ? input.value : '').trim();
    if (!name) { alert(STRINGS.priv_name_empty); return; }
    try {
      const r = await fetch(`/api/private/calendar/${calId}/rename`, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({name})
      });
      const j = await r.json();
      if (j.success) {
        const cal = allCalendars.find(c => c.id === calId);
        if (cal) cal.name = name;
        await loadPrivateCalendars(calId);
      } else {
        alert(j.error || STRINGS.priv_rename_fail);
      }
    } catch(e) { alert(STRINGS.server_error); }
  }

  async function deleteCalendar(calId) {
    if (!confirm(STRINGS.priv_delete_confirm)) return;
    try {
      const r = await fetch(`/api/private/calendar/${calId}`, {method:'DELETE'});
      const j = await r.json();
      if (j.success) {
        allCalendars = allCalendars.filter(c => c.id !== calId);
        delete calState[calId];
        if (activeCalId === calId) activeCalId = allCalendars.length ? allCalendars[0].id : null;
        renderSubtabs(activeCalId);
      } else {
        alert(j.error || STRINGS.priv_delete_fail);
      }
    } catch(e) { alert(STRINGS.server_error); }
  }

  // ── Private calendar chat ─────────────────────────────────────────────────
  async function loadPrivChat(calId) {
    const state = calState[calId];
    if (!state) return;
    const box = $id(`priv-chat-${calId}`);
    if (!box) return;
    try {
      const r = await fetch(`/api/private/calendar/${calId}/comments?year=${state.year}&month=${state.month}`);
      const j = await r.json();
      if (!j.success) return;
      box.innerHTML = '';
      if (!j.comments.length) {
        box.innerHTML = `<div style="color:var(--muted);font-size:12px;text-align:center;padding:16px">Henüz mesaj yok.</div>`;
        return;
      }
      j.comments.forEach(c => {
        const msg = document.createElement('div');
        msg.style.cssText = 'border:1px solid var(--border);border-radius:10px;padding:8px 10px;background:rgba(255,255,255,0.03);';
        msg.innerHTML = `<div style="display:flex;align-items:center;gap:6px;margin-bottom:4px;">
          <span style="width:8px;height:8px;border-radius:50%;background:${esc(c.color||'#4caf50')};flex-shrink:0;"></span>
          <span style="font-weight:700;font-size:12px;">${esc(c.username)}</span>
          <span style="color:var(--muted);font-size:10px;margin-left:auto;">${c.created_at ? new Date(c.created_at+'Z').toLocaleString('tr-TR') : ''}</span>
        </div>
        <div style="font-size:12px;color:rgba(255,255,255,0.88);line-height:1.4;">${esc(c.comment)}</div>`;
        box.appendChild(msg);
      });
      box.scrollTop = box.scrollHeight;
    } catch(e) {}
  }

  async function sendPrivChat(calId) {
    const input = $id(`priv-chat-input-${calId}`);
    const text  = (input ? input.value : '').trim();
    if (!text) return;
    try {
      const r = await fetch(`/api/private/calendar/${calId}/comments`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({comment: text})
      });
      const j = await r.json();
      if (j.success) { input.value = ''; await loadPrivChat(calId); }
    } catch(e) {}
  }

  async function inviteUser(calId) {
    const sel = $id(`invite-sel-${calId}`);
    const uid = sel ? parseInt(sel.value) : 0;
    if (!uid) { alert(STRINGS.priv_select_user_alert); return; }
    try {
      const r = await fetch(`/api/private/calendar/${calId}/invite`, {
        method:'POST',
        headers:{'Content-Type':'application/json'},
        body: JSON.stringify({user_id: uid})
      });
      const j = await r.json();
      if (j.success) {
        alert(`${j.invited} ${STRINGS.priv_invited}`);
        loadCalendarData(calId, calState[calId]&&calState[calId].year, calState[calId]&&calState[calId].month);
      } else {
        alert(j.error || STRINGS.priv_invite_fail);
      }
    } catch(e) { alert(STRINGS.server_error); }
  }

  async function removeMember(calId, memberId) {
    if (!confirm(STRINGS.priv_remove_confirm)) return;
    try {
      const r = await fetch(`/api/private/calendar/${calId}/invite/${memberId}`, {method:'DELETE'});
      const j = await r.json();
      if (j.success) {
        loadCalendarData(calId, calState[calId]&&calState[calId].year, calState[calId]&&calState[calId].month);
      } else {
        alert(j.error || STRINGS.priv_remove_fail);
      }
    } catch(e) { alert(STRINGS.server_error); }
  }

  // ── Create new calendar ────────────────────────────────────────────────────
  // Expose init for services.js to call
  window.initPrivateCalendar = function() {
    loadPrivateCalendars();
    const createBtn = $id('createCalBtn');
    if (createBtn && !createBtn._bound) {
      createBtn._bound = true;
      createBtn.addEventListener('click', async () => {
        const input = $id('newCalName');
        const name  = (input ? input.value : '').trim() || (STRINGS.priv_default_name || 'Özel Takvimim');
        try {
          const r = await fetch('/api/private/calendar/create', {
            method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({name})
          });
          const j = await r.json();
          if (j.success) {
            if (input) input.value = '';
            allCalendars.unshift(j.calendar);
            activeCalId = j.calendar.id;
            renderSubtabs(j.calendar.id);
          } else { alert(j.error || STRINGS.priv_create_fail); }
        } catch(e) { alert(STRINGS.server_error); }
      });
    }
    const nameInput = $id('newCalName');
    if (nameInput && !nameInput._bound) {
      nameInput._bound = true;
      nameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') { const btn = $id('createCalBtn'); if (btn) btn.click(); }
      });
    }
  };

  document.addEventListener('DOMContentLoaded', () => {
    // Create calendar button
    $id('createCalBtn') && $id('createCalBtn').addEventListener('click', async () => {
      const input = $id('newCalName');
      const name  = (input ? input.value : '').trim() || STRINGS.priv_default_name;
      try {
        const r = await fetch('/api/private/calendar/create', {
          method:'POST',
          headers:{'Content-Type':'application/json'},
          body: JSON.stringify({name})
        });
        const j = await r.json();
        if (j.success) {
          if (input) input.value = '';
          allCalendars.unshift(j.calendar);
          activeCalId = j.calendar.id;
          renderSubtabs(j.calendar.id);
          // Switch to private tab if not already there
          document.querySelectorAll('.page-tab').forEach(b => b.classList.remove('active'));
          document.querySelectorAll('.page-tab-panel').forEach(p => p.classList.remove('active'));
          document.querySelector('.page-tab[data-tab="private"]').classList.add('active');
          $id('panel-private').classList.add('active');
        } else {
          alert(j.error || STRINGS.priv_create_fail);
        }
      } catch(e) { alert(STRINGS.server_error); }
    });

    // Allow Enter in new calendar name input
    const nameInput = $id('newCalName');
    if (nameInput) {
      nameInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') $id('createCalBtn').click();
      });
    }

    // Initial notification load + poll every 30s
    loadNotifications();
    setInterval(loadNotifications, 30000);
  });

})();
