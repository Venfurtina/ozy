#!/usr/bin/env python3
"""
Navigation Part 2: Aviat Rechner, Koppelnavigation, Terrestrische Navigation
Based on Aircademy PPL(A) Navigation textbook pages 421-490.
"""
import sqlite3, json, os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "takvim.db")

# ═══════════════════════════════════════════════════════════════════════════
#  SVG DIAGRAMS
# ═══════════════════════════════════════════════════════════════════════════

SVG_AVIAT_RECHNER = """<svg viewBox="0 0 540 280" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="280" fill="#0f172a" rx="12"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Aviat 617 – Mechanischer Navigationsrechner</text>
  <!-- Main disk representation -->
  <circle cx="145" cy="155" r="110" fill="#1e293b" stroke="#475569" stroke-width="2"/>
  <circle cx="145" cy="155" r="85" fill="#0f172a" stroke="#334155"/>
  <circle cx="145" cy="155" r="55" fill="#1e293b" stroke="#3b82f6" stroke-width="1.5"/>
  <circle cx="145" cy="155" r="28" fill="#0f172a" stroke="#475569"/>
  <!-- Scale labels on outer ring -->
  <text x="145" y="57" fill="#fbbf24" font-size="9" text-anchor="middle" font-weight="bold">10</text>
  <text x="210" y="100" fill="#fbbf24" font-size="9" text-anchor="middle">20</text>
  <text x="230" y="165" fill="#fbbf24" font-size="9" text-anchor="middle">30</text>
  <text x="205" y="225" fill="#fbbf24" font-size="9" text-anchor="middle">50</text>
  <text x="145" y="250" fill="#fbbf24" font-size="9" text-anchor="middle">70</text>
  <text x="85" y="225" fill="#fbbf24" font-size="9" text-anchor="middle">90</text>
  <!-- Inner ring labels -->
  <text x="145" y="82" fill="#60a5fa" font-size="8" text-anchor="middle">10</text>
  <text x="196" y="110" fill="#60a5fa" font-size="8" text-anchor="middle">15</text>
  <text x="210" y="163" fill="#60a5fa" font-size="8" text-anchor="middle">20</text>
  <!-- Windows (Fenster) -->
  <rect x="120" y="118" width="50" height="24" rx="4" fill="#1a3a2a" stroke="#22c55e" stroke-width="1.5"/>
  <text x="145" y="134" fill="#22c55e" font-size="10" text-anchor="middle" font-weight="bold">AIR SPEED</text>
  <rect x="120" y="152" width="50" height="24" rx="4" fill="#2d1a00" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="145" y="168" fill="#f59e0b" font-size="9" text-anchor="middle" font-weight="bold">DENSITY</text>
  <!-- Rotation arrow -->
  <path d="M 90 90 A 75 75 0 0 1 200 90" stroke="#a78bfa" stroke-width="2" fill="none" stroke-dasharray="5,3"/>
  <text x="145" y="78" fill="#a78bfa" font-size="9" text-anchor="middle">Drehbar</text>
  <!-- Right: Features list -->
  <rect x="275" y="35" width="255" height="232" rx="8" fill="#1e293b" stroke="#334155"/>
  <text x="403" y="57" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Funktionen</text>
  <!-- Feature items -->
  <rect x="285" y="65" width="235" height="24" rx="5" fill="#1e3a5f" stroke="#3b82f6"/>
  <text x="295" y="81" fill="#93c5fd" font-size="10" font-weight="bold">✕÷  Multiplikation &amp; Division</text>
  <rect x="285" y="95" width="235" height="24" rx="5" fill="#1a2e1a" stroke="#22c55e"/>
  <text x="295" y="111" fill="#86efac" font-size="10" font-weight="bold">⏱  Weg-Zeit-Geschwindigkeit</text>
  <rect x="285" y="125" width="235" height="24" rx="5" fill="#2d1f00" stroke="#f59e0b"/>
  <text x="295" y="141" fill="#fcd34d" font-size="10" font-weight="bold">⛽  Kraftstoffverbrauch</text>
  <rect x="285" y="155" width="235" height="24" rx="5" fill="#1e1040" stroke="#a78bfa"/>
  <text x="295" y="171" fill="#c4b5fd" font-size="10" font-weight="bold">✈  TAS- und Mach-Berechnung</text>
  <rect x="285" y="185" width="235" height="24" rx="5" fill="#2d1a1a" stroke="#ef4444"/>
  <text x="295" y="201" fill="#fca5a5" font-size="10" font-weight="bold">⬆  Druck- und Dichtehöhe</text>
  <rect x="285" y="215" width="235" height="24" rx="5" fill="#1e293b" stroke="#475569"/>
  <text x="295" y="231" fill="#cbd5e1" font-size="10" font-weight="bold">🔄  Maßeinheiten umrechnen</text>
  <rect x="285" y="245" width="235" height="14" rx="4" fill="#0f172a"/>
  <text x="403" y="255" fill="#64748b" font-size="9" text-anchor="middle">Rückseite: Winddreiecksaufgaben</text>
</svg>"""

