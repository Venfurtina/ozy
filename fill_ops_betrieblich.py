#!/usr/bin/env python3
"""
fill_ops_betrieblich.py
Füllt die Datenbank mit vollständigem Inhalt für
'Betriebliche Verfahren' (Band 7) basierend auf dem Advanced PPL-Guide.
"""
import sqlite3, json, os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.getenv("DATABASE_PATH", os.path.join(BASE_DIR, "takvim.db"))

SUBJECT_ID = "ops"

# ── Full chapter + section + quiz data ──────────────────────────────────────

CHAPTERS = [
    # ─────────────────────────────────────────────────────────────
    {
        "id": "ops-krit-wetter",
        "title": "1 – Kritische Wetterbedingungen",
        "sort_order": 10,
        "exam_relevant": 1,
        "sections": [
            ("heading", "Kritische Wetterbedingungen", "Sicheres Fliegen trotz schwieriger Wetterlagen"),
            ("text", "Der Sichtflug (VFR) basiert auf der Sicht des Luftfahrzeugführers aus dem Cockpit. Dies gilt für die Einhaltung der Fluglage, die Navigation, die Vermeidung von Zusammenstößen und die rechtzeitige Erkennung von Gefahren. Schlechte Wetterlagen – auch wenn der Flug weitgehend oberhalb einer Wolkendecke stattfindet – müssen in der kritischen Start- und Landephase berücksichtigt werden.", None),
            ("subheading", "1.1 Sicht und Bewölkung", None),
            ("text", "Ungünstige Wetterbedingungen umfassen: unzureichende Sicht, aufliegende Bewölkung, gefrierenden Niederschlag oder Gewitterfronten. Häufig sind diese Situationen absehbar und werden entsprechend vorhergesagt. In Ausnahmefällen kann die Intensität einer Wettererscheinung überraschen.", None),
            ("fact", "Sicherheitsmindesthöhe (§ 6 LuftVO): Über Städten, Menschenansammlungen, Industrieanlagen, Unglücksorten sowie Katastrophengebieten beträgt die Sicherheitsmindesthöhe mindestens 300 m (1000 ft) über dem höchsten Hindernis im Umkreis von 600 m.", None),
            ("text", "Bei geringer Wolkenuntergrenze oder Hochnebel sollte nicht entlang einer Autobahn geflogen werden, weil bei ansteigendem Gelände ein Einflug in die Hochnebeldecke mit Bodenberührung gerechnet werden muss. Empfohlene Sicherheitsmindesthöhe: mindestens 1.200 ft MSL.", None),
            ("fact", "Mindestsichten: Im Luftraum G gelten mindestens 1,5 km Flugsicht für Flächenflugzeuge unterhalb 3.000 ft AGL (unter 140 kt). In Luftraum E (unkontrolliert) ebenfalls 1,5 km. In kontrollierten Lufträumen B, C, D gelten striktere Mindestbedingungen.", None),
            ("subheading", "Auffanglinien und Navigation in niedrigem Gelände", None),
            ("text", "Sind zuverlässige Leitlinien entlang der Flugstrecke vorhanden, erleichtert dies die Orientierung ungemein. Bei kritischen Wetterverhältnissen kann es sinnvoll sein, Umwege in Kauf zu nehmen und sich anhand von Leitlinien zu bewegen. Auffanglinien: großer Fluss, Autobahn, Eisenbahnlinie quer zur Flugrichtung.", None),
            ("warning", "Beim Durchflug einer Warmfront kommt es zu starkem Sichtrückgang mit Unterschreiten der Sichtflugmindestbedingungen. Sofortiger Umkehrflug oder Landung erforderlich.", None),
            ("subheading", "1.2 Schnee und Eis", None),
            ("text", "Der mitteleuropäische Winter beeinflusst die Sichtflugmöglichkeiten erheblich. Bei der Durchführung sind sicherheitsrelevante Faktoren wie Schnee und Eis zu beachten, die im Sommerhalbjahr nicht auftreten. Im Winterhalbjahr ist bei Eisansatz durch Masse und aerodynamische Eigenschaften die kritischste Faktor.", None),
            ("fact", "Kontaminierung am Boden: Vor dem Start müssen nasser Schnee und Raureif vollständig entfernt und Scharniere, Gelenke und Ruder getrocknet werden. Bei einer dünnen Schneeschicht müssen mindestens die Trag- und Rudeflächen vor dem Start gereinigt werden, damit die Strömungsverhältnisse an den Tragflächen nicht behindert werden.", None),
            ("text", "Wird mit einer mit Schnee bedeckten Piste gestartet, kann aufgewirbelter Schnee zunächst die Sicht behindern. Auch beim Abfangen des Luftfahrzeuges müssen die beweglichen Merkmale eventuell nicht sichtbar sein. Kontaminierte Pisten: Eine Piste gilt als kontaminiert, wenn mehr als 25% ihrer Oberfläche mit mehr als 3 mm Wasser, Schnee oder Eis bedeckt ist.", None),
            ("fact", "Vereisung im Flug: Vereisen während des Fluges die Frontscheiben → Kabinenheizung einschalten und in wärmere Flughöhen einsteigen. Bei Klareisansatz nimmt der Auftriebsbeiwert ab, der Widerstandsbeiwert hingegen zu → Anfluggeschwindigkeit erhöhen.", None),
            ("text", "§ 35 LuftBO: Ein Flug unter Wetterbedingungen, bei denen Vereisung zu erwarten ist, darf nur dann angetreten oder zum Ausweichflugplatz fortgesetzt werden, wenn das Luftfahrzeug mit betriebsbereiten Einrichtungen zur Verhütung oder zur Beobachtung und Beseitigung von Eisansatz ausgerüstet ist.", None),
            ("subheading", "1.3 Gewitter", None),
            ("text", "Gewitter entwickeln sich bevorzugt durch die Hebung feuchter Luft in labiler Schichtung. Sie sind auch durch meteorologische Vorhersagen nicht immer einfach zu bestimmen. Die Grundregel im Umgang mit Gewittern lautet: VERMEIDEN! Gewitter sollten großräumig umflogen werden; keinesfalls sollte während eines Gewitters ein Landeversuch unternommen werden.", None),
            ("fact", "Gefahren eines Gewitters: Turbulenz und Böen (größte Gefahr), vertikale Luftströmungen bis 30 m/s, Hagel (Schäden an Luftfahrzeugen), Sichtrückgang durch starken Niederschlag, Blitz (Schäden am elektrischen System, Magnetkompass), variable Windrichtung und -stärke.", None),
            ("text", "Besonders gefährlich sind eingelagerte Gewitter, da sie von anderer Bewölkung umschlossen sind und mit dem bloßen Auge nicht erkannt werden können. Hierfür wäre ein Wetterradar notwendig. Im Hagelschauer: Vergaservorwärmung einschalten, Geschwindigkeit reduzieren, Schauer schnellstmöglich verlassen.", None),
            ("infobox", "Blitz und Faradayscher Käfig: Ein Flugzeug ist ein sogenannter Faradayscher Käfig. Es kann zwar von einem Blitz getroffen werden, aber die Insassen sind vor der elektrischen Entladung geschützt, da auf der Außenhaut des Faradayschen Käfigs ein Ladungsausgleich stattfindet. Das elektrische System kann dennoch versagen.", "Blitzschutz im Flugzeug"),
            ("subheading", "1.4 Orientierungsverlust und Dunkelheit", None),
            ("text", "Eine unbedingte Einhaltung der Sicherheitsmindesthöhe ist äußerst wichtig. Sofort nach dem Bemerken der Orientierungslosigkeit ist die Sicherheitsmindesthöhe ggf. auf einen breiteren Korridor auszudehnen und entsprechend anzupassen. Der Pilot sollte versuchen, die Orientierung anhand der nächsten Auffanglinie wiederzufinden.", None),
            ("fact", "Bei einer Landung in Dunkelheit ist das Einschätzen der Abfanghöhe deutlich schwieriger als bei Tag. Im Normalfall empfiehlt sich daher, mit einer noch vorhandenen geringen Sinkrate aufzusetzen, statt eine eigentlich perfekte Einschätzung zu versuchen.", None),
            ("text", "Für nach Sichtflugregeln operierende Luftfahrzeugführer ist die Kenntnis der Sonnenuntergangszeit von elementarer Bedeutung. Oft werden die lokalen Sonnenauf- und Sonnenuntergangszeiten an den Flugplätzen ausgehängt. Im AIP VFR im Teil GEN 2 findet sich eine Tabelle, aus der die Zeiten abgelesen werden können.", None),
        ],
        "quiz": [
            {
                "q": "Darf durch eine dünne Wolkenschicht geflogen werden, um am Zielflugplatz zu landen?",
                "opts": ["Ja", "Nein", "Nur, wenn die Wolkendicke 1.000 ft nicht überschreitet", "Nur bei Funkkontakt zum Zielflugplatz"],
                "answer": 1,
                "explanation": "Ein Sichtflug in oder durch Wolken ist verboten. Sichtflugregeln erfordern, dass der Pilot stets Sicht nach außen hat.",
                "is_official": 1
            },
            {
                "q": "Muss bei einem VFR-Flug ein Ausweichflugplatz berücksichtigt werden?",
                "opts": ["Nein, dies ist optional", "Ja, immer", "Nur bei Streckenflügen über 100 NM", "Nur bei Nachtflügen"],
                "answer": 1,
                "explanation": "Die Möglichkeit einer Landung auf dem Ausgangsflugplatz oder einem gerade überflogenen Platz sollte stets in Betracht gezogen werden.",
                "is_official": 0
            },
            {
                "q": "Was ist die größte Gefahr beim Einflug in Schneefallbedingungen?",
                "opts": ["Erhöhter Kraftstoffverbrauch", "Der plötzliche Sichtrückgang", "Gewitterneigung", "Nebelbildung"],
                "answer": 1,
                "explanation": "Der plötzliche Sichtrückgang ist die größte Gefahr beim Einflug in Schneefall.",
                "is_official": 1
            },
            {
                "q": "Welche Maßnahmen können beim Einflug in Vereisungsbedingungen eingeleitet werden?",
                "opts": ["Steigflug in wärmere Schichten, Richtungsänderung, Landung", "Nur Steigflug ist erlaubt", "Nur Richtungsänderung", "Nichts – man muss durchfliegen"],
                "answer": 0,
                "explanation": "Beim Einflug in Vereisung: Vereisungszone verlassen durch Höhenänderung oder Kursänderung, und wenn nötig landen.",
                "is_official": 1
            },
            {
                "q": "Muss vor dem Start der Schnee vollständig entfernt werden?",
                "opts": ["Ja", "Dies ist nur bei anhaltendem Schneefall notwendig", "Ja, bei einer dünnen Schneeschicht sind Tragflächen, Frontscheiben und bewegliche Teile ausreichend", "Dies liegt im Ermessen des Flugführers"],
                "answer": 0,
                "explanation": "Vor dem Start müssen nasser Schnee und Raureif vollständig entfernt werden. Bereits eine dünne Eisschicht kann die aerodynamischen Eigenschaften des Flugzeuges erheblich beeinflussen.",
                "is_official": 1
            },
            {
                "q": "Welche Gefahren für Sichtflieger können bei Gewittern auftreten?",
                "opts": ["Nur Turbulenzen", "Nur schlechte Sicht", "Turbulenzen, Hagel, Blitz, Vereisung, Sichtrückgang, Böen", "Ausschließlich Blitz"],
                "answer": 2,
                "explanation": "Gewitter bringen eine Vielzahl von Gefahren: Turbulenzen, Hagel, Blitz, Vereisung, starken Niederschlag und Böen.",
                "is_official": 0
            },
            {
                "q": "Was eignet sich als Auffanglinie bei Orientierungsverlust?",
                "opts": ["Eine Autobahn quer zur Flugrichtung im Ruhrgebiet", "Ein Kanal längs zur Flugrichtung", "Ein großer Fluss quer zur Flugrichtung", "Eine Eisenbahnlinie, welche die Flugroute streift"],
                "answer": 2,
                "explanation": "Eine Auffanglinie muss quer zur Flugrichtung verlaufen und eindeutig erkennbar sein. Große Flüsse eignen sich ideal.",
                "is_official": 1
            },
            {
                "q": "Wo können die Sonnenauf- und Sonnenuntergangszeiten eingesehen werden?",
                "opts": ["AIP VFR Teil GEN", "AIP VFR Teil ENR", "AIP VFR Teil AD", "Bordbuch"],
                "answer": 0,
                "explanation": "Im AIP VFR im Teil GEN 2 findet sich eine Tabelle mit den Sonnenauf- und Sonnenuntergangszeiten.",
                "is_official": 1
            },
            {
                "q": "Kann ein Gewitter problemlos unterflogen werden?",
                "opts": ["Ja, wenn man unterhalb der Wolkenbasis bleibt", "Nein, nie", "Ja, wenn der Motor eine ausreichende Leistung hat", "Ja, wenn man Radar hat"],
                "answer": 1,
                "explanation": "Das Unterfliegen eines Gewitters ist wegen der starken vertikalen Luftströmungen und Böen unterhalb der Gewitterwolke äußerst gefährlich und sollte nie durchgeführt werden.",
                "is_official": 0
            },
            {
                "q": "Welche Folgen kann eine Temperatur nahe des Taupunktes haben?",
                "opts": ["Schneefall", "Eisbildung", "Gewitterneigung", "Nebelbildung"],
                "answer": 3,
                "explanation": "Bei Temperaturen nahe des Taupunktes ist mit Nebelbildung zu rechnen, was die Sicht erheblich beeinträchtigen kann.",
                "is_official": 1
            },
        ]
    },
    # ─────────────────────────────────────────────────────────────
    {
        "id": "ops-feuer-rauch",
        "title": "2 – Feuer und Rauch",
        "sort_order": 20,
        "exam_relevant": 1,
        "sections": [
            ("heading", "Feuer und Rauch", "Brandbekämpfung und Notfallverfahren an Bord"),
            ("text", "Feuer an Bord eines Luftfahrzeuges gehört zu den gefährlichsten und zeitkritischsten Situationen im Flugverkehr. Es besteht unmittelbarer Handlungsbedarf, wobei zwei mögliche Fälle betrachtet werden können: Der Brand kann entweder noch im Flug unmittelbar bekämpft werden oder den wesentlichen Teil der Löscharbeiten übernehmen nach einer zügigen Landung Fachkräfte am Boden.", None),
            ("text", "Beabsichtigte Feuer an Bord eines Luftfahrzeuges finden in den dafür vorgesehenen Verbrennungsräumen der Triebwerke statt. Das Übergreifen dieses Feuers auf andere Flugzeugteile muss unbedingt verhindert werden.", None),
            ("subheading", "2.1 Brandbekämpfung – Löschmittel", None),
            ("text", "Feuer benötigt zum Brennen ein Brennmaterial (Nahrung), Hitze und Sauerstoff. Die effektivste Methode zur Feuerbekämpfung ist der Entzug eines dieser drei Elemente. Das Löschmittel der Wahl in Flugzeugen ist in den meisten Fällen Halon.", None),
            ("table_row", "Wasser (evtl. mit Zusätzen)", "Hauptlöschwirkung: Kühlen · Nebenlöschwirkung: Ersticken"),
            ("table_row", "Löschschaum (Wasser-Schaummittel-Luft)", "Hauptlöschwirkung: Ersticken durch Auflegen einer Trennschicht · Nebenwirkung: Kühlen"),
            ("table_row", "Kohlenstoffdioxid (CO₂)", "Hauptlöschwirkung: Ersticken · CO₂ wirkt als ATEMGIFT auf das Atemzentrum des Menschen"),
            ("table_row", "Stickstoff", "Hauptlöschwirkung: Ersticken · Bei hohen Konzentrationen kann es zu Sauerstoffmangel kommen"),
            ("table_row", "Löschpulver", "Haupt: Ersticken und chemische Störung des Verbrennungsvorganges · Neben: keine"),
            ("table_row", "Halon (halogenisierte Kohlenwasserstoffe)", "Haupt: Chemische Störung des Verbrennungsvorganges · Neben: keine – wird aber heute kaum noch eingesetzt"),
            ("fact", "Wasser ist zum Löschen eines Luftfahrzeugbrandes am wenigsten geeignet. Halon sind gesundheitsgefährdend, werden aufgrund ihrer Eigenschaften aber an Bord von Luftfahrzeugen verwendet.", None),
            ("subheading", "Brandklassen", None),
            ("text", "In Abhängigkeit von der Beschaffenheit des Materials werden fünf Brandklassen unterschieden. Die Kenntnis einer Brandklasse ermöglicht den richtigen Einsatz von Löschmitteln.", None),
            ("table_row", "Klasse A – Feststoffbrände", "Holz, Papier, Textilien, Flugzeugreifen und Kunststoffe · Löschmittel: Wasser oder wässrige Lösungen bevorzugt"),
            ("table_row", "Klasse B – Flüssigkeitsbrände", "Benzin, Alkohol, Lacke, Harze, viele Kunststoffe · Löschmittel: Schaum, Pulver oder CO₂ (kein Wasser!)"),
            ("table_row", "Klasse C – Gasbrände", "Alle Brände von Gasen · Gasbrände erst löschen, nachdem die Gaszufuhr unterbrochen wurde"),
            ("table_row", "Klasse D – Metallbrände", "Aluminium, Magnesium, Natrium, Kalium, Lithium · spezielles Metallbrandpulver erforderlich"),
            ("table_row", "Klasse F – Speiseölbrände", "Speiseöle und Fette · Fettbrände NIEMALS mit Wasser löschen!"),
            ("fact", "Brandklasse E gibt es nicht mehr. Sie bezeichnete zuvor Brände an elektrischen Niederspannungsanlagen bis 1.000 Volt.", None),
            ("subheading", "2.1.3 Feuerlöscher", None),
            ("text", "Bei der Verwendung von Feuerlöschern jeglicher Art ist zunächst sicherzustellen, dass keine Personen gefährdet werden. Der Feuerlöscher darf erst direkt am Brandherd und nicht bereits vorher betätigt werden. Stehen mehrere Feuerlöscher zur Verfügung, sollten diese gleichzeitig und nicht nacheinander eingesetzt werden.", None),
            ("fact", "Feuerlöscher sind möglichst zusammen und in mehreren Schüben auf den Brandherd zu richten. Außenbrände müssen von außen ausgehend gelöscht werden – die Löschung erfolgt immer mit dem Wind.", None),
            ("subheading", "2.2 Motor und Bremsen", None),
            ("text", "Rauchentwicklung und Brände können grundsätzlich in allen Bereichen und an allen Teilen eines Luftfahrzeuges auftreten. Die ersten Handgriffe für akute Notfälle müssen unbedingt auswendig bekannt und direkt umgesetzt werden.", None),
            ("subheading", "Vergaserbrand", None),
            ("text", "Der Vergaserbrand ist eine Situation, die ausschließlich bei Flugzeugen mit Kolbentriebwerken auftritt. Er entsteht bevorzugt beim Anlassen eines Triebwerkes, wenn sich zu viel Kraftstoff im Zylinder entzündet. Dies führt zu einer Flammenfront, die durch das Einlassventil und Ansaugrohr in den Vergaser zurückschlägt und den dort befindlichen Treibstoff entzündet.", None),
            ("fact", "Vergaserbrand-Maßnahme: Ein zu starkes 'Pumpen' mit dem Gashebel sollte aus diesem Grund vermieden werden. Das genaue Vorgehen bei einem Vergaserbrand wird in jedem Flughandbuch im Kapitel Notverfahren beschrieben. In jedem Fall sollte beim Anlassen eines Feuerlöschers verfügbar sein.", None),
            ("subheading", "Triebwerksbrand", None),
            ("text", "Im Gegensatz zum Vergaserbrand kann ein Triebwerksbrand auch während des Fluges auftreten. Die Löschmöglichkeiten sind bei Flugzeugen der Allgemeinen Luftfahrt sehr begrenzt, sodass eine sofortige Landung in den meisten Fällen die beste Möglichkeit darstellt.", None),
            ("fact", "Bei Triebwerksbrand: Bereits wenn der Verdacht eines Brandes während des Fluges aufkommt, sollte umgehend nach einem geeigneten Notlandefeld Ausschau gehalten werden. Anschließend muss die Flugsicherung informiert werden. Bei Feuer oder Rauch an Bord Luftnotlage ('MAYDAY – MAYDAY – MAYDAY') erklären.", None),
            ("subheading", "2.2.3 Überhitzte Bremsen", None),
            ("text", "Luftfahrzeuge werden üblicherweise mittels Scheibenbremsen am Hauptfahrwerk abgebremst. Dabei besteht die Möglichkeit, das rechte und das linke Rad getrennt voneinander abzubremsen. Bei extrem hohen Belastungen oder Dauerbelastungen kann es jedoch schnell zum Überhitzen der Bremsen und zu Brandgefahr kommen.", None),
            ("fact", "Flugzeugbremsen sind nicht für die dauerhafte Benutzung ausgelegt, sondern lediglich zum einmaligen Abbremsen eines Flugzeuges im Falle eines Startabbruches, nach der Landung und zum Kontrollieren der Rollgeschwindigkeit. Stahlbremsen sind anfällig für Überhitzung.", None),
            ("text", "Sind die Bremsen tatsächlich sehr heiß geworden, sollte die Parkbremse nur in absolut unerlässlichen Fällen gesetzt werden, da die Bremsen festbacken können. Alternativ kann das Flugzeug durch Bremsklötze oder Seile (Tie Downs) gegen ein Wegrollen gesichert werden.", None),
            ("subheading", "2.3 Cockpit und Elektrik", None),
            ("text", "Einer der sensibelsten Orte an Bord eines Luftfahrzeuges ist zweifelsohne das Cockpit, wo alle Fäden zusammenlaufen und die gesamte Technik gesteuert und kontrolliert wird. Rauch oder Feuer im Cockpit kann nicht nur gravierende Auswirkungen auf die technischen Anlagen haben, sondern auch auf die Besatzung.", None),
            ("subheading", "Feuer oder Rauch im Cockpit", None),
            ("text", "Die Ursachen für Feuer oder Rauch im Flugzeugrumpf können ganz unterschiedlich sein. Der durch einen Brand des Triebwerkes verursachte Rauch kann beispielsweise über die Heizungs- oder Lüftungsanlage in die Kabine gelangen und gefährliches Kohlenmonoxid freisetzen. Manche Flugzeugmuster verwenden zudem für die Kabinenheizung statt eines triebwerksgebundenen Wärmetauschers einen Verbrennungsofen im Rumpf, der als Brandquelle in Frage kommt.", None),
            ("fact", "Sofortmaßnahmen bei Feuer/Rauch: Ist die Ursache des Feuers nicht auf den ersten Blick klar erkennbar, sollte zunächst ein geeignetes Landefeld gesucht werden. Als weitere Maßnahme ist bei jedem Feuer das Ausschalten des Hauptschalters angebracht. Wenn möglich, Notruf absetzen und Flugzeug landen.", None),
            ("subheading", "2.3.2 Elektrische Anlage", None),
            ("text", "Auch wenn ein Brand in der elektrischen Anlage zunächst nicht direkt zum Ausfall des Triebwerks führt, kann er die Sicherheit in hohem Maße beeinflussen. In den meisten Fällen sind Probleme an der elektrischen Anlage durch ein Auslösen der Sicherungen zu erkennen. In diesem Fall ist es äußerst wichtig, dass die Sicherung vorsichtig sein und eine Sicherung nicht unbegrenzt oft zurückgesetzt werden.", None),
            ("fact", "Flugzeuge der Allgemeinen Luftfahrt werden meist Gleichspannungsstromnetze mit einer Betriebsspannung von 12 oder 24 Volt verwendet, die vorübergehend durch eine Batterie oder im Normalbetrieb durch einen motorgetriebenen Generator erzeugt wird.", None),
            ("text", "Sind Anzeichen für einen Brand in der elektrischen Anlage oder zu ihr gehörigen Kabeln erkennbar, sollte zunächst ein Notruf abgesetzt und anschließend das komplette System durch den Hauptschalter stromlos geschaltet werden. Der Zündkreislauf über eine separate Stromquelle hat dies in der Regel keine Auswirkung auf den Motorlauf.", None),
        ],
        "quiz": [
            {
                "q": "Kann Vergaserbrand bei allen Flugzeugtypen auftreten?",
                "opts": ["Nur bei Flugzeugen mit Kolbentriebwerken", "Ja", "Nur bei Flugzeugen mit mehr als einem Triebwerk", "Dies tritt nur bei Hubschraubern auf"],
                "answer": 0,
                "explanation": "Vergaserbrand tritt ausschließlich bei Flugzeugen mit Kolbentriebwerken auf – er entsteht wenn sich zu viel Kraftstoff im Vergaser entzündet.",
                "is_official": 1
            },
            {
                "q": "Wodurch entsteht ein Vergaserbrand?",
                "opts": ["Durch zu wenig Kraftstoff", "Durch zu viel Kraftstoff im Zylinder und Zurückschlagen ins Ansaugsystem", "Durch Überhitzung des Propellers", "Durch statische Entladung"],
                "answer": 1,
                "explanation": "Vergaserbrand entsteht wenn sich zu viel Kraftstoff im Zylinder entzündet und eine Flammenfront durch das Einlassventil in den Vergaser zurückschlägt.",
                "is_official": 0
            },
            {
                "q": "Wo ist das Verfahren bei Vergaserbrand beschrieben?",
                "opts": ["Im Flugbuch", "Im Bordbuch", "In den Betriebsanweisungen des LBAs", "Im Flughandbuch des Herstellers"],
                "answer": 3,
                "explanation": "Das genaue Vorgehen bei einem Vergaserbrand wird in jedem Flughandbuch im Kapitel Notverfahren beschrieben.",
                "is_official": 1
            },
            {
                "q": "Was ist bei einem Triebwerksbrand während des Fluges mit einem einmotorigen Sportflugzeug zu tun?",
                "opts": ["Weiterfliegen und Feuerwehr am Zielort informieren", "Sofortige Landung auf dem nächstgelegenen geeigneten Gelände", "Auf größere Höhe steigen", "Motor abstellen und als Segelflugzeug weiterfliegen"],
                "answer": 1,
                "explanation": "Bei Triebwerksbrand ist eine sofortige Landung die beste Möglichkeit, da die Löschmöglichkeiten in der Allgemeinen Luftfahrt sehr begrenzt sind.",
                "is_official": 1
            },
            {
                "q": "Was ist zu beachten, wenn Rauch in Cockpit oder Kabine eindringt?",
                "opts": ["Nichts – Rauch ist harmlos", "Notruf absetzen, geeignetes Landefeld suchen, landen", "Höhe erhöhen um Rauch loszuwerden", "Fenster öffnen und weiterflegen"],
                "answer": 1,
                "explanation": "Bei Rauch im Cockpit: Notruf absetzen, geeignetes Landefeld suchen, und schnellstmöglich landen. Frischluft für Insassen sicherstellen.",
                "is_official": 0
            },
            {
                "q": "Was ist ein erstes Indiz für Probleme mit der elektrischen Anlage?",
                "opts": ["Knistern im Funk", "Nebelschwaden im Cockpit", "Auslösen von Sicherungen", "Unrunder Motorlauf"],
                "answer": 2,
                "explanation": "Das Auslösen von Sicherungen ist in den meisten Fällen das erste Anzeichen für Probleme an der elektrischen Anlage.",
                "is_official": 1
            },
            {
                "q": "Wie viele Sekunden löscht ein Feuerlöscher etwa?",
                "opts": ["3 Sekunden", "6 Sekunden", "12 Sekunden", "30 Sekunden"],
                "answer": 1,
                "explanation": "Die Kapazität eines Handfeuerlöschers ist begrenzt – eine handelsübliche Variante mit sechs Kilogramm Löschmittel löscht für etwa sechs Sekunden.",
                "is_official": 1
            },
            {
                "q": "Wie sollten mehrere Feuerlöscher zum Löschen verwendet werden?",
                "opts": ["Nacheinander", "Maximal zwei Feuerlöscher gleichzeitig", "Alle Feuerlöscher gleichzeitig", "Das spielt keine Rolle"],
                "answer": 2,
                "explanation": "Stehen mehrere Feuerlöscher zur Verfügung, sollten diese gleichzeitig und nicht nacheinander eingesetzt werden, um eine maximale Löschwirkung zu erzielen.",
                "is_official": 1
            },
            {
                "q": "In welche Brandklasse fallen Flugzeugreifen?",
                "opts": ["Klasse A", "Klasse B", "Klasse C", "Klasse D"],
                "answer": 0,
                "explanation": "Flugzeugreifen fallen in Brandklasse A (Feststoffbrände), zusammen mit Holz, Papier, Textilien und einigen Kunststoffen.",
                "is_official": 0
            },
            {
                "q": "Was ist bei brennenden Felgen zu beachten?",
                "opts": ["Sofort löschen mit viel Wasser", "Abstand halten, Bremsen kühlen lassen", "Parkbremse sofort anziehen", "Fahrwerk einfahren"],
                "answer": 1,
                "explanation": "Bei überhitzten Bremsen muss Abstand von den Felgen gehalten werden. Nie mit Wasser kühlen (Risiko: Platzen der Felgen). Abstand seitlich der Räder halten.",
                "is_official": 0
            },
            {
                "q": "Welches freigesetzte Gas bei einem Triebwerksbrand ist besonders gefährlich?",
                "opts": ["Sauerstoff", "Kohlenmonoxid", "Schwefel", "Kohlendioxid"],
                "answer": 1,
                "explanation": "Kohlenmonoxid (CO) ist besonders gefährlich, da es geruchs- und farblos ist und die Sauerstoffbindung im Blut blockiert.",
                "is_official": 1
            },
            {
                "q": "Eine Sicherung löst zum dritten Mal während eines Fluges aus. Was ist ratsam?",
                "opts": ["Der Flug muss unterbrochen und auf dem nächsten Flugplatz gelandet werden", "Wenn möglich ist auf den Verbraucher zu verzichten und nach dem Flug ein Wartungsbetrieb zu konsultieren", "Die Sicherung kann bis zu fünf Mal pro Flug bedenkenlos reaktiviert werden", "Sofern keine weiteren Anzeichen für einen Defekt bestehen, ist die Sicherung bedenkenlos wieder zu aktivieren"],
                "answer": 1,
                "explanation": "Wenn eine Sicherung wiederholt auslöst, deutet dies auf ein ernstes Problem hin. Verzicht auf den betreffenden Verbraucher und nach der Landung Wartung.",
                "is_official": 1
            },
            {
                "q": "Welche Bordspannung haben elektrische Systeme von Kleinflugzeugen meist?",
                "opts": ["6 V", "12 V oder 24 V", "36 V", "110 V"],
                "answer": 1,
                "explanation": "Flugzeuge der Allgemeinen Luftfahrt verwenden meist Gleichspannungsstromnetze mit 12 oder 24 Volt.",
                "is_official": 1
            },
            {
                "q": "Was ist bei einem Kabelbrand während des Fluges nach dem Flughandbuch zu tun?",
                "opts": ["Weiterfliegen bis zum nächsten Flugplatz", "Hauptschalter ausschalten und nach Flughandbuch verfahren", "Nur den betroffenen Schalter ausschalten", "Sofort alle Triebwerke abstellen"],
                "answer": 1,
                "explanation": "Bei einem Kabelbrand während des Fluges ist der Hauptschalter auszuschalten und nach Flughandbuch zu verfahren.",
                "is_official": 0
            },
        ]
    },
    # ─────────────────────────────────────────────────────────────
    {
        "id": "ops-gefahren-boden",
        "title": "3 – Gefahren in Bodennähe",
        "sort_order": 30,
        "exam_relevant": 1,
        "sections": [
            ("heading", "Gefahren in Bodennähe", "Sichere Start- und Landephasen"),
            ("text", "Um den sicheren Start eines Luftfahrzeuges zu gewährleisten, müssen verschiedene Faktoren wie der Zustand und die Neigung der Startbahn, die Wetterbedingungen, die Umgebung des Startflugplatzes, die Masse, die Schwerpunktlage, der äußere Zustand des Flugzeuges, die Leistungsabgabe des Triebwerks, die Druckhöhe, die Temperatur und die Flugtechnik des Piloten als Einflussfaktoren berücksichtigt werden.", None),
            ("subheading", "3.1 Pistenzustand", None),
            ("text", "Einen großen Einfluss auf den Start und die Landung hat der Zustand der Piste, welcher in Abhängigkeit von den äußeren Bedingungen stark variieren kann. Hoher Bewuchs kann stark auf den Rollwiderstand, die Richtungsstabilität und auf die Struktur des Luftfahrzeuges auswirken.", None),
            ("subheading", "Bewuchs und Untergrund", None),
            ("text", "Um den Einfluss einer kurzen trockenen Grasbahn auf die Startrollstrecke abzuschätzen, kann die Kraftaufwand des Fahrradfahrens als Vergleich herangezogen werden. Auf einer asphaltierten Straße ist dieser deutlich geringer als auf einer Wiese, auch wenn diese trocken und gemäht ist.", None),
            ("fact", "Hoher Grasbewuchs erhöht die Unfallgefahr erheblich! Bewuchs länger als 5 cm oder Grasnabe beschädigt → Startrollstrecke verlängert sich um ca. 20 Prozent. Ist der Bewuchs länger als ca. acht Zentimeter, sind Graslängen von ungefähr acht Zentimetern anzusehen.", None),
            ("subheading", "Neigung und Kontaminierung", None),
            ("text", "Auch bei Pisten mit Hartbelag kann es in Folge diverser Einflussfaktoren zu erheblicher Einwirkung auf die Leistungsberechnungen kommen. Bei einer kontaminierten Start- oder Landebahn sind wenigstens 25 Prozent der Oberfläche mit einer drei Millimeter tiefen Wasserschicht oder Schnee oder einer vergleichbaren Tiefe bedeckt.", None),
            ("fact", "Feuchtes Gras reduziert die Bodenhaftung und gibt dem Flugzeuggewicht nach. Nasses Gras verlängert die angenommene Startrollstrecke für eine feuchte Grasbahn um etwa zehn Prozent. Stehendes Wasser erhöht den Rollwiderstand um rund 30 Prozent.", None),
            ("text", "Fällt die Piste in Startrichtung ab oder steigt sie in Landerichtung an, verkürzen sich Start- bzw. Landestrecke. Einige Flugplätze haben ein starkes Gefälle, dass ungeachtet der vorherrschenden Windrichtung immer bergab gestartet und bergauf gelandet wird.", None),
            ("subheading", "3.1.3 Start und Landung", None),
            ("text", "Der verantwortliche Luftfahrzeugführer hat sich vor jedem Start und jeder Landung über die Beschaffenheit der Piste zu informieren und die Start- und Landetechniken anwenden, die eventuelle negative Faktoren ausgleichen können.", None),
            ("fact", "Starttechniken: Auf einer nassen und kurzen Graspiste sollte mit voll ausgefahrenen Landeklappen und geringer Fahrt aufgesetzt werden. Beim Kurzstart sind die Klappen in Startstellung und der Motor auf Startleistung zu bringen, dann die Bremsen lösen, das Bugrad entlasten und mit der Mindestgeschwindigkeit nahe an Bodennähe die sichere Steiglinie erreichen.", None),
            ("subheading", "3.2 Meteorologische Einflüsse", None),
            ("text", "Die Flugbedingungen können durch Wettererscheinungen wesentlich beeinflusst werden und verlangen vom Luftfahrzeugführer besondere Aufmerksamkeit. Selbst wenn der Flug weitgehend oberhalb einer Wolkendecke durchgeführt werden konnte, muss sich der Pilot in den kritischen Start- und Landephasen in jedem Fall mit dem Wetter auseinandersetzen.", None),
            ("subheading", "3.2.1 Wind", None),
            ("text", "Der Wind hat einen besonderen Einfluss auf Start und Landung, weil er durch seine großen Kräfte die Stabilität des An- und Abfluges in hohem Maße beeinträchtigen kann. Er kommt im Idealfall bei Start und Landung von vorne, um bei ausreichend hoher Fluggeschwindigkeit die Geschwindigkeit über Grund zu reduzieren, und im Reiseflug von hinten, um die benötigte Flugzeit zum Ziel zu verkürzen.", None),
            ("fact", "Böigkeit (Gusts): Böigkeit führt zu deutlichen Fahrschwankungen und stellt eine der größten Gefahren im Anflug dar. Als Maßnahme: Zielgeschwindigkeit im Landeanflug (v_lof) erhöhen, also die Referenzgeschwindigkeit (v_ref) oder der Hälfte der konstanten Gegenwindkomponente. Der Aufschlag sollte nicht unbegrenzt hoch ausfallen.", None),
            ("text", "Formel anteilige Gegenwindkomponente: HWC [kt] = cos(WW) × WV [kt]. Formel Seitenwindkomponente: CWC [kt] = sin(WW) × WV [kt].", None),
            ("subheading", "3.2.2 Windscherung", None),
            ("text", "Als Windscherung wird eine sprunghafte Änderung der Windrichtung und/oder Windstärke innerhalb einer kurzen horizontalen und/oder vertikalen Entfernung bezeichnet. Diese kann beispielsweise an Inversionsflächen, im Umfeld von Fronten und in der Nähe von Gewittern durch die Böenwalze entstehen.", None),
            ("fact", "Bei Windscherung im Anflug: Die Flugzeugführerin ist versucht, die Triebwerksleistung zu reduzieren, um die Geschwindigkeit und den Gleitweg unter Kontrolle zu halten. Diese Form der 'positiven' Windscherung wurde im Englischen früher als positive windshear bezeichnet. Nimmt die Gegenwindkomponente plötzlich ab → Gefährlicher Sinkflug möglich!", None),
            ("subheading", "3.2.3 Turbulenz", None),
            ("text", "Turbulenz ist die räumlich und zeitlich ungeordnete Strömung eines Gases oder einer Flüssigkeit. An dieser Stelle wird die Turbulenz der Luft betrachtet: Thermische Turbulenz entsteht durch konvektive Luftbewegung, mechanische Turbulenz durch Strömungshindernisse in bodennahen Luftschichten und frontale Turbulenz an Luftmassengrenzen.", None),
            ("table_row", "Leichte Turbulenz", "Verursacht geringe Änderungen in Höhe und/oder Fluglage"),
            ("table_row", "Mäßige Turbulenz", "Führt zu größeren Änderungen in Höhe und/oder Fluglage – Flugzeug jedoch zu allen Zeiten unter Kontrolle"),
            ("table_row", "Starke Turbulenz", "Bedingt abrupte Änderungen in Höhe und/oder Fluglage – kurzzeitig außer Kontrolle gerät"),
            ("table_row", "Extreme Turbulenz", "Wirft das Flugzeug unkontrolliert umher – Kontrolle über Höhe und Fluglage nicht möglich"),
            ("subheading", "Wirbelschleppen", None),
            ("text", "Wirbelschleppen entstehen durch einen Ausgleich des Überdruckes an der Tragflächenunterseite mit dem Unterdruck an der Tragflächenoberseite des Flugzeuges und äußern sich als Wirbel, die sich vom Randbogen lösen. Die Intensität von Wirbelschleppen ist abhängig von Masse und Auftriebsverteilung.", None),
            ("fact", "Der gefährdete Bereich ist etwa drei Minuten hinter und 1.000 ft unter einem Flugzeug der Wirbelschleppenkategorien MEDIUM und HEAVY. Am stärksten ausgeprägt sind Wirbelschleppen bei einem schweren, langsam fliegenden Flugzeug mit geringer Landeklappenstellung.", None),
            ("table_row", "L (leicht)", "Maximale Startmasse: weniger als 7.000 kg"),
            ("table_row", "M (mittel)", "Maximale Startmasse: zwischen 7.000 und 136.000 kg"),
            ("table_row", "H (schwer)", "Maximale Startmasse: 136.000 kg und mehr"),
            ("table_row", "J (super)", "Derzeit nur für Airbus A380"),
            ("subheading", "3.3 Verkehrssituationen und Flugplatzverkehr", None),
            ("text", "Die Grundlage des Sichtfluges ist die Sicht des Luftfahrzeugführers aus dem Cockpit. Dies gilt für das Halten der Fluglage, die Navigation, die Vermeidung von Zusammenstößen mit Wolken, Hindernissen und anderen Luftverkehrsteilnehmern sowie das rechtzeitige Erkennen von Gefahren.", None),
            ("subheading", "Verkehrsregeln und Ausweichregeln", None),
            ("text", "Grundsätzlich hat der Luftverkehrsteilnehmer mit einer größeren Manövrierfähigkeit demjenigen mit einer geringeren auszuweichen. Während ein Motorflugzeug frei in alle Richtungen bewegt werden kann, verliert ein Segelflugzeug bei jeder Vorwärtsbewegung Höhe.", None),
            ("fact", "§ 12 LuftVO: Der Luftfahrzeugführer hat zur Vermeidung von Zusammenstößen zu Luftfahrzeugen sowie anderen Fahrzeugen und sonstigen Hindernissen einen ausreichenden Abstand einzuhalten. Im Fluge ist außerdem ein Mindestabstand von 150 m einzuhalten; § 6 Abs. 1 bleibt unberührt.", None),
            ("subheading", "3.3.3 Vogelschlag", None),
            ("text", "Durch einen Vogelschlag kann ein Luftfahrzeug nicht nur leicht beschädigt, sondern im schlimmsten Fall flugunfähig werden. Besonders gefährdet sind Gebiete mit einer hohen Vogelkonzentration sowie die gesamte Bundesrepublik Deutschland während des Vogelzuges im Frühjahr und Herbst.", None),
            ("fact", "Vogelschlag-Statistik: Ca. 90% aller Vogelschläge ereignen sich bodennah in der Umgebung eines Flugplatzes. Laut Aussage der ICAO ereignen sich rund 90% aller Vogelschläge bei Start und Landung.", None),
            ("text", "Zur Vermeidung oder Verminderung der Wirkung von Vogelschlägen gibt es drei wesentliche Maßnahmen: Zunächst kann seitens des Flugplatzes versucht werden, die Vögel durch entsprechende Maßnahmen vom Flugplatzgelände zu vertreiben. Der Flugzeugführer kann versuchen, gefährdete Gebiete und Zugvogelrouten zu vermeiden. Das Deutsche DAVVL e.V. gibt ein sogenanntes Birdtam heraus.", None),
        ],
        "quiz": [
            {
                "q": "Welche Gefahr besteht bei hohem Pistenbewuchs?",
                "opts": ["Beschädigungen von Bauteilen mit geringer Bodenfreiheit (Landeklappen, Propeller)", "Eine Verkürzung der Startstrecke", "Probleme beim Funkempfang von unter dem Rumpf angebrachten Antennen", "Gefahr durch Tiere"],
                "answer": 0,
                "explanation": "Bei hohem Pistenbewuchs besteht Gefahr von Beschädigungen an Bauteilen mit geringer Bodenfreiheit wie Landeklappen und Propeller.",
                "is_official": 1
            },
            {
                "q": "Nennen Sie wenigstens vier Faktoren, die beim Start und der Landung berücksichtigt werden müssen.",
                "opts": ["Wetter, Wind, Pistenzustand, Masse und Druckhöhe", "Nur Wind und Pistenzustand", "Nur Masse und Wetter", "Ausschließlich die Pistenlänge"],
                "answer": 0,
                "explanation": "Beim Start/Landung zu berücksichtigen: Pistenzustand, Neigung, Wetterbedingungen, Umgebung des Flugplatzes, Masse, Schwerpunktlage, Flugzeugzustand, Triebwerksleistung, Druckhöhe, Temperatur und Flugtechnik.",
                "is_official": 0
            },
            {
                "q": "Welche Auswirkungen hat feuchtes Gras auf den Startlauf und die Landung?",
                "opts": ["Verlängerte Startrollstrecke und reduzierte Bremswirkung", "Verkürzte Startrollstrecke", "Keine Auswirkungen", "Nur Auswirkungen bei Spornradflugzeugen"],
                "answer": 0,
                "explanation": "Feuchtes Gras reduziert die Bodenhaftung und verlängert die Startrollstrecke um ca. 10%. Gleichzeitig vermindert es die Bremsleistung und die Richtungsstabilität.",
                "is_official": 0
            },
            {
                "q": "Muss bei Schnee auf der Piste ein Zuschlag berücksichtigt werden?",
                "opts": ["Nein", "Ja, wenigstens 30%", "Ja, wenigstens 50%", "Ja, aber nicht mehr als 40%"],
                "answer": 1,
                "explanation": "Bei Schnee auf der Piste ist ein Zuschlag von mindestens 30% für die Startrollstrecke zu berücksichtigen.",
                "is_official": 1
            },
            {
                "q": "Wie ändert sich die Landestrecke bei ansteigender Piste?",
                "opts": ["Sie verlängert sich", "Sie bleibt unverändert", "Das ist vom Wind abhängig", "Sie verkürzt sich"],
                "answer": 3,
                "explanation": "Bei einer in Landerichtung ansteigenden Piste verkürzt sich die Landestrecke – die Steigung wirkt als zusätzliche Bremse.",
                "is_official": 1
            },
            {
                "q": "Mit welcher Formel kann die anteilige Gegenwindkomponente berechnet werden?",
                "opts": ["HWC [kt] = sinWW × WV [kt]", "HWC [kt] = cosWW × WV [kt]", "HWC [kt] = tanWW × WV [kt]", "HWC [kt] = cotWW × WV [kt]"],
                "answer": 1,
                "explanation": "Die Gegenwindkomponente (Head Wind Component) berechnet sich: HWC [kt] = cos(Windwinkel) × WV (Windgeschwindigkeit in kt).",
                "is_official": 1
            },
            {
                "q": "Was ist eine Windscherung?",
                "opts": ["Ständiger Seitenwind", "Sprunghafte Änderung von Windrichtung und/oder -stärke auf kurzer Distanz", "Rückenwind beim Landeanflug", "Seitenwindkomponente beim Start"],
                "answer": 1,
                "explanation": "Windscherung ist eine sprunghafte Änderung der Windrichtung und/oder Windstärke innerhalb einer kurzen horizontalen und/oder vertikalen Entfernung.",
                "is_official": 1
            },
            {
                "q": "Wie viele Turbulenzkategorien werden unterschieden?",
                "opts": ["2", "3", "4", "5"],
                "answer": 2,
                "explanation": "Es werden 4 Turbulenzkategorien unterschieden: Leichte, Mäßige, Starke und Extreme Turbulenz.",
                "is_official": 1
            },
            {
                "q": "In welcher Situation sind Wirbelschleppen am stärksten ausgeprägt?",
                "opts": ["Bei einem leichten, langsam fliegenden Flugzeug mit geringer Landeklappenstellung", "Bei einem schweren, langsam fliegenden Flugzeug mit geringer Landeklappenstellung", "Bei einem schweren, schnell fliegenden Flugzeug mit geringer Landeklappenstellung", "In allen genannten Situationen gleich stark"],
                "answer": 1,
                "explanation": "Wirbelschleppen sind am stärksten bei einem schweren, langsam fliegenden Flugzeug mit geringer Landeklappenstellung – maximale Auftriebsverteilung bei minimaler Geschwindigkeit.",
                "is_official": 1
            },
            {
                "q": "Wie sollte ein leichtes Flugzeug den Anflug hinter einem ebenfalls landenden schwereren Flugzeug durchführen?",
                "opts": ["Direkt hinter dem schwereren Flugzeug ansetzen", "Oberhalb des Gleitweges des vorausfliegenden Flugzeuges und mit Aufsetzpunkt hinter dessen Aufsetzpunkt", "Unterhalb des Gleitweges", "Es spielt keine Rolle"],
                "answer": 1,
                "explanation": "Ein leichtes Flugzeug sollte hinter einem schwereren oberhalb des Gleitweges des vorausfliegenden Flugzeuges fliegen und hinter dessen Aufsetzpunkt aufsetzen.",
                "is_official": 0
            },
            {
                "q": "Ein Luftfahrzeug muss Ihnen ausweichen, tut dies aber nicht. Wie verhalten Sie sich?",
                "opts": ["Auf Kurs bleiben", "Kipp- und Rollbewegungen durchführen", "Dem Luftfahrzeug ausweichen", "Landelichter wechselweise ein- und ausschalten"],
                "answer": 2,
                "explanation": "Wenn ein anderes Luftfahrzeug ausweichen sollte, dies aber nicht tut, müssen Sie trotzdem ausweichen, um eine Kollision zu verhindern.",
                "is_official": 1
            },
            {
                "q": "In welcher Jahreszeit ist vermehrt mit Vogelstürmen zu rechnen?",
                "opts": ["Nur im Sommer", "Nur im Winter", "Im Frühling und Herbst", "Ganzjährig gleich"],
                "answer": 2,
                "explanation": "Im Frühling und Herbst ist vermehrt mit Vogelschlägen zu rechnen, da dies die Zugzeiten der Vögel sind.",
                "is_official": 0
            },
        ]
    },
    # ─────────────────────────────────────────────────────────────
    {
        "id": "ops-aussenlandung",
        "title": "4 – Unplanmäßige Landungen",
        "sort_order": 40,
        "exam_relevant": 1,
        "sections": [
            ("heading", "Unplanmäßige Landungen", "Außenlandung, Sicherheitslandung und Notwasserung"),
            ("text", "Gründe für eine außerplanmäßige Landung können vielfältig sein: Eine Wetterverschlechterung, technische Probleme, gesundheitliche Einschränkungen von Passagieren oder Besatzung, durch Umwege oder übermäßigen Gegenwind bedingte Kraftstoffknappheit oder der Einbruch der Dunkelheit vor Erreichen des Ziels.", None),
            ("subheading", "4.1 Außenlandung", None),
            ("text", "Der Begriff Außenlandung bezieht sich mit nichten nur auf Landungen jenseits von regulären Flugplätzen. Vielmehr können Außenlandungen ebenso auf großen Verkehrsflughäfen während des normalen Betriebs vorkommen. Bereits ein Aufsetzen wenige Meter vor der versetzten Landeschwelle genügt, um den Tatbestand einer Außenlandung zu erfüllen.", None),
            ("fact", "§ 25 LuftVG: Außenlandungen bedürfen entweder einer Genehmigung der zuständigen Luftfahrtbehörde und des Grundstückseigentümers oder eines zwingenden Grundes. Befindet sich das Luftfahrzeug nach einer Außenlandung in betriebsfähigem Zustand, ist ein Außenstart jedoch – auf wenige Ausnahmen – nur nach einer vorherigen Genehmigung durchgeführt werden.", None),
            ("subheading", "4.1.2 Außenlandung mit Motorhilfe", None),
            ("text", "Spitzt sich eine Situation zu, sollte der Entschluss zur Außenlandung so rechtzeitig getroffen werden, dass noch Handlungsspielraum besteht. Bei knapper Kraftstoffreserve muss jederzeit damit gerechnet werden, dass das Triebwerk versagt. Bereits zu einem Zeitpunkt, zu welchem kein Flugplatz mehr mit dem vorantigen Kraftstoff erreicht werden kann, mit den Vorbereitungen für eine Außenlandung beginnen.", None),
            ("subheading", "4.1.3 Triebwerksausfall", None),
            ("text", "Sofern bei einem einmotorigen Flugzeug das Triebwerk ausfällt, muss umgehend mit den Vorbereitungen für eine Außenlandung begonnen und die Geschwindigkeit des besten Gleitens eingenommen werden. Anschließend muss die Höhe über Grund festgestellt werden, um die richtigen Folgemaßnahmen einzuleiten zu können.", None),
            ("fact", "Triebwerksausfall-Gleitdaten (Beispiel): Bei 1.000 ft über Grund und ohne Wind beträgt die Gleitstrecke 2,5 NM. Die Gleitstrecke aus 1.000 ft Höhe nimmt pro 10 kt Rückenwind um 0,3 NM zu. Pro 10 kt Gegenwind nimmt die Gleitstrecke ab 1.000 ft um 0,31 NM ab.", None),
            ("subheading", "4.1.4 Auswahl des Außenlandefeldes", None),
            ("text", "Die Auswahl eines geeigneten Außenlandegeländes richtet sich nach zahlreichen Faktoren, deren Prioritäten gegeneinander abzuwägen sind: Länge, Wind, Hindernissituation im Anflug, Geländeneigung und Untergrund.", None),
            ("subheading", "Länge und Hindernisfreiheit", None),
            ("text", "Das ausgewählte Notlandefeld sollte zunächst eine ausreichende Länge aufweisen. Es ist hilfreich, wenn sowohl der Anflug als auch die Landestrecke frei von Hindernissen sind. Je eiliger der Anflug, je schlechter die Sichtverhältnisse und je höher der Bewuchs ist, desto leichter werden Hindernisse übersehen.", None),
            ("fact", "Besonders geeignete Außenlandefelder: Abgeerntete Getreidefelder sowie große und ebene Gelände, die in Windrichtung liegen und frei von Hindernissen sind. Nach einem Motorausfall ist nach dem Einnehmen der sicheren Gleitfluggeschwindigkeit die Höhe über Grund festzustellen.", None),
            ("subheading", "Oberflächenbeschaffenheit und Neigung", None),
            ("text", "Landwirtschaftlich bearbeitete Felder sind meist gut für eine Landung geeignet. Können Spuren landwirtschaftlicher Maschinen erkannt werden, deutet dies auf eine feste Oberfläche hin. Abgeerntete Getreidefelder bieten einen hervorragenden Untergrund. Sind starke Gefälle oder Unebenheiten bereits aus der Luft erkennbar, ist das betreffende Feld wahrscheinlich nicht für eine Landung geeignet.", None),
            ("subheading", "4.1.5 Anflug und Landung", None),
            ("text", "Stehen ausreichend Zeit und Höhe zur Verfügung, sollte über dem ausgewählten Landefeld gekreist werden, um Anflug und Landefläche in Augenschein zu nehmen. Je nach Situation muss entschieden werden, ob ein Überflug hilfreich ist oder das Risiko erhöht, weil beispielsweise das Triebwerk jeden Moment ausfallen kann.", None),
            ("fact", "Im Anflug sollten soweit möglich Standardverfahren und Checklisten angewendet werden. Damit werden Fehlerquellen durch Hektik, Stress und Vergessen eliminiert. Auf weichem Acker: Aufsetzen mit minimaler Sinkrate. Ist der Untergrund weich, sollte das Aufsetzen mit geringer Sinkrate und minimaler Fahrt erfolgen.", None),
            ("subheading", "4.1.6 Landung auf Außengelände", None),
            ("text", "Das Aufsetzen sollte mit der geringstmöglichen Geschwindigkeit erfolgen, weswegen sich Konfiguration voll ausgefahrene Landeklappen anbieten. Ist das Flugzeug mit Einziehfahrwerk ausgestattet, macht es in den meisten Fällen Sinn, das Fahrwerk auszufahren.", None),
            ("subheading", "4.2 Varianten: Sicherheitslandung, Notlandung und Notwasserung", None),
            ("text", "Eine Außenlandung kann in ganz verschiedenen Situationen und aus unterschiedlichen Motivationen heraus durchgeführt werden. Am kritischsten sind dabei erzwungene Außenlandungen wie die Notlandung und die Notwasserung.", None),
            ("subheading", "4.2.1 Sicherheitslandung", None),
            ("text", "Eine Sicherheitslandung ist eine Landung, die zur Aufrechterhaltung der Sicherheit oder zur Hilfeleistung bei einer Gefahr für Leib oder Leben einer Person erforderlich, jedoch keine Notlandung ist. Die Entscheidung zur Landung wird nicht durch einen Notfall (wie ein Feuer an Bord oder einen Triebwerksausfall bei einer einmotorigen Maschine) erzwungen.", None),
            ("subheading", "4.2.2 Notlandung", None),
            ("text", "Bei einer Notlandung handelt es sich im Gegensatz zur Sicherheitslandung um eine erzwungene Landung. Sie entsteht aus einer Situation, die es unmöglich macht, sich in der Luft zu halten und eine sofortige Landung unvermeidbar macht. Das besonders Prekäre an einer Notlandung ist der unmittelbare Handlungsbedarf des Luftfahrzeugführers.", None),
            ("fact", "Notlandung – Sofortmaßnahmen: Geeignetes Landefeld suchen, bestes Gleiten einnehmen, Höhe festellen, Notruf (7700 squawken), Anflug planen und durchführen, Checkliste abarbeiten. Nach der Landung: Insassen schützen, Rettungskräfte informieren.", None),
            ("subheading", "4.2.3 Notwasserung", None),
            ("text", "Bei der Notwasserung handelt es sich um eine sehr ungünstige Variante der Notlandung. Wenn möglich, sollte eine Notwasserung immer vermieden werden. Über das Verhalten von Luftfahrzeugen bei einer Notwasserung liegen nur wenige Daten vor, da diese Situation nicht im üblichen Umfang erprobt wird.", None),
            ("fact", "Notwasserung – Vorbereitung: § 21 der Betriebsordnung für Luftfahrtgerät fordert, dass für Flüge über Wasser, bei denen im Falle einer Störung mit einer Landung auf dem Wasser zu rechnen ist, eine entsprechende Rettungs- und Signalausrüstung vorhanden sein muss.", None),
            ("text", "Aufgrund der geringen Kabinengröße eines einmotorigen Flugzeuges ist es ratsam, Schwimmwesten vor einem Flug über Wasser bereits anzulegen. Im Fall einer Notwasserung sind die Schwimmwesten erst außerhalb des Flugzeuges aufzublasen, um eine Behinderung durch die sperrige Weste und Beschädigung der Luftkammern zu vermeiden.", None),
        ],
        "quiz": [
            {
                "q": "Wann darf eine Außenlandung durchgeführt werden?",
                "opts": ["Bei einer starken Wetterverschlechterung", "Auf Segelfluggeländen jederzeit", "Zum Nachtanken", "Wenn einem Fluggast übel wird"],
                "answer": 3,
                "explanation": "Eine Außenlandung ist bei zwingenden Gründen erlaubt, wie bei medizinischen Notfällen (Fluggast, dem übel wird). Starke Wetterverschlechterung allein ist kein ausreichender Grund.",
                "is_official": 1
            },
            {
                "q": "Unter welchen Bedingungen darf im Normalfall ein Außenstart nur erfolgen?",
                "opts": ["Mit Genehmigung der zuständigen Luftfahrtbehörde", "Ohne Genehmigung immer", "Nur mit Motorhilfe", "Nur bei Tag"],
                "answer": 0,
                "explanation": "Ein Außenstart darf nur nach einer vorherigen Genehmigung der zuständigen Luftfahrtbehörde durchgeführt werden.",
                "is_official": 0
            },
            {
                "q": "Ist bei einer Außenlandung mit Motorhilfe ein vorheriger Überflug des Landefeldes empfehlenswert?",
                "opts": ["Ja, wenn Zeit und Höhe vorhanden sind", "Nein, grundsätzlich nicht", "Nur bei Motorausfall", "Nur nachts"],
                "answer": 0,
                "explanation": "Wenn Zeit und Höhe zur Verfügung stehen, sollte das Landefeld im Überflug kontrolliert werden.",
                "is_official": 0
            },
            {
                "q": "Welche Maßnahmen sind bei einem Triebwerksausfall eines einmotorigen Flugzeuges zu treffen?",
                "opts": ["Bestes Gleiten einnehmen, Außenlandefeld suchen, Höhe festellen, Notruf", "Sofort landen ohne Planung", "Motor neu starten versuchen und dabei Höhe ignorieren", "Passagiere beruhigen und Weiterfliegen"],
                "answer": 0,
                "explanation": "Bei Triebwerksausfall: umgehend Geschwindigkeit des besten Gleitens einnehmen, geeignetes Außenlandefeld suchen, Höhe feststellen, Notruf absetzen.",
                "is_official": 0
            },
            {
                "q": "Welche Felder sind am besten für eine Außenlandung geeignet?",
                "opts": ["Frisch gepflügte Äcker", "Abgeerntete Getreidefelder sowie große ebene Gelände in Windrichtung, frei von Hindernissen", "Felder mit hohem Bewuchs", "Waldlichtungen"],
                "answer": 1,
                "explanation": "Besonders geeignet: Abgeerntete Getreidefelder sowie große und ebene Gelände, die in Windrichtung liegen und frei von Hindernissen sind.",
                "is_official": 0
            },
            {
                "q": "Was sollte bei einer Außenlandung auf einem Feld mit hohem Bewuchs beachtet werden?",
                "opts": ["Das Fahrwerk darf nicht ausgefahren werden", "Die Türen müssen verschlossen bleiben", "Die Oberfläche des Bewuchses ist als Erdboden anzunehmen", "Das Triebwerk muss vor der Landung abgestellt werden"],
                "answer": 2,
                "explanation": "Bei hohem Bewuchs ist die Oberfläche des Bewuchses als Erdboden anzunehmen, mit voll ausgefahrenen Landeklappen und Mindestfahrt aufzusetzen.",
                "is_official": 1
            },
            {
                "q": "Welche Faktoren müssen bei der Auswahl eines Außenlandefeldes berücksichtigt werden?",
                "opts": ["Nur Länge und Wind", "Länge, Wind, Hindernisse, Neigung, Untergrund und Oberflächenbeschaffenheit", "Nur Länge und Untergrund", "Nur Hindernisse"],
                "answer": 1,
                "explanation": "Bei der Auswahl eines Außenlandefeldes sind zu berücksichtigen: Länge, Wind, Hindernissituation im Anflug, Geländeneigung, Untergrund und Oberflächenbeschaffenheit.",
                "is_official": 0
            },
            {
                "q": "Wie sollte der Anflug auf ein Außenlandefeld durchgeführt werden?",
                "opts": ["Möglichst hoch und steil", "Stabilisiert mit Standardverfahren und Checkliste", "Ohne Checkliste um Zeit zu sparen", "So schnell wie möglich"],
                "answer": 1,
                "explanation": "Im Anflug sollten soweit möglich Standardverfahren und Checklisten angewendet werden. Damit werden Fehlerquellen durch Hektik, Stress und Vergessen eliminiert.",
                "is_official": 0
            },
        ]
    },
    # ─────────────────────────────────────────────────────────────
    {
        "id": "ops-tech-defekte",
        "title": "5 – Technische Defekte",
        "sort_order": 50,
        "exam_relevant": 1,
        "sections": [
            ("heading", "Technische Defekte", "Triebwerksprobleme, Fahrwerk und Systemausfälle"),
            ("text", "Technische Defekte erfordern rasche Reaktion und die korrekte Anwendung von Notverfahren aus dem Flughandbuch. Da in diesen Fällen oft nur wenige Minuten oder Sekunden zur Verfügung stehen, müssen die grundlegenden Handgriffe auswendig bekannt sein.", None),
            ("subheading", "5.1 Triebwerksprobleme", None),
            ("subheading", "5.1.1 Anlassvorgang", None),
            ("text", "Beim Anlassvorgang können verschiedene Probleme auftreten. Ein heißes Triebwerk, das bereits gelaufen ist, benötigt beim Neustart oft weniger Kraftstoff als ein kaltes. Der Anlassvorgang sollte im Flughandbuch nachgeschlagen werden.", None),
            ("fact", "Anlassvorgang: Beim Anlassen muss ein Feuerlöscher verfügbar sein (Vergaserbrandgefahr). Das Starten eines Triebwerks bei manueller Propellerbewegung ist gefährlich. Bei sehr kalten Temperaturen können Flugzeugmotoren mit Warmluft vorgeheizt werden.", None),
            ("subheading", "5.1.2 Start", None),
            ("text", "Beim Start können Triebwerksprobleme besonders kritisch sein. Ein Startabbruch muss rechtzeitig eingeleitet werden. Halbbahnmarkierungen dienen als Anhaltspunkt für einen Startabbruch.", None),
            ("fact", "Gelingt es nicht, rechtzeitig auf der Piste aufzusetzen, ist ein Durchstartmanöver einzuleiten (Vollgas, Vorwärmung kalt, Klappen stufenweise einfahren). Aufgrund der sofortigen Auftriebsverringerung (Gefahr des Durchsackens) dürfen die Landeklappen beim Durchstartmanöver nicht sofort vollständig eingefahren werden.", None),
            ("subheading", "5.1.3 Reiseflug", None),
            ("text", "Im Reiseflug können Triebwerksprobleme durch ungewöhnliche Geräusche, Vibrationen, unrunden Motorlauf, Leistungsabfall oder Anzeigen erkannt werden. Bei anhaltenden Problemen sollte umgehend ein geeigneter Landeplatz angesteuert werden.", None),
            ("subheading", "5.1.4 Abfall des Kraftstoffdrucks", None),
            ("text", "Ein Abfall des Kraftstoffdrucks zeigt an, dass der Motor nicht mehr ausreichend mit Kraftstoff versorgt wird. Ursachen können eine leere Kraftstoffleitung, ein Ausfall der elektrischen Kraftstoffpumpe oder ein verstopfter Kraftstofffilter sein.", None),
            ("fact", "Bei Kraftstoffdruckabfall: Elektrische Kraftstoffpumpe einschalten, Kraftstofftank wechseln, Vergaservorwärmung einschalten. Wenn keine Verbesserung: Außenlandung vorbereiten.", None),
            ("subheading", "5.1.5 Wiederanlassverfahren", None),
            ("text", "Das Wiederanlassverfahren im Flug ist im Flughandbuch beschrieben und sollte in einer sicheren Höhe durchgeführt werden. Ein Neustart nach einer Vergaservereisung ist nur nach einer ausdrücklichen Genehmigung der zuständigen Landesluftfahrtbehörde möglich.", None),
            ("subheading", "5.2 Fahrwerk und Steuerung", None),
            ("text", "Fahrwerksprobleme können beim Ausfahren oder Einfahren des Fahrwerks auftreten. Bei Einziehfahrwerk muss bei jedem Anflug die Fahrwerksposition kontrolliert werden.", None),
            ("fact", "Fahrwerksprobleme: Beim Einziehfahrwerk ist darauf zu achten, dass das Fahrwerk vollständig ausgefahren ist, bevor gelandet wird. Kann das Fahrwerk nicht ausgefahren werden, sollte eine Bauchlandung mit möglichst geringer Fahrt und auf weichem Untergrund durchgeführt werden.", None),
            ("subheading", "5.2.2 Einschränkung der Steuerung", None),
            ("text", "Einschränkungen der Steuerung können durch Klemmungen, Kabelbrüche oder andere mechanische Defekte entstehen. In diesem Fall ist das Flugzeug mit den verbleibenden Steuermöglichkeiten zu kontrollieren und schnellstmöglich zu landen.", None),
            ("subheading", "5.3 Systemausfälle", None),
            ("subheading", "5.3.1 Instrumentenausfall", None),
            ("text", "Beim Ausfall von Instrumenten muss der Pilot auf die verbleibenden Instrumente ausweichen. Bei Ausfall des Fahrtmessers: Geschwindigkeit anhand des Motorgeräuschs und der Fluglage abschätzen.", None),
            ("subheading", "5.3.2 Ausfall der elektrischen Anlage", None),
            ("text", "Beim Ausfall der elektrischen Anlage fallen alle elektrisch betriebenen Geräte aus. Nur das Zündsystem und ggf. die mechanischen Instrumente bleiben funktionsfähig. Sofortige Landung anstreben.", None),
            ("subheading", "5.3.3 Funkausfall", None),
            ("text", "Bei Funkausfall sollte der Transponder auf Code 7600 (NORDO) gestellt werden. An kontrollierten Flugplätzen sind dann die Lichtzeichen der Tower-Lightgun zu beachten.", None),
            ("fact", "NORDO-Verfahren: Transponder auf 7600 stellen, in der Platzrunde anfliegen und auf Lichtzeichen des Towers warten. Grünes stetiges Licht = Landung freigegeben. Rotes stetiges Licht = Bitte warten. Rotes Blinken = Platz ist nicht sicher.", None),
        ],
        "quiz": [
            {
                "q": "Welche Gefahr besteht beim Rollen über Pistenoberflächen mit hohem Bewuchs?",
                "opts": ["Beschädigungen an Bauteilen mit geringer Bodenfreiheit (Landeklappen, Propeller)", "Verkürzung der Startstrecke", "Schlechter Funkempfang", "Gefahr durch Tiere"],
                "answer": 0,
                "explanation": "Bei hohem Bewuchs können Landeklappen und Propeller beschädigt werden.",
                "is_official": 1
            },
            {
                "q": "Was ist beim Rollen auf einem Flughafen bei Orientierungsverlust zu tun?",
                "opts": ["Einfach weiterfahren", "Anhalten und Meldung an die Flugverkehrskontrollstelle machen", "Auf eigene Faust orientieren", "Zurück zum Gate fahren"],
                "answer": 1,
                "explanation": "Bei Orientierungslosigkeit auf dem Rollweg muss sofort die Flugverkehrskontrollstelle informiert werden.",
                "is_official": 0
            },
            {
                "q": "Wovon hängt die Wirbelschleppenstärke ab?",
                "opts": ["Nur von der Masse", "Von Masse, Fluggeschwindigkeit und Klappenstellung", "Nur von der Geschwindigkeit", "Von Masse und Farbe"],
                "answer": 1,
                "explanation": "Wirbelschleppenstärke hängt von Masse, Fluggeschwindigkeit und Klappenstellung ab.",
                "is_official": 0
            },
            {
                "q": "In welchen Schritten wird ein Durchstartmanöver durchgeführt?",
                "opts": ["Vollgas, Vorwärmung kalt, Klappen stufenweise einfahren", "Vollgas, Klappen sofort einfahren", "Nur Vollgas", "Motor abstellen und landen"],
                "answer": 0,
                "explanation": "Durchstart: Vollgas, Vergaservorwärmung kalt, Klappen stufenweise einfahren (nicht sofort vollständig – Gefahr des Durchsackens).",
                "is_official": 0
            },
            {
                "q": "Was ist ein 'stabilisierter Anflug'?",
                "opts": ["Ein Anflug bei dem alle Parameter (Geschwindigkeit, Sinkrate, Konfiguration) rechtzeitig stabilisiert sind", "Ein Anflug ohne Kurs-Änderungen", "Ein Anflug nur bei stabilen Wetterbedingungen", "Ein Anflug bei dem das Fahrwerk eingefahren bleibt"],
                "answer": 0,
                "explanation": "Ein stabilisierter Anflug bedeutet, dass die Anfluggrundlinie ausreichend früh in der Landekonfiguration mit der Endanfluggeschwindigkeit erreicht ist.",
                "is_official": 0
            },
            {
                "q": "Wie wird ein Kurzstart durchgeführt?",
                "opts": ["Klappen in Startstellung, Motor auf Startleistung, Bremsen lösen, Bugrad entlasten, mit Mindestgeschwindigkeit abheben", "Ohne Klappen, maximale Geschwindigkeit", "Klappen voll ausfahren und sofort abheben", "Motor auf halbe Leistung"],
                "answer": 0,
                "explanation": "Kurzstart: Klappen in Startstellung (nach Flughandbuch), Motor auf Startleistung bringen, dann Bremsen lösen, Bugrad entlasten und mit Mindestgeschwindigkeit abheben.",
                "is_official": 0
            },
        ]
    },
    # ─────────────────────────────────────────────────────────────
    {
        "id": "ops-sonstige-gefahren",
        "title": "6 – Sonstige Gefahren",
        "sort_order": 60,
        "exam_relevant": 1,
        "sections": [
            ("heading", "Sonstige Gefahren", "Kritische Fluglagen, Störungen, Gebirgsflug und Beladungsfehler"),
            ("text", "Neben den bisher beschriebenen Gefahren gibt es weitere Situationen, die einen Piloten vor besondere Herausforderungen stellen können. Diese reichen von ungewöhnlichen Fluglagen über gefährliche Eingriffe bis hin zu Beladungsfehlern.", None),
            ("subheading", "6.1 Kritische Fluglagen", None),
            ("subheading", "6.1.1 Ungewöhnliche Fluglagen", None),
            ("text", "Ungewöhnliche Fluglagen können durch plötzliche Turbulenzen, Orientierungsverlust oder Fehler bei der Steuerung entstehen. Das frühzeitige Erkennen und korrekte Ausleiten ist entscheidend.", None),
            ("fact", "Ausleitung einer ungewöhnlichen Fluglage: (1) Mach feststellen, ob Steig- oder Sinkflug vorliegt. (2) Bei Übergeschwindigkeit zunächst Motor drosseln, dann vorsichtig ausleiten. (3) Bei zu geringer Geschwindigkeit zunächst Nase senken, dann Motor geben.", None),
            ("subheading", "6.1.2 Strömungsabriss", None),
            ("text", "Ein Strömungsabriss (Stall) tritt auf, wenn der kritische Anstellwinkel überschritten wird – unabhängig von der Fluggeschwindigkeit! Das Flugzeug verliert abrupt an Auftrieb.", None),
            ("fact", "Strömungsabriss-Ausleitung: Steuerknüppel nach vorne (Nase runter), Motorleistung erhöhen, Querruder neutral, nach Erreichen der normalen Fluggeschwindigkeit ausleiten. Wichtig: Strömungsabriss ist eine Funktion des Anstellwinkels, nicht der Geschwindigkeit!", None),
            ("subheading", "6.1.3 Trudeln", None),
            ("text", "Trudeln (Spin) tritt auf, wenn ein Flügel stärker strömungsabgerissen ist als der andere. Dies führt zur Rotation um die Längsachse kombiniert mit einem steilen Sinkflug.", None),
            ("fact", "Trudelausleitung (PARE): Power (Motor auf Leerlauf), Aileron neutral (Querruder neutral), Rudder gegen die Drehrichtung (Gegenruder), Elevator nach vorne (Nase runter). Nach Beendigung des Trudelns sanft ausleiten.", None),
            ("subheading", "6.1.4 Steilspirale", None),
            ("text", "Eine Steilspirale entsteht, wenn ein steiler Kurvenflug unkontrolliert wird. Das Flugzeug dreht sich schnell und nimmt an Fahrt zu, während die Höhe schnell verloren geht.", None),
            ("subheading", "6.2 Störungen und gefährliche Eingriffe", None),
            ("subheading", "6.2.1 Störungen am Boden", None),
            ("text", "Störungen am Boden können durch fremde Objekte auf dem Rollweg (FOD – Foreign Object Debris), unerwartete Fahrzeuge oder andere Flugzeuge entstehen.", None),
            ("subheading", "6.2.2 Gefährliche Eingriffe", None),
            ("text", "Gefährliche Eingriffe (Unlawful Interference) umfassen Situationen wie Entführungen oder andere Bedrohungen an Bord.", None),
            ("fact", "Bei Entführung: Transponder auf 7500 stellen (ohne Ansage). Alle normalen Verfahren soweit wie möglich einhalten. Mit ATC kommunizieren, wenn sicher möglich.", None),
            ("subheading", "6.3 Gebirgs- und Höhenflüge", None),
            ("text", "Gebirgsflüge erfordern besondere Aufmerksamkeit und Vorbereitung. Leewellen, Turbulenzen und eingeschränkte Ausweichmöglichkeiten machen diese Flüge besonders anspruchsvoll.", None),
            ("fact", "Gebirgsflüge – Grundregeln: Nie unterhalb von 1.000 ft AGL über Gebirge fliegen. Leewellen können extrem stark sein. Bei starkem Wind stets auf der Luvseite der Berge bleiben. Ausreichende Kraftstoff- und Zeitreserve einplanen.", None),
            ("subheading", "6.4 Beladungsfehler", None),
            ("text", "Beladungsfehler können die Flugsicherheit erheblich beeinträchtigen. Ein falscher Schwerpunkt oder eine Überlastung des Flugzeuges kann zu Steuerungsproblemen führen.", None),
            ("fact", "Schwerpunktlage: Der Schwerpunkt (SP) muss sich während des gesamten Fluges innerhalb der zulässigen Grenzen (Envelope) befinden. Die ermittelten Schwerpunktlagen müssen sich während des kompletten Fluges innerhalb der zulässigen Grenzen befinden.", None),
            ("table_row", "Schwerpunkt zu weit vorne", "Erhöhter Steueraufwand am Höhenruder, verschlechterte Steigrate, verlängerte Startstrecke"),
            ("table_row", "Schwerpunkt zu weit hinten", "Instabiles Flugzeug, Neigung zum Aufbäumen, Strömungsabriss schwerer zu beherrschen"),
            ("table_row", "Überladung", "Verlängerte Start- und Landestrecke, reduzierte Steigleistung, verschlechterte Manövrierfähigkeit"),
        ],
        "quiz": [
            {
                "q": "Was bedeutet Schwerpunktlage = Gesamtmoment / Gesamtmasse?",
                "opts": ["Die Berechnung der Schwerpunktlage", "Die maximale Zuladung", "Die Sicherheitsmarge", "Den Kraftstoffverbrauch"],
                "answer": 0,
                "explanation": "Die Schwerpunktlage ergibt sich als: Schwerpunktlage = Gesamtmoment / Gesamtmasse.",
                "is_official": 0
            },
            {
                "q": "Was ist das PARE-Verfahren bei Trudeln?",
                "opts": ["Power, Aileron neutral, Rudder gegen Drehrichtung, Elevator vor", "Pull, Add power, Roll, Exit", "Pitch up, Add throttle, Roll out, Exit", "Power off, Aileron, Rudder, Elevator"],
                "answer": 0,
                "explanation": "PARE: Power (Leerlauf), Aileron neutral, Rudder gegen Drehrichtung (Gegenruder), Elevator nach vorne (Nase runter).",
                "is_official": 0
            },
            {
                "q": "Was ist beim Einflug in starke Turbulenz ratsam?",
                "opts": ["Geschwindigkeit erhöhen", "Geschwindigkeit auf Turbulenzpenetrationsgeschwindigkeit (grüner Bereich) reduzieren und Höhe/Fluglage konstant halten", "Sofort landen", "Motor abstellen"],
                "answer": 1,
                "explanation": "Bei starker Turbulenz: Geschwindigkeit im grünen Bereich des Fahrtmessers halten, konstante Triebwerksleistung setzen und die Fluglage so konstant wie möglich halten.",
                "is_official": 0
            },
            {
                "q": "Was ist ein Strömungsabriss?",
                "opts": ["Überschreitung des kritischen Anstellwinkels, unabhängig von der Geschwindigkeit", "Nur bei zu geringer Geschwindigkeit möglich", "Triebwerksausfall", "Funk-Ausfall"],
                "answer": 0,
                "explanation": "Ein Strömungsabriss tritt auf, wenn der kritische Anstellwinkel überschritten wird – dies ist unabhängig von der Fluggeschwindigkeit möglich!",
                "is_official": 0
            },
            {
                "q": "Was ist bei einem Transponder-Code 7500 zu verstehen?",
                "opts": ["Allgemeiner Notfall", "Funkausfall", "Entführung / Unlawful Interference", "VFR-Standardcode"],
                "answer": 2,
                "explanation": "Transpondercode 7500 bedeutet Entführung / Unlawful Interference. Dieser Code wird nie laut angekündigt.",
                "is_official": 0
            },
        ]
    },
]


