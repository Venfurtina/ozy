"""
fill_human_hpl.py – Expands the 'Menschliches Leistungsvermögen' subject
with comprehensive content from Advanced PPL-Guide Band 6 (AirCademy).

Chapters added / replaced:
  human-basics       → 1.1 Physikalische Grundlagen
  human-physiology   → 1.2 Sauerstoff und Blutkreislauf  (replaces/expands existing)
  human-perception   → 1.3 Menschliche Wahrnehmung
  human-flight       → 1.4 Physiologische Auswirkungen des Fliegens
  human-performance  → 2.x Flugpsychologie                (replaces/expands existing)
"""

import sqlite3, json, os

BASE = os.path.dirname(os.path.abspath(__file__))
DB   = os.path.join(BASE, "takvim.db")

# ── helpers ──────────────────────────────────────────────────────────────────
def add_section(cur, chapter_id, sec_type, content, extra=None, order=0):
    cur.execute(
        "INSERT INTO learn_sections (chapter_id, type, content, extra, sort_order) VALUES (?,?,?,?,?)",
        (chapter_id, sec_type, content, extra, order)
    )

def add_quiz(cur, chapter_id, question, options, answer, explanation, is_official=0, order=0):
    cur.execute(
        "INSERT INTO learn_quiz (chapter_id, question, options, answer, explanation, is_official, sort_order) "
        "VALUES (?,?,?,?,?,?,?)",
        (chapter_id, question, json.dumps(options, ensure_ascii=False), answer, explanation, is_official, order)
    )

def add_flashcard(cur, chapter_id, front, back, order=0):
    cur.execute(
        "INSERT INTO learn_flashcards (chapter_id, front, back, sort_order) VALUES (?,?,?,?)",
        (chapter_id, front, back, order)
    )

def clear_chapter(cur, cid):
    cur.execute("DELETE FROM learn_sections   WHERE chapter_id=?", (cid,))
    cur.execute("DELETE FROM learn_quiz        WHERE chapter_id=?", (cid,))
    cur.execute("DELETE FROM learn_flashcards  WHERE chapter_id=?", (cid,))
    cur.execute("DELETE FROM learn_fts         WHERE chapter_id=?", (cid,))

def upsert_chapter(cur, cid, subject_id, title, sort_order, exam_relevant=1):
    cur.execute(
        "INSERT OR REPLACE INTO learn_chapters (id, subject_id, title, sort_order, exam_relevant) "
        "VALUES (?,?,?,?,?)",
        (cid, subject_id, title, sort_order, exam_relevant)
    )


# ═══════════════════════════════════════════════════════════════════════════════
#  CHAPTER 1 – Physikalische Grundlagen (1.1)
# ═══════════════════════════════════════════════════════════════════════════════
def fill_basics(cur):
    cid = "human-basics"
    upsert_chapter(cur, cid, "human", "1.1 Physikalische Grundlagen", 1)
    clear_chapter(cur, cid)

    summaries = [
        "Die Flugphysiologie beginnt mit den physikalischen Grundlagen der Atmosphäre. "
        "Die Erde ist von einer Gashülle umgeben, deren Zusammensetzung bis etwa 60 km Höhe "
        "annähernd gleichbleibend ist: 78 % Stickstoff, 21 % Sauerstoff, 1 % Edelgase sowie "
        "variabler Wasserdampfanteil (bis 4 %). Für Berechnungen wird die ICAO-Standard-Atmosphäre "
        "(ISA) verwendet.",
        "Der für die Flugphysiologie entscheidende Atmosphärendruck halbiert sich je 5.500 m "
        "(ca. 18.000 ft). Neben dem Gesamtdruck ist der Gesetz von Boyle-Mariotte, Gay-Lussac "
        "und Amontons wichtig: Druckänderungen bewirken Volumenänderungen in gasgefüllten "
        "Körperhohlräumen — ein zentraler Auslöser von Barotraumen.",
    ]
    for i, s in enumerate(summaries):
        add_section(cur, cid, "summary", s, order=i)

    facts = [
        "Die Luft besteht zu 78 % aus Stickstoff, 21 % Sauerstoff und 1 % Edelgasen.",
        "Der Atmosphärendruck halbiert sich alle 5.500 m (18.000 ft).",
        "Boyle-Mariotte: Bei konstanter Temperatur ist Druck × Volumen = konstant (p × V = const.).",
        "Gay-Lussac: Bei konstantem Druck ist das Volumen proportional zur Temperatur (V ~ T).",
        "Amontons: Bei konstantem Volumen ist der Druck proportional zur Temperatur (p ~ T).",
        "Das Gesetz von Dalton: Der Partialdruck eines Gases entspricht seinem Anteil am Gesamtdruck. "
        "Sauerstoffpartialdruck in MSL ≈ 213 hPa (21 % × 1.013 hPa).",
        "Das Gesetz von Henry: Die Menge eines in einer Flüssigkeit gelösten Gases ist proportional "
        "zu seinem Partialdruck über der Flüssigkeit — Grundlage der Caissonkrankheit.",
        "Wasser dampf kann bis zu 4 % Anteil haben; mit steigendem Wasserdampf sinken die anderen Anteile.",
    ]
    for i, f in enumerate(facts):
        add_section(cur, cid, "fact", f, order=i)

    table_rows = [
        ["Boyle-Mariotte", "p × V = const. (T konstant) – Gas dehnt sich bei Druckabfall aus"],
        ["Gay-Lussac", "V ~ T (p konstant) – Gas dehnt sich bei Erwärmung aus"],
        ["Amontons (2. Gesetz von Gay-Lussac)", "p ~ T (V konstant) – Druck steigt mit Temperatur"],
        ["Dalton", "Partialdruck = Gesamtdruck × Stoffanteil"],
        ["Henry", "Gelöste Gasmenge in Flüssigkeit ~ Partialdruck über der Flüssigkeit"],
        ["ICAO-Standardatmosphäre (ISA)", "Referenz: MSL 1.013,25 hPa, +15 °C; Temperaturabnahme 6,5 °C/1.000 m"],
        ["Sauerstoffpartialdruck MSL", "≈ 213 hPa (21 % von 1.013 hPa)"],
    ]
    for row in table_rows:
        add_section(cur, cid, "table_row", json.dumps(row, ensure_ascii=False))

    focuses = [
        "Gasgesetze und ihre Auswirkungen auf gasgefüllte Körperhohlräume kennen",
        "Partialdruck-Begriff und Berechnung verstehen",
        "ICAO-ISA-Werte für MSL und typische Höhen parat haben",
        "Gesetz von Henry als Grundlage der Caissonkrankheit erkennen",
    ]
    for f in focuses:
        add_section(cur, cid, "focus", f)

    # ── Quiz – includes all official Übungsaufgaben 1.1 from book ──────────────
    quizzes = [
        # Offizielle Buchfragen
        ("Wie verändert sich der Luftdruck mit zunehmender Höhe?",
         ["Er steigt linear an",
          "Er bleibt konstant",
          "Er nimmt exponentiell ab und halbiert sich je ca. 5.500 m",
          "Er schwankt je nach Tageszeit stark"],
         2,
         "Der Atmosphärendruck nimmt mit der Höhe exponentiell ab. Er halbiert sich je ca. 5.500 m "
         "(18.000 ft). Dies ist prüfungsrelevant, weil es Sauerstoffpartialdruck und Körpervolumina beeinflusst.",
         1),
        ("Welchen Partialdruck hat Sauerstoff in der Atmosphäre unter Standardbedingungen in MSL?",
         ["210 hPa",
          "213 hPa",
          "1.013 hPa",
          "Nachts 210 hPa, tagsüber 213 hPa"],
         1,
         "21 % × 1.013,25 hPa ≈ 213 hPa. 1.013 hPa ist der Gesamtluftdruck in MSL, nicht der Sauerstoffpartialdruck.",
         1),
        ("Wie verhält sich der Druck, wenn ein ideales Gaspaket bei konstantem Volumen erwärmt wird?",
         ["Der Druck bleibt konstant",
          "Der Druck sinkt",
          "Der Druck steigt proportional zur absoluten Temperatur (Gesetz von Amontons)",
          "Der Druck ändert sich nur nachts"],
         2,
         "Das Gesetz von Amontons (zweites Gesetz von Gay-Lussac) besagt: p ~ T bei konstantem Volumen. "
         "Erwärmung erhöht den Druck.",
         1),
        ("Welche Eigenschaften ändern sich bei einem in der Erdatmosphäre aufsteigenden Gaspaket nach Gay-Lussac?",
         ["Nur der Druck ändert sich",
          "Das Volumen nimmt bei gleichem Druck mit der Temperatur zu oder ab",
          "Die Zusammensetzung ändert sich",
          "Nur die Dichte bleibt konstant"],
         1,
         "Gay-Lussac: V ~ T bei konstantem Druck. Ein aufsteigendes Gaspaket kühlt sich ab, "
         "sein Volumen nimmt ab. Im aufsteigenden Körper (Lunge) dehnen sich Gase aus, weil der Außendruck sinkt.",
         1),
        ("Was beschreibt das Gesetz von Dalton?",
         ["Dass Gase sich bei Erwärmung ausdehnen",
          "Dass der Partialdruck jedes Gases in einem Gemisch seinem Anteil am Gesamtdruck entspricht",
          "Dass Druck und Volumen proportional zueinander sind",
          "Dass Flüssigkeiten Gase lösen"],
         1,
         "Dalton: Gesamtdruck = Summe aller Partialdrücke. Der Sauerstoffpartialdruck = 21 % × Gesamtdruck.",
         1),
        ("Was besagt das Gesetz von Henry?",
         ["Gase dehnen sich bei Druckabfall aus",
          "Die in einer Flüssigkeit gelöste Gasmenge ist proportional zum Partialdruck des Gases über der Flüssigkeit",
          "Temperatur und Druck sind umgekehrt proportional",
          "Volumen und Temperatur sind umgekehrt proportional"],
         1,
         "Henry ist die physikalische Grundlage der Caissonkrankheit: Taucher lösen bei hohem Druck "
         "viel N₂ im Blut. Steigt der Druck schnell ab, perlt N₂ aus wie Kohlensäure in einer geöffneten Flasche.",
         1),
        # Zusatzfragen
        ("Welche Gaszusammensetzung hat die Erdatmosphäre bis etwa 60 km Höhe?",
         ["50 % Stickstoff, 50 % Sauerstoff",
          "78 % Stickstoff, 21 % Sauerstoff, 1 % Edelgase",
          "90 % Stickstoff, 10 % Sauerstoff",
          "60 % Stickstoff, 39 % Sauerstoff, 1 % CO₂"],
         1,
         "Die Zusammensetzung der Atmosphäre ist bis ca. 60 km annähernd konstant: 78 % N₂, 21 % O₂, 1 % Edelgase. "
         "Wasserdampf variiert bis zu 4 %, weshalb andere Anteile entsprechend sinken.",
         0),
        ("Was passiert mit gasgefüllten Körperhohlräumen (Ohren, Nasennebenhöhlen) beim Steigflug?",
         ["Das Gasvolumen schrumpft",
          "Das Gasvolumen bleibt konstant",
          "Das Gasvolumen dehnt sich aus (Boyle-Mariotte)",
          "Der Gasdruck steigt"],
         2,
         "Bei abnehmendem Außendruck (Steigflug) dehnen sich Gase in geschlossenen Räumen aus (Boyle-Mariotte). "
         "Kann das Gas nicht entweichen, entstehen Barotraumen.",
         0),
    ]
    for i, (q, opts, ans, expl, official) in enumerate(quizzes):
        add_quiz(cur, cid, q, opts, ans, expl, official, i)

    flashcards = [
        ("Boyle-Mariotte", "p × V = const. bei konstanter Temperatur. Druck sinkt → Volumen steigt."),
        ("Gay-Lussac", "V ~ T bei konstantem Druck. Abkühlung → Volumen sinkt."),
        ("Amontons", "p ~ T bei konstantem Volumen. Erwärmung → Druck steigt."),
        ("Dalton", "Gesamtdruck = Summe der Partialdrücke. O₂-Partialdruck in MSL ≈ 213 hPa."),
        ("Henry", "Gelöste Gasmenge in Flüssigkeit ist proportional zum Partialdruck darüber."),
        ("ICAO-ISA in MSL", "1.013,25 hPa, +15 °C, Dichte 1,225 kg/m³."),
        ("Druckhalbierung", "Der Luftdruck halbiert sich ca. alle 5.500 m (18.000 ft)."),
    ]
    for i, (fr, bk) in enumerate(flashcards):
        add_flashcard(cur, cid, fr, bk, i)


