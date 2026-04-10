#!/usr/bin/env python3
"""
Comprehensive Navigation content import – based on Aircademy PPL(A)
Navigation textbook (Advanced PPL-Guide Band 3).
Covers: Kap. 1 Die Erde | Kap. 2 Kartenkunde | Kap. 3 Praktische Navigation
"""
import sqlite3, json, os

DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), "takvim.db")

# ═══════════════════════════════════════════════════════════════════════════
#  SVG DIAGRAMS
# ═══════════════════════════════════════════════════════════════════════════

SVG_ERDE_KOORDINATEN = """<svg viewBox="0 0 520 280" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:520px;font-family:system-ui,sans-serif">
  <defs>
    <radialGradient id="erdg" cx="40%" cy="35%">
      <stop offset="0%" stop-color="#2563eb" stop-opacity="0.9"/>
      <stop offset="60%" stop-color="#1d4ed8"/>
      <stop offset="100%" stop-color="#1e3a8a"/>
    </radialGradient>
  </defs>
  <rect width="520" height="280" fill="#0f172a" rx="12"/>
  <text x="260" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Koordinatensystem der Erde</text>
  <!-- Globe -->
  <ellipse cx="140" cy="150" rx="95" ry="110" fill="url(#erdg)" stroke="#3b82f6" stroke-width="1.5"/>
  <!-- Rotation axis -->
  <line x1="140" y1="35" x2="140" y2="265" stroke="#fbbf24" stroke-width="1.5" stroke-dasharray="5,3"/>
  <text x="150" y="32" fill="#fbbf24" font-size="10">Drehachse</text>
  <!-- Equator -->
  <ellipse cx="140" cy="150" rx="95" ry="18" fill="none" stroke="#ef4444" stroke-width="2"/>
  <text x="240" y="154" fill="#ef4444" font-size="11" font-weight="bold">Äquator (0°)</text>
  <!-- Latitude lines -->
  <ellipse cx="140" cy="117" rx="82" ry="15" fill="none" stroke="#60a5fa" stroke-width="1" stroke-dasharray="4,3"/>
  <text x="227" y="121" fill="#60a5fa" font-size="10">30°N</text>
  <ellipse cx="140" cy="88" rx="60" ry="11" fill="none" stroke="#60a5fa" stroke-width="1" stroke-dasharray="4,3"/>
  <text x="205" y="92" fill="#60a5fa" font-size="10">60°N</text>
  <ellipse cx="140" cy="183" rx="82" ry="15" fill="none" stroke="#60a5fa" stroke-width="1" stroke-dasharray="4,3"/>
  <text x="227" y="187" fill="#60a5fa" font-size="10">30°S</text>
  <!-- Meridian -->
  <ellipse cx="140" cy="150" rx="30" ry="110" fill="none" stroke="#a78bfa" stroke-width="1.5" stroke-dasharray="4,2"/>
  <!-- Poles -->
  <circle cx="140" cy="40" r="4" fill="#fbbf24"/>
  <text x="148" y="44" fill="#fbbf24" font-size="10">N-Pol (90°N)</text>
  <circle cx="140" cy="260" r="4" fill="#fbbf24"/>
  <text x="148" y="264" fill="#fbbf24" font-size="10">S-Pol (90°S)</text>
  <!-- Legend box -->
  <rect x="305" y="40" width="205" height="185" rx="8" fill="#1e293b" stroke="#334155"/>
  <text x="408" y="60" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Koordinaten</text>
  <!-- Latitude -->
  <rect x="315" y="70" width="185" height="45" rx="6" fill="#1e3a5f" stroke="#3b82f6"/>
  <text x="325" y="87" fill="#93c5fd" font-size="11" font-weight="bold">Breitenkreise (φ)</text>
  <text x="325" y="102" fill="#cbd5e1" font-size="10">• parallel zum Äquator</text>
  <text x="325" y="113" fill="#cbd5e1" font-size="10">• Abstand: immer 60 NM / 1°</text>
  <!-- Longitude -->
  <rect x="315" y="122" width="185" height="45" rx="6" fill="#2d1f5e" stroke="#7c3aed"/>
  <text x="325" y="139" fill="#c4b5fd" font-size="11" font-weight="bold">Längenkreise / Meridiane (λ)</text>
  <text x="325" y="154" fill="#cbd5e1" font-size="10">• laufen an Polen zusammen</text>
  <text x="325" y="165" fill="#cbd5e1" font-size="10">• 0° = Greenwich-Meridian</text>
  <!-- Key distances -->
  <rect x="315" y="174" width="185" height="42" rx="6" fill="#1a2e1a" stroke="#22c55e"/>
  <text x="325" y="191" fill="#86efac" font-size="11" font-weight="bold">Abstände</text>
  <text x="325" y="205" fill="#cbd5e1" font-size="10">1° Breite = 60 NM = konst.</text>
  <text x="325" y="216" fill="#cbd5e1" font-size="10">1° Länge = 60 NM am Äquator</text>
</svg>"""

SVG_GROSSKREIS_LOXODROME = """<svg viewBox="0 0 540 240" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="240" fill="#0f172a" rx="12"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Orthodrome (Großkreis) vs. Loxodrome (Kursgleiche)</text>
  <!-- Left: Lambert map showing curves -->
  <rect x="10" y="35" width="240" height="190" rx="8" fill="#1e293b" stroke="#334155"/>
  <text x="130" y="53" fill="#94a3b8" font-size="10" text-anchor="middle">Lambert-Karte</text>
  <!-- Grid lines -->
  <line x1="10" y1="90" x2="250" y2="90" stroke="#1e3a5f" stroke-width="0.8"/>
  <line x1="10" y1="130" x2="250" y2="130" stroke="#1e3a5f" stroke-width="0.8"/>
  <line x1="10" y1="170" x2="250" y2="170" stroke="#1e3a5f" stroke-width="0.8"/>
  <line x1="60" y1="35" x2="60" y2="225" stroke="#1e3a5f" stroke-width="0.8"/>
  <line x1="130" y1="35" x2="130" y2="225" stroke="#1e3a5f" stroke-width="0.8"/>
  <line x1="200" y1="35" x2="200" y2="225" stroke="#1e3a5f" stroke-width="0.8"/>
  <!-- Orthodrome = gerade Linie on Lambert -->
  <line x1="40" y1="195" x2="225" y2="65" stroke="#22c55e" stroke-width="2.5"/>
  <text x="105" y="148" fill="#22c55e" font-size="11" font-weight="bold" transform="rotate(-30,105,148)">Orthodrome</text>
  <!-- Loxodrome = curved on Lambert -->
  <path d="M40 195 Q100 155 155 125 Q190 108 225 65" stroke="#f59e0b" stroke-width="2" fill="none" stroke-dasharray="6,3"/>
  <text x="195" y="98" fill="#f59e0b" font-size="10">Loxodrome</text>
  <!-- Points -->
  <circle cx="40" cy="195" r="4" fill="white"/>
  <text x="27" y="208" fill="#94a3b8" font-size="9">Start</text>
  <circle cx="225" cy="65" r="4" fill="white"/>
  <text x="219" y="60" fill="#94a3b8" font-size="9">Ziel</text>
  <!-- Right: Explanation -->
  <rect x="265" y="35" width="265" height="190" rx="8" fill="#1e293b" stroke="#334155"/>
  <text x="398" y="57" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Eigenschaften</text>
  <!-- Orthodrome box -->
  <rect x="275" y="65" width="245" height="82" rx="6" fill="#1a2e1a" stroke="#22c55e"/>
  <text x="285" y="82" fill="#22c55e" font-size="11" font-weight="bold">🟢 Orthodrome (Großkreis)</text>
  <text x="285" y="97" fill="#cbd5e1" font-size="10">• Kürzeste Verbindung auf der Erde</text>
  <text x="285" y="111" fill="#cbd5e1" font-size="10">• Mittelpunkt = Erdmittelpunkt</text>
  <text x="285" y="125" fill="#cbd5e1" font-size="10">• Kurs ändert sich ständig</text>
  <text x="285" y="139" fill="#86efac" font-size="10" font-weight="bold">• Auf Lambert = gerade Linie ✓</text>
  <!-- Loxodrome box -->
  <rect x="275" y="155" width="245" height="62" rx="6" fill="#2d1f00" stroke="#f59e0b"/>
  <text x="285" y="172" fill="#fbbf24" font-size="11" font-weight="bold">🟡 Loxodrome (Kursgleiche)</text>
  <text x="285" y="187" fill="#cbd5e1" font-size="10">• Schneidet jeden Meridian gleich</text>
  <text x="285" y="201" fill="#cbd5e1" font-size="10">• Kurs bleibt konstant → einfacher</text>
  <text x="285" y="215" fill="#fcd34d" font-size="10" font-weight="bold">• Bis 200 NM: Unterschied gering</text>
</svg>"""

SVG_NORD_VARIATION_DEVIATION = """<svg viewBox="0 0 540 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="260" fill="#0f172a" rx="12"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Geografisch Nord · Magnetisch Nord · Kompass Nord</text>
  <!-- Central compass illustration -->
  <circle cx="185" cy="145" r="80" fill="#1e293b" stroke="#475569" stroke-width="2"/>
  <!-- TN arrow (true north) -->
  <line x1="185" y1="145" x2="190" y2="68" stroke="#ef4444" stroke-width="3" marker-end="url(#arrowTN)"/>
  <defs>
    <marker id="arrowTN" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#ef4444"/>
    </marker>
    <marker id="arrowMN" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#3b82f6"/>
    </marker>
    <marker id="arrowCN" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,0 L8,4 L0,8 Z" fill="#22c55e"/>
    </marker>
  </defs>
  <!-- MN arrow (magnetic north) - slightly tilted -->
  <line x1="185" y1="145" x2="198" y2="68" stroke="#3b82f6" stroke-width="3" marker-end="url(#arrowMN)"/>
  <!-- CN arrow (compass north) - more tilted -->
  <line x1="185" y1="145" x2="207" y2="70" stroke="#22c55e" stroke-width="3" marker-end="url(#arrowCN)"/>
  <!-- Labels -->
  <text x="178" y="62" fill="#ef4444" font-size="11" font-weight="bold">TN</text>
  <text x="199" y="62" fill="#3b82f6" font-size="11" font-weight="bold">MN</text>
  <text x="210" y="66" fill="#22c55e" font-size="11" font-weight="bold">CN</text>
  <!-- Variation arc -->
  <path d="M 185 90 A 55 55 0 0 1 200 89" stroke="#fbbf24" stroke-width="2" fill="none"/>
  <text x="197" y="84" fill="#fbbf24" font-size="10">VAR</text>
  <!-- Deviation arc -->
  <path d="M 185 98 A 47 47 0 0 1 199 97" stroke="#a78bfa" stroke-width="1.5" fill="none" stroke-dasharray="3,2"/>
  <text x="196" y="108" fill="#a78bfa" font-size="10">DEV</text>
  <!-- Compass rose degrees -->
  <text x="182" y="78" fill="#64748b" font-size="9" text-anchor="middle">N</text>
  <text x="250" y="148" fill="#64748b" font-size="9" text-anchor="middle">E</text>
  <text x="182" y="220" fill="#64748b" font-size="9" text-anchor="middle">S</text>
  <text x="115" y="148" fill="#64748b" font-size="9" text-anchor="middle">W</text>
  <!-- Right explanation -->
  <rect x="290" y="35" width="240" height="210" rx="8" fill="#1e293b" stroke="#334155"/>
  <text x="410" y="57" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Kursschema</text>
  <!-- TC row -->
  <rect x="300" y="65" width="220" height="28" rx="5" fill="#2d1a1a" stroke="#ef4444"/>
  <text x="310" y="84" fill="#ef4444" font-weight="bold" font-size="11">TC – True Course</text>
  <text x="505" y="84" fill="#fca5a5" font-size="10" text-anchor="end">Rechtweisend</text>
  <!-- VAR row -->
  <text x="410" y="107" fill="#fbbf24" font-size="18" text-anchor="middle">± VAR</text>
  <!-- MC row -->
  <rect x="300" y="118" width="220" height="28" rx="5" fill="#1a2040" stroke="#3b82f6"/>
  <text x="310" y="137" fill="#3b82f6" font-weight="bold" font-size="11">MC – Magnetic Course</text>
  <text x="505" y="137" fill="#93c5fd" font-size="10" text-anchor="end">Missweisend</text>
  <!-- DEV row -->
  <text x="410" y="159" fill="#a78bfa" font-size="18" text-anchor="middle">± DEV</text>
  <!-- CC row -->
  <rect x="300" y="170" width="220" height="28" rx="5" fill="#1a2e1a" stroke="#22c55e"/>
  <text x="310" y="189" fill="#22c55e" font-weight="bold" font-size="11">CC – Compass Course</text>
  <text x="505" y="189" fill="#86efac" font-size="10" text-anchor="end">Kompasssteuerkurs</text>
  <!-- Formula note -->
  <rect x="300" y="207" width="220" height="30" rx="5" fill="#1a1a2e" stroke="#6366f1"/>
  <text x="410" y="224" fill="#a5b4fc" font-size="11" text-anchor="middle" font-weight="bold">TC - VAR - DEV = CC</text>
</svg>"""

