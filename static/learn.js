/* ══ PPL(A) Lernplattform – learn.js ══════════════════════════════════════
   API-driven: all content comes from /api/learn/* (SQLite DB)
   No static ppl_data.js dependency for content – only quiz logic here.
   ═══════════════════════════════════════════════════════════════════════ */
'use strict';

const LETTERS = ['A','B','C','D','E','F'];

/* ── Shuffle answer options, keeping answer index in sync ─────────────── */
function shuffleOptions(q) {
  const opts   = q.options.slice();
  const correct = opts[q.answer]; // remember the correct text
  // Fisher-Yates shuffle
  for (let i = opts.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    [opts[i], opts[j]] = [opts[j], opts[i]];
  }
  return { ...q, options: opts, answer: opts.indexOf(correct) };
}


/* ── State ──────────────────────────────────────────────────────────────── */
const state = {
  subjects:   [],          // from API
  activeSubj: null,        // subject id
  chapters:   [],          // chapters for active subject
  scores:     {},          // { chapterId: { correct, wrong, wrong_q_ids[] } }
  tocData:    [],          // full TOC
  loaded:     false,
};

/* ── Init ───────────────────────────────────────────────────────────────── */
async function init() {
  await Promise.all([loadScores(), loadSubjects()]);
  renderSubjectList();
  renderGlobalStats();
  initSearch();
  updateWrongBtn();
  loadTOC();
  initKeyboardShortcut();
}

/* ── API helpers ────────────────────────────────────────────────────────── */
async function apiFetch(url, opts) {
  try {
    const r = await fetch(url, opts);
    return await r.json();
  } catch(e) { return { success: false, error: String(e) }; }
}

/* ── Score persistence ──────────────────────────────────────────────────── */
async function loadScores() {
  const j = await apiFetch('/api/quiz/scores');
  if (j.success) state.scores = j.scores || {};
  state.loaded = true;
}

async function saveScore(chapterId, correct, wrong, wrongIds) {
  state.scores[chapterId] = { correct, wrong, wrong_q_ids: wrongIds };
  renderGlobalStats();
  renderSubjectList();
  updateWrongBtn();
  updateHeroNums();
  refreshTOCScores();
  await apiFetch('/api/quiz/save', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chapter_id: chapterId, correct, wrong, wrong_q_ids: wrongIds })
  });
}

async function resetChapterScore(chapterId) {
  delete state.scores[chapterId];
  renderGlobalStats();
  renderSubjectList();
  updateWrongBtn();
  updateHeroNums();
  refreshTOCScores();
  await apiFetch('/api/quiz/reset', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ chapter_id: chapterId })
  });
}

/* ── Subjects ───────────────────────────────────────────────────────────── */
async function loadSubjects() {
  const j = await apiFetch('/api/learn/subjects');
  if (j.success) {
    state.subjects = j.subjects || [];
  }
}

function renderSubjectList() {
  const wrap = document.getElementById('subjList');
  if (!wrap) return;
  wrap.innerHTML = '';

  if (!state.subjects.length) {
    document.getElementById('sbWelcome')?.style.setProperty('display', '');
    document.getElementById('emptyState')?.style.setProperty('display', '');
    updateHeroNums();
    return;
  }

  document.getElementById('sbWelcome')?.style.setProperty('display', 'none');
  document.getElementById('emptyState')?.style.setProperty('display', 'none');

  state.subjects.forEach(s => {
    const btn = document.createElement('button');
    btn.className = 'subj-btn' + (s.id === state.activeSubj ? ' active' : '');
    const prog = subjectProgressStr(s);
    btn.innerHTML = `
      <span class="subj-icon">${s.icon}</span>
      <span class="subj-info">
        <div class="subj-nm">${escHtml(s.title)}</div>
        <div class="subj-cd">Fach ${s.code} · ${s.chapter_count} Kapitel</div>
      </span>
      <span class="subj-prog">${prog}</span>`;
    btn.addEventListener('click', () => {
      state.activeSubj = s.id;
      renderSubjectList();
      loadAndRenderSubject(s.id);
      window.scrollTo({ top: 0, behavior: 'smooth' });
    });
    wrap.appendChild(btn);
  });

  updateHeroNums();
}

function subjectProgressStr(s) {
  if (!s.chapter_count) return '–';
  // Count chapters with scores
  let done = 0;
  // We don't have per-chapter IDs here easily, so count score keys matching subject prefix
  // Best effort: use quiz_count vs answered
  return `${s.chapter_count} Kap.`;
}

/* ── Load + Render subject ──────────────────────────────────────────────── */
async function loadAndRenderSubject(subjectId) {
  const main = document.getElementById('chaptersWrap');
  if (main) main.innerHTML = '<div class="ch-body-loading"><div class="spinner"></div> Kapitel werden geladen…</div>';

  const j = await apiFetch(`/api/learn/subject/${subjectId}`);
  if (!j.success) {
    if (main) main.innerHTML = `<div class="quiz-empty">Fehler beim Laden: ${escHtml(j.error || 'Unbekannt')}</div>`;
    return;
  }

  const subj    = j.subject;
  const chapters = j.chapters || [];
  state.chapters = chapters;

  // Update overview card
  setText('sovIcon',    subj.icon);
  setText('sovTitle',   subj.title);
  setText('sovMeta',    `Fach ${subj.code} · ${chapters.length} Kapitel`);
  const sovOv = document.getElementById('sovOverview');
  if (sovOv) sovOv.textContent = subj.overview || '';

  // Render chapters
  if (main) {
    main.innerHTML = '';
    if (!chapters.length) {
      main.innerHTML = '<div class="quiz-empty">Noch keine Kapitel für dieses Fach vorhanden.</div>';
      return;
    }
    chapters.forEach((ch, idx) => {
      main.appendChild(buildChapterCard(ch, idx + 1));
    });
  }
}

/* ── Chapter card (skeleton) ────────────────────────────────────────────── */
function buildChapterCard(ch, num) {
  const sc = state.scores[ch.id] || null;
  const hasScore = sc && (sc.correct + sc.wrong) > 0;
  const pct = hasScore ? Math.round(sc.correct / (sc.correct + sc.wrong) * 100) : null;

  const card = document.createElement('article');
  card.className = 'ch-card' + (hasScore ? (pct >= 70 ? ' scored' : ' scored-bad') : '');
  card.id = 'ch-' + ch.id;

  let scoreTag = '';
  if (hasScore) {
    const cls = pct >= 70 ? 'g' : 'b';
    scoreTag = `<span class="ch-score-tag ${cls}">${pct}% (${sc.correct}✓ ${sc.wrong}✗)</span>`;
  }
  const examTag = ch.exam_relevant ? `<span class="exam-tag">⭐ Prüfungsrelevant</span>` : '';
  const qCount  = ch.quiz_count ? `<span>${ch.quiz_count} Quizfragen</span>` : '<span>Quizfragen werden geladen</span>';

  card.innerHTML = `
    <button class="ch-toggle" type="button">
      <div class="ch-num">${num}</div>
      <div class="ch-info">
        <div class="ch-tit">${escHtml(ch.title)}</div>
        <div class="ch-sub">${examTag}${scoreTag}${qCount}</div>
      </div>
      <svg class="ch-chevron" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="6 9 12 15 18 9"/></svg>
    </button>
    <div class="ch-body">
      <div class="ch-body-loading"><div class="spinner"></div> Inhalt wird geladen…</div>
    </div>`;

  card.querySelector('.ch-toggle').addEventListener('click', () => {
    const isOpen = card.classList.toggle('open');
    if (isOpen) loadAndRenderChapterBody(card, ch.id);
  });

  return card;
}

/* ── Load + render chapter body ─────────────────────────────────────────── */
async function loadAndRenderChapterBody(card, chapterId) {
  const body = card.querySelector('.ch-body');
  if (!body || body.dataset.rendered) return;
  body.dataset.rendered = '1';

  const j = await apiFetch(`/api/learn/chapter/${chapterId}`);
  if (!j.success) {
    body.innerHTML = `<p style="color:var(--muted);padding:16px 0;">Fehler beim Laden des Kapitels.</p>`;
    return;
  }

  const ch   = j.chapter;
  // Use sections_raw (ordered) when available, fall back to grouped sections
  const sectionsData = (j.sections_raw && j.sections_raw.length) ? j.sections_raw : j.sections;
  const quiz = j.quiz;

  // Also load flashcards
  const jfc = await apiFetch(`/api/learn/flashcards/${chapterId}`);
  const flashcards = (jfc && jfc.success) ? jfc.flashcards : [];

  body.innerHTML = buildChapterBodyHTML(ch, sectionsData) + buildFlashcardSectionHTML(ch, flashcards) + buildQuizSectionHTML(ch, quiz);

  // Attach quiz handlers
  attachQuizHandlers(card, ch, quiz);
  // Attach flashcard handlers
  attachFlashcardHandlers(card);
}

/* ── Chapter body HTML ──────────────────────────────────────────────────── */
function buildChapterBodyHTML(ch, secsData) {
  // secsData is either:
  //   Array (sections_raw) → new ordered format with headings/diagrams
  //   Object (sections)    → old grouped format {summaries:[], facts:[], ...}

  if (Array.isArray(secsData)) {
    return buildChapterBodyFromRaw(ch, secsData);
  } else {
    return buildChapterBodyFromGrouped(ch, secsData);
  }
}

/* New renderer: processes sections in document order */
function buildChapterBodyFromRaw(ch, secs) {
  if (!secs || !secs.length) {
    return '<div class="ch-content"><p class="sec-text sec-muted">Kein Inhalt verfügbar.</p></div>';
  }

  let html = '<div class="ch-content">';
  let i = 0;

  while (i < secs.length) {
    const s = secs[i];

    // Group consecutive table_row entries into a table
    if (s.type === 'table_row') {
      let rows = [];
      while (i < secs.length && secs[i].type === 'table_row') {
        rows.push(secs[i]);
        i++;
      }
      html += buildInlineTableHTML(rows);
      continue;
    }

    switch (s.type) {
      case 'heading':
        html += `<div class="sec-heading"><h2>${escHtml(s.content)}</h2>${s.extra ? `<p class="sec-heading-sub">${escHtml(s.extra)}</p>` : ''}</div>`;
        break;
      case 'subheading':
        html += `<div class="sec-subheading"><h3>${escHtml(s.content)}</h3></div>`;
        break;
      case 'text':
      case 'summary':
        html += `<p class="sec-text">${escHtml(s.content)}</p>`;
        break;
      case 'fact':
        html += `<div class="sec-fact"><div class="sec-icon-box">🔑</div><div class="sec-fact-body">${escHtml(s.content)}</div></div>`;
        break;
      case 'focus':
        html += `<div class="sec-focus"><div class="sec-icon-box">⭐</div><div><div class="sec-focus-label">Prüfungsschwerpunkt</div>${escHtml(s.content)}</div></div>`;
        break;
      case 'warning':
        html += `<div class="sec-warning"><div class="sec-icon-box">⚠️</div><div>${escHtml(s.content)}</div></div>`;
        break;
      case 'infobox':
        html += `<div class="sec-infobox"><div class="sec-icon-box">ℹ️</div><div>${s.extra ? `<strong>${escHtml(s.extra)}</strong><br>` : ''}${escHtml(s.content)}</div></div>`;
        break;
      case 'diagram':
        // Raw SVG – NOT escaped. Content is trusted (generated by us).
        html += `<div class="sec-diagram">${s.content}${s.extra ? `<div class="diag-caption">${escHtml(s.extra)}</div>` : ''}</div>`;
        break;
      default:
        if (s.content) html += `<p class="sec-text">${escHtml(s.content)}</p>`;
    }
    i++;
  }

  html += '</div>';
  return html;
}

