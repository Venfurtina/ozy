#!/usr/bin/env python3
"""
fill_new_chapters.py
Füllt die zwei durch extract_pdf.py angelegten leeren Kapitel mit
vollständigem Inhalt aus den Buch-PDFs (PPL Meteorologie, Band 5, AIRCADEMY).

Kapitel-IDs (von extract_pdf.py angelegt):
  meteorologie-kapitel-1-die-atmosphare-aufbau-strahlung-physik
  meteorologie-kapitel-2-wolken-und-niederschlage-bildung-arten

Inhalt basiert 1:1 auf dem Buchtext (Seiten 9-54).
Kein Inhalt wurde erfunden – alle Fakten direkt aus dem Buch übernommen.
"""
import json, sqlite3, os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "takvim.db")

# ── SVG-Diagramme (aus Buchgrafiken rekonstruiert) ──────────────────────────

SVG_ZUSAMMENSETZUNG = """<svg viewBox="0 0 480 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:480px;font-family:system-ui,sans-serif">
  <rect width="480" height="260" fill="#0d1623" rx="10"/>
  <text x="240" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Abb. 1 – Zusammensetzung der Atmosphäre</text>
  <!-- Pie approximation -->
  <!-- N2 78% -->
  <path d="M200 145 L200 55 A90 90 0 1 1 155 235 Z" fill="#3b82f6" opacity="0.85"/>
  <!-- O2 21% -->
  <path d="M200 145 L155 235 A90 90 0 0 1 112 100 Z" fill="#22c55e" opacity="0.85"/>
  <!-- 1% rest -->
  <path d="M200 145 L112 100 A90 90 0 0 1 200 55 Z" fill="#f59e0b" opacity="0.85"/>
  <!-- labels -->
  <text x="232" y="138" fill="white" font-size="16" font-weight="bold">78%</text>
  <text x="228" y="154" fill="#93c5fd" font-size="11">Stickstoff (N₂)</text>
  <text x="122" y="240" fill="white" font-size="14" font-weight="bold">21%</text>
  <text x="118" y="254" fill="#86efac" font-size="11">Sauerstoff (O₂)</text>
  <text x="112" y="95" fill="white" font-size="12" font-weight="bold">~1%</text>
  <text x="105" y="108" fill="#fcd34d" font-size="10">CO₂+Edelgase</text>
  <!-- note box -->
  <rect x="310" y="50" width="158" height="60" fill="#1e3a5f" rx="6" stroke="#3b82f6" stroke-width="1"/>
  <text x="389" y="70" fill="#93c5fd" font-size="10" text-anchor="middle" font-weight="bold">+ Wasserdampf</text>
  <text x="389" y="83" fill="white" font-size="10" text-anchor="middle">0 bis 4%</text>
  <text x="389" y="97" fill="#94a3b8" font-size="9" text-anchor="middle">variabel, nur Troposphäre</text>
  <!-- ICAO note -->
  <rect x="310" y="125" width="158" height="50" fill="#1a2a1a" rx="6" stroke="#22c55e" stroke-width="1"/>
  <text x="389" y="145" fill="#86efac" font-size="10" text-anchor="middle" font-weight="bold">ICAO-Standardatmosphäre:</text>
  <text x="389" y="159" fill="white" font-size="10" text-anchor="middle">Luftfeuchtigkeit = 0%</text>
  <text x="389" y="170" fill="#94a3b8" font-size="9" text-anchor="middle">(reine trockene Luft)</text>
</svg>"""

SVG_SCHICHTEN = """<svg viewBox="0 0 540 360" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <defs>
    <linearGradient id="bg1" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#060614"/>
      <stop offset="40%" stop-color="#0d1b5e"/>
      <stop offset="70%" stop-color="#1a4a7a"/>
      <stop offset="90%" stop-color="#6ea8c8"/>
      <stop offset="100%" stop-color="#c8e8f0"/>
    </linearGradient>
  </defs>
  <rect width="540" height="360" fill="url(#bg1)" rx="10"/>
  <text x="270" y="20" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Abb. 2 – Schichten der Atmosphäre (Temperaturverlauf)</text>
  <!-- Schichten Bänder -->
  <rect x="0" y="295" width="540" height="65" fill="#2d5a1b" opacity="0.75"/>
  <text x="10" y="318" fill="#a8e090" font-size="12" font-weight="bold">TROPOSPHÄRE  0 – 11 km</text>
  <text x="10" y="333" fill="#c8f0b0" font-size="10">Temp ↓ 0,65°C/100m · Wolken · Wetter · Niederschlag</text>
  <text x="10" y="348" fill="#94a3b8" font-size="10">Am Boden: 15°C / 1013,25 hPa · Tropopause: -56,5°C</text>

  <line x1="0" y1="219" x2="540" y2="219" stroke="#facc15" stroke-width="2" stroke-dasharray="8,4"/>
  <text x="8" y="215" fill="#facc15" font-size="11" font-weight="bold">TROPOPAUSE  Äquator: 16–18 km · Pol: 6–8 km · ∅ 11 km</text>

  <rect x="0" y="150" width="540" height="69" fill="#1a1a4a" opacity="0.5"/>
  <text x="10" y="170" fill="#a5b4fc" font-size="12" font-weight="bold">STRATOSPHÄRE  11 – 50 km</text>
  <text x="10" y="185" fill="#c7d2fe" font-size="10">Temperatur erst konstant, dann steigend (Ozonschicht 15–50 km)</text>
  <text x="10" y="200" fill="#94a3b8" font-size="10">Aufstieg: Absorption von UV-Strahlung durch Ozon</text>

  <line x1="0" y1="108" x2="540" y2="108" stroke="#818cf8" stroke-width="1" stroke-dasharray="5,4"/>
  <text x="8" y="105" fill="#a5b4fc" font-size="11" font-weight="bold">MESOSPHÄRE  50 – 80 km  · Temperatur ↓ bis −90°C</text>

  <line x1="0" y1="60" x2="540" y2="60" stroke="#7dd3fc" stroke-width="1" stroke-dasharray="5,4"/>
  <text x="8" y="57" fill="#7dd3fc" font-size="11" font-weight="bold">IONOSPHÄRE / THERMOSPHÄRE  80 km+</text>

  <text x="8" y="40" fill="#94a3b8" font-size="10">EXOSPHÄRE – geht in Weltraum über</text>

  <!-- Temperature scale right side -->
  <text x="460" y="305" fill="#f87171" font-size="10">+15°C</text>
  <text x="460" y="225" fill="#f87171" font-size="10">-56°C</text>
  <text x="460" y="160" fill="#f87171" font-size="10">≈-2°C</text>
  <text x="430" y="22" fill="#f87171" font-size="10" font-weight="bold">Temperatur →</text>

  <!-- Tropo height arrow -->
  <line x1="515" y1="295" x2="515" y2="219" stroke="#facc15" stroke-width="1.5"/>
  <text x="520" y="262" fill="#facc15" font-size="9">11 km</text>
</svg>"""

SVG_STRAHLUNG = """<svg viewBox="0 0 540 270" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="270" fill="#0d1623" rx="10"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Abb. 23 – Vereinfachte Strahlungsbilanz der Erde (nach Kiehl &amp; Trenberth)</text>
  <!-- Sun top -->
  <text x="270" y="45" fill="#fbbf24" font-size="22" text-anchor="middle">☀</text>
  <text x="270" y="60" fill="#fbbf24" font-size="11" text-anchor="middle">Gesamte Sonneneinstrahlung 342 W/m²</text>
  <!-- Arrows down -->
  <!-- Reflexion 30+77=107 -->
  <line x1="120" y1="70" x2="80" y2="110" stroke="#60a5fa" stroke-width="2.5" marker-end="url(#arr)"/>
  <text x="55" y="100" fill="#60a5fa" font-size="10">Reflexion</text>
  <text x="55" y="113" fill="#60a5fa" font-size="10">107 W/m²</text>
  <!-- Absorption atmosphere 67 -->
  <rect x="170" y="85" width="200" height="30" fill="#3b82f630" stroke="#3b82f6" stroke-width="1" rx="5"/>
  <text x="270" y="102" fill="#93c5fd" font-size="11" text-anchor="middle">Atmosphäre (Absorption 67)</text>
  <!-- Through to surface 168 -->
  <line x1="270" y1="120" x2="270" y2="165" stroke="#fbbf24" stroke-width="2.5"/>
  <text x="278" y="148" fill="#fbbf24" font-size="10">168 W/m²</text>
  <!-- Ground -->
  <rect x="80" y="165" width="380" height="30" fill="#3d6b28" rx="5"/>
  <text x="270" y="183" fill="#a7f3d0" font-size="11" text-anchor="middle">Erdboden – absorbiert Sonnenlicht → wird erwärmt</text>
  <!-- Terrestrische Abstrahlung -->
  <line x1="350" y1="165" x2="380" y2="115" stroke="#f97316" stroke-width="2" stroke-dasharray="5,3"/>
  <text x="390" y="112" fill="#f97316" font-size="10">Terrestrisch 350</text>
  <!-- Rückstrahlung -->
  <line x1="400" y1="120" x2="430" y2="165" stroke="#fb923c" stroke-width="2"/>
  <text x="435" y="158" fill="#fb923c" font-size="10">Rückstr. 324</text>
  <!-- Key info box -->
  <rect x="20" y="210" width="500" height="50" fill="#1e2d3a" rx="6" stroke="#334155" stroke-width="1"/>
  <text x="270" y="228" fill="#fbbf24" font-size="11" font-weight="bold" text-anchor="middle">Merksatz: Das Sonnenlicht erwärmt den ERDBODEN – nicht die Atmosphäre!</text>
  <text x="270" y="244" fill="white" font-size="10" text-anchor="middle">Die Atmosphäre erwärmt sich durch Wärmeabgabe des Bodens (langwellige Strahlung + Wärmeleitung)</text>
  <text x="270" y="257" fill="#94a3b8" font-size="9" text-anchor="middle">Strahlungsbilanz: Tagsüber positiv (Einstrahlung &gt; Ausstrahlung) · Nachts negativ (nur Ausstrahlung)</text>
</svg>"""

SVG_DRUCK = """<svg viewBox="0 0 520 280" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:520px;font-family:system-ui,sans-serif">
  <rect width="520" height="280" fill="#0d1623" rx="10"/>
  <text x="260" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Abb. 6 – Verlauf von Druck, Temperatur und Dichte in der Atmosphäre</text>
  <!-- Axes -->
  <line x1="65" y1="35" x2="65" y2="235" stroke="#555" stroke-width="1.5"/>
  <line x1="65" y1="235" x2="490" y2="235" stroke="#555" stroke-width="1.5"/>
  <!-- Y axis (Höhe) -->
  <text x="58" y="238" fill="#94a3b8" font-size="9" text-anchor="end">0</text>
  <text x="58" y="195" fill="#94a3b8" font-size="9" text-anchor="end">5,5 km</text>
  <text x="58" y="155" fill="#94a3b8" font-size="9" text-anchor="end">11 km</text>
  <text x="58" y="108" fill="#94a3b8" font-size="9" text-anchor="end">18 km</text>
  <text x="30" y="140" fill="#94a3b8" font-size="10" transform="rotate(-90,30,140)">Höhe</text>
  <!-- Druck curve (blue) exponential -->
  <polyline points="460,235 370,195 270,155 180,108 130,80 100,58"
    fill="none" stroke="#3b82f6" stroke-width="3"/>
  <text x="455" y="228" fill="#3b82f6" font-size="10">Druck</text>
  <!-- Dichte curve (green) similar -->
  <polyline points="430,235 340,195 240,155 155,108 110,80 85,58"
    fill="none" stroke="#22c55e" stroke-width="2.5"/>
  <text x="425" y="218" fill="#22c55e" font-size="10">Dichte</text>
  <!-- Temp curve (red) different shape -->
  <polyline points="380,235 320,195 260,155 200,108 185,80 185,58"
    fill="none" stroke="#ef4444" stroke-width="2.5"/>
  <text x="355" y="230" fill="#ef4444" font-size="10">Temperatur</text>
  <!-- Halbierung annotation -->
  <line x1="65" y1="195" x2="370" y2="195" stroke="#3b82f640" stroke-width="1" stroke-dasharray="4,3"/>
  <line x1="370" y1="195" x2="370" y2="235" stroke="#3b82f640" stroke-width="1" stroke-dasharray="4,3"/>
  <text x="68" y="192" fill="#facc15" font-size="10">500 hPa bei ~5.500 m (Halbierung)</text>
  <!-- Key table -->
  <rect x="68" y="245" width="440" height="28" fill="#1e2d3a" rx="5"/>
  <text x="80" y="261" fill="white" font-size="10">Barometrische Höhenstufe: MSL = 27 ft/hPa (8 m/hPa)</text>
  <text x="310" y="261" fill="#facc15" font-size="10">18.000 ft = 54 ft/hPa · 36.000 ft = 108 ft/hPa</text>
</svg>"""

SVG_BAROMETER = """<svg viewBox="0 0 480 250" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:480px;font-family:system-ui,sans-serif">
  <rect width="480" height="250" fill="#0d1623" rx="10"/>
  <text x="240" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Abb. 5 – Dosenbarometer (Aneroid) &amp; Abb. 4 – Quecksilberbarometer</text>
  <!-- Aneroid left -->
  <rect x="20" y="35" width="200" height="160" fill="#1e2d3a" rx="8" stroke="#334155" stroke-width="1"/>
  <text x="120" y="55" fill="#93c5fd" font-size="11" font-weight="bold" text-anchor="middle">Dosenbarometer (Aneroid)</text>
  <!-- Dose -->
  <ellipse cx="120" cy="115" rx="45" ry="20" fill="#334155" stroke="#60a5fa" stroke-width="2"/>
  <text x="120" y="119" fill="#93c5fd" font-size="10" text-anchor="middle">Dosenkapsel</text>
  <!-- Feder -->
  <line x1="120" y1="95" x2="120" y2="70" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="95" y="83" fill="#94a3b8" font-size="9">Feder</text>
  <!-- Zeiger -->
  <line x1="120" y1="135" x2="160" y2="155" stroke="#fbbf24" stroke-width="2"/>
  <text x="162" y="159" fill="#fbbf24" font-size="9">Zeiger/Skala</text>
  <text x="120" y="188" fill="white" font-size="9" text-anchor="middle">Hoher Druck → Dose zusammengedrückt</text>
  <text x="120" y="200" fill="white" font-size="9" text-anchor="middle">Niedriger Druck → Dose dehnt sich aus</text>

  <!-- Quecksilber right -->
  <rect x="260" y="35" width="200" height="160" fill="#1e2d3a" rx="8" stroke="#334155" stroke-width="1"/>
  <text x="360" y="55" fill="#93c5fd" font-size="11" font-weight="bold" text-anchor="middle">Quecksilberbarometer</text>
  <!-- U-Rohr -->
  <rect x="330" y="68" width="20" height="100" fill="#334155" stroke="#60a5fa" stroke-width="1.5" rx="2"/>
  <rect x="375" y="108" width="20" height="60" fill="#334155" stroke="#60a5fa" stroke-width="1.5" rx="2"/>
  <line x1="330" y1="168" x2="395" y2="168" stroke="#60a5fa" stroke-width="1.5"/>
  <!-- Quecksilbersäule -->
  <rect x="332" y="100" width="16" height="68" fill="#9ca3af" rx="1"/>
  <rect x="377" y="128" width="16" height="40" fill="#9ca3af" rx="1"/>
  <!-- Labels -->
  <text x="308" y="105" fill="#facc15" font-size="9">760 mm</text>
  <line x1="325" y1="100" x2="350" y2="100" stroke="#facc15" stroke-width="1" stroke-dasharray="3,2"/>
  <text x="400" y="130" fill="#94a3b8" font-size="8">Vakuum</text>
  <text x="265" y="185" fill="white" font-size="9">Luftdruck = 760 mmHg = 29,92 inHg = 1013,25 hPa</text>
  <text x="265" y="197" fill="#94a3b8" font-size="8">Luftfahrt: Dosenbarometer (kein Quecksilber nötig)</text>
</svg>"""