SVG_TAS_BERECHNUNG = """<svg viewBox="0 0 540 220" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="220" fill="#0f172a" rx="12"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">TAS- und Höhenberechnung mit dem Aviat</text>
  <!-- TAS calculation -->
  <rect x="10" y="38" width="250" height="80" rx="8" fill="#1e293b" stroke="#22c55e"/>
  <text x="135" y="58" fill="#86efac" font-size="11" font-weight="bold" text-anchor="middle">TAS-Berechnung</text>
  <text x="135" y="75" fill="#94a3b8" font-size="10" text-anchor="middle">AIR SPEED Fenster (rot)</text>
  <text x="135" y="91" fill="#cbd5e1" font-size="10" text-anchor="middle">OAT ↔ Druckhöhe einstellen</text>
  <text x="135" y="107" fill="#fbbf24" font-size="10" text-anchor="middle" font-weight="bold">→ TAS an äußerer Skala ablesen</text>
  <!-- True altitude -->
  <rect x="10" y="130" width="250" height="78" rx="8" fill="#1e293b" stroke="#3b82f6"/>
  <text x="135" y="150" fill="#93c5fd" font-size="11" font-weight="bold" text-anchor="middle">Wahre Flughöhe (True Altitude)</text>
  <text x="135" y="167" fill="#94a3b8" font-size="10" text-anchor="middle">Altitude-Fenster (blau)</text>
  <text x="135" y="183" fill="#cbd5e1" font-size="10" text-anchor="middle">QNH-Höhe ↔ OAT einstellen</text>
  <text x="135" y="198" fill="#fbbf24" font-size="10" text-anchor="middle" font-weight="bold">→ Wahre Höhe ablesen</text>
  <!-- Density altitude -->
  <rect x="275" y="38" width="255" height="80" rx="8" fill="#1e293b" stroke="#f59e0b"/>
  <text x="402" y="58" fill="#fcd34d" font-size="11" font-weight="bold" text-anchor="middle">Dichtehöhe (Density Altitude)</text>
  <text x="402" y="75" fill="#94a3b8" font-size="10" text-anchor="middle">AIR SPEED Fenster: OAT + Druckhöhe</text>
  <text x="402" y="91" fill="#cbd5e1" font-size="10" text-anchor="middle">→ DENSITY-Fenster ablesen</text>
  <text x="402" y="107" fill="#fca5a5" font-size="10" text-anchor="middle" font-weight="bold">Wichtig für Leistungsberechnungen!</text>
  <!-- Time calculation -->
  <rect x="275" y="130" width="255" height="78" rx="8" fill="#1e293b" stroke="#a78bfa"/>
  <text x="402" y="150" fill="#c4b5fd" font-size="11" font-weight="bold" text-anchor="middle">Zeitberechnung</text>
  <text x="402" y="167" fill="#94a3b8" font-size="10" text-anchor="middle">60 = 1 Stunde (Pfeil-Markierung)</text>
  <text x="402" y="183" fill="#cbd5e1" font-size="10" text-anchor="middle">Verbrauch/h ↔ Flugzeit</text>
  <text x="402" y="198" fill="#fbbf24" font-size="10" text-anchor="middle" font-weight="bold">→ Gesamtverbrauch ablesen</text>
</svg>"""

SVG_KOPPELNAVIGATION = """<svg viewBox="0 0 540 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <defs>
    <pattern id="mapgrid" width="30" height="30" patternUnits="userSpaceOnUse">
      <path d="M 30 0 L 0 0 0 30" fill="none" stroke="#1e293b" stroke-width="0.7"/>
    </pattern>
  </defs>
  <rect width="540" height="260" fill="url(#mapgrid)" rx="12"/>
  <rect width="540" height="260" fill="#0a1220" fill-opacity="0.7" rx="12"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Koppelnavigation – Dead Reckoning (DR)</text>
  <!-- Departure airport -->
  <polygon points="60,195 70,170 80,195" fill="white" stroke="white"/>
  <circle cx="70" cy="195" r="8" fill="none" stroke="white" stroke-width="1.5"/>
  <text x="70" y="215" fill="#94a3b8" font-size="10" text-anchor="middle">Start</text>
  <!-- Planned track -->
  <line x1="80" y1="190" x2="350" y2="90" stroke="#22c55e" stroke-width="2" stroke-dasharray="8,4"/>
  <text x="230" y="128" fill="#22c55e" font-size="10" transform="rotate(-20,230,128)">Geplanter Kurs (TC)</text>
  <!-- Wind drift -->
  <line x1="350" y1="90" x2="395" y2="110" stroke="#60a5fa" stroke-width="2"/>
  <text x="395" y="102" fill="#60a5fa" font-size="10">Wind</text>
  <!-- Actual track -->
  <line x1="80" y1="190" x2="395" y2="110" stroke="#f59e0b" stroke-width="2.5"/>
  <text x="240" y="175" fill="#f59e0b" font-size="10">Tatsächl. Track</text>
  <!-- DR position -->
  <circle cx="350" cy="90" r="6" fill="#22c55e"/>
  <text x="358" y="84" fill="#22c55e" font-size="10" font-weight="bold">DR-Position</text>
  <text x="358" y="96" fill="#94a3b8" font-size="9">(berechnet)</text>
  <!-- Actual position -->
  <circle cx="395" cy="110" r="6" fill="#fbbf24"/>
  <text x="403" y="104" fill="#fbbf24" font-size="10" font-weight="bold">Tats. Position</text>
  <!-- Time markers -->
  <circle cx="175" cy="152" r="4" fill="#a78bfa"/>
  <text x="183" y="148" fill="#a78bfa" font-size="9">t=20min</text>
  <circle cx="265" cy="120" r="4" fill="#a78bfa"/>
  <text x="273" y="116" fill="#a78bfa" font-size="9">t=40min</text>
  <!-- Bottom info boxes -->
  <rect x="10" y="228" width="155" height="25" rx="5" fill="#1e3a1a" stroke="#22c55e"/>
  <text x="88" y="245" fill="#86efac" font-size="10" text-anchor="middle">TH + TAS + Zeit → Position</text>
  <rect x="175" y="228" width="175" height="25" rx="5" fill="#1e3a5f" stroke="#3b82f6"/>
  <text x="263" y="245" fill="#93c5fd" font-size="10" text-anchor="middle">Wind → Drift → Korrektur</text>
  <rect x="360" y="228" width="170" height="25" rx="5" fill="#2d1f00" stroke="#f59e0b"/>
  <text x="445" y="245" fill="#fcd34d" font-size="10" text-anchor="middle">Regelmäßig: pos. überprüfen</text>
</svg>"""

