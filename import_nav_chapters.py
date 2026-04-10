#!/usr/bin/env python3
"""
Import comprehensive Navigation chapters (Kap. 4: Funk-/Satellitennavigation)
based on Aircademy PPL(A) Navigation textbook content (pages 351-420).
"""
import sqlite3, json, os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "takvim.db")

# ─── SVG Diagrams ──────────────────────────────────────────────────────────

SVG_WELLENFORMEL = """<svg viewBox="0 0 520 200" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:520px;font-family:system-ui,sans-serif">
  <rect width="520" height="200" fill="#0d1623" rx="10"/>
  <text x="260" y="24" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Wellenformel: c = λ × f</text>
  <!-- wavelength illustration -->
  <path d="M30 100 Q80 50 130 100 Q180 150 230 100 Q280 50 330 100 Q380 150 430 100" stroke="#60a5fa" stroke-width="2.5" fill="none"/>
  <!-- wavelength arrows -->
  <line x1="30" y1="160" x2="230" y2="160" stroke="#fbbf24" stroke-width="1.5" marker-end="url(#arr)" marker-start="url(#arr2)"/>
  <defs>
    <marker id="arr" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto"><path d="M0,0 L6,3 L0,6 Z" fill="#fbbf24"/></marker>
    <marker id="arr2" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto-start-reverse"><path d="M0,0 L6,3 L0,6 Z" fill="#fbbf24"/></marker>
  </defs>
  <text x="130" y="178" fill="#fbbf24" font-size="12" text-anchor="middle">λ (Wellenlänge)</text>
  <!-- frequency label -->
  <text x="440" y="105" fill="#34d399" font-size="11">f = Frequenz</text>
  <text x="440" y="120" fill="#94a3b8" font-size="10">(Hz = 1/s)</text>
  <!-- formula boxes -->
  <rect x="30" y="30" width="180" height="36" rx="8" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="120" y="47" fill="white" font-size="11" text-anchor="middle">c = 300.000 km/s</text>
  <text x="120" y="61" fill="#93c5fd" font-size="10" text-anchor="middle">Lichtgeschwindigkeit</text>
  <rect x="220" y="30" width="140" height="36" rx="8" fill="#1a3a1a" stroke="#22c55e" stroke-width="1.5"/>
  <text x="290" y="47" fill="white" font-size="12" text-anchor="middle" font-weight="bold">λ = c / f</text>
  <text x="290" y="61" fill="#86efac" font-size="10" text-anchor="middle">f = c / λ</text>
  <rect x="370" y="30" width="130" height="36" rx="8" fill="#2d1a1a" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="435" y="47" fill="white" font-size="11" text-anchor="middle">↑f = ↓λ</text>
  <text x="435" y="61" fill="#fcd34d" font-size="10" text-anchor="middle">umgekehrt proportional</text>
</svg>"""

SVG_WELLENARTEN = """<svg viewBox="0 0 540 280" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <defs>
    <linearGradient id="skyGrd" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0%" stop-color="#080e2a"/>
      <stop offset="60%" stop-color="#0d2040"/>
      <stop offset="100%" stop-color="#1a4060"/>
    </linearGradient>
  </defs>
  <rect width="540" height="280" fill="url(#skyGrd)" rx="10"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Ausbreitung elektromagnetischer Wellen</text>
  <!-- Ionosphere band -->
  <rect x="0" y="45" width="540" height="22" fill="#4f46e5" opacity="0.35" rx="0"/>
  <text x="10" y="60" fill="#a5b4fc" font-size="10" font-weight="bold">IONOSPHÄRE</text>
  <!-- Earth curve -->
  <ellipse cx="270" cy="440" rx="360" ry="220" fill="#1a3a1a" stroke="#22c55e" stroke-width="2"/>
  <text x="270" y="262" fill="#86efac" font-size="11" text-anchor="middle">ERDOBERFLÄCHE</text>
  <!-- Transmitter -->
  <polygon points="120,240 128,200 136,240" fill="#fbbf24"/>
  <line x1="128" y1="200" x2="128" y2="245" stroke="#fbbf24" stroke-width="2"/>
  <text x="128" y="258" fill="#fbbf24" font-size="10" text-anchor="middle">Sender</text>
  <!-- Bodenwelle -->
  <path d="M140 235 Q180 225 220 232 Q260 240 300 235 Q340 228 370 232" stroke="#22c55e" stroke-width="2.5" fill="none" stroke-dasharray="6,3"/>
  <text x="255" y="220" fill="#22c55e" font-size="11" font-weight="bold">Bodenwelle</text>
  <text x="255" y="232" fill="#86efac" font-size="9">folgt Erdkrümmung</text>
  <!-- Raumwelle -->
  <path d="M140 225 L200 100 L270 67 L340 100 L400 225" stroke="#60a5fa" stroke-width="2.5" fill="none"/>
  <text x="272" y="82" fill="#60a5fa" font-size="10" text-anchor="middle">↑ Ionosphäre ↓</text>
  <text x="420" y="215" fill="#60a5fa" font-size="11" font-weight="bold">Raumwelle</text>
  <!-- Direkte Welle -->
  <line x1="140" y1="220" x2="430" y2="215" stroke="#f59e0b" stroke-width="2" stroke-dasharray="4,3"/>
  <text x="430" y="235" fill="#f59e0b" font-size="11" font-weight="bold">Direkte Welle</text>
  <text x="430" y="247" fill="#fcd34d" font-size="9">Line of Sight</text>
  <!-- Tote Zone label -->
  <text x="370" y="190" fill="#ef4444" font-size="10" font-weight="bold">Tote Zone</text>
  <text x="370" y="202" fill="#fca5a5" font-size="9">(Skip Zone)</text>
  <!-- Aircraft -->
  <text x="430" y="208" font-size="16">✈</text>
</svg>"""

SVG_FREQUENZTABELLE = """<svg viewBox="0 0 540 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="260" fill="#0d1623" rx="10"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Frequenzbänder und Navigationsanlagen</text>
  <!-- Header row -->
  <rect x="10" y="30" width="520" height="24" fill="#1e3a5f" rx="4"/>
  <text x="55" y="46" fill="#93c5fd" font-size="11" font-weight="bold">Band</text>
  <text x="130" y="46" fill="#93c5fd" font-size="11" font-weight="bold">Freq./Wellenlänge</text>
  <text x="330" y="46" fill="#93c5fd" font-size="11" font-weight="bold">Navigationsanlage</text>
  <!-- Rows -->
  <rect x="10" y="55" width="520" height="22" fill="#ffffff08" rx="2"/>
  <text x="55" y="70" fill="#fbbf24" font-size="11" font-weight="bold">LF</text>
  <text x="130" y="70" fill="white" font-size="10">30–300 kHz / 10–1 km</text>
  <text x="330" y="70" fill="#86efac" font-size="10">NDB (ab 130 kHz)</text>
  <rect x="10" y="78" width="520" height="22" fill="#ffffff04" rx="2"/>
  <text x="55" y="93" fill="#fbbf24" font-size="11" font-weight="bold">MF</text>
  <text x="130" y="93" fill="white" font-size="10">300–3000 kHz / 1000–100m</text>
  <text x="330" y="93" fill="#86efac" font-size="10">NDB (bis 535/1750 kHz)</text>
  <rect x="10" y="101" width="520" height="22" fill="#ffffff08" rx="2"/>
  <text x="55" y="116" fill="#60a5fa" font-size="11" font-weight="bold">HF</text>
  <text x="130" y="116" fill="white" font-size="10">3–30 MHz / 100–10 m</text>
  <text x="330" y="116" fill="#86efac" font-size="10">Air-Ground COM</text>
  <rect x="10" y="124" width="520" height="22" fill="#ffffff04" rx="2"/>
  <text x="55" y="139" fill="#60a5fa" font-size="11" font-weight="bold">VHF</text>
  <text x="130" y="139" fill="white" font-size="10">30–300 MHz / 10–1 m</text>
  <text x="330" y="139" fill="#86efac" font-size="10">VOR, VDF, VHF COM, Marker</text>
  <rect x="10" y="147" width="520" height="22" fill="#ffffff08" rx="2"/>
  <text x="55" y="162" fill="#a78bfa" font-size="11" font-weight="bold">UHF</text>
  <text x="130" y="162" fill="white" font-size="10">300–3000 MHz / 1–0.1 m</text>
  <text x="330" y="162" fill="#86efac" font-size="10">DME, SSR/Transponder, GPS</text>
  <rect x="10" y="170" width="520" height="22" fill="#ffffff04" rx="2"/>
  <text x="55" y="185" fill="#a78bfa" font-size="11" font-weight="bold">SHF</text>
  <text x="130" y="185" fill="white" font-size="10">3–30 GHz / 10–1 cm</text>
  <text x="330" y="185" fill="#86efac" font-size="10">MLS, Radar, PAR</text>
  <!-- Key rule box -->
  <rect x="10" y="200" width="520" height="50" fill="#1a1a3a" rx="6" stroke="#6366f1" stroke-width="1.5"/>
  <text x="270" y="218" fill="#a5b4fc" font-size="11" text-anchor="middle" font-weight="bold">⭐ Merkregel: Je höher die Frequenz → desto direkter die Ausbreitung</text>
  <text x="270" y="233" fill="white" font-size="10" text-anchor="middle">LF/MF: Boden- und Raumwellen  |  VHF/UHF: Nur direkte Wellen (Line of Sight)</text>
  <text x="270" y="247" fill="#94a3b8" font-size="10" text-anchor="middle">Fading (Dämmerungseffekt) betrifft LF/MF – nicht VHF/UHF</text>
</svg>"""