function buildInlineTableHTML(rows) {
  return `
    <div class="sec-table-wrap">
      <table class="sec-table">
        <thead><tr><th>Begriff / Kürzel</th><th>Bedeutung &amp; Anwendung</th></tr></thead>
        <tbody>${rows.map(r => `<tr><td>${escHtml(r.content)}</td><td>${escHtml(r.extra || '')}</td></tr>`).join('')}</tbody>
      </table>
    </div>`;
}

/* Legacy renderer for old grouped-format chapters */
function buildChapterBodyFromGrouped(ch, secs) {
  let focusHtml = '';
  if (secs.focuses && secs.focuses.length) {
    focusHtml = `<div class="sec-focus" style="margin-bottom:18px"><div class="sec-icon-box">⭐</div><div><div class="sec-focus-label">Prüfungsschwerpunkte</div><ul class="sec-legacy-list">${secs.focuses.map(f => `<li>${escHtml(f)}</li>`).join('')}</ul></div></div>`;
  }
  const summaryHtml = (secs.summaries || []).map(p => `<p class="sec-text">${escHtml(p)}</p>`).join('');
  let tableHtml = '';
  if (secs.tables && secs.tables.length) {
    tableHtml = buildInlineTableHTML(secs.tables.map(r => ({content: r[0], extra: r[1]})));
  }
  let factHtml = '';
  if (secs.facts && secs.facts.length) {
    factHtml = `<div class="sec-fact" style="margin-top:18px"><div class="sec-icon-box">🔑</div><div class="sec-fact-body"><ul class="sec-legacy-list">${secs.facts.map(f => `<li>${escHtml(f)}</li>`).join('')}</ul></div></div>`;
  }
  const vizHtml = buildVisualization(ch.id);
  return `<div class="ch-content">${focusHtml}${summaryHtml}${tableHtml}${vizHtml}${factHtml}</div>`;
}


/* ── Flashcard section HTML ──────────────────────────────────────────────── */
function buildFlashcardSectionHTML(ch, cards) {
  if (!cards || !cards.length) return '';

  const cardsHtml = cards.map((c, i) => `
    <div class="fc-card" data-idx="${i}" data-flipped="0" onclick="flipCard(this)">
      <div class="fc-inner">
        <div class="fc-front">
          <div class="fc-label">Frage</div>
          <div class="fc-text">${escHtml(c.front)}</div>
          <div class="fc-hint">Tippen zum Umdrehen ↻</div>
        </div>
        <div class="fc-back">
          <div class="fc-label">Antwort</div>
          <div class="fc-text">${escHtml(c.back)}</div>
          <div class="fc-hint">Tippen zum Zurückdrehen ↺</div>
        </div>
      </div>
    </div>`).join('');

  return `
    <div class="fc-section" id="fc-${ch.id}">
      <div class="fc-hdr">
        <div class="fc-hdr-left">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><rect x="2" y="4" width="20" height="16" rx="2"/><path d="M12 4v16M2 12h20"/></svg>
          <h3>Lernkarten</h3>
          <span class="fc-count-badge">${cards.length} Karten</span>
        </div>
        <div class="fc-nav-row">
          <button class="fc-btn" onclick="fcPrev('${ch.id}')">‹ Zurück</button>
          <span class="fc-pos" id="fcPos-${ch.id}">1 / ${cards.length}</span>
          <button class="fc-btn" onclick="fcNext('${ch.id}')">Weiter ›</button>
        </div>
        <div class="fc-acts">
          <button class="fc-btn fc-btn-shuffle" onclick="fcShuffle('${ch.id}')">🔀 Mischen</button>
          <button class="fc-btn fc-btn-reset" onclick="fcResetAll('${ch.id}')">↺ Alle zeigen</button>
        </div>
      </div>
      <div class="fc-viewport" id="fcView-${ch.id}">
        <div class="fc-track" id="fcTrack-${ch.id}">
          ${cardsHtml}
        </div>
      </div>
      <div class="fc-progress">
        <div class="fc-prog-bar" id="fcProg-${ch.id}" style="width:${Math.round(100/cards.length)}%"></div>
      </div>
    </div>`;
}

function attachFlashcardHandlers(card) {
  // State per chapter – stored on the track element
  const tracks = card.querySelectorAll('.fc-track');
  tracks.forEach(track => {
    track.dataset.current = '0';
    updateFcDisplay(track);
  });
}

function flipCard(cardEl) {
  const flipped = cardEl.dataset.flipped === '1';
  cardEl.dataset.flipped = flipped ? '0' : '1';
  cardEl.classList.toggle('is-flipped', !flipped);
}

function getFcTrack(chapterId) {
  return document.getElementById('fcTrack-' + chapterId);
}

function updateFcDisplay(track) {
  const chId = track.id.replace('fcTrack-', '');
  const cards = track.querySelectorAll('.fc-card');
  const cur = parseInt(track.dataset.current || '0');
  const total = cards.length;

  // Hide all, show current
  cards.forEach((c, i) => {
    c.style.display = i === cur ? 'block' : 'none';
    // Reset flip when switching
    if (i !== cur) { c.dataset.flipped = '0'; c.classList.remove('is-flipped'); }
  });

  // Update position label
  const pos = document.getElementById('fcPos-' + chId);
  if (pos) pos.textContent = `${cur + 1} / ${total}`;

  // Update progress bar
  const prog = document.getElementById('fcProg-' + chId);
  if (prog) prog.style.width = Math.round(((cur + 1) / total) * 100) + '%';
}

function fcNext(chapterId) {
  const track = getFcTrack(chapterId);
  if (!track) return;
  const total = track.querySelectorAll('.fc-card').length;
  const cur = parseInt(track.dataset.current || '0');
  track.dataset.current = String((cur + 1) % total);
  updateFcDisplay(track);
}

function fcPrev(chapterId) {
  const track = getFcTrack(chapterId);
  if (!track) return;
  const total = track.querySelectorAll('.fc-card').length;
  const cur = parseInt(track.dataset.current || '0');
  track.dataset.current = String((cur - 1 + total) % total);
  updateFcDisplay(track);
}

function fcShuffle(chapterId) {
  const track = getFcTrack(chapterId);
  if (!track) return;
  const cards = [...track.querySelectorAll('.fc-card')];
  // Fisher-Yates shuffle
  for (let i = cards.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1));
    track.appendChild(cards[j]);
    cards.splice(j, 1, cards[i]);
  }
  track.dataset.current = '0';
  updateFcDisplay(track);
}

function fcResetAll(chapterId) {
  const track = getFcTrack(chapterId);
  if (!track) return;
  track.dataset.current = '0';
  updateFcDisplay(track);
}

/* ── Quiz section HTML ──────────────────────────────────────────────────── */
function buildQuizSectionHTML(ch, quiz) {
  const sc    = state.scores[ch.id] || { correct: 0, wrong: 0, wrong_q_ids: [] };
  const noQiz = !quiz || !quiz.length;

  if (noQiz) {
    return `<div class="quiz-section">
      <div class="quiz-empty">Für dieses Kapitel sind noch keine Quizfragen vorhanden.</div>
    </div>`;
  }

  const officialCount = quiz.filter(q => q.is_official).length;
  const officialBadge = officialCount > 0
    ? `<span class="quiz-official-badge">★ ${officialCount} offizielle Prüfungsfragen</span>` : '';

  return `
    <div class="quiz-section" id="quiz-${ch.id}">
      <div class="quiz-hdr">
        <div class="quiz-hdr-left">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
          <h3>Kapitelquiz</h3>
          ${officialBadge}
        </div>
        <div class="quiz-score-row">
          <span class="qs-ok">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polyline points="20 6 9 17 4 12"/></svg>
            <span id="qcOk-${ch.id}">${sc.correct}</span> richtig
          </span>
          <span class="qs-err${sc.wrong === 0 ? ' hidden' : ''}" id="qcErr-${ch.id}-wrap" onclick="openWrongModalForChapter('${ch.id}')">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>
            <span id="qcErr-${ch.id}">${sc.wrong}</span> falsch – wiederholen
          </span>
        </div>
        <div class="quiz-acts">
          <button class="btn-reset" onclick="resetQuizChapter('${ch.id}')">↺ Zurücksetzen</button>
        </div>
      </div>
      <div class="qprog-row">
        <span class="qprog-txt" id="qpTxt-${ch.id}">0/${quiz.length} beantwortet</span>
        <div class="qprog-bg"><div class="qprog-fg" id="qpFg-${ch.id}" style="width:0%"></div></div>
      </div>
      <div id="qlist-${ch.id}"></div>
    </div>`;
}

/* ── Attach quiz event handlers ─────────────────────────────────────────── */
function attachQuizHandlers(card, ch, quiz) {
  if (!quiz || !quiz.length) return;
  const container = card.querySelector('.quiz-section');
  if (!container) return;

  const answered = {}; // qi → chosen oi

  // Shuffle questions
  const shuffled = quiz.map((q, i) => ({ ...q, origIdx: i })).sort(() => Math.random() - 0.5).map(shuffleOptions);

  const qlist = container.querySelector(`#qlist-${ch.id}`);
  if (!qlist) return;

  shuffled.forEach((q, i) => {
    const qcard = document.createElement('div');
    qcard.className = 'q-card';
    qcard.id = `qcard-${ch.id}-${i}`;

    const officialDot = q.is_official
      ? `<span class="q-official-dot" title="Offizielle Prüfungsfrage"></span>` : '';

    qcard.innerHTML = `
      <div class="q-lbl">Frage ${i + 1} / ${shuffled.length} ${officialDot}</div>
      <p class="q-txt">${escHtml(q.q)}</p>
      ${q.image_path ? `<img src="/static/${q.image_path}" class="q-img" alt="Siehe Bild" title="Klicken zum Vergr\u00f6\u00dfern">` : ''}
      <div class="ans-list" id="ans-${ch.id}-${i}">
        ${q.options.map((opt, oi) => `
          <button type="button" class="ans-btn" data-qi="${i}" data-oi="${oi}" data-correct="${q.answer}">
            <span class="ans-prefix">${LETTERS[oi]}.</span>
            <span>${escHtml(opt)}</span>
          </button>`).join('')}
      </div>
      <div class="expl" id="expl-${ch.id}-${i}">
        <span class="expl-ico">
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="12" y1="16" x2="12" y2="12"/><line x1="12" y1="8" x2="12.01" y2="8"/></svg>
        </span>
        <span class="expl-text">${escHtml(q.explanation || '')}</span>
      </div>`;

    qlist.appendChild(qcard);

    // Answer events
    qcard.querySelectorAll('.ans-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const qi  = parseInt(btn.dataset.qi);
        const oi  = parseInt(btn.dataset.oi);
        if (answered[qi] !== undefined) return;

        const correctIdx = parseInt(btn.dataset.correct);
        answered[qi] = oi;

        qcard.querySelectorAll('.ans-btn').forEach(b => {
          b.classList.add('locked');
          const boi = parseInt(b.dataset.oi);
          if (boi === correctIdx) b.classList.add('correct');
          if (boi === oi && oi !== correctIdx) b.classList.add('wrong');
        });

        const expl = qcard.querySelector(`#expl-${ch.id}-${qi}`);
        if (expl) expl.classList.add('show');

        updateQuizScore(card, ch, shuffled, answered, container);
      });
    });
  });
}