SVG_ADIABATISCH = """<svg viewBox="0 0 520 300" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:520px;font-family:system-ui,sans-serif">
  <rect width="520" height="300" fill="#0d1623" rx="10"/>
  <text x="260" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Abb. 14/15 – Trockenadiabatischer &amp; Feuchtadiabatischer Aufstieg</text>
  <!-- Axes -->
  <line x1="65" y1="40" x2="65" y2="255" stroke="#555" stroke-width="1.5"/>
  <line x1="65" y1="255" x2="490" y2="255" stroke="#555" stroke-width="1.5"/>
  <!-- Y labels -->
  <text x="57" y="258" fill="#94a3b8" font-size="9" text-anchor="end">0</text>
  <text x="57" y="200" fill="#94a3b8" font-size="9" text-anchor="end">1000m</text>
  <text x="57" y="148" fill="#94a3b8" font-size="9" text-anchor="end">2000m</text>
  <text x="57" y="95" fill="#94a3b8" font-size="9" text-anchor="end">3000m</text>
  <!-- X labels temperature -->
  <text x="150" y="272" fill="#94a3b8" font-size="9" text-anchor="middle">0°C</text>
  <text x="255" y="272" fill="#94a3b8" font-size="9" text-anchor="middle">10°C</text>
  <text x="360" y="272" fill="#94a3b8" font-size="9" text-anchor="middle">20°C</text>
  <text x="465" y="272" fill="#94a3b8" font-size="9" text-anchor="middle">30°C</text>
  <!-- Grid lines -->
  <line x1="65" y1="200" x2="490" y2="200" stroke="#1e293b" stroke-width="1"/>
  <line x1="65" y1="148" x2="490" y2="148" stroke="#1e293b" stroke-width="1"/>
  <line x1="65" y1="95"  x2="490" y2="95"  stroke="#1e293b" stroke-width="1"/>
  <!-- ISA brown dashed -->
  <polyline points="360,255 297,200 235,148 172,95 142,63" fill="none" stroke="#b45309" stroke-width="2" stroke-dasharray="6,3"/>
  <!-- DALR green (1°C/100m) -->
  <polyline points="415,255 355,200 295,148 235,95 205,63" fill="none" stroke="#22c55e" stroke-width="2.5"/>
  <!-- SALR blue (0,6°C/100m) -->
  <polyline points="395,255 345,200 296,148 246,95 219,63" fill="none" stroke="#3b82f6" stroke-width="2.5"/>
  <!-- Legend -->
  <rect x="68" y="45" width="240" height="88" fill="#1e2d3a" rx="6" stroke="#334155" stroke-width="1"/>
  <line x1="78" y1="65" x2="108" y2="65" stroke="#22c55e" stroke-width="2.5"/>
  <text x="113" y="69" fill="white" font-size="11">Trockenadiabatisch: 1°C / 100 m</text>
  <line x1="78" y1="83" x2="108" y2="83" stroke="#3b82f6" stroke-width="2.5"/>
  <text x="113" y="87" fill="white" font-size="11">Feuchtadiabatisch: 0,6°C / 100 m</text>
  <line x1="78" y1="101" x2="108" y2="101" stroke="#b45309" stroke-width="2" stroke-dasharray="5,3"/>
  <text x="113" y="105" fill="#b45309" font-size="11">ISA Standard: 0,65°C / 100 m</text>
  <!-- KKN annotation -->
  <circle cx="345" cy="200" r="5" fill="#facc15"/>
  <text x="352" y="197" fill="#facc15" font-size="9">KKN (Wolkenuntergrenze)</text>
  <text x="68" y="285" fill="#94a3b8" font-size="9">KKN [ft] = Spread × 400  ·  KKN [m] = Spread × 123</text>
  <text x="68" y="296" fill="#94a3b8" font-size="9">Spread = Temperatur − Taupunkt  (°C)</text>
</svg>"""

SVG_HOEHENMESSUNG = """<svg viewBox="0 0 520 270" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:520px;font-family:system-ui,sans-serif">
  <rect width="520" height="270" fill="#0d1623" rx="10"/>
  <text x="260" y="22" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Abb. 16/17/18 – Höhenmessereinstellungen: QFE · QNH · QNE (FL)</text>
  <!-- Ground -->
  <rect x="0" y="225" width="520" height="45" fill="#2d5a1b" opacity="0.8"/>
  <text x="260" y="247" fill="#86efac" font-size="10" text-anchor="middle">Flugplatz / Erdboden</text>
  <!-- MSL line -->
  <line x1="0" y1="200" x2="520" y2="200" stroke="#3b82f6" stroke-width="1.5" stroke-dasharray="8,4"/>
  <text x="5" y="197" fill="#60a5fa" font-size="10">MSL</text>
  <!-- QNE/FL line at top -->
  <line x1="0" y1="55" x2="520" y2="55" stroke="#facc15" stroke-width="1.5" stroke-dasharray="6,3"/>
  <text x="5" y="52" fill="#facc15" font-size="10">QNE: 1013,25 hPa → Flugfläche (FL)</text>
  <!-- Aircraft symbols -->
  <text x="380" y="115" fill="white" font-size="20">✈</text>
  <!-- QFE column -->
  <line x1="130" y1="225" x2="130" y2="200" stroke="#ef4444" stroke-width="2.5"/>
  <text x="85" y="198" fill="#ef4444" font-size="11" font-weight="bold">↕ QFE</text>
  <text x="55" y="212" fill="#ef4444" font-size="9">Height über Platz</text>
  <text x="55" y="223" fill="#ef4444" font-size="9">Am Boden = 0</text>
  <!-- QNH column -->
  <line x1="260" y1="115" x2="260" y2="200" stroke="#22c55e" stroke-width="2.5"/>
  <text x="270" y="165" fill="#22c55e" font-size="11" font-weight="bold">QNH</text>
  <text x="270" y="178" fill="#22c55e" font-size="9">Altitude (über MSL)</text>
  <!-- FL column -->
  <line x1="390" y1="115" x2="390" y2="55" stroke="#facc15" stroke-width="2.5"/>
  <text x="400" y="90" fill="#facc15" font-size="11" font-weight="bold">FL (QNE)</text>
  <text x="400" y="103" fill="#facc15" font-size="9">1013,25 hPa</text>
  <!-- Übergangsbox -->
  <rect x="65" y="32" width="260" height="38" fill="#1e2d3a" rx="5" stroke="#22c55e" stroke-width="1"/>
  <text x="195" y="48" fill="#86efac" font-size="10" text-anchor="middle" font-weight="bold">Übergangshöhe (D): 5.000 ft MSL / 2.000 ft AGL</text>
  <text x="195" y="62" fill="white" font-size="9" text-anchor="middle">Darunter: QNH · Darüber: QNE (FL) · mind. 1.000 ft Abstand</text>
  <!-- Rules -->
  <rect x="30" y="235" width="460" height="30" fill="#1e2d3a" rx="4"/>
  <text x="260" y="248" fill="#fbbf24" font-size="10" text-anchor="middle">QNH &gt; 1013 hPa → wahre Höhe GRÖSSER als angezeigt</text>
  <text x="260" y="261" fill="#f87171" font-size="10" text-anchor="middle">QNH &lt; 1013 hPa → wahre Höhe KLEINER  ·  „Von Warm nach Kalt, das knallt!"</text>
</svg>"""

SVG_STABILIT = """<svg viewBox="0 0 520 210" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:520px;font-family:system-ui,sans-serif">
  <rect width="520" height="210" fill="#0d1623" rx="10"/>
  <text x="260" y="20" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Abb. 25/26 – Stabilität, Indifferenz, Labilität</text>
  <!-- Panel 1: Stabil -->
  <rect x="10" y="30" width="155" height="165" fill="#0f2a1a" rx="8" stroke="#22c55e" stroke-width="1.5"/>
  <text x="87" y="50" fill="#86efac" font-size="12" font-weight="bold" text-anchor="middle">STABILITÄT</text>
  <line x1="87" y1="60" x2="87" y2="175" stroke="#444" stroke-width="1"/>
  <polyline points="117,175 57,60" fill="none" stroke="#b45309" stroke-width="2"/>
  <polyline points="103,175 72,60" fill="none" stroke="#22c55e" stroke-width="2"/>
  <polyline points="78,175 82,60" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,2"/>
  <circle cx="87" cy="155" r="8" fill="#3b82f6" opacity="0.8"/>
  <text x="87" y="159" fill="white" font-size="9" text-anchor="middle">↓</text>
  <text x="87" y="195" fill="#86efac" font-size="9" text-anchor="middle">Luftpaket kehrt zurück</text>
  <!-- Panel 2: Indifferenz -->
  <rect x="182" y="30" width="155" height="165" fill="#1a1a2a" rx="8" stroke="#6366f1" stroke-width="1.5"/>
  <text x="259" y="50" fill="#a5b4fc" font-size="12" font-weight="bold" text-anchor="middle">INDIFFERENZ</text>
  <line x1="259" y1="60" x2="259" y2="175" stroke="#444" stroke-width="1"/>
  <polyline points="287,175 230,60" fill="none" stroke="#b45309" stroke-width="2"/>
  <polyline points="268,175 250,60" fill="none" stroke="#22c55e" stroke-width="2"/>
  <polyline points="250,175 255,60" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,2"/>
  <circle cx="259" cy="135" r="8" fill="#6366f1" opacity="0.8"/>
  <text x="259" y="139" fill="white" font-size="9" text-anchor="middle">→</text>
  <text x="259" y="195" fill="#a5b4fc" font-size="9" text-anchor="middle">Verbleibt auf Position</text>
  <!-- Panel 3: Labilität -->
  <rect x="354" y="30" width="155" height="165" fill="#2a0a0a" rx="8" stroke="#ef4444" stroke-width="1.5"/>
  <text x="431" y="50" fill="#fca5a5" font-size="12" font-weight="bold" text-anchor="middle">LABILITÄT</text>
  <line x1="431" y1="60" x2="431" y2="175" stroke="#444" stroke-width="1"/>
  <polyline points="455,175 405,60" fill="none" stroke="#b45309" stroke-width="2"/>
  <polyline points="441,175 415,60" fill="none" stroke="#22c55e" stroke-width="2"/>
  <polyline points="408,175 462,60" fill="none" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4,2"/>
  <circle cx="431" cy="90" r="8" fill="#ef4444" opacity="0.8"/>
  <text x="431" y="94" fill="white" font-size="9" text-anchor="middle">↑</text>
  <text x="431" y="195" fill="#fca5a5" font-size="9" text-anchor="middle">Steigt weiter (beschleunigt)</text>
</svg>"""

SVG_WOLKEN = """<svg viewBox="0 0 520 330" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:520px;font-family:system-ui,sans-serif">
  <rect width="520" height="330" fill="#0d1623" rx="10"/>
  <text x="260" y="20" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Abb. 42 – Klassifizierung von Wolken nach Stockwerken</text>
  <!-- Hohes Stockwerk -->
  <rect x="0" y="30" width="520" height="85" fill="#0a1535" opacity="0.8"/>
  <text x="10" y="50" fill="#93c5fd" font-size="11" font-weight="bold">HOHES STOCKWERK  &gt; 18.000 ft · Reine Eiswolken · Temp &lt; −30°C</text>
  <rect x="15" y="57" width="88" height="48" fill="#172554" rx="8" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="59" y="77" fill="white" font-size="11" text-anchor="middle" font-weight="bold">Cirrus</text>
  <text x="59" y="91" fill="#93c5fd" font-size="9" text-anchor="middle">Ci · fadenartig</text>
  <text x="59" y="101" fill="#64748b" font-size="8" text-anchor="middle">Warmfront-Vorläufer</text>
  <rect x="115" y="57" width="100" height="48" fill="#172554" rx="8" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="165" y="77" fill="white" font-size="11" text-anchor="middle" font-weight="bold">Cirrocumulus</text>
  <text x="165" y="91" fill="#93c5fd" font-size="9" text-anchor="middle">Cc · Schäfchen</text>
  <rect x="228" y="57" width="100" height="48" fill="#172554" rx="8" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="278" y="77" fill="white" font-size="11" text-anchor="middle" font-weight="bold">Cirrostratus</text>
  <text x="278" y="91" fill="#93c5fd" font-size="9" text-anchor="middle">Cs · Halo-Effekt</text>
  <!-- 18.000 ft line -->
  <line x1="0" y1="115" x2="520" y2="115" stroke="#334477" stroke-width="1.5" stroke-dasharray="6,4"/>
  <text x="3" y="124" fill="#4466aa" font-size="9">— 18.000 ft —</text>
  <!-- Mittleres Stockwerk -->
  <rect x="0" y="118" width="520" height="80" fill="#091520" opacity="0.8"/>
  <text x="10" y="135" fill="#7dd3fc" font-size="11" font-weight="bold">MITTLERES STOCKWERK  6.500 – 18.000 ft · Mischwolken · Temp −10 bis −30°C</text>
  <rect x="15" y="142" width="105" height="45" fill="#0c2130" rx="8" stroke="#0ea5e9" stroke-width="1.5"/>
  <text x="67" y="162" fill="white" font-size="11" text-anchor="middle" font-weight="bold">Altocumulus</text>
  <text x="67" y="175" fill="#7dd3fc" font-size="9" text-anchor="middle">Ac · Lenticularis (Föhn)</text>
  <rect x="135" y="142" width="95" height="45" fill="#0c2130" rx="8" stroke="#0ea5e9" stroke-width="1.5"/>
  <text x="182" y="162" fill="white" font-size="11" text-anchor="middle" font-weight="bold">Altostratus</text>
  <text x="182" y="175" fill="#7dd3fc" font-size="9" text-anchor="middle">As · Dauerregen</text>
  <!-- 6.500 ft line -->
  <line x1="0" y1="198" x2="520" y2="198" stroke="#334477" stroke-width="1.5" stroke-dasharray="6,4"/>
  <text x="3" y="208" fill="#4466aa" font-size="9">— 6.500 ft —</text>
  <!-- Unteres Stockwerk -->
  <rect x="0" y="200" width="520" height="80" fill="#081510" opacity="0.8"/>
  <text x="10" y="218" fill="#86efac" font-size="11" font-weight="bold">UNTERES STOCKWERK  &lt; 6.500 ft · Wasserwolken · Vereisungsgefahr</text>
  <rect x="15" y="225" width="80" height="45" fill="#0a200e" rx="8" stroke="#22c55e" stroke-width="1.5"/>
  <text x="55" y="250" fill="white" font-size="11" text-anchor="middle" font-weight="bold">Cumulus</text>
  <rect x="108" y="225" width="105" height="45" fill="#0a200e" rx="8" stroke="#22c55e" stroke-width="1.5"/>
  <text x="160" y="250" fill="white" font-size="11" text-anchor="middle" font-weight="bold">Stratocumulus</text>
  <rect x="226" y="225" width="75" height="45" fill="#0a200e" rx="8" stroke="#22c55e" stroke-width="1.5"/>
  <text x="263" y="250" fill="white" font-size="11" text-anchor="middle" font-weight="bold">Stratus</text>
  <!-- Hochreichend rechts -->
  <rect x="345" y="45" width="165" height="235" fill="#1a0808" rx="8" stroke="#ef4444" stroke-width="2"/>
  <text x="427" y="65" fill="#fca5a5" font-size="11" text-anchor="middle" font-weight="bold">HOCHREICHEND</text>
  <rect x="355" y="72" width="145" height="48" fill="#2a0808" rx="6" stroke="#ef4444" stroke-width="1"/>
  <text x="427" y="93" fill="white" font-size="12" text-anchor="middle" font-weight="bold">Cumulonimbus</text>
  <text x="427" y="107" fill="#fca5a5" font-size="9" text-anchor="middle">Cb · bis Tropopause!</text>
  <rect x="355" y="130" width="145" height="40" fill="#181010" rx="6" stroke="#92400e" stroke-width="1"/>
  <text x="427" y="152" fill="white" font-size="11" text-anchor="middle" font-weight="bold">Nimbostratus</text>
  <text x="427" y="165" fill="#fcd34d" font-size="9" text-anchor="middle">Ns · Dauerregen</text>
  <text x="427" y="195" fill="#fca5a5" font-size="10" text-anchor="middle">⚡ Blitz</text>
  <text x="427" y="210" fill="#fca5a5" font-size="10" text-anchor="middle">💨 Extreme Turbulenz</text>
  <text x="427" y="225" fill="#fca5a5" font-size="10" text-anchor="middle">🧊 Starke Vereisung</text>
  <text x="427" y="240" fill="#fca5a5" font-size="10" text-anchor="middle">☄ Hagel</text>
  <text x="427" y="260" fill="#ef4444" font-size="11" text-anchor="middle" font-weight="bold">NIEMALS DURCHFLIEGEN!</text>
  <text x="427" y="272" fill="#ef4444" font-size="9" text-anchor="middle">Min. 5 NM Abstand seitlich</text>
  <!-- Ground -->
  <rect x="0" y="285" width="520" height="45" fill="#2d5a1b" opacity="0.7" rx="0"/>
  <text x="260" y="310" fill="#86efac" font-size="10" text-anchor="middle">Erdboden</text>
</svg>"""

