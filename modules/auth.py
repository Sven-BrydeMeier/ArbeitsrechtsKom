"""
JuraConnect - Authentifizierung
================================
Login-System mit Demo-Modus und Rollenverwaltung

Rollen:
- admin: Vollzugriff + Benutzerverwaltung
- anwalt: Alle Funktionen
- mitarbeiter: Eingeschränkter Zugriff
- demo: Nur Lesen, keine Speicherung
"""

import streamlit as st
import hashlib
import json
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional, List, Dict
from enum import Enum


class UserRole(Enum):
    ADMIN = "admin"
    ANWALT = "anwalt"
    MITARBEITER = "mitarbeiter"
    DEMO = "demo"


@dataclass
class User:
    username: str
    password_hash: str
    rolle: UserRole
    name: str
    email: str
    aktiv: bool = True
    erstellt: str = ""
    letzter_login: str = ""
    
    def __post_init__(self):
        if not self.erstellt:
            self.erstellt = datetime.now().isoformat()


class AuthManager:
    """Verwaltet Authentifizierung und Benutzer"""
    
    def __init__(self, users_file: str = None):
        if users_file is None:
            data_dir = Path.home() / ".juraconnect"
            data_dir.mkdir(exist_ok=True)
            self.users_file = data_dir / "users.json"
        else:
            self.users_file = Path(users_file)
        
        self._init_default_users()
    
    def _hash_password(self, password: str) -> str:
        """Passwort hashen"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def _init_default_users(self):
        """Standard-Benutzer anlegen wenn Datei nicht existiert"""
        if not self.users_file.exists():
            default_users = {
                "admin": User(
                    username="admin",
                    password_hash=self._hash_password("admin123"),
                    rolle=UserRole.ADMIN,
                    name="Administrator",
                    email="admin@kanzlei.de"
                ),
                "demo": User(
                    username="demo",
                    password_hash=self._hash_password("demo"),
                    rolle=UserRole.DEMO,
                    name="Demo-Benutzer",
                    email="demo@example.com"
                ),
                "anwalt": User(
                    username="anwalt",
                    password_hash=self._hash_password("anwalt123"),
                    rolle=UserRole.ANWALT,
                    name="Max Mustermann",
                    email="anwalt@kanzlei.de"
                ),
                "mitarbeiter": User(
                    username="mitarbeiter",
                    password_hash=self._hash_password("mitarbeiter123"),
                    rolle=UserRole.MITARBEITER,
                    name="Anna Assistenz",
                    email="assistenz@kanzlei.de"
                )
            }
            self._save_users(default_users)
    
    def _load_users(self) -> Dict[str, User]:
        """Benutzer aus Datei laden"""
        if not self.users_file.exists():
            return {}
        
        with open(self.users_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        users = {}
        for username, user_data in data.items():
            user_data['rolle'] = UserRole(user_data['rolle'])
            users[username] = User(**user_data)
        
        return users
    
    def _save_users(self, users: Dict[str, User]):
        """Benutzer in Datei speichern"""
        data = {}
        for username, user in users.items():
            user_dict = asdict(user)
            user_dict['rolle'] = user.rolle.value
            data[username] = user_dict
        
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def authenticate(self, username: str, password: str) -> Optional[User]:
        """Benutzer authentifizieren"""
        users = self._load_users()
        
        if username not in users:
            return None
        
        user = users[username]
        
        if not user.aktiv:
            return None
        
        if user.password_hash != self._hash_password(password):
            return None
        
        user.letzter_login = datetime.now().isoformat()
        users[username] = user
        self._save_users(users)
        
        return user
    
    def get_user(self, username: str) -> Optional[User]:
        """Einzelnen Benutzer abrufen"""
        users = self._load_users()
        return users.get(username)
    
    def get_all_users(self) -> List[User]:
        """Alle Benutzer abrufen"""
        users = self._load_users()
        return list(users.values())
    
    def create_user(self, username: str, password: str, rolle: UserRole, 
                    name: str, email: str) -> bool:
        """Neuen Benutzer anlegen"""
        users = self._load_users()
        
        if username in users:
            return False
        
        users[username] = User(
            username=username,
            password_hash=self._hash_password(password),
            rolle=rolle,
            name=name,
            email=email
        )
        
        self._save_users(users)
        return True
    
    def update_user(self, username: str, **kwargs) -> bool:
        """Benutzer aktualisieren"""
        users = self._load_users()
        
        if username not in users:
            return False
        
        user = users[username]
        
        for key, value in kwargs.items():
            if key == 'password':
                user.password_hash = self._hash_password(value)
            elif key == 'rolle' and isinstance(value, str):
                user.rolle = UserRole(value)
            elif hasattr(user, key):
                setattr(user, key, value)
        
        users[username] = user
        self._save_users(users)
        return True
    
    def delete_user(self, username: str) -> bool:
        """Benutzer löschen"""
        users = self._load_users()
        
        if username not in users:
            return False
        
        if username == 'admin':
            return False
        
        del users[username]
        self._save_users(users)
        return True
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Passwort ändern"""
        user = self.authenticate(username, old_password)
        if not user:
            return False
        
        return self.update_user(username, password=new_password)


# =============================================================================
# Streamlit Session State Management
# =============================================================================