function updateQuizScore(card, ch, shuffled, answered, container) {
  let correct = 0, wrong = 0;
  const wrongIds = [];
  shuffled.forEach((q, i) => {
    if (answered[i] !== undefined) {
      if (answered[i] === q.answer) correct++;
      else { wrong++; wrongIds.push(q.id); }
    }
  });

  const answeredCount = Object.keys(answered).length;
  const total         = shuffled.length;

  // Progress bar
  const pTxt = document.getElementById(`qpTxt-${ch.id}`);
  const pFg  = document.getElementById(`qpFg-${ch.id}`);
  if (pTxt) pTxt.textContent = `${answeredCount}/${total} beantwortet`;
  if (pFg)  pFg.style.width  = (answeredCount / total * 100) + '%';

  // Score display
  setText(`qcOk-${ch.id}`, correct);
  setText(`qcErr-${ch.id}`, wrong);
  const errWrap = document.getElementById(`qcErr-${ch.id}-wrap`);
  if (errWrap) errWrap.classList.toggle('hidden', wrong === 0);

  // Chapter header score tag
  if (answeredCount === total) {
    const pct = Math.round(correct / total * 100);
    const sub = card.querySelector('.ch-sub');
    if (sub) {
      const oldTag = sub.querySelector('.ch-score-tag');
      if (oldTag) oldTag.remove();
      const tag = document.createElement('span');
      tag.className = 'ch-score-tag ' + (pct >= 70 ? 'g' : 'b');
      tag.textContent = `${pct}% (${correct}✓ ${wrong}✗)`;
      sub.prepend(tag);
      card.classList.remove('scored','scored-bad');
      card.classList.add(pct >= 70 ? 'scored' : 'scored-bad');
    }
  }

  saveScore(ch.id, correct, wrong, wrongIds);
}

/* ── Reset chapter quiz ─────────────────────────────────────────────────── */
window.resetQuizChapter = async function(chapterId) {
  await resetChapterScore(chapterId);
  const card = document.getElementById('ch-' + chapterId);
  if (!card) return;
  const body = card.querySelector('.ch-body');
  if (body) {
    delete body.dataset.rendered;
    body.innerHTML = '<div class="ch-body-loading"><div class="spinner"></div> Wird neu geladen…</div>';
    loadAndRenderChapterBody(card, chapterId);
  }
  // update header score tag
  const sub = card.querySelector('.ch-sub');
  if (sub) {
    const oldTag = sub.querySelector('.ch-score-tag');
    if (oldTag) oldTag.remove();
    card.classList.remove('scored','scored-bad');
  }
};

/* ── Global stats ───────────────────────────────────────────────────────── */
function renderGlobalStats() {
  let totalC = 0, totalW = 0, totalCh = 0;
  Object.values(state.scores).forEach(sc => {
    totalC  += sc.correct || 0;
    totalW  += sc.wrong   || 0;
    if ((sc.correct + sc.wrong) > 0) totalCh++;
  });
  setText('stCorrect', totalC);
  setText('stWrong',   totalW);
  const total = totalC + totalW;
  const pct   = total > 0 ? Math.round(totalC / total * 100) : 0;
  setText('stPct', total > 0 ? pct + '%' : '–%');
  const bar = document.getElementById('progBar');
  if (bar) bar.style.width = pct + '%';
  setText('progLbl', `${totalCh} Kapitel bewertet`);
}

function updateHeroNums() {
  let totalC = 0, totalW = 0;
  Object.values(state.scores).forEach(sc => { totalC += sc.correct||0; totalW += sc.wrong||0; });
  const total = totalC + totalW;
  const pct   = total > 0 ? Math.round(totalC/total*100) : 0;
  let totalQ = 0, chCount = 0;
  state.subjects.forEach(s => { totalQ += (s.quiz_count||0); chCount += (s.chapter_count||0); });
  setText('heroSubj',  state.subjects.length || '–');
  setText('heroChap',  chCount || '–');
  setText('heroQ',     totalQ  || '–');
  setText('heroScore', total > 0 ? pct + '%' : '–%');
}

function updateWrongBtn() {
  let wrongCount = 0;
  Object.values(state.scores).forEach(sc => {
    wrongCount += (sc.wrong_q_ids || []).length;
  });
  const btn = document.getElementById('btnWrong');
  const cnt = document.getElementById('wrongCount');
  if (btn) btn.style.display = wrongCount > 0 ? '' : 'none';
  if (cnt) cnt.textContent = wrongCount;
}

/* ── TOC ────────────────────────────────────────────────────────────────── */
async function loadTOC() {
  const j = await apiFetch('/api/learn/toc');
  if (!j.success) return;
  state.tocData = j.toc || [];
  renderTOC(state.tocData);
}

function renderTOC(data) {
  const body = document.getElementById('tocBody');
  if (!body) return;
  if (!data.length) {
    body.innerHTML = '<div class="toc-loading" style="color:var(--muted)">Noch keine Inhalte vorhanden.</div>';
    return;
  }
  body.innerHTML = '';
  data.forEach(subj => {
    const div = document.createElement('div');
    div.className = 'toc-subj';
    div.dataset.subjId = subj.id;

    div.innerHTML = `
      <div class="toc-subj-hdr">
        <span class="toc-subj-icon">${subj.icon}</span>
        <span class="toc-subj-nm">${escHtml(subj.title)}</span>
        <span class="toc-subj-chev">▶</span>
      </div>
      <div class="toc-chapters">
        ${(subj.chapters||[]).map(ch => {
          const sc  = state.scores[ch.id];
          const has = sc && (sc.correct + sc.wrong) > 0;
          const pct = has ? Math.round(sc.correct/(sc.correct+sc.wrong)*100) : null;
          const cls = has ? (pct >= 70 ? 'scored-ok' : 'scored-bad') : '';
          const scoreStr = has ? `<span class="toc-ch-score">${pct}%</span>` : '';
          const examStr  = ch.exam_relevant ? `<span class="toc-ch-exam">⭐</span>` : '';
          return `
            <button class="toc-ch-btn ${cls}" data-chapter-id="${ch.id}" data-subject-id="${subj.id}">
              ${examStr}
              <span class="toc-ch-title">${escHtml(ch.title)}</span>
              ${scoreStr}
            </button>`;
        }).join('')}
      </div>`;

    // Toggle subject expand
    div.querySelector('.toc-subj-hdr').addEventListener('click', () => {
      div.classList.toggle('open');
    });

    // Chapter navigation
    div.querySelectorAll('.toc-ch-btn').forEach(btn => {
      btn.addEventListener('click', async () => {
        const chId   = btn.dataset.chapterId;
        const subjId = btn.dataset.subjectId;
        closeTOC();

        // Switch subject if needed
        if (state.activeSubj !== subjId) {
          state.activeSubj = subjId;
          renderSubjectList();
          await loadAndRenderSubject(subjId);
        }

        // Scroll to chapter + open it
        setTimeout(() => {
          const card = document.getElementById('ch-' + chId);
          if (card) {
            card.scrollIntoView({ behavior: 'smooth', block: 'start' });
            if (!card.classList.contains('open')) {
              card.querySelector('.ch-toggle')?.click();
            }
          }
        }, 300);
      });
    });

    body.appendChild(div);
  });
}

function refreshTOCScores() {
  document.querySelectorAll('.toc-ch-btn').forEach(btn => {
    const chId = btn.dataset.chapterId;
    const sc   = state.scores[chId];
    const has  = sc && (sc.correct + sc.wrong) > 0;
    const pct  = has ? Math.round(sc.correct/(sc.correct+sc.wrong)*100) : null;
    btn.classList.remove('scored-ok','scored-bad');
    if (has) btn.classList.add(pct >= 70 ? 'scored-ok' : 'scored-bad');
    let scoreSpan = btn.querySelector('.toc-ch-score');
    if (has) {
      if (!scoreSpan) { scoreSpan = document.createElement('span'); scoreSpan.className = 'toc-ch-score'; btn.appendChild(scoreSpan); }
      scoreSpan.textContent = pct + '%';
    } else if (scoreSpan) {
      scoreSpan.remove();
    }
  });
}

window.openTOC = function() {
  document.getElementById('tocOverlay')?.classList.add('open');
  document.getElementById('tocPanel')?.classList.add('open');
};
window.closeTOC = function() {
  document.getElementById('tocOverlay')?.classList.remove('open');
  document.getElementById('tocPanel')?.classList.remove('open');
};

window.filterTOC = function(q) {
  const qLow = q.toLowerCase().trim();
  document.querySelectorAll('.toc-subj').forEach(subjDiv => {
    let anyVisible = false;
    subjDiv.querySelectorAll('.toc-ch-btn').forEach(btn => {
      const title = btn.querySelector('.toc-ch-title')?.textContent?.toLowerCase() || '';
      const match = !qLow || title.includes(qLow);
      btn.classList.toggle('toc-hidden', !match);
      if (match) anyVisible = true;
    });
    subjDiv.classList.toggle('toc-hidden', !anyVisible && qLow.length > 0);
    if (qLow && anyVisible) subjDiv.classList.add('open');
  });
};

/* ── Search ─────────────────────────────────────────────────────────────── */
function initSearch() {
  const input   = document.getElementById('searchInput');
  const results = document.getElementById('searchResults');
  if (!input || !results) return;

  let debounce;
  input.addEventListener('input', () => {
    clearTimeout(debounce);
    debounce = setTimeout(async () => {
      const q = input.value.trim();
      results.innerHTML = '';
      if (!q || q.length < 2) return;

      const j = await apiFetch(`/api/learn/search?q=${encodeURIComponent(q)}`);
      if (!j.success || !j.results.length) {
        results.innerHTML = '<div class="sr-empty">Keine Treffer.</div>';
        return;
      }

      j.results.forEach(hit => {
        const div = document.createElement('div');
        div.className = 'sr-item';
        div.innerHTML = `
          <div class="sr-subj">${escHtml(hit.subject_title)}</div>
          <div class="sr-chap">${escHtml(hit.chapter_title)}</div>`;
        div.addEventListener('click', async () => {
          input.value = '';
          results.innerHTML = '';
          // Navigate
          if (state.activeSubj !== hit.subject_id) {
            state.activeSubj = hit.subject_id;
            renderSubjectList();
            await loadAndRenderSubject(hit.subject_id);
          }
          setTimeout(() => {
            const card = document.getElementById('ch-' + hit.chapter_id);
            if (card) {
              card.scrollIntoView({ behavior: 'smooth', block: 'start' });
              if (!card.classList.contains('open')) {
                card.querySelector('.ch-toggle')?.click();
              }
            }
          }, 300);
        });
        results.appendChild(div);
      });
    }, 200);
  });
}

