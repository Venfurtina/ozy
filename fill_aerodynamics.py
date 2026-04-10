#!/usr/bin/env python3
"""
fill_aerodynamics.py
Befüllt den 'principles' Bereich (Aerodynamik) mit vollständigem Inhalt
aus den Buch-PDFs (AirCademy Advanced PPL-Guide, Kapitel 2-5).
Inhalt basiert 1:1 auf dem Buchtext – keine Informationen erfunden.
"""
import json, sqlite3, os, sys

DB_PATH = sys.argv[1] if len(sys.argv) > 1 else os.path.join(os.path.dirname(os.path.abspath(__file__)), "site_final7/site_final7/takvim.db")

# ══════════════════════════════════════════════════════════════════════════════
# SVG DIAGRAMME
# ══════════════════════════════════════════════════════════════════════════════

SVG_PROFIL_GEOMETRIE = """<svg viewBox="0 0 560 210" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:560px;font-family:system-ui,sans-serif">
  <rect width="560" height="210" fill="#0d1623" rx="10"/>
  <text x="280" y="20" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Abb. 16 – Tragflügelgeometrie</text>
  <!-- Profil silhouette -->
  <path d="M60 130 Q120 80 200 90 Q280 95 340 105 Q400 113 460 128 Q480 132 490 130 Q480 140 460 143 Q400 148 340 148 Q280 145 200 140 Q120 140 80 145 Q60 145 60 130 Z" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.5"/>
  <!-- Profilsehne -->
  <line x1="60" y1="130" x2="490" y2="130" stroke="#facc15" stroke-width="1.5" stroke-dasharray="6,3"/>
  <text x="270" y="168" fill="#facc15" font-size="10" text-anchor="middle">Profilsehne (Verbindung Vorder- u. Hinterkante)</text>
  <!-- Profiltiefe arrow -->
  <line x1="60" y1="185" x2="490" y2="185" stroke="#22c55e" stroke-width="1.5" marker-end="url(#arr)" marker-start="url(#arr)"/>
  <text x="275" y="198" fill="#22c55e" font-size="10" text-anchor="middle">Profiltiefe / Spannweite (⊥)</text>
  <!-- Profildicke arrow -->
  <line x1="200" y1="88" x2="200" y2="143" stroke="#f472b6" stroke-width="1.5"/>
  <text x="210" y="120" fill="#f472b6" font-size="9">Profildicke</text>
  <!-- Dickenrücklage arrow -->
  <line x1="60" y1="80" x2="200" y2="80" stroke="#fb923c" stroke-width="1.2" stroke-dasharray="5,3"/>
  <text x="130" y="76" fill="#fb923c" font-size="9" text-anchor="middle">Dickenrücklage</text>
  <!-- Anstellwinkel -->
  <line x1="60" y1="140" x2="200" y2="108" stroke="#a78bfa" stroke-width="1" stroke-dasharray="4,2"/>
  <text x="88" y="154" fill="#a78bfa" font-size="9">α = Anstellwinkel</text>
  <!-- Anströmrichtung -->
  <path d="M10 130 L50 130" stroke="#60a5fa" stroke-width="2" marker-end="url(#arr2)"/>
  <text x="28" y="122" fill="#60a5fa" font-size="9" text-anchor="middle">Anström-</text>
  <text x="28" y="133" fill="#60a5fa" font-size="9" text-anchor="middle">richtung</text>
  <!-- Labels -->
  <text x="55" y="115" fill="#94a3b8" font-size="9">Profilnase</text>
  <text x="478" y="120" fill="#94a3b8" font-size="9" text-anchor="end">Profil-</text>
  <text x="478" y="130" fill="#94a3b8" font-size="9" text-anchor="end">hinterkante</text>
  <!-- Arrows defs -->
  <defs>
    <marker id="arr" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#22c55e"/>
    </marker>
    <marker id="arr2" markerWidth="8" markerHeight="8" refX="4" refY="4" orient="auto">
      <path d="M0,1 L8,4 L0,7 Z" fill="#60a5fa"/>
    </marker>
  </defs>
</svg>"""

SVG_AUFTRIEB_WIDERSTAND = """<svg viewBox="0 0 560 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:560px;font-family:system-ui,sans-serif">
  <rect width="560" height="260" fill="#0d1623" rx="10"/>
  <text x="280" y="20" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Kräfte am Tragflügel – Auftrieb &amp; Widerstand</text>
  <!-- Flugzeug Symbol -->
  <g transform="translate(200,120)">
    <!-- Rumpf -->
    <rect x="-60" y="-8" width="120" height="16" rx="8" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.5"/>
    <!-- Tragflächen -->
    <rect x="-15" y="-50" width="30" height="100" rx="4" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.5"/>
    <!-- Höhenleitwerk -->
    <rect x="35" y="-20" width="20" height="40" rx="3" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1"/>
    <!-- Seitenleitwerk -->
    <rect x="40" y="-30" width="18" height="8" rx="2" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1"/>
  </g>
  <!-- Auftrieb – oben -->
  <line x1="200" y1="115" x2="200" y2="30" stroke="#22c55e" stroke-width="3"/>
  <polygon points="200,22 194,38 206,38" fill="#22c55e"/>
  <text x="212" y="65" fill="#22c55e" font-size="13" font-weight="bold">Auftrieb A</text>
  <text x="212" y="78" fill="#86efac" font-size="10">L = ½ρv²·S·cL</text>
  <text x="212" y="89" fill="#86efac" font-size="10">senkrecht zur Anströmung</text>
  <!-- Gewicht – unten -->
  <line x1="200" y1="128" x2="200" y2="210" stroke="#f87171" stroke-width="3"/>
  <polygon points="200,218 194,202 206,202" fill="#f87171"/>
  <text x="212" y="175" fill="#f87171" font-size="13" font-weight="bold">Gewicht G</text>
  <text x="212" y="188" fill="#fca5a5" font-size="10">G = m × g</text>
  <!-- Widerstand – hinten -->
  <line x1="262" y1="120" x2="340" y2="120" stroke="#fb923c" stroke-width="3"/>
  <polygon points="348,120 332,114 332,126" fill="#fb923c"/>
  <text x="350" y="116" fill="#fb923c" font-size="13" font-weight="bold">Widerstand W</text>
  <text x="350" y="129" fill="#fdba74" font-size="10">D = ½ρv²·S·cD</text>
  <text x="350" y="140" fill="#fdba74" font-size="10">parallel zur Anströmung</text>
  <!-- Schub – vorne -->
  <line x1="138" y1="120" x2="60" y2="120" stroke="#60a5fa" stroke-width="3"/>
  <polygon points="52,120 68,114 68,126" fill="#60a5fa"/>
  <text x="5" y="116" fill="#60a5fa" font-size="13" font-weight="bold">Schub S</text>
  <text x="5" y="129" fill="#93c5fd" font-size="10">Motor-/Propellerkraft</text>
  <!-- Infobox -->
  <rect x="14" y="180" width="190" height="55" rx="5" fill="#1e2d1a" stroke="#22c55e" stroke-width="1"/>
  <text x="109" y="198" fill="#86efac" font-size="10" font-weight="bold" text-anchor="middle">Gleichgewicht im Geradeausflug:</text>
  <text x="109" y="212" fill="white" font-size="10" text-anchor="middle">Auftrieb = Gewicht</text>
  <text x="109" y="226" fill="white" font-size="10" text-anchor="middle">Schub = Widerstand</text>
</svg>"""

SVG_POLARDIAGRAMM = """<svg viewBox="0 0 520 300" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:520px;font-family:system-ui,sans-serif">
  <rect width="520" height="300" fill="#0d1623" rx="10"/>
  <text x="260" y="20" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Lilienthal'sches Polardiagramm (schematisch)</text>
  <!-- Axes -->
  <line x1="70" y1="240" x2="70" y2="30" stroke="#475569" stroke-width="1.5"/>
  <line x1="70" y1="240" x2="480" y2="240" stroke="#475569" stroke-width="1.5"/>
  <text x="65" y="28" fill="#94a3b8" font-size="11" text-anchor="middle">cL</text>
  <text x="482" y="244" fill="#94a3b8" font-size="11">cD</text>
  <!-- Grid labels -->
  <text x="65" y="200" fill="#475569" font-size="9" text-anchor="middle">0</text>
  <text x="65" y="165" fill="#475569" font-size="9" text-anchor="middle">0.3</text>
  <text x="65" y="130" fill="#475569" font-size="9" text-anchor="middle">0.6</text>
  <text x="65" y="95" fill="#475569" font-size="9" text-anchor="middle">0.9</text>
  <text x="65" y="60" fill="#475569" font-size="9" text-anchor="middle">1.2</text>
  <!-- cD axis labels -->
  <text x="140" y="252" fill="#475569" font-size="9" text-anchor="middle">0.01</text>
  <text x="210" y="252" fill="#475569" font-size="9" text-anchor="middle">0.03</text>
  <text x="310" y="252" fill="#475569" font-size="9" text-anchor="middle">0.06</text>
  <text x="420" y="252" fill="#475569" font-size="9" text-anchor="middle">0.10</text>
  <!-- Polar curve -->
  <path d="M90,200 Q130,190 150,165 Q175,130 195,100 Q215,75 230,58 Q245,48 250,50 Q265,60 280,80 Q310,115 350,155 Q390,200 430,240" fill="none" stroke="#22c55e" stroke-width="2.5"/>
  <!-- Rückenflug area (below x-axis) -->
  <path d="M90,200 Q80,215 78,225" fill="none" stroke="#22c55e" stroke-width="2.5" stroke-dasharray="4,3"/>
  <!-- Punkt 2: cL=0 (Sturzflug) -->
  <circle cx="90" cy="200" r="5" fill="#facc15"/>
  <text x="95" y="196" fill="#facc15" font-size="9" font-weight="bold">2: cL=0 Sturzflug</text>
  <!-- Punkt 4: bestes Gleiten -->
  <line x1="70" y1="240" x2="195" y2="100" stroke="#f472b6" stroke-width="1.5" stroke-dasharray="5,3"/>
  <circle cx="195" cy="100" r="5" fill="#f472b6"/>
  <text x="200" y="97" fill="#f472b6" font-size="9" font-weight="bold">4: Bestes Gleiten</text>
  <text x="200" y="108" fill="#f9a8d4" font-size="9">(Ursprungstangente)</text>
  <!-- Punkt 5: min. Geschw -->
  <circle cx="250" cy="50" r="5" fill="#fb923c"/>
  <text x="255" y="48" fill="#fb923c" font-size="9" font-weight="bold">5: cL,max</text>
  <text x="255" y="59" fill="#fdba74" font-size="9">Min. Geschw. / Stall-Grenze</text>
  <!-- Punkt 3: min. Widerstand -->
  <line x1="70" y1="240" x2="196" y2="105" stroke="#7c3aed" stroke-width="1" stroke-dasharray="3,3"/>
  <circle cx="145" cy="165" r="4" fill="#a78bfa"/>
  <text x="108" y="162" fill="#a78bfa" font-size="9">3: cD,min</text>
  <!-- cL/cD max tangent label -->
  <text x="135" y="135" fill="#f472b6" font-size="9" transform="rotate(-55,135,135)">cL/cD = max</text>
  <!-- Infobox -->
  <rect x="300" y="40" width="185" height="120" rx="5" fill="#1a1a2e" stroke="#475569" stroke-width="1"/>
  <text x="392" y="57" fill="white" font-size="10" font-weight="bold" text-anchor="middle">Charakterist. Punkte:</text>
  <text x="310" y="73" fill="#facc15" font-size="9">● 2: cL = 0 → Sturzflug / Rückenflug</text>
  <text x="310" y="87" fill="#f472b6" font-size="9">● 4: cL/cD max → Bestes Gleiten</text>
  <text x="310" y="101" fill="#a78bfa" font-size="9">● 3: cD min → Schnellstes Gleiten</text>
  <text x="310" y="115" fill="#fb923c" font-size="9">● 5: cL max → Vmin (Stall)</text>
  <text x="310" y="129" fill="#22c55e" font-size="9">● 6: Überzogener Flugzustand</text>
  <text x="310" y="149" fill="#94a3b8" font-size="9">cD-Achse: immer positiv</text>
  <text x="310" y="160" fill="#94a3b8" font-size="9">cL-Achse: negativ möglich</text>
</svg>"""

SVG_WIDERSTANDSFORMEN = """<svg viewBox="0 0 540 220" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="220" fill="#0d1623" rx="10"/>
  <text x="270" y="20" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Widerstandsformen im Überblick</text>
  <!-- Gesamtwiderstand bars -->
  <!-- Low speed -->
  <rect x="40" y="50" width="40" height="100" fill="#3b82f6" opacity="0.8" rx="3"/>
  <rect x="40" y="80" width="40" height="70" fill="#3b82f6" opacity="0.4" rx="3"/>
  <text x="60" y="165" fill="#93c5fd" font-size="9" text-anchor="middle">Niedrig-V</text>
  <!-- High speed -->
  <rect x="110" y="80" width="40" height="70" fill="#22c55e" opacity="0.8" rx="3"/>
  <rect x="110" y="50" width="40" height="100" fill="#22c55e" opacity="0.4" rx="3"/>
  <text x="130" y="165" fill="#86efac" font-size="9" text-anchor="middle">Hoch-V</text>
  <!-- Legend -->
  <rect x="200" y="50" width="12" height="12" fill="#f87171" rx="2"/>
  <text x="218" y="61" fill="#f87171" font-size="10">Induzierter Widerstand</text>
  <text x="218" y="73" fill="#fca5a5" font-size="9">↑ bei niedrigem v, hohem Auftrieb</text>
  <rect x="200" y="88" width="12" height="12" fill="#fb923c" rx="2"/>
  <text x="218" y="99" fill="#fb923c" font-size="10">Formwiderstand</text>
  <text x="218" y="111" fill="#fdba74" font-size="9">Abhängig von Körperform</text>
  <rect x="200" y="126" width="12" height="12" fill="#facc15" rx="2"/>
  <text x="218" y="137" fill="#facc15" font-size="10">Reibungswiderstand</text>
  <text x="218" y="149" fill="#fde68a" font-size="9">Grenzschicht an Oberfläche</text>
  <rect x="200" y="164" width="12" height="12" fill="#a78bfa" rx="2"/>
  <text x="218" y="175" fill="#a78bfa" font-size="10">Interferenzwiderstand</text>
  <text x="218" y="187" fill="#c4b5fd" font-size="9">Rumpf-Tragflächen-Verbindung</text>
  <!-- Formula box -->
  <rect x="380" y="50" width="140" height="80" rx="5" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1"/>
  <text x="450" y="67" fill="white" font-size="10" font-weight="bold" text-anchor="middle">Gesamtwiderstand</text>
  <text x="450" y="82" fill="#93c5fd" font-size="10" text-anchor="middle">= Profilwiderstand</text>
  <text x="450" y="96" fill="#93c5fd" font-size="10" text-anchor="middle">+ Induzierter Widerstand</text>
  <text x="450" y="110" fill="#facc15" font-size="9" font-weight="bold" text-anchor="middle">→ Minimum bei opt. Geschw.</text>
  <!-- Arrow speed direction -->
  <text x="60" y="188" fill="#94a3b8" font-size="10" text-anchor="middle">Langsam</text>
  <line x1="80" y1="185" x2="130" y2="185" stroke="#94a3b8" stroke-width="1.5" marker-end="url(#arrW)"/>
  <text x="130" y="188" fill="#94a3b8" font-size="10">Schnell</text>
  <defs>
    <marker id="arrW" markerWidth="6" markerHeight="6" refX="3" refY="3" orient="auto">
      <path d="M0,0 L6,3 L0,6 Z" fill="#94a3b8"/>
    </marker>
  </defs>
</svg>"""