# ═══════════════════════════════════════════════════════════════════════════
# Kapitel 1 – Die Atmosphäre (Seiten 9–44)
# Basiert auf PDF 176-210.pdf
# ═══════════════════════════════════════════════════════════════════════════
KAPITEL1_ID = "meteorologie-kapitel-1-die-atmosphare-aufbau-strahlung-physik"

KAPITEL1_SECTIONS = [
    # ── 1. Die Atmosphäre ────────────────────────────────────────────────
    ("heading", "1  Die Atmosphäre", ""),
    ("text",
     "Unsere Erde ist umgeben von einer Gashülle aus Luft – der Atmosphäre. Diese Atmosphäre "
     "ermöglicht aufgrund ihrer Zusammensetzung das Fliegen von Luftfahrzeugen und ist gleichzeitig "
     "Grundlage für das Leben auf der Erde. Im Vergleich zum Erdumfang ist die Atmosphäre nur sehr "
     "dünn, etwa vergleichbar mit der Außenhaut eines Balls.", ""),
    ("text",
     "Bei jedem Flug bewegen wir uns innerhalb der Atmosphäre und sind deren Phänomenen wie Wolken, "
     "Wind und Niederschlag ausgesetzt, profitieren aber auch beispielsweise vom Auftrieb. "
     "Gleichzeitig ermöglicht der Sauerstoff in der Luft die Verbrennung des Treibstoffs in den "
     "Triebwerken. Auch Aufwinde in Form von Thermik oder Wellen sind atmosphärische Phänomene.", ""),

    # ── 1.1 Aufbau ───────────────────────────────────────────────────────
    ("subheading", "1.1  Aufbau der Erdatmosphäre", ""),
    ("text",
     "Mit zunehmender Entfernung vom Erdboden verändern sich einige physikalische Eigenschaften der "
     "Atmosphäre, andere wiederum bleiben auch bis in große Höhen konstant. Für die Vorgänge "
     "innerhalb der Atmosphäre sind diejenigen Höhen relevant, in denen sich bestimmte Eigenschaften "
     "ändern. Der Temperaturverlauf mit zunehmender Höhe ist dabei für das Wettergeschehen von "
     "besonderer Bedeutung.", ""),

    # ── 1.1.1 Atmosphärenzusammensetzung ────────────────────────────────
    ("subheading", "1.1.1  Atmosphärenzusammensetzung", ""),
    ("text",
     "Die Zusammensetzung der Erdatmosphäre bleibt vom Boden bis in große Höhen (etwa 80 km) nahezu "
     "konstant. Den größten Teil in diesem Gasgemisch machen dabei Stickstoff (78%) und Sauerstoff "
     "(21%) aus. Das verbleibende Prozent setzt sich aus Kohlendioxid und Edelgasen zusammen. Auch "
     "gasförmiger Wasserdampf kann bevorzugt in den unteren Schichten der Atmosphäre enthalten sein. "
     "Der Wasserdampf ist maßgeblich für das Wettergeschehen verantwortlich. Sein Anteil ist räumlich "
     "und zeitlich sehr variabel und von der Wetterlage an einem bestimmten Ort abhängig. Enthält die "
     "Luft Wasserdampf, so sind es üblicherweise zwischen 1% und 4% Anteil am Gesamtvolumen – die "
     "übrigen Gase sinken entsprechend.", ""),
    ("diagram", SVG_ZUSAMMENSETZUNG, "Abb. 1 – Zusammensetzung der Atmosphäre"),
    ("fact",
     "Stickstoff (N₂): 78% · Sauerstoff (O₂): 21% · CO₂ + Edelgase: ~1% · "
     "Wasserdampf: 0–4% (variabel, nur Troposphäre). "
     "Die in der Tabelle genannte prozentuale Zusammensetzung der Luft gilt daher nur für absolut "
     "trockene Luft ohne Wasserdampf.", ""),

    # ── 1.1.2 Schichten ─────────────────────────────────────────────────
    ("subheading", "1.1.2  Schichten der Atmosphäre", ""),
    ("text",
     "Die Einteilung der Atmosphäre in Schichten erfolgt anhand des Temperaturverlaufs. Die untersten "
     "bodennahen Luftschichten nehmen die Temperatur des Erdbodens an; dieser wiederum wird tagsüber "
     "durch die Sonneneinstrahlung erwärmt und kühlt sich nachts infolge von Wärmeabstrahlung wieder "
     "ab. Die bodennahen Luftschichten werden also im Wesentlichen durch den Wärmeaustausch mit dem "
     "Erdboden abgekühlt bzw. erwärmt; die Erwärmung erfolgt nicht direkt durch das Sonnenlicht. "
     "Daher nimmt die Temperatur der Luft mit zunehmender Entfernung vom Erdboden ab: In der Höhe "
     "ist es im Allgemeinen kälter als am Boden.", ""),
    ("diagram", SVG_SCHICHTEN, "Abb. 2 – Schematischer Verlauf der Temperatur mit zunehmender Höhe"),
    ("text",
     "In der untersten Schicht, der Troposphäre, nimmt die Temperatur mit zunehmender Entfernung "
     "vom Boden ab. Innerhalb dieser Schicht spielen sich die wichtigsten meteorologischen Vorgänge "
     "wie Wolken- und Niederschlagsbildung ab. Eine Isothermie in etwa 11 km Höhe sowie eine darüber "
     "liegende Inversion bilden eine weitere Schicht, die Stratosphäre. Die Stratosphäre erstreckt "
     "sich bis in ungefähr 50 km Höhe. Oberhalb schließt sich die Mesosphäre bis etwa 80 km Höhe "
     "an. Noch weiter oben folgen die Ionosphäre (oder Thermosphäre) und die Exosphäre, die "
     "schließlich fließend in den Weltraum übergeht.", ""),
    ("table_row", "Troposphäre", "0–11 km · Temperatur ↓ 0,65°C/100m · Wetter, Wolken, Niederschlag"),
    ("table_row", "Tropopause", "Grenzschicht ~11 km · Äquator: 16–18 km · Pol: 6–8 km"),
    ("table_row", "Stratosphäre", "11–50 km · Temperatur erst konstant, dann ↑ · Ozonschicht 15–50 km"),
    ("table_row", "Mesosphäre", "50–80 km · Temperatur ↓"),
    ("table_row", "Ionosphäre / Thermosphäre", "80+ km · sehr hohe rechnerische Temperaturen"),
    ("table_row", "Exosphäre", "Äußerste Schicht · geht in Weltraum über"),
    ("subheading", "Die Tropopause", ""),
    ("text",
     "Die Grenzschicht zwischen der Troposphäre und der Stratosphäre heißt Tropopause und stellt die "
     "Obergrenze des Wettergeschehens dar. Innerhalb der Troposphäre, also unterhalb der Tropopause, "
     "nimmt die Temperatur mit der Höhe um durchschnittlich 0,65°C pro 100 m (2°C pro 1.000 ft) ab. "
     "Die Höhe der Tropopause ist dabei von verschiedenen Faktoren abhängig wie der geographischen "
     "Breite, der Jahreszeit und der Luftmasse, die sich darunter befindet.", ""),
    ("fact",
     "Merkrege Tropopause: Am Äquator ist die Tropopause höher als am Pol. "
     "Im Sommer ist die Tropopause höher als im Winter. "
     "In Warmluft ist die Tropopause höher als in Kaltluft. "
     "Am Äquator ist die Tropopause am KÄLTESTEN (größere Höhe → kältere Temperatur trotz warmer Oberfläche).", ""),

    # ── 1.1.3 Strahlungshaushalt ─────────────────────────────────────────
    ("subheading", "1.1.3  Strahlungshaushalt", ""),
    ("text",
     "Unter Strahlungshaushalt versteht man die Summe der Energieströme, die sich zwischen der Erde, "
     "der Atmosphäre und dem umgebenden Weltall abspielen. Auf der einen Seite wird dem System "
     "Atmosphäre und Erde von der Sonne elektromagnetische Strahlung (Sonnenstrahlung) zugeführt. "
     "Auf der anderen Seite geben Atmosphäre und Erde auch Wärmestrahlung (als terrestrische "
     "Strahlung) wieder ab. Insgesamt stellt sich im Mittel über lange Zeiträume ein Gleichgewicht "
     "von zugeführter und abgegebener Strahlungsenergie in der Atmosphäre ein.", ""),
    ("diagram", SVG_STRAHLUNG, "Abb. 23 – Vereinfachte Strahlungsbilanz der Erde"),
    ("text",
     "Nicht die gesamte Sonnenstrahlung kommt tatsächlich auf der Erdoberfläche an. Ein großer Teil "
     "des einfallenden Lichts wird durch Prozesse wie Reflexion oder Streuung wieder in den Weltraum "
     "gelenkt, ein anderer Teil wiederum in höheren Atmosphärenschichten absorbiert. Der Teil des "
     "Sonnenlichts, der am Erdboden tatsächlich ankommt, wird am Erdboden absorbiert und sorgt so "
     "für dessen Erwärmung oder wird ebenfalls direkt wieder reflektiert.", ""),
    ("text",
     "Die Reflexion: Auf die Erde einfallende Sonnenstrahlung wird zum großen Teil durch Wolken und "
     "die Erdoberfläche, insbesondere die Wasserflächen, zurück in den Weltraum reflektiert. Insgesamt "
     "werden im Mittel etwa 33% der verfügbaren Sonnenstrahlung in den Weltraum reflektiert.", ""),
    ("text",
     "Die Streuung: Wenn ein so genanntes Lichtteilchen (Teilchen eines Lichtstrahls) auf ein "
     "Luftmolekül trifft, kann es dieses für einen kurzen Moment in einen 'angeregten Zustand' "
     "versetzen. Das Luftmolekül fällt aber sehr schnell wieder in den ursprünglichen Zustand zurück "
     "– hierbei wird dasselbe Lichtteilchen wieder ausgesendet, wobei dies jedoch in einer anderen "
     "als der ursprünglichen Strahlungsrichtung erfolgen kann. Blaues kurzwelliges Licht wird viel "
     "effektiver gestreut als die übrigen Farben, etwa um Faktor 16 stärker als rotes Licht. Dies "
     "führt dazu, dass beim Blick durch die Atmosphäre in Richtung Luftmoleküle in jeder Richtung "
     "Luftmoleküle sichtbar werden, die gerade blaues Licht in Richtung Beobachter streuen – die "
     "Streuung lässt den Himmel blau erscheinen.", ""),
    ("text",
     "Die Absorption: In unterschiedlichen Höhen in der Atmosphäre können Teile des Sonnenlichts mit "
     "den Luftteilchen wechselwirken und physikalische sowie chemische Prozesse auslösen. Das Licht "
     "liefert dabei die notwendige Energie für diese Prozesse. Insgesamt werden etwa 15% des "
     "einfallenden Sonnenlichts absorbiert. Die absorbierte Strahlung erreicht den Erdboden somit "
     "nicht. Ein Beispiel hierfür ist kurzwelliges, ultraviolettes Licht (UV-B), das in der "
     "Ozonschicht (ca. 15–50 km Höhe) 'verbraucht' und somit aus dem Sonnenlicht herausgefiltert wird.", ""),
    ("text",
     "Die Strahlungsbilanz gibt die Differenz zwischen zugeführter und abgestrahlter Energie in der "
     "Erdatmosphäre an. Die Strahlungsbilanz ist tagsüber positiv, wenn die Sonne die Erdoberfläche "
     "infolge der Sonneneinstrahlung erwärmt. Sie wird negativ, wenn die Erdoberfläche nachts "
     "langwellige Wärmestrahlung abgibt. In klaren Nächten wird es daher deutlich kälter als unter "
     "geschlossenen Wolkendecken. Aber auch Gase wie Kohlendioxid und Wasserdampf haben "
     "'Absorptionsbanden' im langwelligen Spektralbereich der terrestrischen Strahlung und sind daher "
     "in der Lage, den Verlust von Wärmestrahlung an das Weltall zu reduzieren.", ""),
    ("fact",
     "Merksatz: Das Sonnenlicht erwärmt den Erdboden direkt – NICHT die Atmosphäre! "
     "Die Atmosphäre erwärmt sich durch Wärmeabgabe des Bodens (Wärmestrahlung + Wärmeaustausch). "
     "Strahlungsbilanz tagsüber: positiv (Einstrahlung > Ausstrahlung). "
     "Nachts: negativ (nur Ausstrahlung). Wolken wirken temperaturausgleichend.", ""),
    ("infobox",
     "Die in der Diskussion befindliche 'Globale Erwärmung' beschreibt die Tatsache, dass dieses "
     "Gleichgewicht gestört ist und mehr Energie von der Erde aufgenommen als wieder abgegeben wird. "
     "In den letzten Jahrzehnten wird der diskutierte Treibhauseffekt in Verbindung mit der globalen "
     "Erwärmung angesprochen. Es geht dabei um die Frage, ob das vom Menschen erzeugte Kohlendioxid "
     "als Hauptverursacher für die nachweisliche globale Erwärmung in Frage kommt.",
     "Globale Erwärmung"),

    # ── 1.2 Physikalische Eigenschaften ─────────────────────────────────
    ("heading", "1.2  Physikalische Eigenschaften", ""),
    ("text",
     "Für Wetterbeobachtungen ist der Zustand der Erdatmosphäre messtechnisch zu erfassen. Relevant "
     "sind hierbei Daten wie Luftdruck, Temperatur, Luftfeuchtigkeit sowie Wind und deren tatsächlicher "
     "Verlauf mit zunehmender Höhe. Diese Parameter fließen in Wettermodelle zur Vorhersage ein und "
     "bilden gleichzeitig das Fundament für die Beschreibung von komplexeren Vorgängen in der "
     "Atmosphäre. Auch für die Flugvorbereitung sind diese Zustandsbeschreibungen von großer "
     "Bedeutung.", ""),

    # ── 1.2.1 Druck ──────────────────────────────────────────────────────
    ("subheading", "1.2.1  Druck", ""),
    ("text",
     "Auch wenn es zunächst nicht den Anschein macht, hat die Erdatmosphäre ein hohes Eigengewicht, "
     "das auf der Erdoberfläche lastet. Das wird deutlich, wenn man sich vergegenwärtigt, dass ein "
     "Kubikmeter Luft auf Meereshöhe etwa 1,3 kg wiegt. Durch die Erdanziehungskraft wird die "
     "Atmosphäre dabei an der Erde gehalten, wobei die oberen Schichten die unteren Schichten "
     "'zusammendrücken'. Dieser Druck wird als Luftdruck messbar.", ""),
    ("text",
     "Formal beschreibt Druck das Verhältnis aus Kraft pro Fläche: P = F(N) / A(m²). "
     "F steht hierbei für die Kraft (force) und A für die Fläche (area). Die Einheit von Druck ist "
     "dementsprechend Newton (N) pro Quadratmeter, da Newton die Einheit von Kraft ist. Der Druck, "
     "den genau 1 Newton über einem Quadratmeter ausübt, heißt 1 Pascal (Pa). Der Luftdruck am Boden "
     "beträgt im Mittel 1013,25 hPa. hPa meint dabei Hektopascal, auch Einheiten von 100 Pa. Eine "
     "andere, in der Meteorologie übliche Einheit ist Millibar (mbar). 1.000 mbar ergeben 1 bar. "
     "Außerdem gilt praktischerweise: 1 mbar = 1 hPa. Die Einheiten hPa und mbar lassen sich also "
     "synonym verwenden. Am Boden herrscht ungefähr ein Luftdruck von 1 bar.", ""),
    ("diagram", SVG_DRUCK, "Abb. 6 – Verlauf von Druck, Temperatur und Dichte in der Atmosphäre"),
    ("text",
     "Gemessen wird der Luftdruck mit einem Barometer. Der Luftdruck am Boden ergibt sich aus der "
     "Gewichtskraft der Luftsäule, die auf einer bestimmten Fläche am Boden lastet. Ein historisches "
     "Verfahren zur Luftdruckmessung ist das Quecksilberbarometer: In einem U-Rohr, das auf einer "
     "Seite geschlossen ist, befindet sich flüssiges Quecksilber. Auf der offenen Seite des U-Rohrs "
     "lastet der Umgebungsluftdruck. Über dem Quecksilber auf der geschlossenen Seite befindet sich "
     "ein Vakuum. Der Luftdruck drückt auf die offene Seite das Quecksilber nach unten, wodurch es "
     "auf der anderen Seite des Rohres nach oben steigt. Dem Standard-Atmosphärendruck entsprechen "
     "760 mmHg (1 Torr).", ""),
    ("diagram", SVG_BAROMETER, "Abb. 4/5 – Quecksilberbarometer und Dosenbarometer"),
    ("text",
     "Das in Luftfahrzeuginstrumenten tatsächlich übliche Messverfahren des Dosenbarometers oder "
     "Aneroidbarometers funktioniert mit Hilfe einer (fast) luftleeren Dose, in der eine Feder gegen "
     "den äußeren Luftdruck wirkt. Sinkt der Luftdruck, kann sich die Dose durch die innere "
     "Federkraft weiter ausdehnen. Bei zunehmendem äußerem Druck wird die Dose weiter "
     "zusammengedrückt. Diese Bewegungen der Aneroiddose sind somit ein direktes Maß für den "
     "wirkenden Luftdruck und werden über eine Mechanik auf einen Zeiger im Instrument übertragen.", ""),
    ("fact",
     "1 mbar = 1 hPa · Standardatmosphäre: 1013,25 hPa · "
     "760 mmHg = 29,92 inHg = 1013,25 hPa · "
     "Barometrische Höhenstufe MSL: 27 ft/hPa (8 m/hPa) · "
     "Halbierung des Luftdrucks alle ca. 5.500 m (≈18.000 ft) · "
     "36.000 ft / 11.000 m: 108 ft/hPa (32 m/hPa)", ""),
    ("table_row", "Barometrische Höhenstufe MSL", "27 ft/hPa (8 m/hPa)"),
    ("table_row", "Barometrische Höhenstufe 18.000 ft / 5.500 m", "54 ft/hPa (16 m/hPa)"),
    ("table_row", "Barometrische Höhenstufe 36.000 ft / 11.000 m", "108 ft/hPa (32 m/hPa)"),

    # ── 1.2.2 Temperatur ─────────────────────────────────────────────────
    ("subheading", "1.2.2  Temperatur", ""),
    ("text",
     "Mit dem Begriff Temperatur wird oft das ganz persönliche Wärmeempfinden verbunden. So können "
     "unterschiedliche Medien bei gleicher Temperatur tatsächlich als unterschiedlich warm oder kalt "
     "empfunden werden. Die im Wetterbericht genannte Lufttemperatur meint jedoch eine recht nüchterne "
     "Zahl, die sich aus der mittleren Bewegungsenergie der Luftmoleküle ergibt. Wärme entsteht dabei "
     "durch die Bewegung von Molekülen eines Körpers. Je stärker sich die Moleküle bewegen, umso höher "
     "ist auch die Temperatur. Angegeben wird die Temperatur entsprechend der Standardeinheiten in "
     "Grad Celsius (°C). Dabei entspricht der Siedepunkt von Wasser unter Standardbedingungen 100°C, "
     "der Gefrierpunkt 0°C. In anglophonen Ländern wird oft die Einheit Grad Fahrenheit (°F) "
     "verwendet. Der Siedepunkt von Wasser unter Standardbedingungen bei 212°F, der Gefrierpunkt bei "
     "32°F. Es gelten folgende Umrechnungsformeln: K = °C + 273 · °C = (°F-32) × 5/9 · "
     "°F = °C × 9/5 + 32.", ""),
    ("text",
     "Gemessen wird die Temperatur in einer sonnengeschützten, aber gut durchlüfteten weiß gestrichenen "
     "Wetterhütte zwei Meter über der Erdoberfläche. Die Türen werden nach Norden geöffnet, damit beim "
     "Ablesen der Instrumente keine störende Sonnenstrahlung einfallen kann. Die Temperatur der "
     "umgebenden Luft ist örtlichen und zeitlichen Schwankungen unterworfen, die eine Vielzahl von "
     "Ursachen haben können. Markante Einflussfaktoren sind beispielsweise: Tageszeit · Geographische "
     "Breite · Jahreszeit · Bewölkungsgrad · Oberflächenbeschaffenheit · Windeinflüsse.", ""),
    ("text",
     "Tagsüber wird die Lufttemperatur vor allem durch die Intensität der Sonneneinstrahlung bestimmt "
     "(über die Absorption), nachts hingegen durch die terrestrische Ausstrahlung. Die größte "
     "potenzielle Wärmeenergie steht am Tag zur Verfügung, nachdem die Sonne an ihrem höchsten Stand "
     "die Atmosphäre indirekt erwärmt hat. Die geographische Breite und die Jahreszeit haben ebenfalls "
     "einen unmittelbaren Einfluss auf die Temperatur. In Äquatornähe steht die Sonne senkrechter am "
     "Himmel als in gemäßigten Breiten oder Polregionen, wodurch sich die Sonnenenergie auf einen "
     "kleineren Bereich konzentriert und den Äquatorbereich stärker erwärmt.", ""),
    ("fact",
     "Umrechnungsformeln: K = °C + 273 · °C = (°F − 32) × 5/9 · °F = °C × 9/5 + 32. "
     "Bewölkung wirkt temperaturausgleichend: Tagsüber Reflexion → kühler. "
     "Nachts Rückstrahlung → wärmer als bei klarem Himmel.", ""),

    # ── 1.2.3 Dichte ─────────────────────────────────────────────────────
    ("subheading", "1.2.3  Dichte", ""),
    ("text",
     "Aus dem Druck und der Temperatur von Luft ergibt sich die Anzahl der Luftteilchen in einem "
     "bestimmten Luftvolumen. Dieses Verhältnis aus der Anzahl von Teilchen oder deren Masse m pro "
     "Volumeneinheit V wird Dichte ρ (ausgesprochen Rho) genannt: ρ = m [kg] / V [m³]. "
     "Dichte von Luft hat am Boden im Mittel den Wert von 1,225 kg/m³. Zunächst ist festzustellen, "
     "dass sich Luft mit zunehmender Temperatur ausdehnt sowie die Bewegungsenergie und damit die "
     "mittlere Geschwindigkeit der Luftteilchen zunehmen. Diese benötigen nun etwas mehr Platz, da "
     "sie durch die erhöhte Bewegung ständig aneinander stoßen. Somit dehnt sich das gesamte "
     "Luftvolumen aus. Dieselbe Anzahl Luftteilchen verteilt sich jetzt auf ein größeres Volumen: die "
     "Dichte sinkt.", ""),
    ("text",
     "Der vertikale Dichteverlauf innerhalb der Atmosphäre verläuft tendenziell analog zum "
     "Druckverlauf. In den niedrigen Höhen ist die Dichte groß, weil die Luftmassen von der darüber "
     "liegenden Luftsäule zusammengedrückt werden. Mit zunehmender Höhe nimmt die Dichte ebenfalls "
     "ab. In kalter Luft liegen die Druckflächen dichter zusammen als in warmer Luft.", ""),
    ("fact",
     "Dichte ρ nimmt ab bei: hoher Temperatur · niedrigem Druck · hoher Luftfeuchtigkeit "
     "(H₂O-Moleküle sind leichter als N₂/O₂). "
     "In trockener Luft liegen die Druckflächen dichter zusammen als in feuchter Luft.", ""),

    # ── 1.2.4 Luftfeuchtigkeit ───────────────────────────────────────────
    ("subheading", "1.2.4  Luftfeuchtigkeit", ""),
    ("text",
     "Zu den bisher genannten Eigenschaften besitzt Luft die Fähigkeit Feuchtigkeit aufzunehmen. Wie "
     "viel Feuchtigkeit in Luft enthalten sein kann, hängt im Wesentlichen von der Temperatur der "
     "Luft, aber auch vom Druck ab. Je höher die Temperatur ist, umso mehr Feuchtigkeit kann Luft "
     "aufnehmen. Die Luftfeuchtigkeit kann als eine Menge von Wasser angegeben werden, welche sich "
     "in einem bestimmten Luftvolumen befindet. Da es sich dabei um die tatsächliche Menge handelt, "
     "wird sie als absolute Luftfeuchtigkeit bezeichnet. Sie wird in g/m³ angegeben. Eine besondere "
     "absolute Luftfeuchtigkeit ist die Sättigungsfeuchte, also die maximimal mögliche Menge "
     "Wasserdampf, die bei bestimmten Temperaturen in Luft enthalten sein kann. Die relative "
     "Luftfeuchtigkeit beschreibt das Verhältnis aus tatsächlicher und aktuell maximal möglicher "
     "Menge an Wasser in Prozent. Bei 100% relativer Feuchtigkeit entspricht die tatsächliche "
     "Wasserdampfmenge also der maximal möglichen – die Luft ist mit Feuchtigkeit gesättigt.", ""),
    ("table_row", "Absolute Feuchtigkeit", "Tatsächliche Menge Wasserdampf in g/m³ Luft"),
    ("table_row", "Sättigungsfeuchte", "Maximal mögliche Menge Wasserdampf bei gegebener Temperatur"),
    ("table_row", "Relative Feuchtigkeit", "Verhältnis tatsächlich / maximal möglich in % (100% = gesättigt)"),
    ("table_row", "Taupunkt", "Temperatur, auf die Luft abgekühlt werden muss, damit Kondensation eintritt"),
    ("table_row", "Spread", "Differenz Temperatur minus Taupunkt: Spread = T − Tp (°C)"),
    ("text",
     "Fällt die Temperatur unter den Taupunkt, ist zu viel Wasserdampf enthalten und die Kondensation "
     "beginnt. Dabei verringert sich die relative Feuchtigkeit genau in dem Maße, dass der Taupunkt "
     "der fallenden Temperatur folgt. Der Taupunkt kann niemals größer als die Temperatur sein. "
     "Ein Maß für die Tendenz zur Nebelbildung ist die Differenz zwischen aktueller Temperatur und "
     "Taupunkt – dieser Wert wird Spread (= Differenz) genannt.", ""),
    ("fact",
     "Spread = Temperatur − Taupunkt. "
     "Kleiner Spread → Neigung zu Nebelbildung, niedrige Wolkenuntergrenze. "
     "Spread = 0 → 100% relative Feuchtigkeit = Sättigung = Kondensation beginnt. "
     "KKN [ft] = Spread × 400 · KKN [m] = Spread × 123.", ""),

    # ── 1.2.5 ICAO-Standardatmosphäre ───────────────────────────────────
    ("subheading", "1.2.5  ICAO-Standardatmosphäre", ""),
    ("text",
     "In der ICAO-Standardatmosphäre (ISA) werden bestimmte Standardwerte angenommen, um eine "
     "einheitliche Referenz für die Angabe von Flugleistungen oder für die Eichung von Instrumenten "
     "zu haben. Bei Abweichungen von ISA können Flugleistungen daher besser oder schlechter sein und "
     "müssen für die tatsächlichen Bedingungen vor jedem Flug erneut geprüft werden. Eingeführt wurde "
     "sie vor allem, um ein einheitliches Höhenbezugssystem zu ermöglichen. Bei der Festlegung der "
     "ISA-Werte werden überwiegend globale Durchschnittswerte angenommen.", ""),
    ("table_row", "ISA Luftdruck MSL", "1013,25 hPa"),
    ("table_row", "ISA Temperatur MSL", "+15°C"),
    ("table_row", "ISA Luftdichte MSL", "1,225 kg/m³"),
    ("table_row", "ISA Temperaturabnahme Troposphäre", "0,65°C / 100 m (2°C / 1.000 ft)"),
    ("table_row", "ISA Tropopausenhöhe", "11 km (36.000 ft)"),
    ("table_row", "ISA Tropopausentemperatur", "−56,5°C"),
    ("table_row", "ISA Luftfeuchtigkeit", "0% (reine trockene Luft)"),
    ("fact",
     "ISA-Standardwerte MSL: 1013,25 hPa · +15°C · 1,225 kg/m³ · "
     "Temperaturabnahme: 0,65°C/100m · Tropopause: 11 km / −56,5°C. "
     "ΔISA = Abweichung der tatsächlichen Temperatur von ISA. "
     "Dichtehöhe-Korrektur: Δh = 120 ft pro 1°C ΔISA.", ""),

    # ── 1.3 Luftbewegungen ───────────────────────────────────────────────
    ("heading", "1.3  Luftbewegungen", ""),
    ("text",
     "In der Atmosphäre finden unterschiedliche Luftbewegungen statt. Die wohl bekannteste Form ist "
     "der Wind, eine horizontal gerichtete Bewegung von Luft. Für die Wolkenbildung sind allerdings "
     "nicht die horizontalen, sondern die vertikalen Luftbewegungen in der Atmosphäre relevant. Mit "
     "der vertikalen Bewegung von Luft sind Volumen- und Temperaturänderungen verbunden, welche "
     "wiederum zu Änderungen der relativen Luftfeuchte führen. Im Fall der aufwärts gerichteten "
     "Vertikalbewegung (Hebung) kann dieser Prozess zur Kondensation in der Höhe mit Wolkenbildung "
     "führen, im Fall der abwärts gerichteten Vertikalbewegung (Absinken) ist dagegen Verdunstung "
     "und Wolkenauflösung verbunden.", ""),

    ("subheading", "1.3.1  Schichtung in der Atmosphäre", ""),
    ("text",
     "Der Temperaturverlauf in der Atmosphäre wurde bereits skizziert. Für das Wettergeschehen "
     "relevant ist hierbei das Geschehen in der Troposphäre. Kennzeichnend für diese Schicht ist eine "
     "Temperaturabnahme mit der Höhe von durchschnittlich 0,65°C / 100 m (oder 2°C / 1.000 ft), "
     "welche auch in der ICAO-Standardatmosphäre angenommen wird. Die tatsächlichen Verhältnisse "
     "sehen allerdings nicht ganz so gleichmäßig aus. So nimmt die Temperatur unterschiedlich stark "
     "ab, und es gibt auch innerhalb der Troposphäre Inversionen und Isothermien, also Bereiche in "
     "denen sich die Temperatur mit der Höhe umkehrt bzw. gleich bleibt. Der tatsächliche "
     "Temperaturverlauf bestimmt die Schichtung der Atmosphäre (Schichtungsgradient).", ""),
    ("table_row", "Isothermie", "Temperatur bleibt mit der Höhe konstant"),
    ("table_row", "Inversion", "Temperatur nimmt mit der Höhe zu (stabilisierend)"),
    ("table_row", "Bodeninversion", "Bodennah, durch nächtliche Ausstrahlung des Erdbodens"),
    ("table_row", "Höheninversion", "In größerer Höhe, kein Wettergeschehen darunter"),

    ("subheading", "1.3.2  Adiabatische Prozesse", ""),
    ("text",
     "Mit dem Aufstieg eines Luftpakets ist eine Abkühlung verbunden, da der mit der Höhe "
     "nachlassende Luftdruck dazu führt, dass sich das Luftpaket ausdehnt. Diese Expansion ist mit "
     "Arbeit verbunden, da sich das Luftpaket gegen den herrschenden äußeren Luftdruck ausdehnen "
     "muss. Die dafür notwendige Energie muss das Luftpaket 'aus eigener Kraft' aufbringen, was mit "
     "einem Temperaturgang verbunden ist. Aus dem Alltag ist besonders der umgekehrte Effekt bekannt: "
     "die Erwärmung bei Kompression von Luft. Beim Aufpumpen eines Fahrradreifens mit einer "
     "Handluftpumpe spürt man sehr schnell eine deutliche Erwärmung der Luftpumpe.", ""),
    ("text",
     "Diese idealisierte, adiabatisch ablaufende Form der Luftbewegung wird adiabatischer Aufstieg "
     "genannt. Adiabatisch bedeutet, dass bei einer Volumen- und Temperaturänderung einer vertikalen "
     "Luftbewegung kein Temperaturausgleich mit der Umgebung stattfindet. Wie stark die Abkühlung "
     "bei einem adiabatischen Luftaufstieg ist, hängt davon ab, ob beim Aufstieg Kondensation "
     "stattfindet oder nicht. Freiwerdende Kondensationswärme kann dabei der Abkühlung "
     "entgegenwirken.", ""),
    ("diagram", SVG_ADIABATISCH, "Abb. 14/15 – Trocken- und Feuchtadiabatischer Aufstieg"),
    ("text",
     "Trockenadiabatischer Aufstieg (DALR): Mit der Erwärmung eines lokal begrenzten Luftpakets am "
     "Boden (z.B. durch Sonneneinstrahlung über einem Steinbruch) nimmt die Dichte ab. Eine "
     "geringere Dichte bedeutet, dass das Luftpaket leichter wird als die umgebende Luft und dadurch "
     "aufsteigt und sich dabei außerdem abkühlt. Der Aufstieg erfolgt zunächst trockenadiabatisch, "
     "also mit einer Temperaturabnahme von exakt 1°C / 100 m. Generell verringert sich der Spread "
     "in aufsteigender Luft und vergrößert sich in absinkender Luft.", ""),
    ("text",
     "Feuchtadiabatischer Aufstieg (SALR): Wenn der Taupunkt des trockenadiabatisch aufsteigenden "
     "Luftpakets erreicht wird, wird Kondensation ausgelöst. Während des Kondensationsvorgangs wird "
     "Energie frei. Diese zuvor als latente Wärme enthaltene Energie wirkt der Abkühlung des "
     "Luftpakets beim weiteren Aufstieg entgegen – die Kondensationswärme 'heizt' die aufsteigende "
     "Luft. Dennoch kann die Abkühlung nicht ganz kompensiert werden, sodass sich die Luft auch "
     "beim feuchtadiabatischen Aufstieg weiter abkühlt. Im Mittel wird für den feuchtadiabatischen "
     "Temperaturgradienten ein Wert von 0,6°C / 100 m angenommen.", ""),
    ("fact",
     "DALR (Trockenadiabatischer Temperaturgradient): 1°C / 100 m. "
     "SALR (Feuchtadiabatischer Temperaturgradient): ≈ 0,6°C / 100 m (Mittelwert; je nach Feuchte 0,3–0,9°C/100 m). "
     "ISA-Standardatmosphäre: 0,65°C / 100 m. "
     "Spread verringert sich beim Aufstieg → KKN = Spread × 400 [ft].", ""),

    ("subheading", "1.3.3  Stabilität und Labilität", ""),
    ("text",
     "Ob ein aufsteigendes Luftpaket seinen Aufstieg fortsetzen kann, hängt von der Schichtung der "
     "umgebenden Luft ab. Hierzu spielt die Stabilität der Luftschichtung eine Rolle, wobei "
     "grundsätzlich drei Situationen zu unterscheiden sind: Stabilität · Labilität · Indifferenz.", ""),
    ("text",
     "Stabilität: Eine stabile Situation ist dadurch gekennzeichnet, dass ein Körper (oder auch ein "
     "Luftpaket) bei Auslenkung um seine Ruhelage wieder in diese Ruhelage zurückgeführt wird. "
     "Übertragen auf das Luftpaket bedeutet Stabilität, dass der Aufstieg des Luftpakets gebremst "
     "wird und das Luftpaket wieder in seine ursprüngliche Lage zurücksinkt. Mit anderen Worten: "
     "Der Gradient der umgebenden Luft (Schichtungsgradient) muss kleiner sein als der adiabatische "
     "Temperaturgradient (Hebungsgradient) des aufsteigenden Luftpakets.", ""),
    ("text",
     "Labilität: Eine labile Situation ist dadurch gekennzeichnet, dass ein Körper (oder auch ein "
     "Luftpaket) bei Auslenkung nicht wieder dorthin zurückkehrt, sondern die Bewegung aus der "
     "Ruhelage heraus sogar noch beschleunigt wird. Übertragen auf das Luftpaket bedeutet Labilität, "
     "dass ein Luftpaket beim Aufstieg sogar noch weiter beschleunigt werden kann. Der "
     "Schichtungsgradient muss demnach größer sein als der adiabatische Temperaturgradient.", ""),
    ("text",
     "Indifferenz: Eine indifferente Situation ist dadurch gekennzeichnet, dass ein Körper (oder "
     "auch ein Luftpaket) bei Auslenkung um seine Ruhelage weder eine Tendenz in Richtung "
     "Ruhelage noch in Richtung weiterer Beschleunigung zeigt. Die Umgebung muss also ständig "
     "dieselbe Temperatur wie das Luftpaket selbst haben. Der Schichtungsgradient muss folglich "
     "mit dem Hebungsgradienten übereinstimmen.", ""),
    ("diagram", SVG_STABILIT, "Abb. 25/26 – Stabilität, Indifferenz und Labilität"),
    ("fact",
     "Stabilität: Schichtungsgradient < Hebungsgradient → Luftpaket kühler als Umgebung → sinkt zurück. "
     "Labilität: Schichtungsgradient > Hebungsgradient → Luftpaket wärmer als Umgebung → steigt weiter. "
     "Indifferenz: Schichtungsgradient = Hebungsgradient.", ""),

    ("subheading", "1.3.4  Stabilität in der Atmosphäre", ""),
    ("text",
     "In den Beispielen zur Stabilität und Labilität wurde jeweils nicht spezifiziert, ob das "
     "Luftpaket trocken- oder feuchtadiabatisch aufsteigt. Meist beginnt der Aufstieg "
     "trockenadiabatisch, die Abkühlung während des Aufstiegs kann jedoch dazu führen, dass der "
     "Taupunkt des Luftpakets unterschritten wird und Kondensation einsetzt. Der weitere Aufstieg "
     "erfolgt dann nicht mehr trocken- sondern feuchtadiabatisch.", ""),
    ("table_row", "Absolute Stabilität",
     "Schichtungsgradient < DALR und SALR → stabil für trocken- UND feuchtadiabatische Aufstiege"),
    ("table_row", "Bedingte Stabilität (Feuchtlabilität)",
     "Schichtungsgradient zwischen DALR und SALR → stabil trocken, labil feucht"),
    ("table_row", "Absolute Labilität",
     "Schichtungsgradient > DALR → instabil für jede Aufstiegsart"),
    ("text",
     "Labilität kann entstehen, wenn sich eine Luftmasse von unten erwärmt und/oder in der Höhe "
     "abkühlt. In beiden Fällen nimmt der Schichtungsgradient dann eine etwas 'flachere' Lage ein, "
     "wodurch ein Aufstieg von Luftpaketen (Thermik) begünstigt wird. Bei anhaltender "
     "Labilisierung können sich die Quellungen überentwickeln und bis zur Tropopause durchsteigen. "
     "Die Folge sind hochreichende Schauer und Gewitter, die mit sehr großtropfigem und kräftigem "
     "Schauerniederschlag verbunden sind.", ""),

    # ── 1.4 Höhenmessung ────────────────────────────────────────────────
    ("heading", "1.4  Höhenmessung", ""),
    ("text",
     "Der Höhenmesser gehört zu den wichtigsten Instrumenten an Bord eines Luftfahrzeuges. Auch bei "
     "modernen Luftfahrzeugen mit elektronischen Flugunterstützungssystemen wird noch das Prinzip der "
     "Luftdruckmessung zur Höhenbestimmung eingesetzt. Prinzipiell handelt es sich beim Höhenmesser "
     "um ein Barometer, lediglich die Anzeigeskala und -mechanik sind entsprechend den Eigenschaften "
     "der ICAO-Standardatmosphäre für eine Höhenanzeige geeicht.", ""),
    ("diagram", SVG_HOEHENMESSUNG, "Abb. 16/17/18/19 – Verschiedene Bezugshöhen und Höhenmessereinstellungen"),

    ("subheading", "1.4.1  Höhenangaben", ""),
    ("text",
     "Ein barometrischer Höhenmesser zeigt nicht eine tatsächliche oder absolute, sondern eine "
     "relative Höhe im Verhältnis zu einer in der Nebenskala eingestellten Druckfläche an. Die "
     "wichtigsten Höhenmessereinstellungen sind Height (QFE), Altitude (QNH) und Flight Level (QNE).", ""),
    ("table_row", "Height (QFE)", "Luftdruck am Flugplatz als Bezug · am Boden zeigt der Höhenmesser 0"),
    ("table_row", "Altitude (QNH)", "Auf MSL reduzierter Luftdruck · Höhenmesser zeigt Höhe über MSL"),
    ("table_row", "Flight Level / QNE", "Standard 1013,25 hPa · Flugfläche (FL) · in Reiseflughöhe"),
    ("table_row", "QFF", "Tatsächlicher auf MSL reduzierter Druck (reale Atmosphäre, nicht ISA) · nur in Bodenwetterkarten"),
    ("text",
     "Das QFF dagegen berücksichtigt die tatsächlichen Verhältnisse der tatsächlichen Atmosphäre. "
     "Hierdurch weicht das QFF in fast allen Fällen vom QNH ab. In der Praxis findet in der "
     "Fliegerei ausschließlich das QNH Verwendung, da auf diesem Rechenschema auch die "
     "Höhenmesseranzeige beruht. Das QFF wird lediglich in Bodenwetterkarten verwendet.", ""),
    ("fact",
     "Das QFE ist der mit den tatsächlichen Atmosphärenverhältnissen auf Meereshöhe rechnerisch "
     "reduzierte Luftdruck. Das QNH ist der mit den Werten der ICAO-Standardatmosphäre auf "
     "Meereshöhe rechnerisch reduzierte Luftdruck.", ""),
    ("text",
     "Flugfläche (FL) / QNE: Höhenmessereinstellungen, die eine Höhe über dem Platz oder die Höhe "
     "über MSL anzeigen, sind geeignet für bodennahes Fliegen, wo es primär auf Hindernisfreiheit "
     "ankommt. In größerer Höhe, wo Hindernisfreiheit als gegeben angenommen werden kann, kommt es "
     "insbesondere auf den vertikalen Abstand zwischen Luftfahrzeugen an, damit Radarlotsen eine "
     "entsprechende Staffelung vornehmen können. Die Standardeinstellung ermöglicht die Staffelung "
     "von Luftfahrzeugen über lange Strecken. Sinkt ein Luftfahrzeug von seiner Flugfläche ausgehend "
     "in den Landeanflug, muss die Höhenmessereinstellung wieder auf QNH umgestellt werden, um in "
     "Bodennähe Hindernisfreiheit zu gewährleisten.", ""),
    ("text",
     "Übergangshöhe und Übergangsfläche: Hierzu wird in der ATIS (Automatic Terminal Information "
     "Service) eine Übergangsfläche genannt. Zwischen Übergangshöhe und Übergangsfläche müssen "
     "mindestens 1.000 ft liegen, damit auch die nach QNH fliegenden Luftfahrzeuge von den nach "
     "Standardeinstellung fliegenden Luftfahrzeugen wenigstens 1.000 ft vertikalen Abstand haben. "
     "Als sichere Höhe für hindernisfreie Flüge gelten in Deutschland 5.000 ft MSL oder 2.000 ft "
     "AGL, wobei der höhere Wert ausschlaggebend ist.", ""),

    ("subheading", "1.4.2  Höhenberechnungen", ""),
    ("text",
     "In den Sichtflug-Navigationskarten sind Bodenhebungen und Hindernishöhen als Höhen über MSL "
     "(Altitudes) angegeben. Während des Fluges kann so problemlos die Hindernisfreiheit eingeschätzt "
     "werden. Aufgrund von Abweichungen der tatsächlichen Atmosphäre von der ICAO-Standardatmosphäre "
     "entspricht die angezeigte Höhe jedoch auch bei QNH-Einstellung meist nicht der wahren Höhe über "
     "MSL. Deshalb müssen in der Flugvorbereitung rechnerische Korrekturen vorgenommen werden.", ""),
    ("table_row", "Druckkorrektur", "30 ft pro hPa (Δh = ΔhPa × 30 ft) · QNE-Einstellung zeigt Druckhöhe"),
    ("table_row", "Temperaturkorrektur",
     "Δh = 0,4% pro 1°C ΔISA · 'Von Warm nach Kalt, das knallt!'"),
    ("table_row", "Dichtehöhe", "Δh = 120 ft pro 1°C ΔISA (für Flugleistungsberechnungen, keine reelle Höhe)"),
    ("fact",
     "Bei QNH > 1013 hPa: wahre Höhe GRÖSSER als angezeigte Höhe. "
     "Bei QNH < 1013 hPa: wahre Höhe KLEINER als angezeigte Höhe. "
     "'Von Warm nach Kalt, das knallt!': In kalter Luft fliegt man tiefer als der Höhenmesser zeigt. "
     "Druckkorrektur zuerst, dann Temperaturkorrektur.", ""),
    ("text",
     "Dichtehöhe: Die Dichtehöhe spielt bei der Flugvorbereitung eine bedeutende Rolle und gibt "
     "zuverlässig Hinweise auf die zu erwartenden Flugleistungen. Hierfür spielen insbesondere der "
     "Druck und die Temperatur eine Rolle, da hierdurch die Luftdichte beeinflusst wird. Viele "
     "Leistungswerte (z.B. Steigrate, Auftrieb, Propellervortrieb beim Flugzeug) hängen wiederum "
     "von der Luftdichte ab. So bewirken hoher Druck und kalte Luft eine Verbesserung der "
     "Leistungswerte und eine Verkürzung von Start- und Landestrecke, niedriger Druck und warme "
     "Luft hingegen verschlechtern die Flugleistungen.", ""),
    ("fact",
     "Hohe Dichtehöhe (hoher DA) = schlechte Flugleistungen = längere Startstrecke. "
     "Niedrige Dichtehöhe (niedriger DA) = bessere Flugleistungen.", ""),
]