# ═══════════════════════════════════════════════════════════════════════════════
#  CHAPTER 2 – Sauerstoff und Blutkreislauf (1.2) – expand existing chapter
# ═══════════════════════════════════════════════════════════════════════════════
def fill_physiology(cur):
    cid = "human-physiology"
    # Update title but keep id
    cur.execute("UPDATE learn_chapters SET title=?, sort_order=?, exam_relevant=1 WHERE id=?",
                ("1.2 Sauerstoff, Atmung und Blutkreislauf", 2, cid))
    clear_chapter(cur, cid)

    summaries = [
        "Atmung (Ventilation) und Blutkreislauf sind die Basis der Sauerstoffversorgung. "
        "Die äußere Atmung transportiert O₂ in die Lunge und CO₂ nach außen; "
        "die innere Atmung (Zellatmung) versorgt die Zellen. Hämoglobin in den roten Blutkörperchen "
        "ist der Sauerstoffträger. Bei 90 % Sättigung beginnt die Versorgung der Zellen kritisch zu werden.",
        "Hypoxie (Sauerstoffmangel im Blut) ist eine der gefährlichsten Bedrohungen im Flug, weil sie "
        "schleichend auftritt und die Selbstwahrnehmung trügt. Bereits ab ca. 7.000 ft MSL können erste "
        "Symptome auftreten. Die Betriebsordnung (LuftBO) schreibt ab 10.000 ft MSL Sauerstoff vor. "
        "CO (Kohlenmonoxid) bindet 200–300-mal fester an Hämoglobin als O₂ und ist geruchs- und geschmacklos.",
        "Hyperventilation (zu schnelles Atmen) führt zu einem CO₂-Abfall im Blut, was paradoxerweise "
        "zu Kribbeln, Schwindel und Benommenheit führt. Therapie: Atemfrequenz und -tiefe bewusst reduzieren "
        "oder kurz in eine Papiertüte atmen, um CO₂ zurückzugewinnen.",
    ]
    for i, s in enumerate(summaries):
        add_section(cur, cid, "summary", s, order=i)

    facts = [
        "Der Atemzyklus: Einatmen (Inspiration) = aktiv (Zwerchfell senkt sich); Ausatmen = passiv.",
        "Normale Atemfrequenz Erwachsener: 12–15 Atemzüge/Minute.",
        "Normales Atemzugvolumen: ca. 0,5 l (Vitalkapazität 4,5–6 l, Totalkapazität 6–7 l).",
        "Hämoglobin (Hb) in den Erythrozyten bindet O₂; mit CO₂ angereichert erscheint es bläulich.",
        "Kleiner Kreislauf: Herz → Lunge → Herz (CO₂/O₂-Austausch).",
        "Großer Kreislauf: Herz → Körperzellen → Herz (Nährstoff- und O₂-Transport).",
        "Blutvolumen Erwachsener ≈ 5 Liter; Herzschlag pumpt ≈ 70–80 ml → ca. 5 l/min Herzauswurf.",
        "Hypoxämische Hypoxie: zu wenig O₂ in der Luft (Höhe). Anämische Hypoxie: zu wenig Hb (CO!).",
        "Ischämische Hypoxie: eingeschränkte Durchblutung (Blackout). Histotoxische Hypoxie: Zellen können O₂ nicht verwerten.",
        "CO bindet 200–300× fester als O₂ an Hb; löst sich erst in Druckkammer wieder.",
        "Time of Useful Consciousness (TUC) in FL180 ≈ 20–30 Minuten; in FL280 ≈ 2,5–3 Minuten.",
        "Ab 10.000 ft MSL kann Sauerstoffmangel die Nachtsehfähigkeit einschränken.",
        "Hyperventilation: Atemtiefe/-frequenz reduzieren oder in Papiertüte atmen (CO₂ rückgewinnen).",
        "Diffusion ist vom Partialdruckunterschied abhängig: höherer Unterschied = schnellere Diffusion.",
    ]
    for i, f in enumerate(facts):
        add_section(cur, cid, "fact", f, order=i)

    table_rows = [
        ["Äußere Atmung (Ventilation)", "Transport von O₂ in die Lunge und CO₂ nach außen"],
        ["Innere Atmung (Zellatmung)", "O₂-Aufnahme und CO₂-Abgabe in den Körperzellen"],
        ["Hämoglobin (Hb)", "Sauerstoffträger in roten Blutkörperchen; wird mit O₂ hellrot, mit CO₂ bläulich"],
        ["Kleiner Kreislauf", "Rechtes Herz → Lunge → linkes Herz (Lungenkreislauf, CO₂/O₂-Austausch)"],
        ["Großer Kreislauf", "Linkes Herz → Körper → rechtes Herz (Körperkreislauf)"],
        ["Hypoxämische Hypoxie", "O₂-Partialdruck zu niedrig (Höhenflug)"],
        ["Anämische Hypoxie", "Zu wenig funktionsfähiges Hämoglobin (z. B. CO-Vergiftung, Blutverlust)"],
        ["Ischämische Hypoxie", "Eingeschränkte Organdurchblutung (Blackout, Herzinfarkt)"],
        ["Histotoxische Hypoxie", "Zellen können O₂ nicht verwerten (z. B. Alkohol, Schlafmittel)"],
        ["Time of Useful Consciousness", "FL180: 20–30 min | FL220: 10 min | FL250: 3–6 min | FL280: 2,5–3 min"],
        ["Hyperventilation", "Zu schnelles Atmen → CO₂-Abfall → Kribbeln, Schwindel, Benommenheit"],
        ["Atemzugvolumen (normal)", "≈ 0,5 l; Vitalkapazität 4,5–6 l"],
        ["LuftBO Sauerstoffpflicht", "Ab 10.000 ft MSL für alle Besatzungsmitglieder empfohlen; ab 12.000 ft Pflicht"],
    ]
    for row in table_rows:
        add_section(cur, cid, "table_row", json.dumps(row, ensure_ascii=False))

    focuses = [
        "Hypoxie-Symptome, Arten und Gegenmaßnahmen sicher unterscheiden",
        "CO-Gefahr: unsichtbar, geruchlos, bindet 200–300× stärker als O₂",
        "Time of Useful Consciousness (TUC) für typische Flugflächen kennen",
        "Hyperventilation vs. Hypoxie unterscheiden können",
        "LuftBO-Vorschriften zu Sauerstoff kennen",
    ]
    for f in focuses:
        add_section(cur, cid, "focus", f)

    quizzes = [
        # Offizielle Buchfragen (Übungsaufgaben 1.2)
        ("Welche Funktion hat die innere Atmung?",
         ["Transport von O₂ aus der Luft in die Lunge",
          "Gasaustausch zwischen Blut und Körperzellen (Zellatmung)",
          "Regulierung der Atemfrequenz",
          "Filterung von Schadstoffen in den Bronchien"],
         1,
         "Die innere Atmung (Zellatmung) bezeichnet den Gasaustausch zwischen Blut und Körperzellen: "
         "O₂ wird aufgenommen, CO₂ abgegeben.",
         1),
        ("Was passiert beim Einatmen (Inspiration)?",
         ["Das Zwerchfell hebt sich und Luft strömt heraus",
          "Das Zwerchfell senkt sich; Brustkorb weitet sich; Luft strömt bis in die Lungenbläschen",
          "Der Brustkorb senkt sich und der Sauerstoff diffundiert in den Bronchien",
          "Der Herzmuskel erzeugt einen Unterdruck"],
         1,
         "Beim Einatmen (aktive Phase) senkt sich das Zwerchfell, Teile der Rippenmuskulatur spannen an, "
         "der Brustkorb weitet sich. Dadurch entsteht ein Unterdruck, Luft strömt bis in die Alveolen.",
         1),
        ("Wie viele Atemzüge pro Minute sind bei einem Erwachsenen durchschnittlich normal?",
         ["5–6", "7–10", "12–15", "16–21"],
         2,
         "Die normale Atemfrequenz eines Erwachsenen liegt bei 12–15 Atemzügen pro Minute. "
         "Neugeborene atmen ca. 40–50-mal, Kinder ca. 20-mal pro Minute.",
         1),
        ("Wie hoch ist das normale Atemzugvolumen eines Erwachsenen?",
         ["2,5 Liter", "4 Liter", "0,5 Liter", "1,5 Liter"],
         2,
         "Das normale Atemzugvolumen (Ruheatmung) beträgt ca. 0,5 l. Die Vitalkapazität (maximal "
         "nutzbares Volumen) liegt bei 4,5–6 l; die Totalkapazität bei 6–7 l.",
         1),
        ("Welche Aufgabe haben weiße Blutkörperchen (Leukozyten) vor allem?",
         ["Sauerstofftransport", "Infektionsabwehr", "Blutgerinnung", "Temperaturregulierung"],
         1,
         "Weiße Blutkörperchen (Leukozyten) sind für die Immunabwehr zuständig. "
         "Sauerstofftransport: rote Blutkörperchen (Erythrozyten). Gerinnung: Blutplättchen (Thrombozyten).",
         1),
        ("Wie groß ist das Blutvolumen eines Erwachsenen, und wie viel wird pro Minute durch den Kreislauf gepumpt?",
         ["4 Liter / 2 Liter", "5 Liter / 4 Liter", "4 Liter / 5 Liter", "5 Liter / 5 Liter"],
         3,
         "Das Blutvolumen beträgt ca. 5 Liter. Pro Herzschlag werden 70–80 ml gepumpt. "
         "Bei 70–75 Schlägen/Minute ergibt das ca. 5 Liter/Minute.",
         1),
        ("Welche vier Hypoxiearten können unterschieden werden?",
         ["Hypoxämisch, Anämisch, Ischämisch, Histotoxisch",
          "Akut, Chronisch, Latent, Manifest",
          "Sauerstoff-, Kohlendioxid-, Stickstoff-, Edelgasmangel",
          "Peripher, Zentral, Diffus, Fokal"],
         0,
         "Die vier Hypoxiearten: Hypoxämisch (zu wenig O₂ in der Luft), Anämisch (zu wenig Hb, "
         "z. B. CO), Ischämisch (eingeschränkte Durchblutung), Histotoxisch (Zellen können O₂ nicht verwerten).",
         1),
        ("Wie viel Zeit verbleibt nach Eintreten der Handlungsunfähigkeit (TUC) in Flugfläche 180?",
         ["2,5 bis 3 Minuten", "3 bis 6 Minuten", "10 Minuten", "20 bis 30 Minuten"],
         3,
         "TUC in FL180 (≈ 5.486 m): 20–30 Minuten. In FL250 nur noch 3–6 Minuten, in FL280 nur 2,5–3 Minuten. "
         "Körperliche Anstrengung verkürzt die TUC erheblich.",
         1),
        ("Was ist Hyperventilation, und was sind typische Symptome?",
         ["Zu langsames Atmen; Symptom: Schläfrigkeit",
          "Zu schnelles/tiefes Atmen; Symptom: Kribbeln in Fingern, Schwindel, Taubheit",
          "Sauerstoffüberschuss; Symptom: Euphorie",
          "Kohlendioxidüberschuss; Symptom: Blackout"],
         1,
         "Hyperventilation: zu schnelles/tiefes Atmen → CO₂-Abfall im Blut → Kribbeln in Händen/Füßen, "
         "Schwindel, Sehstörungen, Konzentrationsschwäche. Gegenmaßnahme: Atemfrequenz reduzieren "
         "oder in Papiertüte atmen.",
         1),
        ("Welche Gegenmaßnahmen können bei eintretender Hyperventilation ergriffen werden?",
         ["Sauerstoffmaske anlegen und tief atmen",
          "Atemfrequenz und -tiefe bewusst reduzieren oder kurz in eine Papiertüte atmen",
          "Sofort landen",
          "Notruf absetzen und auf Kurs halten"],
         1,
         "Hyperventilation: Zu viel CO₂ wird ausgeatmet. Gegenmittel: Atemfrequenz/tiefe reduzieren "
         "oder in Papiertüte atmen (CO₂ rückgewinnen). Die Papiertüte erhöht den CO₂-Spiegel wieder.",
         1),
        ("Warum ist CO (Kohlenmonoxid) für Piloten besonders gefährlich?",
         ["Weil es einen starken Geruch hat und sofort erkannt wird",
          "Weil es sich 200–300-mal fester an Hämoglobin bindet als O₂ und geruchs- sowie geschmacklos ist",
          "Weil es nur in Höhen über 10.000 ft auftritt",
          "Weil es ausschließlich im Motorraum vorkommt"],
         1,
         "CO ist geruchs- und geschmacklos und bindet 200–300× fester an Hämoglobin als O₂. "
         "Bereits 0,1 % CO in der Luft kann zur völligen Handlungsunfähigkeit führen. "
         "CO-Detektoren im Cockpit sind daher wichtig.",
         1),
        # Zusatzfragen
        ("Wie wird Sauerstoff im Blut hauptsächlich transportiert?",
         ["Frei gelöst im Blutplasma",
          "Gebunden an Hämoglobin (Hb) in roten Blutkörperchen",
          "In Leukozyten gespeichert",
          "An Thrombozyten gebunden"],
         1,
         "Sauerstoff wird fast ausschließlich an Hämoglobin (Hb) in roten Blutkörperchen (Erythrozyten) "
         "gebunden transportiert. Nur ein kleiner Anteil ist frei im Plasma gelöst.",
         0),
        ("Ab welcher Höhe beginnen erste Hypoxie-Symptome typischerweise aufzutreten?",
         ["Ab 3.000 ft MSL",
          "Ab 7.000–10.000 ft MSL",
          "Erst ab 25.000 ft MSL",
          "Hypoxie tritt nur bei Überdruckflügen auf"],
         1,
         "Ab ca. 7.000 ft MSL kann die Sauerstoffversorgung des Gehirns beeinträchtigt werden "
         "(Einschränkung der Nachtsehfähigkeit). Ab 10.000–12.000 ft schreibt die LuftBO Sauerstoff vor.",
         0),
    ]
    for i, (q, opts, ans, expl, official) in enumerate(quizzes):
        add_quiz(cur, cid, q, opts, ans, expl, official, i)

    flashcards = [
        ("Hypoxämische Hypoxie", "O₂-Partialdruck zu niedrig (Höhe, dünne Luft)"),
        ("Anämische Hypoxie", "Zu wenig funktionsfähiges Hämoglobin – z. B. durch CO-Vergiftung oder Blutverlust"),
        ("Ischämische Hypoxie", "Eingeschränkte Organdurchblutung – z. B. Blackout, Herzinfarkt"),
        ("Histotoxische Hypoxie", "Zellen können O₂ nicht verwerten – z. B. Alkohol, Schlafmittel"),
        ("CO-Gefahr", "200–300× fester gebunden als O₂; geruchs- und geschmacklos; sofortige Handlungsunfähigkeit möglich"),
        ("TUC FL180", "20–30 Minuten"),
        ("TUC FL250", "3–6 Minuten"),
        ("TUC FL280", "2,5–3 Minuten"),
        ("Hyperventilation Therapie", "Atemfrequenz/-tiefe reduzieren oder in Papiertüte atmen"),
        ("Normale Atemfrequenz", "12–15 Atemzüge pro Minute"),
        ("Normales Atemzugvolumen", "ca. 0,5 Liter"),
    ]
    for i, (fr, bk) in enumerate(flashcards):
        add_flashcard(cur, cid, fr, bk, i)


