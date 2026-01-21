"""
JuraConnect - Akten-Verwaltung
===============================
Übersicht und Verwaltung aller Akten
Mit KI-Assistent und Kostentransparenz
"""

import streamlit as st
from datetime import date, timedelta
import sys
sys.path.insert(0, '..')

from modules.datenbank import JuraConnectDB, Mandant, Akte, Frist, Dokument, get_db
from modules.ki_assistent import render_ki_assistent, AktenAssistent
from modules.abrechnung import (
    render_kostenübersicht, render_rechnungsstellung,
    AbrechnungsManager, erfasse_aktion
)
from modules.auth import (
    init_session_state, is_authenticated, get_current_user, is_demo_mode,
    render_user_menu, render_demo_banner
)


def render():
    init_session_state()
    
    st.title("📂 Akten-Verwaltung")
    
    render_demo_banner()
    render_user_menu()
    
    # Tabs für verschiedene Ansichten
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "📋 Aktenübersicht",
        "👥 Mandanten",
        "📅 Fristen",
        "🤖 KI-Assistent",
        "💰 Abrechnung",
        "📊 Dashboard"
    ])
    
    with tab1:
        render_aktenübersicht()
    
    with tab2:
        render_mandanten()
    
    with tab3:
        render_fristen()
    
    with tab4:
        render_ki_tab()
    
    with tab5:
        render_abrechnung_tab()
    
    with tab6:
        render_dashboard()


def render_ki_tab():
    st.header("🤖 KI-Aktenassistent")
    
    st.info("""
    Der KI-Assistent durchsucht **nur interne Akteninhalte** - keine externen Quellen.
    Alle Antworten basieren ausschließlich auf den in der Akte erfassten Informationen.
    """)
    
    # Akte auswählen
    demo_akten = ["2024-001-KS", "2024-002-Z", "2024-003-L"]
    
    selected_akte = st.selectbox(
        "Akte auswählen",
        ["Alle Akten durchsuchen"] + demo_akten,
        key="ki_akte_select"
    )
    
    akte_id = None if selected_akte == "Alle Akten durchsuchen" else selected_akte
    
    # KI-Assistent Widget rendern
    render_ki_assistent(akte_id)
    
    # Hinweis zur Kostenerfassung
    if not is_demo_mode():
        st.caption("💰 Jede KI-Anfrage wird automatisch zur Abrechnung erfasst.")


def render_abrechnung_tab():
    st.header("💰 Abrechnung & Kostentransparenz")
    
    if is_demo_mode():
        st.warning("🎮 Im Demo-Modus werden keine Kosten erfasst.")
    
    # Akte auswählen
    demo_akten = ["2024-001-KS", "2024-002-Z", "2024-003-L"]
    
    selected_akte = st.selectbox(
        "Akte auswählen",
        demo_akten,
        key="abr_akte_select"
    )
    
    st.divider()
    
    # Kostenübersicht
    render_kostenübersicht(selected_akte)
    
    st.divider()
    
    # Demo-Mandantendaten
    mandanten_info = {
        "2024-001-KS": ("Max Müller", "Musterstraße 1\n12345 Musterstadt"),
        "2024-002-Z": ("Anna Schmidt", "Beispielweg 2\n54321 Beispielstadt"),
        "2024-003-L": ("Peter Weber", "Testgasse 3\n67890 Testort")
    }
    
    mandant_name, mandant_adresse = mandanten_info.get(
        selected_akte, 
        ("Unbekannt", "Keine Adresse")
    )
    
    # Rechnungsstellung
    render_rechnungsstellung(selected_akte, mandant_name, mandant_adresse)
    
    st.divider()
    
    # Manuelle Leistungserfassung
    st.subheader("➕ Leistung manuell erfassen")
    
    with st.form("manuelle_leistung"):
        col1, col2 = st.columns(2)
        
        with col1:
            leistung_art = st.selectbox("Leistungsart", [
                "Beratungsgespräch",
                "Schriftsatz erstellt",
                "Gerichtstermin",
                "Dokumentenprüfung",
                "E-Mail/Telefonat",
                "Sonstiges"
            ])
        
        with col2:
            betrag = st.number_input("Betrag (€ netto)", min_value=0.0, value=100.0)
        
        beschreibung = st.text_input("Beschreibung")
        
        if st.form_submit_button("💾 Erfassen"):
            if not is_demo_mode():
                user = get_current_user()
                username = user.name if user else "System"
                
                mgr = AbrechnungsManager()
                mgr.erfasse_leistung(
                    akte_id=selected_akte,
                    leistung=leistung_art,
                    beschreibung=beschreibung,
                    betrag=betrag,
                    erstellt_von=username
                )
                st.success("✅ Leistung erfasst!")
                st.rerun()
            else:
                st.info("🎮 Im Demo-Modus wird nichts gespeichert.")