SVG_DREI_ACHSEN = """<svg viewBox="0 0 560 280" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:560px;font-family:system-ui,sans-serif">
  <rect width="560" height="280" fill="#0d1623" rx="10"/>
  <text x="280" y="20" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Abb. 42 – Die drei Flugzeugachsen</text>
  <!-- Plane top view (schematic) -->
  <g transform="translate(220,140)">
    <!-- Rumpf -->
    <ellipse cx="0" cy="0" rx="70" ry="15" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.5"/>
    <!-- Tragflächen -->
    <rect x="-10" y="-80" width="20" height="160" rx="3" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.5"/>
    <!-- Leitwerk -->
    <rect x="45" y="-30" width="20" height="60" rx="3" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1"/>
    <rect x="50" y="-45" width="15" height="12" rx="2" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1"/>
  </g>
  <!-- Längsachse (x - rote, von Nase zum Heck) -->
  <line x1="100" y1="140" x2="410" y2="140" stroke="#ef4444" stroke-width="2.5"/>
  <polygon points="100,140 116,134 116,146" fill="#ef4444"/>
  <polygon points="410,140 394,134 394,146" fill="#ef4444"/>
  <text x="450" y="136" fill="#ef4444" font-size="10" font-weight="bold">Längsachse</text>
  <text x="450" y="148" fill="#fca5a5" font-size="9">→ Rollen (Querruder)</text>
  <!-- Querachse (y - grün, durch Tragflächen) -->
  <line x1="220" y1="40" x2="220" y2="240" stroke="#22c55e" stroke-width="2.5"/>
  <polygon points="220,40 214,56 226,56" fill="#22c55e"/>
  <polygon points="220,240 214,224 226,224" fill="#22c55e"/>
  <text x="230" y="35" fill="#22c55e" font-size="10" font-weight="bold">Querachse</text>
  <text x="230" y="47" fill="#86efac" font-size="9">→ Nicken (Höhenruder)</text>
  <!-- Hochachse (z - gelb, durch Rumpf oben-unten) -->
  <!-- Show as circle since perpendicular -->
  <circle cx="220" cy="140" r="18" fill="none" stroke="#facc15" stroke-width="2.5" stroke-dasharray="6,3"/>
  <circle cx="220" cy="140" r="4" fill="#facc15"/>
  <text x="245" y="170" fill="#facc15" font-size="10" font-weight="bold">Hochachse ⊙</text>
  <text x="245" y="182" fill="#fde68a" font-size="9">→ Gieren (Seitenruder)</text>
  <!-- Infobox movements -->
  <rect x="14" y="192" width="155" height="70" rx="5" fill="#1a1a2e" stroke="#475569" stroke-width="1"/>
  <text x="91" y="208" fill="white" font-size="10" font-weight="bold" text-anchor="middle">Drehbewegungen</text>
  <text x="20" y="222" fill="#ef4444" font-size="9">● Längsachse → Rollen</text>
  <text x="20" y="236" fill="#22c55e" font-size="9">● Querachse → Nicken</text>
  <text x="20" y="250" fill="#facc15" font-size="9">● Hochachse → Gieren</text>
  <text x="91" y="258" fill="#475569" font-size="8" text-anchor="middle">Alle Achsen durch Schwerpunkt</text>
</svg>"""

SVG_STABILITAET = """<svg viewBox="0 0 540 200" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="200" fill="#0d1623" rx="10"/>
  <text x="270" y="20" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Stabilitätsbegriffe – Kugel-Analogie (Abb. 39)</text>
  <!-- Stabile Lage -->
  <rect x="20" y="40" width="140" height="140" rx="6" fill="#0d2818" stroke="#22c55e" stroke-width="1"/>
  <text x="90" y="58" fill="#22c55e" font-size="10" font-weight="bold" text-anchor="middle">STABIL</text>
  <path d="M30 150 Q90 110 150 150" fill="none" stroke="#4ade80" stroke-width="2"/>
  <circle cx="90" cy="118" r="10" fill="#22c55e"/>
  <path d="M90 128 L85 145 M90 128 L95 145" stroke="#22c55e" stroke-width="1.5"/>
  <text x="90" y="185" fill="#86efac" font-size="9" text-anchor="middle">Kehrt nach Störung zurück</text>
  <!-- Indifferente Lage -->
  <rect x="195" y="40" width="140" height="140" rx="6" fill="#1a1a0d" stroke="#facc15" stroke-width="1"/>
  <text x="265" y="58" fill="#facc15" font-size="10" font-weight="bold" text-anchor="middle">INDIFFERENT</text>
  <line x1="215" y1="145" x2="315" y2="145" stroke="#fde68a" stroke-width="2"/>
  <circle cx="265" cy="133" r="10" fill="#facc15"/>
  <path d="M255 143 L245 158 M275 143 L285 158" stroke="#facc15" stroke-width="1.5" stroke-dasharray="3,2"/>
  <text x="265" y="185" fill="#fde68a" font-size="9" text-anchor="middle">Bleibt in neuer Lage</text>
  <!-- Labile Lage -->
  <rect x="370" y="40" width="140" height="140" rx="6" fill="#1a0d0d" stroke="#ef4444" stroke-width="1"/>
  <text x="440" y="58" fill="#ef4444" font-size="10" font-weight="bold" text-anchor="middle">LABIL</text>
  <path d="M380 120 Q440 155 500 120" fill="none" stroke="#f87171" stroke-width="2"/>
  <circle cx="440" cy="148" r="10" fill="#ef4444"/>
  <path d="M433 155 L420 170 M447 155 L460 170" stroke="#ef4444" stroke-width="1.5"/>
  <text x="440" y="185" fill="#fca5a5" font-size="9" text-anchor="middle">Entfernt sich weiter</text>
</svg>"""

SVG_STALL = """<svg viewBox="0 0 540 240" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="240" fill="#0d1623" rx="10"/>
  <text x="270" y="20" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Strömungsabriss (Stall) – Kritischer Anstellwinkel</text>
  <!-- Normal flow -->
  <g transform="translate(20,50)">
    <text x="110" y="14" fill="#22c55e" font-size="10" text-anchor="middle">Normale Anströmung</text>
    <!-- Profil -->
    <path d="M20 60 Q60 35 100 38 Q140 40 180 48 Q200 52 210 60 Q200 68 180 70 Q140 72 100 70 Q60 68 30 72 Q20 72 20 60 Z" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.2"/>
    <!-- Flow arrows - attached -->
    <path d="M10 42 Q60 30 100 30 Q150 28 210 40" fill="none" stroke="#22c55e" stroke-width="1.5" marker-end="url(#a1)"/>
    <path d="M10 50 Q60 42 100 40 Q150 38 210 50" fill="none" stroke="#22c55e" stroke-width="1.2"/>
    <path d="M10 70 Q60 72 100 72 Q150 72 210 72" fill="none" stroke="#22c55e" stroke-width="1.2" marker-end="url(#a1)"/>
    <text x="110" y="100" fill="#86efac" font-size="9" text-anchor="middle">α = 5–10° → Strömung liegt an</text>
    <defs><marker id="a1" markerWidth="5" markerHeight="5" refX="2.5" refY="2.5" orient="auto"><path d="M0,0 L5,2.5 L0,5 Z" fill="#22c55e"/></marker></defs>
  </g>
  <!-- Stall flow -->
  <g transform="translate(270,50)">
    <text x="115" y="14" fill="#ef4444" font-size="10" text-anchor="middle">Überkritischer Anstellwinkel (STALL)</text>
    <!-- Profil - more angled -->
    <path d="M20 70 Q45 30 90 32 Q135 34 175 55 Q195 62 210 70 Q195 78 175 80 Q135 78 90 76 Q45 78 30 82 Q20 82 20 70 Z" fill="#1e3a5f" stroke="#ef4444" stroke-width="1.5"/>
    <!-- Flow arrows - separated on top -->
    <path d="M10 45 Q40 38 70 36 Q85 34 90 34" fill="none" stroke="#f87171" stroke-width="1.5"/>
    <!-- Turbulent separation -->
    <path d="M90 34 Q110 25 120 32 Q130 40 115 48 Q100 55 115 62 Q130 68 145 60 Q160 52 175 55" fill="none" stroke="#f87171" stroke-width="1.2" stroke-dasharray="4,2"/>
    <!-- Underbelly -->
    <path d="M10 80 Q60 82 110 80 Q160 78 210 80" fill="none" stroke="#f87171" stroke-width="1.2" marker-end="url(#a2)"/>
    <text x="115" y="105" fill="#fca5a5" font-size="9" text-anchor="middle">α &gt; krit. Anstellwinkel → Strömung reißt ab</text>
    <defs><marker id="a2" markerWidth="5" markerHeight="5" refX="2.5" refY="2.5" orient="auto"><path d="M0,0 L5,2.5 L0,5 Z" fill="#f87171"/></marker></defs>
  </g>
  <!-- Warning box -->
  <rect x="20" y="165" width="500" height="55" rx="5" fill="#2d0d0d" stroke="#ef4444" stroke-width="1.5"/>
  <text x="270" y="183" fill="#ef4444" font-size="11" font-weight="bold" text-anchor="middle">⚠ Stall = ANSTELLWINKEL-Problem, kein Geschwindigkeitsproblem!</text>
  <text x="270" y="199" fill="#fca5a5" font-size="10" text-anchor="middle">Tritt bei jedem Anstellwinkel &gt; kritisch auf – unabhängig von Geschwindigkeit oder Fluglage</text>
  <text x="270" y="213" fill="#fca5a5" font-size="10" text-anchor="middle">Recovery: Steuerhorn nachgeben (Nase runter) → Anstellwinkel verkleinern → Motorleistung erhöhen</text>
</svg>"""

SVG_LANDEKLAPPEN = """<svg viewBox="0 0 540 230" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="230" fill="#0d1623" rx="10"/>
  <text x="270" y="20" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Landehilfen – Klappentypen</text>
  <!-- Wölbklappe -->
  <g transform="translate(20,40)">
    <text x="85" y="12" fill="#22c55e" font-size="10" font-weight="bold" text-anchor="middle">Wölbklappe</text>
    <path d="M10 40 Q50 20 90 22 Q120 24 140 32 Q150 38 148 40 Q142 48 120 52 Q90 55 50 55 Q20 52 10 40 Z" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.2"/>
    <path d="M130 45 Q138 52 142 60 Q145 68 140 70" fill="none" stroke="#22c55e" stroke-width="2"/>
    <text x="85" y="80" fill="#86efac" font-size="9" text-anchor="middle">Hinterkante ↓ → mehr Wölbung</text>
    <text x="85" y="90" fill="#86efac" font-size="9" text-anchor="middle">Mehr Auftrieb + Widerstand</text>
  </g>
  <!-- Spreizklappen -->
  <g transform="translate(195,40)">
    <text x="80" y="12" fill="#fb923c" font-size="10" font-weight="bold" text-anchor="middle">Spreizklappen</text>
    <path d="M10 40 Q50 20 90 22 Q120 24 140 32 Q150 38 148 40 Q142 48 120 52 Q90 55 50 55 Q20 52 10 40 Z" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.2"/>
    <path d="M90 53 L95 68 Q100 78 98 82" fill="none" stroke="#fb923c" stroke-width="2"/>
    <text x="80" y="80" fill="#fdba74" font-size="9" text-anchor="middle">Unterseite ↓ → hoher Widerstand</text>
    <text x="80" y="90" fill="#fdba74" font-size="9" text-anchor="middle">Als Starthilfe ungeeignet</text>
  </g>
  <!-- Fowler Klappe -->
  <g transform="translate(370,40)">
    <text x="75" y="12" fill="#a78bfa" font-size="10" font-weight="bold" text-anchor="middle">Fowler-Klappe</text>
    <path d="M10 40 Q50 20 90 22 Q115 24 130 32 Q140 38 138 40 Q132 48 115 52 Q90 55 50 55 Q20 52 10 40 Z" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.2"/>
    <path d="M130 48 L140 52 L155 60 Q162 68 158 72" fill="none" stroke="#a78bfa" stroke-width="2"/>
    <rect x="142" y="57" width="16" height="10" rx="2" fill="#2d1a5f" stroke="#a78bfa" stroke-width="1"/>
    <text x="75" y="80" fill="#c4b5fd" font-size="9" text-anchor="middle">Nachhinter-Ausfahren + Spalt</text>
    <text x="75" y="90" fill="#c4b5fd" font-size="9" text-anchor="middle">Mehr Fläche → weniger Mindestgeschw.</text>
  </g>
  <!-- Infobox bottom -->
  <rect x="20" y="155" width="500" height="60" rx="5" fill="#1a1a2e" stroke="#475569" stroke-width="1"/>
  <text x="270" y="172" fill="white" font-size="10" font-weight="bold" text-anchor="middle">Landeklappen-Wirkung (Zusammenfassung)</text>
  <text x="30" y="188" fill="#22c55e" font-size="9">✓ Auftriebsbeiwert steigt → geringere Mindestgeschwindigkeit</text>
  <text x="30" y="202" fill="#fb923c" font-size="9">✓ Widerstand steigt → steilerer Landeanflug möglich</text>
  <text x="30" y="213" fill="#facc15" font-size="9">⚠ Einfahren in Bodennähe gefährlich (Auftrieb bricht ein → Durchsacken)</text>
</svg>"""