# ═══════════════════════════════════════════════════════════════════════════════
#  CHAPTER 3 – Menschliche Wahrnehmung (1.3)
# ═══════════════════════════════════════════════════════════════════════════════
def fill_perception(cur):
    cid = "human-perception"
    upsert_chapter(cur, cid, "human", "1.3 Menschliche Wahrnehmung", 3)
    clear_chapter(cur, cid)

    summaries = [
        "Der Mensch verfügt über fünf Sinne, die alle nicht für das Fliegen optimiert sind. "
        "Besonders kritisch: das Gleichgewichtsorgan kann im Flug täuschen, und das Auge benötigt "
        "externe Referenzen sowie ausreichend Zeit, um Objekte scharf zu erfassen. "
        "Das Nervensystem besteht aus dem zentralen (ZNS: Gehirn + Rückenmark) und dem peripheren "
        "Nervensystem (PNS). Signale werden über Synapsen übertragen.",
        "Das Auge hat drei Hautschichten: Lederhaut/Sklera, Aderhaut/Chorioidea, Netzhaut/Retina. "
        "Zapfen (Farbsehen, Tagsehen, Zentrum) und Stäbchen (Dämmerungssehen, Peripherie). "
        "Der blinde Fleck (Papille) enthält keine Photorezeptoren. "
        "Das Innenohr enthält Vorhof, Bogengänge und Schnecke — Gleichgewichtsorgan und Gehör.",
        "Das Gehör erfasst Töne zwischen 16 und 20.000 Hz (Sprachbereich 150–8.000 Hz). "
        "Ab dem 30. Lebensjahr sinkt das Hörvermögen oberhalb 4.000 Hz um ca. 10 dB je 10 Jahre. "
        "Das Gleichgewichtsorgan (Vestibularapparat) im Innenohr besteht aus Vorhof (Utriculus, Sacculus) "
        "und drei Bogengängen, die Dreh- und Linearbeschleunigungen registrieren.",
    ]
    for i, s in enumerate(summaries):
        add_section(cur, cid, "summary", s, order=i)

    facts = [
        "ZNS = Gehirn + Rückenmark; PNS = alle übrigen Nervenstränge.",
        "Synapsen sind Verbindungsstellen zwischen zwei Nervenzellen; Neurotransmitter übertragen das Signal.",
        "Das Auge besteht aus drei Hautschichten: Lederhaut (Sklera), Aderhaut, Netzhaut (Retina).",
        "Zapfen: Farbsehen, Tagsehen, in der Fovea konzentriert (schärfstes Sehen).",
        "Stäbchen: Dämmerungssehen, kein Farbsehen; in der Peripherie der Netzhaut.",
        "Blinder Fleck (Papille): keine Photorezeptoren — die Stelle, an der der Sehnerv austritt.",
        "Das Auge kann sich an unterschiedliche Lichtstärken anpassen: Adaption.",
        "Das Gehör funktioniert im Bereich 16–20.000 Hz; Sprache: 150–8.000 Hz.",
        "Ohrläppchen = Resonanzkörper (keine Schmerzempfindung).",
        "Eustachische Röhre (Ohrtrompete): Verbindet Mittelohr mit Rachenraum für Druckausgleich.",
        "Gleichgewichtsorgan: Vorhof (Utriculus + Sacculus, Linearbeschleunigung) + "
        "3 Bogengänge (Drehbeschleunigung).",
        "Bei Kopfdrehung gleiten die Augen automatisch entgegen (Nystagmus) — Blickrichtung bleibt stabil.",
        "Das 'Hosenbodengefühl' ist zur räumlichen Orientierung ohne Sichtflug ungeeignet.",
    ]
    for i, f in enumerate(facts):
        add_section(cur, cid, "fact", f, order=i)

    table_rows = [
        ["ZNS", "Gehirn + Rückenmark; bewusste und vegetative Steuerung"],
        ["PNS", "Alle anderen Nervenstränge; verbindet ZNS mit Körper"],
        ["Synapse", "Verbindung zweier Nervenzellen über Neurotransmitter"],
        ["Zapfen", "Farbsehen, Tagsehen, Zentrum (Fovea/Makula), ca. 6 Mio. im Auge"],
        ["Stäbchen", "Dämmerungssehen, kein Farben, Peripherie, ca. 120 Mio. im Auge"],
        ["Papille (Blinder Fleck)", "Austritt des Sehnervs; keine Photorezeptoren"],
        ["Eustachische Röhre", "Verbindet Mittelohr mit Rachen; öffnet sich beim Schlucken"],
        ["Utriculus + Sacculus", "Lineare Beschleunigungen (Vorhof)"],
        ["Bogengänge (3×)", "Drehbeschleunigungen in allen drei Raumebenen"],
        ["Nystagmus", "Automatische Augenbewegung bei Kopfdrehung zur Bildstabilisierung"],
        ["Hörbereich Mensch", "16–20.000 Hz; Sprache 150–8.000 Hz"],
    ]
    for row in table_rows:
        add_section(cur, cid, "table_row", json.dumps(row, ensure_ascii=False))

    focuses = [
        "ZNS/PNS und Synapse als Grundkonzepte sicher erklären können",
        "Zapfen vs. Stäbchen: Funktion, Lage, Lichtverhältnisse",
        "Eustachische Röhre und Druckausgleich kennen",
        "Gleichgewichtsorgan: Bogengänge (Drehung) vs. Vorhof (lineare Beschleunigung)",
        "Nystagmus und seine Bedeutung für das Sehen bei Kopfbewegungen",
    ]
    for f in focuses:
        add_section(cur, cid, "focus", f)

    quizzes = [
        # Offizielle Buchfragen (Übungsaufgaben 1.3)
        ("In welche beiden Teile kann das Nervensystem unterteilt werden?",
         ["Motorisches und sensorisches System",
          "Zentrales (ZNS) und peripheres Nervensystem (PNS)",
          "Bewusstes und unbewusstes System",
          "Sympathikus und Parasympathikus"],
         1,
         "Das Nervensystem teilt sich in das Zentrale Nervensystem (ZNS = Gehirn + Rückenmark) "
         "und das Periphere Nervensystem (PNS = alle übrigen Nervenstränge).",
         1),
        ("Wie wird der Kontakt zwischen zwei Zellen im Nervensystem hergestellt?",
         ["Über die Sklera",
          "Über die Ziliarkörper",
          "Über die Synapsen",
          "Über die Retina"],
         2,
         "Synapsen sind spezialisierte Verbindungsstellen zwischen Nervenzellen. "
         "Neurotransmitter übertragen das elektrische Signal chemisch auf die nächste Zelle.",
         1),
        ("Wie viele Häute umgeben das menschliche Auge?",
         ["2", "3", "4", "Das ist unterschiedlich"],
         1,
         "Das Auge besteht aus drei Hautschichten: äußere Lederhaut (Sklera/Hornhaut), "
         "mittlere Aderhaut (Chorioidea/Iris) und innere Netzhaut (Retina).",
         1),
        ("Welche Funktion hat das Ohrläppchen?",
         ["Einfangen der Schallwellen",
          "Erzeugen eines schwingenden Gegentons",
          "Ortung der Schallquelle",
          "Resonanzkörper"],
         3,
         "Das Ohrläppchen ist schmerzunempfindlich und dient als Resonanzkörper. "
         "Die eigentliche Schallaufnahme übernimmt die Ohrmuschel und der äußere Gehörgang.",
         1),
        ("In welchem Teil des Ohrs befindet sich das Gleichgewichtsorgan?",
         ["Außenohr", "Mittelohr", "Innenohr", "Ohrläppchen"],
         2,
         "Das Gleichgewichtsorgan (Vestibularapparat) befindet sich im Innenohr. "
         "Es besteht aus Vorhof (Utriculus + Sacculus) und drei Bogengängen.",
         1),
        ("In welchem Frequenzbereich kann der Mensch hören?",
         ["1–5.000 Hz",
          "16–20.000 Hz (Sprachbereich 150–8.000 Hz)",
          "50–50.000 Hz",
          "200–15.000 Hz"],
         1,
         "Menschen hören zwischen 16 und 20.000 Hz. Der für Sprache relevante Bereich "
         "liegt zwischen 150 und 8.000 Hz. Ab dem 30. Lebensjahr sinkt das Hörvermögen "
         "oberhalb 4.000 Hz deutlich.",
         1),
        ("Wozu führt eine Kopfdrehung, wenn ein Gegenstand betrachtet wird?",
         ["Es kommt zu einer automatischen Gegensteuerung der Augen (Nystagmus), sodass die Blickrichtung konstant bleibt",
          "Dies hat keine Auswirkungen auf die Augen",
          "Die Augen benötigen etwa 1 Sekunde, um auf die Kopfbewegung zu reagieren",
          "Die Augen müssen bewusst in die entgegengesetzte Richtung gedreht werden"],
         0,
         "Beim Nystagmus steuern die Augenmuskeln automatisch gegen die Kopfbewegung, "
         "sodass die Blickrichtung stabil bleibt. Das Gleichgewichtsorgan und die Augenmuskelkerne "
         "sind direkt verschaltet.",
         1),
        # Zusatzfragen
        ("Welche Sehzellen ermöglichen das Farbsehen am Tag?",
         ["Stäbchen, konzentriert in der Peripherie",
          "Zapfen, konzentriert in der Fovea (Zentrum der Netzhaut)",
          "Pigmentepithel in der Aderhaut",
          "Ganglienzellen in der Papille"],
         1,
         "Zapfen sind für das Farb- und Tagsehen zuständig und in der Fovea (schärfster Punkt) konzentriert. "
         "Stäbchen ermöglichen Dämmerungssehen, liefern aber kein Farbsignal.",
         0),
        ("Welche Funktion hat die Eustachische Röhre (Ohrtrompete)?",
         ["Verstärkt Schallwellen im Mittelohr",
          "Verbindet Mittelohr mit Rachen für den Druckausgleich",
          "Leitet Nervenimpulse von der Schnecke zum Gehirn",
          "Enthält die Gleichgewichtssensoren"],
         1,
         "Die Eustachische Röhre stellt eine Verbindung zwischen Mittelohr und oberem Rachenraum her "
         "und ermöglicht beim Schlucken einen Luftdruckausgleich — wichtig beim Steig- und Sinkflug.",
         0),
        ("Was ist der 'Blinde Fleck' im Auge?",
         ["Die empfindlichste Stelle auf der Netzhaut",
          "Die Stelle, an der der Sehnerv die Netzhaut verlässt — hier gibt es keine Photorezeptoren",
          "Die Iris, die bei grellem Licht die Pupille verengt",
          "Das Zentrum der Linse, das keine Sehfunktion hat"],
         1,
         "Der Blinde Fleck (Papille) ist die Stelle, an der der Sehnerv die Netzhaut verlässt. "
         "Hier gibt es keine Zapfen oder Stäbchen. Im normalen Sehen wird die Lücke vom Gehirn interpoliert.",
         0),
    ]
    for i, (q, opts, ans, expl, official) in enumerate(quizzes):
        add_quiz(cur, cid, q, opts, ans, expl, official, i)

    flashcards = [
        ("Zapfen vs. Stäbchen", "Zapfen: Farbe, Tag, Fovea. Stäbchen: Dämmerung, Peripherie, kein Farbe"),
        ("Blinder Fleck", "Papille: Sehnervenaustritt, keine Photorezeptoren"),
        ("Nystagmus", "Automatische Augenbewegung gegen Kopfdrehung → Blick bleibt stabil"),
        ("Eustachische Röhre", "Verbindet Mittelohr mit Rachen; ermöglicht Druckausgleich beim Schlucken"),
        ("Bogengänge (3×)", "Registrieren Drehbeschleunigung in allen drei Raumachsen"),
        ("Utriculus + Sacculus", "Registrieren lineare Beschleunigungen (Vorwärts, Rückwärts, Seite, Schwerkraft)"),
        ("ZNS", "Gehirn + Rückenmark"),
        ("PNS", "Alle Nervenstränge außerhalb von Gehirn und Rückenmark"),
        ("Synapse", "Übertragungsstelle zwischen zwei Nervenzellen via Neurotransmitter"),
    ]
    for i, (fr, bk) in enumerate(flashcards):
        add_flashcard(cur, cid, fr, bk, i)


