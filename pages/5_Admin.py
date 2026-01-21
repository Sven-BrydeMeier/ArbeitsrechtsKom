"""
JuraConnect - Admin-Dashboard
==============================
Benutzerverwaltung und Systemeinstellungen
Nur für Administratoren zugänglich
"""

import streamlit as st
from datetime import datetime
import sys
sys.path.insert(0, '..')

from modules.auth import (
    AuthManager, UserRole, User,
    init_session_state, is_authenticated, get_current_user,
    can_admin, require_auth, ADMIN_ONLY, render_user_menu,
    get_config, set_config
)


def render():
    # Session initialisieren
    init_session_state()
    
    # Nur für Admins
    if not is_authenticated():
        st.warning("⚠️ Bitte melden Sie sich an.")
        st.stop()
    
    if not can_admin():
        st.error("🚫 Nur Administratoren haben Zugriff auf diesen Bereich.")
        st.stop()
    
    st.title("🔧 Admin-Dashboard")
    st.markdown("Systemverwaltung und Benutzereinstellungen")
    
    # User-Menü in Sidebar
    render_user_menu()
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "👥 Benutzerverwaltung",
        "⚙️ Systemeinstellungen", 
        "📊 Statistiken",
        "🔐 Sicherheit"
    ])
    
    with tab1:
        render_benutzerverwaltung()
    
    with tab2:
        render_systemeinstellungen()
    
    with tab3:
        render_statistiken()
    
    with tab4:
        render_sicherheit()