SVG_QGRUPPEN = """<svg viewBox="0 0 540 280" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="280" fill="#0d1623" rx="10"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Q-Gruppen: Peilungen und ihre Bedeutung</text>
  <!-- Aircraft position -->
  <text x="140" y="165" font-size="22" text-anchor="middle">✈</text>
  <text x="140" y="183" fill="#94a3b8" font-size="10" text-anchor="middle">Luftfahrzeug</text>
  <!-- Station -->
  <circle cx="400" cy="160" r="18" fill="#1e3a5f" stroke="#60a5fa" stroke-width="2"/>
  <text x="400" y="165" fill="#60a5fa" font-size="12" text-anchor="middle" font-weight="bold">VDF</text>
  <text x="400" y="183" fill="#94a3b8" font-size="10" text-anchor="middle">Station</text>
  <!-- North arrows -->
  <line x1="140" y1="120" x2="140" y2="90" stroke="#22c55e" stroke-width="2" marker-end="url(#nArr)"/>
  <text x="140" y="84" fill="#22c55e" font-size="11" text-anchor="middle">MN</text>
  <defs>
    <marker id="nArr" markerWidth="6" markerHeight="6" refX="3" refY="6" orient="auto"><path d="M0,6 L3,0 L6,6 Z" fill="#22c55e"/></marker>
    <marker id="bArr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#fbbf24"/></marker>
    <marker id="rArr" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#f87171"/></marker>
  </defs>
  <!-- Line AC to Station -->
  <line x1="160" y1="158" x2="382" y2="160" stroke="#fbbf24" stroke-width="2" stroke-dasharray="6,3" marker-end="url(#bArr)"/>
  <!-- QDM label -->
  <rect x="230" y="135" width="110" height="42" rx="6" fill="#1a2a1a" stroke="#22c55e" stroke-width="1.5"/>
  <text x="285" y="152" fill="#22c55e" font-size="12" text-anchor="middle" font-weight="bold">QDM</text>
  <text x="285" y="167" fill="#86efac" font-size="9" text-anchor="middle">MH + RB</text>
  <text x="285" y="178" fill="#86efac" font-size="9" text-anchor="middle">= MB to station</text>
  <!-- QDR label (reverse) -->
  <rect x="10" y="200" width="120" height="42" rx="6" fill="#1a1a3a" stroke="#6366f1" stroke-width="1.5"/>
  <text x="70" y="217" fill="#a5b4fc" font-size="12" text-anchor="middle" font-weight="bold">QDR</text>
  <text x="70" y="232" fill="#c7d2fe" font-size="9" text-anchor="middle">= QDM ± 180°</text>
  <text x="70" y="243" fill="#c7d2fe" font-size="9" text-anchor="middle">MB from station</text>
  <!-- QUJ/QTE labels -->
  <rect x="140" y="200" width="120" height="42" rx="6" fill="#2d1a1a" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="200" y="217" fill="#fbbf24" font-size="12" text-anchor="middle" font-weight="bold">QUJ</text>
  <text x="200" y="232" fill="#fcd34d" font-size="9" text-anchor="middle">= TH + RB</text>
  <text x="200" y="243" fill="#fcd34d" font-size="9" text-anchor="middle">TB to station</text>
  <rect x="270" y="200" width="120" height="42" rx="6" fill="#1a1a1a" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="330" y="217" fill="#e2e8f0" font-size="12" text-anchor="middle" font-weight="bold">QTE</text>
  <text x="330" y="232" fill="#cbd5e1" font-size="9" text-anchor="middle">= QUJ ± 180°</text>
  <text x="330" y="243" fill="#cbd5e1" font-size="9" text-anchor="middle">TB from station</text>
  <!-- Rule box -->
  <rect x="395" y="200" width="135" height="55" rx="6" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="462" y="217" fill="#93c5fd" font-size="10" text-anchor="middle" font-weight="bold">Anflugregeln VDF:</text>
  <text x="462" y="231" fill="white" font-size="9" text-anchor="middle">QDM↓ → kleiner steuern</text>
  <text x="462" y="243" fill="white" font-size="9" text-anchor="middle">QDM↑ → größer steuern</text>
  <text x="462" y="255" fill="#60a5fa" font-size="9" text-anchor="middle">Kreuzpeilung → Position</text>
</svg>"""

SVG_NDB_ADF = """<svg viewBox="0 0 540 290" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="290" fill="#0d1623" rx="10"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">NDB/ADF – Anzeigegeräte und Peilungen</text>
  <!-- RBI -->
  <circle cx="90" cy="130" r="55" fill="#0d1f3d" stroke="#60a5fa" stroke-width="2"/>
  <circle cx="90" cy="130" r="48" fill="none" stroke="#1e3a5f" stroke-width="1"/>
  <!-- Tick marks -->
  <line x1="90" y1="78" x2="90" y2="85" stroke="#60a5fa" stroke-width="2"/>
  <line x1="142" y1="130" x2="135" y2="130" stroke="#60a5fa" stroke-width="1.5"/>
  <line x1="38" y1="130" x2="45" y2="130" stroke="#60a5fa" stroke-width="1.5"/>
  <line x1="90" y1="182" x2="90" y2="175" stroke="#60a5fa" stroke-width="1.5"/>
  <text x="90" y="75" fill="#60a5fa" font-size="10" text-anchor="middle">0°</text>
  <text x="148" y="133" fill="#60a5fa" font-size="9">90°</text>
  <text x="90" y="195" fill="#60a5fa" font-size="9" text-anchor="middle">180°</text>
  <text x="25" y="133" fill="#60a5fa" font-size="9">270°</text>
  <!-- RBI needle -->
  <line x1="90" y1="130" x2="110" y2="87" stroke="#ef4444" stroke-width="3" marker-end="url(#rn)"/>
  <line x1="90" y1="130" x2="70" y2="173" stroke="#94a3b8" stroke-width="2"/>
  <defs>
    <marker id="rn" markerWidth="6" markerHeight="6" refX="3" refY="6" orient="auto"><path d="M0,6 L3,0 L6,6 Z" fill="#ef4444"/></marker>
  </defs>
  <!-- Plane icon in center -->
  <text x="90" y="134" font-size="14" text-anchor="middle">✈</text>
  <text x="90" y="200" fill="white" font-size="11" text-anchor="middle" font-weight="bold">RBI</text>
  <text x="90" y="212" fill="#94a3b8" font-size="9" text-anchor="middle">Starre Kursrose</text>
  <text x="90" y="223" fill="#94a3b8" font-size="9" text-anchor="middle">0° = Längsachse</text>
  <!-- RMI -->
  <circle cx="270" cy="130" r="55" fill="#0d1f3d" stroke="#22c55e" stroke-width="2"/>
  <!-- RMI rotated compass -->
  <text x="270" y="82" fill="#22c55e" font-size="10" text-anchor="middle">MN 000°</text>
  <text x="326" y="133" fill="#22c55e" font-size="9">090°</text>
  <text x="270" y="190" fill="#22c55e" font-size="9" text-anchor="middle">180°</text>
  <text x="205" y="133" fill="#22c55e" font-size="9">270°</text>
  <!-- Kursmarkierung (HDG bug) -->
  <rect x="262" y="76" width="16" height="8" fill="#fbbf24" rx="2"/>
  <text x="270" y="83" fill="black" font-size="7" text-anchor="middle">▲</text>
  <!-- RMI needle -->
  <line x1="270" y1="130" x2="292" y2="87" stroke="#ef4444" stroke-width="3" marker-end="url(#rn2)"/>
  <line x1="270" y1="130" x2="248" y2="173" stroke="#94a3b8" stroke-width="2"/>
  <defs>
    <marker id="rn2" markerWidth="6" markerHeight="6" refX="3" refY="6" orient="auto"><path d="M0,6 L3,0 L6,6 Z" fill="#ef4444"/></marker>
  </defs>
  <text x="270" y="134" font-size="14" text-anchor="middle">✈</text>
  <text x="270" y="200" fill="white" font-size="11" text-anchor="middle" font-weight="bold">RMI</text>
  <text x="270" y="212" fill="#94a3b8" font-size="9" text-anchor="middle">Fernkompass-Kursrose</text>
  <text x="270" y="223" fill="#22c55e" font-size="9" text-anchor="middle">Nadelspitze = QDM</text>
  <!-- Fehlerquellen table -->
  <rect x="350" y="50" width="175" height="180" rx="8" fill="#1e1a10" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="437" y="68" fill="#fbbf24" font-size="11" text-anchor="middle" font-weight="bold">NDB Fehlerquellen</text>
  <text x="365" y="86" fill="#fcd34d" font-size="10">⚡ Elektrische Entladungen</text>
  <text x="365" y="101" fill="#fcd34d" font-size="10">🌊 Küsteneffekt (Shoreline)</text>
  <text x="365" y="116" fill="#fcd34d" font-size="10">⛰️ Bergeffekt (Mountain)</text>
  <text x="365" y="131" fill="#fcd34d" font-size="10">🔄 Quadrantal Error</text>
  <text x="365" y="146" fill="#fcd34d" font-size="10">📉 Dip Error (Kurven)</text>
  <text x="365" y="161" fill="#fcd34d" font-size="10">🌙 Fading (Dämmerung)</text>
  <line x1="365" y1="170" x2="515" y2="170" stroke="#f59e0b" stroke-width="0.5" opacity="0.5"/>
  <text x="437" y="186" fill="white" font-size="11" text-anchor="middle" font-weight="bold">Gesamtfehler: ±5°</text>
  <text x="437" y="200" fill="#94a3b8" font-size="9" text-anchor="middle">vs. VOR: ±1-2°</text>
  <text x="437" y="213" fill="#86efac" font-size="9" text-anchor="middle">Homing: RB=000° halten</text>
  <text x="437" y="225" fill="#86efac" font-size="9" text-anchor="middle">Steh. Peilung: WCA anlegen</text>
</svg>"""