SVG_TERRESTRISCH = """<svg viewBox="0 0 540 250" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <defs>
    <pattern id="tgrid" width="25" height="25" patternUnits="userSpaceOnUse">
      <path d="M 25 0 L 0 0 0 25" fill="none" stroke="#1e293b" stroke-width="0.6"/>
    </pattern>
  </defs>
  <rect width="540" height="250" fill="#0a1220" rx="12"/>
  <rect x="10" y="35" width="320" height="200" rx="8" fill="url(#tgrid)" stroke="#1e293b"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Terrestrische Navigation – Sichtnavigation</text>
  <!-- Rivers / terrain sketch -->
  <path d="M 50 140 Q 100 120 150 145 Q 200 170 250 148 Q 290 130 320 135" stroke="#1d4ed8" stroke-width="3" fill="none" opacity="0.6"/>
  <text x="140" y="110" fill="#60a5fa" font-size="9">Fluss</text>
  <!-- Town -->
  <rect x="140" y="155" width="16" height="12" fill="#6b7280"/>
  <rect x="144" y="152" width="8" height="5" fill="#9ca3af"/>
  <text x="148" y="178" fill="#94a3b8" font-size="9" text-anchor="middle">Ort</text>
  <!-- Aircraft position and track -->
  <text x="80" y="90" font-size="18" text-anchor="middle">✈</text>
  <line x1="80" y1="95" x2="250" y2="120" stroke="#f59e0b" stroke-width="2" stroke-dasharray="6,3"/>
  <!-- Landmark (tower/mast) -->
  <line x1="240" y1="60" x2="240" y2="130" stroke="#ef4444" stroke-width="2"/>
  <polygon points="235,60 240,50 245,60" fill="#ef4444"/>
  <text x="252" y="70" fill="#ef4444" font-size="9">Mast</text>
  <!-- Map reading element -->
  <circle cx="190" cy="118" r="20" fill="none" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="190" y="103" fill="#22c55e" font-size="9" text-anchor="middle">Erkann-</text>
  <text x="190" y="114" fill="#22c55e" font-size="9" text-anchor="middle">tes Merkmal</text>
  <!-- Right: Rules -->
  <rect x="345" y="35" width="185" height="200" rx="8" fill="#1e293b" stroke="#334155"/>
  <text x="437" y="57" fill="white" font-size="11" font-weight="bold" text-anchor="middle">Sichtnavigation</text>
  <rect x="355" y="65" width="165" height="32" rx="5" fill="#1a3a1a" stroke="#22c55e"/>
  <text x="438" y="81" fill="#86efac" font-size="10" text-anchor="middle" font-weight="bold">Kartenorientierung</text>
  <text x="438" y="92" fill="#94a3b8" font-size="9" text-anchor="middle">Karte = Realität abgleichen</text>
  <rect x="355" y="104" width="165" height="32" rx="5" fill="#1e3a5f" stroke="#3b82f6"/>
  <text x="438" y="120" fill="#93c5fd" font-size="10" text-anchor="middle" font-weight="bold">1:60-Regel</text>
  <text x="438" y="131" fill="#94a3b8" font-size="9" text-anchor="middle">1 NM Abweichung pro 60 NM</text>
  <rect x="355" y="143" width="165" height="32" rx="5" fill="#2d1f00" stroke="#f59e0b"/>
  <text x="438" y="159" fill="#fcd34d" font-size="10" text-anchor="middle" font-weight="bold">Dog Legs</text>
  <text x="438" y="170" fill="#94a3b8" font-size="9" text-anchor="middle">Kursabweichung korrigieren</text>
  <rect x="355" y="182" width="165" height="32" rx="5" fill="#2d1a1a" stroke="#ef4444"/>
  <text x="438" y="198" fill="#fca5a5" font-size="10" text-anchor="middle" font-weight="bold">Umplanung im Flug</text>
  <text x="438" y="209" fill="#94a3b8" font-size="9" text-anchor="middle">neue ETA, Kraftstoff prüfen</text>
  <!-- Bottom caption -->
  <rect x="10" y="220" width="320" height="15" rx="4" fill="#0f172a"/>
  <text x="170" y="231" fill="#64748b" font-size="9" text-anchor="middle">Sichtnavigation: Karte, Kompass, Uhr – die Dreifaltigkeit der VFR</text>
</svg>"""

SVG_60_REGEL = """<svg viewBox="0 0 540 230" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="230" fill="#0f172a" rx="12"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Die 1:60-Regel – Kursabweichungskorrektur</text>
  <!-- Main diagram -->
  <!-- Correct track -->
  <line x1="40" y1="180" x2="470" y2="180" stroke="#22c55e" stroke-width="2.5" stroke-dasharray="8,4"/>
  <text x="480" y="184" fill="#22c55e" font-size="11">Kurs</text>
  <!-- Aircraft track (deviated) -->
  <line x1="40" y1="180" x2="280" y2="120" stroke="#f59e0b" stroke-width="2.5"/>
  <!-- 60 NM marker -->
  <line x1="280" y1="100" x2="280" y2="190" stroke="#64748b" stroke-width="1.5" stroke-dasharray="3,3"/>
  <text x="280" y="205" fill="#64748b" font-size="9" text-anchor="middle">60 NM</text>
  <!-- Deviation at 60NM -->
  <line x1="280" y1="120" x2="280" y2="180" stroke="#ef4444" stroke-width="2.5"/>
  <text x="292" y="155" fill="#ef4444" font-size="11" font-weight="bold">d</text>
  <text x="305" y="155" fill="#ef4444" font-size="10">= Abweichung</text>
  <!-- Angle arc -->
  <path d="M 80 180 A 40 40 0 0 0 65 163" stroke="#a78bfa" stroke-width="2" fill="none"/>
  <text x="75" y="158" fill="#a78bfa" font-size="10">α°</text>
  <!-- Formula boxes -->
  <rect x="30" y="38" width="225" height="55" rx="8" fill="#1e293b" stroke="#22c55e"/>
  <text x="143" y="58" fill="#86efac" font-size="11" font-weight="bold" text-anchor="middle">1:60-Formel</text>
  <text x="143" y="76" fill="white" font-size="13" text-anchor="middle" font-weight="bold">α = d × 60 / D</text>
  <text x="143" y="88" fill="#64748b" font-size="9" text-anchor="middle">α=Abweichwinkel · d=Abweichung · D=Distanz</text>
  <!-- Correction formula -->
  <rect x="275" y="38" width="245" height="55" rx="8" fill="#1e293b" stroke="#f59e0b"/>
  <text x="398" y="58" fill="#fcd34d" font-size="11" font-weight="bold" text-anchor="middle">Korrektur</text>
  <text x="398" y="76" fill="white" font-size="12" text-anchor="middle" font-weight="bold">Korr° = α + α/2</text>
  <text x="398" y="88" fill="#64748b" font-size="9" text-anchor="middle">Wenn halbe Strecke noch übrig</text>
  <!-- Example -->
  <rect x="30" y="108" width="225" height="55" rx="8" fill="#1a2040" stroke="#3b82f6"/>
  <text x="143" y="126" fill="#93c5fd" font-size="10" font-weight="bold" text-anchor="middle">Beispiel</text>
  <text x="143" y="143" fill="#cbd5e1" font-size="10" text-anchor="middle">Nach 60 NM: 3 NM Abweichung</text>
  <text x="143" y="158" fill="#60a5fa" font-size="10" text-anchor="middle" font-weight="bold">→ Kurskorrektur: 3°</text>
  <!-- Doubled correction when halfway -->
  <rect x="275" y="108" width="245" height="55" rx="8" fill="#1a2040" stroke="#a78bfa"/>
  <text x="398" y="126" fill="#c4b5fd" font-size="10" font-weight="bold" text-anchor="middle">Halbweg-Korrektur</text>
  <text x="398" y="143" fill="#cbd5e1" font-size="10" text-anchor="middle">3 NM nach 30 NM von 90 NM</text>
  <text x="398" y="158" fill="#a78bfa" font-size="10" text-anchor="middle" font-weight="bold">→ Kor: 6° + 3° = 9° Gesamtkorr.</text>
</svg>"""