/* ── Keyboard shortcut Cmd/Ctrl+K → focus search ───────────────────────── */
function initKeyboardShortcut() {
  document.addEventListener('keydown', e => {
    if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
      e.preventDefault();
      document.getElementById('searchInput')?.focus();
    }
    if (e.key === 'Escape') {
      closeWrongModal();
      closeTOC();
    }
  });
}

/* ── Wrong Answers Modal ────────────────────────────────────────────────── */
window.openWrongModal = async function() {
  const modal    = document.getElementById('wrongModal');
  const body     = document.getElementById('modalBody');
  const subtitle = document.getElementById('modalSubtitle');
  if (!modal || !body) return;

  modal.classList.add('open');
  body.innerHTML = '<div class="modal-loading"><div class="spinner" style="display:inline-block;margin-right:8px"></div> Fragen werden geladen…</div>';

  // Collect all wrong question IDs
  const allIds = [];
  Object.values(state.scores).forEach(sc => {
    (sc.wrong_q_ids || []).forEach(id => allIds.push(id));
  });

  if (!allIds.length) {
    body.innerHTML = '<div style="color:var(--muted);text-align:center;padding:32px;font-size:14px">Keine Fehler vorhanden – weiter so! 🎉</div>';
    if (subtitle) subtitle.textContent = 'Keine falsch beantworteten Fragen.';
    return;
  }

  const j = await apiFetch('/api/learn/wrong_questions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ids: allIds })
  });

  if (!j.success) {
    body.innerHTML = '<div class="modal-loading">Fehler beim Laden der Fragen.</div>';
    return;
  }

  const questions = j.questions || [];
  if (!questions.length) {
    body.innerHTML = '<div style="color:var(--muted);text-align:center;padding:32px;font-size:14px">Keine Fehler vorhanden – weiter so! 🎉</div>';
    return;
  }

  if (subtitle) subtitle.textContent = `${questions.length} falsch beantwortete Fragen zur Wiederholung`;

  // Group by chapter
  const grouped = {};
  questions.forEach(q => {
    const key = q.chapter_id;
    if (!grouped[key]) grouped[key] = { chapter_title: q.chapter_title, subject_title: q.subject_title, subject_icon: q.subject_icon, questions: [] };
    grouped[key].questions.push(q);
  });

  body.innerHTML = '';
  Object.entries(grouped).forEach(([, grp]) => {
    const hdr = document.createElement('div');
    hdr.className = 'modal-group-hdr';
    hdr.textContent = `${grp.subject_icon} ${grp.subject_title} › ${grp.chapter_title}`;
    body.appendChild(hdr);

    grp.questions.forEach((q, modalIdx) => {
      const qcard = document.createElement('div');
      qcard.className = 'q-card';
      const offDot = q.is_official ? `<span class="q-official-dot" title="Offizielle Prüfungsfrage"></span>` : '';
      qcard.innerHTML = `
        <div class="q-lbl">Falsch beantwortet ${offDot}</div>
        <p class="q-txt">${escHtml(q.q)}</p>
        <div class="ans-list" id="modal-ans-${q.id}-${modalIdx}">
          ${q.options.map((opt, oi) => `
            <button type="button" class="ans-btn" data-qi="${modalIdx}" data-oi="${oi}" data-correct="${q.answer}">
              <span class="ans-prefix">${LETTERS[oi]}.</span>
              <span>${escHtml(opt)}</span>
            </button>`).join('')}
        </div>
        <div class="expl" id="modal-expl-${q.id}-${modalIdx}">
          <span class="expl-ico">💡</span>
          <span class="expl-text">${escHtml(q.explanation || '')}</span>
        </div>`;

      const modalAnswered = {};
      qcard.querySelectorAll('.ans-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const qi = parseInt(btn.dataset.qi);
          const oi = parseInt(btn.dataset.oi);
          if (modalAnswered[qi] !== undefined) return;
          modalAnswered[qi] = oi;
          const correctIdx = parseInt(btn.dataset.correct);
          qcard.querySelectorAll('.ans-btn').forEach(b => {
            b.classList.add('locked');
            const boi = parseInt(b.dataset.oi);
            if (boi === correctIdx) b.classList.add('correct');
            if (boi === oi && oi !== correctIdx) b.classList.add('wrong');
          });
          const expl = qcard.querySelector(`#modal-expl-${q.id}-${modalIdx}`);
          if (expl) expl.classList.add('show');
        });
      });

      body.appendChild(qcard);
    });
  });
};

window.openWrongModalForChapter = function(chapterId) {
  window.openWrongModal();
};

window.closeWrongModal = function() {
  document.getElementById('wrongModal')?.classList.remove('open');
};

document.addEventListener('click', e => {
  if (e.target.classList.contains('modal-ov')) window.closeWrongModal();
  if (e.target.classList.contains('toc-overlay')) window.closeTOC();
});

/* ── Mobile sidebar ─────────────────────────────────────────────────────── */
window.toggleMobileSidebar = function() {
  document.querySelector('.lrn-sidebar')?.classList.toggle('mobile-open');
};