SVG_VOR_CDI = """<svg viewBox="0 0 540 290" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="290" fill="#0d1623" rx="10"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">VOR – CDI-Anzeige und Interpretation</text>
  <!-- CDI 1: centered -->
  <circle cx="90" cy="140" r="55" fill="#0d1f3d" stroke="#60a5fa" stroke-width="2"/>
  <!-- OBS ring ticks -->
  <text x="90" y="88" fill="#93c5fd" font-size="9" text-anchor="middle">270</text>
  <!-- Course mark -->
  <rect x="82" y="87" width="16" height="7" fill="#fbbf24" rx="2"/>
  <!-- CDI needle centered -->
  <line x1="90" y1="98" x2="90" y2="182" stroke="#f59e0b" stroke-width="3"/>
  <!-- Dots -->
  <circle cx="70" cy="140" r="3" fill="#94a3b8"/>
  <circle cx="80" cy="140" r="3" fill="#94a3b8"/>
  <circle cx="100" cy="140" r="3" fill="#94a3b8"/>
  <circle cx="110" cy="140" r="3" fill="#94a3b8"/>
  <!-- TO indicator -->
  <polygon points="90,105 82,120 98,120" fill="#22c55e"/>
  <text x="90" y="118" fill="black" font-size="7" text-anchor="middle" font-weight="bold">TO</text>
  <text x="90" y="208" fill="white" font-size="11" text-anchor="middle" font-weight="bold">Auf Radial</text>
  <text x="90" y="220" fill="#22c55e" font-size="9" text-anchor="middle">Nadel zentriert → ✓</text>
  <!-- CDI 2: needle right -->
  <circle cx="270" cy="140" r="55" fill="#0d1f3d" stroke="#ef4444" stroke-width="2"/>
  <rect x="262" y="87" width="16" height="7" fill="#fbbf24" rx="2"/>
  <!-- Needle right -->
  <line x1="310" y1="98" x2="310" y2="182" stroke="#ef4444" stroke-width="3"/>
  <circle cx="250" cy="140" r="3" fill="#94a3b8"/>
  <circle cx="260" cy="140" r="3" fill="#94a3b8"/>
  <circle cx="280" cy="140" r="3" fill="#94a3b8"/>
  <circle cx="290" cy="140" r="3" fill="#94a3b8"/>
  <polygon points="270,105 262,120 278,120" fill="#22c55e"/>
  <text x="270" y="118" fill="black" font-size="7" text-anchor="middle" font-weight="bold">TO</text>
  <text x="270" y="208" fill="white" font-size="11" text-anchor="middle" font-weight="bold">Nadel rechts</text>
  <text x="270" y="220" fill="#ef4444" font-size="9" text-anchor="middle">→ nach rechts fliegen</text>
  <text x="270" y="231" fill="#fca5a5" font-size="9" text-anchor="middle">(zur Nadel hin)</text>
  <!-- CDI 3: FROM -->
  <circle cx="450" cy="140" r="55" fill="#0d1f3d" stroke="#f59e0b" stroke-width="2"/>
  <rect x="442" y="87" width="16" height="7" fill="#fbbf24" rx="2"/>
  <!-- Needle centered -->
  <line x1="450" y1="98" x2="450" y2="182" stroke="#f59e0b" stroke-width="3"/>
  <circle cx="430" cy="140" r="3" fill="#94a3b8"/>
  <circle cx="440" cy="140" r="3" fill="#94a3b8"/>
  <circle cx="460" cy="140" r="3" fill="#94a3b8"/>
  <circle cx="470" cy="140" r="3" fill="#94a3b8"/>
  <!-- FROM indicator (inverted) -->
  <polygon points="450,170 442,155 458,155" fill="#ef4444"/>
  <text x="450" y="165" fill="white" font-size="7" text-anchor="middle" font-weight="bold">FR</text>
  <text x="450" y="208" fill="white" font-size="11" text-anchor="middle" font-weight="bold">FROM-Anzeige</text>
  <text x="450" y="220" fill="#f59e0b" font-size="9" text-anchor="middle">Kurs führt von Station weg</text>
  <!-- Key rule box -->
  <rect x="10" y="245" width="520" height="36" rx="6" fill="#1a3a1a" stroke="#22c55e" stroke-width="1.5"/>
  <text x="270" y="261" fill="#86efac" font-size="11" text-anchor="middle" font-weight="bold">⭐ Merkregel: CDI = Kommandogerät – Korrekturen IMMER zur Nadel hin!</text>
  <text x="270" y="275" fill="white" font-size="10" text-anchor="middle">Schweigekegel (~40°) direkt über Station: Warnflagge erscheint, TO→FROM wechselt</text>
</svg>"""

SVG_GPS = """<svg viewBox="0 0 540 270" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <defs>
    <radialGradient id="earthGrd" cx="50%" cy="50%" r="50%">
      <stop offset="0%" stop-color="#1a4a7a"/>
      <stop offset="100%" stop-color="#0d1623"/>
    </radialGradient>
  </defs>
  <rect width="540" height="270" fill="#060a18" rx="10"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">GPS-System: Funktionsprinzip und Segmente</text>
  <!-- Earth -->
  <circle cx="270" cy="155" r="60" fill="url(#earthGrd)" stroke="#1e4a7f" stroke-width="2"/>
  <text x="270" y="159" fill="#93c5fd" font-size="11" text-anchor="middle" font-weight="bold">WGS84</text>
  <!-- Satellite orbits (ellipses) -->
  <ellipse cx="270" cy="155" rx="120" ry="50" fill="none" stroke="#4f46e5" stroke-width="1" opacity="0.5" transform="rotate(-30 270 155)"/>
  <ellipse cx="270" cy="155" rx="120" ry="50" fill="none" stroke="#4f46e5" stroke-width="1" opacity="0.5" transform="rotate(30 270 155)"/>
  <ellipse cx="270" cy="155" rx="120" ry="50" fill="none" stroke="#4f46e5" stroke-width="1" opacity="0.5" transform="rotate(90 270 155)"/>
  <!-- Satellites -->
  <rect x="148" y="115" width="16" height="10" fill="#fbbf24" rx="2"/>
  <rect x="155" y="108" width="2" height="8" fill="#94a3b8"/>
  <rect x="152" y="107" width="8" height="2" fill="#94a3b8"/>
  <rect x="375" y="115" width="16" height="10" fill="#fbbf24" rx="2"/>
  <rect x="382" y="108" width="2" height="8" fill="#94a3b8"/>
  <rect x="379" y="107" width="8" height="2" fill="#94a3b8"/>
  <rect x="255" y="75" width="16" height="10" fill="#fbbf24" rx="2"/>
  <rect x="262" y="68" width="2" height="8" fill="#94a3b8"/>
  <rect x="259" y="67" width="8" height="2" fill="#94a3b8"/>
  <rect x="215" y="185" width="16" height="10" fill="#fbbf24" rx="2"/>
  <!-- Signal lines -->
  <line x1="165" y1="120" x2="250" y2="165" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.7"/>
  <line x1="382" y1="120" x2="295" y2="165" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.7"/>
  <line x1="265" y1="83" x2="268" y2="150" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.7"/>
  <line x1="228" y1="190" x2="258" y2="175" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="4,3" opacity="0.7"/>
  <!-- Aircraft receiver -->
  <text x="265" y="170" font-size="16" text-anchor="middle">✈</text>
  <!-- Info boxes -->
  <rect x="10" y="40" width="130" height="60" rx="6" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="75" y="58" fill="#93c5fd" font-size="10" text-anchor="middle" font-weight="bold">Raumsegment</text>
  <text x="75" y="72" fill="white" font-size="10" text-anchor="middle">30 Satelliten</text>
  <text x="75" y="84" fill="white" font-size="10" text-anchor="middle">6 Bahnen</text>
  <text x="75" y="96" fill="#60a5fa" font-size="9" text-anchor="middle">20.183 km Höhe</text>
  <rect x="10" y="115" width="130" height="55" rx="6" fill="#1a3a1a" stroke="#22c55e" stroke-width="1.5"/>
  <text x="75" y="133" fill="#86efac" font-size="10" text-anchor="middle" font-weight="bold">Min. 4 Satelliten</text>
  <text x="75" y="147" fill="white" font-size="10" text-anchor="middle">für 3D-Position</text>
  <text x="75" y="161" fill="#22c55e" font-size="9" text-anchor="middle">5-6 für RAIM</text>
  <rect x="10" y="183" width="130" height="55" rx="6" fill="#2d1a1a" stroke="#f59e0b" stroke-width="1.5"/>
  <text x="75" y="201" fill="#fbbf24" font-size="10" text-anchor="middle" font-weight="bold">Bodensegment</text>
  <text x="75" y="215" fill="white" font-size="10" text-anchor="middle">MCS Colorado</text>
  <text x="75" y="229" fill="#fcd34d" font-size="9" text-anchor="middle">+ Überwachungsst.</text>
  <!-- Right side RAIM + SA -->
  <rect x="400" y="40" width="130" height="60" rx="6" fill="#1a1a3a" stroke="#6366f1" stroke-width="1.5"/>
  <text x="465" y="58" fill="#a5b4fc" font-size="10" text-anchor="middle" font-weight="bold">RAIM</text>
  <text x="465" y="72" fill="white" font-size="9" text-anchor="middle">Integritätsprüfung</text>
  <text x="465" y="84" fill="#c7d2fe" font-size="9" text-anchor="middle">Erkennt fehlerh. Sat.</text>
  <text x="465" y="96" fill="#6366f1" font-size="9" text-anchor="middle">NOTAM bei Ausfall</text>
  <rect x="400" y="115" width="130" height="55" rx="6" fill="#1a2a1a" stroke="#f87171" stroke-width="1.5"/>
  <text x="465" y="133" fill="#fca5a5" font-size="10" text-anchor="middle" font-weight="bold">Selective Avail.</text>
  <text x="465" y="147" fill="white" font-size="9" text-anchor="middle">US kann Genauigkeit</text>
  <text x="465" y="161" fill="#f87171" font-size="9" text-anchor="middle">jederzeit reduzieren</text>
  <rect x="400" y="183" width="130" height="55" rx="6" fill="#1a1520" stroke="#a78bfa" stroke-width="1.5"/>
  <text x="465" y="201" fill="#c4b5fd" font-size="10" text-anchor="middle" font-weight="bold">GALILEO (EU)</text>
  <text x="465" y="215" fill="white" font-size="9" text-anchor="middle">GLONASS (RU)</text>
  <text x="465" y="229" fill="#a78bfa" font-size="9" text-anchor="middle">Weitere GNSS-Systeme</text>
</svg>"""

