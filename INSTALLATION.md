# 📦 JuraConnect - Installationsanleitung

Diese Anleitung führt Sie durch alle Schritte zur Installation und zum Betrieb von JuraConnect.

---

## 📋 Inhaltsverzeichnis

1. [Voraussetzungen](#1-voraussetzungen)
2. [Installation (Lokal)](#2-installation-lokal)
3. [Deployment auf Streamlit Cloud](#3-deployment-auf-streamlit-cloud)
4. [Deployment auf eigenem Server](#4-deployment-auf-eigenem-server)
5. [Konfiguration](#5-konfiguration)
6. [Fehlerbehebung](#6-fehlerbehebung)

---

## 1. Voraussetzungen

### Systemanforderungen

- **Betriebssystem**: Windows 10/11, macOS 10.15+, Linux (Ubuntu 20.04+)
- **Python**: Version 3.9 oder höher
- **RAM**: Mindestens 4 GB
- **Festplatte**: 500 MB freier Speicher

### Python installieren

**Windows:**
1. Laden Sie Python von [python.org](https://python.org/downloads) herunter
2. Bei der Installation: ✅ "Add Python to PATH" aktivieren
3. Installation abschließen

**macOS:**
```bash
# Mit Homebrew
brew install python@3.11
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv
```

### Installation prüfen

```bash
python --version
# Sollte ausgeben: Python 3.9.x oder höher

pip --version
# Sollte ausgeben: pip 21.x oder höher
```

---

## 2. Installation (Lokal)

### Schritt 1: Projektdateien herunterladen

**Option A: Mit Git**
```bash
git clone https://github.com/IhrUsername/juraconnect.git
cd juraconnect
```

**Option B: Als ZIP**
1. Auf GitHub: "Code" → "Download ZIP"
2. ZIP entpacken
3. In den Ordner wechseln

### Schritt 2: Virtuelle Umgebung erstellen (empfohlen)

```bash
# Virtuelle Umgebung erstellen
python -m venv venv

# Aktivieren
# Windows:
venv\Scripts\activate

# macOS/Linux:
source venv/bin/activate
```

Nach der Aktivierung sehen Sie `(venv)` vor Ihrem Prompt.

### Schritt 3: Abhängigkeiten installieren

```bash
pip install -r requirements.txt
```

### Schritt 4: Anwendung starten

```bash
streamlit run app.py
```

Die Anwendung öffnet sich automatisch im Browser unter:
**http://localhost:8501**

### Schritt 5: Beenden

- Im Terminal: `Ctrl+C`
- Virtuelle Umgebung deaktivieren: `deactivate`

---

## 3. Deployment auf Streamlit Cloud

Streamlit Cloud ist kostenlos für öffentliche Repositories und ideal zum Testen.

### Schritt 1: GitHub-Repository erstellen

1. Auf [github.com](https://github.com) anmelden
2. "New repository" klicken
3. Name: `juraconnect`
4. Visibility: Public (für kostenlose Cloud) oder Private
5. "Create repository"

### Schritt 2: Code hochladen

```bash
# Im Projektordner
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/IhrUsername/juraconnect.git
git push -u origin main
```

### Schritt 3: Streamlit Cloud verbinden

1. Auf [share.streamlit.io](https://share.streamlit.io) anmelden (mit GitHub)
2. "New app" klicken
3. Repository auswählen: `IhrUsername/juraconnect`
4. Branch: `main`
5. Main file path: `app.py`
6. "Deploy!" klicken

### Schritt 4: Warten und testen

- Deployment dauert ca. 2-5 Minuten
- Sie erhalten eine URL wie: `https://juraconnect.streamlit.app`

### Einschränkungen Streamlit Cloud

⚠️ **Achtung bei Mandantendaten!**
- Daten werden nicht dauerhaft gespeichert
- Nicht für echte Mandantendaten geeignet
- Nur für Demonstrationszwecke

---

## 4. Deployment auf eigenem Server

Für den produktiven Einsatz mit echten Mandantendaten empfehlen wir einen eigenen Server.

### Option A: Einfaches Deployment

```bash
# Auf dem Server
git clone https://github.com/IhrUsername/juraconnect.git
cd juraconnect
pip install -r requirements.txt

# Im Hintergrund starten
nohup streamlit run app.py --server.port 8501 &
```

### Option B: Mit systemd (Linux)

1. Service-Datei erstellen:

```bash
sudo nano /etc/systemd/system/juraconnect.service
```

2. Inhalt:

```ini
[Unit]
Description=JuraConnect Streamlit App
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/juraconnect
ExecStart=/var/www/juraconnect/venv/bin/streamlit run app.py --server.port 8501 --server.address 127.0.0.1
Restart=always

[Install]
WantedBy=multi-user.target
```

3. Service aktivieren:

```bash
sudo systemctl enable juraconnect
sudo systemctl start juraconnect
sudo systemctl status juraconnect
```

### Option C: Mit Docker

1. Dockerfile erstellen (bereits im Projekt enthalten)

2. Image bauen und starten:

```bash
docker build -t juraconnect .
docker run -d -p 8501:8501 --name juraconnect juraconnect
```

### Option D: Mit Nginx als Reverse Proxy

1. Nginx installieren:
```bash
sudo apt install nginx
```

2. Konfiguration:
```nginx
# /etc/nginx/sites-available/juraconnect
server {
    listen 80;
    server_name juraconnect.ihre-domain.de;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

3. Aktivieren:
```bash
sudo ln -s /etc/nginx/sites-available/juraconnect /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### SSL mit Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d juraconnect.ihre-domain.de
```

---

## 5. Konfiguration

### Streamlit-Konfiguration

Datei: `.streamlit/config.toml`

```toml
[theme]
primaryColor = "#1E3A5F"    # Hauptfarbe
backgroundColor = "#FFFFFF"  # Hintergrund

[server]
port = 8501                  # Port
maxUploadSize = 50           # Max. Upload in MB
```

### Datenbank

Die SQLite-Datenbank wird automatisch erstellt unter:
- Linux/macOS: `~/.juraconnect/juraconnect.db`
- Windows: `C:\Users\<Name>\.juraconnect\juraconnect.db`

Pfad ändern:
```python
from modules.datenbank import JuraConnectDB
db = JuraConnectDB("/pfad/zu/meiner/datenbank.db")
```

### Umgebungsvariablen

Für Produktion empfohlen:

```bash
# .env Datei (nicht committen!)
STREAMLIT_SERVER_PORT=8501
STREAMLIT_SERVER_HEADLESS=true
JURACONNECT_DB_PATH=/var/data/juraconnect.db
```

---

## 6. Fehlerbehebung

### Häufige Probleme

**Problem: `ModuleNotFoundError: No module named 'streamlit'`**

Lösung:
```bash
pip install streamlit
# oder virtuelle Umgebung aktivieren
source venv/bin/activate
```

**Problem: Port bereits belegt**

Lösung:
```bash
streamlit run app.py --server.port 8502
```

**Problem: Seiten werden nicht gefunden**

Lösung:
- Prüfen Sie, dass der `pages/` Ordner existiert
- Dateinamen müssen mit Zahl beginnen: `1_Name.py`

**Problem: Datenbank-Fehler**

Lösung:
```bash
# Datenbank löschen und neu erstellen
rm ~/.juraconnect/juraconnect.db
# Anwendung neu starten
```

### Logs anzeigen

```bash
# Streamlit mit Debug-Output
streamlit run app.py --logger.level=debug
```

### Support

Bei weiteren Problemen:
1. GitHub Issues prüfen/erstellen
2. Streamlit Community Forum
3. Stack Overflow mit Tag `streamlit`

---

## 📞 Nächste Schritte

Nach erfolgreicher Installation:

1. **Testen**: Alle Module durchklicken
2. **Konfigurieren**: Theme und Einstellungen anpassen
3. **Daten**: Testdaten eingeben
4. **Backup**: Regelmäßige Backups einrichten
5. **Sicherheit**: Zugangsbeschränkung implementieren

---

**Viel Erfolg mit JuraConnect! ⚖️**