# ═══════════════════════════════════════════════════════════════════════════════
#  CHAPTER 4 – Physiologische Auswirkungen des Fliegens (1.4)
# ═══════════════════════════════════════════════════════════════════════════════
def fill_flight_effects(cur):
    cid = "human-flight"
    upsert_chapter(cur, cid, "human", "1.4 Physiologische Auswirkungen des Fliegens", 4)
    clear_chapter(cur, cid)

    summaries = [
        "Beim Fliegen wirken Kräfte, Druckänderungen und Beschleunigungen auf den menschlichen Körper, "
        "für die er evolutionär nicht ausgelegt ist. Barotraumen entstehen durch Druckänderungen in "
        "gasgefüllten Körperhohlräumen (Boyle-Mariotte). Die Caissonkrankheit (Taucherkrankheit) "
        "entsteht durch zu schnellen Druckabfall und Blasenbildung von N₂ im Blut.",
        "Beschleunigungen (G-Kräfte) wirken auf den Piloten: Positive G (in z-Achse) bei Kurvenflug "
        "führen zu Greyout (ab 3g), Tunnelblick (3,5g), Blackout (4–5,5g), Bewusstlosigkeit (4,5–6g). "
        "Negative G können Rotsichtigkeit (Redout) ab –3g verursachen. Pressatmung kann G-Toleranz erhöhen.",
        "Kinetose (Reisekrankheit) entsteht durch widersprüchliche Signale von Gleichgewichtsorgan "
        "und Augen. Optische Täuschungen beim Anfliegen entstehen u. a. durch Landebahngröße, "
        "Neigung oder Sichtverhältnisse und können zu gefährlichen Anflugen führen.",
    ]
    for i, s in enumerate(summaries):
        add_section(cur, cid, "summary", s, order=i)

    facts = [
        "Barotrauma: Druckänderung in gasgefüllten Hohlräumen (Ohr, Nasennebenhöhlen, Zähne, Lunge, Magen-Darm).",
        "Erkältung verschlechtert den Druckausgleich (Ohrtrompete wirkt wie Einwegventil).",
        "Valsalva-Manöver: Mund zu, Nase zu, gegen zugeh. Nase ausatmen → Druckausgleich möglich.",
        "Caissonkrankheit (Druckkammer-/Dekompressionskrankheit): Blasenbildung von N₂ im Blut nach schnellem Druckabfall.",
        "Caissonkrankheit: nach dem Tauchen mindestens 24 h nicht fliegen (FAA: unkontrollierter Aufstieg ≥48 h).",
        "Positive G-Kräfte in z-Achse: 3g Greyout, 3,5g Tunnelblick, 4–5,5g Blackout, 4,5–6g Bewusstlosigkeit.",
        "Negative G: Rotsichtigkeit (Redout) ab ca. –3g, Gefahr platzender Blutgefäße ab –3g.",
        "60° Neigungswinkel in koordiniertem Kurvenflug → 2g Belastung.",
        "Dreh-Illusion: Bogengänge können sich an konstante Drehrate gewöhnen → Illusion des Stillstands.",
        "Elevator-Illusion: konstanter koordinierter enger Kurvenflug → Eindruck eines Steigfluges.",
        "Schwerkraft-Illusion (Somatogravic): Beschleunigung in Geradeausflug → Eindruck Steigflug; "
        "Sinkflug → Eindruck Verzögerung.",
        "Kinetose: Müdigkeit, Schwindel, Pulserhöhung, Kopfschmerzen, Übelkeit, Erbrechen.",
        "Anflugtäuschungen: breite Piste → Eindruck zu niedrig; schmale Piste → Eindruck zu hoch; "
        "ansteigende Piste → Eindruck zu niedrig (steilerer Anflug nötig); "
        "abfallende Piste → Eindruck zu hoch (zu flacher Anflug).",
        "Scanning (Luftraumbeobachtung): Sichtfeld in 10–20°-Abschnitten abtasten, je ~1 Sekunde verweilen.",
        "Frontalgegenverkehr: Größe erscheint proportional 1/Entfernung; nahe Kollision schwer erkennbar.",
    ]
    for i, f in enumerate(facts):
        add_section(cur, cid, "fact", f, order=i)

    table_rows = [
        ["Barotrauma", "Druckschaden in gasgefüllten Hohlräumen (Ohr, NNH, Zähne, Lunge)"],
        ["Valsalva-Manöver", "Mund + Nase zu, gegen geschlossene Nase ausatmen → Druckausgleich"],
        ["Caissonkrankheit", "N₂-Blasen im Blut nach schnellem Druckabfall; nach Tauchen mind. 24 h kein Flug"],
        ["Positive G (z-Achse) 3g", "Greyout (Farbsehverlust)"],
        ["Positive G (z-Achse) 3,5–5g", "Tunnelblick → Blackout"],
        ["Positive G (z-Achse) 4,5–6g", "Bewusstlosigkeit"],
        ["Negative G –3g", "Rotsichtigkeit (Redout), Blutgefäßplatzen"],
        ["60° Querneigung", "Doppeltes Gewicht (2g) durch Fliehkraft"],
        ["Dreh-Illusion", "Bogengänge gewöhnen sich an Drehrate → falsch: Stillstand"],
        ["Elevator-Illusion", "Enger koordinierter Kurvenflug → Eindruck Steigflug"],
        ["Schwerkraft-/Somatogravic-Illusion", "Linearbeschleunigung → Eindruck Steigflug; Sinkflug → Verzögerung"],
        ["Kinetose", "Müdigkeit, Schwindel, Übelkeit, Erbrechen durch widersprüchliche Sinneseindrücke"],
        ["Breite Landebahn", "Illusion geringerer Flughöhe → zu früh Abfangen → hartes Aufsetzen"],
        ["Schmale Landebahn", "Illusion größerer Flughöhe → zu spät Abfangen → zu langer Anflug"],
        ["Ansteigende Piste", "Illusion kürzerer, näherer Piste → Pilot neigt zu zu niedrigem Anflugwinkel"],
        ["Abfallende Piste", "Illusion längerer, weiter entfernter Piste → zu hoher Anflug"],
        ["Scanning", "10–20°-Abschnitte, je ~1 Sekunde; gesamten Sichtbereich regelmäßig scannen"],
    ]
    for row in table_rows:
        add_section(cur, cid, "table_row", json.dumps(row, ensure_ascii=False))

    focuses = [
        "Barotrauma-Mechanismus und Valsalva-Manöver kennen",
        "Caissonkrankheit: Ursache, Symptome, Maßnahme (mind. 24 h kein Flug nach Tauchen)",
        "G-Kräfte und physiologische Schwellen (Greyout/Blackout/Bewusstlosigkeit)",
        "Illusions-Typen und ihre Auswirkungen auf Anflugsituation",
        "Scanning-Technik und Kollisionsrisiko frontal erkennen",
    ]
    for f in focuses:
        add_section(cur, cid, "focus", f)

    quizzes = [
        # Offizielle Buchfragen (Übungsaufgaben 1.4)
        ("Wovon hängt die Stärke eines Barotraumas vor allem ab?",
         ["Von der Flughöhe allein",
          "Von der Geschwindigkeit der Druckänderung und der Fähigkeit der Organe, sie auszugleichen",
          "Nur von der Körpergröße des Piloten",
          "Ausschließlich von der Außentemperatur"],
         1,
         "Die Stärke eines Barotraumas hängt in erster Linie von der Geschwindigkeit der Druckänderung ab. "
         "Je schneller der Druckabfall, desto weniger Zeit haben die Organe, sich anzupassen. "
         "Plötzliche Druckverluste sind daher besonders gefährlich.",
         1),
        ("Um etwa wie viel Prozent nimmt das Lungenvolumen in 8.000 ft MSL im Vergleich zu MSL zu?",
         ["10 %", "15 %", "20 %", "25 %"],
         3,
         "Das Lungenvolumen nimmt in 8.000 ft MSL bereits um ca. 25 % zu (Boyle-Mariotte). "
         "Da dies langsam geschieht, ist es in der Regel nicht mit Beschwerden verbunden.",
         1),
        ("Wie funktioniert das Valsalva-Manöver?",
         ["Tief einatmen und den Atem anhalten",
          "Mund und Nase schließen, dann gegen die zugeh. Nase ausatmen (Druck aufbauen)",
          "Schnell mehrfach schlucken",
          "Flach atmen und Kopf nach unten beugen"],
         1,
         "Beim Valsalva-Manöver werden Mund und Nase geschlossen; dann wird versucht, "
         "durch die Nase auszuatmen. Dadurch wird Druck in den Nasen-Rachen-Raum aufgebaut, "
         "der die Eustachische Röhre öffnet und so einen momentanen Druckausgleich ermöglicht.",
         1),
        ("Wie lange kann es dauern, bis sich die Symptome der Caissonkrankheit bemerkbar machen?",
         ["Höchstens 10 Minuten",
          "Etwa 15 Minuten",
          "Wenigstens 30 Minuten",
          "Etwa 1 Stunde oder länger"],
         3,
         "Die Caissonkrankheit (Dekompressionskrankheit) kann bis zu einer Stunde oder länger brauchen, "
         "bis erste Symptome auftreten. Daher wird nach dem Tauchen mindestens 24 h keine Flugaktivität empfohlen.",
         1),
        ("Welcher Tiefenunterschied im Wasser entspricht einem Druckunterschied von einer Atmosphäre (1.013 hPa)?",
         ["10 Meter", "20 Meter", "30 Meter", "40 Meter"],
         0,
         "Der Druck im Wasser nimmt linear mit der Tiefe zu — um ca. 1 Atmosphäre (1.013 hPa) pro 10 Meter. "
         "In der Atmosphäre hingegen halbiert sich der Druck alle 5.500 m (exponentiell).",
         1),
        ("Wie wird das Phänomen genannt, dass ein Sinkflug die Illusion einer Verzögerung bewirkt?",
         ["Dreh-Illusion", "Flicker-Illusion", "Schwerkraft-Illusion (Somatogravic)", "Elevator-Illusion"],
         2,
         "Die Schwerkraft-Illusion (Somatogravic Illusion): Eine Beschleunigung im Geradeausflug "
         "erzeugt den Eindruck eines Steigfluges; ein Sinkflug den Eindruck einer Verzögerung. "
         "Gegenmaßnahme: Instrumente vertrauen.",
         1),
        ("Welche Illusion erzeugt eine ungewohnt breite Landebahn?",
         ["Die Illusion einer geringeren Flughöhe als tatsächlich",
          "Die Illusion einer größeren Flughöhe",
          "Die Illusion einer geringeren Schräglage",
          "Die Illusion einer höheren Schräglage"],
         0,
         "Eine ungewohnt breite Landebahn lässt den Piloten glauben, er sei niedriger als tatsächlich. "
         "Dies kann zu einem zu frühen Abfangen und hartem Aufsetzen führen.",
         1),
        ("Welcher Eindruck kann bei einem konstanten koordinierten engen Kurvenflug entstehen?",
         ["Eindruck eines Sinkfluges",
          "Eindruck eines Steigfluges (Elevator-Illusion)",
          "Eindruck der Geradeausfahrt",
          "Kein besonderer Eindruck — Instrumente und Gefühl stimmen überein"],
         1,
         "Die Elevator-Illusion entsteht bei konstantem koordinierten engem Kurvenflug. "
         "Ein Nachdrücken des Höhenruders zur Kompensation kann eine Steilspirale einleiten.",
         1),
        # Zusatzfragen
        ("Ab welchem G-Wert (positive G, z-Achse) tritt typischerweise Greyout auf?",
         ["Ab 1g", "Ab 2g", "Ab 3g", "Ab 6g"],
         2,
         "Ab ca. 3g tritt Greyout (Farbsehverlust, eingeschränktes Sehvermögen) auf. "
         "Ab 3,5–5g Tunnelblick und Blackout; ab 4,5–6g Bewusstlosigkeit.",
         0),
        ("Welche Gegenmaßnahme hilft bei auftretender Kinetose (Reisekrankheit)?",
         ["Kopf stark bewegen, um sich zu gewöhnen",
          "Turbulenzen und schnelle Richtungsänderungen vermeiden; Horizont fixieren; Medikamente",
          "Alkohol trinken, um entspannt zu bleiben",
          "Augen schließen und schlafen"],
         1,
         "Zur Vorbeugung von Kinetose: Turbulenzen meiden, Horizont fixieren, keine schnellen "
         "Kopfbewegungen, ausreichend Frischluft. Medikamente gegen Reisekrankheit können helfen, "
         "machen aber manchmal müde.",
         0),
        ("Wie sollte beim Scanning (Luftraumbeobachtung) vorgegangen werden?",
         ["Den Blick frei schweifen lassen",
          "Das Sichtfeld in 10–20°-Abschnitten abtasten, je ca. 1 Sekunde verweilen",
          "Nur den vorderen Bereich im Blick behalten",
          "Kontinuierlich rotieren ohne Pausen"],
         1,
         "Beim kontrollierten Scanning wird das Sichtfeld in 10–20°-Abschnitten abgetastet. "
         "In jedem Abschnitt sollte das Auge ca. 1 Sekunde verweilen, um Objekte scharf zu erfassen. "
         "Chaotisches Scanning kann ebenfalls effektiv sein.",
         0),
    ]
    for i, (q, opts, ans, expl, official) in enumerate(quizzes):
        add_quiz(cur, cid, q, opts, ans, expl, official, i)

    flashcards = [
        ("Barotrauma", "Druckschaden in gasgefüllten Körperhohlräumen bei zu schneller Druckänderung"),
        ("Valsalva-Manöver", "Mund + Nase zu, gegen zugeh. Nase ausatmen → Druckausgleich im Ohr"),
        ("Caissonkrankheit", "N₂-Blasen nach schnellem Druckabfall; nach Tauchen mind. 24 h kein Flug"),
        ("Greyout (3g)", "Farbsehverlust durch G-Kräfte; Blut wird aus dem Kopf gedrückt"),
        ("Blackout (4–5,5g)", "Vollständiger Sehverlust, dann Bewusstlosigkeit durch positive G"),
        ("Redout (–3g)", "Rotsichtigkeit bei negativen G; Blut strömt in den Kopf"),
        ("Elevator-Illusion", "Enger koordinierter Kurvenflug → fühlt sich an wie Steigflug"),
        ("Schwerkraft-Illusion", "Linearbeschleunigung → Eindruck Steigflug; Sinkflug → Eindruck Bremsen"),
        ("Breite Piste", "Illusion: zu niedrig → zu früh abfangen → harte Landung"),
        ("Schmale Piste", "Illusion: zu hoch → zu flacher Anflug → zu langer Aufsetzen"),
    ]
    for i, (fr, bk) in enumerate(flashcards):
        add_flashcard(cur, cid, fr, bk, i)