SVG_TRUDELN = """<svg viewBox="0 0 540 250" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="250" fill="#0d1623" rx="10"/>
  <text x="270" y="20" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Trudeln – Flugzustand und Ausleiten</text>
  <!-- Spiral path -->
  <path d="M270 50 Q310 70 320 100 Q330 130 310 155 Q285 180 255 175 Q225 168 215 145 Q208 125 220 108 Q235 90 255 92 Q270 93 278 108" fill="none" stroke="#ef4444" stroke-width="2.5" stroke-dasharray="8,4"/>
  <polygon points="278,108 268,96 283,95" fill="#ef4444"/>
  <!-- Plane symbol -->
  <circle cx="310" cy="95" r="8" fill="#1e3a5f" stroke="#f87171" stroke-width="1.5"/>
  <line x1="300" y1="90" x2="320" y2="100" stroke="#f87171" stroke-width="2"/>
  <line x1="306" y1="82" x2="314" y2="108" stroke="#f87171" stroke-width="1.5"/>
  <!-- Trudelachse -->
  <line x1="270" y1="35" x2="270" y2="195" stroke="#facc15" stroke-width="1.5" stroke-dasharray="5,3"/>
  <text x="282" y="48" fill="#facc15" font-size="9">Trudelachse</text>
  <text x="282" y="58" fill="#fde68a" font-size="9">(vertikal)</text>
  <!-- Ausleiten box -->
  <rect x="14" y="50" width="175" height="130" rx="5" fill="#0d1a0d" stroke="#22c55e" stroke-width="1.5"/>
  <text x="101" y="68" fill="#22c55e" font-size="10" font-weight="bold" text-anchor="middle">Ausleiten (Recovery)</text>
  <text x="20" y="86" fill="white" font-size="9">1. Seitenruder gegen Drehrichtung</text>
  <text x="20" y="100" fill="white" font-size="9">2. Querruder NEUTRAL halten</text>
  <text x="20" y="114" fill="white" font-size="9">3. Höhenruder nachgeben</text>
  <text x="20" y="128" fill="white" font-size="9">   (Nase runter – Anströmung)</text>
  <text x="20" y="142" fill="white" font-size="9">4. Nach Stopp: Sturzflug abfangen</text>
  <text x="20" y="156" fill="#fca5a5" font-size="9">5. Motor → Leerlauf während Trudeln</text>
  <text x="101" y="172" fill="#facc15" font-size="8" font-weight="bold" text-anchor="middle">Details im Flughandbuch!</text>
  <!-- Warning box -->
  <rect x="350" y="50" width="170" height="110" rx="5" fill="#2d0d0d" stroke="#ef4444" stroke-width="1.5"/>
  <text x="435" y="68" fill="#ef4444" font-size="10" font-weight="bold" text-anchor="middle">⚠ Gefahren</text>
  <text x="360" y="84" fill="#fca5a5" font-size="9">• Enormer Höhenverlust</text>
  <text x="360" y="98" fill="#fca5a5" font-size="9">• Flachtrudeln: kaum auszuleiten</text>
  <text x="360" y="112" fill="#fca5a5" font-size="9">• Hintere SP-Lage fördert Trudeln</text>
  <text x="360" y="126" fill="#fca5a5" font-size="9">• Rechtsdrehend. Motor verstärkt</text>
  <text x="360" y="140" fill="#fca5a5" font-size="9">  Linkstrudeln</text>
  <text x="360" y="152" fill="#fca5a5" font-size="9">• Kreiselinstrumente beschädigt!</text>
  <!-- Label -->
  <text x="270" y="220" fill="#94a3b8" font-size="9" text-anchor="middle">Trudeln = einseitiger Strömungsabriss + Rotation um vertikale Achse (nicht durch SP)</text>
  <text x="270" y="234" fill="#94a3b8" font-size="9" text-anchor="middle">Steiltrudeln (&gt;50° Längsneigung) vs. Flachtrudeln (flacherer Sinkwinkel, gefährlicher)</text>
</svg>"""

SVG_KURVENFLUG = """<svg viewBox="0 0 540 250" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:540px;font-family:system-ui,sans-serif">
  <rect width="540" height="250" fill="#0d1623" rx="10"/>
  <text x="270" y="20" fill="white" font-size="12" font-weight="bold" text-anchor="middle">Kurvenflug – Kräfte und Lastvielfache</text>
  <!-- Plane tilted -->
  <g transform="translate(230,120) rotate(-30)">
    <rect x="-35" y="-8" width="70" height="16" rx="8" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.5"/>
    <rect x="-8" y="-40" width="16" height="80" rx="3" fill="#1e3a5f" stroke="#3b82f6" stroke-width="1.5"/>
  </g>
  <!-- Auftriebsvektor -->
  <line x1="230" y1="120" x2="195" y2="40" stroke="#22c55e" stroke-width="2.5"/>
  <polygon points="195,40 188,56 202,56" fill="#22c55e"/>
  <text x="148" y="62" fill="#22c55e" font-size="10" font-weight="bold">Auftrieb A</text>
  <!-- Vertical component -->
  <line x1="230" y1="120" x2="230" y2="50" stroke="#22c55e" stroke-width="1.5" stroke-dasharray="4,2"/>
  <text x="235" y="80" fill="#86efac" font-size="9">Vert. Komponente</text>
  <text x="235" y="90" fill="#86efac" font-size="9">= Gewicht kompens.</text>
  <!-- Horizontal component = Zentripetalkraft -->
  <line x1="230" y1="120" x2="195" y2="120" stroke="#f472b6" stroke-width="1.5" stroke-dasharray="4,2"/>
  <text x="145" y="118" fill="#f472b6" font-size="9">Horiz. Komp.</text>
  <text x="145" y="130" fill="#f472b6" font-size="9">= Zentripetalkraft</text>
  <!-- Zentrifugalkraft -->
  <line x1="230" y1="120" x2="310" y2="120" stroke="#fb923c" stroke-width="2"/>
  <polygon points="310,120 294,114 294,126" fill="#fb923c"/>
  <text x="312" y="116" fill="#fb923c" font-size="9" font-weight="bold">Zentrifugalkraft</text>
  <!-- Gewicht -->
  <line x1="230" y1="120" x2="230" y2="195" stroke="#f87171" stroke-width="2"/>
  <polygon points="230,195 224,179 236,179" fill="#f87171"/>
  <text x="235" y="165" fill="#f87171" font-size="9" font-weight="bold">Gewicht</text>
  <!-- Scheingewicht = Resultierende -->
  <line x1="230" y1="195" x2="195" y2="120" stroke="#facc15" stroke-width="2" stroke-dasharray="4,2"/>
  <text x="178" y="162" fill="#facc15" font-size="9">Scheingewicht</text>
  <text x="178" y="173" fill="#fde68a" font-size="9">(Resultierende)</text>
  <!-- Load factor table -->
  <rect x="355" y="40" width="160" height="120" rx="5" fill="#1a1a2e" stroke="#475569" stroke-width="1"/>
  <text x="435" y="57" fill="white" font-size="10" font-weight="bold" text-anchor="middle">Lastvielfach n</text>
  <line x1="355" y1="62" x2="515" y2="62" stroke="#475569" stroke-width="0.5"/>
  <text x="390" y="76" fill="#94a3b8" font-size="9" text-anchor="middle">Querlage</text>
  <text x="475" y="76" fill="#94a3b8" font-size="9" text-anchor="middle">n =1/cos(γ)</text>
  <text x="390" y="92" fill="white" font-size="9" text-anchor="middle">0°</text>
  <text x="475" y="92" fill="#22c55e" font-size="9" text-anchor="middle">1,0 g (100%)</text>
  <text x="390" y="108" fill="white" font-size="9" text-anchor="middle">45°</text>
  <text x="475" y="108" fill="#facc15" font-size="9" text-anchor="middle">1,4 g (119%)</text>
  <text x="390" y="124" fill="white" font-size="9" text-anchor="middle">60°</text>
  <text x="475" y="124" fill="#fb923c" font-size="9" text-anchor="middle">2,0 g (141%)</text>
  <text x="390" y="140" fill="white" font-size="9" text-anchor="middle">75°</text>
  <text x="475" y="140" fill="#ef4444" font-size="9" text-anchor="middle">3,9 g (197%)</text>
  <text x="435" y="155" fill="#f472b6" font-size="8" text-anchor="middle">Stallgeschw. steigt mit √n</text>
  <!-- Label -->
  <text x="270" y="220" fill="#94a3b8" font-size="9" text-anchor="middle">Im Kurvenflug: Scheingewichtskraft (Resultierende aus Gewicht + Zentrifugalkraft) immer senkrecht nach unten in den Sitz</text>
  <text x="270" y="234" fill="#94a3b8" font-size="9" text-anchor="middle">Je größer Schräglage → desto höher Lastvielfach → desto höher benötigte Auftriebskraft und Überziegeschwindigkeit</text>
</svg>"""

# ══════════════════════════════════════════════════════════════════════════════
# KAPITEL-INHALTE
# ══════════════════════════════════════════════════════════════════════════════

