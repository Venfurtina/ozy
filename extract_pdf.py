#!/usr/bin/env python3
"""
extract_pdf.py  –  PPL(A) Lernplattform – Lehrbuch-Extraktor
═══════════════════════════════════════════════════════════════════════════════
Liest eine PDF-Datei (ein Kapitel des Lehrbuchs), extrahiert Inhalte und
schreibt sie in die SQLite-Datenbank (learn_subjects / learn_chapters /
learn_sections / learn_quiz).

Verwendung:
  python extract_pdf.py <pdf_pfad> [optionen]

Optionen:
  --subject-id    ID des Fachs (z. B. "luftrecht", "meteorologie")
  --subject-title Anzeigetitel des Fachs (z. B. "Luftrecht & ATC-Verfahren")
  --subject-code  Prüfungsfach-Kürzel (z. B. "010", "050")
  --subject-icon  Emoji für das Fach (Standard: "📖")
  --subject-color Hex-Farbe (Standard: "#3b82f6")
  --chapter-id    Kapitel-ID (Standard: abgeleitet vom Dateinamen)
  --chapter-title Kapiteltitel (Standard: aus PDF extrahiert)
  --sort-order    Sortierreihenfolge des Kapitels (Standard: 0)
  --exam          Kapitel als prüfungsrelevant markieren
  --db            Pfad zur SQLite-DB (Standard: takvim.db)
  --dry-run       Nur analysieren, nichts schreiben
  --verbose       Ausführliche Ausgabe

Beispiele:
  python extract_pdf.py kapitel01_luftrecht.pdf \
      --subject-id luftrecht \
      --subject-title "Luftrecht & ATC-Verfahren" \
      --subject-code "010" \
      --subject-icon "⚖️" \
      --chapter-title "Lizenz, Medical & Dokumente" \
      --exam

  python extract_pdf.py met_wolken.pdf \
      --subject-id meteorologie \
      --subject-title "Meteorologie" \
      --subject-code "050" \
      --subject-icon "☁️" \
      --sort-order 3
═══════════════════════════════════════════════════════════════════════════════
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sqlite3
import sys
import unicodedata
from pathlib import Path
from typing import Any

# ── Optional dependency: pdfplumber (preferred) or PyMuPDF ──────────────────
try:
    import pdfplumber
    PDF_BACKEND = "pdfplumber"
except ImportError:
    pdfplumber = None

try:
    import fitz  # PyMuPDF
    PDF_BACKEND = "pymupdf"
except ImportError:
    fitz = None

if pdfplumber is None and fitz is None:
    print("❌  Weder pdfplumber noch PyMuPDF gefunden.")
    print("    Bitte installieren:")
    print("      pip install pdfplumber")
    print("    oder:")
    print("      pip install PyMuPDF")
    sys.exit(1)


# ═══════════════════════════════════════════════════════════════════════════════
# Datenbank
# ═══════════════════════════════════════════════════════════════════════════════

def get_db(path: str) -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    ensure_schema(conn)
    return conn


def ensure_schema(conn: sqlite3.Connection) -> None:
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS learn_subjects (
            id         TEXT    PRIMARY KEY,
            code       TEXT    NOT NULL DEFAULT '',
            title      TEXT    NOT NULL,
            icon       TEXT    DEFAULT '📖',
            color      TEXT    DEFAULT '#3b82f6',
            overview   TEXT    DEFAULT '',
            sort_order INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS learn_chapters (
            id            TEXT    PRIMARY KEY,
            subject_id    TEXT    NOT NULL,
            title         TEXT    NOT NULL,
            sort_order    INTEGER DEFAULT 0,
            exam_relevant INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS learn_sections (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_id TEXT    NOT NULL,
            type       TEXT    NOT NULL,
            content    TEXT    NOT NULL,
            extra      TEXT    DEFAULT NULL,
            sort_order INTEGER DEFAULT 0
        );
        CREATE TABLE IF NOT EXISTS learn_quiz (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            chapter_id  TEXT    NOT NULL,
            question    TEXT    NOT NULL,
            options     TEXT    NOT NULL,
            answer      INTEGER NOT NULL,
            explanation TEXT    DEFAULT '',
            is_official INTEGER DEFAULT 0,
            sort_order  INTEGER DEFAULT 0
        );
    """)
    # FTS5 – optional
    try:
        conn.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS learn_fts USING fts5(
                chapter_id    UNINDEXED,
                subject_id    UNINDEXED,
                chapter_title,
                subject_title UNINDEXED,
                content,
                tokenize = 'unicode61 remove_diacritics 1'
            )
        """)
    except Exception:
        pass
    conn.commit()


# ═══════════════════════════════════════════════════════════════════════════════
# PDF-Text-Extraktion
# ═══════════════════════════════════════════════════════════════════════════════

def extract_text_pdfplumber(pdf_path: str, verbose: bool = False) -> list[str]:
    """Gibt eine Liste von Seitentext-Strings zurück."""
    pages = []
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text(x_tolerance=2, y_tolerance=2) or ""
            pages.append(text)
            if verbose:
                print(f"  Seite {i+1}/{len(pdf.pages)}: {len(text)} Zeichen")
    return pages


def extract_text_pymupdf(pdf_path: str, verbose: bool = False) -> list[str]:
    pages = []
    doc = fitz.open(pdf_path)
    for i, page in enumerate(doc):
        text = page.get_text("text") or ""
        pages.append(text)
        if verbose:
            print(f"  Seite {i+1}/{len(doc)}: {len(text)} Zeichen")
    doc.close()
    return pages


def extract_pdf_text(pdf_path: str, verbose: bool = False) -> list[str]:
    if PDF_BACKEND == "pdfplumber":
        return extract_text_pdfplumber(pdf_path, verbose)
    else:
        return extract_text_pymupdf(pdf_path, verbose)


# ═══════════════════════════════════════════════════════════════════════════════
# Text-Analyse und Strukturierung
# ═══════════════════════════════════════════════════════════════════════════════

# Muster für Quizfragen (multiple-choice im deutschen Lehrbuch-Format)
RE_QUESTION_BLOCK = re.compile(
    r'(?:^|\n)(\d{4,6})\s*\n'          # Fragenummer (4-6 Ziffern)
    r'(.+?)\n'                          # Fragetext (1 Zeile)
    r'((?:\s*[A-D][.)]\s*.+\n?){2,5})',# Antwortoptionen A-D
    re.MULTILINE
)

# Alternativ: Fragen mit "Frage:" Präfix
RE_QUESTION_ALT = re.compile(
    r'(?:Frage|Q|Nr\.?)\s*:?\s*(\d+)\s*[\.\)]\s*\n?(.+?)\n'
    r'((?:\s*[A-Da-d][.)]\s*.+\n?){2,5})',
    re.MULTILINE | re.IGNORECASE
)

RE_ANSWER_OPT   = re.compile(r'^\s*([A-Da-d])[.)]\s*(.+)$', re.MULTILINE)
RE_CORRECT_MARK = re.compile(r'[✓✔★\*\[\s]?[Xx✓]\]?', re.UNICODE)

# Erkennungsmuster für Abschnittstypen
RE_HEADING      = re.compile(r'^([A-Z][A-Za-zÄÖÜäöüß\s\-&/]{3,60})$', re.MULTILINE)
RE_BULLET       = re.compile(r'^\s*[•·▪▸\-–—]\s+(.+)$', re.MULTILINE)
RE_NUMBERED     = re.compile(r'^\s*\d+[.)]\s+(.+)$', re.MULTILINE)

MERKSATZ_TRIGGERS = [
    'Merke:', 'Wichtig:', 'Achtung:', 'Hinweis:', 'Note:', 'Key:', 'Regel:',
    'Faustformel:', 'Definition:', 'Grundsatz:', 'Grundregel:'
]


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text)
    text = ''.join(c for c in text if not unicodedata.combining(c))
    text = text.lower()
    text = re.sub(r'[äöü]', lambda m: {'ä':'ae','ö':'oe','ü':'ue'}[m.group()], text)
    text = re.sub(r'[^a-z0-9]+', '-', text)
    return text.strip('-')[:60]


def parse_pages(pages: list[str], chapter_id: str, subject_title: str,
                chapter_title: str, verbose: bool = False) -> dict[str, Any]:
    """
    Analysiert den Rohtext und liefert strukturierte Daten:
      - summaries : Erklärungstexte
      - facts     : Merksätze / Bullet-Points
      - focuses   : Prüfungsschwerpunkte
      - tables    : [(Begriff, Erklärung)]
      - quiz      : [{q, options, answer, explanation, is_official}]
    """
    full_text = "\n".join(pages)

    result: dict[str, Any] = {
        "summaries": [],
        "facts":     [],
        "focuses":   [],
        "tables":    [],
        "quiz":      [],
    }

    # ── Quiz-Fragen extrahieren ─────────────────────────────────────────────
    quiz_questions = extract_quiz_questions(full_text, verbose)
    result["quiz"] = quiz_questions

    # ── Text nach Quiz-Blöcken bereinigen ───────────────────────────────────
    clean_text = remove_quiz_blocks(full_text)

    # ── Paragraphen extrahieren ─────────────────────────────────────────────
    paragraphs = extract_paragraphs(clean_text)

    # ── Klassifizieren ──────────────────────────────────────────────────────
    for para in paragraphs:
        classify_paragraph(para, result)

    # ── Prüfungsschwerpunkte heuristisch erkennen ──────────────────────────
    if not result["focuses"]:
        result["focuses"] = extract_exam_focuses(clean_text)

    # Duplikate entfernen
    result["summaries"] = deduplicate(result["summaries"])
    result["facts"]     = deduplicate(result["facts"])
    result["focuses"]   = deduplicate(result["focuses"])[:8]  # max 8

    if verbose:
        print(f"  → {len(result['summaries'])} Zusammenfassungs-Absätze")
        print(f"  → {len(result['facts'])} Merksätze")
        print(f"  → {len(result['focuses'])} Prüfungsschwerpunkte")
        print(f"  → {len(result['tables'])} Tabellen-Zeilen")
        print(f"  → {len(result['quiz'])} Quizfragen")

    return result


def extract_quiz_questions(text: str, verbose: bool = False) -> list[dict]:
    questions = []
    seen_qs   = set()

    def parse_options(opts_text: str) -> tuple[list[str], int]:
        """Gibt (Optionsliste, korrekter Index) zurück. Korrekte Antwort erkannt durch Markierung."""
        lines   = RE_ANSWER_OPT.findall(opts_text)
        options = []
        answer  = 0
        for i, (letter, text) in enumerate(lines):
            text = text.strip()
            # Korrekte Antwort oft markiert: ✓, *, [X], (richtig) etc.
            if RE_CORRECT_MARK.search(text) or '(richtig)' in text.lower() or '(correct)' in text.lower():
                answer = i
                text = RE_CORRECT_MARK.sub('', text).replace('(richtig)', '').replace('(correct)', '').strip()
            options.append(text)
        return options, answer

    # Versuch 1: Numerierte Fragen (vierstellige ID)
    for m in RE_QUESTION_BLOCK.finditer(text):
        q_num  = m.group(1)
        q_text = m.group(2).strip()
        opts_t = m.group(3)
        if q_text in seen_qs: continue
        seen_qs.add(q_text)
        opts, ans = parse_options(opts_t)
        if len(opts) >= 2:
            questions.append({
                "q":           q_text,
                "options":     opts,
                "answer":      ans,
                "explanation": f"Frage-Nr. {q_num} aus dem offiziellen Fragenkatalog.",
                "is_official": True,
                "sort_order":  int(q_num) if q_num.isdigit() else 0
            })

    # Versuch 2: Alternative Formate
    if not questions:
        for m in RE_QUESTION_ALT.finditer(text):
            q_text = m.group(2).strip()
            opts_t = m.group(3)
            if q_text in seen_qs: continue
            seen_qs.add(q_text)
            opts, ans = parse_options(opts_t)
            if len(opts) >= 2:
                questions.append({
                    "q":           q_text,
                    "options":     opts,
                    "answer":      ans,
                    "explanation": "",
                    "is_official": False,
                    "sort_order":  len(questions)
                })

    if verbose and questions:
        print(f"    Quiz: {len(questions)} Fragen erkannt")

    return questions


def remove_quiz_blocks(text: str) -> str:
    text = RE_QUESTION_BLOCK.sub('', text)
    text = RE_QUESTION_ALT.sub('', text)
    return text


def extract_paragraphs(text: str) -> list[str]:
    """Teilt Text in sinnvolle Absätze auf."""
    # Doppelzeilenumbrüche → Absatzgrenzen
    paras = re.split(r'\n{2,}', text)
    result = []
    for p in paras:
        p = p.strip()
        # Seitenzahlen, Kopfzeilen, leere Zeilen überspringen
        if len(p) < 30: continue
        if re.match(r'^\d+$', p): continue
        if re.match(r'^Seite\s+\d+', p): continue
        result.append(p)
    return result


def classify_paragraph(para: str, result: dict) -> None:
    """Klassifiziert einen Absatz und fügt ihn der richtigen Liste hinzu."""
    # Merksätze / Facts
    for trigger in MERKSATZ_TRIGGERS:
        if para.startswith(trigger):
            fact = para[len(trigger):].strip().strip(':').strip()
            if fact:
                result["facts"].append(fact)
            return

    # Bullet-Point-Listen → Facts
    bullets = RE_BULLET.findall(para)
    if len(bullets) >= 2:
        result["facts"].extend(b.strip() for b in bullets if len(b.strip()) > 10)
        return

    # Tabellen-ähnliche Zeilen (Zwei-Spalten-Muster: "Begriff: Erklärung")
    table_match = re.match(r'^([A-Za-z0-9ÄÖÜäöüß\-/\s]{3,35}):\s+(.{15,})$', para)
    if table_match:
        key = table_match.group(1).strip()
        val = table_match.group(2).strip()
        if len(val.split()) >= 3:  # mindestens 3 Wörter
            result["tables"].append((key, val))
            return

    # Prüfungsschwerpunkte
    if any(w in para.lower() for w in ['prüfungsrelevant', 'prüfungsstoff', 'klausur', 'wichtig für']):
        result["focuses"].append(para)
        return

    # Normaler Text → Summary
    # Nur wenn Satz min. 40 Zeichen und keine reine Überschrift
    if len(para) >= 40 and not RE_HEADING.match(para):
        # Langer Text → in Sätze aufteilen und zusammenfassen
        sentences = re.split(r'(?<=[.!?])\s+', para)
        chunk = ""
        for s in sentences:
            chunk += s + " "
            if len(chunk) > 250:
                result["summaries"].append(chunk.strip())
                chunk = ""
        if chunk.strip() and len(chunk.strip()) >= 40:
            result["summaries"].append(chunk.strip())


def extract_exam_focuses(text: str) -> list[str]:
    """Erkennt heuristisch prüfungsrelevante Punkte."""
    focuses = []
    patterns = [
        r'(?:Prüfungsrelevant|Wichtig|Merke|Achtung)[:\s]+(.{20,120})',
        r'(?:Der Prüfling muss|Der Pilot muss|Es ist wichtig)[,\s]+(.{20,120})',
    ]
    for pat in patterns:
        for m in re.finditer(pat, text, re.IGNORECASE):
            focuses.append(m.group(1).strip())
    return focuses[:6]


def deduplicate(items: list[str]) -> list[str]:
    seen = set()
    result = []
    for item in items:
        key = item[:50].lower().strip()
        if key not in seen:
            seen.add(key)
            result.append(item)
    return result


# ═══════════════════════════════════════════════════════════════════════════════
# Datenbank-Schreiboperationen
# ═══════════════════════════════════════════════════════════════════════════════

def upsert_subject(conn: sqlite3.Connection, subject_id: str, code: str,
                   title: str, icon: str, color: str, sort_order: int,
                   overview: str = "") -> None:
    conn.execute("""
        INSERT INTO learn_subjects (id, code, title, icon, color, overview, sort_order)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            code       = excluded.code,
            title      = excluded.title,
            icon       = excluded.icon,
            color      = excluded.color,
            sort_order = excluded.sort_order
    """, (subject_id, code, title, icon, color, overview, sort_order))
    conn.commit()


def upsert_chapter(conn: sqlite3.Connection, chapter_id: str, subject_id: str,
                   title: str, sort_order: int, exam_relevant: bool) -> None:
    conn.execute("""
        INSERT INTO learn_chapters (id, subject_id, title, sort_order, exam_relevant)
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title         = excluded.title,
            sort_order    = excluded.sort_order,
            exam_relevant = excluded.exam_relevant
    """, (chapter_id, subject_id, title, sort_order, int(exam_relevant)))
    conn.commit()


def clear_chapter_content(conn: sqlite3.Connection, chapter_id: str) -> None:
    """Löscht bestehende Sections und Quiz-Fragen eines Kapitels (für Neuimport)."""
    conn.execute("DELETE FROM learn_sections WHERE chapter_id = ?", (chapter_id,))
    conn.execute("DELETE FROM learn_quiz     WHERE chapter_id = ?", (chapter_id,))
    # FTS bereinigen
    try:
        conn.execute("DELETE FROM learn_fts WHERE chapter_id = ?", (chapter_id,))
    except Exception:
        pass
    conn.commit()


def insert_sections(conn: sqlite3.Connection, chapter_id: str,
                    data: dict[str, Any]) -> int:
    rows  = []
    order = 0

    for s in data["summaries"]:
        rows.append((chapter_id, "summary", s, None, order)); order += 1

    for f in data["facts"]:
        rows.append((chapter_id, "fact", f, None, order)); order += 1

    for fc in data["focuses"]:
        rows.append((chapter_id, "focus", fc, None, order)); order += 1

    for (k, v) in data["tables"]:
        rows.append((chapter_id, "table_row", k, v, order)); order += 1

    if rows:
        conn.executemany("""
            INSERT INTO learn_sections (chapter_id, type, content, extra, sort_order)
            VALUES (?, ?, ?, ?, ?)
        """, rows)
        conn.commit()

    return len(rows)


def insert_quiz(conn: sqlite3.Connection, chapter_id: str,
                quiz: list[dict]) -> int:
    rows = []
    for i, q in enumerate(quiz):
        opts_json = json.dumps(q["options"], ensure_ascii=False)
        rows.append((
            chapter_id,
            q["q"],
            opts_json,
            q["answer"],
            q.get("explanation", ""),
            int(q.get("is_official", False)),
            q.get("sort_order", i)
        ))
    if rows:
        conn.executemany("""
            INSERT INTO learn_quiz
                (chapter_id, question, options, answer, explanation, is_official, sort_order)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, rows)
        conn.commit()
    return len(rows)


