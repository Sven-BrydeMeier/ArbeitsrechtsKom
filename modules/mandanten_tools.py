"""
JuraConnect - Mandanten-Tools
==============================
- Mandanten-Checkliste (interaktiver Gesprächsleitfaden für Erstberatung)
- Druck- & Versandfunktion (PDF-Export, E-Mail, beA, Post)

Version: 2.0.0
"""

from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import json
import os
import base64


# =============================================================================
# MANDANTEN-CHECKLISTE (Interaktiver Gesprächsleitfaden)
# =============================================================================

class FrageTyp(Enum):
    TEXT = "text"
    ZAHL = "zahl"
    DATUM = "datum"
    AUSWAHL = "auswahl"
    MEHRFACH = "mehrfach"
    JANEIN = "janein"


@dataclass
class ChecklistenFrage:
    """Eine einzelne Frage in der Checkliste"""
    id: str
    kategorie: str
    frage: str
    typ: FrageTyp
    optionen: List[str] = field(default_factory=list)  # Für Auswahl/Mehrfach
    pflicht: bool = True
    hilfetext: str = ""
    antwort: any = None
    folgefragen: Dict[str, List[str]] = field(default_factory=dict)  # Bedingte Fragen


@dataclass
class ChecklistenErgebnis:
    """Ergebnis einer ausgefüllten Checkliste"""
    mandant_name: str = ""
    erstellt_am: datetime = None
    antworten: Dict[str, any] = field(default_factory=dict)
    zusammenfassung: str = ""
    naechste_schritte: List[str] = field(default_factory=list)
    risikobewertung: str = ""
    empfohlene_dokumente: List[str] = field(default_factory=list)


