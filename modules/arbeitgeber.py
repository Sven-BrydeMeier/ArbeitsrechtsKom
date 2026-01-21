"""
JuraConnect - Arbeitgeber Modul
Tools für Arbeitgeber im Arbeitsrecht
"""

from datetime import date, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum


class KuendigungsgrundAG(Enum):
    BETRIEBSBEDINGT = "betriebsbedingt"
    VERHALTENSBEDINGT = "verhaltensbedingt"
    PERSONENBEDINGT = "personenbedingt"
    AUSSERORDENTLICH = "außerordentlich"
    PROBEZEIT = "probezeit"


@dataclass
class Mitarbeiter:
    name: str
    geburtsdatum: date
    eintrittsdatum: date
    bruttogehalt: float
    unterhaltspflichten: int = 0
    schwerbehindert: bool = False
    schwerbehindert_grad: int = 0
    gleichgestellt: bool = False
    vergleichbar: bool = True
    leistungstraeger: bool = False
    
    @property
    def alter(self) -> int:
        heute = date.today()
        return heute.year - self.geburtsdatum.year - (
            (heute.month, heute.day) < (self.geburtsdatum.month, self.geburtsdatum.day))
    
    @property
    def betriebszugehoerigkeit_jahre(self) -> float:
        return (date.today() - self.eintrittsdatum).days / 365.25


@dataclass
class SozialauswahlErgebnis:
    mitarbeiter: str
    punkte_gesamt: int
    punkte_details: Dict[str, int]
    rang: int
    kuendigung_empfohlen: bool
    begruendung: str


@dataclass
class KuendigungsCheckliste:
    schritt: str
    erledigt: bool
    erforderlich: bool
    hinweis: str
    frist: Optional[date] = None


@dataclass
class Abmahnung:
    datum: date
    mitarbeiter: str
    sachverhalt: str
    pflichtverletzung: str
    hinweis_kuendigung: str
    volltext: str


@dataclass
class Vertragsbaustein:
    kategorie: str
    titel: str
    text: str
    pflicht: bool
    varianten: List[str] = field(default_factory=list)


class SozialauswahlRechner:
    """Berechnet Sozialauswahl nach BAG-Punktesystem"""
    
    def berechne_punkte(self, mitarbeiter: Mitarbeiter) -> Tuple[int, Dict[str, int]]:
        details = {}
        
        # Alter: 1 Punkt pro Jahr ab 18
        alter_punkte = min(max(0, mitarbeiter.alter - 18), 55)
        details["Alter"] = alter_punkte
        
        # Betriebszugehörigkeit: 1 Punkt pro Jahr, max 30
        bz_punkte = min(int(mitarbeiter.betriebszugehoerigkeit_jahre), 30)
        details["Betriebszugehörigkeit"] = bz_punkte
        
        # Unterhaltspflichten: 4 Punkte pro Person, max 20
        up_punkte = min(mitarbeiter.unterhaltspflichten * 4, 20)
        details["Unterhaltspflichten"] = up_punkte
        
        # Schwerbehinderung: 5 Punkte + 1 pro 10 GdB über 50
        sb_punkte = 0
        if mitarbeiter.schwerbehindert and mitarbeiter.schwerbehindert_grad >= 50:
            sb_punkte = 5 + (mitarbeiter.schwerbehindert_grad - 50) // 10
        elif mitarbeiter.gleichgestellt:
            sb_punkte = 5
        sb_punkte = min(sb_punkte, 10)
        details["Schwerbehinderung"] = sb_punkte
        
        return sum(details.values()), details
    
    def fuehre_sozialauswahl_durch(self, mitarbeiter_liste: List[Mitarbeiter],
                                    anzahl_kuendigungen: int) -> List[SozialauswahlErgebnis]:
        ergebnisse = []
        vergleichbar = [m for m in mitarbeiter_liste if m.vergleichbar]
        
        bewertungen = []
        for ma in vergleichbar:
            if ma.leistungstraeger:
                bewertungen.append((ma, 999, {"Leistungsträger": "Herausnahme"}))
            else:
                punkte, details = self.berechne_punkte(ma)
                bewertungen.append((ma, punkte, details))
        
        bewertungen.sort(key=lambda x: x[1])
        
        for rang, (ma, punkte, details) in enumerate(bewertungen, 1):
            kuendigung = rang <= anzahl_kuendigungen and punkte < 999
            begruendung = "Leistungsträger" if punkte == 999 else (
                f"Rang {rang}: {'Kündigung' if kuendigung else 'Verbleibt'}"
            )
            
            ergebnisse.append(SozialauswahlErgebnis(
                mitarbeiter=ma.name, punkte_gesamt=punkte if punkte < 999 else 0,
                punkte_details=details, rang=rang,
                kuendigung_empfohlen=kuendigung, begruendung=begruendung
            ))
        
        return ergebnisse


