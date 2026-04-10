
// ═══════════════════════════════════════════════════════════════
// PPL DATA PATCH - AGK Instrumente & Aerodynamik (Aircademy Band 1+2)
// Generated from: Allgemeine Luftfahrzeugkunde (Kap 4.1-4.5) + Aerodynamik (Kap 1-2)
// ═══════════════════════════════════════════════════════════════
// NEW CHAPTERS - AGK Instrumente (4.1–4.5) + Aerodynamik (Band 2, Kap 1–2)
// Based on: Aircademy Advanced PPL-Guide Band 1 (Allgemeine Luftfahrzeugkunde) &
//           Aircademy Advanced PPL-Guide Band 2 (Aerodynamik)

window.NEW_CHAPTERS_AGK = [
  // ──────────────────────────────────────────────────────────────
  // 4.1  DOSEN- UND DRUCKINSTRUMENTE
  // ──────────────────────────────────────────────────────────────
  {
    "id": "agk-pitot-static",
    "title": "4.1 Pitot-Static-System: Höhenmesser, Fahrtmesser & Variometer",
    "exam": true,
    "summary": [
      "Das Pitot-Static-System versorgt drei lebensnotwendige Instrumente mit Druckwerten: Der Höhenmesser nutzt nur den statischen Druck, das Variometer die zeitliche Änderung des statischen Drucks, und der Fahrtmesser die Differenz aus Gesamtdruck (statischer + dynamischer Staudruck) und statischem Druck. Alle Drucköffnungen müssen regelmäßig auf Vereisung und Verstopfung geprüft werden.",
      "Der Höhenmesser zeigt die Höhe über einer einstellbaren Bezugsdruckfläche (QFE/QNH/Standard). Dabei gilt: In kalter Luft wird stets eine zu hohe Höhe angezeigt ('Im Winter sind die Berge höher'). Der Fahrtmesser liefert direkt nur die angezeigte Geschwindigkeit (IAS), die von der wahren Eigengeschwindigkeit (TAS) und der Geschwindigkeit über Grund (GS) abweicht."
    ],
    "facts": [
      "Höhenmesser, VSI und Fahrtmesser sind an das Pitot-Static-System angeschlossen.",
      "Beim Höhenmesser gilt: 1 hPa Druckunterschied entspricht ca. 30 ft (8 m) Höhenunterschied.",
      "QFE zeigt die Höhe über dem Flugplatz an; QNH zeigt MSL-Höhe; 1013,25 hPa = Druckhöhe / Flight Level.",
      "TAS ≈ CAS + 2% pro 1.000 ft Flughöhe.",
      "Vier Höhenbegriffe: Elevation (Landschaftshöhe über MSL), Height (AGL), Altitude (MSL), Flight Level (Druckhöhe).",
      "Das Variometer reagiert mit einer Zeitverzögerung von bis zu 9 Sekunden nach Änderung der Flugbewegung.",
      "Farbmarkierungen am Fahrtmesser: Weißer Bogen = mit Klappen, Grüner Bogen = Normalbetrieb, Gelber Bogen = Vorsicht, Roter Strich = Vne (nie überschreiten).",
      "Blockierte Statikdruckleitung → Höhenmesser eingefroren, VSI zeigt 0, Fahrtmesser verhält sich umgekehrt zum Höhenmesser.",
      "Blockiertes Pitot-Rohr (Gesamtdruckleitung) → Fahrtmesser allein betroffen."
    ],
    "table": [
      ["Höhenmesser", "Statischer Druck → zeigt Höhe über Bezugsdruckfläche"],
      ["Variometer (VSI)", "Änderung des statischen Drucks → Steig-/Sinkrate"],
      ["Fahrtmesser (ASI)", "Gesamtdruck minus statischer Druck → IAS"],
      ["QFE", "Lokaler Flugplatzdruck – zeigt Platzrundenhöhe"],
      ["QNH", "Auf MSL umgerechneter Druck – zeigt Höhe über MSL"],
      ["Standard 1013,25 hPa", "Druckhöhe / Flight Level – Staffelung im Reiseflug"],
      ["IAS", "Angezeigte Geschwindigkeit direkt am Fahrtmesser"],
      ["CAS", "IAS korrigiert um Einbau- und Instrumentenfehler"],
      ["TAS", "Wahre Eigengeschwindigkeit in ungestörter Luft"],
      ["GS", "Geschwindigkeit über Grund = TAS ± Wind"],
      ["Vso", "Abreißgeschwindigkeit mit voll ausgefahrenen Klappen"],
      ["Vs1", "Abreißgeschwindigkeit mit eingefahrenen Klappen, geradeaus"],
      ["Vno", "Höchstgeschwindigkeit im Normalbetrieb (oberes Ende Grüner Bogen)"],
      ["Vne", "Nie-Überschreiten-Geschwindigkeit (Roter Strich)"],
      ["Vx", "Bester Steigwinkel (kürzeste Distanz)"],
      ["Vy", "Beste Steigrate (kürzeste Zeit)"]
    ],
    "focus": [
      "Welches Instrument welchen Druck nutzt – und was passiert bei Blockade",
      "Vier Höhenbegriffe und QFE/QNH/Standard unterscheiden",
      "IAS vs. TAS: TAS = CAS + 2% pro 1.000 ft",
      "Farbmarkierungen am Fahrtmesser sicher zuordnen",
      "Warnhinweise: In kalter Luft zeigt der Höhenmesser zu hoch an"
    ],
    "sources": [
      {"label": "Aircademy AGK Band 1 – Kap. 4.1 Dosen- und Druckinstrumente", "url": "https://aircademy.com"},
      {"label": "EASA ECQB – AGK Referenz", "url": "https://www.easa.europa.eu/en/domains/aircrew-and-medical/european-central-question-bank-ecqb"}
    ],
    "quiz": [
      {
        "q": "Welche Instrumente sind an das Pitot-Static-System angeschlossen?",
        "options": [
          "Kompass, ADF und Transponder",
          "Höhenmesser, Variometer und Fahrtmesser",
          "Nur der Fahrtmesser",
          "Drehzahlmesser und Öldruckanzeige"
        ],
        "answer": 1,
        "explanation": "Das Pitot-Static-System versorgt Höhenmesser (statischer Druck), VSI (Änderung statischer Druck) und Fahrtmesser (Differenz Gesamt- zu statischem Druck)."
      },
      {
        "q": "Welcher Druck liegt an der Außenseite der Aneroidosen des Fahrtmessers an?",
        "options": [
          "Nur der Staudruck aus dem Pitot-Rohr",
          "Der statische Druck",
          "Gar kein Druck",
          "Der Kabinendruck"
        ],
        "answer": 1,
        "explanation": "Das Fahrtmessergehäuse ist mit dem statischen System verbunden. Im Innern der Aneroidosen herrscht der Gesamtdruck. Die Membran reagiert auf die Differenz = dynamischer Druck."
      },
      {
        "q": "Was zeigt der Höhenmesser, wenn QNH eingestellt ist?",
        "options": [
          "Die Höhe über dem Flugplatz (AGL)",
          "Die Druckhöhe (Pressure Altitude)",
          "Die Höhe über dem mittleren Meeresspiegel (MSL/Altitude)",
          "Die wahre Höhe (True Altitude)"
        ],
        "answer": 2,
        "explanation": "Mit eingestelltem QNH zeigt der Höhenmesser die Altitude (Höhe über MSL) unter der Voraussetzung, dass die Atmosphäre Standardbedingungen aufweist."
      },
      {
        "q": "Wie lautet die Faustformel für TAS aus CAS?",
        "options": [
          "TAS = CAS − 2% pro 1.000 ft",
          "TAS = CAS + 2% pro 1.000 ft",
          "TAS = CAS × Dichte",
          "TAS und CAS sind identisch"
        ],
        "answer": 1,
        "explanation": "Da die Luftdichte mit der Höhe abnimmt, ist TAS stets größer als CAS. Als Faustformel gilt: TAS ≈ CAS + 2% pro 1.000 ft Flughöhe."
      },
      {
        "q": "In welchem Geschwindigkeitsbereich sollte das Flugzeug im Normalbetrieb geflogen werden?",
        "options": [
          "Im weißen Bogen",
          "Im grünen Bogen",
          "Im gelben Bogen",
          "Über dem roten Strich"
        ],
        "answer": 1,
        "explanation": "Der grüne Bogen ist der normale Betriebsbereich (Vs1 bis Vno). Im weißen Bogen können Klappen gefahren werden; im gelben Bogen ist Vorsicht geboten (nur ruhige Luft)."
      },
      {
        "q": "Welcher Merksatz gilt für den Höhenmesser bei kalter Luft?",
        "options": [
          "Im Sommer sind die Berge höher",
          "Im Winter sind die Berge höher",
          "Im Winter sind die Berge niedriger",
          "Temperatur hat keinen Einfluss"
        ],
        "answer": 1,
        "explanation": "In kalter Luft ziehen sich die Druckflächen zusammen. Der Höhenmesser zeigt eine zu hohe Flughöhe an. Das ist bei Gebirgsflügen kritisch: 'Im Winter sind die Berge höher'."
      },
      {
        "q": "Was passiert mit dem Fahrtmesser, wenn die statische Druckleitung blockiert ist und das Flugzeug steigt?",
        "options": [
          "Er zeigt zunehmende Fahrt an (fälschlicherweise)",
          "Er zeigt abnehmende Fahrt an (fälschlicherweise)",
          "Er ist nicht betroffen",
          "Er zeigt Null an"
        ],
        "answer": 1,
        "explanation": "Bei blockierter Statikleitung wirkt der zuletzt gemessene statische Druck. Beim Steigen wird der Außendruck geringer; da im Gehäuse ein konstant höherer Druck eingeschlossen ist, verhält sich die Anzeige entgegengesetzt zum echten Höhenmesser: Die angezeigte Fahrt nimmt ab."
      },
      {
        "q": "Welcher Referenzdruckwert wird für Überlandflüge in niedrigen Höhen (unterhalb der Übergangshöhe) verwendet?",
        "options": [
          "1013,25 hPa (Standard)",
          "QFE des Abflugplatzes",
          "QNH",
          "QNE"
        ],
        "answer": 2,
        "explanation": "Unterhalb der Übergangshöhe wird QNH eingestellt, damit alle Luftfahrzeuge ihre Höhe über MSL anzeigen und ein sicherer Abstand zu Hindernissen eingehalten werden kann."
      },
      {
        "q": "Was bedeutet die barometrische Höhenstufe?",
        "options": [
          "Die maximale Flughöhe eines Luftfahrzeugs",
          "Die Höhendifferenz, in der sich der Luftdruck um 1 hPa ändert",
          "Die Differenz zwischen QNH und QFE",
          "Die Staffelungshöhe zwischen zwei Luftfahrzeugen"
        ],
        "answer": 1,
        "explanation": "Die barometrische Höhenstufe beschreibt, wie viele Höhenmeter einer Druckänderung von 1 hPa entsprechen. In MSL-Nähe beträgt sie ca. 30 ft (8 m). Mit zunehmender Höhe wird sie größer."
      },
      {
        "q": "Beschreibe das Anzeigeverhalten von Höhenmesser und VSI bei blockierter Statikdruckleitung.",
        "options": [
          "Höhenmesser zeigt konstant, VSI zeigt konstant 0",
          "Höhenmesser zeigt weiter normal, VSI auch",
          "Höhenmesser sinkt auf 0, VSI zeigt Maximalwert",
          "Höhenmesser zeigt weiter normal, VSI zeigt 0"
        ],
        "answer": 0,
        "explanation": "Bei blockierter Statikleitung sind alle Druckinstrumente betroffen: Höhenmesser friert auf dem letzten Wert ein, VSI zeigt 0 an."
      }
    ]
  },

  // ──────────────────────────────────────────────────────────────
  // 4.2  KREISELINSTRUMENTE
  // ──────────────────────────────────────────────────────────────
  {
    "id": "agk-kreiselinstrumente",
    "title": "4.2 Kreiselinstrumente: Kurskreisel, Künstlicher Horizont & Wendezeiger",
    "exam": true,
    "summary": [
      "Kreiselinstrumente nutzen die Eigenschaft rotierender Massen (Massenträgheit), ihre Lage im Raum beizubehalten. Die Stabilität hängt von Kreiselmasse und Drehzahl ab. Wird von außen eine Kraft auf die Rotationsachse ausgeübt, weicht der Kreisel senkrecht dazu aus – dies nennt man Präzession. Antrieb erfolgt elektrisch oder pneumatisch (Unterdruckanlage). Kreiselinstrumente zeigen die Lage und Bewegung des Luftfahrzeugs in drei Achsen.",
      "Der Kurskreisel (Directional Gyro) zeigt den Steuerkurs; er ist kein Kompass und muss regelmäßig mit dem Magnetkompass abgeglichen werden, da er durch scheinbare Drift und tatsächliches Wandern vom Kurs abweicht. Der künstliche Horizont (Attitude Indicator) zeigt die Flugzeugneigung um Längs- und Querachse. Der Wendezeiger misst die Drehgeschwindigkeit um die Hochachse; die Kugellibelle gibt Auskunft über koordinierten Kurvenflug."
    ],
    "facts": [
      "Ein rotierender Kreisel behält aufgrund der Massenträgheit seine Lage im Raum bei.",
      "Präzession: Außenkraft → Kreisel weicht 90° zur Kraftrichtung aus.",
      "Kurskreisel: vollkardanische Aufhängung, Rotationsachse horizontal (N-S-Richtung).",
      "Kurskreisel muss alle 15 Minuten mit dem Magnetkompass synchronisiert werden.",
      "Scheinbare Drift durch Erdrotation = 15° × sin(Breitegrad) pro Stunde.",
      "Künstlicher Horizont: vollkardanische Aufhängung, Rotationsachse vertikal (zum Erdmittelpunkt).",
      "Beschleunigungsfehler beim Künstlichen Horizont: Beschleunigung → scheinbare Rechtskurve und Steigflug.",
      "Kurvenfehler beim Künstlichen Horizont (Pendellappen-Kurvenfehler): relevant bei Kurvenflügen.",
      "Wendezeiger: halbkardanische Aufhängung – misst Drehrate um Hochachse.",
      "Standardkurve = 3° pro Sekunde = vollständiger Kreis in 2 Minuten.",
      "Schräglage für Standardkurve: S = TAS/10 + 7 (in Grad).",
      "Libelle (Ball) zeigt koordinierten Kurvenflug – 'Ball in der Mitte'.",
      "Zu wenig Querneigung (Schmieren/Skidding) → Kugel driftet nach außen.",
      "Zu viel Querneigung (Schieben/Slipping) → Kugel driftet nach innen."
    ],
    "table": [
      ["Kurskreisel", "Vollkardanisch, horizontale Rotationsachse, zeigt Steuerkurs"],
      ["Künstlicher Horizont", "Vollkardanisch, vertikale Rotationsachse, zeigt Pitch & Roll"],
      ["Wendezeiger", "Halbkardanisch, zeigt Drehrate um Hochachse"],
      ["Turn & Bank Coordinator", "Erweiterter Wendezeiger, berücksichtigt auch Rollbewegungen"],
      ["Kugellibelle", "Zeigt Scheinlot – koordinierter Kurvenflug wenn Ball zentriert"],
      ["Scheinbare Drift DR", "DR = 15° × sin φ (φ = Breitegrad)"],
      ["Standardkurve", "3°/s Drehrate, 2-Minuten-Vollkreis"],
      ["Kardanfehler", "Fehlanzeige bei extremen Querlagen durch Kardanverschluss"],
      ["Beschleunigungsfehler (AI)", "Vorübergehend falsche Anzeige bei Beschleunigung/Verzögerung"]
    ],
    "focus": [
      "Kurskreisel ist kein Kompass – scheinbare und tatsächliche Drift kennen",
      "Ausrichten des Kurskreisels vor dem Flug und alle 15 Minuten",
      "Beschleunigungsfehler und Kurvenfehler des Künstlichen Horizonts",
      "Standardkurve: 3°/s, 2 Minuten, Schräglage = TAS/10 + 7",
      "Libelle: Seitenruder in Richtung der Kugel betätigen"
    ],
    "sources": [
      {"label": "Aircademy AGK Band 1 – Kap. 4.2 Kreiselinstrumente", "url": "https://aircademy.com"},
      {"label": "EASA ECQB – AGK Referenz", "url": "https://www.easa.europa.eu/en/domains/aircrew-and-medical/european-central-question-bank-ecqb"}
    ],
    "quiz": [
      {
        "q": "Was ist Präzession bei einem rotierenden Kreisel?",
        "options": [
          "Die Eigenschaft des Kreisels, in Richtung der angreifenden Kraft nachzugeben",
          "Die Ausweichbewegung des Kreisels senkrecht (90°) zur angreifenden Kraft",
          "Der Antriebsmechanismus des Kreisels",
          "Die Lagerreibung des Kreisels"
        ],
        "answer": 1,
        "explanation": "Präzession ist der charakteristische Effekt bei Kreiseln: Greift eine äußere Kraft an der Rotationsachse an, so weicht der Kreisel nicht in Kraftrichtung aus, sondern senkrecht dazu (90° versetzt)."
      },
      {
        "q": "Warum muss der Kurskreisel regelmäßig mit dem Magnetkompass abgeglichen werden?",
        "options": [
          "Weil er nach einem Gewittereinschlag defekt ist",
          "Wegen scheinbarer Drift (Erdrotation) und tatsächlichem Wandern (Lagerreibung)",
          "Weil er magnetisch ist und abweicht",
          "Nur bei IFR-Flügen notwendig"
        ],
        "answer": 1,
        "explanation": "Der Kurskreisel behält seine Raumlage bei, während sich die Erde dreht (scheinbare Drift: ca. 15°/h × sin(Breite)). Zusätzlich führen Lagerreibung und ungleichmäßige Massenverteilung zu tatsächlichem Wandern."
      },
      {
        "q": "Welche Schräglage erfordert eine Standardkurve bei einer Eigengeschwindigkeit (TAS) von 110 kt?",
        "options": [
          "11°",
          "18°",
          "25°",
          "30°"
        ],
        "answer": 1,
        "explanation": "Formel: S = TAS/10 + 7. Mit TAS = 110 kt: S = 110/10 + 7 = 11 + 7 = 18°."
      },
      {
        "q": "Was zeigt eine nach links ausgewanderte Kugellibelle (beim Turn Coordinator/Wendezeiger) an?",
        "options": [
          "Die Kurve ist zu langsam (Schieben/Slipping) – zu viel Querneigung",
          "Die Kurve ist koordiniert",
          "Die Kurve ist zu schnell (Schmieren/Skidding) – zu wenig Querneigung",
          "Das Instrument ist defekt"
        ],
        "answer": 0,
        "explanation": "Driftet die Kugel nach innen (in Kurvenrichtung links), ist die Querneigung zu groß gegenüber der Drehrate → Slipping/Schieben. Seitenruder in Richtung der Kugel betätigen."
      },
      {
        "q": "Was ist der Beschleunigungsfehler des Künstlichen Horizonts?",
        "options": [
          "Zeigt bei Beschleunigung scheinbar Rechtskurve und Steigflug",
          "Zeigt bei Beschleunigung korrekte Werte",
          "Zeigt bei Beschleunigung scheinbar Linkskurve und Sinkflug",
          "Hat keinen Einfluss auf die Anzeige"
        ],
        "answer": 0,
        "explanation": "Durch die konstruktionsbedingte Positionierung des Kreiselschwerpunkts reagiert das Kreiselsystem bei Längsbeschleunigung: Es wird eine scheinbare Rechtskurve und zu große Längsneigung angezeigt. Bei Verzögerung ist es umgekehrt."
      },
      {
        "q": "Eine Standardkurve hat eine Drehgeschwindigkeit von …",
        "options": [
          "1° pro Sekunde (Vollkreis in 6 Minuten)",
          "2° pro Sekunde (Vollkreis in 3 Minuten)",
          "3° pro Sekunde (Vollkreis in 2 Minuten)",
          "6° pro Sekunde (Vollkreis in 1 Minute)"
        ],
        "answer": 2,
        "explanation": "Die Standardkurve (Standard Rate Turn) beträgt 3° pro Sekunde. Ein vollständiger Kreis (360°) dauert damit genau 2 Minuten. Das entspricht der Markierung '2 MIN' am Wendezeiger."
      },
      {
        "q": "Welchen Unterschied hat der Turn & Bank Coordinator gegenüber dem klassischen Wendezeiger?",
        "options": [
          "Er misst nur Rollbewegungen, nicht Kurvendrehungen",
          "Er berücksichtigt neben der Hochachsendrehrate auch Rollbewegungen (Kardanrahmen um 30° geneigt)",
          "Er hat keine Kugellibelle",
          "Er misst die Fahrt"
        ],
        "answer": 1,
        "explanation": "Beim Turn & Bank Coordinator ist der Kardanrahmen um 30° zur Längsachse geneigt, sodass er sowohl Drehbewegungen um die Hochachse als auch Rollbewegungen erfasst. Dies verbessert die Reaktionszeit beim Einleiten von Kurven."
      },
      {
        "q": "Was ist der Kardanfehler (Gimbal Error) beim Kurskreisel?",
        "options": [
          "Ein mechanischer Defekt der Lager",
          "Fehlanzeige bei extremen Querlagen durch Verkanten der Kardanrahmen",
          "Elektrische Störung bei hoher Drehzahl",
          "Temperaturabhängige Abweichung"
        ],
        "answer": 1,
        "explanation": "Bei sehr großen Querlagen (über 55°) können sich die Kardanrahmen des Kurskreisels verkanten (Kardanverschluss). Das führt zu einer falschen Anzeige, die sich nach Beendigung der Kurve nach einiger Zeit von selbst korrigiert."
      }
    ]
  },

  // ──────────────────────────────────────────────────────────────
  // 4.3  TRIEBWERKSÜBERWACHUNGSINSTRUMENTE
  // ──────────────────────────────────────────────────────────────
  {
    "id": "agk-triebwerk-instrumente",
    "title": "4.3–4.4 Triebwerksüberwachung & Sonstige Instrumente",
    "exam": true,
    "summary": [
      "Im Cockpit eines Kolbenflugzeugs überwachen mehrere Instrumente den Zustand des Triebwerks. Der Drehzahlmesser (Tachometer) ist grundlegend; bei Verstellpropeller-Flugzeugen kommt die Ladedruckanzeige als Leistungsindikator hinzu. Öldruck und Öltemperatur müssen stets gemeinsam betrachtet werden – steigende Öltemperatur geht normalerweise mit leicht sinkendem Öldruck einher. Eine plötzliche Abweichung kann auf ernsthafte Triebwerksprobleme hinweisen.",
      "Zylinderkopftemperatur (CHT) und Abgastemperatur (EGT) dienen der optimalen Gemischeinstellung und Überwachung der Triebwerksbelastung. Die Kraftstoffdurchflussanzeige und Kraftstoffvorratsanzeige sind für die Flugplanung unerlässlich. Die Kraftstoffvorratsanzeige ist grundsätzlich ungenau (Schwimmer-Prinzip) und muss vor dem Flug durch Sichtkontrolle und Peilstab überprüft werden."
    ],
    "facts": [
      "Drehzahlmesser: zeigt Umdrehungen der Kurbelwelle pro Minute (U/min oder RPM).",
      "Bei Verstellpropeller: Leistungseinstellung = Drehzahl + Ladedruck gemeinsam.",
      "Ladedruckanzeige: misst Druck im Ansaugrohr zwischen Drosselklappe und Zylinder (in inHg).",
      "Öldruckanzeige: wichtigstes Triebwerkinstrument – misst Gesamtdruck hinter der Ölpumpe via Bourdon-Rohr.",
      "60 Sekunden nach Motorstart sollte ausreichender Öldruck vorhanden sein.",
      "Öldruck und Öltemperatur immer gemeinsam betrachten: 'Vom Hoch ins Tief geht's schief'.",
      "CHT misst am kritischsten Zylinder – bei Steigflug ggf. Schräglage verringern oder Gemisch anreichern.",
      "EGT (Exhaust Gas Temperature): Peak-EGT ist die maximale Abgastemperatur bei Gemischabmagerung.",
      "Kraftstoffdurchfluss in GAL, lbs oder Liter pro Stunde.",
      "Kraftstoffvorratsanzeige: Schwimmer-Prinzip, bei Steig-/Sinkflug ungenau → Sichtprüfung vor dem Flug!",
      "Unterdruckmesser: überwacht die Unterdruckanlage für Kreiselinstrumente (normaler Betrieb: kleines grünes Band).",
      "Amperemeter: misst Ladestrom (positiv = Batterie wird geladen) oder Gesamtstromverbrauch.",
      "Voltmeter: zeigt Batteriespannung; ca. 12–13 V bei stehendem Motor, ca. 14 V mit Generator."
    ],
    "table": [
      ["Drehzahlmesser", "U/min der Kurbelwelle, normale Betriebsbereiche grün markiert"],
      ["Ladedruckanzeige", "Nur bei Verstellpropeller-Flugzeugen; inHg, zeigt Saugrohrdruck"],
      ["Öldruckanzeige", "Gesamtdruck im Ölkreislauf hinter der Pumpe; Bourdon-Rohr"],
      ["Öltemperaturanzeige", "Temperatur des Öls hinter der Pumpe; elektrisches Widerstandsthermometer"],
      ["CHT", "Zylinderkopftemperatur am kritischsten Zylinder; Thermoelement"],
      ["EGT", "Abgastemperatur hinter der Brennkammer; Thermoelement"],
      ["Kraftstoffdurchfluss", "Pro Stunde verbrauchtes Kraftstoffvolumen; Stauscheibenmessung"],
      ["Kraftstoffvorratsanzeige", "Füllstand je Tank; Schwimmerprinzip – grundsätzlich ungenau"],
      ["Unterdruckmesser", "Betriebsdruck der Kreiselinstrumente-Unterdruckanlage"],
      ["Amperemeter", "Ladestrom der Batterie oder Gesamtverbrauch aller Verbraucher"],
      ["Voltmeter", "Batteriespannung; bei laufendem Generator ca. 14 V"]
    ],
    "focus": [
      "Öldruck und Öltemperatur gemeinsam interpretieren",
      "CHT-Reaktion bei Steigflug: Schräglage verringern, Gemisch anreichern",
      "EGT zur Gemischeinstellung: Abmagern bis Peak EGT, dann leicht anfetten",
      "Kraftstoffvorratsanzeige unzuverlässig → immer Sichtkontrolle vor dem Flug",
      "Ladedruckanzeige nur bei Verstellpropeller relevant"
    ],
    "sources": [
      {"label": "Aircademy AGK Band 1 – Kap. 4.3 Triebwerksüberwachungsinstrumente", "url": "https://aircademy.com"},
      {"label": "EASA ECQB – AGK Referenz", "url": "https://www.easa.europa.eu/en/domains/aircrew-and-medical/european-central-question-bank-ecqb"}
    ],
    "quiz": [
      {
        "q": "Wie soll sich die Öldruckanzeige direkt nach dem Motorstart verhalten?",
        "options": [
          "Sofort im grünen Bereich sein",
          "Zunächst im niedrigen Bereich, dann innerhalb von ca. 60 Sekunden steigen",
          "Im roten Bereich bleiben",
          "Bei 0 bleiben"
        ],
        "answer": 1,
        "explanation": "Direkt nach dem Kaltstart ist das Öl noch zähflüssig; der Druck baut sich langsam auf. Innerhalb von 60 Sekunden sollte ein ausreichender Öldruck erreicht sein. Hohe Drehzahlen sollten erst danach eingestellt werden."
      },
      {
        "q": "Warum muss die Kraftstoffvorratsanzeige vor jedem Flug durch Sichtkontrolle überprüft werden?",
        "options": [
          "Weil das Instrument oft zu niedrig hängt",
          "Weil das Schwimmer-Messprinzip ungenau ist und Fehlanzeigen möglich sind",
          "Weil das Voltmeter die Anzeige beeinflusst",
          "Weil die Anzeige nur in Litern, nicht in Gallonen misst"
        ],
        "answer": 1,
        "explanation": "Der Kraftstoffstandmesser nutzt einen Schwimmer, dessen Position durch Steig-/Sinkflug und unebene Böden beeinflusst wird. Die Anzeige ist grundsätzlich ungenau; vor dem Flug ist deshalb immer eine direkte Sichtkontrolle oder Peilstab-Messung vorgeschrieben."
      },
      {
        "q": "Was bedeutet 'Peak EGT' bei der Gemischeinstellung?",
        "options": [
          "Die Abgastemperatur soll auf ein Minimum gebracht werden",
          "Die maximale Abgastemperatur, die bei vollständiger Gemischabmagerung erreicht wird",
          "Der Ausgangszustand vor der Einstellung",
          "Die Temperatur bei vollem Gaz"
        ],
        "answer": 1,
        "explanation": "Beim Abmagern des Gemisches steigt die EGT zunächst. Der höchste Punkt ist die Peak-EGT. Anschließend wird das Gemisch leicht angefettet (z.B. 50°F unter Peak EGT für Reiseflug), um den Motor zu schonen."
      },
      {
        "q": "Was bedeutet es, wenn die Öltemperatur steigt und gleichzeitig der Öldruck sinkt?",
        "options": [
          "Normaler Betriebszustand",
          "Hinweis auf zu wenig Öl oder erhöhte Motorbelastung – sofortige Aufmerksamkeit erforderlich",
          "Nur im Steigflug normal",
          "Das Thermometer ist defekt"
        ],
        "answer": 1,
        "explanation": "Steigende Öltemperatur erhöht die Viskosität des Öls; ein leichtes Absinken des Öldrucks ist daher normal. Ein starkes Absinken des Öldrucks bei steigender Öltemperatur deutet aber auf zu wenig Öl oder Ölverlust hin."
      },
      {
        "q": "Wofür wird die Ladedruckanzeige (Manifold Pressure Gauge) benötigt?",
        "options": [
          "Bei allen Kolbenflugzeugen zur Grundleistungseinstellung",
          "Nur bei Flugzeugen mit Verstellpropeller zur Leistungsbeurteilung neben der Drehzahl",
          "Nur in der Reiseflugphase",
          "Zur Öltemperaturmessung"
        ],
        "answer": 1,
        "explanation": "Bei Flugzeugen mit Festpropeller zeigt der Drehzahlmesser direkt die Motorleistung. Bei Verstellpropeller-Flugzeugen bleibt die Drehzahl konstant und wird separat eingestellt; hier ist die Ladedruckanzeige notwendig, um die Motorleistung zu beurteilen."
      },
      {
        "q": "Was überwacht der Unterdruckmesser (Suction Indicator)?",
        "options": [
          "Den Kraftstoffdruck im Einspritzystem",
          "Den Unterdruck der Unterdruckanlage, die Kreiselinstrumente antreibt",
          "Den Kabinendruck",
          "Die Motoröltemperatur"
        ],
        "answer": 1,
        "explanation": "Viele Kreiselinstrumente (Kurskreisel, Künstlicher Horizont) werden pneumatisch über eine Unterdruckanlage angetrieben. Der Unterdruckmesser (Suction Indicator) überwacht diesen Betriebsdruck; der zulässige Bereich ist grün markiert."
      },
      {
        "q": "Was zeigt ein Amperemeter an, das den Ladestrom der Batterie misst?",
        "options": [
          "Die Bordspannung in Volt",
          "Ob die Batterie geladen wird (+) oder ob mehr Strom verbraucht als erzeugt wird (−)",
          "Den Kraftstoffverbrauch",
          "Die Temperatur der Batterie"
        ],
        "answer": 1,
        "explanation": "Ein Ladeamperemeter zeigt positiven Strom, wenn der Generator Strom liefert und die Batterie geladen wird. Negative Anzeige bedeutet, dass Verbraucher mehr Strom ziehen als der Generator liefert oder der Generator ausgefallen ist."
      }
    ]
  },

  // ──────────────────────────────────────────────────────────────
  // 4.5  ELEKTRONISCHE ANZEIGEN (EFIS / GLASS COCKPIT)
  // ──────────────────────────────────────────────────────────────
  {
    "id": "agk-elektronische-anzeigen",
    "title": "4.5 Elektronische Anzeigen: EFIS, PFD, ND und Glass Cockpit",
    "exam": true,
    "summary": [
      "Elektronische Fluganzeigen (Electronic Flight Displays, EFD / Electronic Flight Information System, EFIS) ersetzen klassische analoge Einzelinstrumente durch integrierte Bildschirmsysteme. Der große Vorteil: Alle relevanten Informationen werden auf einem Bildschirm übersichtlich dargestellt; die mechanische Störanfälligkeit sinkt im Vergleich zu analogen Instrumenten erheblich. Allerdings ist eine genaue Einweisung in das jeweilige System unbedingt erforderlich.",
      "Ein Bordcomputer (Air Data Computer, ADC) verarbeitet die Sensordaten und leitet sie an die Displays weiter. Das Primary Flight Display (PFD) zeigt Fluglage, Geschwindigkeit, Höhe und Steigleistung. Das Navigation Display (ND) zeigt Kurs- und Navigationsinformationen. Das Multifunktionsdisplay (MFD) kann Triebwerksparameter, Wetter und weitere Informationen anzeigen."
    ],
    "facts": [
      "EFIS/Glass Cockpit integriert viele Einzelinstrumente auf wenigen Bildschirmen.",
      "Air Data Computer (ADC) = Bordcomputer: verarbeitet statischen Druck, Staudruck, Außentemperatur, Öldruck.",
      "Navigationsdatenbank muss alle 28 Tage aktualisiert werden.",
      "PFD zeigt: Künstlichen Horizont, Geschwindigkeit (Speed Tape), Höhe (Altitude Tape), VSI, Kurs (HSI).",
      "Speed Tape: Geschwindigkeit als vertikales Band links; farbige Bereiche entsprechen analogen Farbmarkierungen.",
      "Altitude Tape: Höhe als Band rechts; QNH-Einstellung und ausgewählte Zielflughöhe sichtbar.",
      "Flight Director: zeigt empfohlene Fluglage als Kommandonadeln im künstlichen Horizont.",
      "Navigation Display (ND): Basis ist meist HSI; kann Flugweg, Wegpunkte, Wetter und Verkehr (TCAS) zeigen.",
      "MFD (Multifunktionsdisplay): Triebwerksüberwachung, Navigation, Wetter in Echtzeit.",
      "EICAS / ECAM: Engine Indication and Crew Alerting System – bei Verkehrsflugzeugen, zeigt kritische Zustände.",
      "Flugleistungsdatenbank: Aircraft Performance Database liefert Daten für Start-/Landestrecken."
    ],
    "table": [
      ["PFD", "Primary Flight Display: Fluglage, Geschwindigkeit, Höhe, VSI, Kurs"],
      ["ND", "Navigation Display: Kurs, HSI, Wegpunkte, Wetter, TCAS"],
      ["MFD", "Multifunktionsdisplay: Triebwerk, Navigation, Wetter nach Wahl"],
      ["ADC/FDC", "Bordcomputer: verarbeitet Sensordaten, berechnet Anzeigen"],
      ["Flight Director", "Kommandonadeln im PFD – zeigen empfohlene Fluglage"],
      ["Speed Tape", "Vertikales Geschwindigkeitsband links im PFD, mit Farbmarkierungen"],
      ["Altitude Tape", "Vertikales Höhenband rechts im PFD, mit QNH und Zielhöhe"],
      ["AHRS", "Attitude & Heading Reference System – Fluglage- und Kursreferenz"],
      ["Navigationsdatenbank", "Alle 28 Tage zu aktualisieren; VOR, DME, NDB, Wegpunkte, Routen"]
    ],
    "focus": [
      "Drei Grunddisplaytypen: PFD, ND, MFD und ihre Informationsinhalte",
      "ADC: zentraler Bordcomputer – Ausfall wirkt sich auf alle Anzeigen aus",
      "Navigationsdatenbank alle 28 Tage aktualisieren",
      "Glass Cockpit benötigt intensive Einweisung vor dem Betrieb",
      "Speed Tape Farbmarkierungen entsprechen analogen Fahrtmessermarkierungen"
    ],
    "sources": [
      {"label": "Aircademy AGK Band 1 – Kap. 4.5 Elektronische Anzeigen", "url": "https://aircademy.com"},
      {"label": "EASA ECQB – AGK Referenz", "url": "https://www.easa.europa.eu/en/domains/aircrew-and-medical/european-central-question-bank-ecqb"}
    ],
    "quiz": [
      {
        "q": "Welche drei Grundtypen von Displays gibt es in einem typischen Glass-Cockpit-System?",
        "options": [
          "GPS, FMS, Autopilot",
          "PFD (Primary Flight Display), ND (Navigation Display) und MFD (Multifunktionsdisplay)",
          "Radar, Transponder und TCAS",
          "Höhenmesser, Fahrtmesser und Variometer"
        ],
        "answer": 1,
        "explanation": "Das Glass Cockpit besteht aus PFD (Fluglage, Geschwindigkeit, Höhe), ND (Navigation, Kurs, HSI) und MFD (Triebwerk, Wetter, Navigation nach Bedarf)."
      },
      {
        "q": "Was ist der Air Data Computer (ADC)?",
        "options": [
          "Ein Navigationssystem",
          "Ein zentraler Bordcomputer, der Druckdaten und Sensormessungen verarbeitet und an die Displays weiterleitet",
          "Ein Kommunikationsgerät",
          "Der Autopilot-Rechner"
        ],
        "answer": 1,
        "explanation": "Der ADC (auch FDC = Flight Data Computer) verarbeitet statischen Druck, Staudruck, Außentemperatur und andere Sensordaten. Er berechnet daraus Geschwindigkeit, Höhe und andere Parameter und leitet sie digital an alle Displays weiter."
      },
      {
        "q": "In welchem Zyklus muss die Navigationsdatenbank aktualisiert werden?",
        "options": [
          "Täglich",
          "Wöchentlich",
          "Alle 28 Tage",
          "Jährlich"
        ],
        "answer": 2,
        "explanation": "Die Navigationsdatenbank (Wegpunkte, VOR, DME, NDB, Lufträume etc.) muss nach ICAO-Standard alle 28 Tage auf den neuesten Stand gebracht werden, da sich Frequenzen, Luftraumgrenzen und Verfahren ändern."
      },
      {
        "q": "Was unterscheidet elektronische EFIS-Instrumente von klassischer Instrumentierung?",
        "options": [
          "EFIS ist stets ungenauer",
          "EFIS integriert viele Informationen übersichtlich, hat höhere Zuverlässigkeit und ist konfigurierbar",
          "EFIS benötigt keine Einweisung",
          "EFIS funktioniert ohne Strom"
        ],
        "answer": 1,
        "explanation": "EFIS bietet übersichtlichere Informationsdarstellung, geringere mechanische Störanfälligkeit und mehr Flexibilität. Allerdings ist bei einem Totalausfall der Anlage alle Redundanz weg – daher sind bei Allgemeinluffahrt oft pneumatische Notgeräte vorhanden."
      },
      {
        "q": "Was zeigt der Flight Director?",
        "options": [
          "Den Autopiloten-Status",
          "Kommandonadeln im PFD, die die empfohlene Fluglage zum Erreichen des eingestellten Flugwegs anzeigen",
          "Die Kraftstoffmenge",
          "Die Navigation zum nächsten Wegpunkt"
        ],
        "answer": 1,
        "explanation": "Der Flight Director visualisiert im PFD die optimale Fluglage als Kommandonadeln (Pitch und Roll). Der Pilot fliegt das Flugzeug 'auf die Nadeln' und hält so den vorprogrammierten oder eingestellten Flugweg."
      }
    ]
  }
];