def update_fts(conn: sqlite3.Connection, chapter_id: str, subject_id: str,
               chapter_title: str, subject_title: str,
               data: dict[str, Any]) -> None:
    """Befüllt den FTS-Index für Volltextsuche."""
    try:
        # Alle Inhalte als durchsuchbaren Text zusammenführen
        all_text_parts = (
            data["summaries"] + data["facts"] + data["focuses"] +
            [f"{k} {v}" for k, v in data["tables"]] +
            [q["q"] for q in data["quiz"]]
        )
        combined = " ".join(all_text_parts)

        conn.execute("""
            INSERT INTO learn_fts (chapter_id, subject_id, chapter_title, subject_title, content)
            VALUES (?, ?, ?, ?, ?)
        """, (chapter_id, subject_id, chapter_title, subject_title, combined))
        conn.commit()
    except Exception as e:
        pass  # FTS ist optional


# ═══════════════════════════════════════════════════════════════════════════════
# Haupt-Pipeline
# ═══════════════════════════════════════════════════════════════════════════════

def process_pdf(args: argparse.Namespace) -> None:
    pdf_path = args.pdf
    if not os.path.isfile(pdf_path):
        print(f"❌  Datei nicht gefunden: {pdf_path}")
        sys.exit(1)

    # IDs und Titel ableiten
    pdf_stem     = Path(pdf_path).stem
    subject_id   = args.subject_id   or slugify(args.subject_title or pdf_stem)
    chapter_id   = args.chapter_id   or f"{subject_id}-{slugify(args.chapter_title or pdf_stem)}"
    chapter_title = args.chapter_title or pdf_stem.replace('_', ' ').replace('-', ' ').title()
    subject_title = args.subject_title or subject_id.replace('-', ' ').title()

    print(f"📖  Verarbeite: {pdf_path}")
    print(f"    Backend:       {PDF_BACKEND}")
    print(f"    Fach-ID:       {subject_id}")
    print(f"    Fach-Titel:    {subject_title}")
    print(f"    Kapitel-ID:    {chapter_id}")
    print(f"    Kapitel-Titel: {chapter_title}")
    print(f"    Prüfungsrel.:  {'Ja' if args.exam else 'Nein'}")
    print()

    # Text extrahieren
    print("📄  Text wird extrahiert…")
    pages = extract_pdf_text(pdf_path, verbose=args.verbose)
    total_chars = sum(len(p) for p in pages)
    print(f"    {len(pages)} Seiten · {total_chars:,} Zeichen extrahiert")
    print()

    # Struktur analysieren
    print("🔍  Struktur wird analysiert…")
    data = parse_pages(pages, chapter_id, subject_title, chapter_title,
                       verbose=args.verbose)
    print(f"    {len(data['summaries'])} Textabschnitte")
    print(f"    {len(data['facts'])} Merksätze")
    print(f"    {len(data['focuses'])} Prüfungsschwerpunkte")
    print(f"    {len(data['tables'])} Tabellen-Einträge")
    print(f"    {len(data['quiz'])} Quizfragen ({sum(1 for q in data['quiz'] if q.get('is_official'))} offiziell)")
    print()

    if args.dry_run:
        print("🔄  Dry-run – nichts wird in die DB geschrieben.")
        if args.verbose:
            print("\n── Erste 3 Textabschnitte ──────────────────────────────────")
            for s in data["summaries"][:3]:
                print(f"  {s[:120]}…")
            if data["quiz"]:
                print("\n── Erste Quiz-Frage ───────────────────────────────────────")
                q = data["quiz"][0]
                print(f"  F: {q['q']}")
                for i, o in enumerate(q["options"]):
                    marker = "✓" if i == q["answer"] else " "
                    print(f"  [{marker}] {chr(65+i)}) {o}")
        return

    # Datenbank schreiben
    db_path = args.db
    if not os.path.isfile(db_path):
        print(f"❌  Datenbank nicht gefunden: {db_path}")
        print("    Führe zuerst 'python init_db.py' aus.")
        sys.exit(1)

    print(f"💾  Schreibe in Datenbank: {db_path}")
    conn = get_db(db_path)

    # Fach anlegen / aktualisieren
    upsert_subject(
        conn,
        subject_id=subject_id,
        code=args.subject_code or "",
        title=subject_title,
        icon=args.subject_icon or "📖",
        color=args.subject_color or "#3b82f6",
        sort_order=args.subject_sort or 0,
    )
    print(f"    ✓ Fach '{subject_title}' gespeichert")

    # Kapitel anlegen / aktualisieren
    upsert_chapter(
        conn,
        chapter_id=chapter_id,
        subject_id=subject_id,
        title=chapter_title,
        sort_order=args.sort_order or 0,
        exam_relevant=args.exam,
    )
    print(f"    ✓ Kapitel '{chapter_title}' gespeichert")

    # Bestehenden Inhalt löschen (Re-Import)
    clear_chapter_content(conn, chapter_id)

    # Sections und Quiz einfügen
    n_secs = insert_sections(conn, chapter_id, data)
    n_quiz = insert_quiz(conn, chapter_id, data["quiz"])
    update_fts(conn, chapter_id, subject_id, chapter_title, subject_title, data)

    print(f"    ✓ {n_secs} Abschnitte gespeichert")
    print(f"    ✓ {n_quiz} Quizfragen gespeichert")
    print()
    print("✅  Import erfolgreich abgeschlossen!")
    print(f"    Die Lernplattform zeigt das Kapitel '{chapter_title}'")
    print(f"    unter Fach '{subject_title}' (ID: {subject_id})")


