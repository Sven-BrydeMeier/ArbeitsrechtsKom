# ⚖️ JuraConnect - Arbeitsrecht-Software

**Umfassende Softwarelösung für arbeitsrechtliche Kanzleien in Deutschland**

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)
![DSGVO](https://img.shields.io/badge/DSGVO-konform-brightgreen.svg)

---

## 📋 Inhaltsverzeichnis

- [Überblick](#-überblick)
- [Features](#-features)
- [Installation](#-installation)
- [Schnellstart](#-schnellstart)
- [Projektstruktur](#-projektstruktur)
- [Module im Detail](#-module-im-detail)
- [Deployment](#-deployment)
- [DSGVO-Konformität](#-dsgvo-konformität)
- [Beitragen](#-beitragen)
- [Lizenz](#-lizenz)

---

## 🎯 Überblick

JuraConnect ist eine spezialisierte Software für deutsche Arbeitsrechtskanzleien. Sie bietet umfassende Tools für:

- **Arbeitnehmer-Beratung**: Kündigungsschutz-Checks, Abfindungsberechnung, Zeugnisanalyse
- **Arbeitgeber-Beratung**: Sozialauswahl, Kündigungsassistent, Vertragsgestaltung
- **Kanzlei-interne Prozesse**: Schriftsatzgenerierung, Fristenverwaltung, Aktenverwaltung

### Zielgruppe

- Arbeitsrechtliche Kanzleien
- Fachanwälte für Arbeitsrecht
- Rechtsabteilungen mit Arbeitsrechtsfokus

---

## ✨ Features

### 👷 Arbeitnehmer-Dashboard

| Feature | Beschreibung |
|---------|--------------|
| 🚨 **Kündigungsschutz-Check** | Umfassende Prüfung der Kündigungsschutzsituation mit Erfolgsaussichten |
| 💰 **Abfindungsrechner** | Berechnung nach Regelabfindung mit Branchenfaktoren |
| 📄 **Zeugnis-Analyse** | KI-gestützte Analyse von Arbeitszeugnissen inkl. Geheimcode-Erkennung |
| ⏰ **Überstundenrechner** | Berechnung von Überstundenvergütung mit Zuschlägen |
| 🏖️ **Urlaubsrechner** | Anteiliger Urlaub und Urlaubsabgeltung |
| ⚖️ **Prozesskostenrechner** | Vollständige Kostenberechnung nach RVG/GKG 2024 |

### 🏢 Arbeitgeber-Dashboard

| Feature | Beschreibung |
|---------|--------------|
| 📋 **Kündigungs-Assistent** | Schritt-für-Schritt durch den Kündigungsprozess |
| 📊 **Sozialauswahl-Rechner** | Punktesystem nach BAG-Rechtsprechung |
| ⚠️ **Abmahnungs-Generator** | Rechtssichere Abmahnungen aus Vorlagen |
| 📝 **Arbeitsvertrags-Generator** | Modularer Baukasten für Arbeitsverträge |
| ✅ **Compliance-Checklisten** | Neueinstellung, Kündigung, Mutterschutz, DSGVO |

### ⚖️ Kanzlei-Tools

| Feature | Beschreibung |
|---------|--------------|
| 📝 **Schriftsatz-Generator** | Kündigungsschutzklage, Zeugnisklage, Lohnklage |
| 📅 **Fristenrechner** | 3-Wochen-Frist, Kündigungsfristen nach § 622 BGB |
| 📬 **RSV-Deckungsanfrage** | Automatisierte Deckungsanfragen |
| 💼 **Aktenanlage** | Schnelle Erfassung neuer Mandate |
| 📊 **Vergleichsrechner** | Abfindung vs. Weiterbeschäftigung |

### 📂 Aktenverwaltung

- Aktenübersicht mit Filterung und Suche
- Mandantenverwaltung
- Fristenkalender mit Priorisierung
- Dashboard mit KPIs

---

## 🚀 Installation

### Voraussetzungen

- Python 3.9 oder höher
- pip (Python Package Manager)
- Git (optional)

### Option 1: Installation von GitHub

```bash
# Repository klonen
git clone https://github.com/IhrUsername/juraconnect.git
cd juraconnect

# Virtuelle Umgebung erstellen (empfohlen)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# oder: venv\Scripts\activate  # Windows

# Abhängigkeiten installieren
pip install -r requirements.txt
```

### Option 2: Manuelle Installation

```bash
# Ordner erstellen
mkdir juraconnect
cd juraconnect

# Dateien kopieren (alle Dateien aus dem Projekt)

# Abhängigkeiten installieren
pip install streamlit pandas numpy python-dateutil
```

---

## ⚡ Schnellstart

### Lokale Ausführung

```bash
# Im Projektverzeichnis
streamlit run app.py
```

Die Anwendung ist dann unter `http://localhost:8501` erreichbar.

### Erste Schritte

1. **Startseite**: Übersicht über alle Module und aktuelle Fristen
2. **Arbeitnehmer**: Beginnen Sie mit dem Kündigungsschutz-Check
3. **Arbeitgeber**: Nutzen Sie den Kündigungs-Assistenten
4. **Kanzlei-Tools**: Generieren Sie Schriftsätze
5. **Akten**: Verwalten Sie Ihre Mandate

---

## 📁 Projektstruktur (GitHub-Verzeichnis)

```
juraconnect/
│
├── app.py                      # 🏠 Hauptanwendung (Landing Page + Dashboard)
├── requirements.txt            # Python-Abhängigkeiten
├── README.md                   # Diese Dokumentation
├── INSTALLATION.md             # Detaillierte Installationsanleitung
├── LICENSE                     # MIT-Lizenz
├── .gitignore                  # Git-Ausschlüsse (inkl. DSGVO-Schutz)
│
├── .streamlit/
│   └── config.toml            # Streamlit-Theme & Server-Konfiguration
│
├── modules/                    # Python-Backend-Module
│   ├── __init__.py            # Modul-Exporte
│   ├── auth.py                # 🔐 Authentifizierung & Benutzerverwaltung
│   ├── rechner.py             # 🧮 Alle Rechner (Fristen, Abfindung, etc.)
│   ├── kuendigungsschutz.py   # 🚨 Kündigungsschutz-Prüfung
│   ├── zeugnis_analyse.py     # 📄 KI-Zeugnis-Analyse
│   ├── arbeitgeber.py         # 🏢 Arbeitgeber-Tools
│   ├── vorlagen.py            # 📝 Dokumenten-Vorlagen
│   ├── datenbank.py           # 💾 SQLite-Datenbankanbindung
│   ├── wiki.py                # 📚 Arbeitsrecht-Wiki
│   ├── ki_assistent.py        # 🤖 KI-Aktenassistent
│   └── abrechnung.py          # 💰 Abrechnungssystem
│
├── pages/                      # Streamlit-Seiten (Multi-Page-App)
│   ├── 1_Arbeitnehmer.py      # 👷 Arbeitnehmer-Dashboard
│   ├── 2_Arbeitgeber.py       # 🏢 Arbeitgeber-Dashboard
│   ├── 3_Kanzlei_Tools.py     # ⚖️ Kanzlei-Tools
│   ├── 4_Akten.py             # 📂 Aktenverwaltung + KI + Abrechnung
│   ├── 5_Admin.py             # 🔧 Admin-Dashboard (nur für Admins)
│   └── 6_Wiki.py              # 📚 Arbeitsrecht-Wiki
│
└── data/                       # Datenverzeichnis (wird automatisch erstellt)
    ├── juraconnect.db         # SQLite-Datenbank
    └── users.json             # Benutzerdaten
```

---

## 🔐 Authentifizierung & Benutzerrollen

### Demo-Modus (Standard)

Im **Demo-Modus** können alle Funktionen ohne Anmeldung getestet werden:
- Automatischer Zugang beim Öffnen der Anwendung
- Alle Tools und Rechner sind verfügbar
- Daten werden **nicht** dauerhaft gespeichert
- Ideal für Evaluierung und Tests

### Benutzerrollen

| Rolle | Badge | Rechte |
|-------|-------|--------|
| **Admin** | 🔴 | Vollzugriff + Benutzerverwaltung |
| **Anwalt** | 🟢 | Alle Funktionen, Akten bearbeiten/löschen |
| **Mitarbeiter** | 🟡 | Standard-Funktionen, Akten bearbeiten |
| **Demo** | 🔵 | Nur Lesen, keine Speicherung |

### Standard-Zugangsdaten

| Benutzer | Passwort | Rolle |
|----------|----------|-------|
| `admin` | `admin123` | Administrator |
| `anwalt` | `anwalt123` | Anwalt |
| `mitarbeiter` | `mitarbeiter123` | Mitarbeiter |
| `demo` | `demo` | Demo-Benutzer |

⚠️ **Wichtig:** Ändern Sie die Standard-Passwörter vor dem Produktivbetrieb!

### Admin-Dashboard

Das Admin-Dashboard (nur für Admins) bietet:
- 👥 Benutzerverwaltung (anlegen, bearbeiten, löschen)
- ⚙️ Systemeinstellungen (Demo-Modus, Session-Timeout)
- 📊 Statistiken und Logs
- 🔐 Sicherheitseinstellungen

### Konfiguration

In `modules/auth.py` können Sie anpassen:

```python
APP_CONFIG = {
    "demo_mode_enabled": True,   # Demo-Button anzeigen
    "require_login": False,      # False = Direkter Demo-Zugang
    "session_timeout": 60,       # Minuten bis Auto-Logout
    "max_login_attempts": 5,     # Max. Fehlversuche
}
```

---

### rechner.py

Enthält alle Berechnungsklassen:

```python
from modules.rechner import (
    KuendigungsfristenRechner,
    AbfindungsRechner,
    ProzesskostenRechner,
    UrlaubsRechner,
    UeberstundenRechner,
    VerjaehrungsRechner
)

# Beispiel: Kündigungsfrist berechnen
from datetime import date
rechner = KuendigungsfristenRechner()
ergebnis = rechner.berechne_frist(
    eintrittsdatum=date(2018, 1, 1),
    kuendigungsdatum=date(2024, 6, 15),
    ist_arbeitgeber_kuendigung=True
)
print(ergebnis.frist_text)  # "2 Monate"
```

### kuendigungsschutz.py

Umfassende Kündigungsschutzprüfung:

```python
from modules.kuendigungsschutz import KuendigungsschutzPruefer, MandantDaten

daten = MandantDaten(
    alter=45,
    geschlecht="männlich",
    eintrittsdatum=date(2015, 3, 1),
    bruttogehalt=4500.0,
    # ... weitere Daten
)

pruefer = KuendigungsschutzPruefer()
ergebnis = pruefer.pruefe(daten)

print(ergebnis.erfolgsaussichten_prozent)  # z.B. 75
print(ergebnis.zusammenfassung)
```

### zeugnis_analyse.py

KI-gestützte Zeugnisanalyse:

```python
from modules.zeugnis_analyse import analysiere_zeugnis

zeugnis_text = """
Herr Müller hat die ihm übertragenen Aufgaben stets zu unserer 
vollen Zufriedenheit erledigt...
"""

analyse = analysiere_zeugnis(zeugnis_text)
print(analyse.gesamtnote_text)  # "Note 2 (gut)"
print(analyse.geheimcodes)      # Liste gefundener Geheimcodes
```

---

## 🌐 Deployment

### Streamlit Cloud (Empfohlen für Tests)

1. Repository auf GitHub pushen
2. Auf [share.streamlit.io](https://share.streamlit.io) anmelden
3. "New app" → Repository auswählen
4. Main file: `app.py`
5. Deploy!

### Lokaler Server

```bash
# Mit SSL (empfohlen für Produktion)
streamlit run app.py --server.sslCertFile=cert.pem --server.sslKeyFile=key.pem

# Mit spezifischem Port
streamlit run app.py --server.port 8080
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
```

```bash
# Build und Run
docker build -t juraconnect .
docker run -p 8501:8501 juraconnect
```

---

## 🔒 DSGVO-Konformität

JuraConnect wurde mit Blick auf DSGVO-Konformität entwickelt:

### Datenspeicherung

- **Lokal**: Alle Daten werden lokal in einer SQLite-Datenbank gespeichert
- **Keine Cloud**: Standardmäßig werden keine Daten an externe Server übertragen
- **Verschlüsselung**: Empfohlen für Produktivbetrieb

### Empfehlungen

1. **Hosting**: Eigener Server oder DSGVO-konformer EU-Anbieter
2. **Backups**: Regelmäßige, verschlüsselte Backups
3. **Zugriff**: Zugangsbeschränkung implementieren
4. **Löschkonzept**: Automatische Löschung nach Aufbewahrungsfrist

### Verarbeitungsverzeichnis

Die Anwendung verarbeitet:
- Mandantenstammdaten
- Gegnerinformationen
- Akteninhalte
- Fristendaten

---

## 🤝 Beitragen

Beiträge sind willkommen! 

### Entwicklungsumgebung einrichten

```bash
# Repository forken und klonen
git clone https://github.com/IhrUsername/juraconnect.git
cd juraconnect

# Entwicklungsabhängigkeiten installieren
pip install -r requirements.txt
pip install pytest black flake8

# Tests ausführen
pytest

# Code formatieren
black .
```

### Pull Requests

1. Fork erstellen
2. Feature-Branch: `git checkout -b feature/MeinFeature`
3. Commits: `git commit -m 'Beschreibung'`
4. Push: `git push origin feature/MeinFeature`
5. Pull Request öffnen

---

## 📄 Lizenz

MIT License - siehe [LICENSE](LICENSE)

---

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/IhrUsername/juraconnect/issues)
- **Dokumentation**: Diese README
- **E-Mail**: support@juraconnect.de (Beispiel)

---

## 🙏 Danksagung

- Streamlit Team für das großartige Framework
- Die Open-Source-Community
- Alle Beitragenden

---

**Made with ❤️ in Germany 🇩🇪**

*JuraConnect - Weil Arbeitsrecht einfacher sein kann.*