SVG_ZEITRECHNUNG = """<svg viewBox="0 0 540 240" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="240" fill="#0f172a" rx="12"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Zeitsysteme in der Luftfahrt</text>
  <!-- Sun at top center -->
  <circle cx="270" cy="55" r="18" fill="#fbbf24" opacity="0.9"/>
  <text x="270" y="60" fill="#7c3a00" font-size="11" font-weight="bold" text-anchor="middle">☀</text>
  <text x="270" y="88" fill="#fcd34d" font-size="10" text-anchor="middle">Sonnentag = 24h 0m</text>
  <!-- Earth showing rotation -->
  <circle cx="270" cy="140" r="32" fill="#1d4ed8" stroke="#3b82f6" stroke-width="1.5"/>
  <text x="270" y="145" fill="white" font-size="16" text-anchor="middle">🌍</text>
  <path d="M 258 115 Q 255 108 263 108" stroke="#fbbf24" stroke-width="1.5" fill="none" marker-end="url(#rot)"/>
  <defs>
    <marker id="rot" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#fbbf24"/>
    </marker>
  </defs>
  <text x="245" y="102" fill="#fbbf24" font-size="9">15°/h</text>
  <!-- LMT box -->
  <rect x="15" y="95" width="165" height="75" rx="8" fill="#1e293b" stroke="#6366f1"/>
  <text x="98" y="115" fill="#a5b4fc" font-size="11" font-weight="bold" text-anchor="middle">LMT – Mittlere Ortszeit</text>
  <text x="25" y="132" fill="#cbd5e1" font-size="10">• abhängig von geogr. Länge</text>
  <text x="25" y="147" fill="#cbd5e1" font-size="10">• 1° Länge = 4 Minuten</text>
  <text x="25" y="162" fill="#94a3b8" font-size="9" font-style="italic">östl. Orte → frühere Zeit</text>
  <!-- UTC box -->
  <rect x="360" y="95" width="165" height="75" rx="8" fill="#1e293b" stroke="#22c55e"/>
  <text x="443" y="115" fill="#86efac" font-size="11" font-weight="bold" text-anchor="middle">UTC – Koordinierte Weltzeit</text>
  <text x="370" y="132" fill="#cbd5e1" font-size="10">• LMT des Nullmeridians</text>
  <text x="370" y="147" fill="#cbd5e1" font-size="10">• Atomuhr-basiert</text>
  <text x="370" y="162" fill="#86efac" font-size="9" font-weight="bold">• Standard in der Luftfahrt!</text>
  <!-- Arrows to UTC -->
  <line x1="180" y1="132" x2="248" y2="132" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4,3"/>
  <line x1="292" y1="132" x2="360" y2="132" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="264" y="128" fill="#64748b" font-size="9">GMT</text>
  <!-- Time zone band -->
  <rect x="15" y="195" width="510" height="35" rx="6" fill="#1e293b" stroke="#475569"/>
  <text x="270" y="212" fill="#94a3b8" font-size="10" text-anchor="middle">Zeitzonen: 24 Zonen × 15° Länge | MESZ = UTC+2 | MEZ = UTC+1</text>
  <text x="270" y="226" fill="#64748b" font-size="9" text-anchor="middle">Bürgerl. Dämmerung: Sonne 6° unter Horizont – definiert Nacht in der Luftfahrt</text>
</svg>"""

SVG_PROJEKTIONEN = """<svg viewBox="0 0 540 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="260" fill="#0f172a" rx="12"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Kartenprojektionen in der Luftfahrt</text>
  <!-- Three projection illustrations -->
  <!-- 1. Azimuthal/Polar -->
  <rect x="10" y="35" width="155" height="165" rx="8" fill="#1e293b" stroke="#334155"/>
  <text x="88" y="55" fill="#94a3b8" font-size="10" text-anchor="middle" font-weight="bold">Azimutalprojektion</text>
  <!-- Plane touching pole -->
  <ellipse cx="88" cy="100" rx="55" ry="55" fill="#1d4ed8" opacity="0.4" stroke="#3b82f6"/>
  <rect x="33" y="95" width="110" height="3" fill="#60a5fa"/>
  <text x="88" y="85" fill="#94a3b8" font-size="9" text-anchor="middle">Projektionsebene</text>
  <circle cx="88" cy="97" r="5" fill="#fbbf24"/>
  <text x="88" y="112" fill="#fbbf24" font-size="8" text-anchor="middle">Berührpunkt (Pol)</text>
  <text x="88" y="165" fill="#a78bfa" font-size="9" text-anchor="middle">Polar-</text>
  <text x="88" y="178" fill="#a78bfa" font-size="9" text-anchor="middle">stereographisch</text>
  <text x="88" y="192" fill="#64748b" font-size="8" text-anchor="middle">für 70–90°</text>
  <!-- 2. Cylinder / Mercator -->
  <rect x="175" y="35" width="155" height="165" rx="8" fill="#1e293b" stroke="#334155"/>
  <text x="253" y="55" fill="#94a3b8" font-size="10" text-anchor="middle" font-weight="bold">Mercator-Projektion</text>
  <!-- Cylinder shape -->
  <rect x="218" y="70" width="70" height="90" fill="#1d4ed8" opacity="0.3" stroke="#3b82f6"/>
  <ellipse cx="253" cy="70" rx="35" ry="8" fill="none" stroke="#60a5fa"/>
  <ellipse cx="253" cy="160" rx="35" ry="8" fill="none" stroke="#60a5fa"/>
  <text x="253" y="120" fill="#93c5fd" font-size="8" text-anchor="middle">Zylinder</text>
  <text x="253" y="178" fill="#f59e0b" font-size="9" text-anchor="middle">Loxodrome = Gerade</text>
  <text x="253" y="191" fill="#64748b" font-size="8" text-anchor="middle">für 0–30° Breite</text>
  <!-- 3. Lambert -->
  <rect x="340" y="35" width="190" height="165" rx="8" fill="#1e293b" stroke="#22c55e" stroke-width="1.5"/>
  <text x="435" y="55" fill="#86efac" font-size="10" text-anchor="middle" font-weight="bold">Lambert-Karte ★</text>
  <text x="435" y="68" fill="#64748b" font-size="9" text-anchor="middle">Schnittkegelprojektion</text>
  <!-- Cone cutting globe -->
  <polygon points="435,80 380,180 490,180" fill="#1d4ed8" opacity="0.25" stroke="#3b82f6"/>
  <ellipse cx="435" cy="115" rx="35" ry="8" fill="none" stroke="#22c55e" stroke-width="2" stroke-dasharray="4,2"/>
  <text x="435" y="112" fill="#22c55e" font-size="8" text-anchor="middle">Standard-</text>
  <text x="435" y="122" fill="#22c55e" font-size="8" text-anchor="middle">parallele</text>
  <text x="435" y="185" fill="#86efac" font-size="9" text-anchor="middle">Orthodrome ≈ Gerade</text>
  <text x="435" y="197" fill="#86efac" font-size="9" text-anchor="middle" font-weight="bold">✓ LUFTFAHRT-STANDARD</text>
  <text x="435" y="209" fill="#64748b" font-size="8" text-anchor="middle">für 30–70° Breite</text>
  <!-- Bottom table -->
  <rect x="10" y="210" width="520" height="42" rx="6" fill="#1e293b" stroke="#334155"/>
  <text x="88" y="229" fill="#94a3b8" font-size="10" text-anchor="middle" font-weight="bold">0°–30°</text>
  <text x="88" y="244" fill="#f59e0b" font-size="10" text-anchor="middle">Mercator</text>
  <line x1="175" y1="210" x2="175" y2="252" stroke="#334155"/>
  <text x="253" y="229" fill="#94a3b8" font-size="10" text-anchor="middle" font-weight="bold">30°–70°</text>
  <text x="253" y="244" fill="#22c55e" font-size="10" text-anchor="middle" font-weight="bold">Lambert ★ (Luftfahrt)</text>
  <line x1="340" y1="210" x2="340" y2="252" stroke="#334155"/>
  <text x="435" y="229" fill="#94a3b8" font-size="10" text-anchor="middle" font-weight="bold">70°–90°</text>
  <text x="435" y="244" fill="#a78bfa" font-size="10" text-anchor="middle">Polarstereographisch</text>
</svg>"""