def render_benutzerverwaltung():
    st.header("👥 Benutzerverwaltung")
    
    auth: AuthManager = st.session_state.auth_manager
    users = auth.get_all_users()
    
    # Übersicht
    st.subheader("📋 Benutzerübersicht")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Gesamt", len(users))
    with col2:
        aktive = len([u for u in users if u.aktiv])
        st.metric("Aktiv", aktive)
    with col3:
        admins = len([u for u in users if u.rolle == UserRole.ADMIN])
        st.metric("Admins", admins)
    with col4:
        anwaelte = len([u for u in users if u.rolle == UserRole.ANWALT])
        st.metric("Anwälte", anwaelte)
    
    st.divider()
    
    # Benutzerliste
    st.subheader("📝 Benutzer")
    
    for user in users:
        rolle_badge = {
            UserRole.ADMIN: "🔴",
            UserRole.ANWALT: "🟢",
            UserRole.MITARBEITER: "🟡",
            UserRole.DEMO: "🔵"
        }
        
        status = "✅" if user.aktiv else "❌"
        
        with st.expander(f"{rolle_badge.get(user.rolle, '⚪')} **{user.name}** ({user.username}) {status}"):
            col1, col2 = st.columns(2)
            
            with col1:
                st.write(f"**Benutzername:** {user.username}")
                st.write(f"**E-Mail:** {user.email}")
                st.write(f"**Rolle:** {user.rolle.value}")
            
            with col2:
                st.write(f"**Status:** {'Aktiv' if user.aktiv else 'Deaktiviert'}")
                st.write(f"**Erstellt:** {user.erstellt[:10] if user.erstellt else 'N/A'}")
                st.write(f"**Letzter Login:** {user.letzter_login[:10] if user.letzter_login else 'Nie'}")
            
            # Aktionen
            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                if st.button("✏️ Bearbeiten", key=f"edit_{user.username}"):
                    st.session_state[f"edit_user_{user.username}"] = True
            
            with col2:
                new_status = not user.aktiv
                btn_text = "✅ Aktivieren" if not user.aktiv else "🚫 Deaktivieren"
                if st.button(btn_text, key=f"toggle_{user.username}"):
                    auth.update_user(user.username, aktiv=new_status)
                    st.success(f"Status geändert!")
                    st.rerun()
            
            with col3:
                if st.button("🔑 Passwort", key=f"pw_{user.username}"):
                    st.session_state[f"reset_pw_{user.username}"] = True
            
            with col4:
                if user.username != "admin":
                    if st.button("🗑️ Löschen", key=f"del_{user.username}"):
                        st.session_state[f"confirm_del_{user.username}"] = True
            
            # Bearbeiten-Dialog
            if st.session_state.get(f"edit_user_{user.username}", False):
                st.markdown("#### ✏️ Benutzer bearbeiten")
                with st.form(f"edit_form_{user.username}"):
                    new_name = st.text_input("Name", value=user.name)
                    new_email = st.text_input("E-Mail", value=user.email)
                    new_rolle = st.selectbox("Rolle", 
                                             [r.value for r in UserRole],
                                             index=[r.value for r in UserRole].index(user.rolle.value))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Speichern", type="primary"):
                            auth.update_user(user.username, 
                                           name=new_name, 
                                           email=new_email,
                                           rolle=new_rolle)
                            st.success("Änderungen gespeichert!")
                            st.session_state[f"edit_user_{user.username}"] = False
                            st.rerun()
                    with col2:
                        if st.form_submit_button("❌ Abbrechen"):
                            st.session_state[f"edit_user_{user.username}"] = False
                            st.rerun()
            
            # Passwort-Reset-Dialog
            if st.session_state.get(f"reset_pw_{user.username}", False):
                st.markdown("#### 🔑 Neues Passwort setzen")
                with st.form(f"pw_form_{user.username}"):
                    new_pw = st.text_input("Neues Passwort", type="password")
                    new_pw_confirm = st.text_input("Passwort bestätigen", type="password")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.form_submit_button("💾 Speichern", type="primary"):
                            if new_pw != new_pw_confirm:
                                st.error("Passwörter stimmen nicht überein!")
                            elif len(new_pw) < 6:
                                st.error("Passwort muss mind. 6 Zeichen haben!")
                            else:
                                auth.update_user(user.username, password=new_pw)
                                st.success("Passwort geändert!")
                                st.session_state[f"reset_pw_{user.username}"] = False
                                st.rerun()
                    with col2:
                        if st.form_submit_button("❌ Abbrechen"):
                            st.session_state[f"reset_pw_{user.username}"] = False
                            st.rerun()
            
            # Löschen-Bestätigung
            if st.session_state.get(f"confirm_del_{user.username}", False):
                st.warning(f"⚠️ Benutzer **{user.name}** wirklich löschen?")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Ja, löschen", key=f"confirm_yes_{user.username}"):
                        auth.delete_user(user.username)
                        st.success("Benutzer gelöscht!")
                        st.session_state[f"confirm_del_{user.username}"] = False
                        st.rerun()
                with col2:
                    if st.button("❌ Abbrechen", key=f"confirm_no_{user.username}"):
                        st.session_state[f"confirm_del_{user.username}"] = False
                        st.rerun()
    
    st.divider()
    
    # Neuen Benutzer anlegen
    st.subheader("➕ Neuen Benutzer anlegen")
    
    with st.form("new_user_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            new_username = st.text_input("Benutzername*")
            new_name = st.text_input("Vollständiger Name*")
            new_email = st.text_input("E-Mail*")
        
        with col2:
            new_password = st.text_input("Passwort*", type="password")
            new_password_confirm = st.text_input("Passwort bestätigen*", type="password")
            new_rolle = st.selectbox("Rolle*", [
                ("anwalt", "🟢 Anwalt"),
                ("mitarbeiter", "🟡 Mitarbeiter"),
                ("admin", "🔴 Administrator")
            ], format_func=lambda x: x[1])
        
        submitted = st.form_submit_button("➕ Benutzer anlegen", type="primary")
        
        if submitted:
            if not all([new_username, new_name, new_email, new_password]):
                st.error("Bitte alle Pflichtfelder ausfüllen!")
            elif new_password != new_password_confirm:
                st.error("Passwörter stimmen nicht überein!")
            elif len(new_password) < 6:
                st.error("Passwort muss mind. 6 Zeichen haben!")
            else:
                success = auth.create_user(
                    username=new_username,
                    password=new_password,
                    rolle=UserRole(new_rolle[0]),
                    name=new_name,
                    email=new_email
                )
                if success:
                    st.success(f"✅ Benutzer **{new_name}** erfolgreich angelegt!")
                    st.rerun()
                else:
                    st.error("Benutzername existiert bereits!")


def render_systemeinstellungen():
    st.header("⚙️ Systemeinstellungen")
    
    st.subheader("🔐 Anmelde-Einstellungen")
    
    # Demo-Modus
    demo_enabled = st.checkbox(
        "🎮 Demo-Modus aktiviert",
        value=get_config("demo_mode_enabled"),
        help="Wenn aktiviert, wird der Demo-Button auf der Login-Seite angezeigt"
    )
    
    # Login erforderlich
    require_login = st.checkbox(
        "🔒 Login erforderlich",
        value=get_config("require_login"),
        help="Wenn deaktiviert, können Benutzer direkt im Demo-Modus starten"
    )
    
    # Session Timeout
    timeout = st.number_input(
        "⏱️ Session-Timeout (Minuten)",
        min_value=5,
        max_value=480,
        value=get_config("session_timeout", 60),
        help="Automatischer Logout nach Inaktivität"
    )
    
    # Max Login-Versuche
    max_attempts = st.number_input(
        "🚫 Max. Login-Versuche",
        min_value=3,
        max_value=20,
        value=get_config("max_login_attempts", 5),
        help="Anzahl Fehlversuche bis zur Sperrung"
    )
    
    if st.button("💾 Einstellungen speichern", type="primary"):
        set_config("demo_mode_enabled", demo_enabled)
        set_config("require_login", require_login)
        set_config("session_timeout", timeout)
        set_config("max_login_attempts", max_attempts)
        st.success("✅ Einstellungen gespeichert!")
    
    st.divider()
    
    st.subheader("🎨 Erscheinungsbild")
    
    st.info("Diese Einstellungen werden in `.streamlit/config.toml` gespeichert.")
    
    primary_color = st.color_picker("Primärfarbe", value="#1E3A5F")
    
    st.code(f"""
# .streamlit/config.toml
[theme]
primaryColor = "{primary_color}"
    """)
    
    st.divider()
    
    st.subheader("📂 Datenpfade")
    
    st.code(f"""
Benutzerdaten: ~/.juraconnect/users.json
Datenbank: ~/.juraconnect/juraconnect.db
    """)


def render_statistiken():
    st.header("📊 Systemstatistiken")
    
    auth: AuthManager = st.session_state.auth_manager
    users = auth.get_all_users()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("👥 Benutzer nach Rolle")
        
        rollen_count = {}
        for user in users:
            rolle = user.rolle.value
            rollen_count[rolle] = rollen_count.get(rolle, 0) + 1
        
        for rolle, count in rollen_count.items():
            st.progress(count / len(users), text=f"{rolle}: {count}")
    
    with col2:
        st.subheader("📅 Letzte Logins")
        
        recent_logins = sorted(
            [u for u in users if u.letzter_login],
            key=lambda x: x.letzter_login,
            reverse=True
        )[:5]
        
        for user in recent_logins:
            login_date = user.letzter_login[:10] if user.letzter_login else "Nie"
            st.write(f"- **{user.name}**: {login_date}")
    
    st.divider()
    
    st.subheader("💾 Systeminfo")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Version", "1.0.0")
    with col2:
        st.metric("Python", "3.11")
    with col3:
        st.metric("Streamlit", "1.28+")


def render_sicherheit():
    st.header("🔐 Sicherheit")
    
    user = get_current_user()
    
    st.subheader("🔑 Eigenes Passwort ändern")
    
    with st.form("change_own_password"):
        old_pw = st.text_input("Aktuelles Passwort", type="password")
        new_pw = st.text_input("Neues Passwort", type="password")
        new_pw_confirm = st.text_input("Neues Passwort bestätigen", type="password")
        
        if st.form_submit_button("🔑 Passwort ändern", type="primary"):
            if new_pw != new_pw_confirm:
                st.error("Passwörter stimmen nicht überein!")
            elif len(new_pw) < 6:
                st.error("Passwort muss mind. 6 Zeichen haben!")
            else:
                auth: AuthManager = st.session_state.auth_manager
                if auth.change_password(user.username, old_pw, new_pw):
                    st.success("✅ Passwort erfolgreich geändert!")
                else:
                    st.error("❌ Aktuelles Passwort falsch!")
    
    st.divider()
    
    st.subheader("📋 Sicherheits-Empfehlungen")
    
    checks = [
        ("✅", "Passwort-Hashing mit SHA-256"),
        ("✅", "Session-basierte Authentifizierung"),
        ("⚠️", "HTTPS für Produktion konfigurieren"),
        ("⚠️", "Regelmäßige Backups einrichten"),
        ("⚠️", "Firewall-Regeln prüfen"),
    ]
    
    for status, text in checks:
        st.write(f"{status} {text}")
    
    st.divider()
    
    st.subheader("🔒 Standard-Zugangsdaten")
    
    st.warning("""
    **⚠️ Wichtig für Produktion:**
    
    Ändern Sie unbedingt die Standard-Passwörter:
    
    | Benutzer | Standard-Passwort |
    |----------|-------------------|
    | admin | admin123 |
    | anwalt | anwalt123 |
    | mitarbeiter | mitarbeiter123 |
    | demo | demo |
    """)


if __name__ == "__main__":
    render()