SVG_DENSITY_ALTITUDE = """<svg viewBox="0 0 540 220" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="220" fill="#0f172a" rx="12"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Höhenarten: Druck-, Dichte- und Wahre Flughöhe</text>
  <!-- Altitude ladder -->
  <rect x="15" y="40" width="80" height="165" rx="6" fill="#1e293b" stroke="#475569"/>
  <text x="55" y="57" fill="#94a3b8" font-size="10" text-anchor="middle" font-weight="bold">ft</text>
  <text x="55" y="77" fill="#60a5fa" font-size="10" text-anchor="middle">15.000</text>
  <line x1="15" y1="82" x2="95" y2="82" stroke="#1e3a5f" stroke-width="0.8"/>
  <text x="55" y="97" fill="#60a5fa" font-size="10" text-anchor="middle">10.000</text>
  <line x1="15" y1="102" x2="95" y2="102" stroke="#1e3a5f" stroke-width="0.8"/>
  <text x="55" y="117" fill="#60a5fa" font-size="10" text-anchor="middle">5.000</text>
  <line x1="15" y1="122" x2="95" y2="122" stroke="#1e3a5f" stroke-width="0.8"/>
  <text x="55" y="145" fill="#60a5fa" font-size="10" text-anchor="middle">2.000</text>
  <line x1="15" y1="150" x2="95" y2="150" stroke="#1e3a5f" stroke-width="0.8"/>
  <text x="55" y="170" fill="#22c55e" font-size="10" text-anchor="middle" font-weight="bold">MSL / 0</text>
  <!-- Three altitude types comparison -->
  <!-- Pressure Altitude -->
  <rect x="110" y="40" width="130" height="165" rx="6" fill="#1e293b" stroke="#3b82f6"/>
  <text x="175" y="58" fill="#93c5fd" font-size="10" text-anchor="middle" font-weight="bold">Druckhöhe</text>
  <text x="175" y="71" fill="#64748b" font-size="8" text-anchor="middle">(Pressure Altitude)</text>
  <rect x="120" y="80" width="110" height="35" rx="5" fill="#1e3a5f" stroke="#3b82f6"/>
  <text x="175" y="97" fill="#cbd5e1" font-size="9" text-anchor="middle">Höhenmesser auf</text>
  <text x="175" y="109" fill="#fbbf24" font-size="9" text-anchor="middle" font-weight="bold">1013,25 hPa (QNE)</text>
  <text x="175" y="128" fill="#94a3b8" font-size="9" text-anchor="middle">Standardatmosphäre</text>
  <text x="175" y="142" fill="#94a3b8" font-size="9" text-anchor="middle">ohne Tempkorrektur</text>
  <text x="175" y="162" fill="#60a5fa" font-size="9" text-anchor="middle">Basis für TAS &amp;</text>
  <text x="175" y="174" fill="#60a5fa" font-size="9" text-anchor="middle">Dichtehöhe</text>
  <!-- True Altitude -->
  <rect x="250" y="40" width="130" height="165" rx="6" fill="#1e293b" stroke="#22c55e"/>
  <text x="315" y="58" fill="#86efac" font-size="10" text-anchor="middle" font-weight="bold">Wahre Flughöhe</text>
  <text x="315" y="71" fill="#64748b" font-size="8" text-anchor="middle">(True Altitude)</text>
  <rect x="260" y="80" width="110" height="35" rx="5" fill="#1a3a1a" stroke="#22c55e"/>
  <text x="315" y="97" fill="#cbd5e1" font-size="9" text-anchor="middle">Druckhöhe + OAT</text>
  <text x="315" y="109" fill="#fbbf24" font-size="9" text-anchor="middle" font-weight="bold">korrigiert</text>
  <text x="315" y="128" fill="#94a3b8" font-size="9" text-anchor="middle">Mit Aviat berechnen:</text>
  <text x="315" y="142" fill="#94a3b8" font-size="9" text-anchor="middle">Druckhöhe + OAT</text>
  <text x="315" y="162" fill="#22c55e" font-size="9" text-anchor="middle">Hindernisplanung,</text>
  <text x="315" y="174" fill="#22c55e" font-size="9" text-anchor="middle">MEF-Vergleich</text>
  <!-- Density Altitude -->
  <rect x="390" y="40" width="135" height="165" rx="6" fill="#1e293b" stroke="#f59e0b"/>
  <text x="458" y="58" fill="#fcd34d" font-size="10" text-anchor="middle" font-weight="bold">Dichtehöhe</text>
  <text x="458" y="71" fill="#64748b" font-size="8" text-anchor="middle">(Density Altitude)</text>
  <rect x="400" y="80" width="115" height="35" rx="5" fill="#2d1f00" stroke="#f59e0b"/>
  <text x="458" y="97" fill="#cbd5e1" font-size="9" text-anchor="middle">Druckhöhe + hohe</text>
  <text x="458" y="109" fill="#ef4444" font-size="9" text-anchor="middle" font-weight="bold">Temperatur!</text>
  <text x="458" y="128" fill="#94a3b8" font-size="9" text-anchor="middle">Theor. Höhe in ISA</text>
  <text x="458" y="142" fill="#94a3b8" font-size="9" text-anchor="middle">für gleiche Leistung</text>
  <text x="458" y="162" fill="#f59e0b" font-size="9" text-anchor="middle">Leistungsverlust bei</text>
  <text x="458" y="174" fill="#f59e0b" font-size="9" text-anchor="middle">hoher Dichtehöhe!</text>
</svg>"""

