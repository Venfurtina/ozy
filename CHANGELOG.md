# PPL(A) Lernplattform – Update v2026.03-instruments-aero

## Änderungen (Version 2026.03-instruments-aero)

### Neue Kapitel: AGK – Allgemeine Luftfahrzeugkenntnis

Das bisherige Kapitel "Pitot-Static, Gyros, Elektrik und Grundsysteme" wurde durch
4 vollständige, buchbasierte Kapitel ersetzt:

#### 4.1 Pitot-Static-System: Höhenmesser, Fahrtmesser & Variometer
- Alle Druckinstrumente und ihr Messprinzip
- Vier Höhenbegriffe: Elevation, Height, Altitude, Flight Level
- QFE / QNH / Standard-Einstellung
- IAS / CAS / TAS / GS Unterschiede
- Farbmarkierungen am Fahrtmesser (Vso, Vs1, Vno, Vne, Vx, Vy)
- Blockaden und Fehlanzeigen (Pitot vs. Statik)
- **10 Quiz-Fragen** (buchbasiert)

#### 4.2 Kreiselinstrumente: Kurskreisel, Künstlicher Horizont & Wendezeiger
- Funktionsprinzip Kreisel: Massenträgheit, Präzession
- Kurskreisel: Aufhängung, Drift, Synchronisation alle 15 Min.
- Scheinbare Drift: DR = 15° × sin(φ) pro Stunde
- Künstlicher Horizont: Beschleunigungsfehler, Kurvenfehler
- Wendezeiger / Turn & Bank Coordinator
- Standardkurve: 3°/s, 2 Min, Schräglage S = TAS/10 + 7
- Kugellibelle und koordinierter Kurvenflug
- **8 Quiz-Fragen** (buchbasiert)

#### 4.3–4.4 Triebwerksüberwachung, Sonstige Instrumente & Elektrik
- Drehzahlmesser und Ladedruckanzeige
- Öldruck und Öltemperatur (gemeinsam interpretieren)
- Zylinderkopftemperatur (CHT) und Peak EGT
- Kraftstoffdurchfluss und Kraftstoffvorratsanzeige
- Unterdruckmesser, Amperemeter, Voltmeter
- **7 Quiz-Fragen** (buchbasiert)

#### 4.5 Elektronische Anzeigen: EFIS, PFD, ND & Glass Cockpit
- EFIS/Glass Cockpit Vor- und Nachteile
- Air Data Computer (ADC) als Bordcomputer
- PFD: Speed Tape, Altitude Tape, Flight Director
- Navigation Display (ND) und HSI
- MFD (Multifunktionsdisplay) und EICAS
- Navigationsdatenbank: 28-Tage-Zyklus
- **6 Quiz-Fragen** (buchbasiert)

---

### Neue Kapitel: Aerodynamik / Principles of Flight

2 neue Grundlagenkaptitel wurden den bestehenden Aerodynamik-Kapiteln vorangestellt:

#### 1. Atmosphäre, Luftwiderstand, Grenzschicht & Bernoulli-Gleichung
- ICAO-Standardatmosphäre (ISA): 1013,25 hPa, +15°C, 1,225 kg/m³
- Temperaturabnahme: 2°C/1.000 ft bis Tropopause (11 km)
- Luftwiderstandsformel: D = ½·v²·A·ρ·cD (quadratisch mit v)
- Laminare vs. turbulente Grenzschicht
- Bernoulli-Gleichung: p_stat + ½·ρ·v² = const
- Kontinuitätsgesetz: A₁·v₁ = A₂·v₂
- **7 Quiz-Fragen** (buchbasiert)

#### 2. Strömung am Tragflügel: Profilquerschnitt & Auftriebserzeugung
- Tragflügelprofil: runde Vorderkante, spitze Hinterkante
- Druckverteilung: Unterdruck oben, höherer Druck unten
- Anstellwinkel (AoA) als Hauptregulator
- Auftriebsbeiwert cA, kritischer Anstellwinkel ~15–16°
- Stall = Überschreiten des kritischen AoA
- Induzierter Widerstand durch Randwirbel
- Symmetrisches vs. asymmetrisches Profil
- **8 Quiz-Fragen** (buchbasiert)

---

## Statistik

| Bereich | Vorher | Nachher |
|---------|--------|---------|
| AGK-Kapitel | 2 | 5 |
| Aerodynamik-Kapitel | 8 | 10 |
| Gesamt-Kapitel | 48 | 56 |
| Gesamt-Quiz-Fragen | ~485 | ~526 |
| Buchbasierte Quizfragen (is_official=1) | ~280 | ~316 |

## Quellenangaben

Alle Inhalte basieren auf:
- **Aircademy Advanced PPL-Guide Band 1**: Allgemeine Luftfahrzeugkunde (AGK)  
  Kapitel 4.1–4.5 (Seiten 80–130)
- **Aircademy Advanced PPL-Guide Band 2**: Aerodynamik  
  Kapitel 1–2 (Seiten 1–25)

## Deployment

Die Änderungen sind direkt in der SQLite-Datenbank (`takvim.db`) gespeichert.
Kein Neustart der Flask-App erforderlich; die API-Routen lesen die DB dynamisch.

Datei: `takvim.db` (enthält alle Änderungen)