/* ── Subject-specific visualizations ───────────────────────────────────── */
function buildVisualization(chapterId) {
  const id = chapterId || '';

  if (id.includes('airlaw') || id.includes('luftrecht')) {
    return `
      <div class="viz-box">
        <div class="viz-hdr">🗺️ Luftraumklassen (Europa – SERA)</div>
        <div class="as-layers">
          ${[
            { cls:'A', bg:'#1e3a5f', border:'#3b82f6', note:'Nur IFR · Separation für alle' },
            { cls:'B', bg:'#1e3a5f', border:'#60a5fa', note:'IFR+VFR · Separation für alle' },
            { cls:'C', bg:'#1c3360', border:'#93c5fd', note:'IFR+VFR · Freigabe nötig · Sep. für IFR' },
            { cls:'D', bg:'#1a2e54', border:'#bfdbfe', note:'IFR+VFR · Freigabe nötig · VFR: Verkehrsinfo' },
            { cls:'E', bg:'#172747', border:'#e0f2fe', note:'IFR: Freigabe · VFR: frei' },
            { cls:'F', bg:'#15243e', border:'#94a3b8', note:'Beratungsdienst · kein Trennungsdienst' },
            { cls:'G', bg:'#121f35', border:'#64748b', note:'Unkontrolliert · keine ATC-Freigabe nötig' }
          ].map(l => `
            <div class="as-layer" style="background:${l.bg};border:1px solid ${l.border}30">
              <div class="as-cls" style="background:${l.border}20;color:${l.border}">${l.cls}</div>
              <span class="as-nm">Klasse ${l.cls}</span>
              <span class="as-note">${l.note}</span>
            </div>`).join('')}
        </div>
      </div>`;
  }

  if (id.includes('pof') || id.includes('flugzeugkunde') || id.includes('technik')) {
    if (id.includes('control') || id.includes('steuer') || id.includes('stabili')) {
      return `
        <div class="viz-box">
          <div class="viz-hdr">🛩️ Drei Steuerachsen</div>
          <div class="axes-grid">
            <div class="ax-card">
              <div class="ax-icon">↔️</div>
              <div class="ax-nm">Rollachse</div>
              <div class="ax-ctrl">Querruder<br><span style="color:#60a5fa;font-size:10px">Ailerons</span></div>
            </div>
            <div class="ax-card">
              <div class="ax-icon">↕️</div>
              <div class="ax-nm">Nickachse</div>
              <div class="ax-ctrl">Höhenruder<br><span style="color:#60a5fa;font-size:10px">Elevator</span></div>
            </div>
            <div class="ax-card">
              <div class="ax-icon">🔄</div>
              <div class="ax-nm">Gierachse</div>
              <div class="ax-ctrl">Seitenruder<br><span style="color:#60a5fa;font-size:10px">Rudder</span></div>
            </div>
          </div>
          <div style="margin-top:12px;padding:10px;background:rgba(245,158,11,.07);border:1px solid rgba(245,158,11,.25);border-radius:9px;font-size:12px;color:#fde68a;">
            ⚠️ <strong>Adverse Yaw:</strong> Querruder rechts → linker Flügel mehr ind. Widerstand → Gieren nach links → Seitenruder-Gegensteuer!
          </div>
        </div>`;
    }
    if (id.includes('lift') || id.includes('auftrieb') || id.includes('aero')) {
      return `
        <div class="viz-box">
          <div class="viz-hdr">📐 Anstellwinkel & Stall</div>
          <svg class="wind-triangle-svg" viewBox="0 0 380 160" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="stallGrd" x1="0" y1="0" x2="1" y2="0">
                <stop offset="0%"   stop-color="#10b981"/>
                <stop offset="65%"  stop-color="#f59e0b"/>
                <stop offset="100%" stop-color="#ef4444"/>
              </linearGradient>
            </defs>
            <rect x="20" y="70" width="340" height="18" rx="9" fill="url(#stallGrd)" opacity=".85"/>
            <text x="20"  y="63" font-size="10" fill="#94a3b8" font-family="monospace">0°</text>
            <text x="150" y="63" font-size="10" fill="#94a3b8" font-family="monospace">~8°</text>
            <text x="258" y="63" font-size="10" fill="#ef4444" font-weight="700" font-family="monospace">~15-18°</text>
            <line x1="155" y1="65" x2="155" y2="88" stroke="#f59e0b" stroke-width="1.5" stroke-dasharray="3,2"/>
            <line x1="272" y1="65" x2="272" y2="88" stroke="#ef4444" stroke-width="2"/>
            <text x="20"  y="108" font-size="11" fill="#10b981">Normaler Flug</text>
            <text x="130" y="108" font-size="11" fill="#f59e0b">Max. C_L</text>
            <text x="240" y="108" font-size="11" fill="#ef4444" font-weight="700">⚡ STALL</text>
            <text x="20"  y="148" font-size="10" fill="#64748b">Stall = Überschreitung krit. Anstellwinkel (unabhängig von Geschwindigkeit!)</text>
          </svg>
        </div>`;
    }
  }

  if (id.includes('met') || id.includes('wetter') || id.includes('meteorologie')) {
    if (id.includes('atmo') || id.includes('atm')) {
      return `
        <div class="viz-box">
          <div class="viz-hdr">🌍 Atmosphärenschichten (ICAO)</div>
          <div class="atmo-bar">
            ${[
              { nm:'Troposphäre',  ht:'0 – 11 km',    col:'#3b82f6', desc:'Wetter, Wolken, Flugbetrieb' },
              { nm:'Tropopause',   ht:'~11 km',        col:'#8b5cf6', desc:'Grenzschicht, Jetstream, ISA' },
              { nm:'Stratosphäre', ht:'11 – 50 km',    col:'#6366f1', desc:'Ruhige Luft, Ozonschicht' },
              { nm:'Mesosphäre',   ht:'50 – 85 km',    col:'#4f46e5', desc:'Meteore verbrennen hier' }
            ].map(l => `
              <div class="atmo-layer" style="background:${l.col}18;border:1px solid ${l.col}30">
                <span class="atmo-nm" style="color:${l.col}">${l.nm}</span>
                <span class="atmo-ht">${l.ht}</span>
                <span class="atmo-desc">${l.desc}</span>
              </div>`).join('')}
          </div>
          <div style="margin-top:10px;font-size:11px;color:var(--muted)">
            ISA: MSL = 15°C · 1013,25 hPa · Temperaturabnahme −2°C / 300 m (−6,5°C / 1000 m)
          </div>
        </div>`;
    }
    if (id.includes('cloud') || id.includes('wolke') || id.includes('wetter')) {
      return `
        <div class="viz-box">
          <div class="viz-hdr">☁️ Wichtige Wolkenarten für VFR-Piloten</div>
          <div style="display:flex;flex-direction:column;gap:4px">
            ${[
              { nm:'Cumulonimbus (CB)', ht:'500–12000 m', col:'#ef4444', risk:'⚡ GEFÄHRLICH – Turbulenzen, Hagel, Vereisung, Blitz' },
              { nm:'Cumulus (Cu)',       ht:'600–3000 m',  col:'#f59e0b', risk:'⬆️ Aufwind/Böen – IMC möglich' },
              { nm:'Stratus (St)',       ht:'0–500 m',     col:'#94a3b8', risk:'🌫️ Sichtbehinderung, Nieselregen' },
              { nm:'Cirrus (Ci)',        ht:'6000–12000 m',col:'#60a5fa', risk:'❄️ Eiswolken – Warmfrontankündigung' },
              { nm:'Nimbostratus (Ns)',  ht:'500–3000 m',  col:'#6b7280', risk:'🌧️ Dauerregen, schlechte Sicht' }
            ].map(w => `
              <div style="display:flex;align-items:center;gap:9px;padding:7px 10px;border-radius:7px;background:${w.col}12;border:1px solid ${w.col}25">
                <span style="font-weight:700;font-size:12px;color:${w.col};min-width:165px">${w.nm}</span>
                <span style="font-size:10px;color:var(--muted);min-width:80px">${w.ht}</span>
                <span style="font-size:11px;color:rgba(255,255,255,.75)">${w.risk}</span>
              </div>`).join('')}
          </div>
        </div>`;
    }
  }

  if (id === 'nav-flight') {
    return `
      <div class="viz-box">
        <div class="viz-hdr">🧭 Winddreieck – Grundprinzip</div>
        <svg class="wind-triangle-svg" viewBox="0 0 360 160" xmlns="http://www.w3.org/2000/svg">
          <defs>
            <marker id="arrB" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#60a5fa"/></marker>
            <marker id="arrA" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#f59e0b"/></marker>
            <marker id="arrG" markerWidth="8" markerHeight="8" refX="6" refY="3" orient="auto"><path d="M0,0 L0,6 L8,3 z" fill="#10b981"/></marker>
          </defs>
          <line x1="40"  y1="100" x2="200" y2="40"  stroke="#60a5fa" stroke-width="2.5" marker-end="url(#arrB)"/>
          <line x1="200" y1="40"  x2="260" y2="100" stroke="#f59e0b" stroke-width="2"   stroke-dasharray="5,3" marker-end="url(#arrA)"/>
          <line x1="40"  y1="100" x2="260" y2="100" stroke="#10b981" stroke-width="2.5" marker-end="url(#arrG)"/>
          <text x="90"  y="58"  font-size="11" fill="#60a5fa" font-weight="700">TAS (Heading)</text>
          <text x="210" y="78"  font-size="11" fill="#f59e0b" font-weight="700">Wind</text>
          <text x="120" y="120" font-size="11" fill="#10b981" font-weight="700">GS (Track)</text>
          <text x="20"  y="148" font-size="10" fill="#64748b">TAS + Wind-Vektor = GS · WCA = Winkel zwischen Heading und Track</text>
        </svg>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px">
          ${[
            {k:'Grundaufgabe 1', d:'TC, TAS, Wind bekannt → WCA und GS gesucht', c:'#22c55e'},
            {k:'Grundaufgabe 2', d:'TH, TT (geflogener Track), GS bekannt → Wind gesucht', c:'#3b82f6'},
            {k:'Grundaufgabe 3', d:'TH, TAS, Wind bekannt → DA (Abdrift) und GS gesucht', c:'#f59e0b'},
            {k:'1:60-Regel', d:'1 NM Abweichung auf 60 NM = 1° Kursfehler', c:'#8b5cf6'},
          ].map(i=>`<div style="padding:9px;background:${i.c}10;border:1px solid ${i.c}25;border-radius:8px"><div style="font-weight:700;font-size:11px;color:${i.c}">${i.k}</div><div style="font-size:10px;color:var(--muted);margin-top:3px">${i.d}</div></div>`).join('')}
        </div>
      </div>`;
  }

  if (id === 'nav-ssr') {
    return `
      <div class="viz-box">
        <div class="viz-hdr">📡 Transponder-Codes im Überblick</div>
        <div style="display:flex;flex-direction:column;gap:6px">
          ${[
            { code:'7000', lbl:'VFR Standard', col:'#60a5fa', desc:'Standardeinstellung ohne ATC-Anweisung (Deutschland/Europa)' },
            { code:'7700', lbl:'NOTFALL', col:'#ef4444', desc:'Emergency / MAYDAY – sofortige Hilfe nötig' },
            { code:'7600', lbl:'FUNKAUSFALL', col:'#f59e0b', desc:'Radio Failure – Squawk 7600 und NORDO-Verfahren' },
            { code:'7500', lbl:'ENTFÜHRUNG', col:'#8b5cf6', desc:'Unlawful Interference – Hijacking; niemals laut ansagen!' },
          ].map(c=>`
            <div style="display:flex;align-items:center;gap:12px;padding:8px 13px;background:${c.col}10;border:1px solid ${c.col}30;border-radius:9px">
              <span style="font-family:monospace;font-size:17px;font-weight:800;color:${c.col};min-width:48px">${c.code}</span>
              <span style="font-size:11px;font-weight:700;color:${c.col};min-width:110px">${c.lbl}</span>
              <span style="font-size:11px;color:rgba(255,255,255,.75)">${c.desc}</span>
            </div>`).join('')}
        </div>
        <div style="margin-top:10px;display:grid;grid-template-columns:1fr 1fr 1fr;gap:7px">
          ${[
            {m:'Mode A', d:'Nur Code (Squawk)', c:'#64748b'},
            {m:'Mode C', d:'Code + Druckhöhe', c:'#3b82f6'},
            {m:'Mode S', d:'Code + Höhe + ID + Datalink', c:'#22c55e'},
          ].map(m=>`<div style="padding:8px;background:${m.c}12;border:1px solid ${m.c}30;border-radius:7px;text-align:center"><div style="font-weight:700;color:${m.c};font-size:11px">${m.m}</div><div style="font-size:10px;color:var(--muted);margin-top:2px">${m.d}</div></div>`).join('')}
        </div>
      </div>`;
  }

  if (id === 'nav-vor') {
    return `
      <div class="viz-box">
        <div class="viz-hdr">📡 VOR-Navigation – CDI-Interpretation</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:10px">
          <div style="padding:10px;background:rgba(34,197,94,.08);border:1px solid rgba(34,197,94,.25);border-radius:9px">
            <div style="font-weight:700;color:#4ade80;font-size:12px;margin-bottom:5px">✅ TO-Anzeige</div>
            <div style="font-size:11px;color:var(--fg)">Eingestellter Kurs führt <strong>zur Station hin</strong>.<br>Nase auf Station gerichtet.</div>
          </div>
          <div style="padding:10px;background:rgba(245,158,11,.08);border:1px solid rgba(245,158,11,.25);border-radius:9px">
            <div style="font-weight:700;color:#fbbf24;font-size:12px;margin-bottom:5px">↩ FROM-Anzeige (FR)</div>
            <div style="font-size:11px;color:var(--fg)">Eingestellter Kurs führt <strong>von der Station weg</strong>.<br>Flugzeug fliegt vom VOR weg.</div>
          </div>
        </div>
        <div style="padding:10px;background:rgba(59,130,246,.07);border:1px solid rgba(59,130,246,.2);border-radius:9px;font-size:11px">
          <strong style="color:#60a5fa">🔑 CDI als Kommandogerät:</strong> Korrekturen immer <strong>zur Nadel hin</strong> ausführen!<br>
          Nadel rechts → nach rechts fliegen &nbsp;|&nbsp; Nadel links → nach links fliegen<br>
          <span style="color:var(--muted)">1 Vollausschlag = 10° Ablage; 1 Dot = 2° Ablage</span>
        </div>
        <div style="margin-top:8px;padding:8px 10px;background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.25);border-radius:8px;font-size:11px;color:#fca5a5">
          ⚠️ <strong>Schweigekegel:</strong> Kein verlässliches Signal direkt über der Station (±40°). Warnflagge erscheint → CDI nicht nutzbar!
        </div>
      </div>`;
  }

  if (id === 'nav-ndb') {
    return `
      <div class="viz-box">
        <div class="viz-hdr">📻 NDB-Navigationsverfahren im Überblick</div>
        <div style="display:flex;flex-direction:column;gap:7px">
          ${[
            {nm:'Homing (Zielflug)', col:'#22c55e', desc:'RB = 000° halten → immer direkt auf Station; Windversatz führt zur Hundekurve'},
            {nm:'Stehende Peilung (Kursflug zur Station)', col:'#3b82f6', desc:'WCA anlegen, sodass RB konstant bleibt; gerader Kurs trotz Wind'},
            {nm:'Kursflug (Tracking)', col:'#f59e0b', desc:'QDM als Führungsgröße; Kurskorrektur zur Nadel (bei RMI: Nadelspitze)'},
            {nm:'Kreuzpeilung', col:'#8b5cf6', desc:'2 NDB-Peilungen → QTEs auf Karte → Schnittpunkt = Position'},
          ].map(v=>`<div style="display:flex;align-items:flex-start;gap:10px;padding:8px 11px;background:${v.col}10;border:1px solid ${v.col}25;border-radius:8px"><div style="font-weight:700;font-size:11px;color:${v.col};min-width:190px">${v.nm}</div><div style="font-size:11px;color:var(--fg)">${v.desc}</div></div>`).join('')}
        </div>
        <div style="margin-top:9px;padding:9px 11px;background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.25);border-radius:8px;font-size:11px">
          ⚠️ <strong style="color:#f87171">Hauptfehlerquellen:</strong> Fading (Dämmerung) · Küsteneffekt · Bergeffekt · Elektrische Entladungen · Quadrantal Error · Dip Error<br>
          <span style="color:var(--muted)">Gesamtfehler NDB: ca. ±5° | VOR: ca. ±2°</span>
        </div>
      </div>`;
  }

  if (id === 'nav-funk-basics') {
    return `
      <div class="viz-box">
        <div class="viz-hdr">📶 Frequenzbänder – Navidsysteme der VFR-Prüfung</div>
        <div style="display:flex;flex-direction:column;gap:5px">
          ${[
            {band:'LF/MF', rng:'30–3000 kHz', col:'#f59e0b', sys:'NDB (190–1750 kHz)', wave:'Boden + Raumwelle'},
            {band:'HF', rng:'3–30 MHz', col:'#ef4444', sys:'Kurzwellen-Comm', wave:'Raumwelle dominant'},
            {band:'VHF', rng:'30–300 MHz', col:'#22c55e', sys:'VOR (108–117,975) · VHF COM · Marker', wave:'Nur Direkte Welle (LOS)'},
            {band:'UHF', rng:'300–3000 MHz', col:'#3b82f6', sys:'DME · SSR/Transponder · GPS (1575 MHz)', wave:'Nur Direkte Welle (LOS)'},
          ].map(b=>`<div style="display:flex;align-items:center;gap:8px;padding:7px 10px;background:${b.col}10;border:1px solid ${b.col}25;border-radius:7px"><div style="min-width:36px;font-weight:800;font-size:11px;color:${b.col}">${b.band}</div><div style="min-width:100px;font-size:10px;color:var(--muted)">${b.rng}</div><div style="font-weight:600;font-size:11px;color:var(--fg);flex:1">${b.sys}</div><div style="font-size:10px;color:var(--muted);text-align:right">${b.wave}</div></div>`).join('')}
        </div>
        <div style="margin-top:9px;padding:9px 11px;background:rgba(59,130,246,.07);border:1px solid rgba(59,130,246,.2);border-radius:8px;font-size:11px">
          🔑 <strong style="color:#60a5fa">Wellenformel:</strong> c = λ × f &nbsp;(c = 300.000 km/s) &nbsp;|&nbsp; Je höher die Frequenz, desto kürzer die Wellenlänge<br>
          <span style="color:var(--muted)">Fading-Effekt: Überlagerung Raum- + Bodenwelle → Störung bei Dämmerung (betrifft NDB!)</span>
        </div>
      </div>`;
  }

  if (id === 'nav-vdf') {
    return `
      <div class="viz-box">
        <div class="viz-hdr">📡 Q-Gruppen – Peilungsübersicht</div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:9px">
          ${[
            {q:'QDM', full:'Magnetic Bearing to station', col:'#22c55e', form:'MH + RB', de:'Missweisende Peilung ZUR Station'},
            {q:'QDR', full:'Magnetic Bearing from station', col:'#f59e0b', form:'QDM ± 180°', de:'Missweisende Peilung VON Station'},
            {q:'QUJ', full:'True Bearing to station', col:'#3b82f6', form:'TH + RB', de:'Rechtweisende Peilung ZUR Station'},
            {q:'QTE', full:'True Bearing from station', col:'#ef4444', form:'QUJ ± 180°', de:'Rechtweisende Peilung VON Station'},
          ].map(q=>`<div style="padding:10px;background:${q.col}10;border:1px solid ${q.col}30;border-radius:9px"><div style="font-weight:800;font-size:16px;color:${q.col}">${q.q}</div><div style="font-size:10px;color:var(--muted);margin:2px 0">${q.full}</div><div style="font-size:11px;color:var(--fg)">${q.de}</div><div style="margin-top:5px;padding:3px 7px;background:${q.col}15;border-radius:4px;font-family:monospace;font-size:11px;color:${q.col}">${q.form}</div></div>`).join('')}
        </div>
        <div style="padding:9px 11px;background:rgba(59,130,246,.07);border:1px solid rgba(59,130,246,.2);border-radius:8px;font-size:11px">
          🔑 <strong style="color:#60a5fa">Navigationsregel:</strong> QDM wird kleiner → kleiner steuern &nbsp;|&nbsp; QDM wird größer → größer steuern
        </div>
      </div>`;
  }

  if (id === 'nav-dme') {
    return `
      <div class="viz-box">
        <div class="viz-hdr">📏 DME – Wichtige Merksätze</div>
        <div style="display:flex;flex-direction:column;gap:7px">
          ${[
            {ico:'↗', lbl:'Schrägentfernung', col:'#ef4444', d:'DME misst IMMER die direkte Luftlinienentfernung – nicht die Bodenentfernung!'},
            {ico:'🔗', lbl:'VOR-Pairing', col:'#22c55e', d:'DME-Frequenz automatisch mit VOR mitgestimmt; UHF 960–1215 MHz intern'},
            {ico:'📍', lbl:'VOR/DME-Fix', col:'#3b82f6', d:'Radial (VOR) + Entfernung (DME) → eindeutige Position ohne 2. Station'},
            {ico:'⚠', lbl:'Überflug', col:'#f59e0b', d:'Beim Überflug zeigt DME die Flughöhe in NM; Anzeige geht nie auf 0 zurück'},
          ].map(i=>`<div style="display:flex;align-items:flex-start;gap:10px;padding:8px 12px;background:${i.col}10;border:1px solid ${i.col}25;border-radius:8px"><span style="font-size:16px;min-width:24px;text-align:center">${i.ico}</span><div><div style="font-weight:700;font-size:11px;color:${i.col}">${i.lbl}</div><div style="font-size:11px;color:var(--fg);margin-top:2px">${i.d}</div></div></div>`).join('')}
        </div>
      </div>`;
  }

  if (id === 'nav-gnss') {
    return `
      <div class="viz-box">
        <div class="viz-hdr">🛰️ GNSS/GPS – Systemübersicht</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:8px;margin-bottom:10px">
          ${[
            {seg:'Raumsegment', ico:'🛰️', col:'#3b82f6', items:['30 Satelliten (GPS)', '6 Umlaufbahnen', '20.183 km Höhe', 'Umlaufzeit ~12 h']},
            {seg:'Bodensegment', ico:'🏢', col:'#22c55e', items:['Master Control Station', 'Colorado Springs (US)', 'Überwachungsstationen', 'NAV-Message ausstrahlen']},
            {seg:'Bordsegment', ico:'📟', col:'#f59e0b', items:['GPS-Empfänger', 'Empfangsantenne', 'Almanach-Daten', 'RAIM-Funktion']},
          ].map(s=>`<div style="padding:10px;background:${s.col}10;border:1px solid ${s.col}25;border-radius:9px"><div style="font-size:18px;margin-bottom:4px">${s.ico}</div><div style="font-weight:700;font-size:11px;color:${s.col};margin-bottom:6px">${s.seg}</div>${s.items.map(i=>`<div style="font-size:10px;color:var(--muted);padding:1px 0">• ${i}</div>`).join('')}</div>`).join('')}
        </div>
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
          <div style="padding:9px;background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.25);border-radius:8px;font-size:11px">
            <div style="font-weight:700;color:#f87171;margin-bottom:4px">⚠️ Fehlerquellen</div>
            <div style="color:var(--fg)">SA (Selective Availability) · Atmosphärische Ablenkung · Mehrwegeausbreitung (Gebirge) · Empfangslücken</div>
          </div>
          <div style="padding:9px;background:rgba(34,197,94,.07);border:1px solid rgba(34,197,94,.25);border-radius:8px;font-size:11px">
            <div style="font-weight:700;color:#4ade80;margin-bottom:4px">🔑 Schlüsselbegriffe</div>
            <div style="color:var(--fg)">Min. 4 Sat. für 3D-Fix · RAIM braucht 5–6 Sat. · WGS84-Referenz · DGPS für hohe Genauigkeit</div>
          </div>
        </div>
      </div>`;
  }

  if (id.includes('nav') || id.includes('navigat')) {
    return `
      <div class="viz-box">
        <div class="viz-hdr">🧭 Navigation – Schnellübersicht Funknavigation</div>
        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px">
          ${[
            {sys:'NDB/ADF', f:'190–1750 kHz', col:'#f59e0b', note:'Eigenpeilung; ±5° Fehler'},
            {sys:'VDF', f:'VHF', col:'#3b82f6', note:'Fremdpeilung; kein Bordgerät nötig'},
            {sys:'VOR', f:'108–118 MHz', col:'#22c55e', note:'Eigenpeilung; Radiale; ±2°'},
            {sys:'DME', f:'960–1215 MHz', col:'#8b5cf6', note:'Schrägentfernung; VOR-gepaart'},
            {sys:'SSR', f:'1030/1090 MHz', col:'#ef4444', note:'Transponder; Mode A/C/S'},
            {sys:'GPS', f:'1575 MHz (L1)', col:'#60a5fa', note:'4 Sat. für 3D; WGS84'},
          ].map(s=>`<div style="padding:9px;background:${s.col}10;border:1px solid ${s.col}25;border-radius:8px;text-align:center"><div style="font-weight:800;color:${s.col};font-size:13px">${s.sys}</div><div style="font-size:10px;color:var(--muted);margin:2px 0">${s.f}</div><div style="font-size:10px;color:var(--fg)">${s.note}</div></div>`).join('')}
        </div>
      </div>`;
  }

  if (id.includes('agk') || id.includes('instrument') || id.includes('avionik')) {
    return `
      <div class="viz-box">
        <div class="viz-hdr">🎛️ Pitot-Static Instrumente</div>
        <div style="display:grid;grid-template-columns:1fr 1fr 1fr;gap:9px">
          ${[
            { ico:'🌡️', nm:'ASI', src:'Pitot + Static', col:'#60a5fa', desc:'Zeigt IAS' },
            { ico:'📏', nm:'Altimeter', src:'Nur Static', col:'#34d399', desc:'Zeigt QNH-Höhe' },
            { ico:'↕',  nm:'VSI', src:'Nur Static', col:'#a78bfa', desc:'Steig-/Sinkrate' }
          ].map(i => `
            <div style="padding:11px 10px;background:rgba(255,255,255,.04);border:1px solid var(--border);border-radius:10px;text-align:center">
              <div style="font-size:20px;margin-bottom:5px">${i.ico}</div>
              <div style="font-weight:800;font-size:13px;color:${i.col}">${i.nm}</div>
              <div style="font-size:10px;color:var(--muted);margin-top:3px">${i.src}</div>
              <div style="font-size:11px;margin-top:4px">${i.desc}</div>
            </div>`).join('')}
        </div>
        <div style="margin-top:11px;padding:9px 12px;background:rgba(239,68,68,.07);border:1px solid rgba(239,68,68,.25);border-radius:8px;font-size:12px;color:#fca5a5">
          ⚠️ Pitot blockiert → nur ASI falsch · Static blockiert → ASI + Altimeter + VSI falsch
        </div>
      </div>`;
  }

  if (id.includes('com') || id.includes('funk') || id.includes('sprechfunk')) {
    return `
      <div class="viz-box">
        <div class="viz-hdr">📻 Transponder-Notfallcodes (SSR)</div>
        <div style="display:flex;flex-direction:column;gap:6px">
          ${[
            { code:'7700', lbl:'NOTFALL',   col:'#ef4444', desc:'Allgemeiner Notfall – sofortige Hilfe nötig' },
            { code:'7600', lbl:'FUNKVERLUST',col:'#f59e0b', desc:'Radio Failure – Kommunikationsausfall' },
            { code:'7500', lbl:'ENTFÜHRUNG', col:'#8b5cf6', desc:'Unlawful Interference – nie laut ankündigen!' },
            { code:'2000', lbl:'VFR STANDARD',col:'#64748b',desc:'Standard VFR ohne ATC-Zuordnung' },
          ].map(c => `
            <div style="display:flex;align-items:center;gap:12px;padding:8px 13px;background:${c.col}10;border:1px solid ${c.col}30;border-radius:9px">
              <span style="font-family:'JetBrains Mono',monospace;font-size:17px;font-weight:800;color:${c.col};min-width:48px">${c.code}</span>
              <span style="font-size:11px;font-weight:700;color:${c.col};min-width:95px">${c.lbl}</span>
              <span style="font-size:12px;color:rgba(255,255,255,.7)">${c.desc}</span>
            </div>`).join('')}
        </div>
        <div style="margin-top:10px;font-size:11px;color:var(--muted);padding:8px 10px;background:rgba(59,130,246,.07);border-radius:7px;border:1px solid rgba(59,130,246,.2)">
          🔑 Priorität: <strong style="color:#60a5fa">Aviate → Navigate → Communicate</strong>
        </div>
      </div>`;
  }

  return ''; // no viz for this chapter
}