SVG_KOMPASS_FEHLER = """<svg viewBox="0 0 540 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="260" fill="#0f172a" rx="12"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Magnetkompass-Fehler</text>
  <!-- Left: Inklination -->
  <rect x="10" y="35" width="245" height="120" rx="8" fill="#1e293b" stroke="#334155"/>
  <text x="133" y="55" fill="#f59e0b" font-size="11" font-weight="bold" text-anchor="middle">Kompassdrehfehler (Kurvenflug)</text>
  <!-- Compass needle tilted -->
  <circle cx="133" cy="105" r="45" fill="#0f1629" stroke="#3b82f6" stroke-width="1.5"/>
  <!-- Needle -->
  <line x1="133" y1="105" x2="155" y2="72" stroke="#ef4444" stroke-width="3"/>
  <line x1="133" y1="105" x2="111" y2="138" stroke="#94a3b8" stroke-width="2"/>
  <!-- Earth field line (angled) -->
  <line x1="90" y1="68" x2="178" y2="142" stroke="#3b82f6" stroke-width="1.5" stroke-dasharray="4,3"/>
  <text x="185" y="138" fill="#3b82f6" font-size="9">Feldlinie</text>
  <!-- Rule boxes -->
  <rect x="265" y="35" width="265" height="80" rx="8" fill="#2d1a1a" stroke="#ef4444"/>
  <text x="398" y="55" fill="#fca5a5" font-size="11" font-weight="bold" text-anchor="middle">Nordkurse (NH)</text>
  <text x="275" y="73" fill="#cbd5e1" font-size="10">Rechtskurve → Anzeige dreht zuerst LINKS</text>
  <text x="275" y="88" fill="#cbd5e1" font-size="10">→ Kurve vOrher ausleiten (10° früher)</text>
  <text x="275" y="103" fill="#fbbf24" font-size="10" font-weight="bold">Merkregel: N = v O rher</text>
  <rect x="265" y="125" width="265" height="70" rx="8" fill="#1a2e1a" stroke="#22c55e"/>
  <text x="398" y="145" fill="#86efac" font-size="11" font-weight="bold" text-anchor="middle">Südkurse (SH)</text>
  <text x="275" y="163" fill="#cbd5e1" font-size="10">Kurve dreht Anzeige zu gross → erst Ü berkurven</text>
  <text x="275" y="178" fill="#22c55e" font-size="10" font-weight="bold">Merkregel: S = Ü berkurven</text>
  <!-- Acceleration error -->
  <rect x="10" y="165" width="510" height="82" rx="8" fill="#1e293b" stroke="#334155"/>
  <text x="270" y="183" fill="#f59e0b" font-size="11" font-weight="bold" text-anchor="middle">Beschleunigungsfehler (Ost-/West-Kurse)</text>
  <!-- Three compass states -->
  <rect x="20" y="192" width="145" height="48" rx="5" fill="#0f1629" stroke="#3b82f6"/>
  <text x="93" y="208" fill="#93c5fd" font-size="10" text-anchor="middle" font-weight="bold">Beschleunigung auf O/W</text>
  <text x="93" y="224" fill="#cbd5e1" font-size="10" text-anchor="middle">Anzeige dreht → NORDEN</text>
  <text x="93" y="238" fill="#fbbf24" font-size="9" text-anchor="middle">scheinbarer Linksabdrift</text>
  <rect x="185" y="192" width="145" height="48" rx="5" fill="#0f1629" stroke="#ef4444"/>
  <text x="258" y="208" fill="#fca5a5" font-size="10" text-anchor="middle" font-weight="bold">Verzögerung auf O/W</text>
  <text x="258" y="224" fill="#cbd5e1" font-size="10" text-anchor="middle">Anzeige dreht → SÜDEN</text>
  <text x="258" y="238" fill="#fbbf24" font-size="9" text-anchor="middle">scheinbarer Rechtsabdrift</text>
  <rect x="350" y="192" width="160" height="48" rx="5" fill="#1a2e1a" stroke="#22c55e"/>
  <text x="430" y="208" fill="#86efac" font-size="10" text-anchor="middle" font-weight="bold">Auf N/S-Kursen</text>
  <text x="430" y="224" fill="#cbd5e1" font-size="10" text-anchor="middle">kein Beschleunigungsfehler</text>
  <text x="430" y="238" fill="#22c55e" font-size="9" text-anchor="middle">Wirkung = Null</text>
</svg>"""

SVG_WINDDREIECK = """<svg viewBox="0 0 540 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="260" fill="#0f172a" rx="12"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Das Winddreieck</text>
  <!-- Grid background -->
  <defs>
    <pattern id="grid" width="20" height="20" patternUnits="userSpaceOnUse">
      <path d="M 20 0 L 0 0 0 20" fill="none" stroke="#1e293b" stroke-width="0.5"/>
    </pattern>
  </defs>
  <rect x="10" y="35" width="310" height="215" rx="8" fill="url(#grid)" stroke="#334155"/>
  <!-- North arrow -->
  <line x1="35" y1="60" x2="35" y2="40" stroke="white" stroke-width="2" marker-end="url(#arN)"/>
  <defs>
    <marker id="arN" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="white"/>
    </marker>
    <marker id="arTH" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#22c55e"/>
    </marker>
    <marker id="arW" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#60a5fa"/>
    </marker>
    <marker id="arTT" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#f59e0b"/>
    </marker>
  </defs>
  <text x="40" y="44" fill="white" font-size="10">N</text>
  <!-- Start point -->
  <circle cx="100" cy="180" r="5" fill="white"/>
  <text x="88" y="196" fill="#94a3b8" font-size="9">Start</text>
  <!-- True Heading (TH) - aircraft heading vector -->
  <line x1="100" y1="180" x2="195" y2="80" stroke="#22c55e" stroke-width="2.5" marker-end="url(#arTH)" stroke-dasharray="6,3"/>
  <text x="130" y="118" fill="#22c55e" font-size="10" transform="rotate(-45,130,118)">TH / TAS</text>
  <!-- Wind vector -->
  <line x1="195" y1="80" x2="250" y2="120" stroke="#60a5fa" stroke-width="2.5" marker-end="url(#arW)"/>
  <text x="232" y="93" fill="#60a5fa" font-size="10">Wind</text>
  <!-- Track/GS (result) -->
  <line x1="100" y1="180" x2="250" y2="120" stroke="#f59e0b" stroke-width="3" marker-end="url(#arTT)"/>
  <text x="155" y="170" fill="#f59e0b" font-size="11" font-weight="bold">Track / GS</text>
  <!-- End point -->
  <circle cx="250" cy="120" r="5" fill="#f59e0b"/>
  <text x="258" y="124" fill="#94a3b8" font-size="9">Ziel</text>
  <!-- WCA angle arc -->
  <path d="M 130 157 A 35 35 0 0 1 145 148" stroke="#a78bfa" stroke-width="1.5" fill="none"/>
  <text x="135" y="145" fill="#a78bfa" font-size="9">WCA</text>
  <!-- Right explanation -->
  <rect x="330" y="35" width="200" height="215" rx="8" fill="#1e293b" stroke="#334155"/>
  <text x="430" y="57" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Vektoren</text>
  <rect x="340" y="65" width="180" height="34" rx="5" fill="#1a2e1a" stroke="#22c55e"/>
  <text x="350" y="82" fill="#22c55e" font-size="11" font-weight="bold">TH × TAS</text>
  <text x="350" y="94" fill="#cbd5e1" font-size="10">Steuerkurs × Eigengeschw.</text>
  <rect x="340" y="107" width="180" height="34" rx="5" fill="#1e3a5f" stroke="#60a5fa"/>
  <text x="350" y="124" fill="#60a5fa" font-size="11" font-weight="bold">Windvektor</text>
  <text x="350" y="136" fill="#cbd5e1" font-size="10">Richtung und Stärke des Winds</text>
  <rect x="340" y="149" width="180" height="34" rx="5" fill="#2d1f00" stroke="#f59e0b"/>
  <text x="350" y="166" fill="#fbbf24" font-size="11" font-weight="bold">Track × GS</text>
  <text x="350" y="178" fill="#cbd5e1" font-size="10">Tatsächl. Kurs × Grundgeschw.</text>
  <!-- WCA -->
  <rect x="340" y="191" width="180" height="50" rx="5" fill="#2d1a3a" stroke="#a78bfa"/>
  <text x="350" y="208" fill="#c4b5fd" font-size="11" font-weight="bold">WCA – Luvwinkel</text>
  <text x="350" y="223" fill="#cbd5e1" font-size="10">Winkel: TH ↔ Track</text>
  <text x="350" y="236" fill="#cbd5e1" font-size="10">Wind von links → WCA negativ</text>
</svg>"""

SVG_GESCHWINDIGKEITEN = """<svg viewBox="0 0 540 200" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="200" fill="#0f172a" rx="12"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Geschwindigkeiten im Überblick</text>
  <!-- Flow diagram -->
  <rect x="15" y="45" width="95" height="50" rx="8" fill="#1e3a5f" stroke="#3b82f6"/>
  <text x="63" y="67" fill="#93c5fd" font-size="11" font-weight="bold" text-anchor="middle">IAS</text>
  <text x="63" y="82" fill="#60a5fa" font-size="9" text-anchor="middle">Angezeigte</text>
  <text x="63" y="92" fill="#60a5fa" font-size="9" text-anchor="middle">Eigengeschw.</text>
  <!-- Arrow + correction -->
  <line x1="110" y1="70" x2="145" y2="70" stroke="#64748b" stroke-width="1.5"/>
  <text x="127" y="62" fill="#fbbf24" font-size="8" text-anchor="middle">±Instru-</text>
  <text x="127" y="72" fill="#fbbf24" font-size="8" text-anchor="middle">mentenfehler</text>
  <rect x="145" y="45" width="95" height="50" rx="8" fill="#1e3a5f" stroke="#60a5fa"/>
  <text x="193" y="67" fill="#93c5fd" font-size="11" font-weight="bold" text-anchor="middle">CAS</text>
  <text x="193" y="82" fill="#60a5fa" font-size="9" text-anchor="middle">Berichtigte</text>
  <text x="193" y="92" fill="#60a5fa" font-size="9" text-anchor="middle">Eigengeschw.</text>
  <!-- Arrow + density correction -->
  <line x1="240" y1="70" x2="275" y2="70" stroke="#64748b" stroke-width="1.5"/>
  <text x="257" y="62" fill="#22c55e" font-size="8" text-anchor="middle">±Dichte-</text>
  <text x="257" y="72" fill="#22c55e" font-size="8" text-anchor="middle">korrektur</text>
  <rect x="275" y="45" width="95" height="50" rx="8" fill="#1a3a1a" stroke="#22c55e"/>
  <text x="323" y="67" fill="#86efac" font-size="11" font-weight="bold" text-anchor="middle">TAS</text>
  <text x="323" y="82" fill="#86efac" font-size="9" text-anchor="middle">Wahre Eigen-</text>
  <text x="323" y="92" fill="#86efac" font-size="9" text-anchor="middle">geschwindigkeit</text>
  <!-- Arrow + wind -->
  <line x1="370" y1="70" x2="405" y2="70" stroke="#64748b" stroke-width="1.5"/>
  <text x="387" y="62" fill="#60a5fa" font-size="8" text-anchor="middle">±Wind</text>
  <rect x="405" y="45" width="120" height="50" rx="8" fill="#2d1f00" stroke="#f59e0b"/>
  <text x="465" y="67" fill="#fbbf24" font-size="11" font-weight="bold" text-anchor="middle">GS</text>
  <text x="465" y="82" fill="#fcd34d" font-size="9" text-anchor="middle">Geschwindigkeit</text>
  <text x="465" y="92" fill="#fcd34d" font-size="9" text-anchor="middle">über Grund</text>
  <!-- TAS formula box -->
  <rect x="15" y="115" width="245" height="72" rx="8" fill="#1e293b" stroke="#22c55e"/>
  <text x="138" y="135" fill="#86efac" font-size="11" font-weight="bold" text-anchor="middle">TAS ≈ CAS + 2% pro 1.000 ft</text>
  <text x="138" y="153" fill="#cbd5e1" font-size="10" text-anchor="middle">Beispiel: CAS 100 kt @ 10.000 ft</text>
  <text x="138" y="168" fill="#fbbf24" font-size="10" text-anchor="middle" font-weight="bold">TAS ≈ 100 + (10 × 2%) = 120 kt</text>
  <!-- GS info -->
  <rect x="275" y="115" width="250" height="72" rx="8" fill="#1e293b" stroke="#f59e0b"/>
  <text x="400" y="135" fill="#fbbf24" font-size="11" font-weight="bold" text-anchor="middle">GS = TAS ± Wind</text>
  <text x="400" y="153" fill="#cbd5e1" font-size="10" text-anchor="middle">Gegenwind → GS &lt; TAS</text>
  <text x="400" y="168" fill="#cbd5e1" font-size="10" text-anchor="middle">Rückenwind → GS &gt; TAS</text>
</svg>"""