def run():
    db = sqlite3.connect(DATABASE)
    db.row_factory = sqlite3.Row

    # ── Ensure subject exists ──────────────────────────────────────────────
    existing = db.execute("SELECT id FROM learn_subjects WHERE id=?", (SUBJECT_ID,)).fetchone()
    if not existing:
        db.execute("""
            INSERT INTO learn_subjects (id, code, title, icon, color, overview, sort_order)
            VALUES (?,?,?,?,?,?,?)
        """, (SUBJECT_ID, "70", "Betriebliche Verfahren", "✅", "#f59e0b",
              "Verhalten in besonderen Fällen – Kritische Wetterbedingungen, Feuer und Rauch, Gefahren in Bodennähe, unplanmäßige Landungen, technische Defekte und sonstige Gefahren. Band 7 des Advanced PPL-Guide.",
              70))

    # ── Delete existing ops chapters ───────────────────────────────────────
    existing_ch = db.execute("SELECT id FROM learn_chapters WHERE subject_id=?", (SUBJECT_ID,)).fetchall()
    for ch in existing_ch:
        db.execute("DELETE FROM learn_sections WHERE chapter_id=?", (ch["id"],))
        db.execute("DELETE FROM learn_quiz WHERE chapter_id=?", (ch["id"],))
        db.execute("DELETE FROM learn_flashcards WHERE chapter_id=?", (ch["id"],))
    db.execute("DELETE FROM learn_chapters WHERE subject_id=?", (SUBJECT_ID,))
    db.commit()

    # ── Insert chapters ────────────────────────────────────────────────────
    for chap in CHAPTERS:
        db.execute("""
            INSERT INTO learn_chapters (id, subject_id, title, sort_order, exam_relevant)
            VALUES (?,?,?,?,?)
        """, (chap["id"], SUBJECT_ID, chap["title"], chap["sort_order"], chap["exam_relevant"]))

        # Sections
        for idx, sec in enumerate(chap["sections"]):
            stype, content, extra = sec
            db.execute("""
                INSERT INTO learn_sections (chapter_id, type, content, extra, sort_order)
                VALUES (?,?,?,?,?)
            """, (chap["id"], stype, content, extra, idx * 10))

        # Quiz
        for qidx, q in enumerate(chap.get("quiz", [])):
            db.execute("""
                INSERT INTO learn_quiz (chapter_id, question, options, answer, explanation, is_official, sort_order)
                VALUES (?,?,?,?,?,?,?)
            """, (chap["id"], q["q"], json.dumps(q["opts"]), q["answer"],
                  q.get("explanation", ""), q.get("is_official", 0), qidx * 10))

    db.commit()

    # ── Rebuild FTS ────────────────────────────────────────────────────────
    try:
        db.execute("DELETE FROM learn_fts WHERE subject_id=?", (SUBJECT_ID,))
        rows = db.execute("""
            SELECT sec.chapter_id, c.subject_id, c.title AS chapter_title,
                   s.title AS subject_title, sec.content
            FROM learn_sections sec
            JOIN learn_chapters c ON c.id = sec.chapter_id
            JOIN learn_subjects s ON s.id = c.subject_id
            WHERE c.subject_id = ?
        """, (SUBJECT_ID,)).fetchall()
        for r in rows:
            db.execute("""
                INSERT INTO learn_fts (chapter_id, subject_id, chapter_title, subject_title, content)
                VALUES (?,?,?,?,?)
            """, (r["chapter_id"], r["subject_id"], r["chapter_title"], r["subject_title"], r["content"]))
        db.commit()
    except Exception as e:
        print(f"FTS rebuild skipped: {e}")

    db.close()

    total_sec = sum(len(c["sections"]) for c in CHAPTERS)
    total_q   = sum(len(c.get("quiz", [])) for c in CHAPTERS)
    print(f"✅ Betriebliche Verfahren: {len(CHAPTERS)} Kapitel, {total_sec} Abschnitte, {total_q} Quizfragen importiert.")


if __name__ == "__main__":
    run()