CHAPTERS = [

  # ─────────────────────────────────────────────────────────────────────────
  # KAP 2.1/2.2 – TRAGFLÜGELGEOMETRIE & STRÖMUNGSMERKMALE
  # ─────────────────────────────────────────────────────────────────────────
  {
    "id": "aero-profil-geometrie",
    "title": "Kap. 2 – Tragflügelprofil: Geometrie & Luftströmung",
    "sort_order": 10,
    "exam": True,
    "sections": [
      {"type":"heading", "content":"Geometrie des Tragflügelprofils", "extra":"Grundbegriffe für Auftrieb, Widerstand und Stall"},
      {"type":"diagram", "content": SVG_PROFIL_GEOMETRIE, "extra":"Abb. 16 – Markante Punkte am Tragflügelprofil"},
      {"type":"subheading", "content":"Wichtige Begriffe (Abb. 16)"},
      {"type":"table_row","content":"Profilsehne","extra":"Verbindungslinie zwischen Profilvorder- und -hinterkante, unabhängig von der Krümmung"},
      {"type":"table_row","content":"Profiltiefe","extra":"Länge des Profils in Richtung Profilsehne; Länge quer zur Strömungsrichtung = Spannweite"},
      {"type":"table_row","content":"Profildicke","extra":"Höhe des Profils, senkrecht zur Profilsehne gemessen"},
      {"type":"table_row","content":"Dickenrücklage","extra":"Abstand der dicksten Profilstelle von der Profilnase"},
      {"type":"table_row","content":"Anstellwinkel α","extra":"Winkel zwischen Strömungsrichtung und Profilsehne – wichtigste aerodynamische Steuergröße"},
      {"type":"table_row","content":"Einstellwinkel","extra":"Fest eingebauter Winkel zwischen Profilsehne und Flugzeuglängsachse"},
      {"type":"subheading","content":"Merkmale der Luftströmung (Kap. 2.2)"},
      {"type":"text","content":"Am Staupunkt teilt sich die anströmende Luft: Ein Teil strömt über die Oberseite, der andere unter die Unterseite des Profils. Die Strömung verläuft zunächst laminar und schlägt am Umschlagpunkt in eine turbulente Grenzschicht um."},
      {"type":"fact","content":"Im Langsamflug muss der Anstellwinkel erhöht werden (z.B. durch Landeklappen), um ausreichend Auftrieb bei niedrigerer Geschwindigkeit zu erzeugen."},
      {"type":"text","content":"Im Reiseflug ist der Anstellwinkel klein (Hochgeschwindigkeit benötigt wenig Auftrieb). Umgekehrt erfordert Langsamflug (Landenanflug) einen größeren Anstellwinkel."},
      {"type":"warning","content":"Wird der Anstellwinkel zu groß (kritischer Anstellwinkel), reißt die Strömung ab. Die Ablösung beginnt auf der Profiloberseite – zuerst im hinteren Bereich, dann nach vorne wandernd. Dies führt zum Strömungsabriss (Stall)."},
      {"type":"fact","content":"Der Umschlagpunkt liegt im normalen Profil kurz und befindet sich im Bereich der Druckminima (Dickenrücklage). Im Laminarprofil ist die Dickenrücklage weiter hinten, wodurch der Umschlagpunkt nach hinten verschoben wird."},
      {"type":"infobox","content":"Profilform und Flugaufgabe: Schnellflugprofil = schlank, wenig Wölbung, geringer Formwiderstand. Dickes Profil = mehr Auftrieb + Widerstand, besser für Langsamflug.","extra":"Profilwahl"},
      {"type":"focus","content":"Anstellwinkel klein → Schnellflug / Reiseflug; Anstellwinkel groß → Langsamflug / Landung; zu groß → Stall"},
    ],
    "quiz": [
      {"q":"Was versteht man unter dem 'Anstellwinkel' eines Tragflügelprofils?","opts":["Den Winkel zwischen Profilsehne und Flugzeuglängsachse","Den Winkel zwischen Strömungsrichtung und Profilsehne","Den Winkel zwischen Ober- und Unterseite des Profils","Den Winkel zwischen Tragfläche und Horizontale"],"ans":1,"exp":"Der Anstellwinkel α ist der Winkel zwischen der Anströmrichtung (= Strömungsgeschwindigkeit) und der Profilsehne.","official":True},
      {"q":"Was ist die 'Dickenrücklage' eines Profils?","opts":["Die Gesamtdicke des Profils","Die Länge der Profilsehne","Der Abstand der dicksten Profilstelle von der Profilnase","Der Winkel zwischen Profilsehne und Flugzeuglängsachse"],"ans":2,"exp":"Dickenrücklage = Abstand der dicksten Stelle des Profils (gemessen entlang der Profilsehne) von der Profilnase.","official":True},
      {"q":"Wo am Tragflügel wird der Umschlagpunkt (laminare→turbulente Grenzschicht) zuerst erreicht?","opts":["Unterseite","Oberseite","Ober- und Unterseite gleichzeitig","In der turbulenten Grenzschicht"],"ans":1,"exp":"Die Luft strömt auf der Oberseite schneller, die kritische Geschwindigkeit wird dort zuerst überschritten → Umschlagpunkt zuerst auf der Oberseite.","official":True},
      {"q":"Wo am Tragflügel beginnt die Strömungsablösung bei zu großem Anstellwinkel?","opts":["Unterseite","Oberseite","Ober- und Unterseite gleichzeitig","In der Grenzschicht vorne"],"ans":1,"exp":"Bei zu großem Anstellwinkel beginnt die Ablösung auf der Profiloberseite, zuerst im Hinterkantenbereich, dann nach vorne wandernd.","official":True},
      {"q":"Was passiert mit dem Anstellwinkel, wenn ein Flugzeug im Langsamflug (z.B. Landeanflug) dieselbe Auftriebskraft erzeugen muss wie im Reiseflug?","opts":["Er bleibt gleich","Er muss vergrößert werden","Er muss verkleinert werden","Er hängt nur von der Motorleistung ab"],"ans":1,"exp":"Da die Auftriebsformel L = ½ρv²·S·cL zeigt, dass bei geringerer Geschwindigkeit v der Auftriebsbeiwert cL erhöht werden muss – dies geschieht durch Vergrößern des Anstellwinkels.","official":False},
      {"q":"Was versteht man unter 'Einstellwinkel'?","opts":["Der Anstellwinkel im Reiseflug","Der fest verbaute Winkel zwischen Profilsehne und Flugzeuglängsachse","Der Winkel zwischen Höhenleitwerk und Rumpf","Der maximale Anstellwinkel"],"ans":1,"exp":"Der Einstellwinkel ist konstruktiv fest vorgegeben: der Winkel zwischen der Profilsehne und der Flugzeuglängsachse.","official":True},
    ],
    "flashcards": [
      {"front":"Was ist der Anstellwinkel α?","back":"Der Winkel zwischen der Anströmrichtung (Geschwindigkeit) und der Profilsehne des Tragflügels."},
      {"front":"Was bewirkt ein zu großer Anstellwinkel?","back":"Die Strömung kann der Profilform nicht mehr folgen und reißt ab (Stall) → Auftriebsverlust."},
      {"front":"Wo beginnt die Strömungsablösung?","back":"Auf der Profiloberseite – zuerst im Hinterkantenbereich, dann nach vorne wandernd."},
      {"front":"Wozu dienen Laminarprofil-Eigenschaften?","back":"Die Dickenrücklage liegt weiter hinten → Umschlagpunkt nach hinten verschoben → weniger Reibungswiderstand bei Reisefluggeschwindigkeit."},
    ]
  },

  # ─────────────────────────────────────────────────────────────────────────
  # KAP 2.3/2.4 – AUFTRIEB, WIDERSTAND, POLARDIAGRAMM
  # ─────────────────────────────────────────────────────────────────────────
  {
    "id": "aero-auftrieb-widerstand",
    "title": "Kap. 2.3/2.4 – Auftrieb, Widerstand & Polardiagramm",
    "sort_order": 20,
    "exam": True,
    "sections": [
      {"type":"heading","content":"Auftrieb und Widerstand","extra":"Formeln, Abhängigkeiten und das Lilienthal'sche Polardiagramm"},
      {"type":"diagram","content":SVG_AUFTRIEB_WIDERSTAND,"extra":"Vier Kräfte im Geradeausflug"},
      {"type":"subheading","content":"2.3 Die Auftriebsformel"},
      {"type":"text","content":"Die Auftriebskraft L und die Widerstandskraft D hängen von denselben Parametern ab – daher nennt man sie auch 'zwei Seiten einer Medaille'."},
      {"type":"table_row","content":"Auftrieb L","extra":"L = ½ · ρ · v² · S · cL — steigt mit v², Luftdichte ρ, Flügelfläche S und Auftriebsbeiwert cL"},
      {"type":"table_row","content":"Widerstand D","extra":"D = ½ · ρ · v² · S · cD — gleiche Struktur; cD hängt vom Anstellwinkel ab"},
      {"type":"table_row","content":"Auftriebsbeiwert cL","extra":"Dimensionslos; kann positiv, null (Sturzflug) oder negativ (Rückenflug) sein"},
      {"type":"table_row","content":"Widerstandsbeiwert cD","extra":"Immer positiv oder null; steigt bei sehr großen Anstellwinkeln stark an"},
      {"type":"text","content":"Eine höhere Luftdichte (z.B. niedrige Flughöhe, niedrige Temperatur) erzeugt bei gleicher Geschwindigkeit mehr Auftrieb und mehr Widerstand. In großer Höhe muss die Geschwindigkeit erhöht werden, um gleiche Auftriebskraft zu erzielen."},
      {"type":"fact","content":"Auftrieb kann nach 'oben' (normale Lage) und nach 'unten' (Rückenflug mit negativem Anstellwinkel) erzeugt werden. Bei null Anstellwinkel ist cL = 0 für symmetrische Profile."},
      {"type":"subheading","content":"2.3.3 Lilienthal'sches Polardiagramm"},
      {"type":"diagram","content":SVG_POLARDIAGRAMM,"extra":"Abb. 19 – Polardiagramm: Auftrieb (cL) vs. Widerstand (cD) für verschiedene Anstellwinkel"},
      {"type":"text","content":"Im Polardiagramm wird der Auftriebsbeiwert cL gegen den Widerstandsbeiwert cD für jeden Anstellwinkel aufgetragen. Das Diagramm zeigt alle für die Flugleistung wichtigen Betriebspunkte."},
      {"type":"table_row","content":"Punkt 2","extra":"cL = 0: Sturzflug (kein Auftrieb); bei negativem cL: Rückenflug"},
      {"type":"table_row","content":"Punkt 4","extra":"Bestes Gleiten: Tangente vom Ursprung an die Polare → maximales cL/cD-Verhältnis = Gleitzahl"},
      {"type":"table_row","content":"Punkt 3","extra":"Geringster Widerstand (cD,min): schnellstes Gleiten, aber schlechter Gleitwinkel"},
      {"type":"table_row","content":"Punkt 5","extra":"cL,max: geringste Fluggeschwindigkeit, kurz vor dem Stall"},
      {"type":"infobox","content":"Große Gleitzahl = kleiner Gleitwinkel = gutes Gleiten. Segelflugzeuge: Gleitzahlen bis 1:60 und höher. Je größer die Gleitzahl, desto weiter kommt das Flugzeug aus einer gegebenen Höhe.","extra":"Gleitzahl"},
      {"type":"subheading","content":"2.4 Widerstandsformen"},
      {"type":"diagram","content":SVG_WIDERSTANDSFORMEN,"extra":"Schematische Darstellung der Widerstandsanteile"},
      {"type":"text","content":"Der Gesamtwiderstand eines Luftfahrzeugs setzt sich aus mehreren Anteilen zusammen. Für die Prüfung wichtig ist das unterschiedliche Verhalten mit der Geschwindigkeit."},
      {"type":"table_row","content":"Profilwiderstand","extra":"Form- + Reibungswiderstand + Interferenzwiderstand; steigt mit v²"},
      {"type":"table_row","content":"Formwiderstand","extra":"Abhängig von der Querschnittsform; Stromlinienform minimiert ihn"},
      {"type":"table_row","content":"Reibungswiderstand","extra":"Grenzschicht an Oberfläche; rauere Oberfläche → mehr Reibung; laminare Grenzschicht ≺ turbulente"},
      {"type":"table_row","content":"Interferenzwiderstand","extra":"Entsteht an Verbindungsstellen (Rumpf-Tragfläche); individuell je Flugzeug"},
      {"type":"table_row","content":"Induzierter Widerstand","extra":"Durch Auftrieb erzeugt (Randwirbel an Flächenenden); nimmt mit v zu bei niedrigen Geschwindigkeiten"},
      {"type":"fact","content":"Der Gesamtwiderstand hat ein Minimum bei einer bestimmten Geschwindigkeit (Betriebsoptimum). Bei geringen Geschwindigkeiten dominiert der induzierte Widerstand, bei hohen dominiert der schädliche (Profil-)Widerstand."},
      {"type":"warning","content":"Niederschläge wie Eis, Reif oder Schnee auf den Tragflächen erhöhen den Reibungswiderstand erheblich und müssen vor dem Flug unbedingt entfernt werden."},
      {"type":"focus","content":"Prüfungsschwerpunkt: Unterschied induzierter vs. parasitärer Widerstand; Verhalten beider mit Geschwindigkeit; Gleitzahl und Lilienthal-Polare"},
    ],
    "quiz": [
      {"q":"Was ist die 'Gleitzahl' eines Flugzeugs?","opts":["Das Verhältnis von Auftrieb zu Gewicht im Kurvenflug","Das Verhältnis cL/cD – also Auftrieb zu Widerstand; entspricht auch zurückgelegter Horizontalstrecke pro Höhenmeter","Die maximale Sinkrate bei Motorausfall","Die Stallgeschwindigkeit im Geradeausflug"],"ans":1,"exp":"Gleitzahl = cL/cD = zurückgelegte horizontale Strecke pro Höhenverlust (z.B. 1:30 = 30m horizontal pro 1m Höhenverlust).","official":True},
      {"q":"Ist es möglich, Auftrieb ohne Widerstand zu erzeugen?","opts":["Ja, mit speziellen Profilen","Nein","Nur bei Überschall","Nur bei laminarer Grenzschicht"],"ans":1,"exp":"Nein – Auftrieb und Widerstand sind zwei Seiten derselben Medaille. Wo Auftrieb entsteht, entsteht immer auch Widerstand.","official":True},
      {"q":"Welcher Widerstand hängt unmittelbar mit der Auftriebserzeugung zusammen?","opts":["Formwiderstand","Reibungswiderstand","Induzierter Widerstand","Interferenzwiderstand"],"ans":2,"exp":"Der induzierte Widerstand entsteht durch die Auftriebserzeugung (Randwirbel); er ist direkt mit dem Auftrieb verknüpft.","official":True},
      {"q":"Wie verhält sich der induzierte Widerstand bei zunehmender Fluggeschwindigkeit?","opts":["Er steigt quadratisch","Er bleibt konstant","Er sinkt (da geringerer Auftriebsbedarf bei höherer v)","Er hängt nicht von der Geschwindigkeit ab"],"ans":2,"exp":"Mit zunehmender Geschwindigkeit ist weniger Auftriebsbeiwert nötig → weniger Randwirbel → induzierter Widerstand sinkt.","official":True},
      {"q":"Wie ermittelt man die Geschwindigkeit des besten Gleitens aus dem Lilienthal'schen Polardiagramm?","opts":["Am höchsten Punkt der Polarkurve","Durch Tangente vom Koordinatenursprung an die Polarkurve","Am tiefsten Punkt der Polarkurve","An der Stelle des kleinsten cD-Werts"],"ans":1,"exp":"Die Ursprungstangente an die Polare markiert den Punkt cL/cD = maximum → Geschwindigkeit des besten Gleitens.","official":True},
      {"q":"Welche Fläche geht in die Formel zur Berechnung des Luftwiderstands ein?","opts":["Senkrecht zur Strömungsrichtung projizierte Fläche (Stirnfläche)","Horizontale Flügelfläche von oben","Gesamte Oberfläche des Flugzeugs","Querschnittsfläche des Rumpfes"],"ans":0,"exp":"In die Widerstandsformel D = ½ρv²·S·cD geht die in Strömungsrichtung projizierte (Stirn-)Fläche ein.","official":True},
      {"q":"Welche Fläche geht in die Formel zur Berechnung der Auftriebskraft ein?","opts":["Stirnfläche (in Strömungsrichtung)","Senkrecht zur Strömungsrichtung projizierte Fläche (Draufsicht)","Horizontale Flügelfläche (von oben gesehen)","Oberfläche der Unterseite"],"ans":2,"exp":"In die Auftriebsformel L = ½ρv²·S·cL geht die senkrecht zur Strömungsrichtung projizierte Fläche (Grundriss = Draufsicht) ein.","official":True},
      {"q":"Welche Werte kann der Auftriebsbeiwert cL annehmen?","opts":["Nur positive Werte","Nur negative Werte","Positive, Null und negative Werte","Nur Werte zwischen 0 und 1"],"ans":2,"exp":"cL kann positiv (normaler Auftrieb), null (Sturzflug bei symmetrischem Profil) oder negativ (Rückenflug) sein.","official":True},
      {"q":"Welche Werte kann der Widerstandsbeiwert cD annehmen?","opts":["Nur positive Werte (niemals null oder negativ)","Positive und negative Werte","Null und positive Werte","Beliebige Werte"],"ans":0,"exp":"cD ist immer positiv – Widerstand wirkt immer entgegen der Bewegungsrichtung, kann nicht negativ sein.","official":True},
    ],
    "flashcards": [
      {"front":"Was ist der Unterschied zwischen induziertem und parasitärem Widerstand?","back":"Induzierter Widerstand: durch Auftriebserzeugung (Randwirbel) – sinkt mit steigender v. Parasitärer (schädlicher) Widerstand: Form-, Reib-, Interferenzwiderstand – steigt mit v²."},
      {"front":"Formel für Auftrieb?","back":"L = ½ · ρ · v² · S · cL (Luftdichte × Geschwindigkeit² × Flügelfläche × Auftriebsbeiwert × ½)"},
      {"front":"Was zeigt das Lilienthal'sche Polardiagramm?","back":"Den Zusammenhang zwischen Auftriebsbeiwert cL und Widerstandsbeiwert cD für verschiedene Anstellwinkel. Spezielle Punkte: bestes Gleiten (Ursprungstangente), minimaler Widerstand, maximaler Auftrieb (Stall-Grenze)."},
      {"front":"Wie ist die Gleitzahl definiert?","back":"Gleitzahl = cL/cD = horizontal zurückgelegte Strecke / Höhenverlust. Große Gleitzahl = flacher Gleitwinkel = gut."},
    ]
  },

  # ─────────────────────────────────────────────────────────────────────────
  # KAP 2.5 – KONSTRUKTIONSMERKMALE (PROFILE, FLÜGELFORM, AERODYN. HILFEN)
  # ─────────────────────────────────────────────────────────────────────────
  {
    "id": "aero-konstruktion",
    "title": "Kap. 2.5 – Konstruktionsmerkmale: Profile, Flügelform & aerodyn. Hilfen",
    "sort_order": 30,
    "exam": True,
    "sections": [
      {"type":"heading","content":"Konstruktionsmerkmale des Tragflügels","extra":"Profile, Flügelgeometrie und aerodynamische Hilfsmittel"},
      {"type":"subheading","content":"2.5.1 Tragflügelprofile"},
      {"type":"text","content":"Das Profil für einen Tragflügel wird für den gewünschten Betriebsbereich optimiert. Für Reiseflug werden schlanke Profile mit wenig Wölbung und geringem Formwiderstand gewählt (Schnellflugprofil). Dicke Profile erzeugen mehr Auftrieb, aber auch mehr Widerstand."},
      {"type":"table_row","content":"Schnellflugprofil","extra":"Schlank, geringe Wölbung, niedriger Formwiderstand; für Reiseflug optimiert"},
      {"type":"table_row","content":"Laminarprofil","extra":"Dickenrücklage weit hinten → Umschlagpunkt nach hinten verschoben → weniger Reibungswiderstand im Reiseflug; aber weniger gutmütig"},
      {"type":"table_row","content":"Normalprofil","extra":"Dickenrücklage ca. 30% Profiltiefe; gutmütigere Abriss­eigenschaften"},
      {"type":"subheading","content":"2.5.2 Flügelformen"},
      {"type":"text","content":"Flügelstreckung (Seitenverhältnis) = Spannweite / mittlere Profiltiefe. Große Streckung → langer Flügel → geringer induzierter Widerstand (z.B. Segelflugzeuge)."},
      {"type":"table_row","content":"Geometrische Schränkung","extra":"Einstellwinkel verringert sich zum Flügelende hin → äußere Fläche reißt zuletzt ab → besseres Abrissverhalten"},
      {"type":"table_row","content":"Aerodynamische Schränkung","extra":"Profilform ändert sich zum Flügelende hin bei gleichem Einstellwinkel → ähnliche Wirkung wie geometrische Schränkung"},
      {"type":"table_row","content":"Trapezform","extra":"Praktischer Kompromiss aus Streckung und Zuspitzung; gute Allround-Eigenschaften"},
      {"type":"table_row","content":"Elliptische Flügelform","extra":"Aerodynamisch ideal (geringster induzierter Widerstand), aber schwierig herzustellen; praktische Alternative: Trapez"},
      {"type":"subheading","content":"2.5.3 Aerodynamische Hilfsmittel"},
      {"type":"text","content":"An der Tragfläche können verschiedene Hilfsmittel montiert werden, um die Strömung zu verbessern und gutmütige Flugeigenschaften (besonders im Langsamflug) zu erhalten."},
      {"type":"table_row","content":"Grenzschichtzäune","extra":"Senkrechte Bleche an der Flügelnase zur Stabilisierung der Grenzschicht; reduzieren induzierten Widerstand und verbessern Langsamflugeigenschaften"},
      {"type":"table_row","content":"Winglets","extra":"Kleine senkrechte Aufsätze an den Flächenspitzen; lenken die Randwirbel ab und verringern den induzierten Widerstand"},
      {"type":"table_row","content":"Abrisskanten (Nasenkeile)","extra":"Erzwingen frühzeitige Strömungsablösung an einem bestimmten Punkt → vorhersehbares Überziehverhalten; haben meist mehrere Dezimeter Länge"},
      {"type":"table_row","content":"Wirbelgeneratoren (Vortex Generators)","extra":"Kleine senkrechte Bleche; erzeugen turbulente Grenzschicht absichtlich → Strömung folgt Profilform länger, Abriss später; erhöhter Reibungswiderstand bei allen Geschwindigkeiten"},
      {"type":"infobox","content":"Konstruktionsmerkmale werden so kombiniert, dass das Flugzeug im normalen Betriebsbereich optimale Leistung zeigt und bei Annäherung an den Stall kontrollierbar bleibt.","extra":"Design-Ziel"},
      {"type":"focus","content":"Prüfungsschwerpunkte: Unterschied geometrische vs. aerodynamische Schränkung; Funktion von Winglets und Wirbelgeneratoren; welche Flügelform hat den geringsten induzierten Widerstand"},
    ],
    "quiz": [
      {"q":"Welches Konstruktionsmerkmal weist ein Tragflügelprofil auf, das für geringe Geschwindigkeiten (Langsamflug) optimiert wurde?","opts":["Geringe Profilwölbung","Große Dickenrücklage","Geringe Profildicke","Ausgeprägte Wölbung"],"ans":3,"exp":"Für Langsamflug optimierte Profile haben ausgeprägte Wölbung für hohen Auftriebsbeiwert und damit niedrigere Mindestgeschwindigkeit.","official":True},
      {"q":"Wie ist die Flügelstreckung (Seitenverhältnis) definiert?","opts":["Verhältnis von Auftrieb zu Gewicht","Verhältnis von Spannweite zu mittlerer Profiltiefe","Verhältnis von Profiltiefe zu Profildicke","Verhältnis von Klappenfläche zu Gesamtfläche"],"ans":1,"exp":"Flügelstreckung = Spannweite / mittlere Profiltiefe. Große Streckung = langer, schmaler Flügel = geringer induzierter Widerstand.","official":True},
      {"q":"Welche Flügelform erfüllt die praktischen Anforderungen moderner Flugzeuge am besten?","opts":["Trapezform","Elliptische Form","Rechteckform","Delta-Flügel"],"ans":0,"exp":"Die Trapezform ist ein guter praktischer Kompromiss – aerodynamisch nahezu optimal, deutlich einfacher herzustellen als die elliptische Form.","official":True},
      {"q":"Welche Funktion besitzen Wirbelgeneratoren (Vortex Generators)?","opts":["Umwandlung einer turbulenten in eine laminare Grenzschicht","Ablösen der Strömung","Längeres Anliegen einer laminaren Strömung (durch künstliche Turbulenz)","Verbesserung der Langsamflugeigenschaften durch Verzögerung des Strömungsabrisses"],"ans":3,"exp":"Wirbelgeneratoren erzeugen absichtlich turbulente Grenzschicht, die der Profilform besser folgt → verzögerter Stall, bessere Langsamflugeigenschaften.","official":True},
      {"q":"Was bewirken Winglets an Flügelspitzen?","opts":["Sie erhöhen den Auftrieb durch größere Wölbung","Sie leiten die Strömung der Randwirbel ab und verringern den induzierten Widerstand","Sie verbessern ausschließlich die Langsamflugeigenschaften","Sie vergrößern die Strömungsgeschwindigkeit über dem Flügel"],"ans":1,"exp":"Winglets lenken die Strömung um die Flächenspitzen ab und reduzieren damit die Randwirbel und den daraus resultierenden induzierten Widerstand.","official":False},
      {"q":"Wodurch kann bei der Profilkonstruktion die Bereiche laminarer und turbulenter Strömung variiert werden?","opts":["Profildicke","Einstellwinkel","Dickenrücklage","Nur durch die Strömungsgeschwindigkeit"],"ans":2,"exp":"Durch Verschiebung der Dickenrücklage kann der Umschlagpunkt verschoben werden: weit hinten liegende Dickenrücklage ergibt Laminarprofil.","official":True},
    ],
    "flashcards": [
      {"front":"Was ist der Vorteil eines Laminarprofils?","back":"Der Umschlagpunkt von laminarer zu turbulenter Grenzschicht liegt weiter hinten (große Dickenrücklage) → längere laminare Strömung → weniger Reibungswiderstand im Reiseflug."},
      {"front":"Was ist der Nachteil eines Laminarprofils?","back":"Weniger gutmütige Strömungseigenschaften – Abriss tritt abrupter und weniger vorhersehbar auf als beim Normalprofil."},
      {"front":"Warum haben Segelflugzeuge lange, schmale Flügel?","back":"Große Flügelstreckung = kleines Seitenverhältnis-Kehrwert → geringer induzierter Widerstand → sehr gute Gleitzahlen."},
      {"front":"Was ist geometrische Schränkung?","back":"Der Einstellwinkel des Flügels verringert sich von innen nach außen. Dadurch reißt die Strömung zuerst am Innenflügel ab → Querruder bleibt länger wirksam."},
    ]
  },

  # ─────────────────────────────────────────────────────────────────────────
  # KAP 3 – KRÄFTE AM LUFTFAHRZEUG
  # ─────────────────────────────────────────────────────────────────────────
  {
    "id": "aero-kraefte",
    "title": "Kap. 3 – Kräfte am Luftfahrzeug: Gleichgewicht & besondere Flugzustände",
    "sort_order": 40,
    "exam": True,
    "sections": [
      {"type":"heading","content":"Kräfte am Luftfahrzeug","extra":"Gleichgewicht im Geradeausflug, Steig-/Sinkflug, Kurvenflug, Bodeneffekt"},
      {"type":"subheading","content":"3.1 Fliegen im Gleichgewicht (Geradeausflug)"},
      {"type":"text","content":"Im unbeschleunigten Horizontalflug befinden sich alle auf das Luftfahrzeug wirkenden Kräfte im Gleichgewicht – keine resultierende Kraft bleibt übrig. Das Flugzeug erfährt keine Beschleunigung, Verzögerung oder Höhenänderung."},
      {"type":"table_row","content":"Kräftegleichgewicht","extra":"Auftrieb = Gewicht; Schub = Widerstand"},
      {"type":"table_row","content":"Auftriebskraft L","extra":"Senkrecht zur Anströmrichtung nach oben; erzeugt durch Flügel"},
      {"type":"table_row","content":"Gewichtskraft G","extra":"Senkrecht nach unten (Erdanziehung); unabhängig von Fluglage"},
      {"type":"table_row","content":"Schubkraft T","extra":"Parallel zur Flugbahn nach vorne; erzeugt durch Triebwerk/Propeller"},
      {"type":"table_row","content":"Widerstandskraft D","extra":"Parallel zur Anströmrichtung entgegen der Bewegung"},
      {"type":"subheading","content":"3.1.3 Die Gleitflugpolare (Lilienthal-Kurve)"},
      {"type":"text","content":"Die Gleitflugpolare zeigt die Sinkrate W in Abhängigkeit von der Fluggeschwindigkeit V im Motorleerlauf. Sie wird genutzt, um die Geschwindigkeit des besten Gleitens und die geringste Sinkrate zu ermitteln."},
      {"type":"table_row","content":"Geschwindigkeit des besten Gleitens","extra":"Tangente vom Ursprung an die Polare → maximale zurückgelegte Strecke aus einer Höhe"},
      {"type":"table_row","content":"Geringste Sinkgeschwindigkeit","extra":"Höchster Punkt der Polare → geringste Sinkrate (für maximale Flugzeit)"},
      {"type":"text","content":"Rücken- oder Gegenwind verschieben den Ausgangspunkt der Tangente horizontal → Tangentenpunkt verschiebt sich. Bei Gegenwind muss schneller geflogen werden für das beste Gleiten über Grund."},
      {"type":"subheading","content":"3.2 Besondere Flugzustände"},
      {"type":"table_row","content":"Steigflug","extra":"Auftrieb > Gewicht (zeitweise); Triebwerksleistung muss erhöht werden, um bei gleicher Geschwindigkeit zu steigen"},
      {"type":"table_row","content":"Sinkflug","extra":"Auftrieb < Gewicht; Triebwerksleistung reduziert oder Anstellwinkel verkleinert"},
      {"type":"diagram","content":SVG_KURVENFLUG,"extra":"Abb. 38 – Kräfte im Kurvenflug: Zentrifugalkraft und Lastvielfach"},
      {"type":"subheading","content":"3.2.3 Kurvenflug"},
      {"type":"text","content":"Im Kurvenflug kommt zur bisherigen Kräftegleichgewicht die Zentrifugalkraft ZF hinzu. Diese wirkt horizontal nach außen und muss durch die horizontale Komponente der Auftriebskraft (Zentripetalkraft) kompensiert werden. Das Flugzeug wird zur Seite geneigt (Schräglage)."},
      {"type":"fact","content":"Im Kurvenflug ist die Scheingewichtskraft (= Resultierende aus Gewichts- und Zentrifugalkraft) immer senkrecht nach unten in den Sitz gerichtet – ähnlich wie beim Autofahren in der Kurve, jedoch ohne Seitenneigung des Sitzes."},
      {"type":"table_row","content":"Lastvielfach n","extra":"n = 1/cos(γ); Bei 60° Schräglage: n = 2,0g; Bei 45°: n = 1,41g"},
      {"type":"table_row","content":"Überziehgeschwindigkeit","extra":"Steigt mit √Lastvielfach; bei 60° Schräglage ist sie 41% höher als im Geradeausflug"},
      {"type":"table_row","content":"Luftfahrzeugkategorien (EASA CS 23.337)","extra":"Normalflugzeug: +3,8g/-1,52g; Nutzflugzeug: +4,4g/-1,76g; Kunstflugzeug: +6,0g/-3,0g"},
      {"type":"subheading","content":"3.2.4 Bodeneffekt"},
      {"type":"text","content":"In Bodennähe (unter ½ Spannweite Flughöhe) kann die Luft um die Flächenenden nicht frei umströmen → induzierter Widerstand sinkt, Auftrieb steigt. Das Flugzeug 'schwebt' auf einem Luftkissen zwischen Tragfläche und Boden."},
      {"type":"fact","content":"Der Bodeneffekt erklärt, warum ein Flugzeug beim Landen 'schwebt' und weiter gleitet als erwartet. Tiefbordflugzeuge sind stärker beeinflusst. Bodeneffekt wirkt bei Flughöhe unter ½ Spannweite."},
      {"type":"focus","content":"Prüfungsschwerpunkte: Kräftegleichgewicht im Geradeausflug; Lastvielfach im Kurvenflug; Stallgeschwindigkeit steigt mit √n; Bodeneffekt"},
    ],
    "quiz": [
      {"q":"Was bedeutet 'Kräftegleichgewicht' hinsichtlich der Bewegung des Körpers?","opts":["Der Körper ruht","Der Körper wird durch eine resultierende Kraft beschleunigt","Die Geschwindigkeit des Körpers ist Null","Die Geschwindigkeit des Körpers ändert sich nicht"],"ans":3,"exp":"Kräftegleichgewicht bedeutet: keine resultierende Kraft → keine Beschleunigung → gleichförmige Bewegung (konstante Geschwindigkeit) oder Ruhe.","official":True},
      {"q":"Warum ist die Scheingewichtskraft im Kurvenflug höher als die Gewichtskraft im Geradeausflug?","opts":["Weil die Luft im Kurvenflug dichter ist","Weil Gewichtskraft und Zentrifugalkraft als Resultierende wirken","Weil die Triebwerksleistung erhöht werden muss","Weil der Anstellwinkel größer wird"],"ans":1,"exp":"Im Kurvenflug wirkt zusätzlich die Zentrifugalkraft horizontal nach außen. Die Resultierende aus Gewicht und Zentrifugalkraft (= Scheingewichtskraft) ist größer als die bloße Gewichtskraft.","official":True},
      {"q":"Welche Kraftkomponente wirkt im Kurvenflug der Zentrifugalkraft entgegen?","opts":["Vertikale Komponente der Auftriebskraft","Horizontale Komponente der Auftriebskraft (Zentripetalkraft)","Schubkraft des Triebwerks","Gewichtskraft"],"ans":1,"exp":"Die horizontale Komponente der Auftriebskraft (= Zentripetalkraft) ist zur Kurveninnenseite gerichtet und kompensiert die Zentrifugalkraft.","official":True},
      {"q":"Im Kurvenflug muss die Fluggeschwindigkeit mit Hilfe der Triebwerksleistung erhöht werden – warum?","opts":["Weil mehr Widerstand entsteht","Weil mehr Auftrieb benötigt wird (für das höhere Lastvielfach) und Auftrieb mit v² steigt","Weil die Kursänderung Energie kostet","Weil der Pilot mehr Druck auf den Sitz ausübt"],"ans":1,"exp":"Im Kurvenflug wird mehr Auftrieb benötigt (n > 1). Da Auftrieb auch mit v² zunimmt, muss die Geschwindigkeit erhöht werden, wenn der Anstellwinkel nicht vergrößert werden soll.","official":True},
      {"q":"Warum muss zum Beibehalten der Fluggeschwindigkeit im Steigflug die Triebwerksleistung erhöht werden?","opts":["Weil der Widerstand im Steigflug geringer ist","Weil mehr Auftrieb benötigt wird","Weil Auftrieb ≠ Gewicht und die resultierende Kraft das Flugzeug nach oben beschleunigt – dafür braucht man mehr Leistung","Weil die Luftdichte im Steigflug sinkt"],"ans":2,"exp":"Im Steigflug muss ein Überschuss an Auftriebskraft vorhanden sein – dazu wird mehr Triebwerksleistung benötigt, um die Geschwindigkeit zu halten.","official":True},
      {"q":"Wann ist der Bodeneffekt wirksam?","opts":["Bei jedem Flug in der Nähe des Flughafens","Wenn die Flughöhe etwa die halbe Spannweite unterschreitet","Nur beim Landen, nicht beim Start","Wenn der Anstellwinkel größer als 10° ist"],"ans":1,"exp":"Der Bodeneffekt ist wirksam, wenn die Flughöhe unter ½ Spannweite liegt. Der Boden begrenzt die Strömungsumläufe an den Flächenenden → geringerer induzierter Widerstand.","official":False},
    ],
    "flashcards": [
      {"front":"Was ist das Lastvielfach n?","back":"n = Auftriebskraft / Gewichtskraft = 1/cos(Querlage). Bei 60° Schräglage: n = 2,0g. Es gibt an, wie viel-fach mehr Auftrieb im Vergleich zum Geradeausflug benötigt wird."},
      {"front":"Wie verändert sich die Stallgeschwindigkeit im Kurvenflug?","back":"Sie steigt mit der Wurzel des Lastvielfachs: v_s(Kurve) = v_s(normal) × √n. Bei 60° Schräglage (n=2): Stallgeschwindigkeit ist um √2 ≈ 41% höher."},
      {"front":"Was ist der Bodeneffekt?","back":"In Bodennähe (unter ½ Spannweite) wird die Randwirbelbildung durch den Boden eingeschränkt. Der induzierte Widerstand sinkt, der Auftrieb steigt. Das Flugzeug 'schwebt' länger."},
    ]
  },

  # ─────────────────────────────────────────────────────────────────────────
  # KAP 4.1/4.2 – STABILITÄT & ACHSEN
  # ─────────────────────────────────────────────────────────────────────────
  {
    "id": "aero-stabilitaet-achsen",
    "title": "Kap. 4.1/4.2 – Stabilität, Flugzeugachsen & Schwerpunkt",
    "sort_order": 50,
    "exam": True,
    "sections": [
      {"type":"heading","content":"Stabilität und Flugzeugachsen","extra":"Stabilitätsbegriffe, drei Hauptachsen, Schwerpunkt und Druckpunkt"},
      {"type":"subheading","content":"4.1 Stabilitätsbegriffe"},
      {"type":"diagram","content":SVG_STABILITAET,"extra":"Abb. 39 – Stabil, Indifferent und Labil veranschaulicht am Kugel-Beispiel"},
      {"type":"table_row","content":"Statische Stabilität","extra":"Das Flugzeug kehrt nach einer Störung unmittelbar in den ursprünglichen Bewegungszustand zurück (rückführende Kraft entsteht)"},
      {"type":"table_row","content":"Dynamische Stabilität","extra":"Das Flugzeug kehrt nach Störung und möglichen Schwingungen langfristig in den Ausgangszustand zurück; setzt statische Stabilität voraus"},
      {"type":"table_row","content":"Statische Indifferenz","extra":"Das Flugzeug bewegt sich nach Störung weder zurück noch weiter weg; verbleibt in neuer Lage"},
      {"type":"table_row","content":"Statische Labilität","extra":"Das Flugzeug entfernt sich nach Störung weiter vom Ausgangszustand"},
      {"type":"infobox","content":"Für einen stabilen Flugzustand müssen BEIDE – statische UND dynamische Stabilität – vorliegen. Statische Stabilität allein reicht nicht; es können Pendelschwingungen entstehen, die sich aufschaukeln (dynamische Labilität trotz statischer Stabilität).","extra":"Wichtig"},
      {"type":"subheading","content":"4.2 Die drei Flugzeugachsen"},
      {"type":"diagram","content":SVG_DREI_ACHSEN,"extra":"Abb. 42 – Längsachse, Querachse und Hochachse"},
      {"type":"text","content":"Ein Flugzeug kann Bewegungen in alle drei Raumrichtungen vollziehen. Anders als ein Auto ist es nicht an eine Auflagefläche gebunden. In allen Fällen findet die Drehung um eine der drei Hauptachsen statt, die sich im Schwerpunkt schneiden."},
      {"type":"table_row","content":"Längsachse","extra":"Geht längs durch den Rumpf (Nase → Heck); Drehung = Rollen; gesteuert primär mit dem Querruder"},
      {"type":"table_row","content":"Querachse","extra":"Verläuft quer zur Flugrichtung (durch Tragflächen); Drehung = Nicken; gesteuert mit dem Höhenruder"},
      {"type":"table_row","content":"Hochachse","extra":"Steht senkrecht auf Längs- und Querachse (oben-unten durch den Rumpf); Drehung = Gieren; gesteuert mit dem Seitenruder"},
      {"type":"subheading","content":"4.2.1 Schwerpunkt und Druckpunkt"},
      {"type":"text","content":"Alle drei Achsen schneiden sich im Schwerpunkt. Die Gewichtskraft und Trägheitskräfte greifen im Schwerpunkt an. Die Auftriebskräfte am Tragflügel greifen im Druckpunkt an. Der Druckpunkt liegt meist vor dem Schwerpunkt."},
      {"type":"fact","content":"Wenn Auftriebskraft (im Druckpunkt) und Schwerkraft (im Schwerpunkt) nicht am selben Punkt angreifen, entsteht ein Drehmoment um die Querachse. Das Höhenleitwerk muss dieses Moment kompensieren – deshalb erzeugt es meist einen Abtrieb."},
      {"type":"text","content":"Bei größerem Anstellwinkel wandert der Druckpunkt nach vorne (Druckpunktwanderung). Ausnahme: druckpunktfeste Profile (symmetrische Profile, S-Form-Profile) – bei diesen bleibt der Druckpunkt unabhängig vom Anstellwinkel."},
      {"type":"focus","content":"Prüfungsschwerpunkte: Statische UND dynamische Stabilität beide notwendig; drei Achsen und ihre Ruder; Schwerpunkt vs. Druckpunkt; Funktion Höhenleitwerk"},
    ],
    "quiz": [
      {"q":"Warum ist Stabilität ein wichtiges Kriterium bei der Flugzeugkonstruktion?","opts":["Weil ein Flugzeug seine Fluglage nur durch Ruderausschlag ändern kann","Weil Korrekturen der Fluglage nach Störungen ausschließlich mit Ruderwirkung möglich sind","Damit ein Flugzeug nach Einwirken einer äußeren Störung selbstständig in die ursprüngliche Fluglage zurückkehrt","Stabilität kann nicht erreicht werden"],"ans":2,"exp":"Stabilität bedeutet: Das Flugzeug kehrt nach einer Störung selbsttätig in den Ausgangszustand zurück – ohne ständigen Rudereingriff des Piloten.","official":True},
      {"q":"Welche Form der Stabilität muss bei der Flugzeugkonstruktion mindestens erreicht werden?","opts":["Statische Stabilität","Mindestens statische Indifferenz","Dynamische Stabilität","Statische und dynamische Stabilität"],"ans":3,"exp":"Für einen stabilen Flugzustand müssen beide – statische und dynamische Stabilität – vorliegen. Nur statische Stabilität reicht nicht aus.","official":True},
      {"q":"Durch welchen Punkt verlaufen alle drei Bewegungsachsen eines Luftfahrzeuges?","opts":["Druckpunkt","Schwerpunkt","Geometrische Mitte","Neutral point"],"ans":1,"exp":"Alle drei Achsen verlaufen durch den Schwerpunkt – dem Punkt, in dem sich die gesamte Masse des Körpers vereinigt gedacht werden kann.","official":True},
      {"q":"In welchem Punkt greift die Gewichtskraft an?","opts":["Druckpunkt","Schwerpunkt","Angriffspunkt der Luftkräfte","Vorderkante des Profils"],"ans":1,"exp":"Die Gewichtskraft und Trägheitskräfte greifen immer im Schwerpunkt an.","official":True},
      {"q":"Welche Reaktion zeigt ein Luftfahrzeug unmittelbar beim Betätigen des Höhenruders?","opts":["Steigen oder Sinken des Luftfahrzeugs","Drehung des Luftfahrzeugs um die Längsachse","Drehung des Luftfahrzeugs um die Hochachse","Drehung des Luftfahrzeugs um die Querachse"],"ans":3,"exp":"Das Höhenruder steuert die Nickbewegung – die Drehung um die Querachse. Die Nase geht direkt hoch oder runter.","official":True},
      {"q":"Welche Reaktion zeigt ein Luftfahrzeug unmittelbar beim Betätigen des Querruders?","opts":["Drehung um die Querachse","Drehung um die Längsachse (Rollbewegung)","Drehung um die Hochachse","B und C"],"ans":3,"exp":"Das Querruder steuert primär die Rollachse (Längsachse). Durch das negative Wendemoment (adverse yaw) entsteht aber auch eine Gier-Komponente um die Hochachse.","official":True},
    ],
    "flashcards": [
      {"front":"Unterschied: statische vs. dynamische Stabilität","back":"Statisch: Es gibt eine rückstellende Kraft nach Störung. Dynamisch: Das Flugzeug kehrt TATSÄCHLICH in die Ausgangslage zurück (Schwingungen klingen ab). Beide müssen vorhanden sein!"},
      {"front":"Welche drei Drehbewegungen gibt es und was steuert sie?","back":"Rollen (Längsachse) → Querruder; Nicken (Querachse) → Höhenruder; Gieren (Hochachse) → Seitenruder"},
      {"front":"Was ist der Druckpunkt?","back":"Der Punkt, an dem die resultierende Luftkraft (Auftrieb + Widerstand) am Profil angreift. Wandert mit zunehmendem Anstellwinkel nach vorne."},
    ]
  },

  # ─────────────────────────────────────────────────────────────────────────
  # KAP 4.3–4.4 – STABILITÄT AM FLUGZEUG, RUDER & TRIMMUNG
  # ─────────────────────────────────────────────────────────────────────────
  {
    "id": "aero-ruder-trimmung",
    "title": "Kap. 4.2–4.4 – Ruder, Steuerachsen & Trimmung",
    "sort_order": 60,
    "exam": True,
    "sections": [
      {"type":"heading","content":"Ruder, Steuerachsen & Trimmung","extra":"Wende-/Schiebe-Rollmoment, Seitengleitflug, Steuerkräfte und Trimmung"},
      {"type":"subheading","content":"4.2.3 Bewegung um die Längsachse (Querruder)"},
      {"type":"text","content":"Querruder werden zum Einleiten und Ausleiten von Kurven verwendet. Das Querruder schlägt auf der einen Seite nach unten (mehr Auftrieb), auf der anderen Seite nach oben (weniger Auftrieb) aus. Dadurch dreht sich das Flugzeug um die Längsachse."},
      {"type":"fact","content":"Negatives Wendemoment (Adverse Yaw): Der gegensinnige Querruderausschlag bewirkt nicht nur ein Rollmoment, sondern auch ein Giermoment in die falsche Richtung. Beim Auslenken des Steuerknüppels nach rechts dreht die Nase zunächst nach links."},
      {"type":"table_row","content":"Differenzielle Querruder","extra":"Das nach unten ausschlagende Querruder schlägt weniger als das nach oben ausschlagende aus → reduziert das negative Wendemoment"},
      {"type":"table_row","content":"Koordinierter Kurvenflug","extra":"Quer- und Seitenruder werden koordiniert eingesetzt, um das negative Wendemoment zu kompensieren und eine saubere Kurve zu fliegen"},
      {"type":"subheading","content":"4.2.4 Bewegung um die Hochachse (Seitenruder)"},
      {"type":"text","content":"Das Seitenruder steuert die Gierbewegung. Eine reine Drehung um die Hochachse ist für normale Flugmanöver nicht erforderlich. Das Seitenruder dient zur Kompensation des negativen Wendemoments, zum Ausrichten bei Seitenwindlandungen und zur Steuerung bei Triebwerksausfall (Mehrmotorer)."},
      {"type":"fact","content":"Schiebe-Rollmoment: Der gegensinnige Seitenruderausschlag bewirkt nicht nur Gieren, sondern auch Rollen – da das Flugzeug seitlich angeströmt wird und die Tragflächen unterschiedlich viel Auftrieb erzeugen."},
      {"type":"subheading","content":"4.3 Stabilität am Flugzeug"},
      {"type":"table_row","content":"Längsstabilität","extra":"Stabilität um die Querachse; vom Höhenleitwerk (Höhenflosse + Höhenruder) und Schwerpunktlage abhängig"},
      {"type":"table_row","content":"Querstabilität","extra":"Stabilität um die Längsachse; v.a. durch V-Form der Tragflächen erreicht"},
      {"type":"table_row","content":"Richtungsstabilität","extra":"Stabilität um die Hochachse; durch Seitenleitwerk und Rumpfform erreicht"},
      {"type":"subheading","content":"4.4.2 Steuerkräfte und Ruderausgleich"},
      {"type":"text","content":"Die Wirkung aller Ruder besteht darin, die Ruderfläche in der Luftströmung auszulenken und damit Auftrieb/Widerstand zu erzeugen. Bei kleinen Flugzeugen besteht eine direkte mechanische Verbindung zwischen Steuerhorn und Ruder."},
      {"type":"table_row","content":"Aerodynamischer Ruderausgleich","extra":"Teil des Ruders vor der Drehachse; erzeugt Gegenkraft → reduziert nötige Steuerkräfte"},
      {"type":"table_row","content":"Statischer Ruderausgleich","extra":"Gewichte in der Ruderfläche verringern Ruderkräfte; Ruder im Schwerpunkt aufgehängt"},
      {"type":"table_row","content":"Dynamischer Ruderausgleich","extra":"Ruder so konstruiert, dass Trägheitsbewegungen des Ruders selbst die Steuerkräfte reduzieren"},
      {"type":"subheading","content":"4.4.3 Trimmung"},
      {"type":"text","content":"Trimmung bedeutet: das Ruder in einer bestimmten Auslenkung 'fixieren', ohne dass der Pilot dauerhaft Steuerdruck aufbringen muss. Ein getrimmtes Flugzeug fliegt stabil ohne ständige Steuereingriffe."},
      {"type":"table_row","content":"Trimmruder","extra":"Kleines Ruder an der Hinterkante des Hauptruders; erzeugt Gegendruck gegen das Hauptruder"},
      {"type":"table_row","content":"Bügelkanten","extra":"Starr am Ruder befestigte Trimmflächen; für konstante Korrekturen (ständiges Leichthängen oder Drehen)"},
      {"type":"table_row","content":"Kopflastige Trimmung","extra":"Flugrichtung neigt nach Loslassen nach unten ab (Schwerpunkt zu weit vorne)"},
      {"type":"table_row","content":"Schwanzlastige Trimmung","extra":"Flugrichtung neigt nach oben ab (Schwerpunkt zu weit hinten – gefährlicher!)"},
      {"type":"subheading","content":"4.4.4 Limitierungen (Geschwindigkeit und Steuerkräfte)"},
      {"type":"text","content":"Bei sehr hohen Geschwindigkeiten sind keine vollen Ruderausschläge mehr erlaubt. Bei geringen Geschwindigkeiten sind volle Ausschläge aus Strömungsgründen begrenzt. Es gibt eine Manövergeschwindigkeit, bis zu der noch volle abrupte Ruderausschläge möglich sind."},
      {"type":"warning","content":"Abrupte Ruderausschläge bei hoher Geschwindigkeit können strukturelle Überbelastungen verursachen. Bei Turbulenzen: Geschwindigkeit auf unter Manövergeschwindigkeit reduzieren."},
      {"type":"focus","content":"Prüfungsschwerpunkte: Negatives Wendemoment (adverse yaw); koordinierter Kurvenflug; Trimmung; Seitengleitflug; Manövergeschwindigkeit"},
    ],
    "quiz": [
      {"q":"Was ist das 'negative Wendemoment' (adverse yaw)?","opts":["Eine Drehung um die Längsachse bei Seitenruderausschlag","Ein Giermoment entgegen der gewünschten Kurvenrichtung, das beim Querruderausschlag entsteht","Eine unerwünschte Rollbewegung beim Seitenruderausschlag","Die Tendenz des Flugzeugs, in eine Steilkurve zu fallen"],"ans":1,"exp":"Das negative Wendemoment entsteht beim Betätigen des Querruders: Die nach unten ausgeschlagene Seite erzeugt mehr induzierten Widerstand und dreht die Nase zunächst entgegen der Kurvenrichtung.","official":True},
      {"q":"Steuerknüppel/Steuerhorn nach links lenkt – welche Wirkung hat das?","opts":["Linkes Querruder nach oben, rechtes nach unten → Flugzeug dreht rechts","Linkes Querruder nach unten, rechtes nach oben → Flugzeug dreht links","Seitenruder links → Nase nach links","Höhenruder → Nase nach oben"],"ans":1,"exp":"Steuerknüppel links: linkes Querruder nach unten (mehr Auftrieb links), rechtes nach oben (weniger Auftrieb rechts) → Flugzeug rollt links.","official":True},
      {"q":"Warum muss im Kurvenflug Seitenruder betätigt werden?","opts":["Um die Höhe zu halten","Um das negative Wendemoment (Gier entgegen der Kurvenrichtung) zu kompensieren","Um den Kurvenradius zu vergrößern","Um Schub zu erhöhen"],"ans":1,"exp":"Um eine saubere (koordinierte) Kurve zu fliegen, muss das negative Wendemoment durch gleichzeitigen Seitenrudereinsatz ausgeglichen werden.","official":True},
      {"q":"Welche Aufgabe besitzt die Trimmung?","opts":["Die Flugrichtung des Luftfahrzeugs zu ändern","Für eine permanente Auslenkung eines Steuerruders zu sorgen, damit keine dauernde Steuerkraft nötig ist","Das Flugzeug schneller zu machen","Nur Längsstabilität zu gewährleisten"],"ans":1,"exp":"Trimmung fixiert das Ruder in einer bestimmten Stellung, damit der Pilot nicht dauerhaft Kraft aufbringen muss.","official":True},
      {"q":"Was beschreibt die 'Manövergeschwindigkeit'?","opts":["Die Höchstgeschwindigkeit im Kurvenflug","Die Geschwindigkeit, bis zu der noch volle abrupte Ruderausschläge möglich sind","Die Mindestgeschwindigkeit ohne Klappen","Die Geschwindigkeit beim besten Steigen"],"ans":1,"exp":"Die Manövergeschwindigkeit ist die Geschwindigkeit, bis zu der noch volle Ausschläge an allen Rudern durchgeführt werden dürfen, ohne Strukturschäden zu riskieren.","official":True},
      {"q":"Welche Schwerpunktlage fördert die Längsstabilität?","opts":["Sehr weit hinten liegende Schwerpunktlage","Mittlere bis vordere Schwerpunktlage (innerhalb der zulässigen Grenzen)","Schwerpunkt vor dem Druckpunkt","Schwerpunkt im Druckpunkt"],"ans":1,"exp":"Eine eher vordere Schwerpunktlage verbessert die Längsstabilität, weil das Höhenleitwerk dann mehr Abtrieb erzeugen muss und dadurch stärker stabilisiert. Zu weit hinten = gefährlich labil.","official":False},
    ],
    "flashcards": [
      {"front":"Was ist 'adverse yaw' und wie wird es kompensiert?","back":"Adverse Yaw = negatives Wendemoment: Beim Querruderausschlag dreht die Nase zunächst entgegen der Kurvenrichtung. Kompensation durch gleichzeitigen Seitenrudereinsatz (koordinierter Kurvenflug)."},
      {"front":"Worin besteht der Unterschied zwischen kopflastiger und schwanzlastiger Trimmung?","back":"Kopflastig: Nase fällt nach Loslassen des Steuerhorns → SP zu weit vorne. Schwanzlastig: Nase steigt → SP zu weit hinten (gefährlicher, da instabiler)."},
      {"front":"Wie wird Querstabilität erreicht?","back":"Hauptsächlich durch die V-Form (Dihedral) der Tragflächen: Bei einseitiger Windböe kippt eine Fläche nach unten; deren vertikale Auftriebskomponente hebt sie wieder zurück."},
    ]
  },

  # ─────────────────────────────────────────────────────────────────────────
  # KAP 4.5 – LANDEHILFEN (KLAPPEN, VORFLÜGEL, STÖRKLAPPEN)
  # ─────────────────────────────────────────────────────────────────────────
  {
    "id": "aero-landehilfen",
    "title": "Kap. 4.5 – Landehilfen: Klappen, Vorflügel & Störklappen",
    "sort_order": 70,
    "exam": True,
    "sections": [
      {"type":"heading","content":"Landehilfen","extra":"Klappentypen, Vorflügel, Störklappen und ihre Verwendung"},
      {"type":"text","content":"Das Tragflügelprofil ist üblicherweise für den Reiseflug optimiert. Für Start und Landung sind besondere konstruktive Maßnahmen notwendig, um ausreichend Auftrieb auch bei niedrigen Geschwindigkeiten zu erzeugen."},
      {"type":"diagram","content":SVG_LANDEKLAPPEN,"extra":"Abb. 63–68 – Verschiedene Klappentypen und ihre Wirkung"},
      {"type":"subheading","content":"4.5.1 Landeklappen (Flaps)"},
      {"type":"text","content":"Landeklappen müssen zwei Aufgaben erfüllen: (1) ausreichend große Auftriebsbeiwerte bei geringen Geschwindigkeiten; (2) Strömung unterstützen, damit sie bei hohen Anstellwinkeln noch anliegt."},
      {"type":"table_row","content":"Wölbklappe","extra":"Hinterkante des Tragflügels wird nach unten geklappt → größere Wölbung → mehr Auftrieb + Widerstand; einfachster Klappentyp"},
      {"type":"table_row","content":"Spreizklappen","extra":"Nur auf Unterseite; erzeugt enorme Widerstandszunahme bei geringer Auftriebserhöhung; als Starthilfe unbrauchbar"},
      {"type":"table_row","content":"Fowler-Klappen","extra":"Fahren nach hinten und unten aus; vergrößern Flügelfläche + Wölbung; Spalt erzeugt turbulente Grenzschicht auf Oberseite; beste Wirkung für Langsamflug"},
      {"type":"table_row","content":"Wölbklappen mit Spalt","extra":"Ähnlich Fowler, aber ohne Flächenvergrößerung; Grenzschicht wird durch Spalt aufgefrischt → Strömung folgt auch bei großen Anstellwinkeln"},
      {"type":"subheading","content":"4.5.2 Vorflügel (Slats)"},
      {"type":"text","content":"Vorflügel werden an der Profilvorderkante montiert. Beim Ausfahren erzeugen sie erhöhten Auftriebsbeiwert, da die Wölbung vorne verändert wird. Zudem entsteht ein Spalt zwischen Vorflügel und Tragfläche, der die Grenzschicht auf der Oberseite auffrisch (ähnlich Fowler)."},
      {"type":"fact","content":"Vorflügel können die Mindestgeschwindigkeit verringern, ohne den Anstellwinkel zu stark zu erhöhen. Sie werden oft zusammen mit Landeklappen in der ersten Klappenstellung ausgefahren."},
      {"type":"subheading","content":"4.5.3 Störklappen (Spoiler)"},
      {"type":"text","content":"Störklappen (Spoiler) verschlechtern die Flugeigenschaften absichtlich: Sie werden auf der Flügeloberseite nahe der Dickenrücklage ausgefahren und erzeugen Verwirbelungen. Dadurch steigt der Widerstand und sinkt der Auftrieb stark."},
      {"type":"table_row","content":"Luftbremse (Airbrake)","extra":"Im Flug ausgefahren: erhöhter Widerstand → steiler Gleitpfad; Geschwindigkeit bleibt konstant"},
      {"type":"table_row","content":"Bodenspoiler","extra":"Nur am Boden ausgefahren: zerstört Auftrieb auf großem Flächenbereich → Flugzeuggewicht drückt auf Räder → bessere Bremswirkung"},
      {"type":"warning","content":"Spoiler dürfen NUR am Boden ausgefahren werden (Bodenspoiler). Im Flug sind nur Airbrakes zulässig, keine Bodenspoiler – Auftrieb würde zusammenbrechen."},
      {"type":"subheading","content":"Verwendung von Landeklappen"},
      {"type":"table_row","content":"Start","extra":"Kleine Klappenstellung (1. Stufe) für mehr Auftrieb bei kurzer Startrollstrecke; nicht voll ausgefahren (zu hoher Widerstand beim Steigen)"},
      {"type":"table_row","content":"Landung","extra":"Größtmögliche Klappenstellung für minimale Aufsetztgeschwindigkeit und steilen Anflugwinkel"},
      {"type":"table_row","content":"Einfahren in Bodennähe","extra":"GEFÄHRLICH – nach voll ausgefahrenen Wölb-/Spreizklappen bricht Auftrieb ein → Flugzeug 'durchsackt'; nur schrittweise in sicherer Höhe einfahren"},
      {"type":"focus","content":"Prüfung: Unterschiede Wölb-, Spreiz-, Fowler-Klappe; Funktion Vorflügel; Bodenspoiler nur am Boden; Einfahren in Bodennähe gefährlich"},
    ],
    "quiz": [
      {"q":"Warum benötigen Flugzeuge Landeklappen?","opts":["Für schnelleres Reisen","Um ausreichend Auftrieb bei niedrigen Geschwindigkeiten (Start/Landung) zu erzeugen","Für höhere Kursgenauigkeit","Um den Treibstoffverbrauch zu senken"],"ans":1,"exp":"Landeklappen erhöhen den Auftriebsbeiwert (cL) durch vergrößerte Profilwölbung, damit das Flugzeug auch bei niedrigen Geschwindigkeiten genug Auftrieb hat.","official":True},
      {"q":"Worin besteht die Wirkung von Landeklappen?","opts":["Sie verringern den Auftrieb und erhöhen den Widerstand","Sie erhöhen den Auftriebsbeiwert durch Vergrößerung der Profilwölbung (+ effektiver Anstellwinkel)","Sie reduzieren den Gesamtwiderstand","Sie erhöhen ausschließlich die Höchstgeschwindigkeit"],"ans":1,"exp":"Landeklappen erhöhen die Profilwölbung und damit den effektiven Anstellwinkel → der Auftriebsbeiwert cL steigt, die Mindestgeschwindigkeit sinkt. Gleichzeitig steigt auch der Widerstand.","official":True},
      {"q":"Dürfen Landeklappen in Bodennähe wieder eingefahren werden?","opts":["Nein, nie","Nur schrittweise in sicherer Höhe nach Erhöhung der Motorleistung","Ja, in beliebiger Stellung","Nur in großen Stellungen (30°–40°)"],"ans":1,"exp":"Einfahren in Bodennähe ist gefährlich: Bei gleichbleibender Geschwindigkeit reduziert einfahren der Wölb-/Spreizklappen den Auftrieb stark → Flugzeug durchsackt. Deshalb: erst Motorleistung erhöhen, dann schrittweise in sicherer Höhe einfahren.","official":True},
      {"q":"Worin besteht die Wirkung von Spreizklappen?","opts":["Sie erzeugen mehr Auftrieb durch Wölbungserhöhung","Sie erhöhen mehr Widerstand als Auftrieb; als Starthilfe unbrauchbar","Sie verbessern den Gleitwinkel","Sie erhöhen den Unterdruck auf der Flügeloberseite"],"ans":1,"exp":"Spreizklappen (auf der Unterseite) erzeugen hohen Widerstand bei wenig Auftrieb. Sie eignen sich nicht als Starthilfe, da der Startrollwiderstand zu hoch wäre.","official":True},
      {"q":"Was ist der Vorteil von Fowler-Flaps gegenüber Wölbklappen?","opts":["Sie erzeugen nur Auftrieb, aber keinen Widerstand","Sie fahren nach hinten und unten aus, vergrößern dabei die Flügelfläche und erzeugen durch den Spalt turbulente Grenzschicht","Sie sind einfacher zu konstruieren","Sie haben geringeren Einfluss auf das Strömungsverhalten"],"ans":1,"exp":"Fowler-Flaps fahren nach hinten und unten aus (Flächenvergrößerung + Wölbungserhöhung). Der entstehende Spalt frisch die Grenzschicht auf der Oberseite auf → bessere Langsamflugeigenschaften.","official":True},
    ],
    "flashcards": [
      {"front":"Was ist der Unterschied zwischen Wölbklappe und Spreizklappen?","back":"Wölbklappe: Hinterkante klappt nach unten → mehr Wölbung → mehr Auftrieb + etwas Widerstand. Spreizklappen: nur Unterseite → hauptsächlich Widerstand, kaum Auftrieb → als Starthilfe ungeeignet."},
      {"front":"Warum ist Einfahren von Landeklappen in Bodennähe gefährlich?","back":"Bei voll ausgefahrenen Wölb-/Spreizklappen bricht der Auftrieb bei gleichbleibender Geschwindigkeit schlagartig ein → Flugzeug 'durchsackt' – Absturz möglich. Zuerst Motorleistung erhöhen, dann schrittweise in sicherer Höhe einfahren."},
      {"front":"Welche Funktion haben Vorflügel (Slats)?","back":"Sie können die Mindestgeschwindigkeit verringern, indem sie die Profilwölbung vorne erhöhen und durch einen Spalt die Grenzschicht auffrischen. Dadurch ist ein Fliegen bei höherem Anstellwinkel ohne Stall möglich."},
    ]
  },

  # ─────────────────────────────────────────────────────────────────────────
  # KAP 5 – STRÖMUNGSABRISS & TRUDELN
  # ─────────────────────────────────────────────────────────────────────────
  {
    "id": "aero-stall-trudeln",
    "title": "Kap. 5 – Strömungsabriss (Stall) & Trudeln",
    "sort_order": 80,
    "exam": True,
    "sections": [
      {"type":"heading","content":"Besondere Flugzustände: Stall & Trudeln","extra":"Ursachen, Anzeichen, Ausleiten – sicherheitskritisch!"},
      {"type":"subheading","content":"5.1 Strömungsabriss (Stall)"},
      {"type":"diagram","content":SVG_STALL,"extra":"Abb. 69 – Kritischer Anstellwinkel: Normale Anströmung vs. Strömungsabriss"},
      {"type":"text","content":"Solange die Luftströmung der Profilform folgen kann, wird Auftrieb erzeugt. Bei zunehmendem Anstellwinkel wird die Auftriebserzeugung stärker. Es existiert aber ein kritischer Anstellwinkel, ab dem die Strömung von der Oberfläche ablöst – der Stall."},
      {"type":"fact","content":"Der Stall ist kein Geschwindigkeitsproblem, sondern ein Anstellwinkel-Problem! Er kann bei jeder Fluggeschwindigkeit und jeder Fluglage eintreten – auch bei hoher Geschwindigkeit im Sturzflug, wenn der Anstellwinkel zu abrupt vergrößert wird."},
      {"type":"subheading","content":"5.1.2 Anzeichen für einen nahenden Strömungsabriss"},
      {"type":"table_row","content":"Stall Warning (Tröte)","extra":"Elektrisches oder pneumatisches Warnsystem bei Annäherung an den kritischen Anstellwinkel; am Boden testbar"},
      {"type":"table_row","content":"Buffeting","extra":"Ablöseblasen treffen auf Höhenleitwerk → Vibrationen am Steuerhorn; zuverlässiges Vorwarnsignal"},
      {"type":"table_row","content":"Fahrtmessermarkierungen","extra":"Ende des grünen Bogens = VS0 (Überziegeschwindigkeit mit Landeklappen); Ende des weißen Bogens = VS1 (clean configuration)"},
      {"type":"table_row","content":"Steigender Anstellwinkel","extra":"Nase immer höher bei gleichbleibender oder sinkender Geschwindigkeit"},
      {"type":"subheading","content":"5.1.3 Ausleiten (Recovery)"},
      {"type":"text","content":"Recovery muss sofort eingeleitet werden, wenn Anzeichen erkannt werden. Wichtig: Die Strömung muss wieder an den Tragflächen anliegen können."},
      {"type":"table_row","content":"1. Steuerhorn nachgeben","extra":"Nase absenken → Anstellwinkel reduzieren → Strömung liegt wieder an"},
      {"type":"table_row","content":"2. Motorleistung erhöhen","extra":"Startleistung setzen → Geschwindigkeit aufbauen, Höhenverlust minimieren"},
      {"type":"table_row","content":"3. Klappen einfahren","extra":"Erst nach Recovery, schrittweise in sicherer Höhe"},
      {"type":"warning","content":"Stall-Übungen dürfen NICHT in Bodennähe durchgeführt werden – zu wenig Höhe für Recovery. Beim Approach Stall (mit Klappen) ist kein Höhenverlust erlaubt."},
      {"type":"subheading","content":"5.2 Trudeln (Spin)"},
      {"type":"diagram","content":SVG_TRUDELN,"extra":"Abb. 74 – Trudelzustand: Rotation um eine vertikale Achse außerhalb des Flugzeugs"},
      {"type":"text","content":"Trudeln ist ein Zustand mit einseitig abgerissener Strömung. Wenn ein Flugzeug im Bereich des kritischen Anstellwinkels fliegt, dreht dabei das Flugzeug um die Hochachse (Gieren), erhält die innen liegende Fläche weniger Auftrieb – das Flugzeug kippt und beginnt zu trudeln."},
      {"type":"table_row","content":"Steiltrudeln","extra":"Längsneigung > 50°; Nase zeigt steil nach unten; kann mit normalen Steuerbewegungen ausgeleitet werden (gemäß Handbuch)"},
      {"type":"table_row","content":"Flachtrudeln","extra":"Flachere Längsneigung; deutlich gefährlicher – mit normalen Ruderbewegungen kaum auszuleiten; kann sich im stationären Zustand selbst erhalten"},
      {"type":"table_row","content":"Schwerpunktlage","extra":"Hintere SP-Lage fördert Trudelneigung; Schwerpunkt darf NIEMALS hinter der hinteren Grenze liegen → Flachtrudeln!"},
      {"type":"subheading","content":"5.2.2 Einleiten des Trudelns"},
      {"type":"text","content":"Zum Einleiten eines Trudelns muss bewusst der einseitige Strömungsabriss im Bereich des kritischen Anstellwinkels provoziert werden. Im Langsamflug nahe der Abrissgeschwindigkeit: Quer- und Seitenruder gegensinnig ausschlagen. Das Schiebe-Rollmoment beginnt das Trudeln."},
      {"type":"subheading","content":"5.2.3 Ausleiten"},
      {"type":"table_row","content":"1. Seitenruder","extra":"Gegen die Drehrichtung betätigen (Drehung stoppen)"},
      {"type":"table_row","content":"2. Querruder","extra":"Neutral halten"},
      {"type":"table_row","content":"3. Höhenruder","extra":"Nachgeben (Nase runter), um Anströmung wiederherzustellen"},
      {"type":"table_row","content":"4. Sturzflug abfangen","extra":"Nach Stopp der Rotation: Höhenruder ziehen (behutsam)"},
      {"type":"table_row","content":"Motor","extra":"Während Trudeln: Leerlauf setzen; Propeller-Drehmoment beeinflusst Trudelrichtung"},
      {"type":"warning","content":"Details zu Ein-/Ausleiten des Trudelns sind IMMER im Flugzeughandbuch nachzulesen und von einem erfahrenen Fluglehrer zu lernen. Flachtrudeln ist eines der gefährlichsten Flugzustände."},
      {"type":"focus","content":"Prüfungsschwerpunkte: Stall = Anstellwinkelproblem; Recovery-Schritte; Flach- vs. Steiltrudeln; hintere SP-Lage fördert Trudeln; Ausleiten: SR gegen Drehrichtung → HR nachgeben → Sturzflug abfangen"},
    ],
    "quiz": [
      {"q":"Wie hängen Anstellwinkel und Strömungsabriss zusammen?","opts":["Je kleiner der Anstellwinkel, desto eher tritt Stall auf","Je größer der Anstellwinkel über den kritischen Wert, desto eher tritt Stall auf","Stall hängt nur von der Geschwindigkeit ab","Bei geringem Anstellwinkel kommt es immer zum Stall"],"ans":1,"exp":"Der Strömungsabriss tritt auf, wenn der kritische Anstellwinkel überschritten wird. Die Geschwindigkeit ist sekundär – Stall ist ein AoA-Problem.","official":True},
      {"q":"Was unterscheidet den Übergang ins Trudeln vom 'normalen' Abkippen?","opts":["Beim Trudeln fällt nur die Nase","Beim Trudeln dreht das Flugzeug um eine vertikale Achse außerhalb des Schwerpunkts (Rotation + einseitiger Abriss)","Trudeln tritt nur bei Motorausfall auf","Beim Trudeln ist die Geschwindigkeit höher"],"ans":1,"exp":"Beim Trudeln liegt ein einseitiger Strömungsabriss kombiniert mit Rotation vor. Das Flugzeug dreht um eine vertikale Achse, die NICHT durch den Schwerpunkt geht – anders als beim normalen Abkippen.","official":True},
      {"q":"Worin besteht die größte Gefahr beim Trudeln?","opts":["Die zulässige Höchstgeschwindigkeit kann schnell überschritten werden","Enormer Höhenverlust","Das Seitenruder zeigt keine Wirkung mehr","Fahrtmesseranzeige ist unzuverlässig"],"ans":1,"exp":"Beim Trudeln ist der Höhenverlust enorm. Gleichzeitig kann das Flugzeug seine maximale Geschwindigkeit meist nicht überschreiten, aber der Höhenverlust ist die größte Gefahr.","official":True},
      {"q":"Was ist die erste Reaktion zum Recovery bei drohendem Strömungsabriss?","opts":["Motorleistung auf Leerlauf","Beherztes Ziehen am Höhenruder","Klappen einfahren","Nachdrücken am Höhenruder (Gas geben)"],"ans":3,"exp":"Recovery (Ausleiten): Zuerst Steuerhorn nachdrücken/nachgeben → Anstellwinkel reduzieren → Strömung legt sich wieder an. Dann Motorleistung erhöhen.","official":True},
      {"q":"Warum dürfen Stall-Übungen nicht in Bodennähe durchgeführt werden?","opts":["Wegen des Lärms","Wegen mangelnder Mindesthöhe für die Recovery und Starthöhenverlust ist in dieser Lage nicht zulässig","Wegen der Gefahr für andere Flugzeuge","Weil Klappen nicht eingefahren werden können"],"ans":1,"exp":"Stall-Übungen erfordern ausreichend Höhe für Recovery. In Bodennähe fehlt die Höhe für das Abfangen des Sturzflugs nach dem Recovery.","official":True},
      {"q":"In welcher Situation ist die Gefahr besonders groß, ins Trudeln zu geraten?","opts":["Schnelle Steilkurve","Langsamer Kurvenflug nahe der Abrissgeschwindigkeit","Schneller Geradeausflug","Reiseflug bei hoher Geschwindigkeit"],"ans":1,"exp":"Im langsamen Kurvenflug nahe der Abrissgeschwindigkeit: Das Flugzeug befindet sich schon nahe dem kritischen Anstellwinkel. Ein Versuch, die hängende Fläche durch Querruder aufzurichten, kann durch das Schiebe-Rollmoment Trudeln einleiten.","official":True},
      {"q":"Welche Schwerpunktlage fördert die Trudelneigung?","opts":["Vordere Schwerpunktlage","Hintere Schwerpunktlage","Mittlere Schwerpunktlage","Unbelastetes Flugzeug"],"ans":1,"exp":"Hintere Schwerpunktlage fördert die Trudelneigung. Auf keinen Fall darf der Schwerpunkt jenseits der hinteren Grenze liegen, da dann Flachtrudeln entstehen kann, das mit Ruderwirkung nicht mehr auszuleiten ist.","official":True},
      {"q":"Wie wird Trudeln ausgeleitet?","opts":["Querruder in Drehrichtung, Höhenruder ziehen, Motorleistung erhöhen","Seitenruder gegen Drehrichtung, Querruder neutral, Höhenruder nachgeben, dann Sturzflug abfangen","Nur Höhenruder ziehen","Motorleistung erhöhen und Steuerhorn ziehen"],"ans":1,"exp":"Ausleiten: 1. Seitenruder GEGEN Drehrichtung, 2. Querruder NEUTRAL, 3. Höhenruder NACHGEBEN (Nase runter, Strömung wiederherstellen), 4. Nach Stopp: Sturzflug abfangen. Motor: Leerlauf.","official":True},
      {"q":"Was unterscheidet Steiltrudeln von Flachtrudeln?","opts":["Beim Steiltrudeln dreht das Flugzeug schneller","Steiltrudeln hat Längsneigung >50° (auszuleiten); Flachtrudeln hat flachere Neigung und ist kaum auszuleiten","Beim Flachtrudeln ist die Sinkrate geringer","Steiltrudeln kann nicht eingeleitet werden"],"ans":1,"exp":"Steiltrudeln: Nase >50° nach unten, kann mit normalen Steuerbewegungen ausgeleitet werden. Flachtrudeln: flachere Neigung, deutlich gefährlicher – mit normalen Rudern kaum auszuleiten.","official":True},
    ],
    "flashcards": [
      {"front":"Was ist der kritische Unterschied zwischen Stall und Trudeln?","back":"Stall = Strömungsabriss auf BEIDEN Flächen gleichzeitig. Trudeln = einseitiger Strömungsabriss + Rotation um eine vertikale Achse außerhalb des SP. Trudeln beginnt meist aus dem überzogenen Flugzustand."},
      {"front":"Recovery-Schritte beim Stall (einfach)?","back":"1. Steuerhorn nachgeben (Nase runter → AoA verkleinern) 2. Motorleistung erhöhen (Startleistung) 3. Geschwindigkeit aufbauen 4. Klappen erst danach in sicherer Höhe schrittweise einfahren"},
      {"front":"Recovery-Schritte beim Trudeln?","back":"1. SR gegen Drehrichtung 2. QR neutral 3. HR nachgeben (Nase runter) 4. Nach Stopp: Sturzflug abfangen (HR ziehen) 5. Motor: Leerlauf während Trudeln"},
      {"front":"Warum ist Flachtrudeln gefährlicher als Steiltrudeln?","back":"Flachtrudeln hat eine flachere Längsneigung → das Momentengleichgewicht im stationären Flachtrudelzustand kann so stabil sein, dass normale Ruderwirkungen nicht mehr ausreichen, um es auszuleiten."},
    ]
  },

]  # Ende CHAPTERS