class KuendigungsAssistent:
    """Führt durch den Kündigungsprozess"""
    
    def erstelle_checkliste(self, grund: KuendigungsgrundAG,
                            hat_betriebsrat: bool = False,
                            besonderer_schutz: str = None,
                            mitarbeiter_anzahl: int = 50) -> List[KuendigungsCheckliste]:
        checkliste = []
        
        checkliste.append(KuendigungsCheckliste(
            schritt="1. Kündigungsgrund dokumentieren",
            erledigt=False, erforderlich=True,
            hinweis="Alle Fakten und Beweise sammeln"
        ))
        
        if grund == KuendigungsgrundAG.BETRIEBSBEDINGT:
            checkliste.extend([
                KuendigungsCheckliste("2. Unternehmerische Entscheidung dokumentieren",
                    False, True, "Wirtschaftliche Gründe schriftlich festhalten"),
                KuendigungsCheckliste("3. Wegfall des Arbeitsplatzes belegen",
                    False, True, "Dauerhafter Wegfall nachweisen"),
                KuendigungsCheckliste("4. Sozialauswahl durchführen",
                    False, True, "Vergleichbare MA ermitteln, Punktesystem anwenden"),
                KuendigungsCheckliste("5. Weiterbeschäftigung prüfen",
                    False, True, "Freie Stellen im Unternehmen prüfen"),
            ])
        elif grund == KuendigungsgrundAG.VERHALTENSBEDINGT:
            checkliste.extend([
                KuendigungsCheckliste("2. Vorherige Abmahnung(en) prüfen",
                    False, True, "Einschlägige Abmahnung erforderlich"),
                KuendigungsCheckliste("3. Pflichtverletzung dokumentieren",
                    False, True, "Datum, Uhrzeit, Zeugen, Art der Verletzung"),
                KuendigungsCheckliste("4. Verhältnismäßigkeit prüfen",
                    False, True, "Ist Kündigung das mildeste Mittel?"),
            ])
        elif grund == KuendigungsgrundAG.AUSSERORDENTLICH:
            checkliste.extend([
                KuendigungsCheckliste("2. Wichtigen Grund dokumentieren",
                    False, True, "Schwerwiegende Pflichtverletzung"),
                KuendigungsCheckliste("3. 2-Wochen-Frist beachten",
                    False, True, "Ab Kenntnis des Kündigungsgrundes",
                    frist=date.today() + timedelta(days=14)),
            ])
        
        if hat_betriebsrat:
            checkliste.append(KuendigungsCheckliste(
                "📋 Betriebsrat anhören (§ 102 BetrVG)",
                False, True, "Schriftlich mit allen Gründen"
            ))
        
        if besonderer_schutz == "schwerbehindert":
            checkliste.append(KuendigungsCheckliste(
                "🛡️ Zustimmung Integrationsamt einholen",
                False, True, "VOR Ausspruch der Kündigung!"
            ))
        elif besonderer_schutz == "schwanger":
            checkliste.append(KuendigungsCheckliste(
                "🛡️ Zustimmung Gewerbeaufsicht einholen",
                False, True, "Wird nur selten erteilt"
            ))
        
        checkliste.extend([
            KuendigungsCheckliste("📝 Kündigungsschreiben erstellen",
                False, True, "Schriftform § 623 BGB!"),
            KuendigungsCheckliste("📨 Zustellung sicherstellen",
                False, True, "Übergabe mit Zeugen oder Einschreiben"),
        ])
        
        return checkliste


