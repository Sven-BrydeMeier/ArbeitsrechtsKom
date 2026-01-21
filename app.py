"""
JuraConnect - Arbeitsrecht-Software
====================================
Hauptanwendung mit Authentifizierung und Demo-Modus

Starten mit: streamlit run app.py

Version: 1.0.0
"""

import streamlit as st
from datetime import date, timedelta
import sys
from pathlib import Path

# Modulpfad hinzufügen
sys.path.insert(0, str(Path(__file__).parent))

from modules.auth import (
    init_session_state, is_authenticated, get_current_user, is_demo_mode,
    render_login_form, render_user_menu, render_demo_banner,
    auto_demo_login, get_config, UserRole, can_admin
)


def main():
    # Seitenkonfiguration
    st.set_page_config(
        page_title="JuraConnect - Arbeitsrecht",
        page_icon="⚖️",
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            'Get Help': 'https://github.com/juraconnect/juraconnect',
            'Report a bug': 'https://github.com/juraconnect/juraconnect/issues',
            'About': '''
            # JuraConnect
            **Arbeitsrecht-Software für deutsche Kanzleien**
            
            Version 1.0.0
            
            © 2024 JuraConnect Team
            '''
        }
    )
    
    # Custom CSS
    st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E3A5F;
        margin-bottom: 0;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-top: 0;
    }
    .feature-card {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 10px 0;
        border-left: 4px solid #1E3A5F;
    }
    .demo-banner {
        background-color: #e3f2fd;
        border-left: 4px solid #2196f3;
        padding: 15px;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Session State initialisieren
    init_session_state()
    
    # Auto-Login im Demo-Modus wenn require_login=False
    if not get_config("require_login") and not is_authenticated():
        auto_demo_login()
    
    # Sidebar
    render_sidebar()
    
    # Hauptbereich
    if is_authenticated():
        render_dashboard()
    else:
        render_landing_page()


def render_sidebar():
    """Sidebar rendern"""
    with st.sidebar:
        st.markdown("## ⚖️ JuraConnect")
        st.caption("Arbeitsrecht-Software")
        st.markdown("---")
        
        if is_authenticated():
            user = get_current_user()
            
            # Benutzer-Info
            rolle_badges = {
                UserRole.ADMIN: "🔴 Admin",
                UserRole.ANWALT: "🟢 Anwalt",
                UserRole.MITARBEITER: "🟡 Mitarbeiter",
                UserRole.DEMO: "🔵 Demo"
            }
            
            st.markdown(f"👤 **{user.name}**")
            st.caption(rolle_badges.get(user.rolle, ""))
            
            if is_demo_mode():
                st.warning("🎮 Demo-Modus")
            
            st.markdown("---")
            
            # Quick Stats
            st.markdown("### 📊 Quick Stats")
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Akten", "23")
            with col2:
                st.metric("Fristen", "7")
            
            st.markdown("---")
            
            # Navigation
            st.markdown("### 📑 Navigation")
            st.page_link("app.py", label="🏠 Startseite", icon="🏠")
            st.page_link("pages/1_Arbeitnehmer.py", label="👷 Arbeitnehmer")
            st.page_link("pages/2_Arbeitgeber.py", label="🏢 Arbeitgeber")
            st.page_link("pages/3_Kanzlei_Tools.py", label="⚖️ Kanzlei-Tools")
            st.page_link("pages/4_Akten.py", label="📂 Akten")
            st.page_link("pages/6_Wiki.py", label="📚 Wiki")
            
            if can_admin():
                st.page_link("pages/5_Admin.py", label="🔧 Admin")
            
            st.markdown("---")
            
            # Logout
            if st.button("🚪 Abmelden", use_container_width=True):
                from modules.auth import logout_user
                logout_user()
                st.rerun()
        
        else:
            st.info("Bitte anmelden oder Demo starten")
        
        st.markdown("---")
        st.caption("© 2024 JuraConnect")
        st.caption("Version 1.0.0")


def render_landing_page():
    """Landing Page für nicht eingeloggte Benutzer"""
    
    st.markdown('<p class="main-header">⚖️ JuraConnect</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Die Arbeitsrecht-Software für deutsche Kanzleien</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Zwei Spalten: Login links, Features rechts
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### 🚀 Jetzt starten")
        
        # Demo-Modus hervorheben
        st.markdown("""
        <div class="demo-banner">
            <strong>🎮 Demo-Modus verfügbar!</strong><br>
            Testen Sie alle Funktionen ohne Registrierung.
        </div>
        """, unsafe_allow_html=True)
        
        render_login_form()
        
        st.markdown("---")
        st.caption("**Demo-Zugangsdaten:**")
        st.caption("Benutzer: `demo` | Passwort: `demo`")
    
    with col2:
        st.markdown("### ✨ Funktionen")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("""
            #### 👷 Für Arbeitnehmer
            - 🚨 Kündigungsschutz-Check
            - 💰 Abfindungsrechner
            - 📄 Zeugnis-Analyse
            - ⏰ Überstundenrechner
            - 🏖️ Urlaubsrechner
            - ⚖️ Prozesskostenrechner
            """)
            
            st.markdown("""
            #### ⚖️ Kanzlei-Tools
            - 📝 Schriftsatz-Generator
            - 📅 Fristenrechner
            - 📬 RSV-Deckungsanfrage
            - 📊 Vergleichsrechner
            """)
        
        with col_b:
            st.markdown("""
            #### 🏢 Für Arbeitgeber
            - 📋 Kündigungs-Assistent
            - 📊 Sozialauswahl-Rechner
            - ⚠️ Abmahnungs-Generator
            - 📝 Arbeitsverträge
            - ✅ Compliance-Checklisten
            """)
            
            st.markdown("""
            #### 📂 Verwaltung
            - 📋 Aktenübersicht
            - 👥 Mandantenverwaltung
            - 📅 Fristenkalender
            - 📊 Dashboard & KPIs
            """)
    
    st.markdown("---")
    
    # Feature-Highlights
    st.markdown("### 🌟 Warum JuraConnect?")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        #### 🇩🇪 Made in Germany
        Speziell für deutsches Arbeitsrecht entwickelt. 
        Alle Berechnungen basieren auf aktuellen Gesetzen 
        (BGB, KSchG, RVG, GKG 2024).
        """)
    
    with col2:
        st.markdown("""
        #### 🔒 DSGVO-konform
        Lokale Datenspeicherung. Ihre Mandantendaten 
        bleiben auf Ihrem Server. Keine Cloud, 
        keine externen Dienste.
        """)
    
    with col3:
        st.markdown("""
        #### 💡 Einfache Bedienung
        Intuitive Oberfläche, keine Einarbeitung nötig. 
        Alle Tools direkt im Browser, 
        keine Installation erforderlich.
        """)


def render_dashboard():
    """Dashboard für eingeloggte Benutzer"""
    
    user = get_current_user()
    
    # Demo-Banner
    render_demo_banner()
    
    # Header
    st.markdown(f'<p class="main-header">⚖️ JuraConnect</p>', unsafe_allow_html=True)
    st.markdown(f'<p class="sub-header">Willkommen, {user.name}!</p>', unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Dashboard-KPIs
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📂 Aktive Akten", "23", delta="+3 diese Woche")
    
    with col2:
        st.metric("👥 Mandanten", "18", delta="+2 neu")
    
    with col3:
        st.metric("📅 Offene Fristen", "7", delta="1 kritisch", delta_color="inverse")
    
    with col4:
        st.metric("⏱️ Zeit (Woche)", "32,5h", delta="28h abrechenbar")
    
    st.markdown("---")
    
    # Zwei Spalten: Fristen und Aktivitäten
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("🚨 Dringende Fristen")
        
        st.error("🔴 **2024-001-KS**: Klagefrist Kündigungsschutz - **In 3 Tagen**")
        st.warning("⚠️ **2024-002-Z**: Schriftsatzfrist - 7 Tage")
        st.info("📅 **2024-001-KS**: Verhandlungstermin - 14 Tage")
        
        if not is_demo_mode():
            st.page_link("pages/4_Akten.py", label="📅 Alle Fristen anzeigen →")
    
    with col2:
        st.subheader("📋 Letzte Aktivitäten")
        
        aktivitaeten = [
            ("🆕", "Neue Akte angelegt", "2024-003-L", "vor 2 Stunden"),
            ("📝", "Schriftsatz erstellt", "2024-001-KS", "vor 4 Stunden"),
            ("✅", "Frist erledigt", "2024-002-Z", "gestern"),
            ("👥", "Mandant hinzugefügt", "Peter Weber", "gestern"),
            ("💰", "Zahlung eingegangen", "2023-045-KS", "vor 2 Tagen"),
        ]
        
        for icon, aktion, details, zeit in aktivitaeten:
            st.markdown(f"{icon} **{aktion}** - {details} ({zeit})")
    
    st.markdown("---")
    
    # Schnellzugriff
    st.subheader("🚀 Schnellzugriff")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("### 👷 Arbeitnehmer")
        st.markdown("""
        - 🚨 Kündigungsschutz-Check
        - 💰 Abfindungsrechner
        - 📄 Zeugnis-Analyse
        - ⏰ Überstundenrechner
        """)
        st.page_link("pages/1_Arbeitnehmer.py", label="→ Öffnen")
    
    with col2:
        st.markdown("### 🏢 Arbeitgeber")
        st.markdown("""
        - 📋 Kündigungs-Assistent
        - 📊 Sozialauswahl
        - ⚠️ Abmahnung
        - 📝 Arbeitsverträge
        """)
        st.page_link("pages/2_Arbeitgeber.py", label="→ Öffnen")
    
    with col3:
        st.markdown("### ⚖️ Kanzlei")
        st.markdown("""
        - 📝 Schriftsätze
        - 📅 Fristenrechner
        - 📬 RSV-Deckung
        - 📊 Vergleichsrechner
        """)
        st.page_link("pages/3_Kanzlei_Tools.py", label="→ Öffnen")
    
    with col4:
        st.markdown("### 📂 Verwaltung")
        st.markdown("""
        - 📋 Aktenübersicht
        - 👥 Mandanten
        - 📅 Fristen
        - 📊 Dashboard
        """)
        st.page_link("pages/4_Akten.py", label="→ Öffnen")
    
    # Admin-Bereich
    if can_admin():
        st.markdown("---")
        st.subheader("🔧 Administration")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("👥 Benutzer", "4")
        with col2:
            st.metric("🟢 Aktive Sessions", "2")
        with col3:
            st.page_link("pages/5_Admin.py", label="🔧 Admin-Dashboard öffnen")
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #888; padding: 20px;">
        <p><strong>JuraConnect</strong> - Arbeitsrecht-Software für deutsche Kanzleien</p>
        <p>Version 1.0.0 | DSGVO-konform | Made in Germany 🇩🇪</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