# ══════════════════════════════════════════════════════════════════════════════
# DATENBANK-OPERATIONEN
# ══════════════════════════════════════════════════════════════════════════════

def run(db_path: str) -> None:
    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Sicherstellen, dass learn_fts existiert (falls noch nicht)
    try:
        c.execute("""
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

    # 1) Alte Aerodynamik-Inhalte löschen (nur für 'principles' subject)
    c.execute("""
        SELECT id FROM learn_chapters WHERE subject_id = 'principles'
          AND id LIKE 'aero-%'
    """)
    old_ids = [r[0] for r in c.fetchall()]
    for cid in old_ids:
        c.execute("DELETE FROM learn_sections WHERE chapter_id = ?", (cid,))
        c.execute("DELETE FROM learn_quiz WHERE chapter_id = ?", (cid,))
        c.execute("DELETE FROM learn_flashcards WHERE chapter_id = ?", (cid,))
        try:
            c.execute("DELETE FROM learn_fts WHERE chapter_id = ?", (cid,))
        except Exception:
            pass
        c.execute("DELETE FROM learn_chapters WHERE id = ?", (cid,))
    
    # Auch alte pof- Kapitel löschen, falls vorhanden
    c.execute("""
        SELECT id FROM learn_chapters WHERE subject_id = 'principles'
          AND id LIKE 'pof-%'
    """)
    old_pof = [r[0] for r in c.fetchall()]
    for cid in old_pof:
        c.execute("DELETE FROM learn_sections WHERE chapter_id = ?", (cid,))
        c.execute("DELETE FROM learn_quiz WHERE chapter_id = ?", (cid,))
        c.execute("DELETE FROM learn_flashcards WHERE chapter_id = ?", (cid,))
        try:
            c.execute("DELETE FROM learn_fts WHERE chapter_id = ?", (cid,))
        except Exception:
            pass
        c.execute("DELETE FROM learn_chapters WHERE id = ?", (cid,))

    print(f"  Alte Kapitel gelöscht: {len(old_ids) + len(old_pof)}")

    # 2) Neues 'principles' subject sicherstellen
    c.execute("""
        INSERT OR REPLACE INTO learn_subjects (id, code, title, icon, color, overview, sort_order)
        VALUES ('principles', '60', 'Aerodynamik / Principles of Flight', '🛩️',
                '#06b6d4',
                'Dieses Fach erklärt, warum Flugzeuge fliegen, steuern und stallen. Die Kapitel basieren vollständig auf dem AirCademy Advanced PPL-Guide (Kap. 2–5). Verständnis ist wichtiger als Formeln: Wer Ursachen und Wirkungen erkennt, löst viele Prüfungsfragen intuitiv.',
                6)
    """)

    # 3) Kapitel + Inhalte einfügen
    total_q = 0
    total_fc = 0
    for ch in CHAPTERS:
        cid = ch["id"]
        c.execute("""
            INSERT OR REPLACE INTO learn_chapters
              (id, subject_id, title, sort_order, exam_relevant)
            VALUES (?, 'principles', ?, ?, ?)
        """, (cid, ch["title"], ch["sort_order"], 1 if ch.get("exam") else 0))

        # Sections
        for i, s in enumerate(ch.get("sections", [])):
            c.execute("""
                INSERT INTO learn_sections (chapter_id, type, content, extra, sort_order)
                VALUES (?, ?, ?, ?, ?)
            """, (cid, s["type"], s["content"], s.get("extra"), i))

        # Quiz
        for i, q in enumerate(ch.get("quiz", [])):
            opts = json.dumps(q["opts"], ensure_ascii=False)
            c.execute("""
                INSERT INTO learn_quiz
                  (chapter_id, question, options, answer, explanation, is_official, sort_order)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (cid, q["q"], opts, q["ans"], q.get("exp",""), 1 if q.get("official") else 0, i))
        total_q += len(ch.get("quiz", []))

        # Flashcards
        for i, fc in enumerate(ch.get("flashcards", [])):
            c.execute("""
                INSERT INTO learn_flashcards (chapter_id, front, back, sort_order)
                VALUES (?, ?, ?, ?)
            """, (cid, fc["front"], fc["back"], i))
        total_fc += len(ch.get("flashcards", []))

        # FTS
        text_parts = [ch["title"]]
        for s in ch.get("sections", []):
            if s["type"] not in ("diagram",) and s.get("content"):
                text_parts.append(s["content"])
        try:
            c.execute("""
                INSERT INTO learn_fts (chapter_id, subject_id, chapter_title, subject_title, content)
                VALUES (?, 'principles', ?, 'Aerodynamik / Principles of Flight', ?)
            """, (cid, ch["title"], " ".join(text_parts)))
        except Exception:
            pass

        print(f"  ✓ {cid}: {len(ch.get('sections',[]))} Sektionen, {len(ch.get('quiz',[]))} Quiz, {len(ch.get('flashcards',[]))} Flashcards")

    conn.commit()
    conn.close()
    print(f"\nFertig! Gesamt: {len(CHAPTERS)} Kapitel, {total_q} Quiz-Fragen, {total_fc} Flashcards.")


if __name__ == "__main__":
    print(f"Verbinde mit Datenbank: {DB_PATH}")
    run(DB_PATH)
