"""
JuraConnect - Kanzlei-Tools
============================
- Kollisionsprüfung (BRAO § 43a Abs. 4)
- beA-Integration (elektronisches Anwaltspostfach)
- Dokumenten-Checkliste für AN/AG

Version: 2.0.0
"""

from datetime import datetime, date
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Set
from enum import Enum
import re


# =============================================================================
# KOLLISIONSPRÜFUNG (BRAO § 43a Abs. 4)
# =============================================================================

@dataclass
class Partei:
    """Eine Partei in einer Akte"""
    id: str = ""
    name: str = ""
    typ: str = ""  # "natürlich" oder "juristisch"
    vorname: str = ""
    firma: str = ""
    strasse: str = ""
    plz: str = ""
    ort: str = ""
    telefon: str = ""
    email: str = ""
    geburtsdatum: str = ""
    steuernummer: str = ""
    handelsregister: str = ""


@dataclass
class KollisionsPruefungErgebnis:
    """Ergebnis einer Kollisionsprüfung"""
    hat_kollision: bool = False
    kollisionen: List[Dict] = field(default_factory=list)
    warnungen: List[str] = field(default_factory=list)
    geprueft_am: datetime = None
    geprueft_gegen: int = 0  # Anzahl geprüfter Akten


class KollisionsPruefer:
    """
    Prüft auf Interessenkollisionen nach BRAO § 43a Abs. 4.
    
    Ein Interessenkonflikt liegt vor, wenn:
    - Derselbe Mandant in verschiedenen Sachen gegensätzliche Interessen hat
    - Die Kanzlei bereits die Gegenseite vertreten hat
    - Ein enger zeitlicher/sachlicher Zusammenhang besteht
    """
    
    def __init__(self):
        self.parteien_index: Dict[str, List[Dict]] = {}  # Normalisierter Name -> Akten
        self.akten: List[Dict] = []
    
    def _normalisiere_name(self, name: str) -> str:
        """Normalisiert einen Namen für den Vergleich."""
        if not name:
            return ""
        
        # Kleinschreibung, Umlaute normalisieren
        name = name.lower()
        name = name.replace("ä", "ae").replace("ö", "oe").replace("ü", "ue")
        name = name.replace("ß", "ss")
        
        # Rechtsformzusätze entfernen
        rechtsformen = [
            "gmbh", "ag", "kg", "ohg", "gbr", "ug", "e.v.", "e.k.",
            "gmbh & co. kg", "gmbh & co kg", "mbh", "gesellschaft"
        ]
        for rf in rechtsformen:
            name = name.replace(rf, "")
        
        # Sonderzeichen und Mehrfachspaces entfernen
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name)
        name = name.strip()
        
        return name
    
    def registriere_akte(
        self,
        akte_id: str,
        akte_name: str,
        mandant: Partei,
        gegner: Optional[Partei] = None,
        rechtsgebiet: str = "",
        angelegt_am: date = None
    ) -> None:
        """Registriert eine Akte für die Kollisionsprüfung."""
        akte_info = {
            "akte_id": akte_id,
            "akte_name": akte_name,
            "mandant": mandant,
            "gegner": gegner,
            "rechtsgebiet": rechtsgebiet,
            "angelegt_am": angelegt_am or date.today()
        }
        self.akten.append(akte_info)
        
        # Mandant indizieren
        if mandant and mandant.name:
            norm_name = self._normalisiere_name(mandant.name)
            if norm_name not in self.parteien_index:
                self.parteien_index[norm_name] = []
            self.parteien_index[norm_name].append({
                "akte": akte_info,
                "rolle": "mandant"
            })
        
        # Gegner indizieren
        if gegner and gegner.name:
            norm_name = self._normalisiere_name(gegner.name)
            if norm_name not in self.parteien_index:
                self.parteien_index[norm_name] = []
            self.parteien_index[norm_name].append({
                "akte": akte_info,
                "rolle": "gegner"
            })
    
    def pruefe_kollision(
        self,
        mandant: Partei,
        gegner: Optional[Partei] = None,
        rechtsgebiet: str = ""
    ) -> KollisionsPruefungErgebnis:
        """
        Prüft auf Interessenkollision bei Neuaufnahme.
        
        Args:
            mandant: Der potenzielle neue Mandant
            gegner: Der Gegner (falls bekannt)
            rechtsgebiet: Rechtsgebiet der Angelegenheit
            
        Returns:
            KollisionsPruefungErgebnis mit allen gefundenen Konflikten
        """
        ergebnis = KollisionsPruefungErgebnis(
            geprueft_am=datetime.now(),
            geprueft_gegen=len(self.akten)
        )
        
        # 1. Prüfe ob Mandant bereits Gegner war
        if mandant and mandant.name:
            norm_mandant = self._normalisiere_name(mandant.name)
            
            if norm_mandant in self.parteien_index:
                for eintrag in self.parteien_index[norm_mandant]:
                    if eintrag["rolle"] == "gegner":
                        ergebnis.hat_kollision = True
                        ergebnis.kollisionen.append({
                            "typ": "mandant_war_gegner",
                            "schwere": "kritisch",
                            "beschreibung": f"'{mandant.name}' war bereits Gegner in Akte '{eintrag['akte']['akte_name']}'",
                            "akte_id": eintrag["akte"]["akte_id"],
                            "akte_name": eintrag["akte"]["akte_name"]
                        })
        
        # 2. Prüfe ob Gegner bereits Mandant war
        if gegner and gegner.name:
            norm_gegner = self._normalisiere_name(gegner.name)
            
            if norm_gegner in self.parteien_index:
                for eintrag in self.parteien_index[norm_gegner]:
                    if eintrag["rolle"] == "mandant":
                        ergebnis.hat_kollision = True
                        ergebnis.kollisionen.append({
                            "typ": "gegner_war_mandant",
                            "schwere": "kritisch",
                            "beschreibung": f"'{gegner.name}' war bereits Mandant in Akte '{eintrag['akte']['akte_name']}'",
                            "akte_id": eintrag["akte"]["akte_id"],
                            "akte_name": eintrag["akte"]["akte_name"]
                        })
        
        # 3. Ähnliche Namen prüfen (fuzzy matching)
        if mandant and mandant.name:
            for norm_name, eintraege in self.parteien_index.items():
                if self._aehnlich(self._normalisiere_name(mandant.name), norm_name):
                    for eintrag in eintraege:
                        if eintrag["rolle"] == "gegner":
                            ergebnis.warnungen.append(
                                f"Ähnlicher Name gefunden: '{mandant.name}' ~ "
                                f"'{eintrag['akte']['gegner'].name if eintrag['akte'].get('gegner') else 'unbekannt'}' "
                                f"(Akte: {eintrag['akte']['akte_name']})"
                            )
        
        return ergebnis
    
    def _aehnlich(self, name1: str, name2: str, schwelle: float = 0.8) -> bool:
        """Prüft ob zwei Namen ähnlich sind (Levenshtein-ähnlich)."""
        if name1 == name2:
            return False  # Exakt gleich wird separat geprüft
        
        if not name1 or not name2:
            return False
        
        # Einfacher Ähnlichkeitstest: Gemeinsame Wörter
        woerter1 = set(name1.split())
        woerter2 = set(name2.split())
        
        if not woerter1 or not woerter2:
            return False
        
        gemeinsam = woerter1 & woerter2
        gesamt = woerter1 | woerter2
        
        if len(gesamt) == 0:
            return False
        
        aehnlichkeit = len(gemeinsam) / len(gesamt)
        return aehnlichkeit >= schwelle
    
    def suche_partei(self, suchbegriff: str) -> List[Dict]:
        """Sucht nach Parteien im Index."""
        ergebnisse = []
        norm_suche = self._normalisiere_name(suchbegriff)
        
        for norm_name, eintraege in self.parteien_index.items():
            if norm_suche in norm_name or norm_name in norm_suche:
                for eintrag in eintraege:
                    ergebnisse.append({
                        "name": eintrag["akte"]["mandant"].name if eintrag["rolle"] == "mandant" 
                                else eintrag["akte"].get("gegner", {}).name if eintrag["akte"].get("gegner") else "",
                        "rolle": eintrag["rolle"],
                        "akte_id": eintrag["akte"]["akte_id"],
                        "akte_name": eintrag["akte"]["akte_name"]
                    })
        
        return ergebnisse
    
    def statistik(self) -> Dict:
        """Gibt Statistiken über die registrierten Parteien."""
        return {
            "anzahl_akten": len(self.akten),
            "anzahl_parteien": len(self.parteien_index),
            "mandanten": sum(
                1 for eintraege in self.parteien_index.values()
                for e in eintraege if e["rolle"] == "mandant"
            ),
            "gegner": sum(
                1 for eintraege in self.parteien_index.values()
                for e in eintraege if e["rolle"] == "gegner"
            )
        }