# ═══════════════════════════════════════════════════════════════════════════════
#  CHAPTER 5 – Flugpsychologie, Stress und Entscheidungsfindung (2.x) – expand
# ═══════════════════════════════════════════════════════════════════════════════
def fill_performance(cur):
    cid = "human-performance"
    cur.execute("UPDATE learn_chapters SET title=?, sort_order=?, exam_relevant=1 WHERE id=?",
                ("2. Flugpsychologie: Stress, Fehler und Entscheidungsfindung", 5, cid))
    clear_chapter(cur, cid)

    summaries = [
        "Das zweite Kapitel der Flugphysiologie befasst sich mit der menschlichen Informationsverarbeitung. "
        "Das Gehirn verarbeitet eingehende Reize, filtert diese und trifft Entscheidungen. "
        "Gedächtnis gliedert sich in Kurzzeitgedächtnis (ca. 7 Einheiten, kurze Haltedauer) und "
        "Langzeitgedächtnis. Lernen ist der Prozess der Überführung in das Langzeitgedächtnis.",
        "Stress ist eine Belastungsreaktion auf Stressoren (physisch, psychisch, zeitlich). "
        "Moderat fördert Stress die Leistung (Yerkes-Dodson-Kurve); zu hoher Stress führt "
        "zu Tunnelblick, Fehlern und Kontrollverlust. Stressbewältigung im Cockpit: "
        "Checklisten nutzen, Prioritäten setzen, Aufgaben delegieren, frühzeitig Go/No-Go treffen.",
        "Persönlichkeitsmerkmale und Fehlverhalten: Der 'gefährliche Pilot' zeigt oft "
        "Risikobereitschaft, Anti-Autoritätsverhalten, Impulsivität, Unteranpassung oder "
        "Fatalism. Das SHELL-Modell und Cockpit Resource Management (CRM) sind Werkzeuge "
        "zur Analyse und Vermeidung von Fehlern. Das Schweizer-Käse-Modell erklärt, "
        "wie mehrere Schutzschichten (CRM, Checklisten, Regeln) versagen müssen, damit ein Unfall eintritt.",
    ]
    for i, s in enumerate(summaries):
        add_section(cur, cid, "summary", s, order=i)

    facts = [
        "Das Kurzzeitgedächtnis fasst ca. 7 Einheiten und hält sie nur Sekunden bis Minuten.",
        "Stressoren können physisch (Lärm, Hitze), psychisch (Angst, Zeitdruck) oder physiologisch (Müdigkeit) sein.",
        "Moderat fördert Stress die Leistung; zu hoher Stress führt zu Tunnelblick und Entscheidungsfehlern.",
        "Tunnelblick: Fokus auf ein Detail, Verlust des Überblicks über die Gesamtsituation.",
        "Fatigue (Müdigkeit): vermindert Reaktionszeit, Gedächtnis, Urteilsvermögen — wird subjektiv unterschätzt.",
        "Aeronautical Decision Making (ADM): strukturierte fliegerische Entscheidungsfindung.",
        "Threat and Error Management (TEM): Bedrohungen erkennen, Fehler abfangen, Folgen minimieren.",
        "Situational Awareness (SA nach Endsley): 1. Wahrnehmen, 2. Verstehen, 3. Vorausplanen.",
        "5 'Gefährliche Einstellungen': Anti-Autorität, Impulsivität, Unverwundbarkeit, Unteranpassung, Fatalismus.",
        "SHELL-Modell: Software, Hardware, Environment, Liveware (Mensch) — analysiert Mensch-Maschine-Schnittstelle.",
        "FORDEC: Facts, Options, Risks, Decision, Execution, Check — strukturiertes Entscheidungsverfahren.",
        "Schweizer-Käse-Modell (Reason): Unfall entsteht, wenn Löcher in allen Schutzschichten gleichzeitig auftreten.",
        "CRM (Crew Resource Management): alle verfügbaren Ressourcen optimal nutzen.",
        "Go/No-Go: Frühzeitige, konservative Entscheidung zu treffen, ist Kern guter ADM.",
    ]
    for i, f in enumerate(facts):
        add_section(cur, cid, "fact", f, order=i)

    table_rows = [
        ["Kurzzeitgedächtnis", "ca. 7 Einheiten, wenige Sekunden bis Minuten Haltedauer"],
        ["Langzeitgedächtnis", "Dauerhafter Speicher; Überführung durch Wiederholung und Bedeutung"],
        ["Stress (moderat)", "Leistungssteigerung (Yerkes-Dodson); Schärft Aufmerksamkeit"],
        ["Stress (hoch)", "Tunnelblick, Entscheidungsfehler, Leistungsabfall"],
        ["ADM", "Aeronautical Decision Making: strukturierte Entscheidungsfindung im Cockpit"],
        ["TEM", "Threat and Error Management: Bedrohungen erkennen und Fehler abfangen"],
        ["SA (Situational Awareness)", "1. Wahrnehmen 2. Verstehen 3. Vorausplanen (Endsley-Modell)"],
        ["FORDEC", "Facts – Options – Risks – Decision – Execution – Check"],
        ["SHELL-Modell", "Software, Hardware, Environment, Liveware: Mensch-Maschine-Analyse"],
        ["5 Gefährliche Einstellungen", "Anti-Autorität, Impulsivität, Unverwundbarkeit, Unteranpassung, Fatalismus"],
        ["Schweizer-Käse-Modell", "Unfall = Lücken in allen Schutzschichten gleichzeitig offen"],
        ["CRM", "Crew Resource Management: alle Ressourcen (Mensch, Technik) optimal einsetzen"],
        ["Fatigue", "Schlaf-/Erholungsmangel; unterschätzt; verschlechtert alle kognitiven Leistungen"],
    ]
    for row in table_rows:
        add_section(cur, cid, "table_row", json.dumps(row, ensure_ascii=False))

    focuses = [
        "ADM und TEM als zentrale Sicherheitskonzepte kennen und anwenden",
        "5 gefährliche Einstellungen erkennen und Gegenmaßnahmen kennen",
        "SHELL-Modell und Schweizer-Käse-Modell erklären können",
        "FORDEC als Entscheidungsstruktur nutzen",
        "Situational Awareness: 3 Ebenen nach Endsley kennen",
        "Fatigue und Stress als Sicherheitsrisiken bewerten",
    ]
    for f in focuses:
        add_section(cur, cid, "focus", f)

    quizzes = [
        ("Welche Wirkung hat Müdigkeit (Fatigue) im Cockpit typischerweise?",
         ["Verbesserte Rechenleistung und Konzentration",
          "Verminderte Reaktionszeit, geringere Fehlertoleranz und schlechteres Urteilsvermögen",
          "Automatisch bessere Funkarbeit",
          "Nur stärkeren Hunger"],
         1,
         "Müdigkeit verschlechtert alle kognitiven Leistungen: Reaktionszeit, Konzentration, Gedächtnis, "
         "Entscheidungsqualität. Besonders gefährlich ist, dass Müdigkeit subjektiv unterschätzt wird.",
         1),
        ("Was ist ein typisches Zeichen von Tunnelblick?",
         ["Breiteres Situationsbewusstsein und bessere Übersicht",
          "Fokussierung auf ein Detail bei gleichzeitigem Verlust des Gesamtüberblicks",
          "Verbesserte Wahrnehmung aller Systeme gleichzeitig",
          "Automatisches Fehlermanagement"],
         1,
         "Tunnelblick reduziert die Breite der Wahrnehmung. Wichtige Informationen außerhalb des "
         "Fokus werden übersehen. Entsteht häufig unter hohem Stress oder hoher Arbeitsbelastung.",
         1),
        ("Wofür steht TEM (Threat and Error Management)?",
         ["Technische Einweisungs-Maßnahmen",
          "Das aktive Erkennen von Bedrohungen und Fehlern und deren Management zur Minimierung von Konsequenzen",
          "Treibstoff-Einstellungs-Messung",
          "Theoretische Einzelmeldung"],
         1,
         "TEM ist ein Sicherheitsmodell, das beschreibt, wie Piloten Bedrohungen (threats) und "
         "Fehler (errors) aktiv erkennen und managen, um unerwünschte Flugzeugzustände zu vermeiden.",
         1),
        ("Was versteht man unter 'Situational Awareness' (SA) nach Endsley?",
         ["Die Fähigkeit, Wetterkarten zu lesen",
          "Das genaue Wahrnehmen, Verstehen und Vorausplanen von Elementen der Flugumgebung",
          "Das sichere Bedienen aller Cockpit-Systeme",
          "Die Kenntnis aller Flugplätze im Umkreis"],
         1,
         "Situational Awareness (SA) nach Endsley umfasst drei Ebenen: "
         "(1) Wahrnehmen der Umweltelemente, (2) Verstehen ihrer Bedeutung, "
         "(3) Voraussagen zukünftiger Zustände. Verlust der SA ist ein Hauptunfallauslöser.",
         1),
        ("Welche Entscheidung ist im Zweifelfall die sicherere?",
         ["Zeitdruck über die Sicherheit stellen",
          "Weiterfliegen, obwohl zentrale Kriterien nicht mehr passen",
          "Frühzeitig abbrechen, ausweichen oder umplanen",
          "Checklisten bewusst verkürzen"],
         2,
         "Konservative Entscheidungen (Go/No-Go) sind Kern guter fliegerischer Entscheidungsfindung (ADM). "
         "Frühzeitiges Umplanen ist immer besser als spätes Durchdrücken.",
         1),
        ("Welche fünf 'gefährlichen Einstellungen' können die Entscheidungsfindung im Cockpit negativ beeinflussen?",
         ["Anti-Autorität, Impulsivität, Unverwundbarkeit, Unteranpassung, Fatalismus",
          "Euphorie, Aggression, Gleichgültigkeit, Panik, Hysterie",
          "Arroganz, Feigheit, Resignation, Nachlässigkeit, Hybris",
          "Optimismus, Realismus, Pessimismus, Neutralismus, Aktivismus"],
         0,
         "Die 5 gefährlichen Einstellungen nach FAA/EASA: Anti-Autorität ('Regeln gelten nicht für mich'), "
         "Impulsivität ('Handeln ohne Nachdenken'), Unverwundbarkeit ('Mir passiert nichts'), "
         "Unteranpassung ('Na und?') und Fatalismus ('Was soll ich dagegen tun?').",
         1),
        ("Was beschreibt das Schweizer-Käse-Modell (Reason)?",
         ["Eine Methode zur Flugplanung mit mehreren Checkpoints",
          "Das Modell zeigt, dass ein Unfall entsteht, wenn Lücken in allen Schutzschichten gleichzeitig offen sind",
          "Eine Technik zur Verbesserung der Kommunikation im Cockpit",
          "Eine Methode zur Berechnung von Kraftstoffmengen"],
         1,
         "Das Schweizer-Käse-Modell (James Reason) beschreibt Sicherheitsschichten (Käsescheiben) "
         "wie CRM, Checklisten, Regeln. Jede hat Lücken (Löcher). Ein Unfall tritt auf, wenn die "
         "Löcher aller Schichten zufällig gleichzeitig übereinstimmen.",
         1),
        ("Was bedeutet FORDEC?",
         ["Facts – Operations – Risks – Decision – Execution – Check",
          "Facts – Options – Risks – Decision – Execution – Check",
          "Flight – Options – Route – Direction – Efficiency – Check",
          "Fuel – Options – Route – Distance – Elapsed time – Checkpoint"],
         1,
         "FORDEC ist ein strukturiertes Entscheidungsverfahren: "
         "Facts (Fakten sammeln), Options (Optionen prüfen), Risks (Risiken bewerten), "
         "Decision (Entscheiden), Execution (Ausführen), Check (Überprüfen).",
         1),
        # Zusatzfragen
        ("Was ist das Kurzzeitgedächtnis und wie viele Einheiten kann es typischerweise halten?",
         ["Dauerhafter Speicher; unbegrenzt viele Einheiten",
          "Temporärer Arbeitsspeicher; ca. 7 Einheiten für Sekunden bis Minuten",
          "Nur für emotionale Erinnerungen; ca. 3 Einheiten",
          "Gehirnbereich für motorische Abläufe; ca. 100 Einheiten"],
         1,
         "Das Kurzzeitgedächtnis ist ein temporärer Arbeitsspeicher mit einer Kapazität von "
         "ca. 7 Einheiten (Chunking). Informationen bleiben nur Sekunden bis Minuten, "
         "sofern sie nicht durch Wiederholung ins Langzeitgedächtnis übertragen werden.",
         0),
        ("Was versteht man unter dem SHELL-Modell?",
         ["Ein Softwaremodell zur Flugplanung",
          "Ein Analyserahmen: Software, Hardware, Environment, Liveware (Mensch) — beschreibt Mensch-Maschine-Schnittstellen",
          "Ein Werkzeug zur Berechnung von Streckenführungen",
          "Ein Modell zur Wettervorhersage in der Aviatik"],
         1,
         "SHELL: Software (Verfahren, Regeln), Hardware (Instrumente, Flugzeug), "
         "Environment (Umgebung, Wetter), Liveware (Mensch). Das Modell hilft, "
         "Unfallursachen systematisch zu analysieren.",
         0),
    ]
    for i, (q, opts, ans, expl, official) in enumerate(quizzes):
        add_quiz(cur, cid, q, opts, ans, expl, official, i)

    flashcards = [
        ("ADM", "Aeronautical Decision Making – strukturierte, bewusste Entscheidungsfindung"),
        ("TEM", "Threat & Error Management – Bedrohungen erkennen, Fehler abfangen"),
        ("SA (Endsley)", "1. Wahrnehmen 2. Verstehen 3. Vorausplanen"),
        ("FORDEC", "Facts – Options – Risks – Decision – Execution – Check"),
        ("5 gefährliche Einstellungen", "Anti-Autorität | Impulsivität | Unverwundbarkeit | Unteranpassung | Fatalismus"),
        ("SHELL-Modell", "Software – Hardware – Environment – Liveware"),
        ("Schweizer-Käse", "Unfall = alle Schutzschichten-Lücken gleichzeitig offen"),
        ("Tunnelblick", "Fokus auf ein Detail; Überblick geht verloren – typisch bei Stress"),
        ("Fatigue", "Unterschätzte Gefahr; vermindert alle kognitiven und motorischen Leistungen"),
        ("Kurzzeitgedächtnis", "Ca. 7 Einheiten; nur Sekunden bis Minuten"),
    ]
    for i, (fr, bk) in enumerate(flashcards):
        add_flashcard(cur, cid, fr, bk, i)