SVG_TRANSPONDER = """<svg viewBox="0 0 540 250" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="250" fill="#0d1623" rx="10"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Sekundärradar (SSR) und Transponder</text>
  <!-- Ground radar -->
  <rect x="20" y="160" width="100" height="60" rx="6" fill="#1e3a5f" stroke="#60a5fa" stroke-width="2"/>
  <text x="70" y="185" fill="#93c5fd" font-size="11" text-anchor="middle" font-weight="bold">SSR</text>
  <text x="70" y="200" fill="white" font-size="10" text-anchor="middle">Bodenstation</text>
  <text x="70" y="213" fill="#60a5fa" font-size="9" text-anchor="middle">Interrogator</text>
  <!-- Radar dish icon -->
  <path d="M50 160 Q70 140 90 160" stroke="#3b82f6" stroke-width="3" fill="none"/>
  <line x1="70" y1="160" x2="70" y2="145" stroke="#60a5fa" stroke-width="2"/>
  <!-- Aircraft with transponder -->
  <rect x="380" y="60" width="140" height="80" rx="8" fill="#1a1a10" stroke="#fbbf24" stroke-width="2"/>
  <text x="450" y="82" fill="#fbbf24" font-size="11" text-anchor="middle" font-weight="bold">Transponder</text>
  <text x="450" y="97" fill="white" font-size="10" text-anchor="middle">Antwortgerät</text>
  <text x="450" y="115" fill="#fcd34d" font-size="10" text-anchor="middle">Antwort: 1090 MHz</text>
  <text x="450" y="129" fill="#94a3b8" font-size="9" text-anchor="middle">Anfrage: 1030 MHz</text>
  <!-- Aircraft icon -->
  <text x="380" y="75" font-size="22">✈</text>
  <!-- Interrogation signal -->
  <line x1="120" y1="175" x2="375" y2="100" stroke="#3b82f6" stroke-width="2" stroke-dasharray="8,4" marker-end="url(#blArr)"/>
  <text x="250" y="135" fill="#93c5fd" font-size="10" text-anchor="middle">1030 MHz Anfrage</text>
  <!-- Reply signal -->
  <line x1="375" y1="115" x2="125" y2="185" stroke="#22c55e" stroke-width="2" stroke-dasharray="8,4" marker-end="url(#grArr)"/>
  <text x="250" y="170" fill="#86efac" font-size="10" text-anchor="middle">1090 MHz Antwort</text>
  <defs>
    <marker id="blArr" markerWidth="7" markerHeight="7" refX="3" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#3b82f6"/></marker>
    <marker id="grArr" markerWidth="7" markerHeight="7" refX="3" refY="3" orient="auto"><path d="M0,0 L7,3 L0,6 Z" fill="#22c55e"/></marker>
  </defs>
  <!-- Codes table -->
  <rect x="10" y="40" width="230" height="110" rx="6" fill="#0d1a10" stroke="#22c55e" stroke-width="1.5"/>
  <text x="125" y="58" fill="#86efac" font-size="11" text-anchor="middle" font-weight="bold">Wichtige Codes</text>
  <text x="25" y="74" fill="#22c55e" font-size="11" font-weight="bold">7000</text>
  <text x="80" y="74" fill="white" font-size="10">Standard VFR</text>
  <text x="25" y="90" fill="#ef4444" font-size="11" font-weight="bold">7500</text>
  <text x="80" y="90" fill="#fca5a5" font-size="10">Entführung (Hijacking)</text>
  <text x="25" y="106" fill="#f59e0b" font-size="11" font-weight="bold">7600</text>
  <text x="80" y="106" fill="#fcd34d" font-size="10">Funkausfall</text>
  <text x="25" y="122" fill="#ef4444" font-size="11" font-weight="bold">7700</text>
  <text x="80" y="122" fill="#fca5a5" font-size="10">Notfall (MAYDAY)</text>
  <text x="125" y="142" fill="#94a3b8" font-size="9" text-anchor="middle">4.096 Möglichkeiten (4 × 0-7)</text>
  <!-- Mode info -->
  <rect x="10" y="160" width="120" height="80" rx="6" fill="#1a1a3a" stroke="#6366f1" stroke-width="1.5"/>
  <text x="70" y="177" fill="#a5b4fc" font-size="10" text-anchor="middle" font-weight="bold">Mode Übersicht</text>
  <text x="20" y="192" fill="#c7d2fe" font-size="9">Mode A: Code</text>
  <text x="20" y="205" fill="#c7d2fe" font-size="9">Mode C: Code + Höhe</text>
  <text x="20" y="218" fill="#c7d2fe" font-size="9">Mode S: Code + Höhe +</text>
  <text x="20" y="230" fill="#c7d2fe" font-size="9">Eintragungszeichen + DL</text>
</svg>"""

# ─── Chapter data ──────────────────────────────────────────────────────────