class AbmahnungsGenerator:
    """Generiert Abmahnungen"""
    
    GRUENDE = {
        "verspaetung": ("Wiederholtes Zuspätkommen", "Verletzung der Pflicht zur pünktlichen Arbeitsaufnahme"),
        "arbeitsverweigerung": ("Arbeitsverweigerung", "Weigerung, die Arbeitsleistung zu erbringen"),
        "unentschuldigtes_fehlen": ("Unentschuldigtes Fehlen", "Unentschuldigtes Fernbleiben"),
        "beleidigung": ("Beleidigung", "Verletzung der Rücksichtnahmepflicht"),
        "datenschutz": ("Datenschutzverstoß", "Verletzung der Vertraulichkeitspflicht"),
        "internet_missbrauch": ("Private Internetnutzung", "Unerlaubte private Nutzung"),
    }
    
    def generiere(self, mitarbeiter_name: str, grund: str,
                  sachverhalt: str, datum_vorfall: date) -> Abmahnung:
        heute = date.today()
        grund_info = self.GRUENDE.get(grund, (grund, grund))
        
        volltext = f"""ABMAHNUNG

{mitarbeiter_name}
[Adresse]

{heute.strftime('%d.%m.%Y')}

Betreff: Abmahnung wegen {grund_info[0]}

Sehr geehrte/r Frau/Herr {mitarbeiter_name.split()[-1]},

mit diesem Schreiben mahnen wir Sie ab.

I. SACHVERHALT
Am {datum_vorfall.strftime('%d.%m.%Y')} haben Sie sich wie folgt verhalten:
{sachverhalt}

II. PFLICHTVERLETZUNG
Durch das oben geschilderte Verhalten haben Sie gegen Ihre arbeitsvertraglichen 
Pflichten verstoßen: {grund_info[1]}.

III. AUFFORDERUNG UND WARNUNG
Wir fordern Sie auf, künftig Ihre Pflichten zu erfüllen und das Verhalten zu unterlassen.

Wir weisen Sie darauf hin, dass wir im Wiederholungsfall arbeitsrechtliche 
Konsequenzen bis hin zur Kündigung in Betracht ziehen werden.

Mit freundlichen Grüßen

_______________________
Geschäftsführung"""
        
        return Abmahnung(
            datum=heute, mitarbeiter=mitarbeiter_name, sachverhalt=sachverhalt,
            pflichtverletzung=grund_info[1], hinweis_kuendigung="Bei Wiederholung",
            volltext=volltext
        )


