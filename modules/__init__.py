"""
JuraConnect Module
==================
Arbeitsrecht-Softwarelösung für deutsche Kanzleien
"""

from .rechner import (
    KuendigungsfristenRechner,
    AbfindungsRechner,
    ProzesskostenRechner,
    UrlaubsRechner,
    UeberstundenRechner,
    VerjaehrungsRechner,
    berechne_kuendigungsfrist,
    berechne_abfindung,
    berechne_prozesskosten,
    berechne_3_wochen_frist
)

from .kuendigungsschutz import (
    KuendigungsschutzPruefer,
    MandantDaten,
    KuendigungsschutzErgebnis,
    kuendigungsschutz_check
)

from .zeugnis_analyse import (
    ZeugnisAnalysator,
    ZeugnisAnalyse,
    analysiere_zeugnis
)

from .arbeitgeber import (
    SozialauswahlRechner,
    KuendigungsAssistent,
    AbmahnungsGenerator,
    ArbeitsvertragsGenerator,
    ComplianceCheckliste,
    Mitarbeiter,
    sozialauswahl,
    generiere_abmahnung
)

from .vorlagen import (
    VorlagenManager,
    VorlagenDaten,
    erstelle_kuendigungsschutzklage,
    erstelle_deckungsanfrage
)

from .datenbank import (
    JuraConnectDB,
    Mandant,
    Akte,
    Frist,
    Dokument,
    get_db
)

from .auth import (
    AuthManager,
    UserRole,
    User,
    init_session_state,
    is_authenticated,
    get_current_user,
    is_demo_mode,
    login_user,
    logout_user,
    can_edit,
    can_delete,
    can_admin,
    render_login_form,
    render_user_menu,
    render_demo_banner
)

from .wiki import (
    WikiManager,
    WikiFragenManager,
    WikiEintrag,
    WikiFrage,
    WikiKategorie,
    WikiStatus,
    get_wiki_manager,
    get_fragen_manager
)

from .ki_assistent import (
    AktenAssistent,
    AktenNotiz,
    KIAnfrage,
    render_ki_assistent,
    get_akten_assistent
)

from .abrechnung import (
    AbrechnungsManager,
    Leistung,
    Rechnung,
    LeistungsTyp,
    RechnungsStatus,
    erfasse_aktion,
    zeige_kostenhinweis,
    render_kostenübersicht,
    render_rechnungsstellung,
    get_abrechnungs_manager
)

__version__ = "1.2.0"
__author__ = "JuraConnect Team"