CHAPTERS = [
  {
    "id": "nav-funk-basics",
    "title": "Technische Grundlagen der Funknavigation",
    "exam_relevant": 1,
    "sort_order": 3,
    "sections": [
      ("heading", "4.1 Technische Grundlagen der Funknavigation", "Kapitel 4 – Funk-/Satellitennavigation"),
      ("text", "Funknavigationsanlagen nutzen elektromagnetische Wellen zur Informationsübertragung. Diese Wellen entstehen durch elektromagnetische Induktion an Sendeantennen und breiten sich mit Lichtgeschwindigkeit (c = 300.000 km/s) aus. Sie bestehen aus einem elektrischen und einem senkrecht dazu stehenden magnetischen Feld und schwingen senkrecht zur Ausbreitungsrichtung."),
      ("diagram", SVG_WELLENFORMEL, "Abb. – Wellenformel: c = λ × f"),
      ("heading", "4.1.1 Elektromagnetische Wellen und die Wellenformel", None),
      ("text", "Die Wellenlänge λ und die Frequenz f stehen in unmittelbarem Zusammenhang: Je größer die Wellenlänge, desto niedriger die Frequenz – und umgekehrt. Beide sind über die Ausbreitungsgeschwindigkeit (Lichtgeschwindigkeit) miteinander gekoppelt: c = λ × f."),
      ("fact", "Merkmerkregel: Je größer die Wellenlänge → desto niedriger die Frequenz. Je kleiner die Wellenlänge → desto höher die Frequenz."),
      ("heading", "4.1.3 Wellenausbreitung (Wellenarten)", None),
      ("text", "Elektromagnetische Wellen breiten sich je nach Frequenz unterschiedlich aus. Grundsätzlich werden drei Arten unterschieden: Bodenwellen, Raumwellen und direkte Wellen (quasioptisch)."),
      ("diagram", SVG_WELLENARTEN, "Abb. – Ausbreitung der verschiedenen Wellenarten"),
      ("text", "Bodenwellen breiten sich entlang der Erdoberfläche aus und folgen der Erdkrümmung. Ihre Reichweite hängt von Frequenz, Sendeleistung und Bodenleitfähigkeit ab. Raumwellen werden an der Ionosphäre reflektiert und können große Entfernungen überbrücken. Direkte Wellen (UKW/VHF-Bereich ab ca. 30 MHz) breiten sich geradlinig aus und erfordern eine Sichtverbindung zwischen Sender und Empfänger (Line of Sight)."),
      ("warning", "Fading (Dämmerungseffekt): Bei LF/MF-Anlagen (NDB) überlagern sich Boden- und Raumwellen besonders in der Dämmerung. Dies kann zu Fehlpeilungen führen!"),
      ("heading", "4.1.4 Störfaktoren", None),
      ("text", "Wichtige Störfaktoren für Funknavigationsanlagen: Überlagerungen/Fading (NDB besonders betroffen), Brechung beim Übergang zwischen Medien, Reflexionen an topographischen Erhebungen, Absorption durch Ionosphärenschichten sowie elektrische Entladungen (Gewitter)."),
      ("diagram", SVG_FREQUENZTABELLE, "Abb. – Frequenzbänder und zugehörige Navigationsanlagen"),
      ("heading", "4.1.2 Modulations- und Betriebsarten", None),
      ("text", "Für die Übertragung von Informationen auf Trägerwellen werden verschiedene Modulationsarten eingesetzt: Amplitudenmodulation (AM), Frequenzmodulation (FM) und Impulsmodulation. In der Luftfahrt sind folgende Sendearten relevant:"),
      ("table_row", "N0N", "Keine Modulation – unmodulierte Trägerwelle"),
      ("table_row", "A1A", "Morsekennung durch Unterbrechung der Trägerwelle (Ton beim Empfang)"),
      ("table_row", "A2A", "Tonmodulierte Morsekennung (NDB-Standard)"),
      ("table_row", "A3E", "Sprechfunk durch Amplitudenmodulation"),
      ("fact", "Die Sendeart A3E wird für VHF-Sprechfunk verwendet. NDBs verwenden meist A1A oder A2A für ihre Morsekennung."),
      ("focus", "Wellenformel c = λ × f; Frequenzbänder und Navigationsanlagen; Wellenarten und Ausbreitungscharakteristika; Fading bei LF/MF-Anlagen"),
    ],
    "quiz": [
      {"q": "Was gilt für die Beziehung zwischen Wellenlänge und Frequenz?", "options": ["Je größer die Wellenlänge, desto höher die Frequenz", "Je größer die Wellenlänge, desto niedriger die Frequenz", "Wellenlänge und Frequenz sind unabhängig", "Beide ändern sich immer gleich"], "answer": 1, "explanation": "c = λ × f: Bei konstanter Lichtgeschwindigkeit sind Wellenlänge und Frequenz umgekehrt proportional."},
      {"q": "Wie breiten sich Funkwellen im VHF/UHF-Bereich aus?", "options": ["Als Bodenwellen", "Als Raumwellen", "Als direkte (quasioptische) Wellen – Line of Sight", "Gar nicht"], "answer": 2, "explanation": "Ab ca. 30 MHz breiten sich Wellen ausschließlich als direkte Wellen aus – Sichtverbindung erforderlich."},
      {"q": "Was ist der 'Fading-Effekt' beim NDB?", "options": ["Signalverbesserung bei Nacht", "Überlagerungen von Raum- und Bodenwellen → Störungen und Fehlpeilungen", "Ausfall des Senders", "Höhenabhängige Dämpfung"], "answer": 1, "explanation": "Fading (Dämmerungseffekt) entsteht durch Überlagerung von Boden- und Raumwellen, besonders bei LF/MF-Anlagen."},
      {"q": "Welche Sendeart wird für VHF-Sprechfunk genutzt?", "options": ["N0N", "A1A", "A3E", "A2A"], "answer": 2, "explanation": "A3E: Amplitudenmodulation mit Sprachsignal – Standard für VHF-COM-Sprechfunk."},
      {"q": "In welchem Frequenzbereich sendet das NDB in Deutschland?", "options": ["VHF (108-118 MHz)", "UHF (960-1215 MHz)", "MF (200-526,5 kHz)", "HF (3-30 MHz)"], "answer": 2, "explanation": "NDBs senden im MF-Bereich. In Deutschland: 200–526,5 kHz (Kanalabstand 0,5 kHz)."},
      {"q": "Was beschreibt der Doppler-Effekt?", "options": ["Frequenz bleibt konstant", "Bei Annäherung steigt die Frequenz, bei Entfernung sinkt sie", "Nur für Schallwellen relevant", "Frequenz verdoppelt sich immer"], "answer": 1, "explanation": "Der Doppler-Effekt bewirkt eine Frequenzänderung bei Relativbewegung zwischen Sender und Empfänger."},
    ]
  },
  {
    "id": "nav-vdf",
    "title": "UKW-Peiler (VDF) – Peilungen und Q-Gruppen",
    "exam_relevant": 1,
    "sort_order": 4,
    "sections": [
      ("heading", "4.2 UKW-Peiler (VDF)", "Fremdpeilungsverfahren per Sprechfunk"),
      ("text", "UKW-Peilanlagen (VDF – VHF Direction Finder) ermöglichen eine Richtungsbestimmung vom Luftfahrzeug zur Bodenstation mit Hilfe einer bestehenden Sprechfunkverbindung. Da die Peilung von der Bodenstation ausgeführt wird, handelt es sich um ein Fremdpeilungsverfahren. Kein spezielles Bordgerät ist erforderlich."),
      ("fact", "Großer Vorteil: Keine spezielle Bordausrüstung nötig. Die Peilung wird von der Bodenstation ausgeführt und dem Piloten per Funk mitgeteilt."),
      ("heading", "4.2.1 Peilungen und Relative Bearing", None),
      ("text", "Peilungen beschreiben die Luftfahrzeugposition in Bezug auf eine Funkstation als Winkel zwischen zwei gedachten Linien. Das Relative Bearing (RB) ist der Winkel zwischen der Flugzeuglängsachse und der Linie Flugzeug–Bodenstation. Es ist nicht nur von der Position, sondern auch vom Steuerkurs abhängig."),
      ("diagram", SVG_QGRUPPEN, "Abb. – Q-Gruppen: Peilungsarten und Zusammenhänge"),
      ("heading", "4.2.2 Q-Gruppen – Übersicht", None),
      ("table_row", "QDM = MH + RB", "Missweisende Peilung ZUR Station (Magnetic Bearing to the station)"),
      ("table_row", "QDR = QDM ± 180°", "Missweisende Peilung VON der Station (Magnetic Bearing from the station)"),
      ("table_row", "QUJ = TH + RB", "Rechtweisende Peilung ZUR Station (True Bearing to the station)"),
      ("table_row", "QTE = QUJ ± 180°", "Rechtweisende Peilung VON der Station (True Bearing from the station)"),
      ("fact", "QDM wird GRÖSSER → GRÖSSER steuern. QDM wird KLEINER → KLEINER steuern."),
      ("heading", "4.2.3 Fehler und Genauigkeit", None),
      ("text", "Reflexionen an Hindernissen, Bergketten und Wellenüberlagerungen können zu falschen Peilwerten führen. Die Genauigkeit einer VDF-Peilanlage liegt im Allgemeinen bei ±1° bis ±2°. Für Kreuzpeilungen werden mindestens zwei VDF-Stationen benötigt."),
      ("heading", "4.2.4 Navigationsverfahren VDF", None),
      ("text", "Das QDM (missweisende Peilung zur Station) wird bei VDF-Anflügen als Führungsgröße verwendet. Wird das QDM abgeflogen, steuert das Luftfahrzeug direkt auf die Bodenstation zu. Bei Wind muss entsprechend korrigiert werden. Für Kreuzpeilungen werden die QTE-Werte von zwei verschiedenen Stationen als Standlinien in die Karte eingezeichnet – der Schnittpunkt ergibt die Position."),
      ("focus", "QDM-Formel auswendig können; Kreuzpeilung verstehen; VDF als Fremdpeilungsverfahren erkennen"),
    ],
    "quiz": [
      {"q": "Was ist das QDM?", "options": ["Rechtweisende Peilung von der Station", "Missweisende Peilung zur Station", "Frequenz des VDF", "Höhe über der Station"], "answer": 1, "explanation": "QDM = Magnetic Bearing to the station = missweisende Peilung ZUR Station."},
      {"q": "Wie lautet die Formel für QDM?", "options": ["QDM = TH + RB", "QDM = MH – RB", "QDM = MH + RB", "QDM = TH – VAR"], "answer": 2, "explanation": "QDM = MH + RB (Magnetic Heading + Relative Bearing)."},
      {"q": "Was ist der Hauptvorteil des VDF?", "options": ["GPS-Koordinaten", "Kein spezielles Bordgerät nötig – nur VHF-Funk", "UHF-Betrieb", "Unabhängig von Bodenstation"], "answer": 1, "explanation": "Die Peilung erfolgt bodenseitig. Bordgerät: nur das normale VHF-Sprechfunkgerät."},
      {"q": "Anflug mit VDF: Das QDM wird kleiner. Was tun?", "options": ["Größer steuern", "Kleiner steuern", "Höhe ändern", "Nichts"], "answer": 1, "explanation": "QDM wird kleiner → kleiner steuern. QDM wird größer → größer steuern."},
      {"q": "Was liefert eine VDF-Kreuzpeilung?", "options": ["Nur Kurs", "Nur Entfernung", "Eine eindeutige Position durch Schnittpunkt zweier QTE-Linien", "Wind"], "answer": 2, "explanation": "Kreuzpeilung: QTE zweier Stationen als Standlinien in Karte → Schnittpunkt = Position."},
    ]
  },
  {
    "id": "nav-ndb",
    "title": "Ungerichtetes Funkfeuer (NDB) und ADF",
    "exam_relevant": 1,
    "sort_order": 5,
    "sections": [
      ("heading", "4.3 Ungerichtetes Funkfeuer (NDB)", "Eigenpeilung mit ADF"),
      ("text", "Das NDB (Non-Directional Beacon) ist eine Sendestation, die ein kontinuierliches und ungerichtetes Signal auf einer bestimmten Frequenz abstrahlt. An Bord eines Luftfahrzeuges empfängt der ADF (Automatic Direction Finder) diese Signale und zeigt das Relative Bearing (RB) zur Station an. Da die Peilung vom Luftfahrzeug ausgeht, ist es ein Eigenpeilungsverfahren."),
      ("fact", "NDB-Frequenzbereich: 190–1750 kHz (LF/MF). Deutschland: 200–526,5 kHz. Anflug-NDBs: ca. 15–25 NM Reichweite, 2-Buchstaben-Kennung. Strecken-NDBs: ca. 100–150 NM, 3-Buchstaben-Kennung."),
      ("heading", "4.3.1 Funktionsprinzip – Bodenkomponenten", None),
      ("text", "Die NDB-Bodenanlage besteht aus: Sender, ungerichteter Sendeantenne (vertikaler Mast oder T-Antenne) und Überwachungsanlage. Die ADF-Bordanlage besteht aus: Rahmenantenne (Loop Aerial), Seitenbestimmungsantenne (Sense Aerial), Empfänger, Bedienteil und Anzeigegerät."),
      ("table_row", "Bodenkomponenten", "Sender + Sendeantenne + Überwachungsanlage"),
      ("table_row", "Bordkomponenten", "Loop-Antenne + Sense-Antenne + Empfänger + ADF-Bedienteil + Anzeigegerät"),
      ("heading", "4.3.3 Anzeigegeräte", None),
      ("diagram", SVG_NDB_ADF, "Abb. – RBI und RMI: Anzeigegeräte für ADF/NDB"),
      ("text", "Drei Anzeigegeräte sind für NDB-Navigation relevant: Das RBI (Relative Bearing Indicator) hat eine starre Kursrose, 0° entspricht der Flugzeuglängsachse. Beim MDI (Moving Dial Indicator) ist die Kompassrose drehbar und kann auf den missweisenden Steuerkurs eingestellt werden. Das RMI (Radio Magnetic Indicator) führt die Kursrose automatisch nach – an der Nadelspitze kann das QDM direkt abgelesen werden."),
      ("heading", "4.3.4 Fehler und Genauigkeit", None),
      ("text", "Das NDB ist die fehleranfälligste Funknavigationsanlage. Der Gesamtfehler beträgt ca. ±5°. Wichtige Fehlerquellen:"),
      ("table_row", "Ausbreitungsfehler / Fading", "Überlagerung Raum- und Bodenwellen; besonders zur Dämmerung"),
      ("table_row", "Küsteneffekt (Shoreline Effect)", "Brechung beim Übergang Land/Wasser; unter 6.000 ft und < 60° Winkel"),
      ("table_row", "Bergeffekt (Mountain Effect)", "Reflexion und Beugung an Bergkanten → falsche Anzeige"),
      ("table_row", "Quadrantal Error", "Reflexion an Flugzeugteilen bei 45°/135°/225°/315°; durch Funkbeschickung kompensiert"),
      ("table_row", "Dip Error", "In Kurven unzuverlässig; nach Horizontalflug wieder korrekt"),
      ("heading", "4.3.5 Navigationsverfahren", None),
      ("text", "Homing: Die Nadelspitze des RBI auf 000° halten (RMI: Nadel unter Kursmarke). Das Flugzeug fliegt direkt auf das NDB zu, wird aber bei Wind zur Hundekurve gezwungen. Stehende Peilung: Durch Anlegen eines Windvorhalte-Winkels (WCA) wird sichergestellt, dass das RB konstant bleibt – der Pilot fliegt auf einem geraden Kurs zur Station. Kursflug (Tracking): Das QDM als Führungsgröße für einen geraden Kurs auf das NDB zu."),
      ("focus", "RBI/MDI/RMI unterscheiden; Homing vs. stehende Peilung; Fehlerquellen NDB (±5°)"),
    ],
    "quiz": [
      {"q": "Was zeigt der RBI beim NDB-Betrieb?", "options": ["Magnetkurs zum NDB", "Relatives Bearing (Winkel zwischen Längsachse und NDB-Linie)", "VOR-Radial", "Entfernung in NM"], "answer": 1, "explanation": "RBI = Relative Bearing Indicator; starre Kursrose, 0° = Flugzeuglängsachse."},
      {"q": "Was ist 'Homing' beim NDB-Anflug?", "options": ["Gerader Kurs trotz Wind", "RBI-Nadel auf 000° halten → direkt auf NDB", "Kreuzpeilung zweier NDBs", "Konstanter Radius um NDB"], "answer": 1, "explanation": "Homing: Nadelspitze auf 000° halten. Bei Wind entsteht eine Hundekurve."},
      {"q": "Vorteil des RMI gegenüber dem RBI?", "options": ["Größere Reichweite", "QDM direkt an Nadelspitze ablesbar – keine Rechenarbeit", "Empfang auch im UHF-Bereich", "Günstiger"], "answer": 1, "explanation": "RMI führt Kursrose automatisch nach → QDM direkt an Nadelspitze ablesbar."},
      {"q": "Warum hat das NDB größere Fehler als das VOR?", "options": ["Niedrigere Sendeleistung", "LF/MF-Bereich: Boden- und Raumwellen, Fading, Küsteneffekt, Quadrantal Error", "ADF-Geräte ungenauer", "Keine Morsekennung"], "answer": 1, "explanation": "NDB im LF/MF-Bereich = Boden- und Raumwellen → Fading, Küsteneffekt, elektrische Störungen. Gesamtfehler ±5°."},
      {"q": "Was passiert beim NDB-Überflug mit der ADF-Nadel?", "options": ["Nadel zeigt konstant 000°", "Nadel wird unruhig, dreht beim Überflug ca. 180°", "Nadel stoppt", "Keine Reaktion"], "answer": 1, "explanation": "Kurz vor Überflug werden Ausschläge unruhiger; beim Überflug dreht die Nadel rasch um ca. 180°."},
      {"q": "Was ist der Quadrantal Error beim NDB/ADF?", "options": ["Ionosphärischer Fehler", "Konstruktiver Empfangsfehler durch Reflexion an Rumpf/Tragflächen bei 45°/135°/225°/315°", "Störung durch Hochspannungsleitungen", "Fehler durch Übergeschwindigkeit"], "answer": 1, "explanation": "Quadrantal Error: Reflexion an Flugzeugteilen bei bestimmten Einfallswinkeln. Wird durch Funkbeschickung kompensiert."},
    ]
  },
  {
    "id": "nav-vor",
    "title": "UKW-Drehfunkfeuer (VOR)",
    "exam_relevant": 1,
    "sort_order": 6,
    "sections": [
      ("heading", "4.4 UKW-Drehfunkfeuer (VOR)", "Genaueste konventionelle Funknavigationsanlage"),
      ("text", "Das VOR (VHF Omnidirectional Radio Range) wird aufgrund seiner höheren Genauigkeit und komfortableren Anzeige im Cockpit von vielen Piloten als Navigationshilfe bevorzugt. Es arbeitet nach dem Prinzip der Eigenpeilung und sendet im VHF-Bereich (108–117,975 MHz) richtungsabhängige Funkwellen aus. 360 Radiale werden definiert, die als QDR (missweisende Peilung von der Station) angegeben werden."),
      ("heading", "4.4.1 Funktionsprinzip", None),
      ("text", "Das Funktionsprinzip ähnelt einem Turm, der zwei verschiedene Lichtsignale aussendet: ein konstantes Bezugssignal und ein umlaufendes Signal. Der Bordempfänger misst die Phasendifferenz beider Signale – diese entspricht dem Radial, auf dem sich das Flugzeug befindet. Beim CVOR wird das Umlaufsignal durch eine physisch rotierende Antenne erzeugt. Das Doppler-VOR (DVOR) nutzt 40 Außenantennen und ist weniger anfällig für topographische Fehler."),
      ("heading", "4.4.3 Anzeigegeräte", None),
      ("diagram", SVG_VOR_CDI, "Abb. – CDI-Anzeige: Interpretation und Kurskorrekturen"),
      ("text", "Das CDI (Course Deviation Indicator) ist das häufigste VOR-Anzeigegerät. Über den OBS (Omni Bearing Selector) wird ein gewünschter Kurs eingestellt. Die senkrechte Kursablagenadel zeigt die Ablage vom gewählten Radial an. Ein Vollausschlag entspricht 10° Ablage oder mehr; jeder Dot entspricht 2° Ablage. Die TO/FROM-Richtungsanzeige gibt an, ob der eingestellte Kurs zur Station führt (TO) oder von ihr weg (FROM)."),
      ("warning", "CDI = Kommandogerät: Korrekturen IMMER zur Nadel hin! Nadel rechts → rechts fliegen. Nadel links → links fliegen."),
      ("heading", "4.4.4 Fehler und Genauigkeit", None),
      ("text", "Schweigekegel (Cone of Silence): Ein kegelförmiger Bereich von ca. 40° direkt über der Station, in dem kein verlässlicher VOR-Empfang möglich ist. Die Warnflagge erscheint, und beim Überflug wechselt die TO/FROM-Anzeige. VOR-Gesamtfehler: ±1° bis ±2° (deutlich besser als NDB ±5°). VOR-Reichweite ca. 200 NM bei Strecken-VORs."),
      ("heading", "4.4.5 Navigationsverfahren", None),
      ("text", "Kursflug (Tracking): CDI-Nadel in der Mitte halten. Bei Ablage durch Wind: Korrektur zur Nadel hin, dann Vorhaltewinkel anlegen. Kreuzpeilung mit zwei VORs ermöglicht exakte Positionsbestimmung. Anschneiden (Interception): Einen Kurs zu einem oder von einem VOR schnellstmöglich anschneiden. Anschneidewinkel wird aus Differenz IST-Kurs und SOLL-Kurs bestimmt (max. 90°, typisch 45°)."),
      ("focus", "CDI als Kommandogerät; TO/FROM-Interpretation; Schweigekegel; Kursflug Tracking; Kreuzpeilung"),
    ],
    "quiz": [
      {"q": "Was ist ein VOR-Radial?", "options": ["Entfernung in NM", "Missweisender Kurs VON der Station (QDR)", "Steuerkurs zum VOR", "Frequenz in MHz"], "answer": 1, "explanation": "Radial = missweisender Kurs von der Station (QDR). 360 Radiale definieren Himmelsrichtungen um das VOR."},
      {"q": "CDI-Nadel rechts ausgeschlagen – was tun?", "options": ["Links fliegen", "Rechts fliegen (zur Nadel hin)", "Höhe ändern", "Frequenz wechseln"], "answer": 1, "explanation": "CDI = Kommandogerät: immer zur Nadel hin korrigieren."},
      {"q": "Was bedeutet die FROM-Anzeige (FR)?", "options": ["Flugzeug bewegt sich auf Station zu", "Eingestellter Kurs führt von der Station weg", "VOR ausgefallen", "Im Schweigekegel"], "answer": 1, "explanation": "FROM = eingestellter Kurs führt von der Station weg. TO = Kurs zur Station."},
      {"q": "Was passiert beim VOR-Überflug?", "options": ["Anzeige stabil", "Warnflagge erscheint kurz, TO wechselt zu FROM", "Nadel friert ein", "VOR schaltet ab"], "answer": 1, "explanation": "Im Schweigekegel (Cone of Silence) erscheint die Warnflagge, dann wechselt TO zu FROM."},
      {"q": "Was ist der Schweigekegel (Cone of Silence)?", "options": ["Frequenzbereich ohne Signal", "Kegelförmiger Bereich ca. 40° über der Station – kein verlässlicher VOR-Empfang", "Mindestflughöhe", "Schutzzone am Boden"], "answer": 1, "explanation": "Direkt über der VOR-Station (ca. 40° Kegelwinkel) – Warnflagge erscheint, Navigation nicht möglich."},
      {"q": "Unterschied CVOR vs. DVOR?", "options": ["DVOR ist digital", "CVOR: rotierende Antenne/anfällig für Topographie; DVOR: 40 Außenantennen/Doppler-Effekt/genauer", "Unterschiedliche Frequenzbereiche", "Kein Unterschied"], "answer": 1, "explanation": "DVOR nutzt 40 Außenantennen und den Doppler-Effekt – deutlich weniger topographische Fehler als CVOR."},
    ]
  },
  {
    "id": "nav-dme",
    "title": "Entfernungsmessgerät (DME)",
    "exam_relevant": 1,
    "sort_order": 7,
    "sections": [
      ("heading", "4.5 Entfernungsmessgerät (DME)", "Distanzmessung per Radarprinzip"),
      ("text", "Das DME (Distance Measuring Equipment) übermittelt eine Entfernungsangabe zur Station. Das Bordgerät sendet Abfrageimpulse aus, die von der DME-Bodenstation nach einer Verzögerung von 50 μs beantwortet werden. Aus der Impulslaufzeit wird die Entfernung berechnet. Das DME arbeitet im UHF-Bereich (960–1215 MHz) und ist den VOR-Frequenzen durch ein festes Pairing-Schema zugeordnet."),
      ("heading", "4.5.1 Funktionsprinzip", None),
      ("text", "Das Bordgerät sendet Abfrageimpulse und empfängt die Antwortimpulse der Bodenstation. Aus der Laufzeitdifferenz (abzüglich der bekannten 50 μs Verzögerung) wird die Entfernung berechnet. Damit keine fremden Bordanlagen ausgewertet werden, generiert jedes DME-Gerät an Bord einen individuellen Impulsabstand."),
      ("table_row", "Frequenzbereich Bord", "1025–1150 MHz (Abfrage)"),
      ("table_row", "Frequenzbereich Boden", "962–1213 MHz (Antwort)"),
      ("table_row", "Gemessene Größe", "Schrägentfernung (Slant Range) – nicht Bodenentfernung!"),
      ("table_row", "Morsekennung", "3 Buchstaben, höhere Frequenz als VOR"),
      ("heading", "4.5.2 Schräg- vs. Bodenentfernung", None),
      ("text", "Das DME misst die Schrägentfernung (Slant Range) – die direkte Entfernung zwischen Flugzeug und Station. Bei Überflug zeigt das DME die Flughöhe in NM an (zeigt nie den Wert Null). Bei GNSS-Systemen wird die tatsächliche Bodenentfernung angegeben, weshalb bei Annäherung zunehmend Unterschiede auftreten."),
      ("heading", "4.5.3 Navigationsverfahren", None),
      ("text", "Das DME dient als Unterstützung oder ist elementarer Bestandteil vieler Navigationsverfahren. In Kombination mit einem VOR oder NDB ermöglicht es eine eindeutige Positionsbestimmung. Zusätzlich können Groundspeed und verbleibende Zeit zur Station angezeigt werden."),
      ("focus", "DME misst Schrägentfernung, nicht Bodenentfernung; automatische Mitabstimmung mit VOR; VOR/DME-Kombination für eindeutige Position"),
    ],
    "quiz": [
      {"q": "Was misst das DME?", "options": ["Magnetkurs zur Station", "Schrägentfernung (Slant Range)", "Bodenentfernung", "Höhe über Station"], "answer": 1, "explanation": "DME misst Slant Range – direkter Abstand Flugzeug–Station. Beim Überflug zeigt DME die Höhe in NM."},
      {"q": "In welchem Frequenzbereich arbeitet das DME?", "options": ["VHF (108-118 MHz)", "LF/MF", "UHF (960-1215 MHz)", "HF (3-30 MHz)"], "answer": 2, "explanation": "DME arbeitet im UHF-Bereich. Die Frequenzeinstellung erfolgt zusammen mit dem VOR."},
      {"q": "Warum stimmt das DME automatisch mit, wenn das VOR eingestellt wird?", "options": ["Gleiches Frequenzband", "Festes Channel-Pairing: DME-Frequenzen den VOR-Frequenzen fest zugeordnet", "Nur neuere Geräte", "Muss immer separat eingestellt werden"], "answer": 1, "explanation": "Channel-Pairing: Beim Einstellen der VOR-Frequenz wird automatisch die zugeordnete DME-Frequenz gerastet."},
      {"q": "Was ermöglicht VOR/DME kombiniert?", "options": ["Nur Kurs", "Nur Entfernung", "Eindeutige Position ohne zweite Station", "Windmessung"], "answer": 2, "explanation": "VOR = Richtung (Radial); DME = Entfernung → zusammen eindeutige Positionsbestimmung."},
    ]
  },
  {
    "id": "nav-ssr",
    "title": "Sekundärradar (SSR) und Transponder",
    "exam_relevant": 1,
    "sort_order": 8,
    "sections": [
      ("heading", "4.7 Sekundärradar (SSR)", "Transponder und Identifizierung"),
      ("text", "Das Primärradar kann nur Entfernung und Richtung eines Objektes bestimmen. Beim Sekundärradar (SSR – Secondary Surveillance Radar) werden neben Entfernung und Richtung auch Flughöhe und ein Identifizierungscode übermittelt. Dies erfordert ein bordseitiges Antwortgerät (Transponder), das auf Abfrageimpulse der Bodenanlage reagiert."),
      ("heading", "4.7.1 Funktionsprinzip", None),
      ("text", "Der Bodensender (Interrogator) sendet auf 1.030 MHz kurze elektromagnetische Impulse aus, die vom Transponder empfangen und auf 1.090 MHz beantwortet werden. Auf dem Radarbildschirm werden Luftfahrzeuge, die SSR-Signale empfangen, direkt optisch differenziert und mit Zusatzinformationen dargestellt."),
      ("diagram", SVG_TRANSPONDER, "Abb. – SSR-Prinzip und Transponder-Codes"),
      ("heading", "4.7.2 Bedien- und Anzeigegeräte", None),
      ("text", "Am Bedienteil wird eingestellt, welche Informationen übertragen werden sollen."),
      ("table_row", "OFF", "Transponder ausgeschaltet – vor Anlassen einschalten, nach Abstellen ausschalten"),
      ("table_row", "STBY", "Betriebsbereit, sendet aber noch keine Impulse (z.B. am Boden)"),
      ("table_row", "ON/A (Mode A)", "Überträgt nur den 4-stelligen Code (Squawk)"),
      ("table_row", "ALT/C (Mode C)", "Überträgt Code + intern ermittelte Druckhöhe"),
      ("table_row", "TST", "Selbsttest des Transponders – Testlampe muss aufleuchten"),
      ("table_row", "ID/IDENT", "Zusatzimpuls für 15 s – nur auf ATC-Anweisung!"),
      ("heading", "Wichtige Transponder-Codes", None),
      ("table_row", "Code 7000", "Einstellung für VFR-Verkehr (Standard in Deutschland)"),
      ("table_row", "Code 7500", "Entführung / Unerlaubter Eingriff (Hijacking)"),
      ("table_row", "Code 7600", "Funkausfall (Radio Failure)"),
      ("table_row", "Code 7700", "Notfall (Emergency / MAYDAY)"),
      ("heading", "4.7 Mode S", None),
      ("text", "Die meisten modernen Luftfahrzeuge sind mit einem Mode-S-Transponder ausgestattet. Dieser ermöglicht nicht nur die Übermittlung von Höhe und Code, sondern auch des Eintragungszeichens (Flugnummer) sowie Datalink-Kommunikation direkt über den Transponder."),
      ("heading", "4.7.3 Fehler / Genauigkeit", None),
      ("text", "Fehlerquellen: In Kurvenlagen kann die Antennenpositionierung unter dem Rumpf zu Abschattungen führen. Nebenkeulen (Sidelobes) können zu Fehlidentifizierungen führen. Sehr geringe Entfernung zur Bodenstation kann Transponder auf Nebenkeulen reagieren lassen."),
      ("focus", "Sondercodes 7500/7600/7700 kennen; Mode A vs. C vs. S; IDENT nur auf ATC-Anweisung; Standard VFR = 7000"),
    ],
    "quiz": [
      {"q": "Welchen Code squawkt ein VFR-Pilot standardmäßig (ohne ATC-Anweisung)?", "options": ["7700", "2000", "7000", "1200"], "answer": 2, "explanation": "Standard VFR in Deutschland: Code 7000."},
      {"q": "Code 7700 bedeutet?", "options": ["Funkausfall", "Entführung", "VFR-Standard", "Notfall (MAYDAY)"], "answer": 3, "explanation": "7700 = Notfall (MAYDAY). 7600 = Funkausfall. 7500 = Entführung."},
      {"q": "Unterschied Mode A und Mode C?", "options": ["Mode A überträgt Höhe, Mode C nur Code", "Mode A: nur Code; Mode C: Code + Druckhöhe", "Identisch", "Mode C veraltet"], "answer": 1, "explanation": "Mode A (ON/A): nur Squawk. Mode C (ALT/C): Squawk + Druckhöhe."},
      {"q": "Wann IDENT/ID betätigen?", "options": ["Immer beim Start", "Nur auf ATC-Anweisung – 15 s extra Aufleuchten auf Radarschirm", "Bei Einschalten", "Bei Funkausfall"], "answer": 1, "explanation": "IDENT nur auf explizite ATC-Anweisung – das Flugzeug leuchtet ca. 15 s auf dem Radarschirm auf."},
      {"q": "Interrogator-Frequenz und Transponder-Antwortfrequenz?", "options": ["1090 MHz / 1030 MHz", "1030 MHz / 1090 MHz", "Beide 1030 MHz", "108 MHz / 118 MHz"], "answer": 1, "explanation": "Interrogator sendet 1.030 MHz; Transponder antwortet auf 1.090 MHz."},
    ]
  },
  {
    "id": "nav-gnss",
    "title": "Satellitennavigation (GNSS/GPS)",
    "exam_relevant": 1,
    "sort_order": 9,
    "sections": [
      ("heading", "4.8 Satellitennavigation (GNSS)", "GPS, GALILEO und GLONASS"),
      ("text", "Das Aufkommen von Satellitennavigation (GNSS – Global Navigation Satellite System) hat die Navigationsverfahren revolutioniert. Es bietet die Möglichkeit, ohne bodengestützte Navigationshilfen sehr zuverlässig und nahezu wetterunabhängig an jedem Punkt der Erde Position, Flughöhe, Geschwindigkeit und Zeit zu ermitteln. Wichtigste Systeme: GPS (USA), GALILEO (EU), GLONASS (Russland)."),
      ("diagram", SVG_GPS, "Abb. – GPS-System: Segmente, Satelliten und Funktionsprinzip"),
      ("heading", "4.8.1 Funktionsprinzip", None),
      ("text", "Das GPS-Gerät ermittelt die genaue Position anhand der Laufzeitmessung elektromagnetischer Signale zu bekannten Satelliten. Die Satelliten senden auf zwei Frequenzen: L1 (1575,42 MHz) für zivile Nutzer und L2 (1227,60 MHz) nur für Militär. Jeder Satellit hat eine eindeutige PRN-Code-Kennung."),
      ("text", "Für eine eindeutige und bestätigte dreidimensionale Positionsbestimmung werden mindestens 4 Satelliten benötigt. Mit einem fünften Satelliten kann eine Integritätsprüfung (RAIM) durchgeführt werden."),
      ("heading", "4.8.1 Segmente des GPS-Systems", None),
      ("table_row", "Raumsegment", "30 Satelliten, 6 Umlaufbahnen, 20.183 km Höhe, Umlaufzeit ~12 h"),
      ("table_row", "Bodensegment", "Master Control Station (Colorado) + 4 Monitorstationen + 6 NGA-Stationen"),
      ("table_row", "Bordsegment", "Empfangsantenne + Empfänger + Anzeige- und Bediengerät"),
      ("heading", "4.8.2 Fehler / Genauigkeit", None),
      ("text", "Selective Availability (SA): Die US-Regierung kann als Eigentümerin die Genauigkeit jederzeit herabsetzen oder das System abschalten – besonders in Krisenzeiten. Genauigkeit ohne SA: 70–100 m. Mit Differential GPS (DGPS): ±1–5 m. GDOP (Geometric Dilution of Precision): Maß für Qualitätseinbußen durch Satellitenanordnung. RAIM (Receiver Autonomous Integrity Monitoring): Autonome Prüfung im Empfänger; benötigt 5–6 Satellitensignale."),
      ("warning", "GNSS-Geräte die NICHT speziell für die Luftfahrt zertifiziert sind, dürfen NICHT zur Navigation verwendet werden. Sie haben oft weder ausreichende Genauigkeit noch eine aktuelle Datenbank."),
      ("heading", "4.8.3 Navigation mit GPS", None),
      ("text", "Alle GPS-Daten und Navigationskarten basieren auf dem WGS84-Referenzellipsoid. GPS-Empfänger und verwendetes Kartenmaterial müssen auf dasselbe Modell eingestellt sein. Bei der Navigation ist darauf zu achten, dass die Kursablage (CDI-Nadel) sich auf die seitliche Entfernung in NM bezieht – nicht auf eine Ablage in Grad."),
      ("focus", "Min. 4 Satelliten für 3D-Position; RAIM-Funktion; WGS84; Selective Availability; GNSS als Ergänzung, nicht Ersatz klassischer Navigation"),
    ],
    "quiz": [
      {"q": "Wie viele Satelliten für GPS-3D-Positionsbestimmung?", "options": ["Zwei", "Drei", "Vier", "Sechs"], "answer": 2, "explanation": "Mindestens 4 Satelliten für eindeutige 3D-Positionsbestimmung (Zeit eliminieren)."},
      {"q": "Was ist RAIM?", "options": ["Höhenmessung", "Receiver Autonomous Integrity Monitoring – prüft GPS-Integrität; braucht 5-6 Satelliten", "Radar und GPS", "Reichweitenanzeige"], "answer": 1, "explanation": "RAIM erkennt fehlerhafte Satelliten. Benötigt 5 (Erkennung) bzw. 6 (Isolierung) Satelliten."},
      {"q": "Was ist Selective Availability (SA)?", "options": ["Nur bestimmte Satelliten nutzen", "US-Möglichkeit, GPS-Genauigkeit jederzeit zu reduzieren/abzuschalten", "Automatische Kurskorrektur", "Reichweite des Signals"], "answer": 1, "explanation": "SA = US-Militär kann als GPS-Betreiber die zivile Nutzung jederzeit einschränken."},
      {"q": "Auf welchem Erdmodell basieren GPS-Daten?", "options": ["Gauß-Krüger", "WGS84", "ETRS89", "Jedes Land eigenes Modell"], "answer": 1, "explanation": "Alle GPS-Berechnungen und Navigationskarten basieren auf WGS84 (World Geodetic System 1984)."},
      {"q": "Was beschreibt der GDOP?", "options": ["Maximale GPS-Reichweite", "Einfluss der Satellitenanordnung auf Messgenauigkeit", "Anzahl verfügbarer Satelliten", "Atmosphärischer Fehler"], "answer": 1, "explanation": "GDOP = Geometric Dilution of Precision: schlechte Satellitengeometrie (zu nah beieinander) = schlechtere Genauigkeit."},
    ]
  }
]

