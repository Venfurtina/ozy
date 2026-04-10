# PPL(A) Lernplattform – Inhalts-Import-Anleitung

## Systemvoraussetzungen

```bash
pip install -r requirements.txt
```

## Chat-Workflow (26 PDFs auf 13 Chats verteilt)

Jeder neue Chat erhält **2 PDFs** und die **aktuelle site_final.zip**.

### Schritt 1: PDF importieren (pro Chat)

```bash
# PDF 1 importieren
python extract_pdf.py <pdf1.pdf> \
    --subject-id <fach_id> \
    --subject-title "<Fach-Titel>" \
    --subject-code "<Code>" \
    --subject-icon "<Emoji>" \
    --chapter-title "<Kapitel-Titel>" \
    --sort-order <0,1,2,...> \
    --exam \
    --verbose

# PDF 2 importieren
python extract_pdf.py <pdf2.pdf> \
    --subject-id <fach_id> \
    --subject-title "<Fach-Titel>" \
    --subject-code "<Code>" \
    --chapter-title "<Kapitel-Titel>" \
    --sort-order <nächste Nummer> \
    --verbose
```

### Schritt 2: Ergebnis prüfen

```bash
python -m flask run --debug
# → http://localhost:5000/learn
```

### Schritt 3: Zip für nächsten Chat

```bash
zip -r site_final_v2.zip site_final/
```

---

## PPL(A) Fach-IDs (Referenz)

| Code | ID              | Titel                              | Icon |
|------|-----------------|-------------------------------------|------|
| 010  | luftrecht        | Luftrecht & ATC-Verfahren           | ⚖️  |
| 020  | flugzeugkunde    | Allgemeine Luftfahrzeugkunde (AGK)  | 🔧   |
| 021  | triebwerk        | Triebwerk & Systeme                 | ⚙️  |
| 022  | avionik          | Avionik & Instrumente               | 🎛️ |
| 031  | flugplanung      | Flugplanung & Durchführung          | 📋   |
| 032  | leistung         | Flugleistung & Flugplanung         | 📊   |
| 040  | menschliche      | Menschliches Leistungsvermögen      | 🧠   |
| 050  | meteorologie     | Meteorologie                        | ☁️  |
| 060  | navigation       | Navigation                          | 🧭   |
| 070  | betriebsverfahren| Betriebliche Verfahren             | 📡   |
| 080  | fluglehre        | Grundlagen des Fliegens (Fluglehre) | ✈️  |
| 090  | kommunikation    | Kommunikation (Sprechfunk)          | 📻   |

---

## Beispiel: Vollständiger Import für "Luftrecht" Kapitel 1

```bash
python extract_pdf.py buch_luftrecht_kap1.pdf \
    --subject-id luftrecht \
    --subject-title "Luftrecht & ATC-Verfahren" \
    --subject-code "010" \
    --subject-icon "⚖️" \
    --subject-color "#60a5fa" \
    --subject-sort 1 \
    --chapter-title "Lizenz, Medical & Dokumente (Part-FCL, Part-MED)" \
    --sort-order 1 \
    --exam \
    --db takvim.db \
    --verbose
```

---

## Datenbankstruktur (Übersicht)

```
learn_subjects  → Prüfungsfächer (Luftrecht, Meteorologie, etc.)
learn_chapters  → Kapitel pro Fach
learn_sections  → Textinhalte (summary, fact, focus, table_row, source)
learn_quiz      → Quizfragen (multiple-choice, 4 Optionen, korrekte Antwort)
learn_fts       → Volltextsuchindex (SQLite FTS5)
quiz_scores     → Benutzer-Quizscores (pro Kapitel)
```

## Tipp: Dry-Run vor dem echten Import

```bash
python extract_pdf.py mein_pdf.pdf --subject-id test --dry-run --verbose
```

Zeigt, was extrahiert würde, ohne die DB zu verändern.