class MandantenCheckliste:
    """
    Interaktiver Gesprächsleitfaden für die Erstberatung im Arbeitsrecht.
    
    Features:
    - Strukturierte Fragebögen
    - Bedingte Folgefragen
    - Automatische Zusammenfassung
    - Risikobewertung
    - Dokumentenempfehlungen
    """
    
    def __init__(self, typ: str = "kuendigung"):
        """
        Args:
            typ: Art der Beratung (kuendigung, aufhebung, zeugnis, abmahnung, lohn)
        """
        self.typ = typ
        self.fragen: List[ChecklistenFrage] = []
        self.aktuelle_frage_index = 0
        self._lade_fragen()
    
    def _lade_fragen(self):
        """Lädt die Fragen für den gewählten Beratungstyp."""
        if self.typ == "kuendigung":
            self._lade_kuendigungsfragen()
        elif self.typ == "aufhebung":
            self._lade_aufhebungsfragen()
        elif self.typ == "zeugnis":
            self._lade_zeugnisfragen()
        elif self.typ == "abmahnung":
            self._lade_abmahnungsfragen()
        elif self.typ == "lohn":
            self._lade_lohnfragen()
        else:
            self._lade_kuendigungsfragen()  # Default
    
    def _lade_kuendigungsfragen(self):
        """Fragen für Kündigungsberatung."""
        self.fragen = [
            # KATEGORIE: Persönliche Daten
            ChecklistenFrage(
                id="name",
                kategorie="Persönliche Daten",
                frage="Wie heißen Sie vollständig?",
                typ=FrageTyp.TEXT,
                hilfetext="Vor- und Nachname"
            ),
            ChecklistenFrage(
                id="geburtsdatum",
                kategorie="Persönliche Daten",
                frage="Wann sind Sie geboren?",
                typ=FrageTyp.DATUM,
                hilfetext="Für Berechnung des Alters (relevant für Kündigungsfrist)"
            ),
            ChecklistenFrage(
                id="familienstand",
                kategorie="Persönliche Daten",
                frage="Wie ist Ihr Familienstand?",
                typ=FrageTyp.AUSWAHL,
                optionen=["Ledig", "Verheiratet", "Geschieden", "Verwitwet", "Eingetragene Lebenspartnerschaft"]
            ),
            ChecklistenFrage(
                id="unterhaltspflichten",
                kategorie="Persönliche Daten",
                frage="Haben Sie Unterhaltspflichten (Kinder, Partner)?",
                typ=FrageTyp.ZAHL,
                hilfetext="Anzahl der unterhaltsberechtigten Personen"
            ),
            ChecklistenFrage(
                id="schwerbehinderung",
                kategorie="Persönliche Daten",
                frage="Haben Sie einen Schwerbehindertenausweis oder Gleichstellung?",
                typ=FrageTyp.AUSWAHL,
                optionen=["Nein", "Ja, GdB 50+", "Ja, gleichgestellt (GdB 30-50)", "Antrag läuft"],
                folgefragen={"Ja, GdB 50+": ["schwerbehinderung_gdb"], "Ja, gleichgestellt (GdB 30-50)": ["schwerbehinderung_gdb"]}
            ),
            ChecklistenFrage(
                id="schwerbehinderung_gdb",
                kategorie="Persönliche Daten",
                frage="Wie hoch ist der Grad der Behinderung (GdB)?",
                typ=FrageTyp.ZAHL,
                pflicht=False,
                hilfetext="z.B. 50, 60, 70..."
            ),
            
            # KATEGORIE: Arbeitsverhältnis
            ChecklistenFrage(
                id="arbeitgeber",
                kategorie="Arbeitsverhältnis",
                frage="Wie heißt Ihr Arbeitgeber (Firma)?",
                typ=FrageTyp.TEXT
            ),
            ChecklistenFrage(
                id="eintritt",
                kategorie="Arbeitsverhältnis",
                frage="Wann haben Sie dort angefangen zu arbeiten?",
                typ=FrageTyp.DATUM,
                hilfetext="Datum des Arbeitsbeginns"
            ),
            ChecklistenFrage(
                id="position",
                kategorie="Arbeitsverhältnis",
                frage="Welche Position/Tätigkeit haben Sie?",
                typ=FrageTyp.TEXT
            ),
            ChecklistenFrage(
                id="bruttogehalt",
                kategorie="Arbeitsverhältnis",
                frage="Wie hoch ist Ihr monatliches Bruttogehalt?",
                typ=FrageTyp.ZAHL,
                hilfetext="Durchschnitt der letzten 12 Monate inkl. Zulagen"
            ),
            ChecklistenFrage(
                id="betriebsgroesse",
                kategorie="Arbeitsverhältnis",
                frage="Wie viele Mitarbeiter hat der Betrieb insgesamt?",
                typ=FrageTyp.AUSWAHL,
                optionen=["Bis 10", "11-50", "51-200", "201-500", "Über 500", "Weiß ich nicht"],
                hilfetext="Wichtig für KSchG-Anwendbarkeit"
            ),
            ChecklistenFrage(
                id="betriebsrat",
                kategorie="Arbeitsverhältnis",
                frage="Gibt es einen Betriebsrat?",
                typ=FrageTyp.JANEIN
            ),
            ChecklistenFrage(
                id="tarifvertrag",
                kategorie="Arbeitsverhältnis",
                frage="Gilt ein Tarifvertrag?",
                typ=FrageTyp.AUSWAHL,
                optionen=["Nein", "Ja", "Weiß ich nicht"],
                hilfetext="Kann andere Kündigungsfristen vorsehen"
            ),
            
            # KATEGORIE: Kündigung
            ChecklistenFrage(
                id="kuendigung_erhalten",
                kategorie="Kündigung",
                frage="Haben Sie die Kündigung bereits erhalten?",
                typ=FrageTyp.JANEIN,
                folgefragen={"Ja": ["kuendigung_datum", "kuendigung_art", "kuendigung_grund"]}
            ),
            ChecklistenFrage(
                id="kuendigung_datum",
                kategorie="Kündigung",
                frage="Wann haben Sie die Kündigung erhalten (Zugang)?",
                typ=FrageTyp.DATUM,
                pflicht=False,
                hilfetext="Datum des Briefkasteneinwurfs oder persönlicher Übergabe"
            ),
            ChecklistenFrage(
                id="kuendigung_art",
                kategorie="Kündigung",
                frage="Um welche Art von Kündigung handelt es sich?",
                typ=FrageTyp.AUSWAHL,
                optionen=["Ordentliche Kündigung", "Außerordentliche (fristlose) Kündigung", "Änderungskündigung", "Weiß ich nicht"],
                pflicht=False
            ),
            ChecklistenFrage(
                id="kuendigung_grund",
                kategorie="Kündigung",
                frage="Welcher Kündigungsgrund wurde genannt?",
                typ=FrageTyp.AUSWAHL,
                optionen=["Kein Grund genannt", "Betriebsbedingt", "Verhaltensbedingt", "Personenbedingt (Krankheit)", "Sonstiger Grund"],
                pflicht=False,
                folgefragen={"Verhaltensbedingt": ["abmahnung_vorhanden"]}
            ),
            ChecklistenFrage(
                id="abmahnung_vorhanden",
                kategorie="Kündigung",
                frage="Gab es vorher eine Abmahnung wegen des gleichen Verhaltens?",
                typ=FrageTyp.JANEIN,
                pflicht=False
            ),
            
            # KATEGORIE: Sonderschutz
            ChecklistenFrage(
                id="schwangerschaft",
                kategorie="Sonderkündigungsschutz",
                frage="Sind Sie schwanger oder haben Sie in den letzten 4 Monaten entbunden?",
                typ=FrageTyp.JANEIN
            ),
            ChecklistenFrage(
                id="elternzeit",
                kategorie="Sonderkündigungsschutz",
                frage="Befinden Sie sich in Elternzeit oder haben Sie diese beantragt?",
                typ=FrageTyp.JANEIN
            ),
            ChecklistenFrage(
                id="betriebsratsmitglied",
                kategorie="Sonderkündigungsschutz",
                frage="Sind Sie Mitglied des Betriebsrats oder einer anderen Arbeitnehmervertretung?",
                typ=FrageTyp.JANEIN
            ),
            ChecklistenFrage(
                id="datenschutzbeauftragter",
                kategorie="Sonderkündigungsschutz",
                frage="Sind Sie Datenschutzbeauftragter?",
                typ=FrageTyp.JANEIN
            ),
            
            # KATEGORIE: Ziele
            ChecklistenFrage(
                id="ziel",
                kategorie="Ziele & Wünsche",
                frage="Was ist Ihr primäres Ziel?",
                typ=FrageTyp.AUSWAHL,
                optionen=[
                    "Arbeitsplatz behalten",
                    "Möglichst hohe Abfindung",
                    "Gutes Zeugnis",
                    "Schnelle Einigung",
                    "Noch unentschieden"
                ]
            ),
            ChecklistenFrage(
                id="neue_stelle",
                kategorie="Ziele & Wünsche",
                frage="Haben Sie bereits eine neue Stelle in Aussicht?",
                typ=FrageTyp.JANEIN
            ),
            ChecklistenFrage(
                id="rechtsschutz",
                kategorie="Kosten & Versicherung",
                frage="Haben Sie eine Rechtsschutzversicherung mit Arbeitsrecht?",
                typ=FrageTyp.AUSWAHL,
                optionen=["Ja", "Nein", "Weiß ich nicht"],
                hilfetext="Die meisten Rechtsschutzversicherungen decken Arbeitsrecht ab"
            ),
        ]
    
    def _lade_aufhebungsfragen(self):
        """Fragen für Aufhebungsvertragsberatung."""
        self.fragen = [
            ChecklistenFrage(
                id="name", kategorie="Persönliche Daten",
                frage="Wie heißen Sie?", typ=FrageTyp.TEXT
            ),
            ChecklistenFrage(
                id="aufhebung_angeboten", kategorie="Aufhebungsvertrag",
                frage="Wurde Ihnen ein Aufhebungsvertrag angeboten?",
                typ=FrageTyp.JANEIN,
                folgefragen={"Ja": ["abfindung_hoehe", "freistellung"]}
            ),
            ChecklistenFrage(
                id="abfindung_hoehe", kategorie="Aufhebungsvertrag",
                frage="Welche Abfindungshöhe wurde angeboten?",
                typ=FrageTyp.ZAHL, pflicht=False
            ),
            ChecklistenFrage(
                id="freistellung", kategorie="Aufhebungsvertrag",
                frage="Ist eine bezahlte Freistellung vorgesehen?",
                typ=FrageTyp.JANEIN, pflicht=False
            ),
            ChecklistenFrage(
                id="bedenkzeit", kategorie="Aufhebungsvertrag",
                frage="Wie viel Bedenkzeit haben Sie?",
                typ=FrageTyp.TEXT,
                hilfetext="z.B. 'bis Freitag', '1 Woche'"
            ),
            ChecklistenFrage(
                id="kuendigung_droht", kategorie="Aufhebungsvertrag",
                frage="Wurde Ihnen mit Kündigung gedroht, falls Sie nicht unterschreiben?",
                typ=FrageTyp.JANEIN
            ),
        ]
    
    def _lade_zeugnisfragen(self):
        """Fragen für Zeugnisberatung."""
        self.fragen = [
            ChecklistenFrage(
                id="name", kategorie="Persönliche Daten",
                frage="Wie heißen Sie?", typ=FrageTyp.TEXT
            ),
            ChecklistenFrage(
                id="zeugnis_erhalten", kategorie="Zeugnis",
                frage="Haben Sie bereits ein Zeugnis erhalten?",
                typ=FrageTyp.JANEIN
            ),
            ChecklistenFrage(
                id="zeugnis_note", kategorie="Zeugnis",
                frage="Wie bewerten Sie die Gesamtnote des Zeugnisses?",
                typ=FrageTyp.AUSWAHL,
                optionen=["Sehr gut", "Gut", "Befriedigend", "Ausreichend", "Mangelhaft", "Weiß ich nicht"]
            ),
            ChecklistenFrage(
                id="zeugnis_probleme", kategorie="Zeugnis",
                frage="Was stört Sie an dem Zeugnis?",
                typ=FrageTyp.MEHRFACH,
                optionen=["Note zu schlecht", "Tätigkeiten falsch", "Geheimcodes vermutet", "Fehlende Tätigkeiten", "Formfehler", "Sonstiges"]
            ),
        ]
    
    def _lade_abmahnungsfragen(self):
        """Fragen für Abmahnungsberatung."""
        self.fragen = [
            ChecklistenFrage(
                id="name", kategorie="Persönliche Daten",
                frage="Wie heißen Sie?", typ=FrageTyp.TEXT
            ),
            ChecklistenFrage(
                id="abmahnung_datum", kategorie="Abmahnung",
                frage="Wann haben Sie die Abmahnung erhalten?",
                typ=FrageTyp.DATUM
            ),
            ChecklistenFrage(
                id="abmahnung_vorwurf", kategorie="Abmahnung",
                frage="Welcher Vorwurf wird Ihnen gemacht?",
                typ=FrageTyp.TEXT
            ),
            ChecklistenFrage(
                id="vorwurf_berechtigt", kategorie="Abmahnung",
                frage="Ist der Vorwurf Ihrer Meinung nach berechtigt?",
                typ=FrageTyp.AUSWAHL,
                optionen=["Ja, vollständig", "Teilweise", "Nein, unberechtigt"]
            ),
            ChecklistenFrage(
                id="fruhere_abmahnungen", kategorie="Abmahnung",
                frage="Gab es frühere Abmahnungen?",
                typ=FrageTyp.ZAHL
            ),
        ]
    
    def _lade_lohnfragen(self):
        """Fragen für Lohn-/Gehaltsberatung."""
        self.fragen = [
            ChecklistenFrage(
                id="name", kategorie="Persönliche Daten",
                frage="Wie heißen Sie?", typ=FrageTyp.TEXT
            ),
            ChecklistenFrage(
                id="lohn_problem", kategorie="Lohn",
                frage="Was ist das Problem?",
                typ=FrageTyp.MEHRFACH,
                optionen=["Lohn nicht gezahlt", "Lohn zu spät", "Lohn zu niedrig", "Überstunden nicht bezahlt", "Zulagen fehlen", "Sonstiges"]
            ),
            ChecklistenFrage(
                id="offener_betrag", kategorie="Lohn",
                frage="Wie hoch ist der offene Betrag (brutto)?",
                typ=FrageTyp.ZAHL
            ),
            ChecklistenFrage(
                id="zeitraum", kategorie="Lohn",
                frage="Für welchen Zeitraum?",
                typ=FrageTyp.TEXT,
                hilfetext="z.B. 'Januar bis März 2024'"
            ),
        ]
    
    def get_aktuelle_frage(self) -> Optional[ChecklistenFrage]:
        """Gibt die aktuelle Frage zurück."""
        if self.aktuelle_frage_index < len(self.fragen):
            return self.fragen[self.aktuelle_frage_index]
        return None
    
    def beantworte_frage(self, antwort: any) -> bool:
        """
        Speichert eine Antwort und geht zur nächsten Frage.
        
        Returns:
            True wenn weitere Fragen vorhanden, False wenn fertig
        """
        if self.aktuelle_frage_index < len(self.fragen):
            self.fragen[self.aktuelle_frage_index].antwort = antwort
            self.aktuelle_frage_index += 1
            return self.aktuelle_frage_index < len(self.fragen)
        return False
    
    def get_fortschritt(self) -> Tuple[int, int]:
        """Gibt (beantwortete, gesamt) zurück."""
        beantwortet = sum(1 for f in self.fragen if f.antwort is not None)
        return (beantwortet, len(self.fragen))
    
    def get_antworten_nach_kategorie(self) -> Dict[str, List[Tuple[str, any]]]:
        """Gruppiert die Antworten nach Kategorie."""
        kategorien = {}
        for frage in self.fragen:
            if frage.antwort is not None:
                if frage.kategorie not in kategorien:
                    kategorien[frage.kategorie] = []
                kategorien[frage.kategorie].append((frage.frage, frage.antwort))
        return kategorien
    
    def erstelle_ergebnis(self) -> ChecklistenErgebnis:
        """Erstellt das Ergebnis der ausgefüllten Checkliste."""
        ergebnis = ChecklistenErgebnis()
        ergebnis.erstellt_am = datetime.now()
        
        # Antworten sammeln
        for frage in self.fragen:
            if frage.antwort is not None:
                ergebnis.antworten[frage.id] = frage.antwort
        
        # Name
        ergebnis.mandant_name = ergebnis.antworten.get("name", "Unbekannt")
        
        # Zusammenfassung und Empfehlungen generieren
        ergebnis.zusammenfassung = self._erstelle_zusammenfassung(ergebnis.antworten)
        ergebnis.naechste_schritte = self._erstelle_naechste_schritte(ergebnis.antworten)
        ergebnis.risikobewertung = self._bewerte_risiko(ergebnis.antworten)
        ergebnis.empfohlene_dokumente = self._empfehle_dokumente(ergebnis.antworten)
        
        return ergebnis
    
    def _erstelle_zusammenfassung(self, antworten: Dict) -> str:
        """Erstellt eine textuelle Zusammenfassung."""
        text = f"## Mandanten-Checkliste: {self.typ.upper()}\n\n"
        text += f"**Mandant:** {antworten.get('name', 'N/A')}\n"
        text += f"**Erstellt:** {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        
        if self.typ == "kuendigung":
            text += "### Sachverhalt\n"
            text += f"- Arbeitgeber: {antworten.get('arbeitgeber', 'N/A')}\n"
            text += f"- Position: {antworten.get('position', 'N/A')}\n"
            text += f"- Bruttogehalt: {antworten.get('bruttogehalt', 'N/A')} €\n"
            text += f"- Betriebsgröße: {antworten.get('betriebsgroesse', 'N/A')}\n"
            text += f"- Kündigung erhalten: {antworten.get('kuendigung_erhalten', 'N/A')}\n"
            if antworten.get('kuendigung_datum'):
                text += f"- Kündigungszugang: {antworten.get('kuendigung_datum')}\n"
        
        return text
    
    def _erstelle_naechste_schritte(self, antworten: Dict) -> List[str]:
        """Erstellt empfohlene nächste Schritte."""
        schritte = []
        
        if self.typ == "kuendigung":
            if antworten.get("kuendigung_erhalten") == "Ja":
                schritte.append("⏰ DRINGEND: Klagefrist (3 Wochen) prüfen!")
                schritte.append("📋 Kündigungsschreiben analysieren")
            
            if antworten.get("betriebsrat") == "Ja":
                schritte.append("📝 Betriebsratsanhörung anfordern (§ 102 BetrVG)")
            
            if antworten.get("schwerbehinderung") not in [None, "Nein"]:
                schritte.append("🔍 Zustimmung des Integrationsamts prüfen")
            
            if antworten.get("rechtsschutz") == "Ja":
                schritte.append("📞 Rechtsschutzversicherung kontaktieren (Deckungszusage)")
            
            schritte.append("📄 Alle relevanten Dokumente zusammenstellen")
            schritte.append("💼 Kündigungsschutzklage vorbereiten")
        
        return schritte
    
    def _bewerte_risiko(self, antworten: Dict) -> str:
        """Bewertet das Risiko/die Erfolgsaussichten."""
        score = 50  # Neutral
        
        if self.typ == "kuendigung":
            # Positive Faktoren (für AN)
            if antworten.get("betriebsgroesse") not in ["Bis 10"]:
                score += 15  # KSchG anwendbar
            
            if antworten.get("schwerbehinderung") not in [None, "Nein"]:
                score += 20
            
            if antworten.get("schwangerschaft") == "Ja":
                score += 30
            
            if antworten.get("elternzeit") == "Ja":
                score += 25
            
            if antworten.get("betriebsratsmitglied") == "Ja":
                score += 25
            
            if antworten.get("betriebsrat") == "Ja":
                score += 5  # BR muss angehört werden
            
            if antworten.get("kuendigung_grund") == "Verhaltensbedingt" and antworten.get("abmahnung_vorhanden") == "Nein":
                score += 15
        
        if score >= 70:
            return "🟢 Gute Erfolgsaussichten"
        elif score >= 50:
            return "🟡 Moderate Erfolgsaussichten"
        else:
            return "🔴 Schwierige Ausgangslage"
    
    def _empfehle_dokumente(self, antworten: Dict) -> List[str]:
        """Empfiehlt benötigte Dokumente."""
        dokumente = []
        
        if self.typ == "kuendigung":
            dokumente.append("Kündigungsschreiben (Original)")
            dokumente.append("Arbeitsvertrag")
            dokumente.append("Letzte 3 Gehaltsabrechnungen")
            
            if antworten.get("abmahnung_vorhanden") == "Ja":
                dokumente.append("Abmahnungsschreiben")
            
            if antworten.get("schwerbehinderung") not in [None, "Nein"]:
                dokumente.append("Schwerbehindertenausweis / Gleichstellungsbescheid")
            
            if antworten.get("schwangerschaft") == "Ja":
                dokumente.append("Mutterpass / Schwangerschaftsnachweis")
            
            if antworten.get("tarifvertrag") == "Ja":
                dokumente.append("Tarifvertrag (falls vorhanden)")
            
            if antworten.get("rechtsschutz") == "Ja":
                dokumente.append("Rechtsschutz-Versicherungspolice")
        
        return dokumente


