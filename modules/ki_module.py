"""
JuraConnect - KI-Module
========================
- KI-Vertragsanalyse (Arbeitsverträge auf Klauseln prüfen)
- KI-Kündigungscheck (Wirksamkeitsprüfung)
- KI-Wissensdatenbank mit RAG (Retrieval Augmented Generation)

Version: 2.0.0
"""

from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import re
import math


# =============================================================================
# KI-VERTRAGSANALYSE
# =============================================================================

class KlauselBewertung(Enum):
    UNBEDENKLICH = "unbedenklich"
    PRUEFENSWERT = "prüfenswert"
    PROBLEMATISCH = "problematisch"
    UNWIRKSAM = "unwirksam"


@dataclass
class AnalysierteKlausel:
    """Eine analysierte Vertragsklausel"""
    titel: str = ""
    original_text: str = ""
    kategorie: str = ""
    bewertung: KlauselBewertung = KlauselBewertung.UNBEDENKLICH
    erklaerung: str = ""
    rechtliche_grundlage: str = ""
    empfehlung: str = ""
    risiko_score: int = 0  # 0-100


@dataclass
class VertragsanalyseErgebnis:
    """Ergebnis einer Vertragsanalyse"""
    vertragstyp: str = ""
    gesamtbewertung: str = ""
    risiko_score: int = 0
    klauseln: List[AnalysierteKlausel] = field(default_factory=list)
    zusammenfassung: str = ""
    handlungsempfehlungen: List[str] = field(default_factory=list)


