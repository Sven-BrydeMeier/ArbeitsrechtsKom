"""
JuraConnect - Abrechnungssystem
================================
Kostentransparenz und automatische Rechnungsstellung.
Erfasst alle kostenauslösenden Aktionen und erstellt Rechnungen.
"""

import streamlit as st
import json
from datetime import datetime, date
from pathlib import Path
from dataclasses import dataclass, asdict, field
from typing import List, Dict, Optional
from enum import Enum


class LeistungsTyp(Enum):
    BERATUNG = "beratung"
    SCHRIFTSATZ = "schriftsatz"
    GERICHT = "gericht"
    KI_RECHERCHE = "ki_recherche"
    DOKUMENT = "dokument"
    KOMMUNIKATION = "kommunikation"
    SONSTIGE = "sonstige"


class RechnungsStatus(Enum):
    ENTWURF = "entwurf"
    VERSENDET = "versendet"
    BEZAHLT = "bezahlt"
    MAHNUNG = "mahnung"
    STORNIERT = "storniert"


@dataclass
class Leistung:
    """Eine einzelne abrechenbare Leistung"""
    id: str
    akte_id: str
    typ: LeistungsTyp
    beschreibung: str
    betrag: float
    mwst_satz: float = 19.0
    erstellt_von: str = ""
    erstellt_am: str = ""
    abgerechnet: bool = False
    rechnung_id: str = ""
    
    def __post_init__(self):
        if not self.erstellt_am:
            self.erstellt_am = datetime.now().isoformat()
    
    @property
    def mwst_betrag(self) -> float:
        return self.betrag * (self.mwst_satz / 100)
    
    @property
    def brutto_betrag(self) -> float:
        return self.betrag + self.mwst_betrag


@dataclass
class Rechnung:
    """Eine Rechnung an den Mandanten"""
    id: str
    akte_id: str
    mandant_name: str
    mandant_adresse: str
    leistungen: List[str]  # Leistungs-IDs
    netto_summe: float
    mwst_summe: float
    brutto_summe: float
    status: RechnungsStatus = RechnungsStatus.ENTWURF
    erstellt_am: str = ""
    versendet_am: str = ""
    bezahlt_am: str = ""
    zahlungsziel_tage: int = 14
    notizen: str = ""
    
    def __post_init__(self):
        if not self.erstellt_am:
            self.erstellt_am = datetime.now().isoformat()