KAPITEL1_QUIZ = [
    ("Was ist die durchschnittliche Temperaturabnahme mit der Höhe gemäß ISA?",
     ["0,5°C pro 100 m","0,65°C pro 100 m","1,0°C pro 100 m","2°C pro 100 m"], 1,
     "Die ICAO-Standardatmosphäre (ISA) definiert eine Temperaturabnahme von 0,65°C pro 100 m "
     "(= 2°C pro 1.000 ft) in der Troposphäre.", 1),
    ("Wie hoch ist die mittlere Tropopausenhöhe nach ISA?",
     ["5,5 km","8 km","11 km","16 km"], 2,
     "Die mittlere Tropopausenhöhe beträgt 11 km (36.000 ft) nach ISA. Am Äquator liegt sie bei "
     "16–18 km, an den Polen bei 6–8 km.", 1),
    ("Welchen Druck hat die Standardatmosphäre auf Meereshöhe?",
     ["1.000 hPa","1.013,25 hPa","1.020 hPa","998 hPa"], 1,
     "Der Standardluftdruck auf Meereshöhe (ISA) beträgt 1013,25 hPa = 760 mmHg = 29,92 inHg.", 1),
    ("Was ist der trockenadiabatische Temperaturgradient (DALR)?",
     ["0,65°C / 100 m","0,6°C / 100 m","1°C / 100 m","2°C / 100 m"], 2,
     "Der DALR (Dry Adiabatic Lapse Rate) beträgt exakt 1°C pro 100 m. Er gilt solange kein "
     "Kondensation stattfindet.", 1),
    ("Was bedeutet die Höhenmessereinstellung QNH?",
     ["Luftdruck am Flugplatz – Bodenanzeige = 0","Auf MSL reduzierter Luftdruck (Altitude)","Standard 1013,25 hPa für Flugflächen","Tatsächlicher MSL-Druck der realen Atmosphäre"], 1,
     "QNH ist der auf Meereshöhe (MSL) rechnerisch reduzierte Luftdruck nach ISA. Der Höhenmesser "
     "zeigt die Altitude (Höhe über MSL).", 1),
    ("Was ist die Tropopause?",
     ["Die unterste Schicht der Atmosphäre","Die Grenzschicht zwischen Troposphäre und Stratosphäre","Die Ozonschicht","Die Obergrenze der Stratosphäre"], 1,
     "Die Tropopause ist die Grenzschicht zwischen Troposphäre und Stratosphäre. "
     "Hier endet der Wetterbereich bei ca. −56,5°C.", 1),
    ("Wie viel Sauerstoff enthält trockene Luft?",
     ["78%","21%","1%","50%"], 1,
     "Trockene Luft enthält ca. 78% Stickstoff (N₂), 21% Sauerstoff (O₂) und ca. 1% CO₂ + "
     "Edelgase.", 1),
    ("Was ist der 'Spread' in der Meteorologie?",
     ["Luftfeuchtigkeit in %","Differenz zwischen Temperatur und Taupunkt (T − Tp)","Schichtungsgradient","Windscherung"], 1,
     "Spread = Temperatur − Taupunkt (T − Tp) in °C. Kleiner Spread weist auf Nebelbildung oder "
     "eine niedrige Wolkenuntergrenze hin.", 1),
    ("Welche Höhe hat die Wolkenuntergrenze bei einem Spread von 4°C?",
     ["400 ft","1.600 ft","800 ft","4.000 ft"], 1,
     "KKN [ft] = Spread × 400 = 4 × 400 = 1.600 ft. (Alternativ: KKN [m] = 4 × 123 = 492 m)", 1),
    ("Was bedeutet eine Inversion in der Atmosphäre?",
     ["Temperatur nimmt mit Höhe ab (normal)","Temperatur bleibt konstant (Isothermie)","Temperatur nimmt mit der Höhe zu","Kein Temperaturverlauf vorhanden"], 2,
     "Eine Inversion ist ein Bereich, in dem die Temperatur mit zunehmender Höhe zunimmt (statt "
     "abzunehmen). Sie ist sehr stabil und verhindert Konvektion.", 0),
    ("Was zeigt der Höhenmesser bei QFE-Einstellung?",
     ["Höhe über MSL (Altitude)","Höhe über dem Flugplatz (Height) – am Boden = 0","Flight Level","Geographische Höhe (Elevation)"], 1,
     "Bei QFE-Einstellung zeigt der Höhenmesser die Height (Höhe über dem Flugplatz). "
     "Am Boden zeigt er 0.", 1),
    ("Bei einem QNH von 993 hPa: Wie verhält sich die wahre Höhe zur angezeigten?",
     ["Wahre Höhe ist größer","Wahre Höhe ist gleich","Wahre Höhe ist kleiner","Kein Unterschied wenn Temperatur stimmt"], 2,
     "Bei QNH < 1013 hPa ist die wahre Höhe (True Altitude) kleiner als die angezeigte. "
     "Merksatz: Von Warm nach Kalt, das knallt! (gilt auch für Niederdruck).", 1),
    ("Was ist die barometrische Höhenstufe auf Meereshöhe?",
     ["54 ft/hPa","27 ft/hPa","108 ft/hPa","30 ft/hPa"], 1,
     "Die barometrische Höhenstufe auf MSL beträgt 27 ft/hPa (8 m/hPa) nach ISA. "
     "In 18.000 ft beträgt sie 54 ft/hPa.", 1),
    ("Welche ISA-Temperatur herrscht auf Meereshöhe (MSL)?",
     ["0°C","+10°C","+15°C","+20°C"], 2,
     "ISA definiert am MSL folgende Standardwerte: 1013,25 hPa · +15°C · 1,225 kg/m³.", 1),
    ("Wie hoch ist die Übergangshöhe (Transition Altitude) in Deutschland?",
     ["2.000 ft MSL","3.500 ft MSL","5.000 ft MSL oder 2.000 ft AGL (der höhere Wert)","10.000 ft MSL"], 2,
     "In Deutschland ist die Übergangshöhe 5.000 ft MSL oder 2.000 ft AGL (der höhere Wert gilt). "
     "Zwischen Übergangshöhe und Übergangsfläche muss mindestens 1.000 ft Abstand sein.", 1),
]