# =============================================================================
# DRUCK- & VERSANDFUNKTION
# =============================================================================

class VersandTyp(Enum):
    PDF_DOWNLOAD = "pdf_download"
    EMAIL = "email"
    BEA = "bea"
    FAX = "fax"
    POST = "post"


@dataclass
class VersandAuftrag:
    """Ein Versandauftrag"""
    id: str
    dokument_name: str
    dokument_inhalt: str  # HTML oder Text
    versand_typ: VersandTyp
    empfaenger: str
    betreff: str = ""
    aktenzeichen: str = ""
    erstellt_am: datetime = None
    gesendet_am: datetime = None
    status: str = "entwurf"  # entwurf, wartend, gesendet, fehler


class DruckVersandManager:
    """
    Verwaltet Druck- und Versandfunktionen.
    
    Features:
    - PDF-Export
    - E-Mail-Versand (Simulation)
    - beA-Versand (Simulation)
    - Fax (Simulation)
    - Postalischer Versand (Vorbereitung)
    """
    
    def __init__(self):
        self.auftraege: List[VersandAuftrag] = []
        self.vorlagen: Dict[str, str] = self._lade_vorlagen()
    
    def _lade_vorlagen(self) -> Dict[str, str]:
        """Lädt Dokumentvorlagen."""
        return {
            "kuendigungsschutzklage": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; }
        h1 { text-align: center; }
        .header { margin-bottom: 30px; }
        .absender { margin-bottom: 20px; }
        .empfaenger { margin-bottom: 20px; }
        .betreff { font-weight: bold; margin: 20px 0; }
        .inhalt { line-height: 1.6; }
        .unterschrift { margin-top: 50px; }
    </style>