window.NEW_CHAPTERS_AERO = [
  // ──────────────────────────────────────────────────────────────
  // AERODYNAMIK KAP. 1: EIN KÖRPER IM LUFTSTROM
  // ──────────────────────────────────────────────────────────────
  {
    "id": "pof-atmosphaere-grundlagen",
    "title": "1. Atmosphäre, Luftwiderstand, Grenzschicht & Bernoulli",
    "exam": true,
    "summary": [
      "Flugzeuge bewegen sich hauptsächlich in der Troposphäre (0–11 km). Die ICAO-Standardatmosphäre (ISA) definiert einheitliche Bedingungen: am MSL 1013,25 hPa, +15°C, 1,225 kg/m³ Dichte, Temperaturabnahme 2°C / 1.000 ft bis zur Tropopause in 11 km (-56,5°C). Alle Flugleistungsangaben beziehen sich auf ISA-Bedingungen. Der Luftwiderstand steigt quadratisch mit der Geschwindigkeit: Bei doppelter Geschwindigkeit vervierfacht er sich. Formel: D = ½·v²·A·ρ·cD.",
      "Die Grenzschicht ist der Bereich nahe der Körperoberfläche, in dem die Strömung von Null (Oberfläche) auf volle Geschwindigkeit ansteigt. Sie kann laminar (reibungsarm, Stromlinien parallel) oder turbulent (stärker, aber besser anliegend) sein. Die Bernoulli-Gleichung beschreibt den Zusammenhang: Gesamtdruck = Staudruck + statischer Druck = konstant. Höhere Strömungsgeschwindigkeit → niedrigerer statischer Druck."
    ],
    "facts": [
      "Troposphäre: 0–11 km Höhe, dort finden fast alle Flüge mit Luftfahrzeugen der Allgemeinen Luftfahrt statt.",
      "ISA-Bedingungen in MSL: 1013,25 hPa, +15°C, 1,225 kg/m³.",
      "Temperaturabnahme in der Troposphäre: 2°C pro 1.000 ft (= 0,65°C pro 100 m).",
      "Tropopause bei 11 km (36.000 ft), dort ca. −56,5°C.",
      "Luftdruck halbiert sich alle 18.000 ft (5.500 m).",
      "Luftwiderstand steigt quadratisch mit der Geschwindigkeit: D = ½·v²·A·ρ·cD.",
      "Bei doppelter Geschwindigkeit: viermal so viel Luftwiderstand.",
      "Widerstandsbeiwert cD beschreibt die Form des Körpers (unabhängig von Größe/Geschwindigkeit).",
      "Laminare Grenzschicht: Stromlinien parallel, geringer Widerstand.",
      "Turbulente Grenzschicht: Verwirbelungen, höherer Widerstand, aber besseres Anliegen an Oberfläche.",
      "Umschlagpunkt: Übergang von laminar zu turbulent wird durch Reynolds-Zahl beschrieben.",
      "Bernoulli-Gleichung: p_gesamt = p_stat + p_dyn = konstant.",
      "Kontinuitätsgesetz: In einer Stromröhre fließt pro Zeiteinheit dieselbe Luftmasse durch jeden Querschnitt.",
      "Querschnittsverengung → höhere Strömungsgeschwindigkeit, niedrigerer statischer Druck.",
      "Staudruck (dynamischer Druck) = ½·ρ·v² – Grundlage für Fahrtmesser."
    ],
    "table": [
      ["ISA MSL-Bedingungen", "1013,25 hPa, +15°C, 1,225 kg/m³, 0% relative Feuchte"],
      ["Temperaturabnahme", "2°C/1.000 ft = 0,65°C/100 m bis Tropopause"],
      ["Tropopause", "11 km / 36.000 ft, −56,5°C"],
      ["Luftwiderstandsformel", "D = ½ · v² · A · ρ · cD"],
      ["Widerstandsbeiwert cD", "Formfaktor des Körpers; kleine Werte = stromlinienförmig"],
      ["Bernoulli-Gleichung", "p_stat + ½·ρ·v² = const (Gesamtdruck konstant)"],
      ["Kontinuitätsgesetz", "A₁·v₁ = A₂·v₂ (gleicher Massendurchfluss)"],
      ["Laminare Strömung", "Reibungsarm, Stromlinien parallel, bei niedriger Geschwindigkeit"],
      ["Turbulente Strömung", "Wirbelbildung, höhere Reibung, Umschlag ab krit. Reynolds-Zahl"],
      ["Reynolds-Zahl RE", "RE = v·s·ρ/μ – bestimmt ob Strömung laminar oder turbulent"]
    ],
    "focus": [
      "ISA-Bedingungen auswendig kennen: 1013,25 hPa, 15°C, 1,225 kg/m³",
      "Luftwiderstand quadratisch mit Geschwindigkeit – verdoppeln = vierfacher Widerstand",
      "Bernoulli: höhere Geschwindigkeit = niedrigerer statischer Druck",
      "Laminar vs. turbulent: laminare Strömung reibungsärmer, aber anfälliger für Abriss",
      "Kontinuitätsgesetz: Querschnittsverengung → Geschwindigkeit steigt"
    ],
    "sources": [
      {"label": "Aircademy Aerodynamik Band 2 – Kap. 1 Ein Körper im Luftstrom", "url": "https://aircademy.com"},
      {"label": "EASA ECQB – Aerodynamik Referenz", "url": "https://www.easa.europa.eu/en/domains/aircrew-and-medical/european-central-question-bank-ecqb"}
    ],
    "quiz": [
      {
        "q": "Was sind die ISA-Standardbedingungen in Meereshöhe (MSL)?",
        "options": [
          "1000 hPa, 0°C, 1,0 kg/m³",
          "1013,25 hPa, +15°C, 1,225 kg/m³",
          "1013,25 hPa, +20°C, 1,0 kg/m³",
          "1013 hPa, +5°C, 1,2 kg/m³"
        ],
        "answer": 1,
        "explanation": "Die ICAO-Standardatmosphäre (ISA) definiert in MSL: Luftdruck 1013,25 hPa, Temperatur +15°C und Luftdichte 1,225 kg/m³. Diese Werte sind für alle Flugleistungsangaben die Bezugsbasis."
      },
      {
        "q": "Auf welche Schicht der Atmosphäre beschränken sich die meisten PPL-Flüge?",
        "options": [
          "Stratosphäre",
          "Troposphäre",
          "Mesosphäre",
          "Ionosphäre"
        ],
        "answer": 1,
        "explanation": "Die Troposphäre erstreckt sich von 0 bis ca. 11 km (36.000 ft). In ihr finden praktisch alle Flüge der Allgemeinen Luftfahrt statt. Sie ist charakterisiert durch die Temperaturabnahme mit der Höhe."
      },
      {
        "q": "Um welchen Faktor steigt der Luftwiderstand, wenn die Fluggeschwindigkeit verdoppelt wird?",
        "options": [
          "Faktor 2",
          "Faktor 4",
          "Faktor 8",
          "Faktor 1,5"
        ],
        "answer": 1,
        "explanation": "Die Widerstandsformel D = ½·v²·A·ρ·cD zeigt: Der Widerstand steigt mit dem Quadrat der Geschwindigkeit. Verdoppelte Geschwindigkeit → vierfacher (2²) Widerstand."
      },
      {
        "q": "Was beschreibt die Bernoulli-Gleichung?",
        "options": [
          "Die Schwerkraft nimmt mit der Höhe ab",
          "In einer Strömung ist die Summe aus statischem und dynamischem Druck konstant",
          "Bei höherer Temperatur sinkt der Luftdruck",
          "Der Luftwiderstand steigt linear mit der Geschwindigkeit"
        ],
        "answer": 1,
        "explanation": "Bernoulli: p_stat + ½·ρ·v² = const. Höhere Strömungsgeschwindigkeit → mehr dynamischer Druck (Staudruck) → niedrigerer statischer Druck. Dieser Effekt ist grundlegend für Auftriebserzeugung am Tragflügel."
      },
      {
        "q": "Was besagt das Kontinuitätsgesetz?",
        "options": [
          "Luft ist inkompressibel und hat konstante Dichte",
          "In einer Stromröhre muss zu jeder Zeit dieselbe Luftmasse durch jeden Querschnitt fließen",
          "Die Strömungsgeschwindigkeit ist überall konstant",
          "Verengungen führen zu geringerer Strömungsgeschwindigkeit"
        ],
        "answer": 1,
        "explanation": "Das Kontinuitätsgesetz sagt: Bei gleicher Zeit muss durch einen engeren Querschnitt dieselbe Luftmasse fließen. Da weniger Platz ist, müssen die Teilchen schneller werden (A₁·v₁ = A₂·v₂). Dies führt bei Querschnittsverengungen zu höherer Geschwindigkeit und – nach Bernoulli – zu niedrigerem statischem Druck."
      },
      {
        "q": "Welchen Vorteil hat eine turbulente Grenzschicht gegenüber einer laminaren?",
        "options": [
          "Deutlich geringerer Reibungswiderstand",
          "Sie liegt besser an der Oberfläche an und verzögert den Strömungsabriss",
          "Geringere Wärmeentwicklung",
          "Kein Vorteil; laminare Strömung ist immer besser"
        ],
        "answer": 1,
        "explanation": "Obwohl die turbulente Grenzschicht durch gegenseitige Beeinflussung der Luftteilchen einen höheren Reibungswiderstand erzeugt, liegt sie besser an ungünstigen Oberflächen an und kann auch dort noch der Körperform folgen, wo laminare Strömung bereits abreißen würde."
      },
      {
        "q": "Welcher Temperaturgradient gilt in der Troposphäre?",
        "options": [
          "0,5°C pro 100 m",
          "0,65°C pro 100 m (= 2°C pro 1.000 ft)",
          "1°C pro 100 m",
          "Die Temperatur bleibt konstant"
        ],
        "answer": 1,
        "explanation": "In der Troposphäre nimmt die Temperatur mit 0,65°C pro 100 m (entspricht ca. 2°C pro 1.000 ft) ab. An der Tropopause (11 km / 36.000 ft) beträgt die Temperatur ca. −56,5°C."
      }
    ]
  },

  // ──────────────────────────────────────────────────────────────
  // AERODYNAMIK KAP. 2: STRÖMUNG AM TRAGFLÜGEL
  // ──────────────────────────────────────────────────────────────
  {
    "id": "pof-stroemung-tragfluegel",
    "title": "2. Strömung am Tragflügel: Profilquerschnitt & Auftriebserzeugung",
    "exam": true,
    "summary": [
      "Ein Tragflügelquerschnitt (Profilquerschnitt) hat eine runde Vorderkante und läuft nach hinten spitz zu. Dies ermöglicht die Umströmung aus verschiedenen Anströmwinkeln. Auftrieb entsteht durch eine Druckdifferenz zwischen Profiloberseite (Unterdruck) und Profilunterseite (höherer Druck). Diese Druckdifferenz entsteht durch unterschiedliche Strömungsgeschwindigkeiten: Auf der Oberseite sind die Stromlinien enger (höhere Geschwindigkeit, niedriger Druck nach Bernoulli), auf der Unterseite weiter.",
      "Der Anstellwinkel (Angle of Attack, AoA) zwischen Profilsehne und Anströmrichtung bestimmt die Stärke des Auftriebs. Mit zunehmendem Anstellwinkel steigt der Auftrieb bis zum kritischen Anstellwinkel, ab dem die Strömung abreißt (Strömungsabriss/Stall). Das Tragflügelprofil erzeugt gegenüber einem einfachen Brett bei gleicher Anströmgeschwindigkeit mehr Auftrieb bei geringerem Widerstand – und das über einen größeren Bereich von Anströmwinkeln."
    ],
    "facts": [
      "Tragflügelprofil: runde Vorderkante, spitze Hinterkante – für breiten Anströmwinkelbereich geeignet.",
      "Auftrieb = Druckdifferenz: Unterdruck oben, Überdruck unten → Nettokraft nach oben.",
      "Kutta-Bedingung: Strömung muss an der Hinterkante parallel abströmen.",
      "Anstellwinkel (AoA): Winkel zwischen Profilsehne und Anströmrichtung.",
      "Auftriebsformel: FA = ½·v²·A·ρ·cA (analog zu Widerstand).",
      "Auftriebsbeiwert cA hängt stark vom Anstellwinkel ab.",
      "Kritischer Anstellwinkel: typisch 15–16°; darüber = Strömungsabriss.",
      "Stall = Überschreiten des kritischen Anstellwinkels, nicht primär Geschwindigkeitsproblem.",
      "Wölbungsstich (camber): asymmetrisches Profil erzeugt schon bei 0° AoA Auftrieb.",
      "Zirkulation: das entscheidende Konzept der Auftriebserzeugung – Überlagerung von Grundströmung und Zirkulationsströmung.",
      "Staudruck an Vorderkante: maximaler Staudruck direkt am Stagnationspunkt.",
      "Profilwiderstand setzt sich zusammen aus: Reibungswiderstand + Druckwiderstand.",
      "Induzierter Widerstand entsteht durch Randwirbel am Flügelende – proportional zu cA².",
      "Gesamtwiderstand = Profilwiderstand + induzierter Widerstand + parasitärer Widerstand."
    ],
    "table": [
      ["Anstellwinkel (AoA)", "Winkel zwischen Profilsehne und Anströmung; bestimmt Auftriebsgröße"],
      ["Auftriebsbeiwert cA", "Auftriebseffizienz; steigt mit AoA bis kritischer Winkel"],
      ["Profilsehne", "Gerade Verbindungslinie von Vorderkante zu Hinterkante"],
      ["Profilwölbung", "Asymmetrie Ober-/Unterseite; gewölbte Profile haben bei 0° AoA Auftrieb"],
      ["Stagnationspunkt", "Punkt vor der Vorderkante, wo Strömung zum Stillstand kommt"],
      ["Zirkulation", "Überlagerte Strömung, die Geschwindigkeitsunterschied Ober-/Unterseite erzeugt"],
      ["Kritischer AoA", "Ca. 15–16°; darüber Strömungsabriss (Stall)"],
      ["Induzierter Widerstand", "Durch Randwirbel; steigt mit cA² → groß bei niedriger Geschwindigkeit"],
      ["Profilwiderstand", "Summe aus Reibungswiderstand und Formwiderstand des Profils"],
      ["Gleitpolares Diagram", "Darstellung von cA über cW – optimales Gleiten bei max. cA/cW"]
    ],
    "focus": [
      "Druckverteilung am Profil: Unterdruck oben, höherer Druck unten",
      "Anstellwinkel als Hauptregulator des Auftriebs",
      "Stall = kritischer Anstellwinkel überschritten (nicht allein Geschwindigkeitsproblem!)",
      "Induzierter Widerstand steigt bei niedrigen Geschwindigkeiten",
      "Profilvorteil gegenüber Brett: mehr Auftrieb bei weniger Widerstand"
    ],
    "sources": [
      {"label": "Aircademy Aerodynamik Band 2 – Kap. 2 Strömung am Tragflügel", "url": "https://aircademy.com"},
      {"label": "EASA ECQB – Aerodynamik Referenz", "url": "https://www.easa.europa.eu/en/domains/aircrew-and-medical/european-central-question-bank-ecqb"}
    ],
    "quiz": [
      {
        "q": "Welche Druckverhältnisse an einem umströmten Tragflügelprofil sind für die Auftriebsbildung erforderlich?",
        "options": [
          "Überdruck auf der Profiloberseite und Unterdruck auf der Unterseite",
          "Unterdruck auf der Profiloberseite und erhöhter Druck auf der Profilunterseite",
          "Gleicher Druck auf beiden Seiten",
          "Überdruck auf beiden Seiten"
        ],
        "answer": 1,
        "explanation": "Für Auftrieb muss der statische Druck auf der Profiloberseite geringer sein als auf der Unterseite. Nach Bernoulli entsteht das durch höhere Strömungsgeschwindigkeit auf der Oberseite (engere Stromlinien)."
      },
      {
        "q": "Welche Vorteile besitzt ein Tragflügelprofil gegenüber einem einfach 'Brett' hinsichtlich der Auftriebserzeugung?",
        "options": [
          "Die Auftriebskraft ist unabhängig vom Anströmwinkel",
          "Nur die Profilform ist in der Lage, Auftrieb zu erzeugen",
          "Bei gleicher Anströmgeschwindigkeit erzeugt ein Tragflügelprofil mehr Auftrieb bei geringerem Widerstand und über einen größeren Bereich von Anströmwinkeln",
          "Ein Tragflügelprofil erzeugt Auftrieb über einen größeren Bereich von Anströmwinkeln"
        ],
        "answer": 2,
        "explanation": "Das Tragflügelprofil bietet gegenüber einem Brett den Vorteil, bei gleicher Anströmgeschwindigkeit mehr Auftrieb bei weniger Widerstand zu erzeugen. Zusätzlich ist es durch die runde Vorderkante für einen breiteren Anströmwinkelbereich geeignet."
      },
      {
        "q": "Was ist der Anstellwinkel (Angle of Attack)?",
        "options": [
          "Der Winkel zwischen Rumpflängsachse und Horizontalebene",
          "Der Winkel zwischen Profilsehne und Anströmrichtung",
          "Der Winkel, unter dem der Pilot sitzt",
          "Der Winkel zwischen Flügel und Rumpf"
        ],
        "answer": 1,
        "explanation": "Der Anstellwinkel (AoA) ist der Winkel zwischen der Profilsehne (Linie von Vorderkante zu Hinterkante) und der Richtung der anströmenden Luft. Er ist der wichtigste Parameter für den Auftrieb."
      },
      {
        "q": "In welchem Bereich des Tragflügelprofils wird der größte Beitrag zur Auftriebserzeugung erbracht?",
        "options": [
          "An der Hinterkante",
          "Im vorderen Bereich der Profiloberseite, besonders nahe der Vorderkante",
          "Auf der Profilunterseite gleichmäßig verteilt",
          "Am Stagnationspunkt direkt"
        ],
        "answer": 1,
        "explanation": "Der größte Unterdruckanteil entsteht auf der Profiloberseite, insbesondere im vorderen Bereich nahe der Vorderkante. Dort sind die Stromlinien am stärksten zusammengepresst → höchste Strömungsgeschwindigkeit → größter Unterdruckpeak."
      },
      {
        "q": "Auf welchem Erhaltungssatz basiert das Kontinuitätsgesetz?",
        "options": [
          "Energieerhaltung",
          "Impulserhaltung",
          "Massenerhaltung",
          "Rotations-Invarianz"
        ],
        "answer": 2,
        "explanation": "Das Kontinuitätsgesetz basiert auf der Massenerhaltung: In einer Stromröhre muss stets dieselbe Masse pro Zeiteinheit durch jeden Querschnitt fließen. Wird der Querschnitt enger, muss die Strömung schneller werden."
      },
      {
        "q": "Auf welchem Erhaltungssatz basiert die Bernoulli-Gleichung?",
        "options": [
          "Energieerhaltung",
          "Impulserhaltung",
          "Massenerhaltung",
          "Rotations-Invarianz"
        ],
        "answer": 0,
        "explanation": "Die Bernoulli-Gleichung leitet sich aus der Energieerhaltung ab: In einer Stromröhre bleibt die Summe aus kinetischer (dynamischer) und potentieller (statischer) Druckenergie konstant."
      },
      {
        "q": "Ab welchem Anstellwinkel kommt es typischerweise zum Strömungsabriss (Stall)?",
        "options": [
          "5°",
          "10°",
          "15–16°",
          "25–30°"
        ],
        "answer": 2,
        "explanation": "Der kritische Anstellwinkel, ab dem die Strömung auf der Profiloberseite abreißt, liegt typischerweise bei 15–16°. Die exakten Werte sind profilabhängig und im Flughandbuch des jeweiligen Flugzeugs angegeben."
      },
      {
        "q": "Was versteht man unter dem induzierten Widerstand?",
        "options": [
          "Der Widerstand durch Reibung der Luftteilchen an der Oberfläche",
          "Der Widerstand durch die Auftriebserzeugung selbst, verursacht durch Randwirbel an den Flügelspitzen",
          "Der Formwiderstand des Rumpfes",
          "Der Widerstand bei überschallschnellen Flügen"
        ],
        "answer": 1,
        "explanation": "Induzierter Widerstand entsteht als unvermeidbare Nebenwirkung der Auftriebserzeugung: Die Druckdifferenz zwischen Flügeloberseite und -unterseite erzeugt an den Flügelspitzen Randwirbel, die Energie kosten. Er steigt bei niedriger Geschwindigkeit (hohem Auftriebsbedarf) stark an."
      }
    ]
  }
];