# =============================================================================
# beA-INTEGRATION (elektronisches Anwaltspostfach)
# =============================================================================

class BeANachrichtTyp(Enum):
    EINGANG = "eingang"
    AUSGANG = "ausgang"
    ENTWURF = "entwurf"


class BeAStatus(Enum):
    UNGELESEN = "ungelesen"
    GELESEN = "gelesen"
    BEARBEITET = "bearbeitet"
    ARCHIVIERT = "archiviert"


@dataclass
class BeANachricht:
    """Eine beA-Nachricht"""
    id: str = ""
    typ: BeANachrichtTyp = BeANachrichtTyp.EINGANG
    betreff: str = ""
    absender: str = ""
    absender_safe_id: str = ""
    empfaenger: str = ""
    empfaenger_safe_id: str = ""
    datum: datetime = None
    aktenzeichen: str = ""
    inhalt: str = ""
    anlagen: List[str] = field(default_factory=list)
    status: BeAStatus = BeAStatus.UNGELESEN
    akte_id: str = ""
    signiert: bool = False
    zustellnachweis: bool = False


class BeAIntegration:
    """
    Simulation der beA-Integration.
    
    In der Produktion würde diese Klasse die echte beA-API anbinden.
    Hier simulieren wir die Funktionalität für Demo-Zwecke.
    """
    
    # Beispiel-Gerichte mit SAFE-IDs
    GERICHTE = {
        "ArbG Frankfurt": "DE.BRAK.12345678.ArbG-Frankfurt",
        "ArbG Berlin": "DE.BRAK.23456789.ArbG-Berlin",
        "ArbG München": "DE.BRAK.34567890.ArbG-Muenchen",
        "ArbG Hamburg": "DE.BRAK.45678901.ArbG-Hamburg",
        "ArbG Köln": "DE.BRAK.56789012.ArbG-Koeln",
        "LAG Frankfurt": "DE.BRAK.67890123.LAG-Frankfurt",
        "LAG Berlin": "DE.BRAK.78901234.LAG-Berlin",
        "BAG Erfurt": "DE.BRAK.89012345.BAG-Erfurt",
    }
    
    def __init__(self, kanzlei_safe_id: str = "DE.BRAK.99999999.Kanzlei"):
        self.kanzlei_safe_id = kanzlei_safe_id
        self.nachrichten: List[BeANachricht] = []
        self.naechste_id = 1
        
        # Demo-Nachrichten erstellen
        self._erstelle_demo_nachrichten()
    
    def _erstelle_demo_nachrichten(self):
        """Erstellt Demo-Nachrichten."""
        demo_nachrichten = [
            {
                "betreff": "Ladung zum Gütetermin - Az. 12 Ca 456/24",
                "absender": "ArbG Frankfurt",
                "absender_safe_id": self.GERICHTE["ArbG Frankfurt"],
                "aktenzeichen": "12 Ca 456/24",
                "inhalt": "Sehr geehrte Damen und Herren,\n\nzu dem o.g. Rechtsstreit wird Gütetermin bestimmt auf:\n\nMittwoch, 15.02.2024, 10:00 Uhr\nSaal 214\n\nMit freundlichen Grüßen\nDas Arbeitsgericht Frankfurt am Main",
                "anlagen": ["Ladung.pdf", "Hinweis_Guetetermin.pdf"]
            },
            {
                "betreff": "Klageerwiderung - Az. 7 Ca 789/24",
                "absender": "RA Müller & Partner",
                "absender_safe_id": "DE.BRAK.11111111.Mueller",
                "aktenzeichen": "7 Ca 789/24",
                "inhalt": "Sehr geehrte Kollegen,\n\nnamens und in Vollmacht des Beklagten wird die Klage mit dem Antrag beantwortet, die Klage abzuweisen...",
                "anlagen": ["Klageerwiderung.pdf", "Anlage_K1.pdf"]
            },
            {
                "betreff": "Urteil verkündet - Az. 3 Ca 123/24",
                "absender": "ArbG Berlin",
                "absender_safe_id": self.GERICHTE["ArbG Berlin"],
                "aktenzeichen": "3 Ca 123/24",
                "inhalt": "Im Namen des Volkes\n\nUrteil\n\nIn dem Rechtsstreit... wird für Recht erkannt:\n\n1. Es wird festgestellt, dass das Arbeitsverhältnis...",
                "anlagen": ["Urteil.pdf"]
            }
        ]
        
        for n in demo_nachrichten:
            self.nachrichten.append(BeANachricht(
                id=f"bea_{self.naechste_id}",
                typ=BeANachrichtTyp.EINGANG,
                betreff=n["betreff"],
                absender=n["absender"],
                absender_safe_id=n["absender_safe_id"],
                empfaenger="Kanzlei",
                empfaenger_safe_id=self.kanzlei_safe_id,
                datum=datetime.now(),
                aktenzeichen=n["aktenzeichen"],
                inhalt=n["inhalt"],
                anlagen=n["anlagen"],
                status=BeAStatus.UNGELESEN
            ))
            self.naechste_id += 1
    
    def hole_posteingang(self, nur_ungelesen: bool = False) -> List[BeANachricht]:
        """Holt alle Nachrichten aus dem Posteingang."""
        nachrichten = [n for n in self.nachrichten if n.typ == BeANachrichtTyp.EINGANG]
        if nur_ungelesen:
            nachrichten = [n for n in nachrichten if n.status == BeAStatus.UNGELESEN]
        return sorted(nachrichten, key=lambda n: n.datum or datetime.min, reverse=True)
    
    def hole_postausgang(self) -> List[BeANachricht]:
        """Holt alle gesendeten Nachrichten."""
        return [n for n in self.nachrichten if n.typ == BeANachrichtTyp.AUSGANG]
    
    def hole_entwuerfe(self) -> List[BeANachricht]:
        """Holt alle Entwürfe."""
        return [n for n in self.nachrichten if n.typ == BeANachrichtTyp.ENTWURF]
    
    def markiere_gelesen(self, nachricht_id: str) -> bool:
        """Markiert eine Nachricht als gelesen."""
        for n in self.nachrichten:
            if n.id == nachricht_id:
                n.status = BeAStatus.GELESEN
                return True
        return False
    
    def erstelle_nachricht(
        self,
        empfaenger: str,
        empfaenger_safe_id: str,
        betreff: str,
        inhalt: str,
        aktenzeichen: str = "",
        anlagen: List[str] = None,
        als_entwurf: bool = False
    ) -> BeANachricht:
        """Erstellt eine neue Nachricht (Entwurf oder zum Senden)."""
        nachricht = BeANachricht(
            id=f"bea_{self.naechste_id}",
            typ=BeANachrichtTyp.ENTWURF if als_entwurf else BeANachrichtTyp.AUSGANG,
            betreff=betreff,
            absender="Kanzlei",
            absender_safe_id=self.kanzlei_safe_id,
            empfaenger=empfaenger,
            empfaenger_safe_id=empfaenger_safe_id,
            datum=datetime.now(),
            aktenzeichen=aktenzeichen,
            inhalt=inhalt,
            anlagen=anlagen or [],
            status=BeAStatus.UNGELESEN
        )
        self.nachrichten.append(nachricht)
        self.naechste_id += 1
        return nachricht
    
    def sende_nachricht(self, nachricht_id: str) -> Tuple[bool, str]:
        """Sendet eine Nachricht (simuliert)."""
        for n in self.nachrichten:
            if n.id == nachricht_id:
                if n.typ == BeANachrichtTyp.ENTWURF:
                    n.typ = BeANachrichtTyp.AUSGANG
                n.datum = datetime.now()
                n.zustellnachweis = True
                return True, "Nachricht erfolgreich gesendet"
        return False, "Nachricht nicht gefunden"
    
    def ordne_akte_zu(self, nachricht_id: str, akte_id: str) -> bool:
        """Ordnet eine Nachricht einer Akte zu."""
        for n in self.nachrichten:
            if n.id == nachricht_id:
                n.akte_id = akte_id
                return True
        return False
    
    def suche_gericht(self, suchbegriff: str) -> List[Dict]:
        """Sucht ein Gericht nach Name."""
        ergebnisse = []
        for name, safe_id in self.GERICHTE.items():
            if suchbegriff.lower() in name.lower():
                ergebnisse.append({"name": name, "safe_id": safe_id})
        return ergebnisse
    
    def statistik(self) -> Dict:
        """Gibt Statistiken über das Postfach."""
        return {
            "eingang_gesamt": len([n for n in self.nachrichten if n.typ == BeANachrichtTyp.EINGANG]),
            "eingang_ungelesen": len([n for n in self.nachrichten if n.typ == BeANachrichtTyp.EINGANG and n.status == BeAStatus.UNGELESEN]),
            "ausgang_gesamt": len([n for n in self.nachrichten if n.typ == BeANachrichtTyp.AUSGANG]),
            "entwuerfe": len([n for n in self.nachrichten if n.typ == BeANachrichtTyp.ENTWURF]),
        }