def render_aktenübersicht():
    st.header("📋 Aktenübersicht")
    
    # Filter
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_filter = st.selectbox("Status", ["Alle", "Aktiv", "Ruhend", "Abgeschlossen"])
    
    with col2:
        sachgebiet_filter = st.selectbox("Sachgebiet", [
            "Alle",
            "Kündigungsschutz",
            "Zeugnis",
            "Lohn/Gehalt",
            "Abfindung",
            "Sonstiges"
        ])
    
    with col3:
        suche = st.text_input("🔍 Suche", placeholder="Aktenzeichen, Name...")
    
    st.divider()
    
    # Demo-Daten (in Produktion aus DB)
    demo_akten = [
        {"az": "2024-001-KS", "rubrum": "Müller ./. TechCorp GmbH", "sachgebiet": "Kündigungsschutz", 
         "status": "Aktiv", "streitwert": 12000, "angelegt": "15.01.2024"},
        {"az": "2024-002-Z", "rubrum": "Schmidt ./. Handel AG", "sachgebiet": "Zeugnis", 
         "status": "Aktiv", "streitwert": 4500, "angelegt": "22.01.2024"},
        {"az": "2024-003-L", "rubrum": "Weber ./. Gastro GmbH", "sachgebiet": "Lohn/Gehalt", 
         "status": "Ruhend", "streitwert": 8500, "angelegt": "05.02.2024"},
        {"az": "2023-045-KS", "rubrum": "Fischer ./. Auto AG", "sachgebiet": "Kündigungsschutz", 
         "status": "Abgeschlossen", "streitwert": 15000, "angelegt": "12.09.2023"},
    ]
    
    # Filtern
    gefiltert = demo_akten
    if status_filter != "Alle":
        gefiltert = [a for a in gefiltert if a["status"] == status_filter]
    if sachgebiet_filter != "Alle":
        gefiltert = [a for a in gefiltert if a["sachgebiet"] == sachgebiet_filter]
    if suche:
        suche_lower = suche.lower()
        gefiltert = [a for a in gefiltert if suche_lower in a["az"].lower() or suche_lower in a["rubrum"].lower()]
    
    # Anzeige
    st.info(f"📂 {len(gefiltert)} Akten gefunden")
    
    for akte in gefiltert:
        status_farbe = {"Aktiv": "🟢", "Ruhend": "🟡", "Abgeschlossen": "⚪"}.get(akte["status"], "⚪")
        
        with st.expander(f"{status_farbe} **{akte['az']}** - {akte['rubrum']}"):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.write(f"**Sachgebiet:** {akte['sachgebiet']}")
                st.write(f"**Status:** {akte['status']}")
            
            with col2:
                st.write(f"**Streitwert:** {akte['streitwert']:,.2f} €")
                st.write(f"**Angelegt:** {akte['angelegt']}")
            
            with col3:
                st.button("📝 Bearbeiten", key=f"edit_{akte['az']}")
                st.button("📄 Dokumente", key=f"docs_{akte['az']}")
    
    # Neue Akte anlegen
    st.divider()
    if st.button("➕ Neue Akte anlegen"):
        st.session_state.show_neue_akte = True
    
    if st.session_state.get('show_neue_akte', False):
        with st.form("neue_akte_form"):
            st.subheader("📂 Neue Akte anlegen")
            
            col1, col2 = st.columns(2)
            with col1:
                neues_az = st.text_input("Aktenzeichen", value=f"2024-{len(demo_akten)+1:03d}")
                rubrum = st.text_input("Rubrum")
            
            with col2:
                sachgebiet = st.selectbox("Sachgebiet", [
                    "Kündigungsschutz", "Zeugnis", "Lohn/Gehalt", "Abfindung", "Sonstiges"
                ], key="neue_akte_sg")
                streitwert = st.number_input("Streitwert", min_value=0.0)
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Speichern", type="primary"):
                    st.success(f"✅ Akte {neues_az} angelegt!")
                    st.session_state.show_neue_akte = False
            with col2:
                if st.form_submit_button("❌ Abbrechen"):
                    st.session_state.show_neue_akte = False