</head>
<body>
    <div class="header">
        <div class="absender">
            {absender_name}<br>
            {absender_strasse}<br>
            {absender_plz_ort}
        </div>
        
        <div class="empfaenger">
            Arbeitsgericht {gericht_ort}<br>
            {gericht_strasse}<br>
            {gericht_plz_ort}
        </div>
    </div>
    
    <p>Datum: {datum}</p>
    
    <p class="betreff">Kündigungsschutzklage</p>
    
    <p><strong>{klaeger_name}</strong></p>
    <p>- Kläger/in -</p>
    <p>gegen</p>
    <p><strong>{beklagter_name}</strong><br>
    {beklagter_adresse}</p>
    <p>- Beklagte/r -</p>
    
    <p class="betreff">wegen: Feststellung der Unwirksamkeit einer Kündigung</p>
    
    <div class="inhalt">
        <p>Namens und in Vollmacht des Klägers/der Klägerin erhebe ich Klage und beantrage:</p>
        
        <ol>
            <li>Es wird festgestellt, dass das zwischen den Parteien bestehende Arbeitsverhältnis 
            durch die Kündigung vom {kuendigung_datum} nicht aufgelöst worden ist.</li>
            
            <li>Es wird festgestellt, dass das Arbeitsverhältnis auch nicht durch andere 
            Beendigungstatbestände endet, sondern zu unveränderten Bedingungen fortbesteht.</li>
            
            <li>Die Beklagte wird verurteilt, den Kläger/die Klägerin bis zum rechtskräftigen 
            Abschluss des Rechtsstreits zu unveränderten Arbeitsbedingungen als 
            {position} weiterzubeschäftigen.</li>
        </ol>
        
        <p><strong>Begründung:</strong></p>
        
        <p>Der Kläger/Die Klägerin ist seit dem {eintritt_datum} bei der Beklagten als 
        {position} beschäftigt. Das monatliche Bruttogehalt beträgt {bruttogehalt} Euro.</p>
        
        <p>Mit Schreiben vom {kuendigung_datum}, zugegangen am {zugang_datum}, 
        kündigte die Beklagte das Arbeitsverhältnis.</p>
        
        <p>Die Kündigung ist unwirksam.</p>
        
        <p>{begruendung}</p>
    </div>
    
    <div class="unterschrift">
        <p>________________________</p>
        <p>{absender_name}</p>
    </div>