class KIVertragsanalyse:
    """
    Analysiert Arbeitsverträge auf problematische Klauseln.
    
    Prüft auf:
    - Unwirksame AGB-Klauseln
    - Versteckte Nachteile
    - Fehlende Regelungen
    - Abweichungen vom Gesetz
    """
    
    # Problematische Klauselmuster
    KLAUSEL_MUSTER = {
        "ausschlussfristen": {
            "muster": [
                r"Ansprüche.*verfallen.*(\d+)\s*Monat",
                r"Ausschlussfrist.*(\d+)\s*Monat",
                r"Geltendmachung.*innerhalb.*(\d+)\s*Monat",
                r"Verfall.*(\d+)\s*Monat",
            ],
            "kategorie": "Ausschlussfristen",
        },
        "ueberstunden_abgegolten": {
            "muster": [
                r"Überstunden.*(?:abgegolten|pauschal|mit dem Gehalt)",
                r"Mehrarbeit.*(?:abgegolten|vergütet|enthalten)",
                r"(?:pauschal|pauschaliert).*Überstunden",
            ],
            "kategorie": "Überstundenregelung",
        },
        "kuendigungsfrist_kurz": {
            "muster": [
                r"Kündigungsfrist.*(\d+)\s*(?:Woche|Tag)",
                r"Kündigung.*(?:jederzeit|fristlos|sofort)",
            ],
            "kategorie": "Kündigungsfrist",
        },
        "vertragsstrafe": {
            "muster": [
                r"Vertragsstrafe",
                r"(?:Strafe|Strafzahlung).*(?:Brutto|Gehalt|Monat)",
                r"Konventionalstrafe",
            ],
            "kategorie": "Vertragsstrafe",
        },
        "wettbewerbsverbot": {
            "muster": [
                r"Wettbewerbsverbot",
                r"Konkurrenztätigkeit.*untersagt",
                r"nachvertragliches.*Wettbewerbsverbot",
            ],
            "kategorie": "Wettbewerbsverbot",
        },
        "rueckzahlung_fortbildung": {
            "muster": [
                r"Rückzahlung.*Fortbildung",
                r"Fortbildungskosten.*(?:zurück|erstatten)",
                r"Bindungsdauer.*(?:Jahr|Monat)",
            ],
            "kategorie": "Fortbildungsrückzahlung",
        },
        "versetzungsklausel": {
            "muster": [
                r"(?:jederzeit|bundesweit).*(?:versetz|Versetzung)",
                r"Versetzung.*(?:anderer Ort|Filiale|Standort)",
            ],
            "kategorie": "Versetzungsklausel",
        },
        "freiwilligkeitsvorbehalt": {
            "muster": [
                r"freiwillig.*(?:Leistung|Zahlung|Bonus)",
                r"ohne.*Rechtsanspruch",
                r"Widerrufsvorbehalt",
            ],
            "kategorie": "Freiwilligkeitsvorbehalt",
        },
        "geheimhaltung": {
            "muster": [
                r"Geheimhaltung",
                r"Verschwiegenheit",
                r"vertraulich.*(?:Information|Daten)",
            ],
            "kategorie": "Geheimhaltung",
        },
        "nebentaetigkeit": {
            "muster": [
                r"Nebentätigkeit.*(?:verboten|untersagt|genehmigung)",
                r"(?:keine|nicht).*Nebentätigkeit",
            ],
            "kategorie": "Nebentätigkeit",
        }
    }
    
    # Bewertungsfunktionen pro Klauseltyp
    def _bewerte_ausschlussfristen(self, match, text: str) -> Dict:
        try:
            monate = int(match.group(1))
        except:
            monate = 0
        
        if monate < 3:
            return {
                "bewertung": KlauselBewertung.UNWIRKSAM,
                "erklaerung": f"Ausschlussfrist von {monate} Monaten ist zu kurz und daher unwirksam.",
                "rechtliche_grundlage": "§ 202 BGB, § 307 BGB - Mindestens 3 Monate erforderlich",
                "empfehlung": "Klausel ist unwirksam. Ansprüche bestehen trotzdem!",
                "risiko": 80
            }
        else:
            return {
                "bewertung": KlauselBewertung.PRUEFENSWERT,
                "erklaerung": f"Ausschlussfrist von {monate} Monaten. Frist unbedingt beachten!",
                "rechtliche_grundlage": "§ 202 BGB",
                "empfehlung": "Ansprüche rechtzeitig geltend machen.",
                "risiko": 40
            }
    
    def _bewerte_ueberstunden(self, match, text: str) -> Dict:
        return {
            "bewertung": KlauselBewertung.PROBLEMATISCH,
            "erklaerung": "Pauschale Überstundenabgeltung kann unwirksam sein, wenn Umfang nicht klar begrenzt.",
            "rechtliche_grundlage": "§ 307 BGB, BAG 5 AZR 517/09 - Max. 10-15% der Arbeitszeit",
            "empfehlung": "Prüfen ob konkrete Stundenanzahl genannt ist. Ohne Begrenzung unwirksam!",
            "risiko": 65
        }
    
    def _bewerte_kuendigungsfrist(self, match, text: str) -> Dict:
        return {
            "bewertung": KlauselBewertung.PRUEFENSWERT,
            "erklaerung": "Die Kündigungsfrist sollte den gesetzlichen Mindestanforderungen entsprechen.",
            "rechtliche_grundlage": "§ 622 BGB - Mindestens 4 Wochen",
            "empfehlung": "Prüfen ob gesetzliche Mindestfrist eingehalten wird.",
            "risiko": 45
        }
    
    def _bewerte_vertragsstrafe(self, match, text: str) -> Dict:
        return {
            "bewertung": KlauselBewertung.PROBLEMATISCH,
            "erklaerung": "Vertragsstrafen sind nur eingeschränkt zulässig (max. 1 Bruttomonatsgehalt).",
            "rechtliche_grundlage": "§ 307 BGB, BAG-Rechtsprechung",
            "empfehlung": "Höhe der Strafe prüfen, bei Überschreitung Streichung verhandeln.",
            "risiko": 60
        }
    
    def _bewerte_wettbewerbsverbot(self, match, text: str) -> Dict:
        return {
            "bewertung": KlauselBewertung.PRUEFENSWERT,
            "erklaerung": "Nachvertragliche Wettbewerbsverbote erfordern Karenzentschädigung (mind. 50%).",
            "rechtliche_grundlage": "§§ 74 ff. HGB - Max. 2 Jahre, mind. 50% Entschädigung",
            "empfehlung": "Dauer und Entschädigung prüfen. Ohne Entschädigung unverbindlich!",
            "risiko": 55
        }
    
    def _bewerte_rueckzahlung(self, match, text: str) -> Dict:
        return {
            "bewertung": KlauselBewertung.PRUEFENSWERT,
            "erklaerung": "Rückzahlungsklauseln müssen verhältnismäßig sein.",
            "rechtliche_grundlage": "§ 307 BGB - Faustregel: 1 Jahr Bindung pro 1 Monat Fortbildung",
            "empfehlung": "Bindungsdauer und Staffelung prüfen.",
            "risiko": 45
        }
    
    def _bewerte_versetzung(self, match, text: str) -> Dict:
        return {
            "bewertung": KlauselBewertung.PRUEFENSWERT,
            "erklaerung": "Weite Versetzungsklauseln können das Direktionsrecht unangemessen erweitern.",
            "rechtliche_grundlage": "§ 106 GewO, § 307 BGB",
            "empfehlung": "Auf geografische und sachliche Grenzen achten.",
            "risiko": 40
        }
    
    def _bewerte_freiwilligkeit(self, match, text: str) -> Dict:
        return {
            "bewertung": KlauselBewertung.PRUEFENSWERT,
            "erklaerung": "Freiwilligkeitsvorbehalte können bei regelmäßiger Zahlung unwirksam werden.",
            "rechtliche_grundlage": "§ 307 BGB - Betriebliche Übung nach 3x Zahlung",
            "empfehlung": "Bei regelmäßigen Zahlungen kann Anspruch entstehen.",
            "risiko": 35
        }
    
    def _bewerte_geheimhaltung(self, match, text: str) -> Dict:
        return {
            "bewertung": KlauselBewertung.UNBEDENKLICH,
            "erklaerung": "Geheimhaltungsklauseln sind grundsätzlich zulässig und üblich.",
            "rechtliche_grundlage": "§ 17 UWG, Geschäftsgeheimnisgesetz",
            "empfehlung": "Achten Sie darauf, dass die Klausel nicht zu weit gefasst ist.",
            "risiko": 15
        }
    
    def _bewerte_nebentaetigkeit(self, match, text: str) -> Dict:
        return {
            "bewertung": KlauselBewertung.PRUEFENSWERT,
            "erklaerung": "Ein generelles Nebentätigkeitsverbot ist unwirksam.",
            "rechtliche_grundlage": "Art. 12 GG, § 307 BGB",
            "empfehlung": "Erlaubnisvorbehalt ist zulässig, Totalverbot nicht.",
            "risiko": 40
        }
    
    # Fehlende wichtige Regelungen
    FEHLENDE_REGELUNGEN = [
        {
            "suche": r"(?:Urlaub|Urlaubstage|Jahresurlaub)",
            "titel": "Urlaubsregelung",
            "erklaerung": "Der Vertrag sollte Urlaubstage regeln (mind. 20 bei 5-Tage-Woche).",
            "risiko": 30
        },
        {
            "suche": r"(?:Arbeitszeit|Wochenarbeitszeit|Stunden.*Woche)",
            "titel": "Arbeitszeitregelung",
            "erklaerung": "Die wöchentliche Arbeitszeit sollte definiert sein.",
            "risiko": 40
        },
        {
            "suche": r"(?:Gehalt|Vergütung|Lohn|Entgelt).*(?:€|EUR|Euro|\d+)",
            "titel": "Vergütungsregelung",
            "erklaerung": "Die Vergütung muss klar geregelt sein.",
            "risiko": 50
        },
    ]
    
    def analysiere_vertrag(self, vertragstext: str) -> VertragsanalyseErgebnis:
        """Analysiert einen Arbeitsvertrag vollständig."""
        ergebnis = VertragsanalyseErgebnis()
        ergebnis.vertragstyp = self._erkenne_vertragstyp(vertragstext)
        
        # Bewertungsfunktionen zuordnen
        bewertungen = {
            "ausschlussfristen": self._bewerte_ausschlussfristen,
            "ueberstunden_abgegolten": self._bewerte_ueberstunden,
            "kuendigungsfrist_kurz": self._bewerte_kuendigungsfrist,
            "vertragsstrafe": self._bewerte_vertragsstrafe,
            "wettbewerbsverbot": self._bewerte_wettbewerbsverbot,
            "rueckzahlung_fortbildung": self._bewerte_rueckzahlung,
            "versetzungsklausel": self._bewerte_versetzung,
            "freiwilligkeitsvorbehalt": self._bewerte_freiwilligkeit,
            "geheimhaltung": self._bewerte_geheimhaltung,
            "nebentaetigkeit": self._bewerte_nebentaetigkeit,
        }
        
        # 1. Klauseln analysieren
        for klausel_id, klausel_def in self.KLAUSEL_MUSTER.items():
            for muster in klausel_def["muster"]:
                match = re.search(muster, vertragstext, re.IGNORECASE)
                if match:
                    if klausel_id in bewertungen:
                        pruefung = bewertungen[klausel_id](match, vertragstext)
                    else:
                        pruefung = {
                            "bewertung": KlauselBewertung.PRUEFENSWERT,
                            "erklaerung": "Klausel gefunden.",
                            "rechtliche_grundlage": "",
                            "empfehlung": "Rechtliche Prüfung empfohlen.",
                            "risiko": 30
                        }
                    
                    # Textausschnitt extrahieren
                    start = max(0, match.start() - 30)
                    end = min(len(vertragstext), match.end() + 80)
                    original = "..." + vertragstext[start:end].strip() + "..."
                    
                    klausel = AnalysierteKlausel(
                        titel=klausel_def["kategorie"],
                        original_text=original,
                        kategorie=klausel_def["kategorie"],
                        bewertung=pruefung["bewertung"],
                        erklaerung=pruefung["erklaerung"],
                        rechtliche_grundlage=pruefung["rechtliche_grundlage"],
                        empfehlung=pruefung["empfehlung"],
                        risiko_score=pruefung["risiko"]
                    )
                    ergebnis.klauseln.append(klausel)
                    break
        
        # 2. Fehlende Regelungen prüfen
        for regelung in self.FEHLENDE_REGELUNGEN:
            if not re.search(regelung["suche"], vertragstext, re.IGNORECASE):
                klausel = AnalysierteKlausel(
                    titel=f"⚠️ Fehlt: {regelung['titel']}",
                    original_text="(Nicht im Vertrag gefunden)",
                    kategorie="Fehlende Regelung",
                    bewertung=KlauselBewertung.PRUEFENSWERT,
                    erklaerung=regelung["erklaerung"],
                    empfehlung=f"Ergänzung empfohlen.",
                    risiko_score=regelung["risiko"]
                )
                ergebnis.klauseln.append(klausel)
        
        # 3. Gesamtbewertung
        self._berechne_gesamtbewertung(ergebnis)
        
        return ergebnis
    
    def _erkenne_vertragstyp(self, text: str) -> str:
        """Erkennt den Vertragstyp."""
        text_lower = text.lower()
        if "befristet" in text_lower:
            return "Befristeter Arbeitsvertrag"
        elif "teilzeit" in text_lower:
            return "Teilzeit-Arbeitsvertrag"
        elif "minijob" in text_lower or "geringfügig" in text_lower:
            return "Minijob-Vertrag"
        elif "geschäftsführer" in text_lower:
            return "Geschäftsführer-Dienstvertrag"
        else:
            return "Unbefristeter Arbeitsvertrag"
    
    def _berechne_gesamtbewertung(self, ergebnis: VertragsanalyseErgebnis):
        """Berechnet die Gesamtbewertung."""
        if not ergebnis.klauseln:
            ergebnis.gesamtbewertung = "nicht_analysierbar"
            ergebnis.risiko_score = 0
            return
        
        avg_risiko = sum(k.risiko_score for k in ergebnis.klauseln) / len(ergebnis.klauseln)
        max_risiko = max(k.risiko_score for k in ergebnis.klauseln)
        ergebnis.risiko_score = int((avg_risiko + max_risiko) / 2)
        
        unwirksame = len([k for k in ergebnis.klauseln if k.bewertung == KlauselBewertung.UNWIRKSAM])
        problematische = len([k for k in ergebnis.klauseln if k.bewertung == KlauselBewertung.PROBLEMATISCH])
        
        if unwirksame > 0:
            ergebnis.gesamtbewertung = "kritisch"
        elif problematische > 0:
            ergebnis.gesamtbewertung = "bedenklich"
        elif ergebnis.risiko_score > 40:
            ergebnis.gesamtbewertung = "prüfenswert"
        else:
            ergebnis.gesamtbewertung = "akzeptabel"
        
        # Zusammenfassung
        ergebnis.zusammenfassung = f"""
**Vertragstyp:** {ergebnis.vertragstyp}
**Gesamtbewertung:** {ergebnis.gesamtbewertung.upper()}
**Risiko-Score:** {ergebnis.risiko_score}/100

Gefunden: {unwirksame} unwirksame, {problematische} problematische Klauseln
        """.strip()
        
        # Empfehlungen
        if unwirksame > 0:
            ergebnis.handlungsempfehlungen.append(
                f"🔴 {unwirksame} Klausel(n) sind vermutlich unwirksam - vor Unterschrift ansprechen!"
            )
        if problematische > 0:
            ergebnis.handlungsempfehlungen.append(
                f"🟠 {problematische} Klausel(n) sind problematisch - Nachverhandlung empfohlen."
            )
        if ergebnis.gesamtbewertung in ["kritisch", "bedenklich"]:
            ergebnis.handlungsempfehlungen.append(
                "⚠️ Rechtliche Beratung vor Vertragsunterzeichnung empfohlen!"
            )


