/* global INITIAL_YEAR, INITIAL_MONTH, RESERVATIONS, USERS, COMMENTS, CURRENT_USER */

(function () {
  const state = {
    year: INITIAL_YEAR,
    month: INITIAL_MONTH, // 1-12
  };

  const reservations = RESERVATIONS || {}; // dateStr -> {userId, username, color, timestamp}
  const changes = {}; // dateStr -> reservation OR null (delete)

  const $ = (id) => document.getElementById(id);

  function pad2(n) {
    return String(n).padStart(2, '0');
  }

  function monthLabel(year, month) {
    const d = new Date(year, month - 1, 1);
    return d.toLocaleString('tr-TR', { month: 'long', year: 'numeric' });
  }

  function dateStr(year, month, day) {
    return `${year}-${pad2(month)}-${pad2(day)}`;
  }

  function drawLegend() {
    const wrap = $('legend');
    wrap.innerHTML = '';

    (USERS || []).forEach((u) => {
      const item = document.createElement('div');
      item.className = 'legend-item';

      const dot = document.createElement('div');
      dot.className = 'dot';
      dot.style.background = u.color || '#4caf50';

      const name = document.createElement('div');
      name.textContent = u.username;
      name.style.fontSize = '13px';
      name.style.fontWeight = '700';

      item.appendChild(dot);
      item.appendChild(name);
      wrap.appendChild(item);
    });
  }

  function drawCalendar() {
    $('monthTitle').textContent = monthLabel(state.year, state.month);

    const grid = $('calGrid');
    grid.innerHTML = '';

    const weekdays = ['Pzt', 'Sal', 'Çar', 'Per', 'Cum', 'Cmt', 'Paz'];
    weekdays.forEach((w) => {
      const el = document.createElement('div');
      el.className = 'weekday';
      el.textContent = w;
      grid.appendChild(el);
    });

    const first = new Date(state.year, state.month - 1, 1);
    const startDow = first.getDay(); // 0 Sun ... 6 Sat
    const offset = (startDow + 6) % 7; // Monday=0

    const daysInMonth = new Date(state.year, state.month, 0).getDate();

    // leading blanks
    for (let i = 0; i < offset; i++) {
      const blank = document.createElement('div');
      blank.className = 'cal-cell disabled';
      blank.title = '';
      grid.appendChild(blank);
    }

    // days
    for (let day = 1; day <= daysInMonth; day++) {
      const ds = dateStr(state.year, state.month, day);
      const existing = reservations[ds];

      const cell = document.createElement('div');
      cell.className = 'cal-cell';

      const dayEl = document.createElement('div');
      dayEl.className = 'cal-day';
      dayEl.textContent = String(day);
      cell.appendChild(dayEl);

      if (existing) {
        const isMine = existing.userId === CURRENT_USER.id;
        cell.style.background = existing.color || 'rgba(255,255,255,0.10)';

        const meta = document.createElement('div');
        meta.className = 'cal-meta';
        meta.textContent = existing.username || '';
        cell.appendChild(meta);

        const ts = existing.timestamp ? new Date(existing.timestamp).toLocaleString('tr-TR') : '';
        cell.title = `${existing.username || ''}`;

        if (!isMine) {
          cell.classList.add('locked');
        }
      } else {
        cell.title = '';
      }

      cell.addEventListener('click', () => {
        const cur = reservations[ds];

        // someone else -> do nothing
        if (cur && cur.userId !== CURRENT_USER.id) return;

        // toggle off
        if (cur && cur.userId === CURRENT_USER.id) {
          delete reservations[ds];
          changes[ds] = null; // tell server to delete
          drawCalendar();
          setDirty(true);
          return;
        }

        // toggle on
        const entry = {
          userId: CURRENT_USER.id,
          username: CURRENT_USER.name,
          color: CURRENT_USER.color,
          timestamp: new Date().toISOString(),
        };
        reservations[ds] = entry;
        changes[ds] = entry;
        drawCalendar();
        setDirty(true);
      });

      grid.appendChild(cell);
    }

    // trailing blanks to complete grid
    const total = grid.children.length;
    const mod = total % 7;
    if (mod !== 0) {
      const add = 7 - mod;
      for (let i = 0; i < add; i++) {
        const blank = document.createElement('div');
        blank.className = 'cal-cell disabled';
        grid.appendChild(blank);
      }
    }
  }

  function renderChat() {
    const wrap = $('chatMessages');
    wrap.innerHTML = '';

    (COMMENTS || []).forEach((c) => {
      const box = document.createElement('div');
      box.className = 'msg';

      const top = document.createElement('div');
      top.className = 'msg-top';

      const left = document.createElement('div');
      left.className = 'msg-name';

      const dot = document.createElement('span');
      dot.className = 'dot';
      dot.style.width = '10px';
      dot.style.height = '10px';
      dot.style.borderWidth = '1px';
      dot.style.background = c.color || '#4caf50';

      const name = document.createElement('span');
      name.textContent = c.username || 'Kullanıcı';

      left.appendChild(dot);
      left.appendChild(name);

      const time = document.createElement('div');
      time.className = 'msg-time';
      time.textContent = c.timestamp ? new Date(c.timestamp).toLocaleString('tr-TR') : '';

      top.appendChild(left);
      top.appendChild(time);

      const text = document.createElement('div');
      text.className = 'msg-text';
      text.textContent = c.comment || '';

      box.appendChild(top);
      box.appendChild(text);
      wrap.appendChild(box);
    });

    wrap.scrollTop = wrap.scrollHeight;
  }

  function postComment() {
    const input = $('chatInput');
    const text = (input.value || '').trim();
    if (!text) return;

    // store comment under first day of visible month (server filters per month)
    const d = `${state.year}-${pad2(state.month)}-01`;

    fetch('/add_comment', {
      method: 'POST',
      headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
      body: `date=${encodeURIComponent(d)}&comment=${encodeURIComponent(text)}`,
    })
      .then((r) => r.json())
      .then((data) => {
        if (!data.success) {
          alert(data.message || STRINGS.cal_comment_fail);
          return;
        }

        COMMENTS.push({
          username: CURRENT_USER.name,
          color: CURRENT_USER.color,
          comment: text,
          timestamp: new Date().toISOString(),
        });
        input.value = '';
        renderChat();
      })
      .catch(() => alert(STRINGS.server_error));
  }

  function saveChanges() {
    const keys = Object.keys(changes);
    if (keys.length === 0) {
      alert(STRINGS.no_changes);
      return;
    }

    fetch('/save_reservations', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ changes }),
    })
      .then((r) => r.json())
      .then((data) => {
        if (!data.success) {
          alert(data.error || STRINGS.server_error);
          return;
        }

        const conflicts = data.conflicts || [];
        if (conflicts.length) {
          const lines = conflicts.map((c) => `${c.date} (${STRINGS.cal_conflict_by} ${c.by})`).join('\n');
          alert(STRINGS.cal_conflict + '\n' + lines);
        } else {
          alert(STRINGS.cal_reservation_saved);
        }

        // clear local change-set
        keys.forEach((k) => delete changes[k]);
        setDirty(false);
      })
      .catch(() => alert(STRINGS.server_error));
  }

  function goMonth(delta) {
    if (Object.keys(changes).length) {
      const ok = confirm(STRINGS.unsaved_changes);
      if (!ok) return;
    }

    let y = state.year;
    let m = state.month + delta;

    if (m <= 0) {
      m = 12;
      y -= 1;
    } else if (m >= 13) {
      m = 1;
      y += 1;
    }

    window.location.href = `/calendar?year=${y}&month=${m}`;
  }

  function setDirty(isDirty) {
    const el = $('dirtyBadge');
    el.style.display = isDirty ? 'inline-flex' : 'none';
  }

  // wire up
  document.addEventListener('DOMContentLoaded', () => {
    drawLegend();
    drawCalendar();
    renderChat();
    setDirty(false);

    $('prevBtn').addEventListener('click', () => goMonth(-1));
    $('nextBtn').addEventListener('click', () => goMonth(1));
    $('saveBtn').addEventListener('click', saveChanges);

    $('sendBtn').addEventListener('click', postComment);
    $('chatInput').addEventListener('keydown', (e) => {
      if (e.key === 'Enter') postComment();
    });

    // Logout confirm
    $('logoutLink').addEventListener('click', (e) => {
      e.preventDefault();
      const ok = confirm(STRINGS.cal_logout_confirm);
      if (ok) window.location.href = '/logout';
    });
  });
})();