# ═══════════════════════════════════════════════════════════════════════════
#  CHAPTER CONTENT
# ═══════════════════════════════════════════════════════════════════════════

CHAPTERS = {
    "nav-aviat": {
        "subject_id": "nav",
        "title": "Der Aviat 617 – Mechanischer Navigationsrechner",
        "sort_order": 55,
        "exam": 1,
        "sections": [
            ("heading", "Kapitel 3.3: Der mechanische Navigationsrechner", "Der Aviat 617"),
            ("diagram", SVG_AVIAT_RECHNER, "Aviat 617 – Aufbau und Funktionen"),
            ("subheading", "3.3.1 Aufbau des Aviat 617", None),
            ("text", "Der Aviat 617 ist wie ähnliche Modelle ein Kreisrechenschieber. Er besteht aus einer runden Haupttrechenscheibe (beidseitig bedruckt) und einem Diagrammschieber.", None),
            ("fact", "Elektronische Navigationsrechner sind für offizielle Prüfungen in der Regel nicht zugelassen. Der mechanische Rechner (Aviat 617 oder ähnlich) ist der Standard.", None),
            ("table_row", "Vorderseite", "Zwei gegeneinander verschiebbare Hauptskalen (äußere und innere) + 4 Fenster in der Mitte. Für: Mult./Div., Geschwindigkeit, TAS, Kraftstoff, Maßeinheiten."),
            ("table_row", "Rückseite", "Zwei Skalen (innere drehbar, äußere halber Umfang) + Diagrammschieber. Ausschließlich für Winddreieck-Aufgaben."),
            ("table_row", "Ausgangspunkt", "Beide äußere Skalen deckungsgleich stellen (schwarz hinterlegte 10 exakt untereinander)."),
            ("subheading", "3.3.2 Maßeinheiten umrechnen", None),
            ("text", "Maßeinheiten können ausschließlich innerhalb einer Farbgruppe umgerechnet werden (blau=Flüssigkeitsmaße, rot=große Entfernungen, schwarz=kleine Entfernungen).", None),
            ("table_row", "Längeneinheiten (rot)", "NM ↔ km ↔ Statute Miles. Ausgangswert auf innerer Skala unter Markierungsstrich der Ausgangseinheit stellen."),
            ("table_row", "Geschwindigkeiten", "Keine gesonderten Markierungen für kt/km/h – Zeitbezug 1 Stunde auf roten Markierungen."),
            ("table_row", "Kraftstoff-Einheiten", "Liter, US-Gal, Imp. Gal. Sp. G.-Skala (0,72 für AVGAS) für kg/lbs Umrechnung."),
            ("subheading", "3.3.3 Zeitberechnung", None),
            ("text", "Mit dem Aviaten können Zeitberechnungen schnell durchgeführt werden. Die 60-Markierung auf der inneren Skala steht für 1 Stunde.", None),
            ("table_row", "Kraftstoffverbrauch", "60 auf innere Skala, Verbrauch/h auf äußere. Flugdauer einstellen → Gesamtverbrauch ablesen."),
            ("table_row", "Weg-Zeit", "60 (=1h) unter Geschwindigkeit. Zeit ablesen unter zurückgelegter Strecke."),
            ("table_row", "Faustregel", "5×8 Regel: bei 5 min Flugzeit mit 150 kt → 12,5 NM zurückgelegt"),
            ("subheading", "3.3.4 TAS-Berechnung", None),
            ("diagram", SVG_TAS_BERECHNUNG, "TAS, Wahre Höhe und Dichtehöhe mit dem Aviat berechnen"),
            ("text", "Die wahre Eigengeschwindigkeit (TAS) hängt von der Außentemperatur und dem Luftdruck/Höhe ab. Sie weicht mit zunehmender Höhe erheblich von der IAS ab.", None),
            ("table_row", "TAS-Berechnung (Aviat)", "Rotes Air Speed-Fenster: OAT und Druckhöhe gegenüberstellen → EAS/CAS innen, TAS außen ablesen."),
            ("table_row", "TAS Faustformel", "TAS = CAS + 2% pro 1.000 ft Flughöhe"),
            ("subheading", "3.3.5 Flughöhenberechnung", None),
            ("diagram", SVG_DENSITY_ALTITUDE, "Druckhöhe, Wahre Flughöhe und Dichtehöhe im Vergleich"),
            ("text", "Mit dem Aviaten können verschiedene Höhenarten berechnet werden. Die Dichtehöhe ist besonders für Leistungsberechnungen wichtig.", None),
            ("table_row", "Druckhöhe", "Höhenmesser auf 1013,25 hPa eingestellt. Basis für TAS und Dichtehöhe."),
            ("table_row", "QNH-Höhe → Wahre Höhe", "Altitude-Fenster (blau): QNH-Höhe + OAT → Wahre Höhe ablesen."),
            ("table_row", "Dichtehöhe", "Druckhöhe + hohe Temperatur → Dichtehöhe steigt erheblich. Kritisch für Leistung!"),
            ("infobox", "An heißen Sommertagen liegt die Dichtehöhe deutlich über der tatsächlichen Flughöhe – dies führt zu erheblichen Leistungseinbußen beim Start!", "Achtung: Dichtehöhe"),
        ],
        "quiz": [
            {"q": "Wofür wird die Rückseite des Aviat 617 ausschließlich verwendet?", "opts": ["TAS-Berechnung","Winddreieck-Aufgaben","Kraftstoffberechnung","Zeitberechnung"], "a": 1, "e": "Die Rückseite der Hauptrechenscheibe und der Diagrammschieber des Aviat 617 sind ausschließlich für Winddreieck-Aufgaben vorgesehen."},
            {"q": "Was bedeutet es, wenn der Aviat 617 für Kraftstoffberechnungen auf Zeitbasis genutzt wird?", "opts": ["Man stellt die Flugzeit ein und liest die Geschwindigkeit ab","Man stellt 60 (=1 Stunde) unter dem Stundenwert und liest bei der Flugdauer den Gesamtverbrauch ab","Man multipliziert Verbrauch mal Stunden direkt im Kopf","Man liest die Kraftstoffdichte ab"], "a": 1, "e": "Für Kraftstoffberechnungen stellt man den Verbrauch pro Stunde (auf der äußeren Skala) unter der 60-Markierung (= 1 Stunde auf innerer Skala) ein und kann bei beliebiger Flugdauer den Gesamtverbrauch ablesen."},
            {"q": "Wie wird die Dichtehöhe (Density Altitude) definiert?", "opts": ["Die tatsächliche Flughöhe über MSL","Die theoretische Höhe in der ISA-Standardatmosphäre, bei der dieselbe Luftdichte wie aktuell herrscht","Die angezeigte Höhe am Höhenmesser","Die Druckhöhe minus Temperaturkorrektur"], "a": 1, "e": "Dichtehöhe = die Höhe in der ISA-Standardatmosphäre, bei der die gleiche Luftdichte wie am aktuellen Ort herrscht. Hohe Temperaturen erhöhen die Dichtehöhe erheblich, was zu Leistungseinbußen führt."},
            {"q": "Warum ist die TAS höher als die IAS/CAS bei großen Höhen?", "opts": ["Wegen des Gegenwinds","Wegen der mit der Höhe abnehmenden Luftdichte – das Flugzeug muss schneller durch dünnere Luft","Wegen des Kursfehlers","Wegen der Erdkrümmung"], "a": 1, "e": "Mit zunehmender Höhe nimmt die Luftdichte ab. Bei konstanter IAS/CAS muss das Flugzeug tatsächlich schneller (höhere TAS) durch die dünnere Luft fliegen, um den gleichen dynamischen Druck zu erzeugen."},
            {"q": "Welche Höhe wird benötigt, wenn der Höhenmesser auf 1013,25 hPa eingestellt ist?", "opts": ["QNH-Höhe","Wahre Flughöhe","Druckhöhe (Pressure Altitude)","Dichtehöhe"], "a": 2, "e": "Die Druckhöhe ergibt sich, wenn der Höhenmesser auf den Standardluftdruck von 1013,25 hPa (QNE) eingestellt ist. Sie dient als Basis für TAS- und Dichtehöhenberechnungen."},
            {"q": "Was kennzeichnet einen sicheren Umgang mit dem Aviat bei der Maßeinheitenumrechnung?", "opts": ["Man kann alle Einheiten beliebig umrechnen","Umrechnung funktioniert nur innerhalb einer Farbgruppe (blau, rot, schwarz)","Man braucht immer die Rückseite","Man rechnet nur Geschwindigkeiten um"], "a": 1, "e": "Wichtig: Maßeinheiten können ausschließlich innerhalb der gleichen Farbgruppe umgerechnet werden. Blau = Flüssigkeitsmaße, Rot = große Entfernungen, Schwarz = kleine Entfernungen."},
        ],
        "flashcards": [
            ("Was sind die Hauptfunktionen des Aviat 617?", "Multiplikation/Division, Weg-Zeit-Geschwindigkeit, Kraftstoff, TAS, Druck-/Dichtehöhe, Maßeinheiten, Winddreieck (Rückseite)"),
            ("Aviat: TAS-Berechnung – welches Fenster?", "Rotes AIR SPEED-Fenster: OAT gegenüber Druckhöhe einstellen → TAS außen ablesen"),
            ("Was ist die Dichtehöhe?", "Theoretische Höhe in ISA, bei der gleiche Luftdichte wie aktuell. Steigt bei hoher Temperatur stark an → Leistungsverlust!"),
            ("Was bedeutet 60 auf dem Aviat?", "60 Minuten = 1 Stunde. Die Pfeil-Markierung bei der 60 dient als Zeitbezug für alle Zeit/Weg/Geschwindigkeit-Berechnungen."),
            ("Kraftstoffberechnung Aviat: Schritte?", "1. Verbrauch/h auf äußerer Skala unter 60 (innere Skala) stellen. 2. Flugdauer einstellen. 3. Gesamtverbrauch auf äußerer Skala ablesen."),
        ]
    },

    "nav-sicht": {
        "subject_id": "nav",
        "title": "Navigation während des Fluges – Koppel- & Sichtnavigation",
        "sort_order": 58,
        "exam": 1,
        "sections": [
            ("heading", "Kapitel 3.5: Navigation während des Fluges", "Terrestrische Navigation und Koppelnavigation"),
            ("diagram", SVG_KOPPELNAVIGATION, "Koppelnavigation (Dead Reckoning) – Positionsberechnung"),
            ("subheading", "3.5.1 Terrestrische Navigation (Sichtnavigation)", None),
            ("text", "Die Sichtnavigation (Visual Navigation) basiert auf dem Abgleich von Karte und Gelände. Dabei werden markante Geländepunkte identifiziert und mit der Navigationskarte verglichen.", None),
            ("diagram", SVG_TERRESTRISCH, "Sichtnavigation: Geländeabgleich mit der Karte"),
            ("fact", "Drei Grundwerkzeuge der Sichtnavigation: Karte (aktuelle VFR-Karte), Kompass (Steuerkurs) und Uhr (Zeit für Koppelrechnung). Diese Dreifaltigkeit ermöglicht genaue Navigation ohne weitere Hilfsmittel.", None),
            ("table_row", "Kartenorientierung", "Karte in Flugrichtung ausrichten. Gelände mit Karte abgleichen. Markante Punkte suchen: Straßenkreuzungen, Seen, Städte, Bahnlinien."),
            ("table_row", "Koppelnavigation (DR)", "Dead Reckoning: Ausgehend von bekannter Position Kurs, Geschwindigkeit und Zeit nutzen, um neue Position zu berechnen."),
            ("table_row", "ETA (Estimated Time of Arrival)", "Berechnung: ETA = ETD + Flugzeit (= Distanz / GS)"),
            ("table_row", "Kontrollpunkte (CheckPoints)", "Bekannte Geländepunkte auf der Route zur Lagebestimmung. Regelmäßig mit ETA abgleichen."),
            ("subheading", "3.5.2 Koppelnavigation (Dead Reckoning)", None),
            ("text", "Bei Koppelnavigation wird die aktuelle Position durch Berechnung aus der letzten bekannten Position, Kurs, Geschwindigkeit und Zeit ermittelt.", None),
            ("fact", "Koppelnavigation-Formel: Neue Position = Ausgangsposition + (TH × TAS × Zeit ± Windeinfluss)", None),
            ("table_row", "Fehlerquellen DR", "Windabschätzungsfehler, Steuerkursfehler, Zeitfehler – all diese Fehler akkumulieren sich!"),
            ("table_row", "Genauigkeit", "Fehler wächst mit Zeit und Entfernung. Je mehr Zeit seit letzter bekannter Position → desto größer der Unsicherheitsbereich."),
            ("table_row", "Praktische Empfehlung", "Position regelmäßig (alle 10–15 Min.) durch Sichtabgleich bestätigen. Niemals nur auf DR vertrauen."),
            ("subheading", "3.5.3 1:60-Regel", None),
            ("diagram", SVG_60_REGEL, "Die 1:60-Regel zur Kurskorrektur"),
            ("text", "Die 1:60-Regel ist eine schnelle Näherungsformel zur Berechnung und Korrektur von Kursabweichungen.", None),
            ("table_row", "Grundformel", "α = d × 60 / D  (α=Abweichwinkel in °, d=Seitenabweichung in NM, D=geflogene Distanz in NM)"),
            ("table_row", "Beispiel", "3 NM Abweichung nach 60 NM → α = 3 × 60/60 = 3° Kurskorrektur"),
            ("table_row", "Halbweg-Korrektur", "Wenn noch gleich viel Strecke übrig: Korr = 2α (= α zum Ziel + α zurück zum Kurs)"),
            ("infobox", "Die 1:60-Regel gilt auch für Windbestimmung, ETA-Korrekturen und Zielpunkt-Abschätzung. Merke: 1 NM Abweichung pro 60 NM entspricht 1° Kursabweichung.", "Anwendung 1:60-Regel"),
            ("subheading", "3.5.4 Dog Legs – Kursänderungen während des Fluges", None),
            ("text", "Wenn das Flugzeug vom geplanten Kurs abgewichen ist und eine Korrektur eingeleitet werden soll, wird eine Dog-Leg-Manöver durchgeführt.", None),
            ("table_row", "Dog Leg", "Kursänderung um definierte Gradzahl für bestimmte Zeit → dann zurück auf geplanten Kurs. Einfache Korrekturmethode."),
            ("table_row", "Umplanung", "Bei erheblichen Abweichungen: neue ETA berechnen, Kraftstoff prüfen, ATC informieren wenn nötig."),
            ("subheading", "3.5.5 Umplanungen im Flug", None),
            ("text", "Umplanungen können notwendig sein wegen: Wetteränderung, Airspace-Aktivierung, technischer Probleme, zu niedrigem Kraftstoffstand.", None),
            ("table_row", "Neue ETA", "Neue Distanz / aktuelle GS + aktuelle Zeit = neue ETA"),
            ("table_row", "Kraftstoffcheck", "Verbleibende Zeit × Verbrauch/h + Reserve = benötigter Kraftstoff. Vergleich mit verfügbarem Kraftstoff."),
            ("fact", "Sicherheitsmindesthöhe: Vor jedem neuen Streckenabschnitt MEF/MGAA aus Karte prüfen. Sicherheitspuffer von mindestens 500 ft über MEF halten.", None),
        ],
        "quiz": [
            {"q": "Was versteht man unter Koppelnavigation (Dead Reckoning)?", "opts": ["Navigation nur mit Funk","Berechnung der aktuellen Position aus letzter bekannter Position + Kurs + Geschwindigkeit + Zeit","Navigation mit GPS","Sichtnavigation anhand von Geländepunkten"], "a": 1, "e": "Dead Reckoning (DR) = Koppelnavigation: Ausgehend von einer bekannten Position wird die neue Position durch Kurs, Geschwindigkeit und Zeit berechnet, ohne externe Positionsreferenz."},
            {"q": "Auf welchen 3 Grundwerkzeugen basiert die Sichtnavigation?", "opts": ["GPS, Funk und Radar","Karte, Kompass und Uhr","Autopilot, VOR und NDB","Barometer, Variometer und Tacho"], "a": 1, "e": "Die Dreifaltigkeit der Sichtnavigation: Karte (aktuell, korrekt gefaltet), Kompass (für Kurs) und Uhr (für Zeit/ETA-Berechnung)."},
            {"q": "Wie lautet die 1:60-Regel zur Berechnung der Kursabweichung?", "opts": ["α = d + D / 60","α = d × 60 / D","α = D × d × 60","α = D / d × 60"], "a": 1, "e": "1:60-Regel: α (Abweichwinkel in Grad) = Seitenabweichung (d in NM) × 60 / geflogene Distanz (D in NM). Beispiel: 3 NM Abweichung nach 90 NM → α = 3×60/90 = 2°."},
            {"q": "Was ist ein Kontrollpunkt (Checkpoint) bei der Sichtnavigation?", "opts": ["Ein Flugplatz","Ein bekannter Geländepunkt auf der Route zur regelmäßigen Positionskontrolle","Ein Funknavigationsgerät","Ein Meldepunkt für ATC"], "a": 1, "e": "Kontrollpunkte sind markante, eindeutig identifizierbare Geländepunkte (Städte, Kreuzungen, Seen, Bahnhöfe) auf der geplanten Route, die regelmäßig mit der ETA abgeglichen werden."},
            {"q": "Welche Schritte gehören zur vollständigen Umplanung im Flug?", "opts": ["Nur Funkspruch an ATC","Neue ETA berechnen, Kraftstoff prüfen, ATC informieren, neue Route planen","Nur GPS neu eingeben","Nur die Geschwindigkeit erhöhen"], "a": 1, "e": "Bei Umplanungen: 1) Neue Distanz/Kurs bestimmen, 2) neue ETA = Restdistanz/GS + aktuelle Zeit, 3) Kraftstoff: Restzeit × Verbrauch + Reserve prüfen, 4) ATC informieren wenn nötig."},
            {"q": "Wie groß ist laut 1:60-Regel die Kursabweichung, wenn du nach 30 NM 2 NM vom Kurs abgekommen bist?", "opts": ["1°","2°","4°","6°"], "a": 2, "e": "α = d × 60 / D = 2 × 60 / 30 = 4°. Deshalb ist frühzeitiges Erkennen einer Abweichung wichtig – nach wenig Strecke ist die Abweichungsformel sehr sensitiv."},
            {"q": "Warum nimmt der Fehler bei der Koppelnavigation mit der Zeit zu?", "opts": ["Weil der Kompass immer ungenauer wird","Weil Fehler in Kurs, Geschwindigkeit und Wind sich mit der Zeit akkumulieren","Weil GPS ausfällt","Weil die Karte veraltet"], "a": 1, "e": "Bei der Koppelnavigation akkumulieren sich kleine Fehler: Kursabweichungen, Windschätzfehler und Zeitfehler werden mit jeder Minute größer. Deshalb muss die DR-Position regelmäßig durch Sichtabgleich überprüft werden."},
            {"q": "Was ist die Formel für die Estimated Time of Arrival (ETA)?", "opts": ["ETA = ETD × GS / Distanz","ETA = ETD + (Distanz / GS)","ETA = Distanz × GS + ETD","ETA = ETD - Windeinfluss"], "a": 1, "e": "ETA = ETD + Flugzeit. Flugzeit = Distanz / Ground Speed (GS). Dabei muss beachtet werden, dass GS von Wind beeinflusst wird."},
        ],
        "flashcards": [
            ("Was sind die 3 Säulen der Sichtnavigation?", "1. Karte (aktuell, korrekt) 2. Kompass (Steuerkurs) 3. Uhr (Zeit/ETA)"),
            ("1:60-Regel: Formel?", "α (°) = d (NM Abweichung) × 60 / D (NM geflogen)"),
            ("1:60-Regel: Halbwegkorrektur?", "Wenn noch gleich viel Strecke übrig: Gesamtkorrektur = 2α (einmal zum Kurs, einmal zum Ziel)"),
            ("ETA-Formel?", "ETA = Abflugzeit (ETD) + Flugzeit = ETD + (Distanz / GS)"),
            ("Was ist Dead Reckoning?", "Koppelnavigation: Aus bekannter Position + Kurs + TAS + Zeit die neue Position berechnen."),
            ("Wann ist eine Umplanung nötig?", "Wetteränderung, Airspace-Aktivierung, technisches Problem, Kraftstoffmangel oder erhebliche Kursabweichung"),
        ]
    },
}