# ─── Insert into DB ─────────────────────────────────────────────────────────

def insert_chapters():
    conn = sqlite3.connect(DB)
    cur = conn.cursor()
    
    for ch_data in CHAPTERS:
        ch_id = ch_data["id"]
        
        # Check if chapter already exists
        existing = cur.execute("SELECT id FROM learn_chapters WHERE id=?", (ch_id,)).fetchone()
        if existing:
            print(f"  Updating existing: {ch_id}")
            cur.execute("DELETE FROM learn_sections WHERE chapter_id=?", (ch_id,))
            cur.execute("DELETE FROM learn_quiz WHERE chapter_id=?", (ch_id,))
        else:
            print(f"  Inserting new: {ch_id}")
            cur.execute("""INSERT INTO learn_chapters (id, subject_id, title, sort_order, exam_relevant)
                           VALUES (?, 'nav', ?, ?, ?)""",
                        (ch_id, ch_data["title"], ch_data["sort_order"], ch_data["exam_relevant"]))
        
        # Insert sections
        for idx, sec in enumerate(ch_data["sections"]):
            typ = sec[0]
            cont = sec[1]
            extra = sec[2] if len(sec) > 2 else None
            cur.execute("INSERT INTO learn_sections (chapter_id, type, content, extra, sort_order) VALUES (?,?,?,?,?)",
                        (ch_id, typ, cont, extra, idx))
        
        # Insert quiz
        for idx, q in enumerate(ch_data["quiz"]):
            cur.execute("""INSERT INTO learn_quiz (chapter_id, question, options, answer, explanation, is_official, sort_order)
                           VALUES (?,?,?,?,?,0,?)""",
                        (ch_id, q["q"], json.dumps(q["options"], ensure_ascii=False), q["answer"], q["explanation"], idx))
    
    conn.commit()
    conn.close()
    print("Done!")

insert_chapters()

# Update nav subject overview
conn = sqlite3.connect(DB)
cur = conn.cursor()
cur.execute("""UPDATE learn_subjects SET 
    overview='Navigation verbindet Karte, Kurs, Zeit, Wind und moderne Funknavigation. Das Fach umfasst klassische Navigationsverfahren, das Winddreieck und die 1:60-Regel sowie alle wichtigen Funknavigationssysteme: VDF, NDB/ADF, VOR, DME, SSR/Transponder und GNSS/GPS.'
    WHERE id='nav'""")
conn.commit()

total_nav = cur.execute("SELECT COUNT(*) FROM learn_chapters WHERE subject_id='nav'").fetchone()[0]
total_q = cur.execute("SELECT COUNT(*) FROM learn_quiz WHERE chapter_id LIKE 'nav-%'").fetchone()[0]
print(f"Nav chapters: {total_nav}, Nav quiz questions: {total_q}")
conn.close()