// ── Year Overview ──────────────────────────────────────────────────────────
(function () {
  const MONTH_NAMES_TR = ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran',
                          'Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık'];
  const MONTH_NAMES_EN = ['January','February','March','April','May','June',
                          'July','August','September','October','November','December'];
  const MONTH_NAMES_DE = ['Januar','Februar','März','April','Mai','Juni',
                          'Juli','August','September','Oktober','November','Dezember'];
  const WD_TR = ['Pt','Sa','Ça','Pe','Cu','Ct','Pz'];
  const WD_EN = ['Mo','Tu','We','Th','Fr','Sa','Su'];
  const WD_DE = ['Mo','Di','Mi','Do','Fr','Sa','So'];

  function getLang() {
    return (typeof STRINGS !== 'undefined' && STRINGS._lang) || 'tr';
  }
  function monthNames() {
    const l = getLang();
    return l === 'de' ? MONTH_NAMES_DE : l === 'en' ? MONTH_NAMES_EN : MONTH_NAMES_TR;
  }
  function wdNames() {
    const l = getLang();
    return l === 'de' ? WD_DE : l === 'en' ? WD_EN : WD_TR;
  }

  let yearViewYear = INITIAL_YEAR;
  let yearData     = {};  // date -> {color, username}

  function pad2(n) { return String(n).padStart(2, '0'); }

  async function loadYearData(year) {
    yearViewYear = year;
    document.getElementById('yearNavLabel').textContent = year;
    document.getElementById('yearGrid').innerHTML =
      '<div style="grid-column:1/-1;padding:30px;text-align:center;color:var(--muted)">Yükleniyor…</div>';
    try {
      const r = await fetch(`/api/year_reservations?year=${year}`);
      const j = await r.json();
      yearData = j.success ? j.reservations : {};
      renderYearGrid(year);
    } catch(e) {
      document.getElementById('yearGrid').innerHTML =
        '<div style="grid-column:1/-1;padding:20px;text-align:center;color:#ef4444">Yüklenemedi.</div>';
    }
  }

  function renderYearGrid(year) {
    const grid   = document.getElementById('yearGrid');
    const legend = document.getElementById('yearLegend');
    const names  = monthNames();
    const wds    = wdNames();
    const today  = new Date();
    const todayStr = `${today.getFullYear()}-${pad2(today.getMonth()+1)}-${pad2(today.getDate())}`;

    grid.innerHTML = '';

    // Collect users for legend
    const usersMap = {};
    Object.values(yearData).forEach(v => { usersMap[v.username] = v.color; });

    // Legend
    legend.innerHTML = Object.entries(usersMap).map(([name, color]) =>
      `<div class="year-legend-item">
        <div class="year-legend-dot" style="background:${color}"></div>
        <span>${name}</span>
      </div>`
    ).join('');

    for (let m = 1; m <= 12; m++) {
      const daysInMonth = new Date(year, m, 0).getDate();
      const firstDow    = (new Date(year, m-1, 1).getDay() + 6) % 7; // Mon=0
      const monthKey    = `${year}-${pad2(m)}`;

      const box = document.createElement('div');
      box.className = 'mini-month';

      // Month name — clickable to jump to that month
      const nameEl = document.createElement('div');
      nameEl.className = 'mini-month-name';
      nameEl.textContent = names[m-1];
      nameEl.title = 'Bu aya git';
      nameEl.addEventListener('click', () => {
        closeYearView();
        window.location.href = `/calendar?year=${year}&month=${m}`;
      });
      box.appendChild(nameEl);

      // Mini grid
      const calEl = document.createElement('div');
      calEl.className = 'mini-cal';

      // Weekday headers
      wds.forEach(w => {
        const wd = document.createElement('div');
        wd.className = 'mini-wd';
        wd.textContent = w;
        calEl.appendChild(wd);
      });

      // Blanks
      for (let b = 0; b < firstDow; b++) {
        const blank = document.createElement('div');
        blank.className = 'mini-cell blank';
        calEl.appendChild(blank);
      }

      // Days
      for (let d = 1; d <= daysInMonth; d++) {
        const ds   = `${year}-${pad2(m)}-${pad2(d)}`;
        const res  = yearData[ds];
        const cell = document.createElement('div');
        cell.className = 'mini-cell ' + (res ? 'reserved' : 'free');
        if (ds === todayStr) cell.classList.add('today-cell');
        cell.textContent = d;
        if (res) {
          cell.style.background = res.color || '#3b82f6';
          cell.title = res.username;
        }
        calEl.appendChild(cell);
      }

      box.appendChild(calEl);
      grid.appendChild(box);
    }
  }

  function openYearView() {
    document.getElementById('yearOverlay').classList.add('open');
    loadYearData(yearViewYear);
  }

  function closeYearView() {
    document.getElementById('yearOverlay').classList.remove('open');
  }

  document.addEventListener('DOMContentLoaded', () => {
    const btn = document.getElementById('yearViewBtn');
    if (btn) btn.addEventListener('click', openYearView);

    const closeBtn = document.getElementById('yearClose');
    if (closeBtn) closeBtn.addEventListener('click', closeYearView);

    const overlay = document.getElementById('yearOverlay');
    if (overlay) overlay.addEventListener('click', e => {
      if (e.target === overlay) closeYearView();
    });

    const prevBtn = document.getElementById('yearPrev');
    if (prevBtn) prevBtn.addEventListener('click', () => loadYearData(yearViewYear - 1));

    const nextBtn = document.getElementById('yearNext');
    if (nextBtn) nextBtn.addEventListener('click', () => loadYearData(yearViewYear + 1));

    // Esc to close
    document.addEventListener('keydown', e => {
      if (e.key === 'Escape') closeYearView();
    });
  });
})();