def render_mandanten():
    st.header("👥 Mandanten")
    
    # Suche
    suche = st.text_input("🔍 Mandant suchen", placeholder="Name, E-Mail...")
    
    # Demo-Mandanten
    demo_mandanten = [
        {"name": "Max Müller", "email": "m.mueller@email.de", "telefon": "0171-1234567", "akten": 2},
        {"name": "Anna Schmidt", "email": "a.schmidt@email.de", "telefon": "0172-2345678", "akten": 1},
        {"name": "Peter Weber", "email": "p.weber@email.de", "telefon": "0173-3456789", "akten": 1},
        {"name": "Lisa Fischer", "email": "l.fischer@email.de", "telefon": "0174-4567890", "akten": 3},
    ]
    
    # Filtern
    if suche:
        suche_lower = suche.lower()
        demo_mandanten = [m for m in demo_mandanten if suche_lower in m["name"].lower() or suche_lower in m["email"].lower()]
    
    st.divider()
    
    # Anzeige als Tabelle
    col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 1, 1])
    with col1:
        st.markdown("**Name**")
    with col2:
        st.markdown("**E-Mail**")
    with col3:
        st.markdown("**Telefon**")
    with col4:
        st.markdown("**Akten**")
    with col5:
        st.markdown("**Aktion**")
    
    for m in demo_mandanten:
        col1, col2, col3, col4, col5 = st.columns([3, 3, 2, 1, 1])
        with col1:
            st.write(m["name"])
        with col2:
            st.write(m["email"])
        with col3:
            st.write(m["telefon"])
        with col4:
            st.write(str(m["akten"]))
        with col5:
            st.button("📝", key=f"edit_m_{m['name']}")
    
    st.divider()
    
    # Neuer Mandant
    with st.expander("➕ Neuen Mandanten anlegen"):
        with st.form("neuer_mandant"):
            col1, col2 = st.columns(2)
            
            with col1:
                anrede = st.selectbox("Anrede", ["Herr", "Frau", "Firma"])
                vorname = st.text_input("Vorname")
                nachname = st.text_input("Nachname")
            
            with col2:
                email = st.text_input("E-Mail", key="nm_email")
                telefon = st.text_input("Telefon", key="nm_tel")
                mobil = st.text_input("Mobil")
            
            strasse = st.text_input("Straße/Nr.")
            col1, col2 = st.columns(2)
            with col1:
                plz = st.text_input("PLZ")
            with col2:
                ort = st.text_input("Ort")
            
            if st.form_submit_button("💾 Mandant speichern", type="primary"):
                st.success(f"✅ Mandant {vorname} {nachname} angelegt!")