SVG_KARTEN_SYMBOLE = """<svg viewBox="0 0 540 270" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="270" fill="#0f172a" rx="12"/>
  <text x="270" y="22" fill="white" font-size="13" font-weight="bold" text-anchor="middle">Wichtige ICAO-Symbole auf VFR-Karten</text>
  <!-- Grid of symbols -->
  <!-- Row 1: Airports -->
  <circle cx="40" cy="65" r="14" fill="none" stroke="white" stroke-width="1.5"/>
  <text x="40" y="70" fill="white" font-size="10" text-anchor="middle">▲</text>
  <text x="40" y="88" fill="#94a3b8" font-size="9" text-anchor="middle">Zivil</text>
  <circle cx="90" cy="65" r="14" fill="none" stroke="#64748b" stroke-width="1.5"/>
  <text x="90" y="70" fill="#64748b" font-size="10" text-anchor="middle">✕</text>
  <text x="90" y="88" fill="#94a3b8" font-size="9" text-anchor="middle">Geschlossen</text>
  <text x="150" y="70" fill="white" font-size="12" font-weight="bold">H</text>
  <circle cx="150" cy="65" r="13" fill="none" stroke="white" stroke-width="1.5"/>
  <text x="150" y="88" fill="#94a3b8" font-size="9" text-anchor="middle">Heliport</text>
  <!-- NDB symbol -->
  <circle cx="215" cy="65" r="8" fill="none" stroke="#f59e0b" stroke-width="1.5"/>
  <circle cx="215" cy="65" r="3" fill="#f59e0b"/>
  <text x="215" y="88" fill="#f59e0b" font-size="9" text-anchor="middle">NDB</text>
  <!-- VOR symbol -->
  <polygon points="270,52 282,78 258,78" fill="none" stroke="#22c55e" stroke-width="1.5"/>
  <circle cx="270" cy="65" r="5" fill="#22c55e"/>
  <text x="270" y="88" fill="#22c55e" font-size="9" text-anchor="middle">VOR</text>
  <!-- DME -->
  <rect x="308" y="52" width="24" height="24" fill="none" stroke="#60a5fa" stroke-width="1.5"/>
  <text x="320" y="88" fill="#60a5fa" font-size="9" text-anchor="middle">DME</text>
  <!-- Meldepunkte -->
  <polygon points="380,52 390,78 370,78" fill="white" stroke="white"/>
  <text x="380" y="88" fill="#94a3b8" font-size="9" text-anchor="middle">Pflicht</text>
  <polygon points="435,52 445,78 425,78" fill="none" stroke="white" stroke-width="1.5"/>
  <text x="435" y="88" fill="#94a3b8" font-size="9" text-anchor="middle">Bedarf</text>
  <!-- Divider -->
  <line x1="10" y1="100" x2="530" y2="100" stroke="#1e293b"/>
  <!-- Row 2: Airspace -->
  <text x="270" y="118" fill="#94a3b8" font-size="10" text-anchor="middle" font-weight="bold">LUFTRAUMGRENZEN</text>
  <!-- CTR solid -->
  <rect x="15" y="128" width="100" height="28" rx="4" fill="none" stroke="#3b82f6" stroke-width="2.5"/>
  <text x="65" y="148" fill="#3b82f6" font-size="10" text-anchor="middle" font-weight="bold">CTR / TMA</text>
  <!-- Restricted zone -->
  <rect x="130" y="128" width="100" height="28" rx="4" fill="#ef444420" stroke="#ef4444" stroke-width="2" stroke-dasharray="6,3"/>
  <text x="180" y="148" fill="#ef4444" font-size="10" text-anchor="middle" font-weight="bold">Gefahrengebiet</text>
  <!-- FIR -->
  <rect x="245" y="128" width="100" height="28" rx="4" fill="none" stroke="#a78bfa" stroke-width="1.5" stroke-dasharray="8,4"/>
  <text x="295" y="148" fill="#a78bfa" font-size="10" text-anchor="middle">FIR-Grenze</text>
  <!-- Isogone -->
  <line x1="360" y1="128" x2="430" y2="156" stroke="#fbbf24" stroke-width="1.5"/>
  <text x="370" y="127" fill="#fbbf24" font-size="9">3°E</text>
  <text x="360" y="165" fill="#fbbf24" font-size="9" text-anchor="middle">Isogone</text>
  <!-- Row 3: Elevations / MEF -->
  <line x1="10" y1="178" x2="530" y2="178" stroke="#1e293b"/>
  <text x="270" y="196" fill="#94a3b8" font-size="10" text-anchor="middle" font-weight="bold">SICHERHEITSMINDESTHÖHEN (MEF / MGAA)</text>
  <rect x="15" y="208" width="240" height="52" rx="6" fill="#2d1a00" stroke="#f59e0b"/>
  <text x="30" y="226" fill="#fbbf24" font-size="28" font-weight="bold">27</text>
  <text x="80" y="222" fill="#fcd34d" font-size="11" font-weight="bold">MEF = 2.700 ft MSL</text>
  <text x="80" y="237" fill="#cbd5e1" font-size="10">größte Ziffer = Tausender</text>
  <text x="80" y="250" fill="#94a3b8" font-size="9">gilt für 30'×30'-Kartenfeld</text>
  <rect x="270" y="208" width="260" height="52" rx="6" fill="#1e293b" stroke="#334155"/>
  <text x="400" y="226" fill="white" font-size="11" text-anchor="middle" font-weight="bold">MGAA – Safety Buffer</text>
  <text x="400" y="241" fill="#cbd5e1" font-size="10" text-anchor="middle">Höchste Erhebung &lt;5000ft → +1000ft</text>
  <text x="400" y="256" fill="#fbbf24" font-size="10" text-anchor="middle">Höchste Erhebung ≥5000ft → +2000ft</text>
</svg>"""

# ═══════════════════════════════════════════════════════════════════════════
#  CHAPTER CONTENT DATA
# ═══════════════════════════════════════════════════════════════════════════