# ═══════════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="PPL(A) Lernplattform – PDF-Inhaltsextraktor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument("pdf", help="Pfad zur PDF-Datei")

    # Fach
    parser.add_argument("--subject-id",    default=None, help="Fach-ID (z. B. 'meteorologie')")
    parser.add_argument("--subject-title", default=None, help="Fach-Titel")
    parser.add_argument("--subject-code",  default="",   help="Prüfungsfach-Kürzel")
    parser.add_argument("--subject-icon",  default="📖", help="Emoji für das Fach")
    parser.add_argument("--subject-color", default="#3b82f6", help="Hex-Farbe")
    parser.add_argument("--subject-sort",  default=0,    type=int, help="Sortierreihenfolge des Fachs")

    # Kapitel
    parser.add_argument("--chapter-id",    default=None, help="Kapitel-ID (automatisch abgeleitet)")
    parser.add_argument("--chapter-title", default=None, help="Kapiteltitel")
    parser.add_argument("--sort-order",    default=0,    type=int, help="Sortierreihenfolge")
    parser.add_argument("--exam",          action="store_true",    help="Als prüfungsrelevant markieren")

    # System
    parser.add_argument("--db",      default="takvim.db", help="Pfad zur SQLite-DB")
    parser.add_argument("--dry-run", action="store_true", help="Nur analysieren, nicht schreiben")
    parser.add_argument("--verbose", action="store_true", help="Ausführliche Ausgabe")

    args = parser.parse_args()
    process_pdf(args)


if __name__ == "__main__":
    main()