def render_fristen():
    st.header("📅 Fristenübersicht")
    
    # Demo-Fristen
    heute = date.today()
    demo_fristen = [
        {"akte": "2024-001-KS", "frist": "Klagefrist", "datum": heute + timedelta(days=3), "prioritaet": "kritisch"},
        {"akte": "2024-002-Z", "frist": "Schriftsatzfrist", "datum": heute + timedelta(days=7), "prioritaet": "hoch"},
        {"akte": "2024-001-KS", "frist": "Verhandlungstermin", "datum": heute + timedelta(days=14), "prioritaet": "normal"},
        {"akte": "2024-003-L", "frist": "Stellungnahme", "datum": heute + timedelta(days=21), "prioritaet": "normal"},
        {"akte": "2024-002-Z", "frist": "Berufungsfrist", "datum": heute + timedelta(days=30), "prioritaet": "hoch"},
    ]
    
    # Sortieren nach Datum
    demo_fristen.sort(key=lambda x: x["datum"])
    
    # Kategorisierung
    kritisch = [f for f in demo_fristen if f["prioritaet"] == "kritisch" or (f["datum"] - heute).days <= 3]
    diese_woche = [f for f in demo_fristen if f not in kritisch and (f["datum"] - heute).days <= 7]
    spaeter = [f for f in demo_fristen if f not in kritisch and f not in diese_woche]
    
    # Anzeige
    if kritisch:
        st.error(f"🚨 **KRITISCH** - {len(kritisch)} Frist(en) in den nächsten 3 Tagen!")
        for f in kritisch:
            tage = (f["datum"] - heute).days
            st.markdown(f"- **{f['akte']}**: {f['frist']} - **{f['datum'].strftime('%d.%m.%Y')}** ({tage} Tage)")
    
    st.divider()
    
    if diese_woche:
        st.warning(f"⚠️ **Diese Woche** - {len(diese_woche)} Frist(en)")
        for f in diese_woche:
            tage = (f["datum"] - heute).days
            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
            with col1:
                st.write(f["akte"])
            with col2:
                st.write(f["frist"])
            with col3:
                st.write(f"{f['datum'].strftime('%d.%m.%Y')} ({tage}T)")
            with col4:
                st.checkbox("", key=f"done_{f['akte']}_{f['frist']}")
    
    st.divider()
    
    if spaeter:
        st.info(f"📅 **Später** - {len(spaeter)} Frist(en)")
        for f in spaeter:
            tage = (f["datum"] - heute).days
            col1, col2, col3, col4 = st.columns([2, 3, 2, 1])
            with col1:
                st.write(f["akte"])
            with col2:
                st.write(f["frist"])
            with col3:
                st.write(f"{f['datum'].strftime('%d.%m.%Y')} ({tage}T)")
            with col4:
                st.checkbox("", key=f"done_s_{f['akte']}_{f['frist']}")
    
    # Neue Frist
    st.divider()
    with st.expander("➕ Neue Frist eintragen"):
        with st.form("neue_frist"):
            col1, col2 = st.columns(2)
            
            with col1:
                frist_akte = st.selectbox("Akte", ["2024-001-KS", "2024-002-Z", "2024-003-L"])
                frist_bezeichnung = st.text_input("Bezeichnung")
            
            with col2:
                frist_datum = st.date_input("Fristdatum", value=heute + timedelta(days=14))
                frist_vorfrist = st.date_input("Vorfrist", value=heute + timedelta(days=7))
            
            frist_prioritaet = st.select_slider("Priorität", 
                                                 options=["niedrig", "normal", "hoch", "kritisch"],
                                                 value="normal")
            
            if st.form_submit_button("💾 Frist speichern", type="primary"):
                st.success("✅ Frist eingetragen!")


def render_dashboard():
    st.header("📊 Dashboard")
    
    # KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Aktive Akten", "23", delta="+3")
    
    with col2:
        st.metric("Mandanten", "18", delta="+2")
    
    with col3:
        st.metric("Offene Fristen", "7", delta="-2")
    
    with col4:
        st.metric("Überfällig", "1", delta="0")
    
    st.divider()
    
    # Charts (vereinfacht ohne Plotly)
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Akten nach Sachgebiet")
        sachgebiete = {
            "Kündigungsschutz": 12,
            "Zeugnis": 5,
            "Lohn/Gehalt": 4,
            "Abfindung": 2,
            "Sonstiges": 0
        }
        for sg, anzahl in sachgebiete.items():
            st.progress(anzahl / 15, text=f"{sg}: {anzahl}")
    
    with col2:
        st.subheader("📈 Akten pro Monat")
        monate = {
            "Jan": 5,
            "Feb": 3,
            "Mär": 7,
            "Apr": 4,
            "Mai": 2,
            "Jun": 2
        }
        for monat, anzahl in monate.items():
            st.progress(anzahl / 10, text=f"{monat}: {anzahl}")
    
    st.divider()
    
    # Zeiterfassung
    st.subheader("⏱️ Zeiterfassung diese Woche")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Erfasste Stunden", "32,5 h")
        st.metric("Abrechenbare Stunden", "28,0 h")
    
    with col2:
        st.metric("Ø pro Tag", "6,5 h")
        st.metric("Honorar (geschätzt)", "5.600 €")


if __name__ == "__main__":
    render()