# Each section: (type, content, extra)
CHAPTERS = {
    # ── KAPITEL 1: DIE ERDE ───────────────────────────────────────────────
    "nav-erde": {
        "subject_id": "nav",
        "title": "Die Erde – Gestalt, Koordinaten & Nordbezüge",
        "sort_order": 1,
        "exam": 1,
        "sections": [
            ("heading", "Kapitel 1: Die Erde", "Grundlagen der Navigation"),
            ("diagram", SVG_ERDE_KOORDINATEN, "Koordinatensystem: Breitenkreise und Meridiane"),
            ("subheading", "1.1 Die Gestalt der Erde", None),
            ("text", "Die Erde ist keine perfekte Kugel, sondern ein Rotationsellipsoid – an den Polen leicht abgeplattet, am Äquator aufgewölbt. Der Poldurchmesser ist ca. 42 km kleiner als der Äquatordurchmesser.", None),
            ("fact", "Abplattungsverhältnis der Erde: 1/300 (Pol-Radius ca. 21 km kürzer als Äquator-Radius). Für VFR-Navigation gilt die Erde praktisch als Kugel.", None),
            ("table_row", "Erdumfang (Äquator)", "21.639 NM ≈ 40.077 km"),
            ("table_row", "Erdumfang (Pol)", "21.603 NM ≈ 40.009 km"),
            ("table_row", "Abplattungsverhältnis", "1/300 (AP = (RE – RP) / RE)"),
            ("table_row", "WGS84", "Referenzellipsoid für GNSS und VFR-Navigationskarten"),
            ("subheading", "1.2 Orientierung auf der Erde", None),
            ("text", "Zur eindeutigen Positionsbestimmung wird die Erde mit einem virtuellen Koordinatennetz überzogen. Längen- und Breitenkreise ermöglichen die präzise Angabe jedes Punktes.", None),
            ("fact", "Breitenkreise (φ): parallele Kreise zum Äquator. Abstand zwischen zwei Breitenparallelen: konstant 60 NM pro Grad.", None),
            ("fact", "Längenkreise / Meridiane (λ): verlaufen von Pol zu Pol. Alle Meridiane sind Halbkreise. Nullmeridian: Greenwich (0°). Werte 0–180° Ost/West.", None),
            ("infobox", "Breitenunterschiede und Längenunterschiede berechnen: Beide Koordinaten können auf verschiedenen Hemisphären liegen. Längenunterschied wird immer über den kürzesten Weg (max. 180°) berechnet.", "Berechnungen"),
            ("subheading", "1.3 Navigatorisch wichtige Linien", None),
            ("diagram", SVG_GROSSKREIS_LOXODROME, "Orthodrome (Großkreis) und Loxodrome (Kursgleiche) im Vergleich"),
            ("text", "Auf der Erde gibt es zwei grundlegende navigatorische Linien für die Flugplanung:", None),
            ("table_row", "Orthodrome (Großkreis)", "Kürzeste Verbindung zweier Punkte. Mittelpunkt = Erdmittelpunkt. Kurs ändert sich stetig. Auf Lambert-Karte ≈ gerade Linie."),
            ("table_row", "Loxodrome (Kursgleiche)", "Schneidet jeden Meridian unter gleichem Winkel. Kurs bleibt konstant → einfacher zu fliegen. Strecke länger als Orthodrome."),
            ("fact", "Bis 200 NM Entfernung ist der Unterschied zwischen Orthodrome und Loxodrome so gering, dass er für VFR-Navigation vernachlässigt werden kann.", None),
            ("focus", "Prüfungsrelevant: Meridianen und Äquator sind gleichzeitig Orthodrome UND Loxodrome. Andere Breitenkreise (außer Äquator) sind nur Loxodromen.", None),
            ("subheading", "1.4 Entfernungen und Maßeinheiten", None),
            ("table_row", "Nautische Meile (NM)", "1 NM = 1 Bogenminute auf einem Großkreis = 1,852 km"),
            ("table_row", "Horizontale Entfernungen", "in Nautischen Meilen [NM]"),
            ("table_row", "Vertikale Entfernungen (Höhe)", "in Fuß [ft]; 1 ft = 0,3048 m; 1 m = 3,281 ft"),
            ("table_row", "Horizontale Geschwindigkeit", "in Knoten [kt] = NM/h"),
            ("table_row", "Vertikale Geschwindigkeit", "in ft/min oder m/s"),
            ("table_row", "Umrechnung NM ↔ km", "NM = km/2 + 10% | ft = m × 3 + 10%"),
        ],
        "quiz": [
            {"q": "Welche Form hat die Erde?", "opts": ["Perfekte Kugel","Rotationsellipsoid, an den Polen abgeplattet","Zylinder","Würfel"], "a": 1, "e": "Die Erde ist ein Rotationsellipsoid: am Äquator leicht aufgewölbt, an den Polen abgeplattet. Abplattungsverhältnis 1/300."},
            {"q": "Wie groß ist der Abstand zweier benachbarter Breitenkreise?", "opts": ["30 NM","60 NM","90 NM","abhängig vom Breitengrad"], "a": 1, "e": "Der Abstand zweier Breitenparallelen beträgt konstant 60 NM pro Grad. Dies gilt überall auf der Erde."},
            {"q": "Was ist die Orthodrome?", "opts": ["Eine Linie mit konstantem Kurs","Der Großkreis – kürzeste Verbindung zwischen zwei Punkten","Ein Breitenkreis","Der Nullmeridian"], "a": 1, "e": "Die Orthodrome ist Teil eines Großkreises, dessen Mittelpunkt mit dem Erdmittelpunkt identisch ist. Sie ist die kürzeste Verbindung zwischen zwei Punkten."},
            {"q": "Was ist ein Vorteil der Loxodrome gegenüber der Orthodrome?", "opts": ["Sie ist kürzer","Der Kurs bleibt konstant – einfacheres Fliegen","Sie verläuft immer entlang eines Meridians","Sie ist nur in Polargebieten relevant"], "a": 1, "e": "Die Loxodrome (Kursgleiche) schneidet jeden Meridian unter demselben Winkel, der Kurs bleibt also konstant. Das macht die Navigation einfacher, obwohl die Strecke länger ist."},
            {"q": "Was bedeutet WGS84 in der Navigation?", "opts": ["Ein Flugzeugtyp","Das Referenzellipsoid für GNSS und Navigationskarten","Eine Frequenz für NDB","Eine Abkürzung für Windgeschwindigkeit"], "a": 1, "e": "WGS84 (World Geodetic System 1984) ist das für GNSS (GPS) und auf VFR-Navigationskarten verwendete Referenzellipsoid."},
            {"q": "An welchen Punkten laufen alle Längengrade zusammen?", "opts": ["Am Äquator","Am geografischen Nord- und Südpol","Auf dem Nullmeridian","Am Wendekreis"], "a": 1, "e": "Alle Meridiane laufen an den geografischen Polen zusammen. Deshalb nimmt der Abstand zwischen zwei Meridianen mit zunehmender Breite ab."},
            {"q": "Auf welchem Längenkreis bezieht sich die geografische Länge eines Ortes?", "opts": ["Auf den Datumsgrenz-Meridian","Auf den Nullmeridian (Greenwich)","Auf den Zentralmeridian der Zeitzone","Auf den Heimatmeridian"], "a": 1, "e": "Die geografische Länge (λ) wird als Winkelunterschied zum Greenwich-Meridian (0°) angegeben. Werte 0–180° Ost oder West."},
            {"q": "Wie wird der breitenunabhängige Abstand zweier Längengrade bezeichnet?", "opts": ["Departure","Abweitung","True Track","Dip"], "a": 0, "e": "Der breitenunabhängige Abstand zweier Längengrade heißt Abweitung (Departure). Am Äquator beträgt er 60 NM pro Grad, nimmt zu den Polen hin ab."},
            {"q": "Welche der folgenden Linien sind sowohl Orthodromen als auch Loxodromen?", "opts": ["Alle Breitenkreise","Meridiane und Äquator","Nur der Nullmeridian","Alle Parallelen"], "a": 1, "e": "Meridiane (Längenkreise) und der Äquator sind gleichzeitig Großkreise (Orthodromen) UND Loxodromen, da sie jeden Meridian unter konstantem Winkel schneiden."},
            {"q": "Welches Vorzeichen besitzt die Variation (Ortsmissweisung) im Kursschema?", "opts": ["Immer positiv","+/- je nach Richtung östlich oder westlich","Immer negativ","Kein Vorzeichen"], "a": 1, "e": "Die Variation wird mit + für östliche und – für westliche Werte angegeben. Im Kursschema: TC - VAR = MC."},
        ]
    },

    # ── KAPITEL 1.4: ZEITRECHNUNG ─────────────────────────────────────────
    "nav-zeit": {
        "subject_id": "nav",
        "title": "Zeitrechnung – LMT, UTC, Zeitzonen & Dämmerung",
        "sort_order": 2,
        "exam": 1,
        "sections": [
            ("heading", "Zeitrechnung in der Luftfahrt", "Kapitel 1.4"),
            ("diagram", SVG_ZEITRECHNUNG, "Zeitsysteme: LMT → GMT → UTC"),
            ("subheading", "Tageslänge – Siderischer Tag vs. Sonnentag", None),
            ("text", "Die Zeitrechnung basiert auf der Rotation der Erde. Je nach verwendetem Bezugspunkt entstehen unterschiedliche Tageslängen.", None),
            ("table_row", "Siderischer Tag (Sterntag)", "23 h 56 m 4,091 s – Bezugspunkt: unendlich weit entfernter Fixstern"),
            ("table_row", "Sonnentag (mittlerer)", "24 Stunden – Bezugspunkt: obere Kulmination der Sonne um 1200"),
            ("table_row", "Schaltjahr", "365,25 Tage → alle 4 Jahre ein Schalttag (29. Februar)"),
            ("infobox", "Zeitpunkte werden in 4-stelligem Format HHMM angegeben (z.B. 1430 UTC). Zeitspannen in HH:MM Format.", "Zeitformat"),
            ("subheading", "1.4.2 Jahreszeiten", None),
            ("text", "Die Jahreszeiten entstehen durch die Schrägstellung der Erdachse um 23,5° gegenüber der Umlaufbahnebene um die Sonne (Ekliptik).", None),
            ("table_row", "Wendekreise (23,5° N/S)", "Sonne steht hier je 1× jährlich im Zenit. Zwischen den Wendekreisen: Tropen (bis 2× jährlich im Zenit)."),
            ("table_row", "Polarkreise (66,5° N/S)", "Markieren Grenze der Polarnacht und des Polartags"),
            ("table_row", "Sommersonnenwende NH", "20./21. Juni – Sonne im Zenit am Wendekreis des Krebses (23,5°N)"),
            ("table_row", "Wintersonnenwende NH", "21./22. Dezember – Sonne im Zenit am Wendekreis des Steinbocks (23,5°S)"),
            ("subheading", "1.4.3 Zeitsysteme", None),
            ("text", "Da es nicht praktisch ist, überall eine lokale Zeit zu verwenden, wurde die Erde in 24 Zeitzonen eingeteilt. Jede Zone erstreckt sich über 15° geografischer Länge.", None),
            ("fact", "Mittlere Ortszeit (LMT): Die lokale Ortszeit hängt ausschließlich von der geografischen Länge ab. Östlich gelegene Punkte haben eine frühere (spätere) LMT.", None),
            ("table_row", "LMT (Local Mean Time)", "Lokale Ortszeit basierend auf geografischer Länge. 1° Länge = 4 Minuten Zeitunterschied."),
            ("table_row", "Zonenzeit (ZT)", "Standardzeit einer 15°-Zone. Differenz zur Nachbarzone: genau 1 Stunde."),
            ("table_row", "GMT / UTC", "Mittlere Ortszeit am Nullmeridian. UTC ist atomuhrenbasiert und die Bezugszeit der Luftfahrt."),
            ("table_row", "MESZ / MEZ", "MESZ = UTC+2 (Sommer). MEZ = UTC+1 (Winter)."),
            ("fact", "UTC ist die universelle Zeitreferenz in der Luftfahrt. Alle Zeiten (Start, Landung, Funkverkehr, NOTAMs) werden in UTC angegeben.", None),
            ("subheading", "Sonnenauf- und -untergang", None),
            ("text", "Für VFR-Flüge sind Sonnenauf- und Sonnenuntergang prüfungsrelevant. Die Zeiten hängen von geografischer Länge UND Breite ab.", None),
            ("infobox", "Die Nacht beginnt mit dem Ende der bürgerlichen Abenddämmerung (ECET – End of Civil Evening Twilight) und endet mit dem Beginn der bürgerlichen Morgendämmerung (BCMT). Die bürgerliche Dämmerung endet/beginnt, wenn die Sonne 6° unterhalb des Horizonts steht.", "Definition Nacht in der Luftfahrt"),
            ("fact", "Datumsgrenze: liegt theoretisch am 180°-Meridian (tatsächlich politisch angepasst). Von West nach Ost: Datum erhöht sich um 1 Tag. Von Ost nach West: Datum verringert sich.", None),
        ],
        "quiz": [
            {"q": "Wie lange dauert ein Sonnentag?", "opts": ["23 h 56 m 4 s","24 Stunden","24 h 3 m","365,25 Tage"], "a": 1, "e": "Der mittlere Sonnentag dauert genau 24 Stunden und basiert auf der oberen Kulmination der Sonne um 1200 Mittags."},
            {"q": "Ist der siderische Tag oder der Sonnentag länger, und warum?", "opts": ["Siderisch, weil er ein Fixstern-Bezugspunkt hat","Sonnentag, weil die Erde sich zusätzlich um die Sonne dreht","Beide gleich lang","Siderisch, weil die Erde schneller rotiert"], "a": 1, "e": "Der Sonnentag (24h) ist länger als der siderische Tag (23h56m), weil sich die Erde zusätzlich zu ihrer Rotation um die Sonne bewegt und deshalb ca. 1° weiterdrehen muss, damit die Sonne wieder im Kulminationspunkt steht."},
            {"q": "Wofür stehen die Bezeichnungen 'TN' und 'MN'?", "opts": ["True Navigation und Magnetic Navigation","True North (Geografisch Nord) und Magnetic North (Magnetisch Nord)","Time North und Meridian North","Total Navigation und Main Navigation"], "a": 1, "e": "TN = True North (Geografisch/Rechtweisend Nord) und MN = Magnetic North (Magnetisch/Missweisend Nord)."},
            {"q": "Von welchem Faktor hängt die Local Mean Time (LMT) ab?", "opts": ["Von der Jahreszeit","Von der geografischen Länge eines Ortes","Von der Flughöhe","Von der UTC-Zeitzone"], "a": 1, "e": "Die LMT hängt ausschließlich von der geografischen Länge ab. Pro 1° Längenunterschied ergibt sich ein Zeitunterschied von 4 Minuten."},
            {"q": "Wie viel Uhr UTC ist es in Greenwich, wenn die Sonne direkt über dem Nullmeridian (Greenwich) steht?", "opts": ["0000 UTC","1200 UTC","1800 UTC","0600 UTC"], "a": 1, "e": "Wenn die Sonne direkt über dem Nullmeridian steht (obere Kulmination), ist es per Definition 1200 UTC (Mittag)."},
            {"q": "Wie viel Uhr UTC ist es in Deutschland, wenn die Sonne direkt über dem Nullmeridian steht?", "opts": ["1100 UTC","1200 UTC (die Weltzeit ist überall gleich)","1300 UTC","Abhängig von der Jahreszeit"], "a": 1, "e": "UTC ist überall auf der Welt gleich. Wenn es am Nullmeridian 1200 UTC ist, ist es auch in Deutschland 1200 UTC – nur die Lokalzeit unterscheidet sich."},
            {"q": "Wie definiert die Luftfahrt den Beginn der Nacht?", "opts": ["Bei Sonnenuntergang","Mit dem Ende der bürgerlichen Abenddämmerung (ECET) – Sonne 6° unter Horizont","Um 2200 Uhr Lokalzeit","Wenn es vollständig dunkel ist"], "a": 1, "e": "Die Nacht beginnt in der Luftfahrt mit dem Ende der bürgerlichen Abenddämmerung (ECET), wenn die Sonne 6° unterhalb des Horizonts steht."},
            {"q": "Welche Zeit orientiert sich an Zeitzonen und politischen Interessen?", "opts": ["UTC","Standardzeit (ST / Zonenzeit)","LMT","GMT"], "a": 1, "e": "Die Standardzeit (auch Zonenzeit) berücksichtigt sowohl geografische Merkmale als auch politische und wirtschaftliche Interessen. Sie wird über eine Zeitdifferenz zu UTC ausgedrückt."},
        ]
    },

    # ── KAPITEL 2: KARTENKUNDE ────────────────────────────────────────────
    "nav-karten": {
        "subject_id": "nav",
        "title": "Kartenkunde – Projektionen, Karten & Symbole",
        "sort_order": 3,
        "exam": 1,
        "sections": [
            ("heading", "Kapitel 2: Kartenkunde", "Kartenprojektionen und VFR-Navigationskarten"),
            ("diagram", SVG_PROJEKTIONEN, "Die drei wichtigsten Kartenprojektionen in der Luftfahrt"),
            ("subheading", "2.1 Projektionsverfahren", None),
            ("text", "Da es unmöglich ist, eine gekrümmte Kugeloberfläche fehlerfrei auf einer zweidimensionalen Karte darzustellen, muss bei jeder Projektion ein Kompromiss eingegangen werden.", None),
            ("fact", "Winkeltreue (konforme Projektion) ist die wichtigste Anforderung an eine Navigationskarte! Nur auf einer winkeltreuen Karte können korrekte Kurse und Peilungen abgelesen werden.", None),
            ("table_row", "Azimutalprojektion", "Projektionsebene = Ebene. Am Pol: Polarstereographische Projektion (für 70–90°)."),
            ("table_row", "Zylinderprojektion / Mercator", "Projektionsebene = Zylinder. Loxodrome = gerade Linie. Verwendung: äquatornahe Gebiete (0–30°)."),
            ("table_row", "Kegelprojektion / Lambert", "Projektionsebene = Kegel. Orthodrome ≈ gerade Linie. Standard in der Luftfahrt für 30–70° Breite."),
            ("subheading", "2.2 Die Lambert'sche Schnittkegelprojektion", None),
            ("text", "Die gebräuchlichste Projektionsart für die Luftfahrt mittlerer Breiten. Durch zwei Standardparallelen (Schnittbreiten) wird der Maßstabsfehler minimiert.", None),
            ("fact", "Zwischen den Standardparallelen: Maßstab etwas zu klein. Außerhalb: Maßstab zu groß. An den Standardparallelen: Maßstab exakt.", None),
            ("table_row", "Konformität", "Winkeltreu – Kurse stimmen mit Karte überein"),
            ("table_row", "Maßstab", "Annähernd konstant, kann als konstant angenommen werden"),
            ("table_row", "Orthodrome", "Erscheint als gerade Linie (leichte Krümmung in Äquatorrichtung)"),
            ("table_row", "Loxodrome", "Leicht gebogene Linie Richtung Äquator"),
            ("table_row", "Kartenkonvergenz (mc)", "mc = Δλ × sin φ₀ (Winkel zwischen Meridianen auf der Karte)"),
            ("infobox", "Die Lambert-Karte ist die bevorzugte Navigationskarte in der Luftfahrt, weil sie winkeltreu ist und der Großkreis als gerade Linie erscheint.", "Fazit Lambert-Karte"),
            ("subheading", "2.3 Eigenschaften von Karten und Maßstab", None),
            ("text", "Navigationskarten sind verkleinerte Abbilder der Erde. Der Maßstab gibt das Verhältnis der Kartenentfernung zur tatsächlichen Entfernung an.", None),
            ("table_row", "Maßstabszahl", "1:500.000 bedeutet 1 cm Karte = 500.000 cm = 5 km = 2,7 NM in Wirklichkeit"),
            ("table_row", "Typische Maßstäbe", "1:500.000 (ICAO-VFR), 1:1.000.000 (WAC), 1:250.000 (dichte Gebiete)"),
            ("fact", "Für die Kursentnahme auf einer Lambert-Karte: Kurs immer am Mittelmeridian zwischen Start- und Endpunkt ablesen.", None),
            ("subheading", "2.4 Luftfahrt-VFR-Navigationskarten", None),
            ("diagram", SVG_KARTEN_SYMBOLE, "Wichtige ICAO-Kartensymbole auf VFR-Karten"),
            ("text", "Für den VFR-Flugbereich werden von ICAO-Mitgliedsstaaten und privaten Anbietern spezielle Luftfahrtkarten herausgegeben. Standard ist Lambert-Projektion im Maßstab 1:500.000.", None),
            ("table_row", "ICAO-Karte (1:500.000)", "Standard-VFR-Navigationskarte. Lambert-Projektion. Enthält: Luftraumstruktur, Funknavigationsanlagen, Meldepunkte, MEF-Angaben."),
            ("table_row", "Sichtflugkarte", "Detaillierter Überblick der Flugplatzumgebung. Im Kopfteil: Frequenzen, Koordinaten, Platzrunde."),
            ("table_row", "Flugplatzkarte", "Gebäude, Rollwege, Pisten, Start- und Landestrecken."),
            ("table_row", "Streckenkarte (Enroute)", "Für IFR und Nachtflüge. Airways, Waypoints, Mindesthöhen."),
            ("table_row", "Digitale Karten", "z.B. ForeFlight, Garmin Pilot. Dynamisch, immer aktuell, mit GAFOR, NOTAMs, SIGMETs."),
            ("subheading", "Sicherheitsmindesthöhen (MEF und MGAA)", None),
            ("text", "Für die Sicherheit sind auf VFR-Karten Sicherheitsmindesthöhen eingetragen, die für einen bestimmten Bereich die maximale Höhe mit Sicherheitspuffer angeben.", None),
            ("table_row", "MEF (Maximum Elevation Figure)", "Basiert auf höchster Geländeerhebung + 328ft (fictives Hindernis) + Aufrundung auf 100ft. Als zweiziffrige Zahl dargestellt (z.B. 27 = 2.700 ft MSL)."),
            ("table_row", "MGAA (Minimum Grid Area Altitude)", "Basiert auf höchster Erhebung. Bis 5.000ft: +1.000ft Buffer. Ab 5.001ft: +2.000ft Buffer."),
        ],
        "quiz": [
            {"q": "Wie wird das Verfahren genannt, nach dem Oberflächenmerkmale der Erdkugel auf eine Fläche abgebildet werden?", "opts": ["Interpolation","Projektion","Triangulation","Kartierung"], "a": 1, "e": "Das Verfahren zur Abbildung der gekrümmten Erdoberfläche auf eine zweidimensionale Fläche heißt Projektion."},
            {"q": "Welche Projektionsart liegt der Lambert-Karte zugrunde?", "opts": ["Zylinderprojektion","Kegelprojektion (Schnittkegelprojektion)","Azimutalprojektion","Flächentreue Projektion"], "a": 1, "e": "Die Lambert-Karte basiert auf einer Kegelprojektion (genauer: Schnittkegelprojektion / conformal conic projection)."},
            {"q": "Warum ist Winkeltreue für Navigationskarten unverzichtbar?", "opts": ["Weil sie schöner aussieht","Weil aus der Karte entnommene Kurse mit den Winkeln in der Realität übereinstimmen müssen","Weil Flugzeuge keinen Maßstab brauchen","Weil Flächentreue wichtiger ist"], "a": 1, "e": "Winkeltreue (Konformität) ist die wichtigste Eigenschaft, damit die von der Karte abgelesenen Kurse exakt mit den tatsächlichen Kursen übereinstimmen."},
            {"q": "Welche Projektionsart liegt der Mercator-Karte zugrunde?", "opts": ["Kegelprojektion","Zylinderprojektion","Azimutalprojektion","Schnittprojektion"], "a": 1, "e": "Die Mercator-Karte basiert auf einer (mathematisch korrigierten) Zylinderprojektion, bei der die Loxodrome als gerade Linie erscheint."},
            {"q": "Wie ist die Karteneigenschaft 'annähernd längentreu' zu verstehen?", "opts": ["Auf einem Kartenblatt kann ein konstanter Maßstab angenommen werden","Jede Länge ist exakt korrekt","Der Maßstab ändert sich stark","Nur für Breitengrade gilt konstanter Maßstab"], "a": 0, "e": "Annähernd längentreu bedeutet, dass innerhalb eines Kartenausschnitts ein praktisch konstanter Maßstab verwendet werden kann."},
            {"q": "Welche wichtigsten Anforderungen werden an Navigationskarten gestellt?", "opts": ["Nur Schönheit und Farbe","Winkeltreue (exakt), Längen- und Flächentreue (annähernd)","Nur Flächentreue","Nur Maßstabskonstanz"], "a": 1, "e": "Die wichtigsten Anforderungen an Navigationskarten sind: Winkeltreue (exakt erfüllt), Längen- und Flächentreue (annähernd). Winkeltreue ist die kritischste Eigenschaft."},
            {"q": "Beschreibe die Orthodrome als wichtige navigatorische Linie.", "opts": ["Eine Linie mit konstantem Kurs","Teil eines Großkreises, kürzeste Verbindung zwischen zwei Orten, Kurs variabel","Eine Linie parallel zum Äquator","Der Nullmeridian"], "a": 1, "e": "Die Orthodrome ist Teil eines Großkreises, die kürzeste Verbindung zwischen zwei Orten auf der Erde. Ihr Kurs ändert sich ständig."},
            {"q": "Auf welcher Karte erscheint die Orthodrome als gerade Linie?", "opts": ["Mercator-Karte","Lambert-Karte (Schnittkegelprojektion)","Polarstereographische Karte","Auf keiner Karte"], "a": 1, "e": "Auf der Lambert-Karte erscheint der Großkreis (Orthodrome) als gerade Linie. Das ist der entscheidende Vorteil für die Luftfahrt."},
            {"q": "Welche Bedeutung haben Maximum Elevation Figures (MEF) und Minimum Grid Area Altitudes (MGAA)?", "opts": ["Sie geben die optimale Reiseflughöhe an","Sie ermöglichen schnelle Bestimmung der Sicherheitsmindesthöhe auf der Karte","Sie markieren Flugplatzhöhen","Sie sind nur für IFR relevant"], "a": 1, "e": "MEF und MGAA dienen als Planungshilfe: Sie zeigen die maximale Hindernishöhe in einem Kartenquadranten plus Sicherheitspuffer, um schnell eine sichere Flughöhe bestimmen zu können."},
            {"q": "In welcher Karte finden sich Hinweise zu vorgeschriebenem Verlauf und Höhe einer Platzrunde?", "opts": ["Streckenkarte","Sichtflugkarte","Weltluftfahrtkarte","Topographische Karte"], "a": 1, "e": "Die Sichtflugkarte (VFR Chart) enthält detaillierte Informationen zur Platzrunde, inklusive Höhe, Richtung und Besonderheiten."},
        ]
    },

    # ── KAPITEL 3: MAGNETKOMPASS & KURSSCHEMA ─────────────────────────────
    "nav-kompass": {
        "subject_id": "nav",
        "title": "Magnetkompass, Variation, Deviation & Kursschema",
        "sort_order": 4,
        "exam": 1,
        "sections": [
            ("heading", "Kapitel 3: Magnetkompass & Bezugsrichtungen", "Praktische Navigation"),
            ("diagram", SVG_NORD_VARIATION_DEVIATION, "Kursschema: TC → MC → CC mit Variation und Deviation"),
            ("subheading", "3.1 Geografisch Nord (True North / TN)", None),
            ("text", "Der tatsächliche Nordpol wird als rechtweisender oder geografischer Nordpol bezeichnet. Kurse, die auf diesen Pol bezogen sind, heißen rechtweisende oder geografische Kurse.", None),
            ("fact", "Rechtweisende Kurse werden auf Kartenmaterial verwendet, da die Längengrade in Richtung TN verlaufen. Abkürzung: TC (True Course) oder TH (True Heading).", None),
            ("subheading", "3.2 Magnetisch Nord (Magnetic North / MN)", None),
            ("text", "Die Erde verhält sich wie ein riesiger Stabmagnet. Die magnetischen Pole sind von den geografischen Nordpolen versetzt und wandern jährlich ca. 40 km nordwestwärts.", None),
            ("table_row", "Variation (VAR)", "Winkel zwischen TN und MN. Positiv (+) = östlich, Negativ (–) = westlich. In Mitteleuropa ca. 0–3° Ost."),
            ("table_row", "Isogone", "Linie gleicher Variation auf der Navigationskarte. Die Isogone mit Variation 0° heißt Agone."),
            ("table_row", "Agone", "Isogone der Variation 0° – verläuft derzeit durch Deutschland."),
            ("fact", "Die Variation ändert sich jährlich (in Mitteleuropa ca. 0,08–0,12° nach Osten). Aktuelle Werte sind auf VFR-Karten eingetragen.", None),
            ("subheading", "3.3 Kompass Nord (Compass North / CN)", None),
            ("diagram", SVG_KOMPASS_FEHLER, "Kompassdrehfehler und Beschleunigungsfehler"),
            ("text", "Der praktische Magnetkompass im Flugzeug zeigt wegen Störfeldern durch Metallteile, elektrische Geräte und Zündanlage nicht exakt magnetisch Nord.", None),
            ("table_row", "Deviation (DEV)", "Winkel zwischen MN und CN. Luftfahrzeugeigen. Richtungsabhängig. Wird in Deviationstabelle (30°-Schritte) eingetragen."),
            ("table_row", "Deviationstabelle", "Gibt für verschiedene Kurse an, um wieviel Grad kleiner oder größer gesteuert werden muss."),
            ("fact", "Deviation ist richtungsabhängig! Deshalb wird sie in 30°-Schritten für alle möglichen Kurse in einer Korrekturtabelle unter dem Kompass angebracht.", None),
            ("infobox", "Kursschema von Karte zum Steuerkurs:\nTC – VAR = MC\nMC – DEV = CC\nTC – VAR – DEV = CC\nUmgekehrt (Kompass → Karte):\nCC + DEV = MC → MC + VAR = TC", "Das Kursschema"),
            ("subheading", "Kompassdrehfehler (Turning Error)", None),
            ("text", "Im Kurvenflug kippt die Kompassnadel durch die vertikale Komponente des Erdmagnetfeldes (Inklination) in eine Schräglage – dies verursacht Anzeigeverfälschungen.", None),
            ("table_row", "Nordkurse (N)", "Kurve eilt der Anzeige voraus: Kurve vOrher ausleiten (z.B. bei 120° Ziel → ab 110° ausleiten)"),
            ("table_row", "Südkurse (S)", "Kurve hinkt nach: erst Überkurven (z.B. bei 240° Ziel → Kurve bis 250° fortsetzen)"),
            ("table_row", "Ost-/Westkurse", "Kein Kompassdrehfehler (Nadel kippt in Inklination, keine seitliche Ablenkung)"),
            ("fact", "Merkregel für Nordkurse: N = v O rher ausleiten | Merkregel für Südkurse: S = Ü berkurven", None),
            ("subheading", "Beschleunigungsfehler (Acceleration Error)", None),
            ("text", "Bei Beschleunigung oder Verzögerung auf Ost-/West-Kursen dreht sich die Kompassnadel durch Trägheitskräfte scheinbar.", None),
            ("table_row", "Beschleunigung auf O/W", "Anzeige dreht nach NORDEN (scheinbarer Linksabdrift) – NH (Nordhalbkugel)"),
            ("table_row", "Verzögerung auf O/W", "Anzeige dreht nach SÜDEN (scheinbarer Rechtsabdrift) – NH"),
            ("table_row", "Auf N/S-Kursen", "Kein Beschleunigungsfehler"),
            ("subheading", "Steig- und Sinkflug-Fehler", None),
            ("text", "Im Steig- und Sinkflug auf Ost-/West-Kursen treten ähnliche Fehler wie beim Kurvenflug auf.", None),
            ("table_row", "Sinkflug auf Ostkurs (NH)", "Drehung Richtung Norden"),
            ("table_row", "Steigflug auf Ostkurs (NH)", "Drehung Richtung Süden"),
        ],
        "quiz": [
            {"q": "Was ist die Deviation?", "opts": ["Der Winkel zwischen TN und MN","Der Winkel zwischen MN und CN (Kompass Nord)","Die Abweichung vom geplanten Kurs","Die Differenz zwischen IAS und TAS"], "a": 1, "e": "Die Deviation ist der Winkel zwischen der Anzeige des Magnetkompasses (Kompass Nord) und dem tatsächlichen magnetischen Nord. Sie entsteht durch Störfelder im Luftfahrzeug."},
            {"q": "Was ist die Variation?", "opts": ["Der Winkel zwischen TN und MN","Der Winkel zwischen MN und CN","Die Ablenkung durch Turbulenzen","Der Unterschied zwischen IAS und GS"], "a": 0, "e": "Die Variation (Ortsmissweisung) ist der Winkel zwischen geografischem (TN) und magnetischem Nord (MN). Sie ist ortsabhängig und auf VFR-Karten eingetragen."},
            {"q": "Welche Einheiten werden in der Luftfahrt üblicherweise für horizontale und vertikale Geschwindigkeiten verwendet?", "opts": ["km/h und m/s","Knoten (kt) und ft/min","mph und m/min","NM/s und km/h"], "a": 1, "e": "Horizontale Geschwindigkeiten in Knoten [kt] (NM/h), vertikale Geschwindigkeiten (Steig-/Sinkrate) in ft/min."},
            {"q": "Wofür stehen TC, MC und CC im Kursschema?", "opts": ["Time Course, Magnetic Compass, Compass Course","True Course, Magnetic Course, Compass Course","Total Course, Main Course, Calculated Course","True Cruise, Magnetic Cruise, Corrected Course"], "a": 1, "e": "TC = True Course (rechtweisend), MC = Magnetic Course (missweisend), CC = Compass Course (Kompasskurs). Formel: TC – VAR = MC; MC – DEV = CC."},
            {"q": "Bei einer Beschleunigung auf einem Westkurs dreht die Kompassanzeige auf der Nordhalbkugel …", "opts": ["nach Süden","nach Norden","gar nicht","nach Osten"], "a": 1, "e": "Auf Ost-/Westkursen dreht die Kompassanzeige bei Beschleunigung nach Norden (scheinbarer Linksabdrift auf NH). Merkregel: ANDS – Acceleration North, Deceleration South."},
            {"q": "Beim Einleiten einer Kurve auf einem Nordkurs mit dem Magnetkompass: Wann muss die Kurve ausgeleitet werden?", "opts": ["Wenn der Zielkurs erreicht ist","Vorher – wenn der Kompass noch ca. 10° vor dem Zielkurs anzeigt","Nachher – wenn der Kompass 10° über den Zielkurs hinaus ist","Kein Fehler auf Nordkursen"], "a": 1, "e": "Auf Nordkursen eilt die Kompassanzeige dem tatsächlichen Kurs voraus. Die Kurve muss vOrher (vor Erreichen des Zielkurses) ausgeleitet werden."},
            {"q": "Wofür stehen die Abkürzungen TN und MN?", "opts": ["Total Navigation und Magnetic Navigation","True North (Geografisch Nord) und Magnetic North (Magnetisch Nord)","Track Number und Mach Number","Transponder Number und Minimum Noise"], "a": 1, "e": "TN = True North = Geografisch/Rechtweisend Nord. MN = Magnetic North = Magnetisch/Missweisend Nord."},
            {"q": "Was zeigt die Kursrose auf einem Magnetkompass?", "opts": ["Die geografische Länge","Den missweisenden Steuerkurs (Kompasskurs), abgelesen an der Vorderseite des Steuerstrichs","Den rechtweisenden Kurs","Die aktuelle Zeit in UTC"], "a": 1, "e": "Die Kursrose des Magnetkompasses bleibt stets nach magnetisch Nord ausgerichtet, während sich das Flugzeug dreht. Abgelesen wird der Kurs am Steuerstrich (vorne)."},
        ]
    },

    # ── KAPITEL 3: GESCHWINDIGKEITEN & WINDDREIECK ────────────────────────
    "nav-geschw": {
        "subject_id": "nav",
        "title": "Kursschema, Geschwindigkeiten & das Winddreieck",
        "sort_order": 5,
        "exam": 1,
        "sections": [
            ("heading", "Kapitel 3: Kursschema & Geschwindigkeiten", "Praktische Navigation"),
            ("diagram", SVG_GESCHWINDIGKEITEN, "Geschwindigkeitskette: IAS → CAS → TAS → GS"),
            ("subheading", "3.2.3 Fluggeschwindigkeiten", None),
            ("text", "Die horizontale Fluggeschwindigkeit kann aus verschiedenen Standpunkten beschrieben werden. Jede Geschwindigkeit hat ihre eigene Bedeutung für Navigation und Aerodynamik.", None),
            ("table_row", "IAS (Indicated Airspeed)", "Angezeigt direkt vom Fahrtmesser. Enthält Instrumentenfehler."),
            ("table_row", "CAS (Calibrated Airspeed)", "IAS korrigiert um Einbau- und Instrumentenfehler. Meist sehr ähnlich wie IAS bei niedrigen Geschwindigkeiten."),
            ("table_row", "TAS (True Airspeed)", "Wahre Eigengeschwindigkeit gegenüber der Luft. Dichtefaktorkorrigiert. Steigt mit Höhe bei konstanter IAS."),
            ("table_row", "GS (Ground Speed)", "Geschwindigkeit über Grund. GS = TAS ± Wind. Bestimmt Flugzeit und Kraftstoffverbrauch."),
            ("fact", "Faustregel TAS: TAS = CAS + 2% pro 1.000 ft Höhe. Beispiel: CAS 100 kt @ 8.000 ft → TAS ≈ 116 kt.", None),
            ("subheading", "3.2 Kursschema und Windeinfluss", None),
            ("diagram", SVG_WINDDREIECK, "Das Winddreieck: TH/TAS + Wind = Track/GS"),
            ("text", "Würde das Luftfahrzeug den Kartenkurs (True Course) ohne Windkorrektur fliegen, würde es abgetrieben werden. Der Wind muss im Kursschema berücksichtigt werden.", None),
            ("table_row", "TC (True Course)", "Kartenkurs – in der Karte eingezeichneter Kurs"),
            ("table_row", "WCA (Wind Correction Angle)", "Luvwinkel – Winkel zwischen TH und TC. Negativ wenn Wind von links kommt."),
            ("table_row", "TH (True Heading)", "Steuerkurs rechtweisend = TC + WCA"),
            ("table_row", "MH (Magnetic Heading)", "Steuerkurs missweisend = TH – VAR"),
            ("table_row", "CH (Compass Heading)", "Kompasskurs = MH – DEV"),
            ("table_row", "Track (TT)", "Tatsächlich geflogener Kurs über Grund"),
            ("table_row", "Drift (DA)", "Winkel zwischen TH und Track – durch ungenauen WCA"),
            ("infobox", "Vollständiges Kursschema:\nTC ± WCA = TH → TH – VAR = MH → MH – DEV = CH\nUmgekehrt für Positionsbestimmung:\nCH + DEV = MH → MH + VAR = TH → TH – WCA = Track", "Kursschema komplett"),
            ("subheading", "Das Winddreieck", None),
            ("text", "Das Winddreieck ist das geometrische Werkzeug zur Berechnung der Windeinwirkung auf den Flug. Es besteht aus drei Vektoren:", None),
            ("fact", "TH × TAS (Steuerkurs × Eigengeschwindigkeit) + Windvektor = Track × GS (Kurs über Grund × Grundgeschwindigkeit)", None),
            ("table_row", "Grundaufgabe 1", "Gegeben: TC, Wind. Gesucht: TH und GS. → WCA und GS berechnen."),
            ("table_row", "Grundaufgabe 2", "Gegeben: Track, TAS, GS. Gesucht: TH und Wind. → Wind bestimmen."),
            ("table_row", "Grundaufgabe 3", "Gegeben: TC, TAS, Wind. Gesucht: GS und Flugzeit."),
        ],
        "quiz": [
            {"q": "Was gibt die Ground Speed (GS) an?", "opts": ["Die Eigengeschwindigkeit in ungestörter Luft","Die Geschwindigkeit relativ zur Erdoberfläche – also TAS ± Wind","Die angezeigte Eigengeschwindigkeit","Die maximale Reisegeschwindigkeit"], "a": 1, "e": "GS (Ground Speed) = Geschwindigkeit des Flugzeugs über Grund. GS = TAS korrigiert um Windeinfluss. Bei Gegenwind: GS < TAS, bei Rückenwind: GS > TAS."},
            {"q": "Wie lautet die Formel für eine ungefähre TAS-Berechnung?", "opts": ["TAS = CAS – 2% pro 1.000 ft","TAS = CAS + 2% pro 1.000 ft","TAS = GS – Windstärke","TAS = IAS × Höhe / 1000"], "a": 1, "e": "TAS ≈ CAS + 2% pro 1.000 ft Flughöhe. Bei 10.000 ft ist die TAS also ca. 20% größer als die CAS."},
            {"q": "Was ist der Windvorhaltewinkel (WCA)?", "opts": ["Der Winkel zwischen TN und MN","Der Winkel zwischen geplantem Kurs (TC) und Steuerkurs (TH) – nötig zur Windkorrektur","Der Winkel zwischen Track und GS","Die Deviation im Kursschema"], "a": 1, "e": "WCA (Wind Correction Angle) ist der Winkel, um den der Steuerkurs vom Kartenkurs abweichen muss, damit trotz Wind der geplante Kurs über Grund eingehalten wird."},
            {"q": "Was ist der Unterschied zwischen IAS und CAS?", "opts": ["IAS ist immer größer als CAS","CAS ist die um Einbau- und Instrumentenfehler korrigierte IAS","CAS ist die Geschwindigkeit über Grund","Kein Unterschied – beide identisch"], "a": 1, "e": "CAS (Calibrated Airspeed) = IAS korrigiert um Einbau- und Instrumentenfehler. Die Differenz ist meist gering, bei niedrigen Geschwindigkeiten aber relevant."},
            {"q": "Welche Einheiten werden für Treibstoffmengen angegeben?", "opts": ["Nur Liter","Liter (l), Kilogramm (kg) oder Gallone (gal)","Nur Kilogramm","Nur US-Gallonen"], "a": 1, "e": "Treibstoffmengen können in Litern (l), Kilogramm (kg) oder Gallonen (gal) angegeben werden. Avgas hat eine Dichte von ca. 0,72 kg/l."},
            {"q": "Was ist der Kurs über Grund (Track) in der Navigation?", "opts": ["Der Steuerkurs des Piloten","Der tatsächlich geflogene Kurs des Flugzeugs über die Erdoberfläche","Der Kartenkurs vom Start zum Ziel","Der magnetische Kurs"], "a": 1, "e": "Track = Kurs über Grund (TT – True Track). Das ist der tatsächlich auf der Erdoberfläche zurückgelegte Kurs, abhängig von Steuerkurs und Windeinfluss."},
            {"q": "Was beinhaltet der Aviaten-Navigationsrechner (z.B. Aviat 617)?", "opts": ["Nur GPS-Berechnung","Kreisrechenschieber für Multiplikation, Division, Zeit, Geschwindigkeit, TAS, Höhe und Winddreieck","Nur Winddreieckberechnung","Nur Kraftstoffverbrauch"], "a": 1, "e": "Der Aviat 617 ist ein mechanischer Navigationsrechner (Kreisrechenschieber). Er ermöglicht Multiplikation/Division, Zeit-Geschwindigkeit-Weg-Aufgaben, Maßeinheitenumrechnung, TAS-Berechnung, Dichtehöhe und Winddreieck."},
            {"q": "Wie ist der True Heading (TH) definiert?", "opts": ["TC abzüglich VAR","TC plus Wind Correction Angle (WCA)","MC plus DEV","Kompasskurs plus Variation"], "a": 1, "e": "TH (True Heading) = TC + WCA. Der True Heading ist der rechtweisende Steuerkurs, der unter Berücksichtigung des Windvektors geflogen werden muss."},
        ]
    },
}