class ArbeitsvertragsGenerator:
    """Generiert Arbeitsverträge aus Bausteinen"""
    
    BAUSTEINE = {
        "vertragsparteien": Vertragsbaustein("Grundlagen", "§ 1 Vertragsparteien", 
            """§ 1 Vertragsparteien

Zwischen {arbeitgeber_name}, {arbeitgeber_adresse}
- nachfolgend "Arbeitgeber" -
und {arbeitnehmer_name}, {arbeitnehmer_adresse}
- nachfolgend "Arbeitnehmer" -
wird folgender Arbeitsvertrag geschlossen:""", True),
        
        "taetigkeit": Vertragsbaustein("Grundlagen", "§ 2 Tätigkeit",
            """§ 2 Tätigkeit
Der Arbeitnehmer wird als {position} eingestellt.
Arbeitsort: {arbeitsort}""", True),
        
        "beginn": Vertragsbaustein("Grundlagen", "§ 3 Beginn",
            """§ 3 Beginn und Dauer
Das Arbeitsverhältnis beginnt am {beginn_datum}.
Die ersten sechs Monate gelten als Probezeit.""", True),
        
        "arbeitszeit": Vertragsbaustein("Arbeitszeit", "§ 4 Arbeitszeit",
            """§ 4 Arbeitszeit
Die wöchentliche Arbeitszeit beträgt {wochenstunden} Stunden.""", True),
        
        "verguetung": Vertragsbaustein("Vergütung", "§ 5 Vergütung",
            """§ 5 Vergütung
Das Bruttogehalt beträgt {bruttogehalt} Euro monatlich.
Mit dem Gehalt sind {ueberstunden_inkl} Überstunden monatlich abgegolten.""", True),
        
        "urlaub": Vertragsbaustein("Urlaub", "§ 6 Urlaub",
            """§ 6 Urlaub
Der Jahresurlaub beträgt {urlaubstage} Arbeitstage.""", True),
        
        "kuendigung": Vertragsbaustein("Beendigung", "§ 7 Kündigung",
            """§ 7 Kündigung
Nach der Probezeit: {kuendigungsfrist} zum {kuendigungstermin}.
Schriftform erforderlich.""", True),
        
        "verschwiegenheit": Vertragsbaustein("Pflichten", "§ 8 Verschwiegenheit",
            """§ 8 Verschwiegenheit
Stillschweigen über Betriebs- und Geschäftsgeheimnisse, auch nach Beendigung.""", True),
        
        "schluss": Vertragsbaustein("Sonstiges", "§ 9 Schlussbestimmungen",
            """§ 9 Schlussbestimmungen
Änderungen bedürfen der Schriftform.

{ort}, den {datum}

_______________________    _______________________
Arbeitgeber                Arbeitnehmer""", True),
    }
    
    def generiere_vertrag(self, bausteine: List[str], platzhalter: Dict[str, str]) -> str:
        teile = ["ARBEITSVERTRAG", "=" * 50, ""]
        
        for key in bausteine:
            if key in self.BAUSTEINE:
                text = self.BAUSTEINE[key].text
                for k, v in platzhalter.items():
                    text = text.replace(f"{{{k}}}", str(v))
                teile.append(text)
                teile.append("")
        
        return "\n".join(teile)
    
    def get_pflicht_bausteine(self) -> List[str]:
        return [k for k, b in self.BAUSTEINE.items() if b.pflicht]


class ComplianceCheckliste:
    """Compliance-Checklisten für HR"""
    
    CHECKLISTEN = {
        "neueinstellung": [
            ("Arbeitsvertrag unterschrieben", True),
            ("Sozialversicherungsanmeldung", True),
            ("Steuer-ID erhalten", True),
            ("Datenschutz-Belehrung", True),
            ("Arbeitsmittel übergeben", False),
        ],
        "kuendigung_durch_ag": [
            ("Kündigungsgrund dokumentiert", True),
            ("Kündigungsfrist berechnet", True),
            ("Sozialauswahl durchgeführt", True),
            ("Betriebsrat angehört", True),
            ("Besonderer Kündigungsschutz geprüft", True),
            ("Schriftliche Kündigung erstellt", True),
            ("Zustellung nachweisbar", True),
        ],
        "mutterschutz": [
            ("Mitteilung dokumentiert", True),
            ("Gefährdungsbeurteilung", True),
            ("Beschäftigungsverbot geprüft", True),
            ("Mutterschutzfristen berechnet", True),
        ],
        "betriebsrat_wahl": [
            ("Wahlvorstand bestellt", True),
            ("Wählerliste erstellt", True),
            ("Wahlausschreiben", True),
            ("Wahlergebnis verkündet", True),
        ],
        "datenschutz_mitarbeiter": [
            ("Datenschutz-Belehrung", True),
            ("Verarbeitungsverzeichnis", True),
            ("Zugriffsbeschränkungen", True),
            ("Löschkonzept", True),
        ],
    }
    
    def get_checkliste(self, typ: str) -> List[Tuple[str, bool]]:
        return self.CHECKLISTEN.get(typ, [])
    
    def get_alle_typen(self) -> List[str]:
        return list(self.CHECKLISTEN.keys())


def sozialauswahl(mitarbeiter: List[Mitarbeiter], anzahl: int) -> List[SozialauswahlErgebnis]:
    return SozialauswahlRechner().fuehre_sozialauswahl_durch(mitarbeiter, anzahl)

def generiere_abmahnung(name: str, grund: str, sachverhalt: str, datum: date) -> Abmahnung:
    return AbmahnungsGenerator().generiere(name, grund, sachverhalt, datum)