KAPITEL1_FLASHCARDS = [
    ("DALR?", "1°C / 100 m (trockenadiabatisch, ohne Kondensation)"),
    ("SALR?", "≈ 0,6°C / 100 m (feuchtadiabatisch, Mittelwert)"),
    ("ISA Temperaturgradient?", "0,65°C / 100 m = 2°C / 1.000 ft"),
    ("KKN-Formel?", "KKN [ft] = Spread × 400 · KKN [m] = Spread × 123"),
    ("ISA MSL-Werte?", "1013,25 hPa · +15°C · 1,225 kg/m³"),
    ("QFE zeigt?", "Height über Flugplatz – am Boden = 0"),
    ("QNH zeigt?", "Altitude über MSL"),
    ("QNE zeigt?", "Flight Level – Standardeinstellung 1013,25 hPa"),
    ("Halbierungshöhe Luftdruck?", "alle ca. 5.500 m / 18.000 ft"),
    ("Spread = ?", "Temperatur − Taupunkt (°C)"),
    ("ΔISA?", "Abweichung der tatsächlichen Temperatur von ISA (positiv = wärmer als ISA)"),
    ("Dichtehöhe-Korrektur?", "Δh = 120 ft pro 1°C ΔISA"),
]

# ═══════════════════════════════════════════════════════════════════════════
# Kapitel 2 – Wolken und Niederschläge (Seiten 45–65)
# Basiert auf PDF 141-175.pdf
# ═══════════════════════════════════════════════════════════════════════════
KAPITEL2_ID = "meteorologie-kapitel-2-wolken-und-niederschlage-bildung-arten"