/* ── Helpers ────────────────────────────────────────────────────────────── */
function escHtml(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g,  '&amp;')
    .replace(/</g,  '&lt;')
    .replace(/>/g,  '&gt;')
    .replace(/"/g,  '&quot;');
}
function escAttr(str) { return escHtml(str); }

function getHostname(url) {
  try { return new URL(url).hostname.replace('www.',''); } catch(e) { return ''; }
}

function setText(id, val) {
  const el = document.getElementById(id);
  if (el) el.textContent = val;
}

/* ── Start ──────────────────────────────────────────────────────────────── */
document.addEventListener('DOMContentLoaded', init);

/* ══════════════════════════════════════════════════════════════════════════
   TEST SIMULATION MODULE
   ══════════════════════════════════════════════════════════════════════════ */

const SIM = {
  active: false,
  simId: null,
  questions: [],
  answered: {},   // qi → chosen oi
  startedAt: null,
  timer: null,
  elapsed: 0
};

/* ── Open / close sim modal ─────────────────────────────────────────────── */
window.openSimModal = async function() {
  document.getElementById('simModal')?.classList.add('open');
  await renderSimConfig();
};

window.closeSimModal = function() {
  document.getElementById('simModal')?.classList.remove('open');
  if (SIM.timer) { clearInterval(SIM.timer); SIM.timer = null; }
};

