"""
JuraConnect - Arbeitszeugnis Analyse
KI-gestützte Analyse von Arbeitszeugnissen
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum
import re


class ZeugnisNote(Enum):
    SEHR_GUT = 1
    GUT = 2
    BEFRIEDIGEND = 3
    AUSREICHEND = 4
    MANGELHAFT = 5
    UNGENUEGEND = 6


@dataclass
class Formulierung:
    text: str
    kategorie: str
    bewertung: ZeugnisNote
    bedeutung: str
    problematisch: bool = False
    verbesserungsvorschlag: str = ""


@dataclass
class ZeugnisAnalyse:
    gesamtnote: ZeugnisNote
    gesamtnote_text: str
    konfidenz: float
    formulierungen: List[Formulierung] = field(default_factory=list)
    vollstaendig: bool = False
    fehlende_elemente: List[str] = field(default_factory=list)
    probleme: List[str] = field(default_factory=list)
    geheimcodes: List[Dict] = field(default_factory=list)
    verbesserungen: List[str] = field(default_factory=list)
    zusammenfassung: str = ""
    empfehlung: str = ""


class ZeugnisAnalysator:
    """Analysiert Arbeitszeugnisse"""
    
    LEISTUNGSFORMULIERUNGEN = {
        "stets zu unserer vollsten zufriedenheit": (ZeugnisNote.SEHR_GUT, "Sehr gute Leistung"),
        "stets zur vollsten zufriedenheit": (ZeugnisNote.SEHR_GUT, "Sehr gute Leistung"),
        "in jeder hinsicht außerordentlich": (ZeugnisNote.SEHR_GUT, "Herausragend"),
        "stets zu unserer vollen zufriedenheit": (ZeugnisNote.GUT, "Gute Leistung"),
        "zu unserer vollsten zufriedenheit": (ZeugnisNote.GUT, "Gut (fehlt 'stets')"),
        "zu unserer zufriedenheit": (ZeugnisNote.BEFRIEDIGEND, "Durchschnitt"),
        "stets zu unserer zufriedenheit": (ZeugnisNote.BEFRIEDIGEND, "Befriedigend"),
        "im großen und ganzen zu unserer zufriedenheit": (ZeugnisNote.AUSREICHEND, "Gerade ausreichend"),
        "im wesentlichen zu unserer zufriedenheit": (ZeugnisNote.AUSREICHEND, "Nur teilweise"),
        "hat sich bemüht": (ZeugnisNote.MANGELHAFT, "Erfolglos bemüht"),
        "war bemüht": (ZeugnisNote.MANGELHAFT, "Ohne messbaren Erfolg"),
        "zeigte interesse": (ZeugnisNote.MANGELHAFT, "Nur Interesse, keine Leistung"),
    }
    
    GEHEIMCODES = {
        "gesellig": "Alkoholprobleme",
        "trug zur verbesserung des betriebsklimas bei": "Störte den Betriebsfrieden",
        "zeigte verständnis für seine arbeit": "Hat nichts geleistet",
        "bemühte sich, den anforderungen gerecht zu werden": "War überfordert",
        "war tüchtig und wusste sich gut zu verkaufen": "Wichtigtuer",
        "erledigte alle aufgaben pflichtbewusst": "Keine Eigeninitiative",
        "war bei kollegen sehr beliebt": "Nicht bei Vorgesetzten",
        "hat alle arbeiten ordnungsgemäß erledigt": "Nur Routine",
        "wir wünschen ihm für die zukunft alles gute, besonders gesundheit": "War oft krank",
        "er verlässt uns auf eigenen wunsch": "Wurde gegangen",
        "wir haben uns einvernehmlich getrennt": "Kündigung durch AG",
    }
    
    def analysiere(self, zeugnis_text: str) -> ZeugnisAnalyse:
        text = zeugnis_text.lower()
        
        analyse = ZeugnisAnalyse(
            gesamtnote=ZeugnisNote.BEFRIEDIGEND,
            gesamtnote_text="", konfidenz=0.0
        )
        
        self._erkenne_formulierungen(text, analyse)
        self._finde_geheimcodes(text, analyse)
        self._pruefe_vollstaendigkeit(text, analyse)
        self._berechne_gesamtnote(analyse)
        self._generiere_verbesserungen(analyse)
        self._erstelle_zusammenfassung(analyse)
        
        return analyse
    
    def _erkenne_formulierungen(self, text: str, analyse: ZeugnisAnalyse):
        for muster, (note, bedeutung) in self.LEISTUNGSFORMULIERUNGEN.items():
            if muster in text:
                analyse.formulierungen.append(Formulierung(
                    text=muster, kategorie="leistung", bewertung=note,
                    bedeutung=bedeutung, problematisch=note.value >= 4
                ))
    
    def _finde_geheimcodes(self, text: str, analyse: ZeugnisAnalyse):
        for muster, bedeutung in self.GEHEIMCODES.items():
            if muster in text:
                analyse.geheimcodes.append({
                    "formulierung": muster,
                    "versteckte_bedeutung": bedeutung,
                    "warnung": True
                })
                analyse.probleme.append(f"⚠️ Geheimcode: '{muster}' → {bedeutung}")
    
    def _pruefe_vollstaendigkeit(self, text: str, analyse: ZeugnisAnalyse):
        pruefungen = [
            ("zeugnis", "Überschrift"),
            (r"(geboren|geb\.)", "Persönliche Daten"),
            (r"\d{1,2}\.\d{1,2}\.\d{2,4}", "Beschäftigungsdauer"),
            (r"(aufgaben|tätigkeiten)", "Tätigkeitsbeschreibung"),
            (r"(zufriedenheit|leistung)", "Leistungsbeurteilung"),
            (r"(verhalten|kollegen)", "Verhaltensbeurteilung"),
        ]
        
        for muster, name in pruefungen:
            if not re.search(muster, text, re.IGNORECASE):
                analyse.fehlende_elemente.append(name)
        
        analyse.vollstaendig = len(analyse.fehlende_elemente) == 0
    
    def _berechne_gesamtnote(self, analyse: ZeugnisAnalyse):
        if not analyse.formulierungen:
            analyse.gesamtnote = ZeugnisNote.BEFRIEDIGEND
            analyse.gesamtnote_text = "Note 3 (keine eindeutigen Formulierungen)"
            analyse.konfidenz = 0.3
            return
        
        noten = [f.bewertung.value for f in analyse.formulierungen]
        durchschnitt = sum(noten) / len(noten)
        
        if durchschnitt <= 1.4:
            analyse.gesamtnote = ZeugnisNote.SEHR_GUT
        elif durchschnitt <= 2.4:
            analyse.gesamtnote = ZeugnisNote.GUT
        elif durchschnitt <= 3.4:
            analyse.gesamtnote = ZeugnisNote.BEFRIEDIGEND
        elif durchschnitt <= 4.4:
            analyse.gesamtnote = ZeugnisNote.AUSREICHEND
        else:
            analyse.gesamtnote = ZeugnisNote.MANGELHAFT
        
        analyse.konfidenz = min(1.0, len(noten) * 0.2)
        
        if analyse.geheimcodes:
            neue_note = min(6, analyse.gesamtnote.value + 1)
            for note in ZeugnisNote:
                if note.value == neue_note:
                    analyse.gesamtnote = note
                    break
        
        note_texte = {
            ZeugnisNote.SEHR_GUT: "Note 1 (sehr gut)",
            ZeugnisNote.GUT: "Note 2 (gut)",
            ZeugnisNote.BEFRIEDIGEND: "Note 3 (befriedigend)",
            ZeugnisNote.AUSREICHEND: "Note 4 (ausreichend)",
            ZeugnisNote.MANGELHAFT: "Note 5 (mangelhaft)",
        }
        analyse.gesamtnote_text = note_texte.get(analyse.gesamtnote, "Unbekannt")
    
    def _generiere_verbesserungen(self, analyse: ZeugnisAnalyse):
        for element in analyse.fehlende_elemente:
            analyse.verbesserungen.append(f"📝 {element} sollte ergänzt werden")
        
        for code in analyse.geheimcodes:
            analyse.verbesserungen.append(f"🚫 Entfernen: '{code['formulierung']}'")
        
        verbesserungen_map = {
            "hat sich bemüht": "stets zu unserer vollen Zufriedenheit",
            "war bemüht": "hat engagiert und erfolgreich gearbeitet",
            "zu unserer zufriedenheit": "stets zu unserer vollen Zufriedenheit",
        }
        
        for form in analyse.formulierungen:
            if form.text in verbesserungen_map:
                analyse.verbesserungen.append(
                    f"💡 '{form.text}' → '{verbesserungen_map[form.text]}'"
                )
    
    def _erstelle_zusammenfassung(self, analyse: ZeugnisAnalyse):
        if analyse.gesamtnote.value <= 2 and not analyse.geheimcodes:
            analyse.empfehlung = "akzeptieren"
        elif analyse.gesamtnote.value <= 3 and len(analyse.probleme) <= 2:
            analyse.empfehlung = "nachverhandeln"
        else:
            analyse.empfehlung = "klagen"


def analysiere_zeugnis(text: str) -> ZeugnisAnalyse:
    return ZeugnisAnalysator().analysiere(text)