# =============================================================================
# KI-KÜNDIGUNGSCHECK
# =============================================================================

@dataclass
class KuendigungsCheckErgebnis:
    """Ergebnis des KI-Kündigungschecks"""
    wirksamkeit_score: int = 100  # 0-100 (100 = wirksam aus AG-Sicht)
    wirksamkeit_prognose: str = ""
    formelle_fehler: List[Dict] = field(default_factory=list)
    materielle_fehler: List[Dict] = field(default_factory=list)
    verfahrensfehler: List[Dict] = field(default_factory=list)
    sonderschutz: List[Dict] = field(default_factory=list)
    empfehlungen: List[str] = field(default_factory=list)
    klagefrist: date = None
    zusammenfassung: str = ""


class KIKuendigungsCheck:
    """
    KI-gestützte Prüfung der Kündigungswirksamkeit.
    
    Prüft:
    - Formelle Wirksamkeit (Schriftform, etc.)
    - Materielle Wirksamkeit (Kündigungsgrund)
    - Verfahrensfehler (BR-Anhörung, etc.)
    - Sonderkündigungsschutz
    """
    
    def pruefe_kuendigung(
        self,
        # Basisdaten
        zugang_datum: date,
        betriebsgroesse: int,
        betriebszugehoerigkeit_monate: int,
        kuendigungsart: str = "ordentlich",
        kuendigungsgrund: str = "",
        # Formelles
        schriftform: bool = True,
        unterschrift_vorhanden: bool = True,
        kuendigungserklaerung_eindeutig: bool = True,
        # Verfahren
        hat_betriebsrat: bool = False,
        betriebsrat_angehoert: bool = True,
        # Sonderschutz
        ist_schwerbehindert: bool = False,
        integrationsamt_zugestimmt: bool = False,
        ist_schwanger: bool = False,
        arbeitgeber_wusste_schwangerschaft: bool = False,
        ist_in_elternzeit: bool = False,
        ist_betriebsratsmitglied: bool = False,
        ist_datenschutzbeauftragter: bool = False,
        # Bei verhaltensbedingt
        abmahnung_vorhanden: bool = False,
        abmahnung_einschlaegig: bool = False,
        # Bei betriebsbedingt
        sozialauswahl_durchgefuehrt: bool = False,
    ) -> KuendigungsCheckErgebnis:
        """Führt eine umfassende Kündigungsprüfung durch."""
        
        ergebnis = KuendigungsCheckErgebnis()
        ergebnis.klagefrist = zugang_datum + timedelta(days=21)
        
        abzug = 0  # Wird von 100 abgezogen
        
        # ============ 1. FORMELLE PRÜFUNG ============
        if not schriftform:
            ergebnis.formelle_fehler.append({
                "fehler": "Schriftform nicht eingehalten",
                "erklaerung": "Kündigung muss schriftlich erfolgen (§ 623 BGB). E-Mail, Fax, WhatsApp sind UNWIRKSAM!",
                "schwere": "kritisch"
            })
            abzug += 100  # Sofort unwirksam
        
        if not unterschrift_vorhanden:
            ergebnis.formelle_fehler.append({
                "fehler": "Keine Unterschrift",
                "erklaerung": "Eigenhändige Unterschrift erforderlich (§ 126 BGB).",
                "schwere": "kritisch"
            })
            abzug += 80
        
        if not kuendigungserklaerung_eindeutig:
            ergebnis.formelle_fehler.append({
                "fehler": "Kündigungserklärung unklar",
                "erklaerung": "Die Kündigung muss eindeutig als solche erkennbar sein.",
                "schwere": "mittel"
            })
            abzug += 20
        
        # ============ 2. VERFAHRENSFEHLER ============
        if hat_betriebsrat and not betriebsrat_angehoert:
            ergebnis.verfahrensfehler.append({
                "fehler": "Betriebsrat nicht angehört",
                "erklaerung": "Anhörung nach § 102 BetrVG ist zwingend. Ohne Anhörung ist Kündigung UNWIRKSAM!",
                "schwere": "kritisch"
            })
            abzug += 60
        
        # ============ 3. SONDERKÜNDIGUNGSSCHUTZ ============
        if ist_schwanger:
            if arbeitgeber_wusste_schwangerschaft:
                ergebnis.sonderschutz.append({
                    "schutz": "Mutterschutz",
                    "erklaerung": "Kündigung während Schwangerschaft ist VERBOTEN (§ 17 MuSchG)!",
                    "schwere": "kritisch"
                })
                abzug += 90
            else:
                ergebnis.sonderschutz.append({
                    "schutz": "Mutterschutz",
                    "erklaerung": "Schwangerschaft innerhalb 2 Wochen nach Kündigung mitteilen!",
                    "schwere": "hinweis"
                })
        
        if ist_schwerbehindert:
            if not integrationsamt_zugestimmt:
                ergebnis.sonderschutz.append({
                    "schutz": "Schwerbehinderung",
                    "erklaerung": "Kündigung ohne Zustimmung des Integrationsamts ist UNWIRKSAM (§ 168 SGB IX)!",
                    "schwere": "kritisch"
                })
                abzug += 70
        
        if ist_in_elternzeit:
            ergebnis.sonderschutz.append({
                "schutz": "Elternzeit",
                "erklaerung": "Kündigung während Elternzeit nur mit Behördenzustimmung (§ 18 BEEG).",
                "schwere": "kritisch"
            })
            abzug += 70
        
        if ist_betriebsratsmitglied and kuendigungsart == "ordentlich":
            ergebnis.sonderschutz.append({
                "schutz": "Betriebsratsmitglied",
                "erklaerung": "Ordentliche Kündigung ist ausgeschlossen (§ 15 KSchG)!",
                "schwere": "kritisch"
            })
            abzug += 80
        
        if ist_datenschutzbeauftragter:
            ergebnis.sonderschutz.append({
                "schutz": "Datenschutzbeauftragter",
                "erklaerung": "Besonderer Kündigungsschutz während und 1 Jahr nach Tätigkeit (§ 38 BDSG).",
                "schwere": "mittel"
            })
            abzug += 30
        
        # ============ 4. MATERIELLE PRÜFUNG ============
        kschg_anwendbar = betriebsgroesse > 10 and betriebszugehoerigkeit_monate >= 6
        
        if kschg_anwendbar:
            if not kuendigungsgrund:
                ergebnis.materielle_fehler.append({
                    "fehler": "Kein Kündigungsgrund erkennbar",
                    "erklaerung": "Bei KSchG-Anwendbarkeit ist ein Grund erforderlich (§ 1 KSchG).",
                    "schwere": "kritisch"
                })
                abzug += 40
            
            elif "verhaltensbedingt" in kuendigungsgrund.lower():
                if not abmahnung_vorhanden:
                    ergebnis.materielle_fehler.append({
                        "fehler": "Keine Abmahnung vor verhaltensbedingter Kündigung",
                        "erklaerung": "In der Regel ist vorherige Abmahnung erforderlich.",
                        "schwere": "mittel"
                    })
                    abzug += 35
                elif not abmahnung_einschlaegig:
                    ergebnis.materielle_fehler.append({
                        "fehler": "Abmahnung nicht einschlägig",
                        "erklaerung": "Abmahnung muss gleichartiges Fehlverhalten betreffen.",
                        "schwere": "mittel"
                    })
                    abzug += 25
            
            elif "betriebsbedingt" in kuendigungsgrund.lower():
                if not sozialauswahl_durchgefuehrt:
                    ergebnis.materielle_fehler.append({
                        "fehler": "Sozialauswahl nicht erkennbar",
                        "erklaerung": "Bei betriebsbedingter Kündigung muss Sozialauswahl erfolgen (§ 1 Abs. 3 KSchG).",
                        "schwere": "mittel"
                    })
                    abzug += 30
        
        # ============ 5. ERGEBNIS BERECHNEN ============
        ergebnis.wirksamkeit_score = max(0, min(100, 100 - abzug))
        
        if ergebnis.wirksamkeit_score >= 70:
            ergebnis.wirksamkeit_prognose = "wahrscheinlich_wirksam"
            prognose_text = "Kündigung erscheint wirksam"
        elif ergebnis.wirksamkeit_score >= 40:
            ergebnis.wirksamkeit_prognose = "unsicher"
            prognose_text = "Wirksamkeit rechtlich unsicher"
        else:
            ergebnis.wirksamkeit_prognose = "wahrscheinlich_unwirksam"
            prognose_text = "Kündigung wahrscheinlich unwirksam"
        
        # ============ 6. EMPFEHLUNGEN ============
        if ergebnis.wirksamkeit_score < 50:
            ergebnis.empfehlungen.append(
                "🟢 Gute Chancen! Die Kündigung weist erhebliche Mängel auf. "
                "Eine Kündigungsschutzklage ist aussichtsreich."
            )
        elif ergebnis.wirksamkeit_score < 70:
            ergebnis.empfehlungen.append(
                "🟡 Verhandlungsbasis vorhanden. Die Kündigung hat Schwachstellen. "
                "Eine Abfindungsverhandlung könnte erfolgreich sein."
            )
        else:
            ergebnis.empfehlungen.append(
                "🔴 Schwierige Ausgangslage. Die Kündigung erscheint formal korrekt. "
                "Dennoch sollte anwaltlich geprüft werden."
            )
        
        ergebnis.empfehlungen.append(
            f"⏰ WICHTIG: Klagefrist endet am {ergebnis.klagefrist.strftime('%d.%m.%Y')}! "
            f"Nur noch {(ergebnis.klagefrist - date.today()).days} Tage!"
        )
        
        # ============ 7. ZUSAMMENFASSUNG ============
        ergebnis.zusammenfassung = f"""
## Kündigungscheck Ergebnis

**Prognose:** {prognose_text}
**Score:** {ergebnis.wirksamkeit_score}/100 (0 = unwirksam, 100 = wirksam)
**KSchG anwendbar:** {"Ja" if kschg_anwendbar else "Nein"}

**Gefundene Probleme:**
- Formelle Fehler: {len(ergebnis.formelle_fehler)}
- Materielle Fehler: {len(ergebnis.materielle_fehler)}
- Verfahrensfehler: {len(ergebnis.verfahrensfehler)}
- Sonderkündigungsschutz: {len(ergebnis.sonderschutz)}

**Klagefrist:** {ergebnis.klagefrist.strftime('%d.%m.%Y')}
        """.strip()
        
        return ergebnis