# ═══════════════════════════════════════════════════════════════════════════════
#  Update FTS and subject overview
# ═══════════════════════════════════════════════════════════════════════════════
def rebuild_fts(cur, subject_id):
    """Rebuild FTS index for all chapters in this subject."""
    cur.execute("DELETE FROM learn_fts WHERE subject_id=?", (subject_id,))
    cur.execute("SELECT id, title FROM learn_chapters WHERE subject_id=?", (subject_id,))
    chapters = cur.fetchall()
    for chap_id, chap_title in chapters:
        cur.execute("SELECT content FROM learn_sections WHERE chapter_id=?", (chap_id,))
        texts = " ".join(r[0] for r in cur.fetchall())
        cur.execute(
            "INSERT INTO learn_fts (chapter_id, subject_id, chapter_title, subject_title, content) "
            "VALUES (?,?,?,?,?)",
            (chap_id, subject_id, chap_title, "Menschliches Leistungsvermögen", texts)
        )

def update_subject_overview(cur):
    overview = (
        "Das Fach 'Menschliches Leistungsvermögen' (Human Performance & Limitations / HPL) "
        "umfasst Flugphysiologie und -psychologie. Es deckt die physikalischen Grundlagen der Atmosphäre, "
        "Sauerstoffversorgung, Wahrnehmung, physiologische Auswirkungen des Fliegens sowie "
        "psychologische Faktoren wie Stress, Entscheidungsfindung und Fehlermanagement ab. "
        "Inhalte entsprechen dem Advanced PPL-Guide Band 6 (AirCademy, PPLHPL-AC-311)."
    )
    cur.execute("UPDATE learn_subjects SET overview=? WHERE id='human'", (overview,))


