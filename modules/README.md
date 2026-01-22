# JuraConnect v2.0 - Arbeitsrecht Kanzleisoftware

## 🚀 Vollständige arbeitsrechtliche Kanzleisoftware

JuraConnect ist eine moderne, KI-gestützte Softwarelösung für Arbeitsrecht mit drei differenzierten Zugangswegen:

- **👷 Arbeitnehmer**: Tools zur Einschätzung bei Kündigung, Abfindung, Zeugnis
- **🏢 Arbeitgeber**: Kündigungs-Assistent, Sozialauswahl, Compliance
- **⚖️ Kanzlei**: **ALLE FEATURES** + Aktenverwaltung, KI-Schriftsatz-Generator, beA

## ✨ Alle Features implementiert

### 🔴 Kritische Features
1. ✅ PKH-Rechner (2024 Freibeträge)
2. ✅ Prozesskostenrechner 3 Instanzen (AG/LAG/BAG)
3. ✅ RA-Micro Aktenimport
4. ✅ Feature-Parität AN/AG
5. ✅ Neue Landing Page (3 Zugangswege)

### 🟡 Wichtige Features
6. ✅ Zeiterfassung (Stoppuhr, abrechenbar)
7. ✅ Kollisionsprüfung (BRAO §43a)
8. ✅ beA-Integration (Simulation)
9. ✅ KI-Vertragsanalyse
10. ✅ KI-Kündigungscheck
11. ✅ Fristen-Tracker mit Warnungen
12. ✅ Dokumenten-Checkliste AN/AG

### 🟢 Nice-to-have Features
13. ✅ KI-Wissensdatenbank mit RAG
14. ✅ Mandanten-Checkliste interaktiv
15. ✅ Druck- & Versandfunktion

### ⚖️ NEU: KI-Schriftsatz-Generator
16. ✅ **Kündigungsschutzklage** - Vollständige Klageschrift
17. ✅ **Lohnklage** - Klage auf Arbeitsentgelt
18. ✅ **Urlaubsklage** - Anspruch auf Urlaubsgewährung
19. ✅ **Urlaubsabgeltungsklage** - Nach Beendigung
20. ✅ **Zeugnisklage** - Erteilung/Berichtigung
21. ✅ **Vergleichsvorschlag** - Für Gütetermin

## 📊 Feature-Verfügbarkeit nach Dashboard

| Feature | 👷 AN | 🏢 AG | ⚖️ Kanzlei |
|---------|:-----:|:-----:|:----------:|
| **ANALYSE-TOOLS** ||||
| Kündigungsschutz-Check | ✅ | - | ✅ |
| KI-Kündigungscheck | ✅ | - | ✅ |
| KI-Vertragsanalyse | ✅ | ✅ | ✅ |
| Zeugnis-Analyse | ✅ | - | ✅ |
| **RECHNER** ||||
| Abfindungsrechner | ✅ | ✅ | ✅ |
| PKH-Rechner 2024 | ✅ | ✅ | ✅ |
| Prozesskostenrechner | ✅ | ✅ | ✅ |
| Sozialauswahl | - | ✅ | ✅ |
| **KANZLEI-TOOLS** ||||
| RA-Micro Import | - | - | ✅ |
| Zeiterfassung | - | - | ✅ |
| Fristen-Tracker | - | - | ✅ |
| Kollisionsprüfung | - | - | ✅ |
| beA-Postfach | - | - | ✅ |
| **SCHRIFTSÄTZE (KI)** ||||
| Klagen-Generator | - | - | ✅ |
| Druck & Versand | - | - | ✅ |
| **WEITERE** ||||
| Wissensdatenbank | ✅ | ✅ | ✅ |
| Mandanten-Checkliste | - | - | ✅ |
| Dokumenten-Checkliste | ✅ | ✅ | ✅ |

**Kanzlei = ALLE Features (29 Seiten)**

## 📦 Installation

```bash
# Repository klonen oder ZIP entpacken
cd juraconnect_v2

# Dependencies installieren
pip install -r requirements.txt

# Anwendung starten
streamlit run app.py
```

## 📁 Projektstruktur

```
juraconnect_v2/
├── app.py                          # Hauptanwendung (~2400 Zeilen)
├── requirements.txt                # Dependencies
├── README.md                       # Diese Datei
└── modules/
    ├── __init__.py
    ├── aktenimport.py              # RA-Micro Import (~550 Zeilen)
    ├── erweiterte_rechner.py       # PKH, Prozesskosten, Zeit, Fristen (~850 Zeilen)
    ├── kanzlei_tools.py            # Kollision, beA, Checkliste (~800 Zeilen)
    ├── ki_module.py                # KI-Vertragsanalyse, Kündigungscheck, RAG (~850 Zeilen)
    ├── mandanten_tools.py          # Mandanten-Checkliste, Druck/Versand (~700 Zeilen)
    ├── schriftsatz_generator.py    # KI-Klagen-Generator (~800 Zeilen) NEU
    ├── rechner.py                  # Basis-Rechner
    ├── kuendigungsschutz.py        # KSchG-Prüfung
    ├── zeugnis_analyse.py          # Zeugnis-Decoder
    ├── wiki.py                     # Wissensdatenbank
    ├── auth.py                     # Authentifizierung
    └── datenbank.py                # Datenbankoperationen

Gesamt: ~10.500 Zeilen Code
```

## ⚖️ KI-Schriftsatz-Generator

Der neue KI-Schriftsatz-Generator erstellt vollständige, anpassbare Schriftsätze:

### Verfügbare Klagen:
- **Kündigungsschutzklage** (§ 4 KSchG)
- **Lohnklage** (§ 611a BGB)
- **Urlaubsklage** (§ 7 BUrlG)
- **Urlaubsabgeltungsklage** (§ 7 Abs. 4 BUrlG)
- **Zeugnisklage** (§ 109 GewO)
- **Vergleichsvorschlag** (§§ 9, 10 KSchG)

### Features:
- Automatische Streitwertberechnung
- Fristüberwachung (21-Tage-Klagefrist)
- Vollständiges Rubrum
- Anträge nach aktueller Rechtsprechung
- Begründung mit Rechtsgrundlagen
- HTML + Text Export
- Direkte Weiterleitung an Druck & Versand

## 🔧 Technische Details

- **Framework**: Streamlit
- **Python**: 3.10+
- **Rechtsstand**: RVG/GKG 2024, PKH Freibeträge 2024
- **Styling**: Custom CSS mit Dark Theme (Amber/Orange Akzente)

## 📋 RVG/GKG 2024 Compliance

- Vollständige Gebührentabellen bis 200.000€ Streitwert
- Korrekte Gebührensätze pro Instanz (AG/LAG/BAG)
- Sonderregel: Vergleich am Arbeitsgericht kostenlos
- MwSt. 19%, Post-/Telekommunikationspauschale max. 20€

## 📋 PKH 2024 Compliance

- Freibetrag Antragsteller: 619€
- Freibetrag Ehepartner: 619€
- Freibetrag Kinder: 393-619€ (altersabhängig)
- Erwerbstätigenfreibetrag: 255€
- Wohnkosten-Grenze: 572€
- Ratentabelle: max. 48 Monatsraten

## 🛡️ Sicherheit & Datenschutz

- DSGVO-konform
- Keine Speicherung sensibler Daten ohne Zustimmung
- Lokale Verarbeitung (kein Cloud-Upload erforderlich)

## 📝 Lizenz

© 2024 JuraConnect | Made in Germany 🇩🇪

## 🤝 Support

Bei Fragen oder Problemen wenden Sie sich an den Support.