# ═══════════════════════════════════════════════════════════════════════════
#  IMPORT LOGIC
# ═══════════════════════════════════════════════════════════════════════════

def run():
    db = sqlite3.connect(DB)
    db.row_factory = sqlite3.Row

    for ch_id, ch in CHAPTERS.items():
        print(f"\n→ Importing chapter: {ch_id}")

        # Ensure chapter exists
        existing = db.execute("SELECT id FROM learn_chapters WHERE id=?", (ch_id,)).fetchone()
        if not existing:
            db.execute("""
                INSERT INTO learn_chapters (id, subject_id, title, sort_order, exam_relevant)
                VALUES (?,?,?,?,?)
            """, (ch_id, ch["subject_id"], ch["title"], ch["sort_order"], ch["exam"]))
            print(f"  Created chapter: {ch['title']}")
        else:
            db.execute("UPDATE learn_chapters SET title=?, sort_order=?, exam_relevant=? WHERE id=?",
                       (ch["title"], ch["sort_order"], ch["exam"], ch_id))
            print(f"  Updated chapter: {ch['title']}")

        # Clear existing sections and quiz
        db.execute("DELETE FROM learn_sections WHERE chapter_id=?", (ch_id,))
        db.execute("DELETE FROM learn_quiz WHERE chapter_id=?", (ch_id,))

        # Insert sections
        for order, sec in enumerate(ch["sections"]):
            sec_type, content, extra = sec
            db.execute("""
                INSERT INTO learn_sections (chapter_id, type, content, extra, sort_order)
                VALUES (?,?,?,?,?)
            """, (ch_id, sec_type, content, extra, order))

        print(f"  Inserted {len(ch['sections'])} sections")

        # Insert quiz
        for order, q in enumerate(ch["quiz"]):
            db.execute("""
                INSERT INTO learn_quiz (chapter_id, question, options, answer, explanation, is_official, sort_order)
                VALUES (?,?,?,?,?,?,?)
            """, (ch_id, q["q"], json.dumps(q["opts"], ensure_ascii=False), q["a"], q["e"], 1, order))

        print(f"  Inserted {len(ch['quiz'])} quiz questions")

    # Also update FTS index
    try:
        for ch_id, ch in CHAPTERS.items():
            db.execute("DELETE FROM learn_fts WHERE chapter_id=?", (ch_id,))
            for sec in ch["sections"]:
                sec_type, content, _ = sec
                if sec_type not in ("diagram",):
                    subj = db.execute("SELECT title FROM learn_subjects WHERE id=?",
                                      (ch["subject_id"],)).fetchone()
                    subj_title = subj["title"] if subj else "Navigation"
                    db.execute("""
                        INSERT INTO learn_fts (chapter_id, subject_id, chapter_title, subject_title, content)
                        VALUES (?,?,?,?,?)
                    """, (ch_id, ch["subject_id"], ch["title"], subj_title, content))
    except Exception as e:
        print(f"  FTS update skipped: {e}")

    db.commit()
    db.close()
    print("\n✅ Navigation chapters imported successfully!")
    print("Chapters created/updated:")
    for ch_id, ch in CHAPTERS.items():
        print(f"  • {ch_id}: {ch['title']} ({len(ch['sections'])} sections, {len(ch['quiz'])} quiz questions)")

if __name__ == "__main__":
    run()
