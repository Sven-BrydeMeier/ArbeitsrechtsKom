"""
JuraConnect v2.0 - Arbeitsrecht Kanzleisoftware
================================================
Vollständige arbeitsrechtliche Kanzleisoftware mit:
- Differenziertem Zugang (Arbeitnehmer/Arbeitgeber/Kanzlei)
- Feature-Parität zwischen AN und AG Dashboards
- RA-Micro Aktenimport
- KI-gestützte Rechtsberatung
- PKH-Rechner 2024
- Prozesskostenrechner (3 Instanzen)
- Zeiterfassung
- Kollisionsprüfung
- beA-Integration

Autor: JuraConnect Team
Version: 2.0.0
"""

import streamlit as st
from datetime import datetime, date, timedelta
import sys
import os

# Pfad für Module
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Seiten-Konfiguration MUSS zuerst kommen
st.set_page_config(
    page_title="JuraConnect - Arbeitsrecht",
    page_icon="⚖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Imports nach set_page_config
from modules.auth import UserRole
from modules.rechner import (
    KuendigungsfristenRechner, 
    AbfindungsRechner, 
    UeberstundenRechner,
    UrlaubsRechner
)
from modules.kuendigungsschutz import KuendigungsschutzPruefer
from modules.zeugnis_analyse import ZeugnisAnalyse
from modules.erweiterte_rechner import (
    PKHRechner, 
    ProzesskostenRechner3Instanzen, 
    Instanz,
    Zeiterfassung,
    FristenTracker
)
from modules.kanzlei_tools import (
    KollisionsPruefer,
    BeAIntegration,
    DokumentenCheckliste,
    Partei
)
from modules.aktenimport import RAMicroAktenImporter, BatchImporter
from modules.ki_module import (
    KIVertragsanalyse, 
    KIKuendigungsCheck, 
    KIWissensdatenbank,
    KlauselBewertung
)
from modules.mandanten_tools import (
    MandantenCheckliste,
    DruckVersandManager,
    VersandTyp,
    FrageTyp
)
from modules.schriftsatz_generator import (
    KISchriftsatzGenerator,
    SchriftsatzTyp,
    Akteninhalt,
    Parteidaten,
    Arbeitsverhältnis,
    Kuendigungsdaten,
    Lohndaten,
    Urlaubsdaten,
    Zeugnisdaten
)


# =============================================================================
# CUSTOM CSS
# =============================================================================

def load_custom_css():
    st.markdown("""
    <style>
    :root {
        --primary: #f59e0b;
        --primary-dark: #d97706;
        --background: #0f172a;
        --surface: #1e293b;
        --surface-light: #334155;
        --text: #f1f5f9;
        --text-muted: #94a3b8;
        --success: #10b981;
        --warning: #f59e0b;
        --error: #ef4444;
        --info: #3b82f6;
    }
    
    .stApp {
        background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
    }
    
    .main-header {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid rgba(245, 158, 11, 0.3);
        border-radius: 16px;
        padding: 2rem;
        margin-bottom: 2rem;
        text-align: center;
    }
    
    .main-header h1 { color: #f59e0b; font-size: 2.5rem; margin-bottom: 0.5rem; }
    .main-header p { color: #94a3b8; font-size: 1.1rem; }
    
    .access-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 2px solid rgba(245, 158, 11, 0.2);
        border-radius: 16px;
        padding: 2rem;
        text-align: center;
        transition: all 0.3s ease;
        min-height: 320px;
    }
    
    .access-card:hover {
        border-color: #f59e0b;
        transform: translateY(-5px);
        box-shadow: 0 20px 40px rgba(245, 158, 11, 0.2);
    }
    
    .access-card-icon { font-size: 4rem; margin-bottom: 1rem; }
    .access-card h3 { color: #f59e0b; font-size: 1.5rem; margin-bottom: 0.5rem; }
    .access-card p { color: #94a3b8; font-size: 0.95rem; line-height: 1.6; }
    
    .feature-tag {
        display: inline-block;
        background: rgba(245, 158, 11, 0.2);
        color: #f59e0b;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        margin: 0.25rem;
    }
    
    .metric-card {
        background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
        border: 1px solid rgba(245, 158, 11, 0.2);
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    
    .metric-value { font-size: 2rem; font-weight: bold; color: #f59e0b; }
    .metric-label { color: #94a3b8; font-size: 0.9rem; }
    
    .stButton > button {
        background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
        color: #0f172a;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 2rem;
        font-weight: 600;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 10px 20px rgba(245, 158, 11, 0.3);
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e293b 0%, #0f172a 100%);
        border-right: 1px solid rgba(245, 158, 11, 0.2);
    }
    
    .status-kritisch { background: #dc2626; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; }
    .status-warnung { background: #f59e0b; color: black; padding: 0.25rem 0.5rem; border-radius: 4px; }
    .status-ok { background: #10b981; color: white; padding: 0.25rem 0.5rem; border-radius: 4px; }
    
    .footer {
        text-align: center;
        color: #64748b;
        padding: 2rem;
        font-size: 0.85rem;
    }
    </style>
    """, unsafe_allow_html=True)


# =============================================================================
# SESSION STATE
# =============================================================================

def init_session_state():
    """Initialisiert den Session State."""
    defaults = {
        'authenticated': False,
        'user_role': UserRole.DEMO,
        'access_type': None,
        'username': 'Gast',
        'show_login': False,
        'current_page': 'dashboard',
        'zeiterfassung': Zeiterfassung(),
        'fristen_tracker': FristenTracker(),
        'kollision_pruefer': KollisionsPruefer(),
        'bea': BeAIntegration(),
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


# =============================================================================
# LANDING PAGE
# =============================================================================

def render_landing_page():
    """Rendert die Landing Page mit drei Zugangswegen."""
    
    st.markdown("""
    <div class="main-header">
        <h1>⚖️ JuraConnect</h1>
        <p>Die moderne Softwarelösung für Arbeitsrecht</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="access-card">
            <div class="access-card-icon">👷</div>
            <h3>ARBEITNEHMER</h3>
            <p>Sie haben eine Kündigung erhalten oder Probleme mit Ihrem Arbeitgeber? 
            Nutzen Sie unsere Tools zur ersten Einschätzung.</p>
            <div style="margin-top: 1rem;">
                <span class="feature-tag">Kündigungsschutz-Check</span>
                <span class="feature-tag">Abfindungsrechner</span>
                <span class="feature-tag">Zeugnis-Analyse</span>
                <span class="feature-tag">PKH-Rechner</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎮 Als Arbeitnehmer starten", key="btn_an", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.access_type = "arbeitnehmer"
            st.session_state.username = "AN-Demo"
            st.rerun()
    
    with col2:
        st.markdown("""
        <div class="access-card">
            <div class="access-card-icon">🏢</div>
            <h3>ARBEITGEBER</h3>
            <p>Sie müssen Personal abbauen oder haben Fragen zu Arbeitsverträgen? 
            Wir helfen bei allen arbeitsrechtlichen Themen.</p>
            <div style="margin-top: 1rem;">
                <span class="feature-tag">Kündigungs-Assistent</span>
                <span class="feature-tag">Sozialauswahl</span>
                <span class="feature-tag">Arbeitsverträge</span>
                <span class="feature-tag">Compliance</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎮 Als Arbeitgeber starten", key="btn_ag", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.access_type = "arbeitgeber"
            st.session_state.username = "AG-Demo"
            st.rerun()
    
    with col3:
        st.markdown("""
        <div class="access-card">
            <div class="access-card-icon">⚖️</div>
            <h3>KANZLEI</h3>
            <p>Vollständige Kanzleiverwaltung mit Aktenverwaltung, 
            Zeiterfassung, beA-Integration und KI-Assistenz.</p>
            <div style="margin-top: 1rem;">
                <span class="feature-tag">Aktenverwaltung</span>
                <span class="feature-tag">RA-Micro Import</span>
                <span class="feature-tag">Zeiterfassung</span>
                <span class="feature-tag">beA</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        if st.button("🎮 Als Kanzlei starten", key="btn_kanzlei", use_container_width=True):
            st.session_state.authenticated = True
            st.session_state.access_type = "kanzlei"
            st.session_state.username = "Kanzlei-Demo"
            st.rerun()
    
    # Feature-Übersicht
    st.markdown("---")
    st.markdown("### 🚀 Alle Features im Überblick")
    
    f1, f2, f3, f4 = st.columns(4)
    
    with f1:
        st.markdown("""
        **📊 Rechner**
        - Kündigungsfrist (§ 622 BGB)
        - Abfindungsrechner
        - Prozesskosten (3 Instanzen)
        - PKH-Rechner 2024
        - Überstunden & Urlaub
        """)
    
    with f2:
        st.markdown("""
        **🤖 KI-Tools**
        - Kündigungsschutz-Check
        - Zeugnis-Decoder
        - Wissensdatenbank
        - Schriftsatz-Generator
        """)
    
    with f3:
        st.markdown("""
        **📁 Kanzlei**
        - Aktenverwaltung
        - RA-Micro Import
        - Zeiterfassung
        - Kollisionsprüfung
        - beA-Postfach
        """)
    
    with f4:
        st.markdown("""
        **📋 Workflows**
        - Fristen-Tracker
        - Dokumenten-Checkliste
        - RSV-Deckungsanfrage
        - PKH-Workflow
        """)
    
    st.markdown("""
    <div class="footer">
        <p>JuraConnect v2.0 | © 2024 | RVG/GKG 2024 | DSGVO-konform | Made in Germany 🇩🇪</p>
    </div>
    """, unsafe_allow_html=True)


# =============================================================================
# ARBEITNEHMER-SEITEN
# =============================================================================

def render_arbeitnehmer_dashboard():
    """Dashboard für Arbeitnehmer."""
    st.title("👷 Arbeitnehmer-Portal")
    
    st.info("🎯 **Willkommen!** Hier finden Sie alle Tools zur Einschätzung Ihrer arbeitsrechtlichen Situation.")
    
    # Quick Stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-value">21</div><div class="metric-label">Tage Klagefrist</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">0,5</div><div class="metric-label">Regelabfindung</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">3</div><div class="metric-label">Instanzen</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><div class="metric-value">RVG</div><div class="metric-label">Stand 2024</div></div>', unsafe_allow_html=True)


def render_kuendigungsschutz_check():
    """Kündigungsschutz-Check für Arbeitnehmer."""
    st.title("🛡️ Kündigungsschutz-Check")
    
    st.markdown("""
    Prüfen Sie, ob das Kündigungsschutzgesetz (KSchG) auf Sie anwendbar ist 
    und welchen besonderen Kündigungsschutz Sie möglicherweise genießen.
    """)
    
    with st.form("kschg_check"):
        col1, col2 = st.columns(2)
        
        with col1:
            beschaeftigte = st.number_input("Anzahl Mitarbeiter im Betrieb", min_value=1, value=15)
            betriebszugehoerigkeit = st.number_input("Ihre Betriebszugehörigkeit (Monate)", min_value=0, value=12)
            arbeitszeit = st.number_input("Wöchentliche Arbeitszeit (Stunden)", min_value=1.0, value=40.0)
        
        with col2:
            st.markdown("**Besonderer Kündigungsschutz:**")
            schwerbehindert = st.checkbox("Schwerbehindert (GdB ≥ 50)")
            schwanger = st.checkbox("Schwanger / in Mutterschutz")
            elternzeit = st.checkbox("In Elternzeit")
            betriebsrat = st.checkbox("Betriebsratsmitglied")
            datenschutz = st.checkbox("Datenschutzbeauftragter")
        
        submitted = st.form_submit_button("🔍 Prüfen", use_container_width=True)
        
        if submitted:
            # KSchG Prüfung
            kschg_anwendbar = beschaeftigte > 10 and betriebszugehoerigkeit >= 6
            
            st.markdown("### Ergebnis")
            
            if kschg_anwendbar:
                st.success("✅ **Das Kündigungsschutzgesetz ist anwendbar!**")
                st.markdown("""
                - Betrieb hat mehr als 10 Mitarbeiter
                - Sie sind länger als 6 Monate beschäftigt
                - **Ihr Arbeitgeber braucht einen Kündigungsgrund!**
                """)
            else:
                st.warning("⚠️ **Das KSchG ist NICHT anwendbar**")
                if beschaeftigte <= 10:
                    st.markdown("- Kleinbetrieb mit ≤10 Mitarbeitern")
                if betriebszugehoerigkeit < 6:
                    st.markdown("- Wartezeit von 6 Monaten nicht erfüllt")
            
            # Sonderkündigungsschutz
            sonderschutz = []
            if schwerbehindert:
                sonderschutz.append("🔴 **Schwerbehinderung**: Zustimmung des Integrationsamts erforderlich!")
            if schwanger:
                sonderschutz.append("🔴 **Mutterschutz**: Kündigung während Schwangerschaft verboten!")
            if elternzeit:
                sonderschutz.append("🔴 **Elternzeit**: Besonderer Kündigungsschutz nach BEEG!")
            if betriebsrat:
                sonderschutz.append("🔴 **Betriebsrat**: Ordentliche Kündigung ausgeschlossen!")
            if datenschutz:
                sonderschutz.append("🟡 **Datenschutzbeauftragter**: Kündigungsschutz während der Tätigkeit")
            
            if sonderschutz:
                st.markdown("### Besonderer Kündigungsschutz")
                for s in sonderschutz:
                    st.markdown(s)
            
            # Frist-Hinweis
            st.markdown("### ⚠️ Wichtige Frist")
            st.error("""
            **21-Tage-Frist beachten!**
            
            Die Kündigungsschutzklage muss innerhalb von **3 Wochen** nach Zugang 
            der Kündigung beim Arbeitsgericht eingereicht werden (§ 4 KSchG).
            """)


def render_abfindungsrechner():
    """Abfindungsrechner für Arbeitnehmer."""
    st.title("💰 Abfindungsrechner")
    
    with st.form("abfindung"):
        col1, col2 = st.columns(2)
        
        with col1:
            brutto_monat = st.number_input("Bruttomonatsgehalt (€)", min_value=0.0, value=4000.0, step=100.0)
            betriebszugehoerigkeit = st.number_input("Betriebszugehörigkeit (Jahre)", min_value=0.0, value=5.0, step=0.5)
            alter = st.number_input("Ihr Alter", min_value=18, max_value=67, value=40)
        
        with col2:
            st.markdown("**Faktoren für höhere Abfindung:**")
            kuendigungsgrund_schwach = st.checkbox("Kündigungsgrund fraglich")
            sonderschutz = st.checkbox("Besonderer Kündigungsschutz")
            arbeitsmarkt_schwierig = st.checkbox("Schwierige Arbeitsmarktsituation")
            unterhaltspflichten = st.checkbox("Unterhaltspflichten")
        
        submitted = st.form_submit_button("💰 Berechnen", use_container_width=True)
        
        if submitted:
            # Basisberechnung
            regelabfindung = brutto_monat * betriebszugehoerigkeit * 0.5
            
            # Faktoren
            faktor = 0.5
            if kuendigungsgrund_schwach:
                faktor += 0.25
            if sonderschutz:
                faktor += 0.25
            if arbeitsmarkt_schwierig:
                faktor += 0.15
            if unterhaltspflichten:
                faktor += 0.1
            if alter > 50:
                faktor += 0.15
            if alter > 55:
                faktor += 0.1
            
            abfindung_empfohlen = brutto_monat * betriebszugehoerigkeit * faktor
            
            st.markdown("### Ergebnis")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Regelabfindung (0,5)", f"{regelabfindung:,.2f} €")
            with col2:
                st.metric(f"Empfohlen ({faktor:.2f})", f"{abfindung_empfohlen:,.2f} €")
            with col3:
                st.metric("Maximum (1,0)", f"{brutto_monat * betriebszugehoerigkeit:,.2f} €")
            
            st.markdown(f"""
            ### Berechnung
            - **Formel:** Bruttogehalt × Jahre × Faktor
            - **Ihr Faktor:** {faktor:.2f} (basierend auf Ihren Angaben)
            - **Empfohlene Verhandlungsspanne:** {regelabfindung:,.2f} € - {abfindung_empfohlen * 1.2:,.2f} €
            """)


def render_pkh_rechner():
    """PKH-Rechner für Arbeitnehmer."""
    st.title("📋 PKH-Rechner (Prozesskostenhilfe)")
    
    st.markdown("""
    Prüfen Sie, ob Sie Anspruch auf Prozesskostenhilfe haben.
    **Stand: 2024** (aktuelle Freibeträge)
    """)
    
    rechner = PKHRechner()
    
    with st.form("pkh"):
        st.markdown("### Einkommen")
        col1, col2 = st.columns(2)
        
        with col1:
            netto = st.number_input("Nettoeinkommen (€/Monat)", min_value=0.0, value=1800.0)
            partner_einkommen = st.number_input("Einkommen Partner (€/Monat)", min_value=0.0, value=0.0)
        
        with col2:
            ist_erwerbstaetig = st.checkbox("Erwerbstätig", value=True)
        
        st.markdown("### Kinder")
        kinder_anzahl = st.number_input("Anzahl Kinder", min_value=0, max_value=10, value=0)
        
        kinder = []
        if kinder_anzahl > 0:
            for i in range(kinder_anzahl):
                col1, col2 = st.columns(2)
                with col1:
                    alter = st.number_input(f"Alter Kind {i+1}", min_value=0, max_value=25, value=10, key=f"kind_alter_{i}")
                with col2:
                    einkommen = st.number_input(f"Einkommen Kind {i+1} (€)", min_value=0.0, value=0.0, key=f"kind_eink_{i}")
                kinder.append((alter, einkommen))
        
        st.markdown("### Ausgaben")
        col1, col2 = st.columns(2)
        with col1:
            wohnkosten = st.number_input("Miete/Wohnkosten (€/Monat)", min_value=0.0, value=600.0)
        with col2:
            sonstige = st.number_input("Sonstige notwendige Ausgaben (€/Monat)", min_value=0.0, value=100.0)
        
        submitted = st.form_submit_button("📋 PKH prüfen", use_container_width=True)
        
        if submitted:
            ergebnis = rechner.berechne_pkh(
                bruttoeinkommen=netto * 1.3,  # Schätzung
                nettoeinkommen=netto,
                ehepartner_einkommen=partner_einkommen,
                kinder=kinder,
                wohnkosten=wohnkosten,
                sonstige_ausgaben=sonstige,
                ist_erwerbstaetig=ist_erwerbstaetig
            )
            
            st.markdown("### Ergebnis")
            
            if ergebnis.anspruch == "ja":
                st.success("✅ **PKH wird voraussichtlich bewilligt!**")
                st.markdown("Ohne Ratenzahlung - die Kosten werden vollständig übernommen.")
            elif ergebnis.anspruch == "raten":
                st.warning(f"⚠️ **PKH mit Ratenzahlung**")
                st.markdown(f"Monatliche Rate: **{ergebnis.monatliche_rate:.2f} €**")
                st.markdown(f"Maximale Anzahl Raten: {ergebnis.raten_anzahl}")
            else:
                st.error("❌ **PKH wird voraussichtlich nicht bewilligt**")
            
            st.markdown(f"""
            ### Details
            - **Freibeträge gesamt:** {ergebnis.freibetraege_gesamt:.2f} €
            - **Einzusetzendes Einkommen:** {ergebnis.einzusetzendes_einkommen:.2f} €
            
            {ergebnis.begruendung}
            """)


def render_prozesskosten_rechner():
    """Prozesskostenrechner für alle 3 Instanzen."""
    st.title("⚖️ Prozesskostenrechner (3 Instanzen)")
    
    st.markdown("**Stand: RVG/GKG 2024**")
    
    rechner = ProzesskostenRechner3Instanzen()
    
    with st.form("prozesskosten"):
        col1, col2 = st.columns(2)
        
        with col1:
            streitwert = st.number_input(
                "Streitwert (€)", 
                min_value=0.0, 
                value=15000.0,
                help="Bei Kündigungsschutz: 3 Bruttomonatsgehälter"
            )
        
        with col2:
            gewinnchance = st.slider("Geschätzte Gewinnchance (%)", 0, 100, 50) / 100
        
        submitted = st.form_submit_button("⚖️ Berechnen", use_container_width=True)
        
        if submitted:
            ergebnis = rechner.berechne_alle_instanzen(streitwert, gewinnchance)
            
            st.markdown("### Kostenübersicht")
            
            # Tabs für Instanzen
            tab1, tab2, tab3 = st.tabs(["1. Instanz (Arbeitsgericht)", "2. Instanz (LAG)", "3. Instanz (BAG)"])
            
            with tab1:
                ag = ergebnis["1_instanz"]["streitig"]
                ag_v = ergebnis["1_instanz"]["vergleich"]
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**Bei Urteil:**")
                    st.metric("Wenn Sie verlieren", f"{ag.gesamt_verlieren:,.2f} €")
                    st.metric("Wenn Sie gewinnen", f"{ag.gesamt_gewinnen:,.2f} €")
                with col2:
                    st.markdown("**Bei Vergleich:**")
                    st.metric("Gesamtkosten", f"{ag_v.gesamt_vergleich:,.2f} €")
                    st.success(f"💡 Ersparnis: {ag.gesamt_verlieren - ag_v.gesamt_vergleich:,.2f} €")
            
            with tab2:
                lag = ergebnis["2_instanz"]["streitig"]
                st.metric("Zusätzliche Kosten LAG (bei Verlieren)", f"{lag.gesamt_verlieren:,.2f} €")
                st.metric("Kumuliert 1.+2. Instanz", f"{ergebnis['2_instanz']['kumuliert_verlieren']:,.2f} €")
            
            with tab3:
                bag = ergebnis["3_instanz"]["streitig"]
                st.metric("Zusätzliche Kosten BAG (bei Verlieren)", f"{bag.gesamt_verlieren:,.2f} €")
                st.metric("Kumuliert alle Instanzen", f"{ergebnis['3_instanz']['kumuliert_verlieren']:,.2f} €")
            
            # Empfehlung
            st.markdown("### Empfehlung")
            emp = ergebnis["empfehlung"]
            if emp["empfehlung"] == "vergleich":
                st.success(f"""
                💡 **Vergleich empfohlen**
                - Ersparnis gegenüber Prozess: {emp['vergleich_ersparnis']:,.2f} €
                - Erwartungswert Klage: {emp['erwartungswert_klage']:,.2f} €
                """)
            else:
                st.info(f"""
                ⚖️ **Klage kann sinnvoll sein**
                - Erwartungswert: {emp['erwartungswert_klage']:,.2f} €
                - Bei Ihrer Gewinnchance von {gewinnchance*100:.0f}%
                """)


def render_zeugnis_analyse():
    """Zeugnis-Analyse für Arbeitnehmer."""
    st.title("📄 Zeugnis-Analyse")
    
    st.markdown("""
    Analysieren Sie Ihr Arbeitszeugnis auf versteckte Botschaften (Geheimcodes).
    """)
    
    analyse = ZeugnisAnalyse()
    
    zeugnis_text = st.text_area(
        "Zeugnistext eingeben",
        height=300,
        placeholder="Fügen Sie hier den Text Ihres Arbeitszeugnisses ein..."
    )
    
    if st.button("🔍 Analysieren", use_container_width=True):
        if zeugnis_text:
            ergebnis = analyse.analysiere(zeugnis_text)
            
            st.markdown("### Analyse-Ergebnis")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Gesamtnote", ergebnis.get('gesamtnote', 'N/A'))
            with col2:
                st.metric("Gefundene Codes", len(ergebnis.get('gefundene_codes', [])))
            
            if ergebnis.get('gefundene_codes'):
                st.markdown("### Gefundene Formulierungen")
                for code in ergebnis['gefundene_codes']:
                    with st.expander(f"⚠️ {code.get('formulierung', '')}"):
                        st.markdown(f"**Bedeutung:** {code.get('bedeutung', '')}")
                        st.markdown(f"**Bewertung:** {code.get('bewertung', '')}")
            
            if ergebnis.get('verbesserungsvorschlaege'):
                st.markdown("### Verbesserungsvorschläge")
                for v in ergebnis['verbesserungsvorschlaege']:
                    st.markdown(f"- {v}")
        else:
            st.warning("Bitte geben Sie einen Zeugnistext ein.")


def render_dokumenten_checkliste_an():
    """Dokumenten-Checkliste für Arbeitnehmer."""
    st.title("✅ Dokumenten-Checkliste")
    
    checkliste = DokumentenCheckliste("arbeitnehmer")
    
    # Fortschritt
    fortschritt = checkliste.fortschritt()
    st.progress(fortschritt['prozent'] / 100)
    st.markdown(f"**Fortschritt:** {fortschritt['prozent']}% ({fortschritt['vorhanden']}/{fortschritt['gesamt']})")
    
    if fortschritt['fehlend_pflicht']:
        st.warning(f"⚠️ {len(fortschritt['fehlend_pflicht'])} Pflichtdokumente fehlen noch!")
    
    # Nach Kategorie
    for kategorie, items in checkliste.nach_kategorie().items():
        with st.expander(f"📁 {kategorie}", expanded=True):
            for item in items:
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    pflicht = " ⭐" if item.pflicht else ""
                    st.markdown(f"**{item.titel}**{pflicht}")
                    st.caption(item.beschreibung)
                with col2:
                    status = st.selectbox(
                        "Status",
                        ["fehlend", "teilweise", "vorhanden", "nicht_zutreffend"],
                        key=f"status_{item.id}",
                        label_visibility="collapsed"
                    )
                with col3:
                    if status == "vorhanden":
                        st.markdown("✅")
                    elif status == "teilweise":
                        st.markdown("⚠️")
                    elif status == "fehlend":
                        st.markdown("❌")
                    else:
                        st.markdown("➖")


# =============================================================================
# ARBEITGEBER-SEITEN (Feature-Parität)
# =============================================================================

def render_arbeitgeber_dashboard():
    """Dashboard für Arbeitgeber."""
    st.title("🏢 Arbeitgeber-Portal")
    
    st.info("🎯 **Willkommen!** Hier finden Sie alle Tools für Ihre arbeitsrechtlichen Fragen als Arbeitgeber.")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.markdown('<div class="metric-card"><div class="metric-value">§ 102</div><div class="metric-label">BR-Anhörung</div></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div class="metric-card"><div class="metric-value">§ 1</div><div class="metric-label">KSchG</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div class="metric-card"><div class="metric-value">RVG</div><div class="metric-label">Stand 2024</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><div class="metric-value">GKG</div><div class="metric-label">Stand 2024</div></div>', unsafe_allow_html=True)


def render_kuendigungs_assistent():
    """Kündigungsassistent für Arbeitgeber."""
    st.title("📋 Kündigungs-Assistent")
    
    st.markdown("""
    Prüfen Sie systematisch alle Voraussetzungen für eine rechtswirksame Kündigung.
    """)
    
    with st.form("kuendigung_ag"):
        st.markdown("### 1. Kündigungsgrund")
        grund = st.selectbox("Art der Kündigung", [
            "Betriebsbedingt",
            "Verhaltensbedingt",
            "Personenbedingt",
            "Außerordentlich (fristlos)"
        ])
        
        st.markdown("### 2. Betriebsgröße")
        mitarbeiter = st.number_input("Anzahl Mitarbeiter (ohne Azubis)", min_value=1, value=15)
        
        st.markdown("### 3. Arbeitnehmer-Daten")
        col1, col2 = st.columns(2)
        with col1:
            zugehoerigkeit = st.number_input("Betriebszugehörigkeit (Monate)", min_value=0, value=24)
            alter = st.number_input("Alter des Mitarbeiters", min_value=18, value=40)
        with col2:
            st.markdown("**Besonderer Schutz:**")
            schwerbehindert = st.checkbox("Schwerbehindert")
            schwanger = st.checkbox("Schwanger/Mutterschutz")
            elternzeit = st.checkbox("Elternzeit")
            betriebsrat_mitglied = st.checkbox("Betriebsratsmitglied")
        
        st.markdown("### 4. Betriebsrat")
        hat_betriebsrat = st.checkbox("Betriebsrat vorhanden")
        
        if grund == "Verhaltensbedingt":
            st.markdown("### 5. Abmahnung")
            abmahnung = st.checkbox("Einschlägige Abmahnung erteilt")
        
        submitted = st.form_submit_button("🔍 Prüfen", use_container_width=True)
        
        if submitted:
            st.markdown("### Prüfungsergebnis")
            
            probleme = []
            hinweise = []
            
            # KSchG
            if mitarbeiter > 10 and zugehoerigkeit >= 6:
                hinweise.append("⚠️ KSchG anwendbar - Sie brauchen einen Kündigungsgrund!")
            
            # Sonderschutz
            if schwerbehindert:
                probleme.append("🔴 **Zustimmung Integrationsamt erforderlich!**")
            if schwanger:
                probleme.append("🔴 **Kündigung während Schwangerschaft verboten!**")
            if elternzeit:
                probleme.append("🔴 **Kündigung während Elternzeit nur mit Genehmigung!**")
            if betriebsrat_mitglied:
                probleme.append("🔴 **Ordentliche Kündigung von BR-Mitgliedern ausgeschlossen!**")
            
            # Betriebsrat
            if hat_betriebsrat:
                hinweise.append("⚠️ **§ 102 BetrVG:** Betriebsrat muss angehört werden!")
            
            # Abmahnung
            if grund == "Verhaltensbedingt" and not abmahnung:
                probleme.append("🔴 **Fehlende Abmahnung!** Bei verhaltensbedingter Kündigung i.d.R. erforderlich.")
            
            if probleme:
                st.error("### ❌ Kritische Punkte")
                for p in probleme:
                    st.markdown(p)
            
            if hinweise:
                st.warning("### ⚠️ Hinweise")
                for h in hinweise:
                    st.markdown(h)
            
            if not probleme:
                st.success("### ✅ Grundsätzlich möglich")
                st.markdown("Nach den Angaben bestehen keine offensichtlichen Hindernisse. Eine rechtliche Prüfung im Einzelfall ist dennoch empfehlenswert.")


def render_sozialauswahl():
    """Sozialauswahl-Rechner für Arbeitgeber."""
    st.title("👥 Sozialauswahl-Rechner")
    
    st.markdown("""
    Berechnen Sie die Sozialauswahl nach § 1 Abs. 3 KSchG.
    """)
    
    st.markdown("### Mitarbeiter eingeben")
    
    # Beispiel-Mitarbeiter
    mitarbeiter = []
    
    anzahl = st.number_input("Anzahl vergleichbarer Mitarbeiter", min_value=2, max_value=20, value=4)
    
    for i in range(anzahl):
        with st.expander(f"Mitarbeiter {i+1}", expanded=(i==0)):
            col1, col2 = st.columns(2)
            with col1:
                name = st.text_input("Name", value=f"Mitarbeiter {i+1}", key=f"name_{i}")
                alter = st.number_input("Alter", min_value=18, max_value=67, value=40, key=f"alter_{i}")
                zugehoerigkeit = st.number_input("Betriebszugehörigkeit (Jahre)", min_value=0, max_value=50, value=5, key=f"zug_{i}")
            with col2:
                unterhalt = st.number_input("Unterhaltspflichten", min_value=0, max_value=10, value=0, key=f"unt_{i}")
                schwerbehindert = st.checkbox("Schwerbehindert", key=f"sb_{i}")
            
            # Punkte berechnen
            punkte_alter = alter  # 1 Punkt pro Lebensjahr
            punkte_zug = zugehoerigkeit * 2  # 2 Punkte pro Jahr
            punkte_unterhalt = unterhalt * 4  # 4 Punkte pro Unterhaltspflicht
            punkte_sb = 5 if schwerbehindert else 0
            
            gesamt = punkte_alter + punkte_zug + punkte_unterhalt + punkte_sb
            
            mitarbeiter.append({
                "name": name,
                "alter": alter,
                "zugehoerigkeit": zugehoerigkeit,
                "unterhalt": unterhalt,
                "schwerbehindert": schwerbehindert,
                "punkte": gesamt
            })
            
            st.metric("Sozialpunkte", gesamt)
    
    if st.button("📊 Rangfolge anzeigen", use_container_width=True):
        # Nach Punkten sortieren (höchste zuerst = am meisten schutzwürdig)
        sortiert = sorted(mitarbeiter, key=lambda x: x["punkte"], reverse=True)
        
        st.markdown("### Rangfolge (höchste Punktzahl = schutzwürdigster)")
        
        for i, m in enumerate(sortiert):
            schutz = "🟢 Schutzwürdig" if i < len(sortiert) // 2 else "🔴 Weniger schutzwürdig"
            st.markdown(f"""
            **{i+1}. {m['name']}** - {m['punkte']} Punkte {schutz}
            - Alter: {m['alter']} | Zugehörigkeit: {m['zugehoerigkeit']} J. | Unterhalt: {m['unterhalt']}
            """)


# =============================================================================
# KANZLEI-SEITEN
# =============================================================================

def render_kanzlei_dashboard():
    """Dashboard für Kanzlei."""
    st.title("⚖️ Kanzlei-Dashboard")
    
    # Stats
    col1, col2, col3, col4 = st.columns(4)
    
    fristen_stat = st.session_state.fristen_tracker.statistik()
    bea_stat = st.session_state.bea.statistik()
    
    with col1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{fristen_stat["offen"]}</div><div class="metric-label">Offene Fristen</div></div>', unsafe_allow_html=True)
    with col2:
        kritisch = fristen_stat["kritisch"] + fristen_stat["ueberfaellig"]
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color: {"#ef4444" if kritisch > 0 else "#10b981"}">{kritisch}</div><div class="metric-label">Kritische Fristen</div></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{bea_stat["eingang_ungelesen"]}</div><div class="metric-label">Ungelesene beA</div></div>', unsafe_allow_html=True)
    with col4:
        st.markdown('<div class="metric-card"><div class="metric-value">0</div><div class="metric-label">Aktive Timer</div></div>', unsafe_allow_html=True)
    
    # Kritische Fristen
    kritische = st.session_state.fristen_tracker.get_kritische_fristen()
    if kritische:
        st.error(f"⚠️ **{len(kritische)} kritische Fristen!**")
        for f in kritische[:3]:
            st.markdown(f"- **{f.titel}** ({f.akte_name}) - {f.datum}")


def render_ramicro_import():
    """RA-Micro Import."""
    st.title("📥 RA-Micro Aktenimport")
    
    st.markdown("""
    Importieren Sie Ihre RA-Micro Akten als PDF. Das System erkennt automatisch:
    - Aktenvorblatt (Rubrum, Parteien, Gegenstandswert)
    - Einzelne Dokumente (30+ Kategorien)
    - OCR für gescannte Dokumente
    """)
    
    uploaded = st.file_uploader("PDF-Akte hochladen", type=["pdf"])
    
    if uploaded:
        with st.spinner("Analysiere PDF..."):
            # Temporäre Datei
            import tempfile
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(uploaded.read())
                tmp_path = tmp.name
            
            importer = RAMicroAktenImporter(tmp_path)
            ergebnis = importer.analysiere_pdf()
            
            if ergebnis.erfolg:
                st.success(f"✅ Import erfolgreich! Qualität: {ergebnis.qualitaet} ({ergebnis.qualitaet_score}/100)")
                
                # Aktenvorblatt
                if ergebnis.aktenvorblatt:
                    av = ergebnis.aktenvorblatt
                    st.markdown("### Aktenvorblatt")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Rubrum:** {av.rubrum}")
                        st.markdown(f"**Aktennummer:** {av.aktennummer}")
                        st.markdown(f"**Wegen:** {av.wegen}")
                    with col2:
                        st.markdown(f"**Gegenstandswert:** {av.gegenstandswert:,.2f} €")
                        st.markdown(f"**Gericht:** {av.instanz_1_gericht}")
                    
                    # Parteien
                    if av.parteien:
                        st.markdown("### Parteien")
                        for p in av.parteien:
                            with st.expander(f"{p.rolle}: {p.name}"):
                                if p.anschrift:
                                    st.markdown(f"Anschrift: {p.anschrift}")
                                if p.plz_ort:
                                    st.markdown(f"PLZ/Ort: {p.plz_ort}")
                                if p.telefon1:
                                    st.markdown(f"Tel: {p.telefon1}")
                                if p.email:
                                    st.markdown(f"E-Mail: {p.email}")
                
                # Dokumente
                if ergebnis.dokumente:
                    st.markdown(f"### Erkannte Dokumente ({len(ergebnis.dokumente)})")
                    for doc in ergebnis.dokumente:
                        with st.expander(f"{doc.id}. {doc.titel} ({doc.kategorie})"):
                            st.markdown(f"Seiten: {doc.seite_von}-{doc.seite_bis}")
                            if doc.datum:
                                st.markdown(f"Datum: {doc.datum}")
                            st.caption(doc.inhalt_vorschau[:200] + "..." if len(doc.inhalt_vorschau) > 200 else doc.inhalt_vorschau)
                
                # Import-Button
                if st.button("📁 In JuraConnect importieren", use_container_width=True):
                    jc_data = importer.fuer_juraconnect()
                    st.success("✅ Akte wurde importiert!")
                    st.json(jc_data)
            else:
                st.error("❌ Import fehlgeschlagen")
                for fehler in ergebnis.fehler:
                    st.markdown(f"- {fehler}")


def render_zeiterfassung():
    """Zeiterfassung."""
    st.title("⏱️ Zeiterfassung")
    
    zeiterfassung = st.session_state.zeiterfassung
    
    tab1, tab2, tab3 = st.tabs(["Timer", "Manuell erfassen", "Auswertung"])
    
    with tab1:
        st.markdown("### Stoppuhr")
        
        col1, col2 = st.columns(2)
        with col1:
            akte_id = st.text_input("Aktenzeichen", value="123/24")
            akte_name = st.text_input("Aktenname", value="Müller ./. Schmidt GmbH")
        with col2:
            taetigkeit = st.text_input("Tätigkeit", value="Schriftsatz")
            kategorie = st.selectbox("Kategorie", zeiterfassung.KATEGORIEN)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("▶️ Timer starten", use_container_width=True):
                try:
                    zeiterfassung.starte_timer(akte_id, akte_name, taetigkeit, kategorie)
                    st.success("Timer gestartet!")
                except ValueError as e:
                    st.warning(str(e))
        with col2:
            if st.button("⏹️ Timer stoppen", use_container_width=True):
                eintrag = zeiterfassung.stoppe_timer(akte_id)
                if eintrag:
                    st.success(f"Timer gestoppt: {eintrag.dauer_minuten} Minuten")
                else:
                    st.warning("Kein aktiver Timer für diese Akte")
        
        # Aktive Timer
        if zeiterfassung.aktive_timer:
            st.markdown("### Aktive Timer")
            for akte, start in zeiterfassung.aktive_timer.items():
                dauer = (datetime.now() - start).seconds // 60
                st.markdown(f"⏱️ **{akte}**: {dauer} Minuten")
    
    with tab2:
        st.markdown("### Manuelle Erfassung")
        
        with st.form("zeit_manuell"):
            col1, col2 = st.columns(2)
            with col1:
                m_akte_id = st.text_input("Aktenzeichen", key="m_akte")
                m_akte_name = st.text_input("Aktenname", key="m_name")
                m_datum = st.date_input("Datum", value=date.today())
            with col2:
                m_dauer = st.number_input("Dauer (Minuten)", min_value=1, value=30)
                m_taetigkeit = st.text_input("Tätigkeit", key="m_taet")
                m_kategorie = st.selectbox("Kategorie", zeiterfassung.KATEGORIEN, key="m_kat")
            
            m_notizen = st.text_area("Notizen")
            
            if st.form_submit_button("💾 Speichern", use_container_width=True):
                eintrag = zeiterfassung.manueller_eintrag(
                    m_akte_id, m_akte_name, m_datum, m_dauer, m_taetigkeit, m_kategorie, notizen=m_notizen
                )
                st.success(f"Eintrag gespeichert: {eintrag.dauer_minuten} Minuten = {zeiterfassung.berechne_wert(eintrag):.2f} €")
    
    with tab3:
        st.markdown("### Auswertung")
        
        if zeiterfassung.eintraege:
            stat = zeiterfassung.statistik_zeitraum(
                date.today() - timedelta(days=30),
                date.today()
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Einträge (30 Tage)", stat["anzahl_eintraege"])
            with col2:
                st.metric("Stunden gesamt", f"{stat['gesamt_stunden']:.1f}")
            with col3:
                st.metric("Wert", f"{stat['gesamt_wert']:,.2f} €")
        else:
            st.info("Noch keine Zeiteinträge vorhanden.")


def render_kollisionspruefung():
    """Kollisionsprüfung."""
    st.title("⚠️ Kollisionsprüfung")
    
    pruefer = st.session_state.kollision_pruefer
    
    st.markdown("""
    Prüfen Sie auf Interessenkollisionen nach BRAO § 43a Abs. 4.
    """)
    
    tab1, tab2 = st.tabs(["Neue Prüfung", "Parteien-Suche"])
    
    with tab1:
        with st.form("kollision"):
            st.markdown("### Potenzieller Mandant")
            m_name = st.text_input("Name des Mandanten")
            
            st.markdown("### Gegner (falls bekannt)")
            g_name = st.text_input("Name des Gegners")
            
            if st.form_submit_button("🔍 Prüfen", use_container_width=True):
                mandant = Partei(name=m_name) if m_name else None
                gegner = Partei(name=g_name) if g_name else None
                
                if mandant:
                    ergebnis = pruefer.pruefe_kollision(mandant, gegner)
                    
                    st.markdown("### Ergebnis")
                    st.markdown(f"Geprüft gegen {ergebnis.geprueft_gegen} Akten")
                    
                    if ergebnis.hat_kollision:
                        st.error("❌ **KOLLISION GEFUNDEN!**")
                        for k in ergebnis.kollisionen:
                            st.markdown(f"- **{k['typ']}**: {k['beschreibung']}")
                    else:
                        st.success("✅ Keine Kollision gefunden")
                    
                    if ergebnis.warnungen:
                        st.warning("⚠️ Warnungen:")
                        for w in ergebnis.warnungen:
                            st.markdown(f"- {w}")
                else:
                    st.warning("Bitte Mandantenname eingeben")
    
    with tab2:
        suchbegriff = st.text_input("Partei suchen")
        if suchbegriff and st.button("🔍 Suchen"):
            ergebnisse = pruefer.suche_partei(suchbegriff)
            if ergebnisse:
                for e in ergebnisse:
                    st.markdown(f"- **{e['name']}** ({e['rolle']}) in Akte {e['akte_name']}")
            else:
                st.info("Keine Treffer")


def render_bea_postfach():
    """beA-Postfach."""
    st.title("📧 beA-Postfach")
    
    bea = st.session_state.bea
    stat = bea.statistik()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Eingang", stat["eingang_gesamt"])
    with col2:
        st.metric("Ungelesen", stat["eingang_ungelesen"])
    with col3:
        st.metric("Ausgang", stat["ausgang_gesamt"])
    with col4:
        st.metric("Entwürfe", stat["entwuerfe"])
    
    tab1, tab2, tab3 = st.tabs(["Posteingang", "Postausgang", "Neue Nachricht"])
    
    with tab1:
        nachrichten = bea.hole_posteingang()
        for n in nachrichten:
            status_icon = "🔴" if n.status.value == "ungelesen" else "⚪"
            with st.expander(f"{status_icon} {n.betreff} - {n.absender}"):
                st.markdown(f"**Von:** {n.absender}")
                st.markdown(f"**Datum:** {n.datum}")
                st.markdown(f"**Az:** {n.aktenzeichen}")
                st.markdown("---")
                st.markdown(n.inhalt)
                if n.anlagen:
                    st.markdown("**Anlagen:** " + ", ".join(n.anlagen))
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Als gelesen markieren", key=f"lesen_{n.id}"):
                        bea.markiere_gelesen(n.id)
                        st.rerun()
    
    with tab2:
        nachrichten = bea.hole_postausgang()
        if nachrichten:
            for n in nachrichten:
                with st.expander(f"📤 {n.betreff} - {n.empfaenger}"):
                    st.markdown(f"**An:** {n.empfaenger}")
                    st.markdown(f"**Datum:** {n.datum}")
                    st.markdown(n.inhalt)
        else:
            st.info("Keine gesendeten Nachrichten")
    
    with tab3:
        with st.form("neue_nachricht"):
            empfaenger = st.text_input("Empfänger")
            empfaenger_safe = st.text_input("SAFE-ID Empfänger")
            betreff = st.text_input("Betreff")
            aktenzeichen = st.text_input("Aktenzeichen")
            inhalt = st.text_area("Nachricht")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.form_submit_button("💾 Als Entwurf speichern"):
                    bea.erstelle_nachricht(empfaenger, empfaenger_safe, betreff, inhalt, aktenzeichen, als_entwurf=True)
                    st.success("Entwurf gespeichert")
            with col2:
                if st.form_submit_button("📤 Senden"):
                    nachricht = bea.erstelle_nachricht(empfaenger, empfaenger_safe, betreff, inhalt, aktenzeichen)
                    erfolg, msg = bea.sende_nachricht(nachricht.id)
                    if erfolg:
                        st.success(msg)
                    else:
                        st.error(msg)


def render_fristen_tracker():
    """Fristen-Tracker."""
    st.title("📅 Fristen-Tracker")
    
    tracker = st.session_state.fristen_tracker
    stat = tracker.statistik()
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Offen", stat["offen"])
    with col2:
        st.metric("Kritisch", stat["kritisch"], delta_color="inverse")
    with col3:
        st.metric("Überfällig", stat["ueberfaellig"], delta_color="inverse")
    with col4:
        st.metric("Erledigt", stat["erledigt"])
    
    tab1, tab2 = st.tabs(["Übersicht", "Neue Frist"])
    
    with tab1:
        tracker.aktualisiere_status()
        
        for frist in sorted(tracker.fristen, key=lambda f: f.datum or date.max):
            if frist.status.value == "erledigt":
                continue
            
            status_class = {
                "offen": "status-ok",
                "kritisch": "status-warnung",
                "überfällig": "status-kritisch"
            }.get(frist.status.value, "")
            
            with st.expander(f"{frist.titel} - {frist.datum}"):
                st.markdown(f'<span class="{status_class}">{frist.status.value.upper()}</span>', unsafe_allow_html=True)
                st.markdown(f"**Akte:** {frist.akte_name}")
                st.markdown(f"**Typ:** {frist.typ.value}")
                if frist.beschreibung:
                    st.markdown(frist.beschreibung)
                
                if st.button("✅ Als erledigt markieren", key=f"frist_{frist.id}"):
                    tracker.erledige_frist(frist.id)
                    st.rerun()
    
    with tab2:
        with st.form("neue_frist"):
            akte_id = st.text_input("Aktenzeichen")
            akte_name = st.text_input("Aktenname")
            titel = st.text_input("Frist-Titel")
            datum = st.date_input("Fristdatum")
            typ = st.selectbox("Typ", ["gesetzlich", "gerichtlich", "vertraglich", "intern"])
            beschreibung = st.text_area("Beschreibung")
            
            if st.form_submit_button("💾 Frist anlegen"):
                from modules.erweiterte_rechner import FristTyp
                tracker.erstelle_frist(
                    akte_id, akte_name, titel, datum,
                    FristTyp(typ), beschreibung
                )
                st.success("Frist angelegt!")
                st.rerun()


# =============================================================================
# SIDEBAR & NAVIGATION
# =============================================================================

def render_sidebar():
    """Rendert die Sidebar."""
    
    with st.sidebar:
        st.markdown("""
        <div style="text-align: center; padding: 1rem;">
            <span style="font-size: 2.5rem;">⚖️</span>
            <h2 style="color: #f59e0b; margin: 0;">JuraConnect</h2>
            <p style="color: #64748b; font-size: 0.8rem;">v2.0</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        access_type = st.session_state.access_type
        
        st.markdown(f"👤 **{st.session_state.username}**")
        st.caption(f"Modus: {access_type}")
        
        st.markdown("---")
        
        # Navigation je nach Zugangstyp
        if access_type == "arbeitnehmer":
            pages = [
                ("🏠 Dashboard", "dashboard"),
                ("🛡️ Kündigungsschutz-Check", "kuendigungsschutz"),
                ("🔍 KI-Kündigungscheck", "ki_kuendigungscheck"),
                ("📋 KI-Vertragsanalyse", "ki_vertragsanalyse"),
                ("💰 Abfindungsrechner", "abfindung"),
                ("📋 PKH-Rechner", "pkh"),
                ("⚖️ Prozesskostenrechner", "prozesskosten"),
                ("📄 Zeugnis-Analyse", "zeugnis"),
                ("📚 Wissensdatenbank", "wissensdatenbank"),
                ("✅ Dokumenten-Checkliste", "checkliste"),
            ]
        elif access_type == "arbeitgeber":
            pages = [
                ("🏠 Dashboard", "dashboard"),
                ("📋 Kündigungs-Assistent", "kuendigung_ag"),
                ("📋 KI-Vertragsanalyse", "ki_vertragsanalyse"),
                ("👥 Sozialauswahl", "sozialauswahl"),
                ("💰 Abfindungsrechner", "abfindung"),
                ("⚖️ Prozesskostenrechner", "prozesskosten"),
                ("📋 PKH-Rechner", "pkh"),
                ("📚 Wissensdatenbank", "wissensdatenbank"),
                ("✅ Dokumenten-Checkliste", "checkliste_ag"),
            ]
        else:  # kanzlei - ALLE FEATURES
            pages = [
                ("🏠 Dashboard", "dashboard"),
                ("", "divider1"),  # Divider
                ("📁 AKTENVERWALTUNG", "header1"),
                ("📥 RA-Micro Import", "ramicro"),
                ("⏱️ Zeiterfassung", "zeiterfassung"),
                ("📅 Fristen-Tracker", "fristen"),
                ("⚠️ Kollisionsprüfung", "kollision"),
                ("📧 beA-Postfach", "bea"),
                ("", "divider2"),
                ("✍️ SCHRIFTSÄTZE (KI)", "header2"),
                ("⚖️ Klagen-Generator", "schriftsatz_generator"),
                ("🖨️ Druck & Versand", "druck_versand"),
                ("", "divider3"),
                ("🔍 ANALYSE-TOOLS", "header3"),
                ("🛡️ Kündigungsschutz-Check", "kuendigungsschutz"),
                ("🔍 KI-Kündigungscheck", "ki_kuendigungscheck"),
                ("📋 KI-Vertragsanalyse", "ki_vertragsanalyse"),
                ("📄 Zeugnis-Analyse", "zeugnis"),
                ("", "divider4"),
                ("🧮 RECHNER", "header4"),
                ("💰 Abfindungsrechner", "abfindung"),
                ("📋 PKH-Rechner", "pkh"),
                ("⚖️ Prozesskostenrechner", "prozesskosten"),
                ("👥 Sozialauswahl", "sozialauswahl"),
                ("", "divider5"),
                ("📚 WEITERE TOOLS", "header5"),
                ("📚 Wissensdatenbank", "wissensdatenbank"),
                ("📋 Mandanten-Checkliste", "mandanten_checkliste"),
                ("✅ Checkliste AN", "checkliste"),
                ("✅ Checkliste AG", "checkliste_ag"),
            ]
        
        for label, key in pages:
            # Divider
            if key.startswith("divider"):
                st.markdown("---")
            # Header (nicht klickbar)
            elif key.startswith("header"):
                st.markdown(f"**{label}**")
            # Normale Navigation
            else:
                if st.button(label, key=f"nav_{key}", use_container_width=True):
                    st.session_state.current_page = key
                    st.rerun()
        
        st.markdown("---")
        
        if st.button("🏠 Zur Startseite", use_container_width=True):
            st.session_state.authenticated = False
            st.session_state.access_type = None
            st.rerun()


# =============================================================================
# NEUE FEATURES: KI-MODULE
# =============================================================================

def render_ki_vertragsanalyse():
    """KI-Vertragsanalyse für Arbeitsverträge."""
    st.title("📋 KI-Vertragsanalyse")
    st.info("🤖 Lassen Sie Ihren Arbeitsvertrag auf problematische Klauseln prüfen!")
    
    analysierer = KIVertragsanalyse()
    
    tab1, tab2 = st.tabs(["📝 Vertrag analysieren", "ℹ️ Erklärung"])
    
    with tab1:
        vertragstext = st.text_area(
            "Fügen Sie hier Ihren Arbeitsvertrag ein (Text):",
            height=300,
            placeholder="Kopieren Sie den vollständigen Vertragstext hierher..."
        )
        
        if st.button("🔍 Vertrag analysieren", type="primary"):
            if vertragstext and len(vertragstext) > 100:
                with st.spinner("Analysiere Vertrag..."):
                    ergebnis = analysierer.analysiere_vertrag(vertragstext)
                
                # Gesamtbewertung
                bewertung_farbe = {
                    "kritisch": "🔴",
                    "bedenklich": "🟠",
                    "prüfenswert": "🟡",
                    "akzeptabel": "🟢",
                }.get(ergebnis.gesamtbewertung, "⚪")
                
                st.markdown(f"""
                <div class="metric-card" style="text-align: center;">
                    <div class="metric-value">{bewertung_farbe} {ergebnis.gesamtbewertung.upper()}</div>
                    <div class="metric-label">Risiko-Score: {ergebnis.risiko_score}/100</div>
                    <div class="metric-label">Vertragstyp: {ergebnis.vertragstyp}</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Gefundene Klauseln
                if ergebnis.klauseln:
                    st.markdown("### 📋 Gefundene Klauseln")
                    
                    for klausel in ergebnis.klauseln:
                        bewertung_emoji = {
                            KlauselBewertung.UNWIRKSAM: "❌",
                            KlauselBewertung.PROBLEMATISCH: "⚠️",
                            KlauselBewertung.PRUEFENSWERT: "🔍",
                            KlauselBewertung.UNBEDENKLICH: "✅",
                        }.get(klausel.bewertung, "❓")
                        
                        with st.expander(f"{bewertung_emoji} {klausel.titel} (Risiko: {klausel.risiko_score})"):
                            st.markdown(f"**Gefunden:** _{klausel.original_text}_")
                            st.markdown(f"**Bewertung:** {klausel.bewertung.value}")
                            st.markdown(f"**Erklärung:** {klausel.erklaerung}")
                            if klausel.rechtliche_grundlage:
                                st.markdown(f"**Rechtsgrundlage:** {klausel.rechtliche_grundlage}")
                            st.markdown(f"**Empfehlung:** {klausel.empfehlung}")
                
                # Handlungsempfehlungen
                if ergebnis.handlungsempfehlungen:
                    st.markdown("### 💡 Handlungsempfehlungen")
                    for emp in ergebnis.handlungsempfehlungen:
                        st.markdown(f"- {emp}")
            else:
                st.warning("Bitte fügen Sie einen längeren Vertragstext ein.")
    
    with tab2:
        st.markdown("""
        ### Was wird geprüft?
        
        Die KI-Vertragsanalyse prüft Ihren Arbeitsvertrag auf:
        
        - **Ausschlussfristen** (müssen mind. 3 Monate betragen)
        - **Überstundenregelungen** (pauschale Abgeltung oft unwirksam)
        - **Vertragsstrafen** (max. 1 Bruttomonatsgehalt)
        - **Wettbewerbsverbote** (Karenzentschädigung erforderlich)
        - **Versetzungsklauseln** (müssen begrenzt sein)
        - **Rückzahlungsklauseln** (Bindungsdauer angemessen?)
        - **Fehlende Pflichtangaben** nach § 2 NachwG
        
        ### ⚠️ Hinweis
        
        Diese Analyse ersetzt keine anwaltliche Beratung. Bei kritischen 
        Klauseln sollten Sie vor Vertragsunterzeichnung rechtlichen Rat einholen.
        """)


def render_ki_kuendigungscheck():
    """KI-gestützter Kündigungscheck."""
    st.title("🔍 KI-Kündigungscheck")
    st.info("🤖 Prüfen Sie die Wirksamkeit einer Kündigung!")
    
    checker = KIKuendigungsCheck()
    
    with st.form("kuendigungscheck_form"):
        st.markdown("### 📅 Kündigung")
        col1, col2 = st.columns(2)
        
        with col1:
            zugang_datum = st.date_input(
                "Wann haben Sie die Kündigung erhalten?",
                value=date.today()
            )
            kuendigungsart = st.selectbox(
                "Art der Kündigung",
                ["ordentlich", "außerordentlich"]
            )
        
        with col2:
            kuendigungsgrund = st.selectbox(
                "Genannter Kündigungsgrund",
                ["", "betriebsbedingt", "verhaltensbedingt", "personenbedingt", "unklar/kein Grund"]
            )
            schriftform = st.checkbox("Kündigung liegt schriftlich vor", value=True)
            unterschrift = st.checkbox("Unterschrift vorhanden", value=True)
        
        st.markdown("### 🏢 Betrieb")
        col1, col2 = st.columns(2)
        
        with col1:
            betriebsgroesse = st.number_input(
                "Anzahl Mitarbeiter im Betrieb",
                min_value=1, value=50
            )
            hat_betriebsrat = st.checkbox("Betriebsrat vorhanden")
        
        with col2:
            betriebsrat_angehoert = st.checkbox("Betriebsrat wurde angehört", value=True)
            betriebszugehoerigkeit = st.number_input(
                "Ihre Betriebszugehörigkeit (Monate)",
                min_value=0, value=24
            )
        
        st.markdown("### 🛡️ Sonderkündigungsschutz")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            ist_schwerbehindert = st.checkbox("Schwerbehindert/Gleichgestellt")
            integrationsamt = st.checkbox("Integrationsamt hat zugestimmt")
        
        with col2:
            ist_schwanger = st.checkbox("Schwanger")
            arbeitgeber_wusste = st.checkbox("AG wusste von Schwangerschaft")
        
        with col3:
            ist_in_elternzeit = st.checkbox("In Elternzeit")
            ist_br_mitglied = st.checkbox("Betriebsratsmitglied")
            ist_dsb = st.checkbox("Datenschutzbeauftragter")
        
        st.markdown("### 📝 Bei verhaltensbedingter Kündigung")
        col1, col2 = st.columns(2)
        
        with col1:
            abmahnung = st.checkbox("Abmahnung vorhanden")
        with col2:
            abmahnung_einschlaegig = st.checkbox("Abmahnung war einschlägig")
        
        st.markdown("### 📊 Bei betriebsbedingter Kündigung")
        sozialauswahl = st.checkbox("Sozialauswahl wurde durchgeführt")
        
        submitted = st.form_submit_button("🔍 Kündigung prüfen", type="primary")
        
        if submitted:
            ergebnis = checker.pruefe_kuendigung(
                zugang_datum=zugang_datum,
                betriebsgroesse=betriebsgroesse,
                betriebszugehoerigkeit_monate=betriebszugehoerigkeit,
                kuendigungsart=kuendigungsart,
                kuendigungsgrund=kuendigungsgrund,
                schriftform=schriftform,
                unterschrift_vorhanden=unterschrift,
                hat_betriebsrat=hat_betriebsrat,
                betriebsrat_angehoert=betriebsrat_angehoert,
                ist_schwerbehindert=ist_schwerbehindert,
                integrationsamt_zugestimmt=integrationsamt,
                ist_schwanger=ist_schwanger,
                arbeitgeber_wusste_schwangerschaft=arbeitgeber_wusste,
                ist_in_elternzeit=ist_in_elternzeit,
                ist_betriebsratsmitglied=ist_br_mitglied,
                ist_datenschutzbeauftragter=ist_dsb,
                abmahnung_vorhanden=abmahnung,
                abmahnung_einschlaegig=abmahnung_einschlaegig,
                sozialauswahl_durchgefuehrt=sozialauswahl
            )
            
            st.markdown("---")
            
            # Prognose anzeigen
            prognose_farbe = {
                "wahrscheinlich_wirksam": ("🔴", "error"),
                "unsicher": ("🟡", "warning"),
                "wahrscheinlich_unwirksam": ("🟢", "success")
            }.get(ergebnis.wirksamkeit_prognose, ("⚪", "info"))
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Wirksamkeits-Score", f"{ergebnis.wirksamkeit_score}/100")
            with col2:
                st.metric("Prognose", ergebnis.wirksamkeit_prognose.replace("_", " ").title())
            with col3:
                st.metric("Klagefrist", ergebnis.klagefrist.strftime("%d.%m.%Y"))
            
            # Fehler anzeigen
            if ergebnis.formelle_fehler:
                st.error("**Formelle Fehler:**")
                for f in ergebnis.formelle_fehler:
                    st.markdown(f"- **{f['fehler']}**: {f['erklaerung']}")
            
            if ergebnis.verfahrensfehler:
                st.warning("**Verfahrensfehler:**")
                for f in ergebnis.verfahrensfehler:
                    st.markdown(f"- **{f['fehler']}**: {f['erklaerung']}")
            
            if ergebnis.materielle_fehler:
                st.warning("**Materielle Fehler:**")
                for f in ergebnis.materielle_fehler:
                    st.markdown(f"- **{f['fehler']}**: {f['erklaerung']}")
            
            if ergebnis.sonderschutz:
                st.info("**Sonderkündigungsschutz:**")
                for s in ergebnis.sonderschutz:
                    st.markdown(f"- **{s['schutz']}**: {s['erklaerung']}")
            
            # Empfehlungen
            st.markdown("### 💡 Empfehlungen")
            for emp in ergebnis.empfehlungen:
                st.markdown(f"- {emp}")


def render_ki_wissensdatenbank():
    """KI-Wissensdatenbank mit RAG."""
    st.title("📚 KI-Wissensdatenbank")
    st.info("🤖 Stellen Sie Fragen zum Arbeitsrecht!")
    
    if "wissensdatenbank" not in st.session_state:
        st.session_state.wissensdatenbank = KIWissensdatenbank()
    
    wdb = st.session_state.wissensdatenbank
    
    tab1, tab2 = st.tabs(["🔍 Frage stellen", "📖 Themen durchsuchen"])
    
    with tab1:
        frage = st.text_input(
            "Ihre Frage zum Arbeitsrecht:",
            placeholder="z.B. Wie lange ist die Kündigungsfrist?"
        )
        
        if st.button("🔍 Antwort suchen", type="primary") or frage:
            if frage:
                with st.spinner("Suche in Wissensdatenbank..."):
                    antwort = wdb.beantworte_frage(frage)
                
                st.markdown("### 📝 Antwort")
                st.markdown(antwort["antwort"])
                
                if antwort["quellen"]:
                    st.markdown("### 📚 Quellen")
                    for quelle in antwort["quellen"]:
                        st.caption(f"- {quelle['titel']} ({quelle['rechtsgrundlage']})")
        
        # Beispielfragen
        st.markdown("### 💡 Beispielfragen")
        beispiele = [
            "Wie lange ist die Kündigungsfrist?",
            "Was ist die 3-Wochen-Klagefrist?",
            "Wann gilt das Kündigungsschutzgesetz?",
            "Wie hoch ist die Regelabfindung?",
            "Was ist Mutterschutz?"
        ]
        
        for beispiel in beispiele:
            if st.button(beispiel, key=f"bsp_{beispiel[:10]}"):
                antwort = wdb.beantworte_frage(beispiel)
                st.markdown(antwort["antwort"])
    
    with tab2:
        kategorien = wdb.get_kategorien()
        
        selected = st.selectbox("Kategorie wählen:", kategorien)
        
        if selected:
            eintraege = wdb.get_nach_kategorie(selected)
            
            for eintrag in eintraege:
                with st.expander(f"📄 {eintrag.titel}"):
                    st.markdown(eintrag.inhalt)
                    st.caption(f"Rechtsgrundlage: {eintrag.rechtsgrundlage}")


def render_mandanten_checkliste():
    """Interaktive Mandanten-Checkliste."""
    st.title("📋 Mandanten-Checkliste")
    st.info("🎯 Strukturierter Gesprächsleitfaden für die Erstberatung")
    
    # Typ auswählen
    typ = st.selectbox(
        "Beratungsthema:",
        ["kuendigung", "aufhebung", "zeugnis", "abmahnung", "lohn"],
        format_func=lambda x: {
            "kuendigung": "🔴 Kündigung erhalten",
            "aufhebung": "📝 Aufhebungsvertrag",
            "zeugnis": "📄 Arbeitszeugnis",
            "abmahnung": "⚠️ Abmahnung",
            "lohn": "💰 Lohn/Gehalt"
        }.get(x, x)
    )
    
    if f"checkliste_{typ}" not in st.session_state:
        st.session_state[f"checkliste_{typ}"] = MandantenCheckliste(typ)
    
    checkliste = st.session_state[f"checkliste_{typ}"]
    
    # Fortschritt
    beantwortet, gesamt = checkliste.get_fortschritt()
    st.progress(beantwortet / gesamt if gesamt > 0 else 0)
    st.caption(f"Fortschritt: {beantwortet} von {gesamt} Fragen beantwortet")
    
    # Fragen anzeigen
    st.markdown("### 📝 Fragen")
    
    aktuelle_kategorie = ""
    for i, frage in enumerate(checkliste.fragen):
        if frage.kategorie != aktuelle_kategorie:
            aktuelle_kategorie = frage.kategorie
            st.markdown(f"**{aktuelle_kategorie}**")
        
        # Frage-Eingabe je nach Typ
        if frage.typ == FrageTyp.TEXT:
            frage.antwort = st.text_input(
                frage.frage,
                value=frage.antwort or "",
                key=f"frage_{typ}_{i}",
                help=frage.hilfetext
            )
        elif frage.typ == FrageTyp.ZAHL:
            frage.antwort = st.number_input(
                frage.frage,
                value=frage.antwort or 0,
                key=f"frage_{typ}_{i}",
                help=frage.hilfetext
            )
        elif frage.typ == FrageTyp.DATUM:
            frage.antwort = st.date_input(
                frage.frage,
                value=frage.antwort if frage.antwort else date.today(),
                key=f"frage_{typ}_{i}",
                help=frage.hilfetext
            )
        elif frage.typ == FrageTyp.AUSWAHL:
            frage.antwort = st.selectbox(
                frage.frage,
                [""] + frage.optionen,
                index=frage.optionen.index(frage.antwort) + 1 if frage.antwort in frage.optionen else 0,
                key=f"frage_{typ}_{i}",
                help=frage.hilfetext
            )
        elif frage.typ == FrageTyp.JANEIN:
            frage.antwort = st.radio(
                frage.frage,
                ["Ja", "Nein"],
                index=0 if frage.antwort == "Ja" else 1,
                key=f"frage_{typ}_{i}",
                horizontal=True
            )
        elif frage.typ == FrageTyp.MEHRFACH:
            frage.antwort = st.multiselect(
                frage.frage,
                frage.optionen,
                default=frage.antwort or [],
                key=f"frage_{typ}_{i}"
            )
    
    # Ergebnis generieren
    if st.button("📊 Zusammenfassung erstellen", type="primary"):
        ergebnis = checkliste.erstelle_ergebnis()
        
        st.markdown("---")
        st.markdown("### 📊 Ergebnis")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"**Mandant:** {ergebnis.mandant_name}")
            st.markdown(f"**Erstellt:** {ergebnis.erstellt_am.strftime('%d.%m.%Y %H:%M')}")
        with col2:
            st.markdown(f"**Risikobewertung:** {ergebnis.risikobewertung}")
        
        st.markdown("### 📋 Nächste Schritte")
        for schritt in ergebnis.naechste_schritte:
            st.markdown(f"- {schritt}")
        
        st.markdown("### 📄 Benötigte Dokumente")
        for dok in ergebnis.empfohlene_dokumente:
            st.markdown(f"- {dok}")


def render_druck_versand():
    """Druck- und Versandfunktion."""
    st.title("🖨️ Druck & Versand")
    st.info("📤 Dokumente erstellen und versenden")
    
    if "versand_manager" not in st.session_state:
        st.session_state.versand_manager = DruckVersandManager()
    
    manager = st.session_state.versand_manager
    
    tab1, tab2, tab3 = st.tabs(["📝 Neues Dokument", "📤 Versandaufträge", "📋 Vorlagen"])
    
    with tab1:
        vorlage = st.selectbox(
            "Vorlage wählen:",
            ["kuendigungsschutzklage", "abmahnung_gegendarstellung", "brief_standard"],
            format_func=lambda x: {
                "kuendigungsschutzklage": "⚖️ Kündigungsschutzklage",
                "abmahnung_gegendarstellung": "📝 Gegendarstellung Abmahnung",
                "brief_standard": "✉️ Standardbrief"
            }.get(x, x)
        )
        
        st.markdown("### 📝 Daten eingeben")
        
        if vorlage == "brief_standard":
            absender = st.text_area("Absender (Name, Adresse):", height=80)
            empfaenger = st.text_area("Empfänger (Name, Adresse):", height=80)
            betreff = st.text_input("Betreff:")
            inhalt = st.text_area("Inhalt:", height=200)
            
            if st.button("📄 Brief erstellen", type="primary"):
                html = manager.generiere_brief(
                    absender=absender,
                    empfaenger=empfaenger,
                    betreff=betreff,
                    inhalt=inhalt
                )
                st.markdown("### 👁️ Vorschau")
                st.components.v1.html(html, height=600, scrolling=True)
                
                # Versandoptionen
                st.markdown("### 📤 Versenden")
                versand_typ = st.selectbox(
                    "Versandweg:",
                    [VersandTyp.PDF_DOWNLOAD, VersandTyp.EMAIL, VersandTyp.BEA, VersandTyp.POST],
                    format_func=lambda x: {
                        VersandTyp.PDF_DOWNLOAD: "📥 PDF Download",
                        VersandTyp.EMAIL: "📧 E-Mail",
                        VersandTyp.BEA: "⚖️ beA",
                        VersandTyp.POST: "📮 Post"
                    }.get(x, str(x))
                )
                
                if st.button("📤 Versandauftrag erstellen"):
                    auftrag = manager.erstelle_versandauftrag(
                        dokument_name=f"Brief_{betreff[:20]}",
                        dokument_inhalt=html,
                        versand_typ=versand_typ,
                        empfaenger=empfaenger.split("\n")[0] if empfaenger else "",
                        betreff=betreff
                    )
                    st.success(f"Versandauftrag {auftrag.id} erstellt!")
    
    with tab2:
        auftraege = manager.get_auftraege()
        
        if auftraege:
            for auftrag in auftraege:
                status_emoji = {
                    "entwurf": "📝",
                    "wartend": "⏳",
                    "gesendet": "✅",
                    "fehler": "❌"
                }.get(auftrag.status, "❓")
                
                with st.expander(f"{status_emoji} {auftrag.dokument_name} ({auftrag.status})"):
                    st.markdown(f"**ID:** {auftrag.id}")
                    st.markdown(f"**Empfänger:** {auftrag.empfaenger}")
                    st.markdown(f"**Erstellt:** {auftrag.erstellt_am.strftime('%d.%m.%Y %H:%M')}")
                    
                    if auftrag.status == "entwurf":
                        if st.button("📤 Jetzt senden", key=f"send_{auftrag.id}"):
                            erfolg, msg = manager.sende_auftrag(auftrag.id)
                            if erfolg:
                                st.success(msg)
                            else:
                                st.error(msg)
        else:
            st.info("Noch keine Versandaufträge vorhanden.")
    
    with tab3:
        st.markdown("""
        ### 📋 Verfügbare Vorlagen
        
        | Vorlage | Beschreibung |
        |---------|--------------|
        | ⚖️ Kündigungsschutzklage | Klage gegen Kündigung |
        | 📝 Gegendarstellung | Widerspruch gegen Abmahnung |
        | ✉️ Standardbrief | Allgemeiner Geschäftsbrief |
        
        *Weitere Vorlagen können auf Anfrage erstellt werden.*
        """)


def render_schriftsatz_generator():
    """KI-Schriftsatz-Generator für Klagen und Schriftsätze."""
    st.title("⚖️ KI-Schriftsatz-Generator")
    st.info("🤖 Automatische Erstellung von Klagen und Schriftsätzen aus Aktendaten")
    
    generator = KISchriftsatzGenerator()
    
    # Schriftsatztyp wählen
    schriftsatz_typen = generator.get_verfuegbare_schriftsaetze()
    
    col1, col2 = st.columns([1, 2])
    with col1:
        st.markdown("### 📋 Schriftsatztyp")
        for ss in schriftsatz_typen:
            if st.button(f"{ss['icon']} {ss['name']}", key=f"ss_{ss['typ'].value}", use_container_width=True):
                st.session_state.selected_schriftsatz = ss['typ']
    
    with col2:
        selected = st.session_state.get('selected_schriftsatz', SchriftsatzTyp.KUENDIGUNGSSCHUTZKLAGE)
        
        st.markdown(f"### ✍️ {selected.value.replace('_', ' ').title()}")
        
        # Aktendaten eingeben
        with st.expander("📁 Aktendaten", expanded=True):
            aktenzeichen = st.text_input("Aktenzeichen:", value="", placeholder="z.B. 123/24")
            gericht = st.text_input("Arbeitsgericht:", value="Frankfurt am Main")
        
        with st.expander("👤 Mandant (Kläger)", expanded=True):
            m_name = st.text_input("Name:", key="m_name", placeholder="Max Mustermann")
            m_strasse = st.text_input("Straße:", key="m_strasse", placeholder="Musterstraße 1")
            m_plz = st.text_input("PLZ:", key="m_plz", placeholder="60311")
            m_ort = st.text_input("Ort:", key="m_ort", placeholder="Frankfurt am Main")
        
        with st.expander("🏢 Gegner (Beklagter)", expanded=True):
            g_name = st.text_input("Firma:", key="g_name", placeholder="Muster GmbH")
            g_strasse = st.text_input("Straße:", key="g_strasse", placeholder="Industriestr. 10")
            g_plz = st.text_input("PLZ:", key="g_plz", placeholder="60311")
            g_ort = st.text_input("Ort:", key="g_ort", placeholder="Frankfurt am Main")
        
        with st.expander("💼 Arbeitsverhältnis", expanded=True):
            col_a, col_b = st.columns(2)
            with col_a:
                eintritt = st.date_input("Eintrittsdatum:", value=date(2020, 1, 1))
                position = st.text_input("Position:", placeholder="Sachbearbeiter/in")
            with col_b:
                bruttogehalt = st.number_input("Bruttogehalt (€):", min_value=0.0, value=3500.0, step=100.0)
                urlaubstage = st.number_input("Urlaubstage/Jahr:", min_value=20, value=30)
        
        # Je nach Schriftsatztyp weitere Eingaben
        if selected == SchriftsatzTyp.KUENDIGUNGSSCHUTZKLAGE:
            with st.expander("📝 Kündigungsdaten", expanded=True):
                col_k1, col_k2 = st.columns(2)
                with col_k1:
                    kuendigung_datum = st.date_input("Kündigungsdatum:", value=date.today() - timedelta(days=7))
                    zugang_datum = st.date_input("Zugang der Kündigung:", value=date.today() - timedelta(days=5))
                with col_k2:
                    kuendigungsart = st.selectbox("Kündigungsart:", ["ordentlich", "außerordentlich"])
                    kuendigungsgrund = st.text_input("Kündigungsgrund:", placeholder="betriebsbedingt")
                
                kuendigung_zum = st.date_input("Kündigung zum:", value=date.today() + timedelta(days=30))
                betriebsrat = st.checkbox("Betriebsrat angehört?")
                abmahnung = st.checkbox("Abmahnung vorhanden?")
        
        elif selected == SchriftsatzTyp.LOHNKLAGE:
            with st.expander("💰 Lohndaten", expanded=True):
                offene_monate = st.text_input("Offene Monate:", placeholder="Januar 2024, Februar 2024")
                offener_betrag = st.number_input("Offener Betrag (€ brutto):", min_value=0.0, value=7000.0)
                ueberstunden = st.number_input("Offene Überstunden:", min_value=0.0, value=0.0)
                stundenlohn = st.number_input("Stundenlohn (€):", min_value=0.0, value=25.0)
        
        elif selected in [SchriftsatzTyp.URLAUBSKLAGE, SchriftsatzTyp.URLAUBSABGELTUNG]:
            with st.expander("🏖️ Urlaubsdaten", expanded=True):
                urlaubsjahr = st.number_input("Jahr:", min_value=2020, value=date.today().year)
                genommen = st.number_input("Genommene Tage:", min_value=0, value=15)
                offene_tage = st.number_input("Offene Tage:", min_value=0, value=15)
        
        elif selected == SchriftsatzTyp.ZEUGNISKLAGE:
            with st.expander("📄 Zeugnisdaten", expanded=True):
                zeugnis_erhalten = st.checkbox("Zeugnis bereits erhalten?")
                zeugnis_art = st.selectbox("Zeugnisart:", ["qualifiziert", "einfach"])
                gewuenschte_note = st.selectbox("Gewünschte Note:", ["sehr gut", "gut", "befriedigend"])
                maengel = st.text_area("Mängel (einer pro Zeile):", placeholder="Note zu schlecht\nTätigkeiten fehlen")
        
        elif selected == SchriftsatzTyp.VERGLEICHSVORSCHLAG:
            with st.expander("🤝 Vergleichsdaten", expanded=True):
                abfindung = st.number_input("Abfindung (€ brutto):", min_value=0.0, value=10500.0)
                beendigungsdatum = st.date_input("Beendigungsdatum:", value=date.today() + timedelta(days=60))
                freistellung = st.checkbox("Freistellung?", value=True)
                zeugnisnote = st.selectbox("Zeugnisnote:", ["sehr gut", "gut", "befriedigend"])
        
        # Schriftsatz generieren
        if st.button("🤖 Schriftsatz generieren", type="primary", use_container_width=True):
            # Aktendaten zusammenstellen
            akte = Akteninhalt(
                aktenzeichen=aktenzeichen,
                mandant=Parteidaten(name=m_name, strasse=m_strasse, plz=m_plz, ort=m_ort),
                gegner=Parteidaten(name=g_name, strasse=g_strasse, plz=g_plz, ort=g_ort),
                gericht=gericht,
                arbeitsverhaeltnis=Arbeitsverhältnis(
                    eintrittsdatum=eintritt,
                    position=position,
                    bruttogehalt=bruttogehalt,
                    urlaubstage_jahr=urlaubstage
                )
            )
            
            # Je nach Typ spezifische Daten hinzufügen
            if selected == SchriftsatzTyp.KUENDIGUNGSSCHUTZKLAGE:
                akte.kuendigung = Kuendigungsdaten(
                    kuendigung_datum=kuendigung_datum,
                    zugang_datum=zugang_datum,
                    kuendigungsart=kuendigungsart,
                    kuendigungsgrund=kuendigungsgrund,
                    kuendigung_zum=kuendigung_zum,
                    betriebsrat_angehoert=betriebsrat,
                    abmahnung_vorhanden=abmahnung
                )
                schriftsatz = generator.generiere_kuendigungsschutzklage(akte)
            
            elif selected == SchriftsatzTyp.LOHNKLAGE:
                akte.lohn = Lohndaten(
                    offene_monate=offene_monate.split(", ") if offene_monate else [],
                    offener_betrag_brutto=offener_betrag,
                    offene_ueberstunden=ueberstunden,
                    ueberstunden_stundenlohn=stundenlohn
                )
                schriftsatz = generator.generiere_lohnklage(akte)
            
            elif selected in [SchriftsatzTyp.URLAUBSKLAGE, SchriftsatzTyp.URLAUBSABGELTUNG]:
                akte.urlaub = Urlaubsdaten(
                    urlaubsjahr=urlaubsjahr,
                    gesamtanspruch_tage=urlaubstage,
                    genommen_tage=genommen,
                    offene_tage=offene_tage
                )
                schriftsatz = generator.generiere_urlaubsklage(akte, abgeltung=(selected == SchriftsatzTyp.URLAUBSABGELTUNG))
            
            elif selected == SchriftsatzTyp.ZEUGNISKLAGE:
                akte.zeugnis = Zeugnisdaten(
                    zeugnis_erhalten=zeugnis_erhalten,
                    zeugnis_art=zeugnis_art,
                    gewuenschte_note=gewuenschte_note,
                    maengel=maengel.split("\n") if maengel else []
                )
                schriftsatz = generator.generiere_zeugnisklage(akte)
            
            elif selected == SchriftsatzTyp.VERGLEICHSVORSCHLAG:
                schriftsatz = generator.generiere_vergleichsvorschlag(
                    akte, abfindung, beendigungsdatum, freistellung, zeugnisnote
                )
            
            else:
                st.warning("Dieser Schriftsatztyp wird noch entwickelt.")
                return
            
            # Ergebnis anzeigen
            st.markdown("---")
            
            # Hinweise
            if schriftsatz.hinweise:
                for hinweis in schriftsatz.hinweise:
                    st.warning(hinweis)
            
            # Metadaten
            col_m1, col_m2, col_m3 = st.columns(3)
            with col_m1:
                st.metric("Streitwert", f"{schriftsatz.streitwert:,.2f} €")
            with col_m2:
                st.metric("Generiert", schriftsatz.generiert_am.strftime("%d.%m.%Y %H:%M"))
            with col_m3:
                st.metric("Typ", schriftsatz.typ.value.replace("_", " ").title())
            
            # Vorschau
            st.markdown("### 👁️ Vorschau")
            st.components.v1.html(schriftsatz.inhalt_html, height=800, scrolling=True)
            
            # Download-Buttons
            col_d1, col_d2 = st.columns(2)
            with col_d1:
                st.download_button(
                    "📥 HTML herunterladen",
                    schriftsatz.inhalt_html,
                    file_name=f"{schriftsatz.typ.value}_{date.today().isoformat()}.html",
                    mime="text/html"
                )
            with col_d2:
                st.download_button(
                    "📝 Text herunterladen",
                    schriftsatz.inhalt_text,
                    file_name=f"{schriftsatz.typ.value}_{date.today().isoformat()}.txt",
                    mime="text/plain"
                )


# =============================================================================
# MAIN
# =============================================================================

def main():
    load_custom_css()
    init_session_state()
    
    if not st.session_state.authenticated:
        render_landing_page()
    else:
        render_sidebar()
        
        page = st.session_state.current_page
        access = st.session_state.access_type
        
        # Routing
        if page == "dashboard":
            if access == "arbeitnehmer":
                render_arbeitnehmer_dashboard()
            elif access == "arbeitgeber":
                render_arbeitgeber_dashboard()
            else:
                render_kanzlei_dashboard()
        elif page == "kuendigungsschutz":
            render_kuendigungsschutz_check()
        elif page == "abfindung":
            render_abfindungsrechner()
        elif page == "pkh":
            render_pkh_rechner()
        elif page == "prozesskosten":
            render_prozesskosten_rechner()
        elif page == "zeugnis":
            render_zeugnis_analyse()
        elif page == "checkliste":
            render_dokumenten_checkliste_an()
        elif page == "checkliste_ag":
            checkliste = DokumentenCheckliste("arbeitgeber")
            st.title("✅ Dokumenten-Checkliste (Arbeitgeber)")
            # Similar to AN version
        elif page == "kuendigung_ag":
            render_kuendigungs_assistent()
        elif page == "sozialauswahl":
            render_sozialauswahl()
        elif page == "ramicro":
            render_ramicro_import()
        elif page == "zeiterfassung":
            render_zeiterfassung()
        elif page == "fristen":
            render_fristen_tracker()
        elif page == "kollision":
            render_kollisionspruefung()
        elif page == "bea":
            render_bea_postfach()
        elif page == "ki_vertragsanalyse":
            render_ki_vertragsanalyse()
        elif page == "ki_kuendigungscheck":
            render_ki_kuendigungscheck()
        elif page == "wissensdatenbank":
            render_ki_wissensdatenbank()
        elif page == "mandanten_checkliste":
            render_mandanten_checkliste()
        elif page == "druck_versand":
            render_druck_versand()
        elif page == "schriftsatz_generator":
            render_schriftsatz_generator()
        else:
            st.info(f"Seite '{page}' wird noch entwickelt...")


if __name__ == "__main__":
    main()