def init_session_state():
    """Session State initialisieren"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = False
    if 'auth_manager' not in st.session_state:
        st.session_state.auth_manager = AuthManager()


def login_user(user: User):
    """Benutzer einloggen"""
    st.session_state.authenticated = True
    st.session_state.user = user
    st.session_state.demo_mode = (user.rolle == UserRole.DEMO)


def logout_user():
    """Benutzer ausloggen"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.demo_mode = False


def is_authenticated() -> bool:
    """Prüfen ob eingeloggt"""
    return st.session_state.get('authenticated', False)


def get_current_user() -> Optional[User]:
    """Aktuellen Benutzer abrufen"""
    return st.session_state.get('user', None)


def is_demo_mode() -> bool:
    """Prüfen ob Demo-Modus"""
    return st.session_state.get('demo_mode', False)


def has_role(required_roles: List[UserRole]) -> bool:
    """Prüfen ob Benutzer eine der erforderlichen Rollen hat"""
    user = get_current_user()
    if not user:
        return False
    return user.rolle in required_roles


def require_auth(allowed_roles: List[UserRole] = None):
    """Funktion für Seitenschutz"""
    if not is_authenticated():
        st.warning("⚠️ Bitte melden Sie sich an, um diese Seite zu nutzen.")
        st.stop()
    
    if allowed_roles:
        user = get_current_user()
        if user.rolle not in allowed_roles:
            st.error("🚫 Sie haben keine Berechtigung für diese Seite.")
            st.stop()


# =============================================================================
# Login UI Komponenten
# =============================================================================

def render_login_form():
    """Login-Formular rendern"""
    st.markdown("### 🔐 Anmeldung")
    
    with st.form("login_form"):
        username = st.text_input("Benutzername")
        password = st.text_input("Passwort", type="password")
        
        col1, col2 = st.columns(2)
        with col1:
            login_btn = st.form_submit_button("🔓 Anmelden", type="primary")
        with col2:
            demo_btn = st.form_submit_button("🎮 Demo starten")
    
    if login_btn and username and password:
        auth = st.session_state.auth_manager
        user = auth.authenticate(username, password)
        
        if user:
            login_user(user)
            st.success(f"✅ Willkommen, {user.name}!")
            st.rerun()
        else:
            st.error("❌ Ungültige Anmeldedaten")
    
    if demo_btn:
        auth = st.session_state.auth_manager
        demo_user = auth.get_user("demo")
        if demo_user:
            login_user(demo_user)
            st.success("🎮 Demo-Modus gestartet!")
            st.rerun()


def render_user_menu():
    """Benutzer-Menü in der Sidebar"""
    user = get_current_user()
    
    if user:
        st.sidebar.markdown("---")
        st.sidebar.markdown(f"👤 **{user.name}**")
        
        rolle_badges = {
            UserRole.ADMIN: "🔴 Admin",
            UserRole.ANWALT: "🟢 Anwalt",
            UserRole.MITARBEITER: "🟡 Mitarbeiter",
            UserRole.DEMO: "🔵 Demo"
        }
        st.sidebar.caption(rolle_badges.get(user.rolle, ""))
        
        if is_demo_mode():
            st.sidebar.warning("🎮 Demo-Modus")
        
        if st.sidebar.button("🚪 Abmelden", use_container_width=True):
            logout_user()
            st.rerun()


def render_demo_banner():
    """Demo-Banner anzeigen"""
    if is_demo_mode():
        st.info("""
        🎮 **Demo-Modus aktiv** - Sie können alle Funktionen testen. 
        Daten werden nicht dauerhaft gespeichert.
        """)


# =============================================================================
# Berechtigungsprüfungen
# =============================================================================

ADMIN_ONLY = [UserRole.ADMIN]
FULL_ACCESS = [UserRole.ADMIN, UserRole.ANWALT]
STANDARD_ACCESS = [UserRole.ADMIN, UserRole.ANWALT, UserRole.MITARBEITER]
ALL_ACCESS = [UserRole.ADMIN, UserRole.ANWALT, UserRole.MITARBEITER, UserRole.DEMO]


def can_edit() -> bool:
    """Prüfen ob Benutzer bearbeiten darf"""
    if is_demo_mode():
        return False
    return has_role(STANDARD_ACCESS)


def can_delete() -> bool:
    """Prüfen ob Benutzer löschen darf"""
    if is_demo_mode():
        return False
    return has_role(FULL_ACCESS)


def can_admin() -> bool:
    """Prüfen ob Benutzer Admin-Rechte hat"""
    return has_role(ADMIN_ONLY)


# =============================================================================
# Konfiguration
# =============================================================================

APP_CONFIG = {
    "demo_mode_enabled": True,
    "require_login": False,  # False = Direkter Zugang im Demo-Modus ohne Login
    "session_timeout": 60,
    "max_login_attempts": 5,
}


def get_config(key: str, default=None):
    """Konfigurationswert abrufen"""
    return APP_CONFIG.get(key, default)


def set_config(key: str, value):
    """Konfigurationswert setzen"""
    APP_CONFIG[key] = value


def auto_demo_login():
    """Automatisch als Demo-User einloggen wenn require_login=False"""
    if not get_config("require_login") and not is_authenticated():
        auth = st.session_state.get('auth_manager')
        if auth is None:
            auth = AuthManager()
            st.session_state.auth_manager = auth
        
        demo_user = auth.get_user("demo")
        if demo_user:
            login_user(demo_user)