KAPITEL2_SECTIONS = [
    ("heading", "2  Wolken und Niederschläge", ""),
    ("text",
     "Wenn im Allgemeinen über das 'Wetter' gesprochen wird, ist meist die Bewölkung gemeint. "
     "'Schönes Wetter' wird mit wolkenlosem Himmel in Verbindung gebracht, bei 'schlechtem Wetter' "
     "denken wir an graue, geschlossene Bewölkung und Regen. Tatsächlich enthalten auch "
     "Flugwettermeldungen zum großen Teil Angaben zur Bewölkung, weil hiervon Gefahren ausgehen "
     "können. Um diese einschätzen zu können, müssen zunächst die physikalischen Vorgänge verstanden "
     "werden, die zur Bildung der unterschiedlichen Formen von Bewölkung, Nebel und Niederschlag "
     "führen.", ""),

    # ── 2.1 Wolkenbildung ────────────────────────────────────────────────
    ("subheading", "2.1  Wolkenbildung", ""),
    ("text",
     "Wolken entstehen fast ausnahmslos durch den Aufstieg und die damit verbundene Abkühlung der "
     "Luft. Beim Abkühlen wird in einer bestimmten Höhe der Taupunkt erreicht und durch die "
     "einsetzende Kondensation oder Sublimation bilden sich an mikroskopisch kleinen "
     "Kondensationskeimen Wolkentröpfchen. Neben dem Vorhandensein von Wasserdampf sind die "
     "Vertikalbewegungen in der Luft zunächst die Hauptursache für die Wolkenentstehung.", ""),
    ("text",
     "Wolken sind in der Atmosphäre schwebende 'Hydrometeore', die aus winzigen Wassertröpfchen oder "
     "Eiskristallen bestehen oder aus einer Mischung aus beiden. Das Größenspektrum der Wassertröpfchen "
     "variiert in einem großen Bereich; typische Wolkentröpfchen haben einen Durchmesser von einem "
     "Hundertstel Millimeter. Dadurch ist die Sinkgeschwindigkeit dieser Teilchen sehr gering, was sie "
     "vom Niederschlag unterscheidet. In einem Liter Wolkenluft findet man bis zu einer halben Million "
     "Wassertröpfchen dieser Art. Als Sonderform einer Wolke gilt Nebel als am Boden aufliegende "
     "Bewölkung.", ""),

    ("subheading", "2.1.1  Allgemeines zur Wolkenbildung", ""),
    ("text",
     "Zur Ausbildung von Wolkentröpfchen werden Kondensationskeime benötigt, an welchen sich "
     "Wasserteilchen bevorzugt zu größeren Tropfen anlagern können, die anschließend als Niederschlag "
     "aus der Wolke herausfallen. Sind nun Temperatur und Taupunkt – also der Spread – eines "
     "Luftpakets am Boden bekannt, kann abgeschätzt werden, in welcher Höhe 100% Luftfeuchtigkeit "
     "erreicht wird und somit die Wolkenbildung ausgelöst wird. Diese Höhe wird als KKN "
     "(Kumulus-Kondensations-Niveau) bezeichnet.", ""),
    ("fact",
     "KKN [ft] = Spread × 400 · KKN [m] = Spread × 123. "
     "Bei einem Spread von 5°C ergibt sich eine Wolkenuntergrenze von 5 × 400 = 2.000 ft.", ""),

    ("subheading", "2.1.2  Thermische Entstehung", ""),
    ("text",
     "Die thermische Entstehung von Wolken kann an fast jedem schönen Sonnentag beobachtet werden, "
     "wenn sich der morgens noch klare, blaue Himmel gegen Mittag mit weißen Wolken füllt. Im "
     "Tagesverlauf ist in der Folge oft ein Wechsel zwischen Wolken und Sonne zu beobachten, bis "
     "sich die Wolken gegen Abend wieder auflösen und eine sternenklare Nacht folgt. Ursache für die "
     "thermische Entstehung von Wolken ist die Sonneneinstrahlung, die den Erdboden erwärmt – "
     "allerdings nicht gleichmäßig, sondern je nach Beschaffenheit unterschiedlich schnell. So bleibt "
     "es über feuchten Wiesen länger kühl als über trockenen Sandflächen. Es bilden sich örtlich "
     "bodennahe 'Warmluftblasen', in denen die Luft wärmer ist als in der Umgebung.", ""),
    ("text",
     "Solche Warmluftpakete haben eine geringere Dichte als das, was mit einer Abkühlung verbunden "
     "ist, und steigen deshalb auf, kühlen sich dabei zunächst trockenadiabatisch mit einer "
     "Temperaturabnahme von 1°C / 100 m ab. Mit dem Luftpaket wird auch die darin enthaltene "
     "Feuchtigkeit mit in die Höhe transportiert. Die absolute Feuchtigkeit, also die Gesamtmenge "
     "des in dem Luftpaket enthaltenen Wassers, bleibt dabei konstant. Eine konstante "
     "Feuchtigkeitsmenge und abnehmende Temperatur bedeuten eine Zunahme der relativen Feuchtigkeit. "
     "Diese wächst auf 100%, wenn sich das Luftpaket auf seinen Taupunkt abgekühlt hat. Der Taupunkt "
     "nimmt zwar auch beim Aufstieg ab, allerdings viel langsamer als die Temperatur. Dadurch gibt "
     "es zwangsläufig eine bestimmte Höhe, in welcher Temperatur und Taupunkt gleich sind und bei "
     "weiterem Aufstieg Kondensation eintreten muss.", ""),
    ("text",
     "Eine Wetterlage mit einer ausgeprägten und kräftigen Inversion begünstigt morgens Dunstbildung "
     "in Bodennähe, weil sich dort die Luft über Nacht am stärksten abgekühlt hat und der Spread "
     "klein geworden ist. Im Laufe des Tages setzt Thermik ein und es bilden sich einige flache "
     "Quellwolken, deren Obergrenzen durch die Inversion bestimmt werden, da die aufsteigende Luft "
     "dort nicht mehr wärmer als die umgebende Luft ist und weiteres Steigen unterbunden wird.", ""),

    ("subheading", "2.1.3  Entstehung an Luftmassengrenzen", ""),
    ("text",
     "Wenn unterschiedliche Luftmassen aufeinandertreffen, kann Luft zum Aufstieg gezwungen werden. "
     "Stößt beispielsweise eine Kaltluftmasse gegen eine wärmere Luftmasse vor, so schiebt sie sich "
     "keilförmig unter die wärmere Luft, da die kalte Luft eine größere Dichte hat. Die wärmere "
     "Luft wird dadurch zum Aufstieg gezwungen und bildet entlang der Luftmassengrenze einen "
     "ausgedehnten Bereich starker, konvektiver Bewölkung mit zum Teil kräftigen Niederschlägen. "
     "Wenn sich Warmluft in Richtung der kälteren Luft bewegt, gleitet die wärmere Luft auf die "
     "kalte Luft auf. Hierbei steigt sie langsam, aber stetig auf und bildet dabei hoch reichende, "
     "stabil geschichtete Bewölkung, aus der auch Niederschläge fallen können.", ""),
    ("fact",
     "Bewölkung an Luftmassengrenzen ist meist hoch reichend und stark ausgeprägt. "
     "Während bei normaler Thermik nicht vereinzelte Quellwolken oft ohne Niederschläge entstehen, "
     "sind die mit Luftmassengrenzen verbundenen Wolken in den meisten Fällen geschlossene Linien "
     "von mehreren hundert oder tausend Kilometern Ausdehnung und stets mit teils kräftigen "
     "Niederschlägen verbunden.", ""),

    ("subheading", "2.1.4  Orographische Entstehung", ""),
    ("text",
     "Ursache für orographisch bedingte Wolkenbildung ist die Hebung von Höhenstrukturen auf der "
     "Erdoberfläche. Auslöser können dabei einzelne Berge oder auch ganze Gebirgsketten sein, an "
     "denen bei entsprechender Windrichtung die Luft über hunderte Kilometer zum Aufstieg gezwungen "
     "wird. Im Gegensatz zu ihrer thermischen Entstehung ist die Luftschichtung bei dieser "
     "Wetterlage meist stabil.", ""),
    ("text",
     "Wenn Luft über ein Gebirge strömt, bilden sich auf der dem Wind zugewandten Seite dicke "
     "Schichtwolken mit Niederschlägen. Es scheint, die Wolken würden sich am Gebirge 'stauen', "
     "eine Staubewölkung entsteht. Hinter dem Gebirge, auf dem dem Wind abgewandten Seite (im Lee) "
     "kann die Luft wieder absinken und sich erwärmen. Durch die Erwärmung wird dort vorhandene "
     "Bewölkung aufgelöst und die Luft strömt als warmer Fallwind – Föhn genannt – in die "
     "Niederungen. Das Besondere am Föhn ist, dass die Luft hinter dem Gebirge wärmer ankommt, "
     "als sie vor dem Gebirge in gleicher Höhe war. Dies wird dadurch verursacht, dass sich die Luft "
     "im Stau eben durch die Wolkenbildung feuchtadiabatisch abgekühlt hat, auf der Leeseite aber "
     "trockenadiabatisch gesunken ist.", ""),
    ("fact",
     "Föhn: Luft auf Leeseite wärmer als auf Luvseite in gleicher Höhe, weil: "
     "Luvseite = feuchtadiabatische Abkühlung (0,6°C/100m) + Kondensation. "
     "Leeseite = trockenadiabatische Erwärmung (1°C/100m). "
     "Energiequelle = freiwerdende Kondensationswärme beim Aufstieg.", ""),
    ("text",
     "Dennoch ist auch ein Flug auf der Leeseite nicht ungefährlich. Die Luft strömt mit hohen "
     "Geschwindigkeiten über das Gebirge, wobei auf der windabgewandten Seite Verwirbelungen sehr "
     "wahrscheinlich sind. Es bilden sich so genannte Rotoren, die mit gefährlicher Turbulenz und "
     "ggf. Vereisung verbunden sein können. Optisch sind Leewellen an einer linsenförmigen Art von "
     "Wolken zu erkennen, die sich in den 'Wellenbergen' den so genannten Lentis (Altocumulus "
     "lenticularis) bilden. Sie sind Hinweise auf die Wellenbewegung und warnen gleichzeitig vor den "
     "Rotoren auf der Leeseite des Gebirges.", ""),

    ("subheading", "2.1.5  Turbulente Durchmischung", ""),
    ("text",
     "In Bodennähe entsteht infolge des Reibungseffekts stets eine turbulente Durchmischung, "
     "besonders bei höheren Windgeschwindigkeiten. Bei Vorhandensein einer niedrig gelegenen "
     "Inversion mit genügend Feuchtigkeit steigen und sinken die Luftteilchen infolge Turbulenz und "
     "es kommt zur Wolkenbildung. Diese Art der Bewölkung heißt daher Turbulenz-Stratus.", ""),

    # ── 2.2 Klassifizierung von Wolken ──────────────────────────────────
    ("heading", "2.2  Klassifizierung von Wolken", ""),
    ("text",
     "Es besteht eine Vielzahl von möglichen Kriterien, eine Klassifizierung von Wolken vorzunehmen. "
     "Ein Blick in den Himmel macht jedoch recht schnell deutlich, dass jede Wolke eine gewisse "
     "Einzigartigkeit besitzt und nicht immer eindeutig einer Kategorie zugeordnet werden kann. "
     "Dennoch bestehen Ähnlichkeiten zwischen Wolken, welche beispielsweise mit Eigenschaften "
     "hinsichtlich Vereisung, Turbulenz und Niederschlag verbunden sind. In der Flugmeteorologie "
     "wird eine Vielzahl von Wolken in Wettermeldungen benannt.", ""),

    ("subheading", "2.2.1  Einteilung nach Entstehung", ""),
    ("text",
     "Bei Wolken wird nach der Art ihrer Entstehung grundsätzlich zwischen Quellwolken und "
     "Schichtwolken unterschieden. Quellwolken entstehen meist durch Konvektion bei labilen "
     "Wetterlagen. Sie haben meist eine einheitliche Untergrenze, die Obergrenze besteht aus einer "
     "uneinheitlichen Wölbung. Schichtwolken entstehen durch gleichmäßige Hebung oder Abkühlung "
     "einer insgesamt stabilen Luftmasse. Optisch sind sie meist nur als ausgedehnte Schicht ohne "
     "innere Struktur zu erfassen.", ""),
    ("table_row", "Quellwolken (Cumulus / Cumulo)",
     "Konvektion, labile Wetterlage · einheitliche Untergrenze · Schauer, Turbulenz, Vereisung"),
    ("table_row", "Schichtwolken (Stratus / Strato)",
     "Hebung stabiler Luftmasse · ausgedehnte Schicht · Sprühregen, Sichtbehinderung"),

    ("subheading", "2.2.2  Entstehung nach Stockwerken", ""),
    ("text",
     "Je nach Höhe und vertikaler Ausdehnung besitzen Wolken unterschiedliche Anteile von Wasser und "
     "Eis. Es werden daher drei Stockwerke unterschieden. Im unteren Stockwerk besteht eine Wolke fast "
     "ausschließlich aus Wasser. Das mittlere Stockwerk enthält Mischwolken aus Wasser und Eis. Im "
     "oberen Stockwerk bestehen die Wolken bei Temperaturen unter -30°C fast ausschließlich aus Eis.", ""),
    ("diagram", SVG_WOLKEN, "Abb. 42 – Klassifizierung von Wolken"),
    ("table_row", "Stockwerk", "km / ft / Temperatur / Wolkenart"),
    ("table_row", "Oberes Stockwerk",
     "6–13 km · 18.000–39.000 ft · < −20°C · Reine Eiswolken"),
    ("table_row", "Mittleres Stockwerk",
     "2–7 km · 6.500–23.000 ft · bis −30°C · Mischwolken"),
    ("table_row", "Unteres Stockwerk",
     "0–2 km · 0–6.500 ft · > −10°C · Wasserwolken ggf. unterkühlte Tropfen"),
    ("text",
     "Insgesamt ergeben sich zehn grundlegende Wolkenklassifizierungen, die man am Vorsilbe und den "
     "Wortstamm eindeutig identifizieren lassen.", ""),
    ("table_row", "Cirrus (Ci)",  "> 18.000 ft · Eiswolken · fadenartig · Warmfront-Vorläufer"),
    ("table_row", "Cirrocumulus (Cc)", "> 18.000 ft · Eiswolken · kleine Schäfchen"),
    ("table_row", "Cirrostratus (Cs)", "> 18.000 ft · Eiswolken · dünner Schleier, Halo-Effekt"),
    ("table_row", "Altocumulus (Ac)",  "6.500–23.000 ft · Mischwolken · Ac Lenticularis bei Leewellen/Föhn"),
    ("table_row", "Altostratus (As)",  "6.500–23.000 ft · Mischwolken · grau-blau · Dauerregen"),
    ("table_row", "Cumulus (Cu)",     "< 6.500 ft · Wasserwolken · Quellwolke · Thermik, Schauer, Turbulenz"),
    ("table_row", "Stratocumulus (Sc)", "< 6.500 ft · Rollenwolke · häufigste Wolke in Mitteleuropa"),
    ("table_row", "Stratus (St)",     "< 6.500 ft · Schicht · Bodennebel, Sprühregen"),
    ("table_row", "Nimbostratus (Ns)", "Mehrere Stockwerke · Regenwolke · anhaltender Dauerregen"),
    ("table_row", "Cumulonimbus (Cb)", "Mehrere Stockwerke · bis Tropopause · Gewitterwolke · GEFÄHRLICHSTE Wolke!"),
    ("fact",
     "Cumulonimbus (Cb) – Gefahren für Piloten: "
     "Extreme Turbulenz und Böen (Strukturgefahr) · Hagel · Starke Vereisung · "
     "Blitzschlag · Starke Auf- und Abwinde · Mikrobursts · Windscherung · "
     "Niemals in einen Cb fliegen! Mindestabstand: 5 NM seitlich.", ""),
    ("warning",
     "NIEMALS in einen Cumulonimbus (Cb) fliegen! "
     "Mindestabstand: 5 NM seitlich, 2.000 ft über der Wolkenobergrenze. "
     "Embedded Cb (eingebettete Gewitter in Schichtwolken) sind besonders gefährlich, "
     "da sie von außen nicht sichtbar sind!", ""),

    ("subheading", "2.2.3  Sichtflugbedingungen in Wolkennähe", ""),
    ("text",
     "Aufgrund der zunehmenden Feuchtigkeit durch den abnehmenden Spread nahe der "
     "Wolkenuntergrenze muss unter Wolken mit einer Beeinträchtigung der Sichtverhältnisse "
     "gerechnet werden. Niederschläge reduzieren die Sicht dabei deutlich. So können direkt unter "
     "Quellwolken die Sichten weniger als 1.500 m, unter Schichtwolken in Sprühregen weniger als "
     "1.000 m betragen. Bei niedrigen Temperaturen kann die zunehmende Feuchtigkeit zu Vereisung "
     "führen. Weiterhin besteht bei Quellwolken eine Gefahr durch die thermisch bedingte Turbulenz.", ""),
    ("text",
     "Die seitlichen, blumenkohlartigen Ränder einer Quellwolke sind oft scharf abgegrenzt; die "
     "wolkenfreie Luft befindet sich außerhalb der Aufwindzone mit kleiner werdendem Spread. In "
     "ausreichendem seitlichem Abstand neben Quellwolken ist daher keine Gefahr durch "
     "Sichtverschlechterung oder Vereisung zu erwarten.", ""),

    # ── 2.3 Niederschläge ───────────────────────────────────────────────
    ("heading", "2.3  Niederschläge", ""),
    ("text",
     "Wird der Taupunkt unterschritten, tritt Kondensation ein und es bilden sich feine "
     "Wassertröpfchen in Form von Nebel oder Wolken. Diese Tröpfchen sind allerdings so klein und "
     "leicht, dass sie zunächst weiterhin in der Luft schweben. Zur Ausbildung von großen "
     "Niederschlagsteilchen, die in ganz unterschiedlicher Form vorkommen können, sind zum Teil "
     "recht komplexe Vorgänge erforderlich. Als Niederschlag bezeichnet man jedes aus einer Wolke "
     "herausfallende Kondensations- oder Sublimationsprodukt.", ""),

    ("subheading", "2.3.1  Allgemeines", ""),
    ("text",
     "In mittleren Breiten entsteht nennenswerter Niederschlag grundsätzlich aus Mischwolken, also "
     "solchen Wolken, die sowohl unterkühlte Wassertröpfchen als auch Eiskristalle enthalten. Das "
     "bedeutet, dass die Wolke an der Obergrenze kälter als -25°C sein sollte, da nur dann "
     "ausreichend Eiskristalle vorhanden sind. Die Niederschlagsbildung verläuft also über die "
     "'Eisphase', sodass man demzufolge Regen als geschmolzenen Schnee interpretieren muss. "
     "Besonders im Sommer haben Regenwolken somit eine große vertikale Ausdehnung.", ""),
    ("text",
     "Begrifflich werden zwei Arten von Niederschlägen unterschieden: Solche, die aus konvektiven "
     "Wolken (Cu / Cb) fallen, nennt man Schauer; aus stratiformem Wolken treten eher "
     "Flächenniederschläge auf. Diese unterscheiden sich sowohl in der räumlichen und zeitlichen "
     "Ausdehnung als auch in den sich bildenden Niederschlagsteilchen und den mit ihnen verbundenen "
     "Gefahren. Außerdem könnte man noch flüssige Niederschläge (Regen, Sprühregen) von festen "
     "Niederschlägen (Schnee, Hagel) unterscheiden sowie fallende Niederschläge (alles, was von oben "
     "kommt) und am Boden abgesetzte Niederschläge (Tau und Reif).", ""),

    ("subheading", "2.3.2  Schauer", ""),
    ("text",
     "Regenschauer sind meist kräftige, aber nicht lange andauernde Niederschläge. Die Regentropfen "
     "benötigen einen gewissen Durchmesser, um als 'kräftig' empfunden zu werden, sie müssen also "
     "in der Wolke Voraussetzungen finden, welche die Bildung von relativ großen Tropfen unterstützen. "
     "Diese Voraussetzungen finden sich in cumulusartigen Wolken, weil die vertikale Erstreckung so "
     "groß sein kann, dass an der Wolkenobergrenze Eiskristalle zu finden sind. Aus Cu-Wolken fallen "
     "immer Schauer!", ""),
    ("fact",
     "Aus Cu-Wolken (Cumuluswolken) fallen IMMER Schauer! "
     "Schauer = kräftig, kurzanhaltend, große Tropfen. "
     "Flächenniederschlag = gleichmäßig, lang andauernd, aus Ns/As.", ""),

    ("subheading", "2.3.3  Flächenniederschläge", ""),
    ("text",
     "Aus stratiformem Wolken treten eher Flächenniederschläge auf, also gleichmäßige, "
     "langanhaltende Niederschläge. Diese Vorgänge entstehen an ausgedehnten Fronten "
     "(Warm- oder Kaltfronten) und können über große Flächen und lange Zeiträume anhalten.", ""),

    ("subheading", "2.3.4  Hagel und Graupel", ""),
    ("text",
     "Im Cumulonimbus können durch die starken Auf- und Abwinde Eisteilchen mehrfach zwischen dem "
     "unterkühlten Bereich und der Eiszone hin und her transportiert werden, wobei sie immer mehr "
     "Eis anlagern und so zu Hagelkörnern wachsen. Hagel tritt immer in Schauerform auf.", ""),
    ("table_row", "Hagel", "Nur aus Cb · Eiskörner ≥ 5 mm · durch Auf-/Abwinde im Cb geformt"),
    ("table_row", "Graupel", "Schneekörner mit Eismantel · aus Cb/Cu bei Mischphasenwetterlagen"),

    ("subheading", "2.3.5  Gefrierender Regen", ""),
    ("text",
     "Besonders gefährlich für den Flugbetrieb ist gefrierender Regen (FZRA): Unterkühlte "
     "Regentropfen (flüssig trotz T < 0°C) gefrieren beim Aufprall auf Flächen sofort. "
     "Dies kann zu raschem und schwerem Eisansatz am Luftfahrzeug führen.", ""),
    ("warning",
     "Gefrierender Regen (FZRA) ist eine der gefährlichsten Vereisungsarten! "
     "Unterkühlte Tropfen gefrieren sofort beim Aufprall → rapider Eisaufbau. "
     "Im METAR als FZRA gekennzeichnet.", ""),

    ("subheading", "2.3.6  Schnee", ""),
    ("text",
     "Schnee fällt, wenn die Temperaturen in den tiefen Luftschichten unter dem Gefrierpunkt liegen "
     "und die Eiskristalle nicht schmelzen, bevor sie den Boden erreichen.", ""),

    ("subheading", "2.3.7  Niederschläge am Boden", ""),
    ("text",
     "Tau und Reif entstehen durch Abkühlung von Oberflächen unter den Taupunkt. Bei Temperaturen "
     "über 0°C: Tau (flüssig). Bei Temperaturen unter 0°C: Reif (fest, durch Sublimation). "
     "Bereifung auf Flugzeugen ist vor dem Start immer zu entfernen!", ""),
    ("fact",
     "Alle Arten von Eis, Schnee oder Reif sind vor dem Start vollständig vom Luftfahrzeug zu "
     "entfernen! Auch dünne Reifschichten stören die Aerodynamik erheblich (raue Oberfläche "
     "= erhöhter Widerstand, verringerter Auftrieb).", ""),
]