class AbrechnungsManager:
    """Verwaltet Leistungen und Rechnungen"""
    
    # Standard-Preise für verschiedene Leistungen
    STANDARD_PREISE = {
        LeistungsTyp.BERATUNG: 150.0,      # pro Stunde
        LeistungsTyp.SCHRIFTSATZ: 250.0,   # pauschal
        LeistungsTyp.GERICHT: 500.0,       # pro Termin
        LeistungsTyp.KI_RECHERCHE: 15.0,   # pro Anfrage
        LeistungsTyp.DOKUMENT: 50.0,       # pro Dokument
        LeistungsTyp.KOMMUNIKATION: 25.0,  # pro Vorgang
        LeistungsTyp.SONSTIGE: 100.0,      # pauschal
    }
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            self.data_dir = Path.home() / ".juraconnect"
        else:
            self.data_dir = Path(data_dir)
        
        self.data_dir.mkdir(exist_ok=True)
        self.leistungen_file = self.data_dir / "leistungen.json"
        self.rechnungen_file = self.data_dir / "rechnungen.json"
        
        self._init_files()
    
    def _init_files(self):
        """Dateien initialisieren"""
        if not self.leistungen_file.exists():
            self._save_leistungen({})
        if not self.rechnungen_file.exists():
            self._save_rechnungen({})
    
    def _load_leistungen(self) -> Dict[str, Leistung]:
        """Leistungen laden"""
        with open(self.leistungen_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        result = {}
        for lid, ldata in data.items():
            ldata['typ'] = LeistungsTyp(ldata['typ'])
            result[lid] = Leistung(**ldata)
        return result
    
    def _save_leistungen(self, leistungen: Dict[str, Leistung]):
        """Leistungen speichern"""
        data = {}
        for lid, leistung in leistungen.items():
            ldict = asdict(leistung)
            ldict['typ'] = leistung.typ.value
            data[lid] = ldict
        
        with open(self.leistungen_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def _load_rechnungen(self) -> Dict[str, Rechnung]:
        """Rechnungen laden"""
        with open(self.rechnungen_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        result = {}
        for rid, rdata in data.items():
            rdata['status'] = RechnungsStatus(rdata['status'])
            result[rid] = Rechnung(**rdata)
        return result
    
    def _save_rechnungen(self, rechnungen: Dict[str, Rechnung]):
        """Rechnungen speichern"""
        data = {}
        for rid, rechnung in rechnungen.items():
            rdict = asdict(rechnung)
            rdict['status'] = rechnung.status.value
            data[rid] = rdict
        
        with open(self.rechnungen_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # ==========================================================================
    # Leistungserfassung
    # ==========================================================================
    
    def erfasse_leistung(self, akte_id: str, leistung: str, beschreibung: str,
                         betrag: float = None, typ: LeistungsTyp = None,
                         erstellt_von: str = "") -> Leistung:
        """
        Erfasst eine neue abrechenbare Leistung.
        Wird automatisch bei kostenauslösenden Aktionen aufgerufen.
        """
        # Typ bestimmen
        if typ is None:
            typ = self._bestimme_typ(leistung)
        
        # Betrag bestimmen
        if betrag is None:
            betrag = self.STANDARD_PREISE.get(typ, 100.0)
        
        # Leistung erstellen
        leistung_id = f"L{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        neue_leistung = Leistung(
            id=leistung_id,
            akte_id=akte_id,
            typ=typ,
            beschreibung=f"{leistung}: {beschreibung}",
            betrag=betrag,
            erstellt_von=erstellt_von
        )
        
        # Speichern
        leistungen = self._load_leistungen()
        leistungen[leistung_id] = neue_leistung
        self._save_leistungen(leistungen)
        
        return neue_leistung
    
    def _bestimme_typ(self, leistung: str) -> LeistungsTyp:
        """Leistungstyp aus Beschreibung ableiten"""
        leistung_lower = leistung.lower()
        
        if any(x in leistung_lower for x in ['beratung', 'gespräch', 'besprechung']):
            return LeistungsTyp.BERATUNG
        elif any(x in leistung_lower for x in ['schriftsatz', 'klage', 'antrag']):
            return LeistungsTyp.SCHRIFTSATZ
        elif any(x in leistung_lower for x in ['termin', 'gericht', 'verhandlung']):
            return LeistungsTyp.GERICHT
        elif any(x in leistung_lower for x in ['ki', 'recherche', 'assistent']):
            return LeistungsTyp.KI_RECHERCHE
        elif any(x in leistung_lower for x in ['dokument', 'vertrag', 'zeugnis']):
            return LeistungsTyp.DOKUMENT
        elif any(x in leistung_lower for x in ['email', 'anruf', 'brief']):
            return LeistungsTyp.KOMMUNIKATION
        else:
            return LeistungsTyp.SONSTIGE
    
    def get_leistungen_fuer_akte(self, akte_id: str, 
                                  nur_offen: bool = False) -> List[Leistung]:
        """Alle Leistungen einer Akte abrufen"""
        leistungen = self._load_leistungen()
        result = [l for l in leistungen.values() if l.akte_id == akte_id]
        
        if nur_offen:
            result = [l for l in result if not l.abgerechnet]
        
        return sorted(result, key=lambda x: x.erstellt_am, reverse=True)
    
    def get_offene_summe(self, akte_id: str) -> float:
        """Offene Summe einer Akte"""
        leistungen = self.get_leistungen_fuer_akte(akte_id, nur_offen=True)
        return sum(l.brutto_betrag for l in leistungen)
    
    # ==========================================================================
    # Rechnungserstellung
    # ==========================================================================
    
    def erstelle_rechnung(self, akte_id: str, mandant_name: str, 
                          mandant_adresse: str) -> Rechnung:
        """
        Erstellt eine Rechnung aus allen offenen Leistungen einer Akte.
        """
        # Offene Leistungen holen
        leistungen = self.get_leistungen_fuer_akte(akte_id, nur_offen=True)
        
        if not leistungen:
            raise ValueError("Keine offenen Leistungen vorhanden")
        
        # Summen berechnen
        netto_summe = sum(l.betrag for l in leistungen)
        mwst_summe = sum(l.mwst_betrag for l in leistungen)
        brutto_summe = sum(l.brutto_betrag for l in leistungen)
        
        # Rechnung erstellen
        rechnung_id = f"R{datetime.now().strftime('%Y%m%d%H%M%S')}"
        rechnung = Rechnung(
            id=rechnung_id,
            akte_id=akte_id,
            mandant_name=mandant_name,
            mandant_adresse=mandant_adresse,
            leistungen=[l.id for l in leistungen],
            netto_summe=netto_summe,
            mwst_summe=mwst_summe,
            brutto_summe=brutto_summe
        )
        
        # Rechnung speichern
        rechnungen = self._load_rechnungen()
        rechnungen[rechnung_id] = rechnung
        self._save_rechnungen(rechnungen)
        
        # Leistungen als abgerechnet markieren
        all_leistungen = self._load_leistungen()
        for l in leistungen:
            all_leistungen[l.id].abgerechnet = True
            all_leistungen[l.id].rechnung_id = rechnung_id
        self._save_leistungen(all_leistungen)
        
        return rechnung
    
    def get_rechnung(self, rechnung_id: str) -> Optional[Rechnung]:
        """Einzelne Rechnung abrufen"""
        rechnungen = self._load_rechnungen()
        return rechnungen.get(rechnung_id)
    
    def get_rechnungen_fuer_akte(self, akte_id: str) -> List[Rechnung]:
        """Alle Rechnungen einer Akte"""
        rechnungen = self._load_rechnungen()
        return [r for r in rechnungen.values() if r.akte_id == akte_id]
    
    def rechnung_versenden(self, rechnung_id: str) -> bool:
        """Rechnung als versendet markieren"""
        rechnungen = self._load_rechnungen()
        
        if rechnung_id not in rechnungen:
            return False
        
        rechnungen[rechnung_id].status = RechnungsStatus.VERSENDET
        rechnungen[rechnung_id].versendet_am = datetime.now().isoformat()
        self._save_rechnungen(rechnungen)
        return True
    
    def rechnung_bezahlt(self, rechnung_id: str) -> bool:
        """Rechnung als bezahlt markieren"""
        rechnungen = self._load_rechnungen()
        
        if rechnung_id not in rechnungen:
            return False
        
        rechnungen[rechnung_id].status = RechnungsStatus.BEZAHLT
        rechnungen[rechnung_id].bezahlt_am = datetime.now().isoformat()
        self._save_rechnungen(rechnungen)
        return True
    
    # ==========================================================================
    # Rechnungs-Dokument generieren
    # ==========================================================================
    
    def generiere_rechnungsdokument(self, rechnung_id: str, 
                                     kanzlei_name: str,
                                     kanzlei_adresse: str) -> str:
        """Generiert ein Rechnungsdokument als Text"""
        rechnung = self.get_rechnung(rechnung_id)
        if not rechnung:
            return "Rechnung nicht gefunden"
        
        # Leistungen laden
        all_leistungen = self._load_leistungen()
        leistungen = [all_leistungen[lid] for lid in rechnung.leistungen 
                      if lid in all_leistungen]
        
        # Dokument erstellen
        doc = f"""
{'='*60}
                        RECHNUNG
{'='*60}

Rechnungsnummer: {rechnung.id}
Rechnungsdatum:  {rechnung.erstellt_am[:10]}
Aktenzeichen:    {rechnung.akte_id}

{'─'*60}

VON:
{kanzlei_name}
{kanzlei_adresse}

AN:
{rechnung.mandant_name}
{rechnung.mandant_adresse}

{'─'*60}

LEISTUNGEN:
{'─'*60}
"""
        
        for l in leistungen:
            doc += f"""
{l.erstellt_am[:10]}  {l.beschreibung[:40]}
            Netto: {l.betrag:>10.2f} €
            MwSt:  {l.mwst_betrag:>10.2f} €
"""
        
        doc += f"""
{'─'*60}

ZUSAMMENFASSUNG:
                                    Netto:  {rechnung.netto_summe:>10.2f} €
                                    MwSt (19%): {rechnung.mwst_summe:>10.2f} €
                                    ────────────────────
                                    GESAMT: {rechnung.brutto_summe:>10.2f} €

{'─'*60}

Zahlungsziel: {rechnung.zahlungsziel_tage} Tage

Bankverbindung:
IBAN: DE12 3456 7890 1234 5678 90
BIC: DEUTDEDBXXX

{'='*60}
        Vielen Dank für Ihr Vertrauen!
{'='*60}
"""
        
        return doc


# =============================================================================
# Automatische Erfassung bei Aktionen
# =============================================================================

def erfasse_aktion(akte_id: str, aktion: str, details: str = "", 
                   betrag: float = None):
    """
    Wrapper-Funktion zur einfachen Erfassung von Aktionen.
    Kann als Decorator oder direkt aufgerufen werden.
    """
    from modules.auth import get_current_user, is_demo_mode
    
    # Im Demo-Modus keine echte Erfassung
    if is_demo_mode():
        return None
    
    user = get_current_user()
    username = user.name if user else "System"
    
    mgr = AbrechnungsManager()
    leistung = mgr.erfasse_leistung(
        akte_id=akte_id,
        leistung=aktion,
        beschreibung=details,
        betrag=betrag,
        erstellt_von=username
    )
    
    return leistung


def zeige_kostenhinweis(leistung: Leistung):
    """Zeigt einen Kostenhinweis in Streamlit an"""
    st.info(f"""
    💰 **Kosten erfasst**
    
    {leistung.beschreibung}
    
    **Betrag:** {leistung.brutto_betrag:.2f} € (inkl. MwSt)
    """)


# =============================================================================
# Streamlit-Komponenten
# =============================================================================

def render_kostenübersicht(akte_id: str):
    """Widget für Kostenübersicht einer Akte"""
    st.markdown("### 💰 Kostenübersicht")
    
    mgr = AbrechnungsManager()
    
    # Offene Leistungen
    offene = mgr.get_leistungen_fuer_akte(akte_id, nur_offen=True)
    offene_summe = sum(l.brutto_betrag for l in offene)
    
    # Alle Rechnungen
    rechnungen = mgr.get_rechnungen_fuer_akte(akte_id)
    bezahlt = sum(r.brutto_summe for r in rechnungen if r.status == RechnungsStatus.BEZAHLT)
    offen_rechnung = sum(r.brutto_summe for r in rechnungen if r.status != RechnungsStatus.BEZAHLT)
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Offene Leistungen", f"{offene_summe:.2f} €")
    with col2:
        st.metric("Offene Rechnungen", f"{offen_rechnung:.2f} €")
    with col3:
        st.metric("Bezahlt", f"{bezahlt:.2f} €")
    
    # Details
    if offene:
        with st.expander(f"📋 {len(offene)} offene Leistungen"):
            for l in offene:
                st.markdown(f"- {l.erstellt_am[:10]}: {l.beschreibung} - **{l.brutto_betrag:.2f} €**")


def render_rechnungsstellung(akte_id: str, mandant_name: str, mandant_adresse: str):
    """Widget für Rechnungsstellung"""
    st.markdown("### 📄 Rechnungsstellung")
    
    mgr = AbrechnungsManager()
    offene = mgr.get_leistungen_fuer_akte(akte_id, nur_offen=True)
    
    if not offene:
        st.info("Keine offenen Leistungen zur Abrechnung.")
        return
    
    st.write(f"**{len(offene)} offene Leistungen** bereit zur Abrechnung:")
    
    summe = sum(l.brutto_betrag for l in offene)
    st.metric("Rechnungsbetrag", f"{summe:.2f} €")
    
    if st.button("📄 Rechnung erstellen", type="primary"):
        try:
            rechnung = mgr.erstelle_rechnung(akte_id, mandant_name, mandant_adresse)
            st.success(f"✅ Rechnung {rechnung.id} erstellt!")
            
            # Dokument anzeigen
            doc = mgr.generiere_rechnungsdokument(
                rechnung.id,
                "Kanzlei RHM",
                "Musterstraße 1\n12345 Musterstadt"
            )
            st.code(doc)
            
            st.download_button(
                "📥 Rechnung herunterladen",
                doc,
                file_name=f"rechnung_{rechnung.id}.txt",
                mime="text/plain"
            )
        except ValueError as e:
            st.error(str(e))


def get_abrechnungs_manager() -> AbrechnungsManager:
    """AbrechnungsManager aus Session State"""
    if 'abrechnungs_manager' not in st.session_state:
        st.session_state.abrechnungs_manager = AbrechnungsManager()
    return st.session_state.abrechnungs_manager