</body>
</html>
            """,
            "abmahnung_gegendarstellung": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
    </style>
</head>
<body>
    <p>{absender_name}<br>{absender_adresse}</p>
    
    <p>{empfaenger_name}<br>{empfaenger_adresse}</p>
    
    <p>Datum: {datum}</p>
    
    <p><strong>Gegendarstellung zur Abmahnung vom {abmahnung_datum}</strong></p>
    
    <p>Sehr geehrte Damen und Herren,</p>
    
    <p>gegen die mir erteilte Abmahnung vom {abmahnung_datum} lege ich hiermit 
    Gegendarstellung ein und bitte um Aufnahme in meine Personalakte.</p>
    
    <p>{gegendarstellung_text}</p>
    
    <p>Ich bitte um Entfernung der Abmahnung aus meiner Personalakte.</p>
    
    <p>Mit freundlichen Grüßen</p>
    
    <p>{absender_name}</p>
</body>
</html>
            """,
            "brief_standard": """
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; line-height: 1.6; }
    </style>
</head>
<body>
    <p>{absender}</p>
    
    <p>{empfaenger}</p>
    
    <p>{ort}, {datum}</p>
    
    <p><strong>{betreff}</strong></p>
    
    <p>{anrede}</p>
    
    <p>{inhalt}</p>
    
    <p>Mit freundlichen Grüßen</p>
    
    <p>{unterschrift}</p>
</body>
</html>
            """
        }
    
    def erstelle_pdf(self, vorlage_name: str, daten: Dict) -> str:
        """
        Erstellt ein PDF aus einer Vorlage.
        
        Args:
            vorlage_name: Name der Vorlage
            daten: Platzhalter-Daten
            
        Returns:
            HTML-String (in echter Anwendung: PDF-Bytes)
        """
        if vorlage_name not in self.vorlagen:
            return ""
        
        html = self.vorlagen[vorlage_name]
        
        # Platzhalter ersetzen
        for key, value in daten.items():
            html = html.replace("{" + key + "}", str(value))
        
        return html
    
    def erstelle_versandauftrag(
        self,
        dokument_name: str,
        dokument_inhalt: str,
        versand_typ: VersandTyp,
        empfaenger: str,
        betreff: str = "",
        aktenzeichen: str = ""
    ) -> VersandAuftrag:
        """Erstellt einen neuen Versandauftrag."""
        auftrag = VersandAuftrag(
            id=f"VA-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            dokument_name=dokument_name,
            dokument_inhalt=dokument_inhalt,
            versand_typ=versand_typ,
            empfaenger=empfaenger,
            betreff=betreff,
            aktenzeichen=aktenzeichen,
            erstellt_am=datetime.now(),
            status="entwurf"
        )
        self.auftraege.append(auftrag)
        return auftrag
    
    def sende_auftrag(self, auftrag_id: str) -> Tuple[bool, str]:
        """
        Sendet einen Auftrag (Simulation).
        
        Returns:
            (erfolg, nachricht)
        """
        auftrag = next((a for a in self.auftraege if a.id == auftrag_id), None)
        if not auftrag:
            return (False, "Auftrag nicht gefunden")
        
        # Simulation des Versands
        if auftrag.versand_typ == VersandTyp.PDF_DOWNLOAD:
            auftrag.status = "bereit"
            return (True, "PDF zum Download bereit")
        
        elif auftrag.versand_typ == VersandTyp.EMAIL:
            # Simulation
            auftrag.gesendet_am = datetime.now()
            auftrag.status = "gesendet"
            return (True, f"E-Mail an {auftrag.empfaenger} gesendet (Simulation)")
        
        elif auftrag.versand_typ == VersandTyp.BEA:
            # Simulation
            auftrag.gesendet_am = datetime.now()
            auftrag.status = "gesendet"
            return (True, f"beA-Nachricht an {auftrag.empfaenger} gesendet (Simulation)")
        
        elif auftrag.versand_typ == VersandTyp.FAX:
            auftrag.status = "wartend"
            return (True, "Fax-Auftrag erstellt (Simulation)")
        
        elif auftrag.versand_typ == VersandTyp.POST:
            auftrag.status = "vorbereitet"
            return (True, "Dokument für postalischen Versand vorbereitet")
        
        return (False, "Unbekannter Versandtyp")
    
    def get_auftraege(self, status: str = None) -> List[VersandAuftrag]:
        """Gibt Versandaufträge zurück, optional gefiltert nach Status."""
        if status:
            return [a for a in self.auftraege if a.status == status]
        return self.auftraege
    
    def export_als_html(self, inhalt: str, dateiname: str = "dokument.html") -> str:
        """Exportiert Inhalt als HTML-Datei."""
        # In echter Anwendung würde hier die Datei gespeichert
        return inhalt
    
    def generiere_brief(
        self,
        absender: str,
        empfaenger: str,
        betreff: str,
        inhalt: str,
        anrede: str = "Sehr geehrte Damen und Herren,",
        ort: str = "",
        unterschrift: str = ""
    ) -> str:
        """Generiert einen formatierten Brief."""
        return self.erstelle_pdf("brief_standard", {
            "absender": absender,
            "empfaenger": empfaenger,
            "ort": ort or "Frankfurt am Main",
            "datum": datetime.now().strftime("%d.%m.%Y"),
            "betreff": betreff,
            "anrede": anrede,
            "inhalt": inhalt,
            "unterschrift": unterschrift or absender.split("\n")[0]
        })