KAPITEL2_QUIZ = [
    ("Aus welcher Wolkenart fallen immer Schauer?",
     ["Stratus","Altostratus","Cumuluswolken (Cu)","Cirrus"], 2,
     "Aus Cu-Wolken (Cumuluswolken) fallen IMMER Schauer! Regel laut Buch: "
     "'Aus Cu-Wolken fallen immer Schauer!'", 1),
    ("Was ist das KKN?",
     ["Maximale Flughöhe","Kumulus-Kondensations-Niveau – Wolkenuntergrenze","Kälte-Kompensations-Niveau","Kritisches Kondensationsniveau für Hagel"], 1,
     "KKN = Kumulus-Kondensations-Niveau: Die Höhe, in der ein aufsteigendes Luftpaket seinen "
     "Taupunkt erreicht und Kondensation einsetzt. KKN [ft] = Spread × 400.", 1),
    ("Welche Wolke ist die gefährlichste für Piloten?",
     ["Cirrus","Altostratus","Cumulonimbus (Cb)","Nimbostratus"], 2,
     "Der Cumulonimbus (Cb) ist die gefährlichste Wolke: extreme Turbulenz, Hagel, Blitz, "
     "starke Vereisung, extreme Auf-/Abwinde. Niemals in einen Cb fliegen! Min. 5 NM Abstand.", 1),
    ("Wie hoch ist das untere Wolkenstockwerk?",
     ["Bis 18.000 ft","Bis 23.000 ft","Bis 6.500 ft","Bis 10.000 ft"], 2,
     "Das untere Stockwerk reicht bis 6.500 ft (≈2 km). Wolken: Cumulus, Stratocumulus, Stratus. "
     "Temperaturen meist über -10°C → hauptsächlich Wasserwolken.", 1),
    ("Was kennzeichnet die Vorsilbe 'Nimbo' oder der Wortstamm 'Nimbus'?",
     ["Hohe Eiswolken","Schichtwolken mit Hebung","Hochreichende Wolken mit starken Niederschlägen","Linsenförmige Leewellenwolken"], 2,
     "Nimbo/Nimbus kennzeichnet hochreichende Wolken, die starke Vertikalbewegungen und "
     "Niederschläge erzeugen: Nimbostratus (Ns) und Cumulonimbus (Cb).", 1),
    ("Welche Wolkenart entsteht beim Föhn auf der Leeseite?",
     ["Cumulonimbus","Altocumulus Lenticularis (Ac Len)","Stratus","Cirrostratus"], 1,
     "Altocumulus Lenticularis (Ac Len, linsenförmig) entsteht an Leewellen über Gebirgen. "
     "Er warnt vor Wellenbewegungen und Rotor-Turbulenz auf der Leeseite.", 1),
    ("Was ist die Entstehungsursache von Turbulenz-Stratus?",
     ["Thermik bei labiler Schichtung","Turbulente Durchmischung in Bodennähe bei Inversion","Orographische Hebung","Konvektion an Luftmassengrenzen"], 1,
     "Turbulenz-Stratus entsteht durch turbulente Durchmischung in Bodennähe, "
     "besonders bei starkem Wind und Vorhandensein einer Inversion mit ausreichend Feuchtigkeit.", 1),
    ("Was ist gefrierender Regen (FZRA)?",
     ["Schnee der bei 0°C gefriert","Unterkühlte Regentropfen die beim Aufprall sofort gefrieren","Hagel kleiner als 5mm","Graupel"], 1,
     "Gefrierender Regen (FZRA) besteht aus unterkühlten Wassertropfen (T < 0°C, flüssig), "
     "die beim Aufprall auf Oberflächen sofort gefrieren. Besonders gefährlich durch raschen Eisaufbau.", 1),
    ("Was ist der Unterschied zwischen Schauer und Flächenniederschlag?",
     ["Schauer sind kälter","Schauer aus Cu/Cb (kräftig, kurz), Flächenniederschlag aus Ns/As (gleichmäßig, lang)","Kein Unterschied","Schauer fallen nur im Winter"], 1,
     "Schauer fallen aus konvektiven Wolken (Cu/Cb): kräftig, kurz, große Tropfen. "
     "Flächenniederschlag aus stratiformem Wolken (Ns/As): gleichmäßig, langanhaltend.", 1),
    ("In welchem Stockwerk befinden sich Cirruswolken?",
     ["Unteres Stockwerk < 6.500 ft","Mittleres Stockwerk 6.500–18.000 ft","Hohes Stockwerk > 18.000 ft","Mehrere Stockwerke"], 2,
     "Cirrus (Ci) gehört zum hohen Stockwerk (> 18.000 ft). Alle Ci-Wolken bestehen aus reinen "
     "Eiskristallen (Temp < -30°C). Ci ist oft Vorläufer einer Warmfront.", 1),
    ("Was muss vor dem Abflug immer vom Luftfahrzeug entfernt werden?",
     ["Nur Schnee, Reif ist unkritisch","Nur Klareis","Alle Arten von Eis, Schnee und Reif","Nur Ablagerungen auf den Tragflächen"], 2,
     "Alle Arten von Eis, Schnee oder Reif sind vor dem Start vollständig zu entfernen! "
     "Auch dünne Reifschichten erhöhen den Widerstand und verringern den Auftrieb erheblich.", 1),
]