/* ── Config screen ──────────────────────────────────────────────────────── */
async function renderSimConfig() {
  const body = document.getElementById('simModalBody');
  const sub  = document.getElementById('simModalSub');
  if (!body) return;
  if (sub) sub.textContent = 'EASA-konforme Prüfungssimulation';

  body.innerHTML = '<div class="modal-loading"><div class="spinner" style="display:inline-block;margin-right:8px"></div> Lade Fächer…</div>';

  const [jSubj, jHist] = await Promise.all([
    apiFetch('/api/test/subjects'),
    apiFetch('/api/test/history')
  ]);

  const subjects = (jSubj.success ? jSubj.subjects : []);
  const history  = (jHist.success ? jHist.history  : []);

  const subjCheckboxes = subjects.map(s => `
    <label class="sim-subj-check" style="border-color:${s.color}30;background:${s.color}08">
      <input type="checkbox" class="sim-subj-cb" value="${escAttr(s.id)}" checked>
      <span style="font-size:16px">${s.icon}</span>
      <div>
        <div style="font-weight:600;font-size:12px">${escHtml(s.title)}</div>
        <div style="font-size:10px;color:var(--muted)">${s.quiz_count} Fragen</div>
      </div>
    </label>`).join('');

  const histRows = history.slice(0, 10).map(h => {
    const date = h.started_at ? new Date(h.started_at + 'Z').toLocaleString('de-DE') : '–';
    const pct  = h.score_pct != null ? h.score_pct.toFixed(1) + '%' : '–';
    const cls  = h.score_pct >= 75 ? 'sim-hist-pass' : h.score_pct >= 0 ? 'sim-hist-fail' : '';
    const status = h.status === 'completed' ? '' : '<span style="color:#f59e0b;font-size:10px"> (unvollständig)</span>';
    return `<tr class="${cls}">
      <td>${date}</td>
      <td>${h.total_q || 0} Fragen</td>
      <td>${h.correct || 0}✓ ${h.wrong || 0}✗</td>
      <td><strong>${pct}</strong>${status}</td>
    </tr>`;
  }).join('');

  const histSection = history.length > 0 ? `
    <div class="sim-section">
      <h4 class="sim-sec-title">📋 Letzte Simulationen</h4>
      <div class="sim-hist-wrap">
        <table class="sim-hist-table">
          <thead><tr><th>Datum &amp; Uhrzeit</th><th>Umfang</th><th>Ergebnis</th><th>Score</th></tr></thead>
          <tbody>${histRows}</tbody>
        </table>
      </div>
    </div>` : '';

  body.innerHTML = `
    <div class="sim-config">
      <div class="sim-section">
        <h4 class="sim-sec-title">📚 Prüfungsfächer auswählen</h4>
        <div class="sim-subj-grid">${subjCheckboxes}</div>
        <div class="sim-select-actions">
          <button class="sim-sel-btn" onclick="simSelectAll(true)">Alle auswählen</button>
          <button class="sim-sel-btn" onclick="simSelectAll(false)">Alle abwählen</button>
        </div>
      </div>
      <div class="sim-section">
        <h4 class="sim-sec-title">⚙️ Fragenanzahl</h4>
        <div class="sim-count-row">
          ${[10, 20, 30, 40, 50].map(n => `
            <label class="sim-count-opt ${n===30?'active':''}">
              <input type="radio" name="simCount" value="${n}" ${n===30?'checked':''}>
              ${n}
            </label>`).join('')}
        </div>
      </div>
      ${histSection}
      <div class="sim-start-row">
        <button class="sim-start-btn" onclick="startSimulation()">
          🚀 Simulation starten
        </button>
      </div>
    </div>`;

  // Style active radio
  body.querySelectorAll('input[name="simCount"]').forEach(r => {
    r.addEventListener('change', () => {
      body.querySelectorAll('.sim-count-opt').forEach(el => el.classList.remove('active'));
      r.closest('.sim-count-opt')?.classList.add('active');
    });
  });
}

window.simSelectAll = function(val) {
  document.querySelectorAll('.sim-subj-cb').forEach(cb => cb.checked = val);
};

/* ── Start simulation ───────────────────────────────────────────────────── */
window.startSimulation = async function() {
  const body = document.getElementById('simModalBody');
  const checkedSubjects = [...document.querySelectorAll('.sim-subj-cb:checked')].map(cb => cb.value);
  const countRadio = document.querySelector('input[name="simCount"]:checked');
  const count = countRadio ? parseInt(countRadio.value) : 30;

  if (checkedSubjects.length === 0) {
    alert('Bitte wähle mindestens ein Prüfungsfach aus.');
    return;
  }

  body.innerHTML = '<div class="modal-loading"><div class="spinner" style="display:inline-block;margin-right:8px"></div> Simulation wird vorbereitet…</div>';

  const j = await apiFetch('/api/test/start', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ subject_ids: checkedSubjects, count })
  });

  if (!j.success || !j.questions?.length) {
    body.innerHTML = '<div style="text-align:center;padding:32px;color:var(--muted)">Keine Fragen gefunden. Bitte andere Fächer auswählen.</div>';
    return;
  }

  SIM.active    = true;
  SIM.simId     = j.sim_id;
  SIM.questions = (j.questions || []).sort(() => Math.random() - 0.5).map(shuffleOptions);
  SIM.answered  = {};
  SIM.startedAt = j.started_at;
  SIM.elapsed   = 0;

  renderSimQuiz();

  // Start timer
  if (SIM.timer) clearInterval(SIM.timer);
  SIM.timer = setInterval(() => {
    SIM.elapsed++;
    const el = document.getElementById('simTimer');
    if (el) el.textContent = formatSimTime(SIM.elapsed);
  }, 1000);
};

function formatSimTime(s) {
  const m = Math.floor(s / 60);
  const sec = s % 60;
  return `${m}:${sec.toString().padStart(2,'0')}`;
}

/* ── Render sim quiz ────────────────────────────────────────────────────── */
function renderSimQuiz() {
  const body = document.getElementById('simModalBody');
  const sub  = document.getElementById('simModalSub');
  if (!body) return;
  if (sub) sub.textContent = `${SIM.questions.length} Fragen · EASA-Simulation`;

  const total = SIM.questions.length;

  body.innerHTML = `
    <div class="sim-quiz-wrap">
      <div class="sim-quiz-hdr">
        <div class="sim-progress-info">
          <span id="simProgressTxt">0 / ${total} beantwortet</span>
          <div class="sim-prog-bg"><div class="sim-prog-fg" id="simProgFg" style="width:0%"></div></div>
        </div>
        <div class="sim-stats-row">
          <span class="sim-stat-ok" id="simStatOk">0 ✓</span>
          <span class="sim-stat-err" id="simStatErr">0 ✗</span>
          <span class="sim-timer" id="simTimer">0:00</span>
        </div>
      </div>
      <div class="sim-qlist" id="simQlist"></div>
      <div class="sim-finish-row">
        <button class="sim-finish-btn" id="simFinishBtn" onclick="finishSimulation()" disabled>
          🏁 Simulation abschließen
        </button>
      </div>
    </div>`;

  const qlist = document.getElementById('simQlist');
  SIM.questions.forEach((q, i) => {
    const qcard = document.createElement('div');
    qcard.className = 'q-card sim-q-card';
    qcard.id = `simq-${i}`;

    const offDot = q.is_official ? `<span class="q-official-dot" title="Offizielle Prüfungsfrage"></span>` : '';
    const subjTag = `<span class="sim-subj-tag">${q.subject_icon} ${escHtml(q.subject_title)}</span>`;

    qcard.innerHTML = `
      <div class="q-lbl">Frage ${i+1} / ${SIM.questions.length} ${offDot} ${subjTag}</div>
      <p class="q-txt">${escHtml(q.q)}</p>
      ${q.image_path ? `<img src="/static/${q.image_path}" class="q-img" alt="Siehe Bild" title="Klicken zum Vergr\u00f6\u00dfern">` : ''}
      <div class="ans-list" id="simans-${i}">
        ${q.options.map((opt, oi) => `
          <button type="button" class="ans-btn" data-qi="${i}" data-oi="${oi}" data-correct="${q.answer}">
            <span class="ans-prefix">${LETTERS[oi]}.</span>
            <span>${escHtml(opt)}</span>
          </button>`).join('')}
      </div>
      <div class="expl" id="simexpl-${i}">
        <span class="expl-ico">💡</span>
        <span class="expl-text">${escHtml(q.explanation || '')}</span>
      </div>`;

    qcard.querySelectorAll('.ans-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const qi = parseInt(btn.dataset.qi);
        if (SIM.answered[qi] !== undefined) return;
        const oi = parseInt(btn.dataset.oi);
        const correctIdx = parseInt(btn.dataset.correct);
        SIM.answered[qi] = oi;

        qcard.querySelectorAll('.ans-btn').forEach(b => {
          b.classList.add('locked');
          const boi = parseInt(b.dataset.oi);
          if (boi === correctIdx) b.classList.add('correct');
          if (boi === oi && oi !== correctIdx) b.classList.add('wrong');
        });

        const expl = document.getElementById(`simexpl-${qi}`);
        if (expl) expl.classList.add('show');

        updateSimProgress();
      });
    });

    qlist.appendChild(qcard);
  });
}