# =============================================================================
# KI-WISSENSDATENBANK (RAG)
# =============================================================================

@dataclass
class WissensEintrag:
    """Ein Eintrag in der Wissensdatenbank"""
    id: str = ""
    titel: str = ""
    kategorie: str = ""
    inhalt: str = ""
    schlagworte: List[str] = field(default_factory=list)
    rechtsgrundlage: str = ""
    stand: str = "2024"
    relevanz: float = 0.0


class KIWissensdatenbank:
    """
    Semantische Wissensdatenbank für Arbeitsrecht (RAG-System).
    """
    
    def __init__(self):
        self.eintraege: List[WissensEintrag] = []
        self._initialisiere()
    
    def _initialisiere(self):
        """Initialisiert die Wissensbasis."""
        self.eintraege = [
            WissensEintrag(
                id="kschg",
                titel="Kündigungsschutzgesetz (KSchG) - Anwendbarkeit",
                kategorie="Kündigungsschutz",
                inhalt="""
Das KSchG gilt bei:
• Betrieb mit mehr als 10 Arbeitnehmern (§ 23 KSchG)
• Arbeitsverhältnis besteht länger als 6 Monate (Wartezeit)

Teilzeitkräfte zählen anteilig:
• Bis 20 Std./Woche: 0,5
• Bis 30 Std./Woche: 0,75
• Über 30 Std./Woche: 1,0

Auszubildende zählen NICHT mit!

Bei Anwendbarkeit braucht der AG einen Kündigungsgrund:
• Betriebsbedingt
• Verhaltensbedingt
• Personenbedingt
                """,
                schlagworte=["KSchG", "Kündigungsschutz", "10 Mitarbeiter", "Wartezeit", "Betriebsgröße"],
                rechtsgrundlage="§§ 1, 23 KSchG"
            ),
            WissensEintrag(
                id="klagefrist",
                titel="Klagefrist für Kündigungsschutzklage",
                kategorie="Fristen",
                inhalt="""
Die Kündigungsschutzklage muss innerhalb von 3 WOCHEN (21 Tage) 
nach Zugang der Kündigung beim Arbeitsgericht erhoben werden!

Dies ist eine AUSSCHLUSSFRIST - wird sie versäumt, gilt die 
Kündigung als wirksam, auch wenn sie eigentlich unwirksam wäre!

Nachträgliche Zulassung (§ 5 KSchG) nur bei:
• Unverschuldeter Verhinderung
• Krankheit
• Auslandsaufenthalt ohne Kenntnisnahme
                """,
                schlagworte=["Klagefrist", "3 Wochen", "21 Tage", "Ausschlussfrist", "§ 4 KSchG"],
                rechtsgrundlage="§§ 4, 5 KSchG"
            ),
            WissensEintrag(
                id="kuendigungsfrist",
                titel="Gesetzliche Kündigungsfristen",
                kategorie="Kündigungsfristen",
                inhalt="""
§ 622 BGB - Kündigungsfristen für Arbeitgeber:

Grundfrist: 4 Wochen zum 15. oder Monatsende

Nach Betriebszugehörigkeit:
• 2 Jahre: 1 Monat zum Monatsende
• 5 Jahre: 2 Monate zum Monatsende
• 8 Jahre: 3 Monate zum Monatsende
• 10 Jahre: 4 Monate zum Monatsende
• 12 Jahre: 5 Monate zum Monatsende
• 15 Jahre: 6 Monate zum Monatsende
• 20 Jahre: 7 Monate zum Monatsende

Probezeit (max. 6 Monate): 2 Wochen jederzeit
                """,
                schlagworte=["Kündigungsfrist", "622 BGB", "4 Wochen", "Probezeit", "Monatsende"],
                rechtsgrundlage="§ 622 BGB"
            ),
            WissensEintrag(
                id="abfindung",
                titel="Abfindung bei Kündigung",
                kategorie="Abfindung",
                inhalt="""
Es gibt KEINEN gesetzlichen Anspruch auf Abfindung!

Mögliche Abfindungsquellen:
1. § 1a KSchG: AG bietet 0,5 Gehälter/Jahr bei Klageverzicht
2. Vergleich im Kündigungsschutzprozess
3. Sozialplan bei Betriebsänderung
4. Aufhebungsvertrag

Faustformeln:
• Regelabfindung: 0,5 Bruttogehälter × Beschäftigungsjahre
• Bei gutem Schutz: bis 1,0 Bruttogehälter × Jahre
• Bei sehr gutem Schutz: bis 1,5 Bruttogehälter × Jahre

Faktoren für höhere Abfindung:
• Längere Betriebszugehörigkeit
• Höheres Alter (>50)
• Sonderkündigungsschutz
• Fehlerhafte Kündigung
                """,
                schlagworte=["Abfindung", "1a KSchG", "0,5", "Vergleich", "Aufhebungsvertrag"],
                rechtsgrundlage="§ 1a KSchG"
            ),
            WissensEintrag(
                id="betriebsrat",
                titel="Betriebsratsanhörung vor Kündigung",
                kategorie="Betriebsrat",
                inhalt="""
§ 102 BetrVG: Der Betriebsrat muss vor JEDER Kündigung angehört werden!

Inhalt der Anhörung:
• Person des AN (Name, Alter, Familie)
• Art der Kündigung
• Kündigungsgründe (vollständig!)
• Kündigungstermin

Fristen für BR-Stellungnahme:
• Ordentliche Kündigung: 1 Woche
• Außerordentliche Kündigung: 3 Tage

RECHTSFOLGE bei fehlender/fehlerhafter Anhörung:
Kündigung ist UNWIRKSAM!

BR-Widerspruch führt zu Weiterbeschäftigungsanspruch!
                """,
                schlagworte=["Betriebsrat", "102 BetrVG", "Anhörung", "Widerspruch", "1 Woche"],
                rechtsgrundlage="§ 102 BetrVG"
            ),
            WissensEintrag(
                id="mutterschutz",
                titel="Kündigungsschutz bei Schwangerschaft",
                kategorie="Sonderkündigungsschutz",
                inhalt="""
§ 17 MuSchG: Absolutes Kündigungsverbot!

Schutzbereich:
• Während der gesamten Schwangerschaft
• Bis 4 Monate nach Entbindung
• Bei Fehlgeburt nach 12. SSW: 4 Monate

Voraussetzung:
AG muss Schwangerschaft kennen ODER
Mitteilung innerhalb 2 Wochen nach Kündigungszugang

Ausnahme: Nur mit Behördenzustimmung (selten!)

Rechtsfolge bei Verstoß:
Kündigung ist NICHTIG (§ 134 BGB)!
                """,
                schlagworte=["Mutterschutz", "Schwangerschaft", "17 MuSchG", "Kündigungsverbot"],
                rechtsgrundlage="§ 17 MuSchG"
            ),
            WissensEintrag(
                id="schwerbehinderung",
                titel="Kündigungsschutz bei Schwerbehinderung",
                kategorie="Sonderkündigungsschutz",
                inhalt="""
§ 168 SGB IX: Besonderer Kündigungsschutz

Geschützt sind:
• Schwerbehinderte (GdB ≥ 50)
• Gleichgestellte (GdB 30-50 mit Gleichstellungsbescheid)

Verfahren:
1. AG beantragt Zustimmung beim Integrationsamt
2. Integrationsamt prüft (ca. 4 Wochen)
3. Erst nach Zustimmung darf gekündigt werden

OHNE Zustimmung: Kündigung ist UNWIRKSAM!

Das Integrationsamt prüft:
• Zusammenhang mit Behinderung
• Zumutbarkeit der Weiterbeschäftigung
                """,
                schlagworte=["Schwerbehinderung", "GdB 50", "Integrationsamt", "168 SGB IX"],
                rechtsgrundlage="§ 168 SGB IX"
            ),
            WissensEintrag(
                id="pkh",
                titel="Prozesskostenhilfe (PKH)",
                kategorie="Prozesskosten",
                inhalt="""
PKH ermöglicht einkommensschwachen Personen den Gerichtszugang.

Voraussetzungen (§ 114 ZPO):
1. Wirtschaftliche Bedürftigkeit
2. Hinreichende Erfolgsaussichten
3. Keine Mutwilligkeit

Freibeträge 2024:
• Antragsteller: 619 €
• Ehepartner: 619 €
• Kinder: 393-619 € (altersabhängig)
• Erwerbstätigenfreibetrag: 255 €

Umfang:
• Gerichtskosten
• Eigene Anwaltskosten
• NICHT: Gegnerische Kosten bei Verlieren!

Ratenzahlung bei Einkommen über Freibetrag (max. 48 Raten)
                """,
                schlagworte=["PKH", "Prozesskostenhilfe", "arm", "Freibetrag", "114 ZPO"],
                rechtsgrundlage="§§ 114 ff. ZPO"
            ),
            WissensEintrag(
                id="zeugnis",
                titel="Arbeitszeugnis - Anspruch und Inhalt",
                kategorie="Arbeitszeugnis",
                inhalt="""
§ 109 GewO: Jeder AN hat Anspruch auf ein Zeugnis!

Arten:
• Einfaches Zeugnis: Art und Dauer
• Qualifiziertes Zeugnis: + Leistung und Verhalten

AN kann wählen welche Art!

Grundsätze:
• Wahrheitspflicht
• Wohlwollende Formulierung
• Keine Geheimcodes (versteckte negative Aussagen)

Notenskala (Leistung):
• "stets zur vollsten Zufriedenheit" = sehr gut (1)
• "stets zur vollen Zufriedenheit" = gut (2)
• "zur vollen Zufriedenheit" = befriedigend (3)
• "zur Zufriedenheit" = ausreichend (4)
• "im Großen und Ganzen zur Zufriedenheit" = mangelhaft (5)
                """,
                schlagworte=["Zeugnis", "Arbeitszeugnis", "109 GewO", "Geheimcode", "Note"],
                rechtsgrundlage="§ 109 GewO"
            ),
        ]
    
    def suche(self, anfrage: str, max_ergebnisse: int = 5) -> List[WissensEintrag]:
        """Semantische Suche in der Wissensdatenbank."""
        anfrage_lower = anfrage.lower()
        anfrage_woerter = set(anfrage_lower.split())
        
        for eintrag in self.eintraege:
            score = 0
            
            # Titel-Match (hoch gewichtet)
            for wort in anfrage_woerter:
                if len(wort) > 2 and wort in eintrag.titel.lower():
                    score += 20
            
            # Schlagwort-Match (sehr hoch gewichtet)
            for schlagwort in eintrag.schlagworte:
                sw_lower = schlagwort.lower()
                if sw_lower in anfrage_lower:
                    score += 30
                for wort in anfrage_woerter:
                    if wort in sw_lower or sw_lower in wort:
                        score += 15
            
            # Inhalt-Match
            inhalt_lower = eintrag.inhalt.lower()
            for wort in anfrage_woerter:
                if len(wort) > 3 and wort in inhalt_lower:
                    score += 3
            
            eintrag.relevanz = score
        
        sortiert = sorted(self.eintraege, key=lambda e: e.relevanz, reverse=True)
        return [e for e in sortiert[:max_ergebnisse] if e.relevanz > 0]
    
    def beantworte_frage(self, frage: str) -> Dict:
        """Beantwortet eine Frage mit RAG."""
        relevante = self.suche(frage, max_ergebnisse=3)
        
        if not relevante:
            return {
                "antwort": "Zu dieser Frage habe ich keine Informationen in meiner Wissensbasis.",
                "quellen": [],
                "konfidenz": 0
            }
        
        # Antwort aus relevantem Eintrag
        haupt = relevante[0]
        
        antwort = f"**{haupt.titel}**\n\n"
        antwort += haupt.inhalt.strip() + "\n\n"
        antwort += f"_Rechtsgrundlage: {haupt.rechtsgrundlage}_"
        
        if len(relevante) > 1:
            antwort += "\n\n**Siehe auch:**\n"
            for e in relevante[1:]:
                antwort += f"• {e.titel}\n"
        
        return {
            "antwort": antwort,
            "quellen": [{"titel": e.titel, "rechtsgrundlage": e.rechtsgrundlage} for e in relevante],
            "konfidenz": min(100, int(relevante[0].relevanz))
        }
    
    def get_kategorien(self) -> List[str]:
        """Gibt alle Kategorien zurück."""
        return list(set(e.kategorie for e in self.eintraege))
    
    def get_nach_kategorie(self, kategorie: str) -> List[WissensEintrag]:
        """Filtert nach Kategorie."""
        return [e for e in self.eintraege if e.kategorie == kategorie]