# =============================================================================
# DOKUMENTEN-CHECKLISTE
# =============================================================================

@dataclass
class ChecklistenItem:
    """Ein Item in der Checkliste"""
    id: str = ""
    titel: str = ""
    beschreibung: str = ""
    kategorie: str = ""
    pflicht: bool = True
    status: str = "fehlend"  # fehlend, teilweise, vorhanden, nicht_zutreffend
    notizen: str = ""
    dokument_id: str = ""  # Verknüpftes Dokument


class DokumentenCheckliste:
    """
    Dokumenten-Checklisten für Arbeitnehmer und Arbeitgeber.
    """
    
    # Checkliste für Arbeitnehmer (z.B. bei Kündigungsschutzklage)
    CHECKLISTE_ARBEITNEHMER = [
        {
            "id": "arbeitsvertrag",
            "titel": "Arbeitsvertrag",
            "beschreibung": "Aktueller Arbeitsvertrag inkl. aller Änderungen und Nachträge",
            "kategorie": "Grundlagen",
            "pflicht": True
        },
        {
            "id": "kuendigung",
            "titel": "Kündigungsschreiben",
            "beschreibung": "Original der Kündigung mit Datum und Unterschrift",
            "kategorie": "Grundlagen",
            "pflicht": True
        },
        {
            "id": "lohnabrechnungen",
            "titel": "Lohnabrechnungen (letzte 12 Monate)",
            "beschreibung": "Zur Berechnung von Abfindung und Streitwert",
            "kategorie": "Finanzen",
            "pflicht": True
        },
        {
            "id": "zeugnis",
            "titel": "Zwischenzeugnis / Arbeitszeugnisse",
            "beschreibung": "Falls vorhanden, auch frühere Zeugnisse",
            "kategorie": "Dokumente",
            "pflicht": False
        },
        {
            "id": "abmahnungen",
            "titel": "Abmahnungen",
            "beschreibung": "Falls Sie Abmahnungen erhalten haben",
            "kategorie": "Dokumente",
            "pflicht": True
        },
        {
            "id": "korrespondenz",
            "titel": "E-Mail-Verkehr mit Arbeitgeber",
            "beschreibung": "Relevante E-Mails zum Kündigungsgrund",
            "kategorie": "Korrespondenz",
            "pflicht": False
        },
        {
            "id": "stellenbeschreibung",
            "titel": "Stellenbeschreibung",
            "beschreibung": "Falls vorhanden",
            "kategorie": "Dokumente",
            "pflicht": False
        },
        {
            "id": "sozialplan",
            "titel": "Sozialplan / Interessenausgleich",
            "beschreibung": "Falls betriebsbedingte Kündigung mit Betriebsrat",
            "kategorie": "Dokumente",
            "pflicht": False
        },
        {
            "id": "betriebsrat",
            "titel": "Anhörung Betriebsrat",
            "beschreibung": "Schreiben zur Betriebsratsanhörung (falls BR vorhanden)",
            "kategorie": "Dokumente",
            "pflicht": True
        },
        {
            "id": "krankmeldungen",
            "titel": "Krankmeldungen",
            "beschreibung": "Falls krankheitsbedingte Kündigung",
            "kategorie": "Medizinisch",
            "pflicht": False
        },
        {
            "id": "schwerbehinderung",
            "titel": "Schwerbehindertenausweis",
            "beschreibung": "Falls Schwerbehinderung vorliegt",
            "kategorie": "Sonderschutz",
            "pflicht": False
        },
        {
            "id": "mutterschutz",
            "titel": "Schwangerschaftsnachweis",
            "beschreibung": "Falls schwanger oder in Elternzeit",
            "kategorie": "Sonderschutz",
            "pflicht": False
        },
        {
            "id": "ausweis",
            "titel": "Personalausweis",
            "beschreibung": "Zur Identifikation",
            "kategorie": "Grundlagen",
            "pflicht": True
        }
    ]
    
    # Checkliste für Arbeitgeber (z.B. bei Kündigung)
    CHECKLISTE_ARBEITGEBER = [
        {
            "id": "arbeitsvertrag",
            "titel": "Arbeitsvertrag des Mitarbeiters",
            "beschreibung": "Inkl. aller Änderungen und Nachträge",
            "kategorie": "Grundlagen",
            "pflicht": True
        },
        {
            "id": "personalakte",
            "titel": "Personalakte",
            "beschreibung": "Vollständige Personalakte des Mitarbeiters",
            "kategorie": "Grundlagen",
            "pflicht": True
        },
        {
            "id": "kuendigungsgrund",
            "titel": "Dokumentation Kündigungsgrund",
            "beschreibung": "Schriftliche Begründung und Beweise",
            "kategorie": "Kündigung",
            "pflicht": True
        },
        {
            "id": "abmahnungen",
            "titel": "Abmahnungen",
            "beschreibung": "Alle erteilten Abmahnungen mit Zugangsnachweis",
            "kategorie": "Kündigung",
            "pflicht": True
        },
        {
            "id": "betriebsrat_anhoerung",
            "titel": "Betriebsratsanhörung (§ 102 BetrVG)",
            "beschreibung": "Anhörungsschreiben und Stellungnahme des BR",
            "kategorie": "Betriebsrat",
            "pflicht": True
        },
        {
            "id": "sozialauswahl",
            "titel": "Sozialauswahl-Dokumentation",
            "beschreibung": "Bei betriebsbedingter Kündigung",
            "kategorie": "Kündigung",
            "pflicht": False
        },
        {
            "id": "organigramm",
            "titel": "Organigramm / Mitarbeiterliste",
            "beschreibung": "Zur Darstellung der Betriebsstruktur",
            "kategorie": "Grundlagen",
            "pflicht": False
        },
        {
            "id": "integrationsamt",
            "titel": "Zustimmung Integrationsamt",
            "beschreibung": "Bei Kündigung schwerbehinderter Mitarbeiter",
            "kategorie": "Sonderschutz",
            "pflicht": False
        },
        {
            "id": "mutterschutz_genehmigung",
            "titel": "Genehmigung Kündigungsschutz",
            "beschreibung": "Bei Kündigung während Schwangerschaft/Elternzeit",
            "kategorie": "Sonderschutz",
            "pflicht": False
        },
        {
            "id": "handelsregister",
            "titel": "Handelsregisterauszug",
            "beschreibung": "Aktueller Auszug",
            "kategorie": "Grundlagen",
            "pflicht": True
        },
        {
            "id": "vollmacht",
            "titel": "Vollmacht für Verfahren",
            "beschreibung": "Unterschriebene Prozessvollmacht",
            "kategorie": "Verfahren",
            "pflicht": True
        }
    ]
    
    def __init__(self, typ: str = "arbeitnehmer"):
        """
        Initialisiert eine Checkliste.
        
        Args:
            typ: "arbeitnehmer" oder "arbeitgeber"
        """
        self.typ = typ
        self.items: List[ChecklistenItem] = []
        self._initialisiere_checkliste()
    
    def _initialisiere_checkliste(self):
        """Initialisiert die Checkliste basierend auf dem Typ."""
        vorlage = (self.CHECKLISTE_ARBEITNEHMER if self.typ == "arbeitnehmer" 
                   else self.CHECKLISTE_ARBEITGEBER)
        
        for item_def in vorlage:
            self.items.append(ChecklistenItem(
                id=item_def["id"],
                titel=item_def["titel"],
                beschreibung=item_def["beschreibung"],
                kategorie=item_def["kategorie"],
                pflicht=item_def["pflicht"],
                status="fehlend"
            ))
    
    def setze_status(self, item_id: str, status: str, notizen: str = "") -> bool:
        """Setzt den Status eines Items."""
        for item in self.items:
            if item.id == item_id:
                item.status = status
                if notizen:
                    item.notizen = notizen
                return True
        return False
    
    def verknuepfe_dokument(self, item_id: str, dokument_id: str) -> bool:
        """Verknüpft ein Dokument mit einem Checklisten-Item."""
        for item in self.items:
            if item.id == item_id:
                item.dokument_id = dokument_id
                item.status = "vorhanden"
                return True
        return False
    
    def fortschritt(self) -> Dict:
        """Berechnet den Fortschritt der Checkliste."""
        gesamt = len(self.items)
        pflicht = [i for i in self.items if i.pflicht]
        
        vorhanden = len([i for i in self.items if i.status == "vorhanden"])
        pflicht_vorhanden = len([i for i in pflicht if i.status in ["vorhanden", "nicht_zutreffend"]])
        
        return {
            "gesamt": gesamt,
            "vorhanden": vorhanden,
            "prozent": round(vorhanden / gesamt * 100) if gesamt > 0 else 0,
            "pflicht_gesamt": len(pflicht),
            "pflicht_vorhanden": pflicht_vorhanden,
            "pflicht_prozent": round(pflicht_vorhanden / len(pflicht) * 100) if pflicht else 100,
            "fehlend_pflicht": [i for i in pflicht if i.status == "fehlend"]
        }
    
    def nach_kategorie(self) -> Dict[str, List[ChecklistenItem]]:
        """Gruppiert Items nach Kategorie."""
        kategorien = {}
        for item in self.items:
            if item.kategorie not in kategorien:
                kategorien[item.kategorie] = []
            kategorien[item.kategorie].append(item)
        return kategorien
    
    def fehlende_pflichtdokumente(self) -> List[ChecklistenItem]:
        """Gibt alle fehlenden Pflichtdokumente zurück."""
        return [i for i in self.items if i.pflicht and i.status == "fehlend"]
    
    def export_als_text(self) -> str:
        """Exportiert die Checkliste als Text."""
        lines = [
            f"Dokumenten-Checkliste ({self.typ.upper()})",
            "=" * 50,
            ""
        ]
        
        fortschritt = self.fortschritt()
        lines.append(f"Fortschritt: {fortschritt['prozent']}% ({fortschritt['vorhanden']}/{fortschritt['gesamt']})")
        lines.append(f"Pflichtdokumente: {fortschritt['pflicht_prozent']}% ({fortschritt['pflicht_vorhanden']}/{fortschritt['pflicht_gesamt']})")
        lines.append("")
        
        for kategorie, items in self.nach_kategorie().items():
            lines.append(f"\n[{kategorie}]")
            for item in items:
                status_symbol = {
                    "vorhanden": "✅",
                    "teilweise": "⚠️",
                    "fehlend": "❌",
                    "nicht_zutreffend": "➖"
                }.get(item.status, "❓")
                
                pflicht_marker = " *" if item.pflicht else ""
                lines.append(f"  {status_symbol} {item.titel}{pflicht_marker}")
        
        lines.append("\n* = Pflichtdokument")
        return "\n".join(lines)