# ═══════════════════════════════════════════════════════════════════════════
#  IMPORT
# ═══════════════════════════════════════════════════════════════════════════

def run():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row

    for ch_id, ch in CHAPTERS.items():
        print(f"\n→ Importing: {ch_id}")
        existing = db.execute("SELECT id FROM learn_chapters WHERE id=?", (ch_id,)).fetchone()
        if not existing:
            db.execute("INSERT INTO learn_chapters (id, subject_id, title, sort_order, exam_relevant) VALUES (?,?,?,?,?)",
                       (ch_id, ch["subject_id"], ch["title"], ch["sort_order"], ch["exam"]))
        else:
            db.execute("UPDATE learn_chapters SET title=?, sort_order=?, exam_relevant=? WHERE id=?",
                       (ch["title"], ch["sort_order"], ch["exam"], ch_id))

        db.execute("DELETE FROM learn_sections WHERE chapter_id=?", (ch_id,))
        db.execute("DELETE FROM learn_quiz WHERE chapter_id=?", (ch_id,))
        db.execute("DELETE FROM learn_flashcards WHERE chapter_id=?", (ch_id,))

        for order, sec in enumerate(ch["sections"]):
            sec_type, content, extra = sec
            db.execute("INSERT INTO learn_sections (chapter_id, type, content, extra, sort_order) VALUES (?,?,?,?,?)",
                       (ch_id, sec_type, content, extra, order))

        for order, q in enumerate(ch["quiz"]):
            db.execute("INSERT INTO learn_quiz (chapter_id, question, options, answer, explanation, is_official, sort_order) VALUES (?,?,?,?,?,?,?)",
                       (ch_id, q["q"], json.dumps(q["opts"], ensure_ascii=False), q["a"], q["e"], 1, order))

        for order, (front, back) in enumerate(ch.get("flashcards", [])):
            db.execute("INSERT INTO learn_flashcards (chapter_id, front, back, sort_order) VALUES (?,?,?,?)",
                       (ch_id, front, back, order))

        print(f"  ✓ {len(ch['sections'])} sections | {len(ch['quiz'])} quiz | {len(ch.get('flashcards',[]))} flashcards")

    db.commit()
    db.close()
    print("\n✅ Part 2 import complete!")

if __name__ == "__main__":
    run()