// ─── Apply patches after main data loads ───────────────────────
(function applyPatch() {
  if (!window.PPL_DATA) return;

  // 1) Replace agk-instruments with the new pitot-static chapter AND add 3 more AGK chapters
  var agkSubj = window.PPL_DATA.subjects.find(function(s){ return s.id === 'agk'; });
  if (agkSubj) {
    // Find and replace agk-instruments
    var instIdx = agkSubj.chapters.findIndex(function(c){ return c.id === 'agk-instruments'; });
    if (instIdx !== -1) {
      agkSubj.chapters.splice(instIdx, 1, 
        window.NEW_CHAPTERS_AGK[0],   // pitot-static (replaces agk-instruments)
        window.NEW_CHAPTERS_AGK[1],   // kreiselinstrumente
        window.NEW_CHAPTERS_AGK[2],   // triebwerk-instrumente
        window.NEW_CHAPTERS_AGK[3]    // elektronische anzeigen
      );
    } else {
      agkSubj.chapters = agkSubj.chapters.concat(window.NEW_CHAPTERS_AGK);
    }
    // Update agk overview
    agkSubj.overview = "AGK verbindet Triebwerk, Propeller, Systeme und Instrumente. Kapitel 4.1–4.5 behandeln alle Cockpit-Instrumente: vom Pitot-Static-System über Kreiselinstrumente und Triebwerksüberwachung bis hin zu Glass-Cockpit-Systemen (EFIS). Für PPL(A) geht es um funktionales Verständnis: Was macht das System, woran erkennst du Fehler und welche Folgen hat das?";
  }

  // 2) Add new Aerodynamik chapters to principles
  var princSubj = window.PPL_DATA.subjects.find(function(s){ return s.id === 'principles'; });
  if (princSubj) {
    // Prepend the two new aerodynamics foundation chapters
    var liftIdx = princSubj.chapters.findIndex(function(c){ return c.id === 'pof-lift'; });
    if (liftIdx !== -1) {
      princSubj.chapters.splice(liftIdx, 0, 
        window.NEW_CHAPTERS_AERO[0],  // Atmosphäre + Bernoulli
        window.NEW_CHAPTERS_AERO[1]   // Strömung am Tragflügel
      );
    } else {
      princSubj.chapters = window.NEW_CHAPTERS_AERO.concat(princSubj.chapters);
    }
    // Update principles overview
    princSubj.overview = "Aerodynamik erklärt, warum Flugzeuge fliegen. Von der Atmosphäre über Luftwiderstand, Grenzschicht und Bernoulli-Gleichung bis hin zu Auftrieb, Widerstand und Stall. Kapitel basieren auf dem Aircademy Advanced PPL-Guide Band 2 – Aerodynamik. Verständnis ist wichtiger als Formeln: Wer Ursachen und Wirkungen erkennt, löst viele Prüfungsfragen intuitiv.";
  }

  // 3) Update metadata counts
  var totalChapters = 0;
  var totalQuestions = 0;
  window.PPL_DATA.subjects.forEach(function(s) {
    s.chapters.forEach(function(c) {
      totalChapters++;
      if (c.quiz) totalQuestions += c.quiz.length;
    });
  });
  window.PPL_DATA.meta.chapters = totalChapters;
  window.PPL_DATA.meta.questions = totalQuestions;
  window.PPL_DATA.meta.version = '2026.03-instruments-aero-update';

  console.log('[PPL Patch] Applied: ' + totalChapters + ' chapters, ' + totalQuestions + ' questions');
})();