# ═══════════════════════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    conn = sqlite3.connect(DB)
    cur  = conn.cursor()

    print("▶ Fülle Kapitel: 1.1 Physikalische Grundlagen …")
    fill_basics(cur)

    print("▶ Erweitere Kapitel: 1.2 Sauerstoff und Blutkreislauf …")
    fill_physiology(cur)

    print("▶ Fülle neues Kapitel: 1.3 Menschliche Wahrnehmung …")
    fill_perception(cur)

    print("▶ Fülle neues Kapitel: 1.4 Physiologische Auswirkungen des Fliegens …")
    fill_flight_effects(cur)

    print("▶ Erweitere Kapitel: 2.x Flugpsychologie …")
    fill_performance(cur)

    print("▶ Aktualisiere Fach-Übersicht …")
    update_subject_overview(cur)

    print("▶ Baue FTS-Index neu auf …")
    rebuild_fts(cur, "human")

    conn.commit()
    conn.close()

    print("\n✅ Fertig! Folgende Kapitel wurden angelegt/erweitert:")
    print("   human-basics       → 1.1 Physikalische Grundlagen")
    print("   human-physiology   → 1.2 Sauerstoff, Atmung und Blutkreislauf  (erweitert)")
    print("   human-perception   → 1.3 Menschliche Wahrnehmung")
    print("   human-flight       → 1.4 Physiologische Auswirkungen des Fliegens")
    print("   human-performance  → 2.x Flugpsychologie                        (erweitert)")

if __name__ == "__main__":
    main()