function updateSimProgress() {
  const answered = Object.keys(SIM.answered).length;
  const total    = SIM.questions.length;
  let correct = 0, wrong = 0;

  SIM.questions.forEach((q, i) => {
    if (SIM.answered[i] !== undefined) {
      if (SIM.answered[i] === q.answer) correct++;
      else wrong++;
    }
  });

  setText('simProgressTxt', `${answered} / ${total} beantwortet`);
  const fg = document.getElementById('simProgFg');
  if (fg) fg.style.width = (answered / total * 100) + '%';
  setText('simStatOk',  correct + ' ✓');
  setText('simStatErr', wrong + ' ✗');

  const btn = document.getElementById('simFinishBtn');
  if (btn) btn.disabled = answered < total;
}

/* ── Finish simulation ──────────────────────────────────────────────────── */
window.finishSimulation = async function() {
  if (SIM.timer) { clearInterval(SIM.timer); SIM.timer = null; }

  let correct = 0, wrong = 0;
  SIM.questions.forEach((q, i) => {
    if (SIM.answered[i] !== undefined) {
      if (SIM.answered[i] === q.answer) correct++;
      else wrong++;
    }
  });

  const j = await apiFetch('/api/test/finish', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ sim_id: SIM.simId, correct, wrong })
  });

  const total = correct + wrong;
  const pct   = total > 0 ? (correct / total * 100).toFixed(1) : 0;
  const passed = parseFloat(pct) >= 75;

  const body = document.getElementById('simModalBody');
  const sub  = document.getElementById('simModalSub');
  if (sub) sub.textContent = 'Simulation abgeschlossen';

  // Build wrong questions list
  const wrongQs = SIM.questions.filter((q, i) => SIM.answered[i] !== q.answer).map(shuffleOptions);
  const wrongHtml = wrongQs.length > 0 ? `
    <div class="sim-wrong-list">
      <h4 class="sim-sec-title" style="margin-top:20px">❌ Falsch beantwortete Fragen (${wrongQs.length})</h4>
      ${wrongQs.map(q => {
        const qi = SIM.questions.indexOf(q);
        const chosenOi = SIM.answered[qi];
        const chosenTxt = chosenOi !== undefined ? q.options[chosenOi] : '–';
        const correctTxt = q.options[q.answer] || '–';
        return `<div class="sim-wrong-item">
          <div class="sim-wrong-q">${escHtml(q.q)}</div>
          <div class="sim-wrong-ans wrong-ans">❌ Gegeben: ${escHtml(chosenTxt)}</div>
          <div class="sim-wrong-ans correct-ans">✅ Richtig: ${escHtml(correctTxt)}</div>
          ${q.explanation ? `<div class="sim-wrong-expl">💡 ${escHtml(q.explanation)}</div>` : ''}
        </div>`;
      }).join('')}
    </div>` : '';

  body.innerHTML = `
    <div class="sim-result">
      <div class="sim-result-circle ${passed ? 'pass' : 'fail'}">
        <div class="sim-result-pct">${pct}%</div>
        <div class="sim-result-label">${passed ? '✅ Bestanden' : '❌ Nicht bestanden'}</div>
      </div>
      <div class="sim-result-stats">
        <div class="sim-res-stat"><span class="sim-res-val green">${correct}</span><span>Richtig</span></div>
        <div class="sim-res-stat"><span class="sim-res-val red">${wrong}</span><span>Falsch</span></div>
        <div class="sim-res-stat"><span class="sim-res-val">${total}</span><span>Gesamt</span></div>
        <div class="sim-res-stat"><span class="sim-res-val blue">${formatSimTime(SIM.elapsed)}</span><span>Zeit</span></div>
      </div>
      <div class="sim-result-note">
        ${passed
          ? '🎉 Herzlichen Glückwunsch! Du hast die Simulation bestanden (Bestehensgrenze: 75%).'
          : `Leider nicht bestanden. Bestehensgrenze: 75%. Du hast ${(75 - parseFloat(pct)).toFixed(1)}% gefehlt.`}
      </div>
      ${wrongHtml}
      <div class="sim-result-actions">
        <button class="sim-start-btn" onclick="openSimModal()" style="font-size:13px;padding:10px 24px">
          🔄 Neue Simulation starten
        </button>
      </div>
    </div>`;

  SIM.active = false;
};

/* ══════════════════════════════════════════════════════════════════════════
   WRONG ANSWER REMOVAL: when retried correctly → remove from bank
   ══════════════════════════════════════════════════════════════════════════ */

/* Override the modal's answer handler to auto-remove correct retries */
const _origOpenWrong = window.openWrongModal;
window.openWrongModal = async function() {
  const modal    = document.getElementById('wrongModal');
  const body     = document.getElementById('modalBody');
  const subtitle = document.getElementById('modalSubtitle');
  if (!modal || !body) return;

  modal.classList.add('open');
  body.innerHTML = '<div class="modal-loading"><div class="spinner" style="display:inline-block;margin-right:8px"></div> Fragen werden geladen…</div>';

  const allIds = [];
  Object.values(state.scores).forEach(sc => {
    (sc.wrong_q_ids || []).forEach(id => allIds.push(id));
  });

  if (!allIds.length) {
    body.innerHTML = '<div style="color:var(--muted);text-align:center;padding:32px;font-size:14px">Keine Fehler vorhanden – weiter so! 🎉</div>';
    if (subtitle) subtitle.textContent = 'Keine falsch beantworteten Fragen.';
    return;
  }

  const j = await apiFetch('/api/learn/wrong_questions', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ ids: allIds })
  });

  if (!j.success) {
    body.innerHTML = '<div class="modal-loading">Fehler beim Laden der Fragen.</div>';
    return;
  }

  const questions = j.questions || [];
  if (!questions.length) {
    body.innerHTML = '<div style="color:var(--muted);text-align:center;padding:32px;font-size:14px">Keine Fehler vorhanden – weiter so! 🎉</div>';
    return;
  }

  if (subtitle) subtitle.textContent = `${questions.length} falsch beantwortete Fragen zur Wiederholung`;

  const grouped = {};
  questions.forEach(q => {
    if (!grouped[q.chapter_id]) grouped[q.chapter_id] = {
      chapter_title: q.chapter_title, subject_title: q.subject_title,
      subject_icon: q.subject_icon, questions: []
    };
    grouped[q.chapter_id].questions.push(q);
  });

  body.innerHTML = '';
  const modalAnswered = {};

  Object.entries(grouped).forEach(([chapterId, grp]) => {
    const hdr = document.createElement('div');
    hdr.className = 'modal-group-hdr';
    hdr.textContent = `${grp.subject_icon} ${grp.subject_title} › ${grp.chapter_title}`;
    body.appendChild(hdr);

    grp.questions.forEach((q, modalIdx) => {
      const qcard = document.createElement('div');
      qcard.className = 'q-card';
      qcard.id = `mq-${q.id}`;
      const offDot = q.is_official ? `<span class="q-official-dot" title="Offizielle Prüfungsfrage"></span>` : '';
      qcard.innerHTML = `
        <div class="q-lbl">Fehler wiederholen ${offDot}</div>
        <p class="q-txt">${escHtml(q.q)}</p>
        <div class="ans-list" id="modal-ans-${q.id}-${modalIdx}">
          ${q.options.map((opt, oi) => `
            <button type="button" class="ans-btn" data-qid="${q.id}" data-oi="${oi}" data-correct="${q.answer}">
              <span class="ans-prefix">${LETTERS[oi]}.</span>
              <span>${escHtml(opt)}</span>
            </button>`).join('')}
        </div>
        <div class="expl" id="modal-expl-${q.id}-${modalIdx}">
          <span class="expl-ico">💡</span>
          <span class="expl-text">${escHtml(q.explanation || '')}</span>
        </div>`;

      qcard.querySelectorAll('.ans-btn').forEach(btn => {
        btn.addEventListener('click', () => {
          const qid = parseInt(btn.dataset.qid);
          const oi  = parseInt(btn.dataset.oi);
          if (modalAnswered[qid] !== undefined) return;
          modalAnswered[qid] = oi;
          const correctIdx = parseInt(btn.dataset.correct);
          qcard.querySelectorAll('.ans-btn').forEach(b => {
            b.classList.add('locked');
            const boi = parseInt(b.dataset.oi);
            if (boi === correctIdx) b.classList.add('correct');
            if (boi === oi && oi !== correctIdx) b.classList.add('wrong');
          });
          const expl = qcard.querySelector(`#modal-expl-${qid}-${modalIdx}`);
          if (expl) expl.classList.add('show');

          // ── KEY FIX: if answered correctly → remove from wrong bank ──
          if (oi === correctIdx) {
            // Remove from local state scores
            Object.keys(state.scores).forEach(chId => {
              const sc = state.scores[chId];
              if (sc && sc.wrong_q_ids) {
                const before = sc.wrong_q_ids.length;
                sc.wrong_q_ids = sc.wrong_q_ids.filter(id => id !== qid);
                if (sc.wrong_q_ids.length < before) {
                  sc.wrong = Math.max(0, (sc.wrong || 1) - 1);
                }
              }
            });
            // Persist to server
            apiFetch('/api/quiz/remove_wrong', {
              method: 'POST',
              headers: { 'Content-Type': 'application/json' },
              body: JSON.stringify({ remove_ids: [qid] })
            });
            // Visual feedback
            setTimeout(() => {
              qcard.style.transition = 'opacity 0.5s, transform 0.5s';
              qcard.style.opacity = '0.4';
              qcard.style.transform = 'translateX(20px)';
              const okBadge = document.createElement('div');
              okBadge.style.cssText = 'text-align:center;padding:8px;font-size:12px;color:#4ade80;font-weight:600;';
              okBadge.textContent = '✅ Richtig beantwortet – aus Fehlerliste entfernt';
              qcard.appendChild(okBadge);
            }, 600);
            // Update UI
            updateWrongBtn();
            renderGlobalStats();
          }
        });
      });

      body.appendChild(qcard);
    });
  });
};

/* ══ Image Zoom (lightbox) ═══════════════════════════════════════════════════════════════════════════════ */
document.addEventListener('click', function(e) {
  if (e.target.classList.contains('q-img')) {
    var modal = document.getElementById('imgZoomModal');
    var img   = document.getElementById('imgZoomImg');
    img.src = e.target.src;
    modal.classList.add('open');
    document.body.style.overflow = 'hidden';
    e.stopPropagation();
  }
});

function closeImgZoom(e) {
  if (e && e.target && e.target.classList.contains('img-zoom-img')) return;
  document.getElementById('imgZoomModal').classList.remove('open');
  document.body.style.overflow = '';
}

document.addEventListener('keydown', function(e) {
  if (e.key === 'Escape') closeImgZoom();
});