KAPITEL2_FLASHCARDS = [
    ("Aus welchen Wolken fallen immer Schauer?", "Cu-Wolken (Cumuluswolken): Aus Cu fallen IMMER Schauer!"),
    ("Was ist das KKN?", "Kumulus-Kondensations-Niveau: KKN[ft] = Spread × 400 · KKN[m] = Spread × 123"),
    ("Cumulonimbus – 3 Hauptgefahren?", "1. Extreme Turbulenz · 2. Hagel · 3. Starke Vereisung (+ Blitz, Mikrobursts)"),
    ("Wolken oberes Stockwerk?", "Cirrus (Ci) · Cirrocumulus (Cc) · Cirrostratus (Cs) · > 18.000 ft · Eiswolken"),
    ("Wolken mittleres Stockwerk?", "Altocumulus (Ac) · Altostratus (As) · 6.500–18.000 ft · Mischwolken"),
    ("Wolken unteres Stockwerk?", "Cumulus (Cu) · Stratocumulus (Sc) · Stratus (St) · < 6.500 ft · Wasserwolken"),
    ("Was ist gefrierender Regen?", "FZRA: unterkühlte Tropfen (flüssig bei T<0°C) gefrieren beim Aufprall sofort → gefährlich!"),
    ("Föhn – warum ist Lee wärmer als Luv?", "Luvseite: feuchtadiabatisch (0,6°C/100m). Leeseite: trockenadiabatisch (1°C/100m). Kondensationswärme bleibt in der Luft."),
]

# ── Hauptprogramm ────────────────────────────────────────────────────────────

def fill_chapter(conn, chapter_id, sections, quiz, flashcards):
    c = conn.cursor()
    # Check chapter exists
    row = c.execute("SELECT id FROM learn_chapters WHERE id=?", (chapter_id,)).fetchone()
    if not row:
        print(f"  ❌ Kapitel nicht gefunden: {chapter_id}")
        return False

    # Clear old (empty) content for this chapter
    c.execute("DELETE FROM learn_sections WHERE chapter_id=?", (chapter_id,))
    c.execute("DELETE FROM learn_quiz WHERE chapter_id=?", (chapter_id,))
    c.execute("DELETE FROM learn_flashcards WHERE chapter_id=?", (chapter_id,))

    # Insert sections
    for i, s in enumerate(sections):
        c.execute(
            "INSERT INTO learn_sections (chapter_id,type,content,extra,sort_order) VALUES (?,?,?,?,?)",
            (chapter_id, s[0], s[1], s[2] if len(s) > 2 else '', i)
        )

    # Insert quiz
    for i, q in enumerate(quiz):
        question, options, answer, explanation = q[0], q[1], q[2], q[3]
        is_official = q[4] if len(q) > 4 else 0
        c.execute(
            "INSERT INTO learn_quiz (chapter_id,question,options,answer,explanation,is_official,sort_order) "
            "VALUES (?,?,?,?,?,?,?)",
            (chapter_id, question, json.dumps(options, ensure_ascii=False),
             answer, explanation, is_official, i)
        )

    # Insert flashcards
    for i, (front, back) in enumerate(flashcards):
        c.execute(
            "INSERT INTO learn_flashcards (chapter_id,front,back,sort_order) VALUES (?,?,?,?)",
            (chapter_id, front, back, i)
        )

    conn.commit()
    nsec = len(sections); nq = len(quiz); nfc = len(flashcards)
    ndiag = sum(1 for s in sections if s[0] == 'diagram')
    print(f"  ✓ {chapter_id[:60]}")
    print(f"    sections={nsec} (diagrams={ndiag}) · quiz={nq} · flashcards={nfc}")
    return True


def main():
    print(f"\n📖  Fülle neue Kapitel aus PDFs…\n    DB: {DB}\n")
    conn = sqlite3.connect(DB)
    conn.execute("PRAGMA journal_mode=WAL")

    # Check existing chapters untouched
    all_chs = conn.execute("SELECT id FROM learn_chapters ORDER BY subject_id,sort_order").fetchall()
    print(f"  Vorhandene Kapitel gesamt: {len(all_chs)}")
    for r in all_chs:
        n = conn.execute("SELECT COUNT(*) FROM learn_sections WHERE chapter_id=?", (r[0],)).fetchone()[0]
        status = "✓ belegt" if n > 0 else "○ leer (wird befüllt)"
        print(f"    {r[0][:55]:55} sec={n:3}  {status}")

    print()
    ok1 = fill_chapter(conn, KAPITEL1_ID, KAPITEL1_SECTIONS, KAPITEL1_QUIZ, KAPITEL1_FLASHCARDS)
    ok2 = fill_chapter(conn, KAPITEL2_ID, KAPITEL2_SECTIONS, KAPITEL2_QUIZ, KAPITEL2_FLASHCARDS)

    # FTS update
    try:
        conn.execute("DELETE FROM learn_fts")
        conn.execute("""
            INSERT INTO learn_fts (chapter_id, subject_id, chapter_title, subject_title, content)
            SELECT sec.chapter_id, c.subject_id, c.title, s.title, sec.content
            FROM learn_sections sec
            JOIN learn_chapters c ON c.id = sec.chapter_id
            JOIN learn_subjects  s ON s.id = c.subject_id
        """)
        conn.commit()
        print("\n  ✓ Volltextsuche (FTS) aktualisiert")
    except Exception as e:
        print(f"\n  ⚠ FTS (nicht kritisch): {e}")

    # Final summary
    print("\n" + "═"*60)
    print("ENDZUSTAND DER DATENBANK")
    print("═"*60)
    for r in conn.execute("SELECT id FROM learn_chapters ORDER BY subject_id,sort_order").fetchall():
        n  = conn.execute("SELECT COUNT(*) FROM learn_sections  WHERE chapter_id=?", (r[0],)).fetchone()[0]
        q  = conn.execute("SELECT COUNT(*) FROM learn_quiz      WHERE chapter_id=?", (r[0],)).fetchone()[0]
        fc = conn.execute("SELECT COUNT(*) FROM learn_flashcards WHERE chapter_id=?", (r[0],)).fetchone()[0]
        d  = conn.execute("SELECT COUNT(*) FROM learn_sections  WHERE chapter_id=? AND type='diagram'", (r[0],)).fetchone()[0]
        print(f"  {r[0][:55]:55} sec={n:3} quiz={q:2} fc={fc:2} diag={d}")

    conn.close()
    print(f"\n✅  Fertig!\n")


if __name__ == "__main__":
    main()
