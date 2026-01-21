"""
JuraConnect - Arbeitsrecht Rechner-Modul
=========================================
Alle Berechnungsfunktionen für deutsches Arbeitsrecht
"""

from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math


class Kuendigungsgrund(Enum):
    BETRIEBSBEDINGT = "betriebsbedingt"
    VERHALTENSBEDINGT = "verhaltensbedingt"
    PERSONENBEDINGT = "personenbedingt"
    AUSSERORDENTLICH = "außerordentlich"


@dataclass
class Kuendigungsfrist:
    gesetzliche_frist: int
    vertragliche_frist: Optional[int] = None
    frist_text: str = ""
    ende_zum: str = ""
    fruehester_termin: Optional[date] = None
    berechnung_details: str = ""


@dataclass
class Abfindungsberechnung:
    regelabfindung: float
    minimum: float
    maximum: float
    empfehlung: float
    faktoren: Dict[str, float] = field(default_factory=dict)
    begruendung: str = ""


@dataclass
class Prozesskostenberechnung:
    streitwert: float
    gerichtskosten: float
    anwaltskosten_eigen: float
    anwaltskosten_gegner: float
    gesamt_1_instanz: float
    gesamt_2_instanz: float
    mit_vergleich: float
    ohne_rsvg: float
    details: Dict[str, float] = field(default_factory=dict)


@dataclass
class Urlaubsberechnung:
    jahresurlaub: int
    anteiliger_urlaub: float
    resturlaub: float
    urlaubsabgeltung: float
    berechnung: str = ""


@dataclass
class Ueberstundenberechnung:
    anzahl_stunden: float
    stundenlohn: float
    grundverguetung: float
    zuschlag_prozent: float
    zuschlag_betrag: float
    gesamt_brutto: float
    verjaehrt_ab: Optional[date] = None


class KuendigungsfristenRechner:
    """Berechnet Kündigungsfristen nach § 622 BGB"""
    
    FRISTEN_ARBEITGEBER = [
        (0, 4, "4 Wochen", 28),
        (2, 5, "1 Monat", 30),
        (5, 8, "2 Monate", 60),
        (8, 10, "3 Monate", 90),
        (10, 12, "4 Monate", 120),
        (12, 15, "5 Monate", 150),
        (15, 20, "6 Monate", 180),
        (20, 999, "7 Monate", 210),
    ]
    
    FRIST_ARBEITNEHMER = 28
    
    def berechne_frist(self, eintrittsdatum: date, kuendigungsdatum: date,
                       ist_arbeitgeber_kuendigung: bool = True,
                       probezeit: bool = False,
                       vertragliche_frist_tage: int = None) -> Kuendigungsfrist:
        zugehoerigkeit_jahre = (kuendigungsdatum - eintrittsdatum).days / 365.25
        
        if probezeit:
            frist_tage = 14
            frist_text = "2 Wochen (Probezeit)"
            ende_zum = "jederzeit"
        elif ist_arbeitgeber_kuendigung:
            frist_tage = 28
            frist_text = "4 Wochen"
            ende_zum = "zum 15. oder Monatsende"
            
            for min_jahre, max_jahre, text, tage in self.FRISTEN_ARBEITGEBER:
                if min_jahre <= zugehoerigkeit_jahre < max_jahre:
                    frist_tage = tage
                    frist_text = text
                    if min_jahre >= 2:
                        ende_zum = "zum Monatsende"
                    break
        else:
            frist_tage = self.FRIST_ARBEITNEHMER
            frist_text = "4 Wochen"
            ende_zum = "zum 15. oder Monatsende"
        
        fruehester = kuendigungsdatum + timedelta(days=frist_tage)
        
        if ende_zum == "zum Monatsende":
            if fruehester.day > 1:
                if fruehester.month == 12:
                    fruehester = date(fruehester.year + 1, 1, 1) - timedelta(days=1)
                else:
                    fruehester = date(fruehester.year, fruehester.month + 1, 1) - timedelta(days=1)
        elif ende_zum == "zum 15. oder Monatsende":
            if fruehester.day <= 15:
                fruehester = date(fruehester.year, fruehester.month, 15)
            else:
                if fruehester.month == 12:
                    fruehester = date(fruehester.year + 1, 1, 1) - timedelta(days=1)
                else:
                    fruehester = date(fruehester.year, fruehester.month + 1, 1) - timedelta(days=1)
        
        berechnung = f"""Betriebszugehörigkeit: {zugehoerigkeit_jahre:.1f} Jahre
Gesetzliche Frist: {frist_text}
Kündigung vom: {kuendigungsdatum.strftime('%d.%m.%Y')}
Frühester Beendigungstermin: {fruehester.strftime('%d.%m.%Y')}"""
        
        return Kuendigungsfrist(
            gesetzliche_frist=frist_tage, vertragliche_frist=vertragliche_frist_tage,
            frist_text=frist_text, ende_zum=ende_zum, fruehester_termin=fruehester,
            berechnung_details=berechnung
        )
    
    def berechne_3_wochen_frist(self, zugang_kuendigung: date) -> Dict:
        fristende = zugang_kuendigung + timedelta(days=21)
        heute = date.today()
        verbleibend = (fristende - heute).days
        
        if fristende.weekday() == 5:
            fristende += timedelta(days=2)
        elif fristende.weekday() == 6:
            fristende += timedelta(days=1)
        
        hinweise = {
            -999: "⚠️ FRIST ABGELAUFEN! Nachträgliche Zulassung nur bei Verschulden (§ 5 KSchG)",
            0: "🚨 HEUTE LETZTER TAG! Sofort Klage einreichen!",
            3: "🚨 HÖCHSTE EILE! Sofort Klage einreichen!",
            7: "⚡ DRINGEND! Klage schnellstmöglich vorbereiten!",
            14: "📋 Zeit für sorgfältige Klagevorbereitung",
            999: "✅ Ausreichend Zeit für Mandatierung und Klagevorbereitung"
        }
        
        hinweis = ""
        for grenze, text in sorted(hinweise.items()):
            if verbleibend <= grenze:
                hinweis = text
                break
        
        return {
            "zugang": zugang_kuendigung, "fristende": fristende,
            "verbleibende_tage": max(0, verbleibend), "abgelaufen": verbleibend < 0,
            "dringend": 0 < verbleibend <= 7, "hinweis": hinweis
        }


class AbfindungsRechner:
    """Berechnet Abfindungen nach verschiedenen Methoden"""
    
    BRANCHENFAKTOREN = {
        "industrie": 1.2, "handel": 0.9, "dienstleistung": 1.0,
        "oeffentlicher_dienst": 0.8, "it": 1.3, "finanzen": 1.4,
        "gesundheit": 0.9, "sonstige": 1.0
    }
    
    def berechne(self, bruttogehalt: float, betriebszugehoerigkeit_jahre: float,
                 alter: int = None, branche: str = "sonstige",
                 kuendigungsgrund: Kuendigungsgrund = Kuendigungsgrund.BETRIEBSBEDINGT,
                 sozialauswahl_fehler: bool = False,
                 kuendigungsschutz: bool = True) -> Abfindungsberechnung:
        faktoren = {}
        regelabfindung = bruttogehalt * betriebszugehoerigkeit_jahre * 0.5
        faktoren["Regelabfindung (0,5 × Gehalt × Jahre)"] = 0.5
        
        basis_faktor = 0.5
        branchen_faktor = self.BRANCHENFAKTOREN.get(branche, 1.0)
        faktoren[f"Branchenfaktor ({branche})"] = branchen_faktor
        
        alter_faktor = 1.0
        if alter:
            if alter >= 55:
                alter_faktor = 1.3
                faktoren["Altersfaktor (55+)"] = 1.3
            elif alter >= 50:
                alter_faktor = 1.2
                faktoren["Altersfaktor (50+)"] = 1.2
            elif alter < 30:
                alter_faktor = 0.8
                faktoren["Altersfaktor (unter 30)"] = 0.8
        
        grund_faktor = 1.0
        if kuendigungsgrund == Kuendigungsgrund.BETRIEBSBEDINGT:
            grund_faktor = 1.0
        elif kuendigungsgrund == Kuendigungsgrund.VERHALTENSBEDINGT:
            grund_faktor = 0.5
            faktoren["Kündigungsgrund (verhaltensbedingt)"] = 0.5
        elif kuendigungsgrund == Kuendigungsgrund.PERSONENBEDINGT:
            grund_faktor = 0.7
            faktoren["Kündigungsgrund (personenbedingt)"] = 0.7
        
        if sozialauswahl_fehler:
            faktoren["Sozialauswahl-Fehler"] = 1.5
            grund_faktor *= 1.5
        
        if not kuendigungsschutz:
            faktoren["Kein KSchG-Schutz"] = 0.3
            grund_faktor *= 0.3
        
        gesamt_faktor = basis_faktor * branchen_faktor * alter_faktor * grund_faktor
        empfehlung = bruttogehalt * betriebszugehoerigkeit_jahre * gesamt_faktor
        minimum = regelabfindung * 0.5
        maximum = regelabfindung * 2.0
        
        begruendung = f"""Berechnungsgrundlage:
- Bruttogehalt: {bruttogehalt:,.2f} €
- Betriebszugehörigkeit: {betriebszugehoerigkeit_jahre:.1f} Jahre
- Alter: {alter if alter else 'nicht angegeben'}

Regelabfindung (§ 1a KSchG):
{betriebszugehoerigkeit_jahre:.1f} × {bruttogehalt:,.2f} € × 0,5 = {regelabfindung:,.2f} €

Verhandlungsspanne:
- Minimum: {minimum:,.2f} €
- Empfehlung: {empfehlung:,.2f} €
- Maximum: {maximum:,.2f} €"""
        
        return Abfindungsberechnung(
            regelabfindung=regelabfindung, minimum=minimum, maximum=maximum,
            empfehlung=empfehlung, faktoren=faktoren, begruendung=begruendung
        )


class ProzesskostenRechner:
    """Berechnet Prozesskosten nach RVG und GKG"""
    
    RVG_TABELLE = [
        (500, 49), (1000, 88), (1500, 127), (2000, 166), (3000, 222),
        (4000, 278), (5000, 334), (6000, 390), (7000, 446), (8000, 502),
        (9000, 558), (10000, 614), (13000, 666), (16000, 718), (19000, 770),
        (22000, 822), (25000, 874), (30000, 955), (35000, 1036), (40000, 1117),
        (45000, 1198), (50000, 1279), (65000, 1373), (80000, 1467),
        (95000, 1561), (110000, 1655), (125000, 1749), (140000, 1843),
        (155000, 1937), (170000, 2031), (185000, 2125), (200000, 2219),
    ]
    
    GKG_FAKTOR = 2.0
    
    def _ermittle_gebuehr(self, streitwert: float) -> float:
        for grenze, gebuehr in self.RVG_TABELLE:
            if streitwert <= grenze:
                return gebuehr
        return 2219 + ((streitwert - 200000) / 50000) * 198
    
    def berechne(self, streitwert: float) -> Prozesskostenberechnung:
        gebuehr = self._ermittle_gebuehr(streitwert)
        details = {}
        
        verfahrensgebuehr = gebuehr * 1.3
        terminsgebuehr = gebuehr * 1.2
        auslagenpauschale = 20.0
        
        anwaltskosten_netto = verfahrensgebuehr + terminsgebuehr + auslagenpauschale
        anwaltskosten_brutto = anwaltskosten_netto * 1.19
        
        details["Verfahrensgebühr (1,3)"] = verfahrensgebuehr
        details["Terminsgebühr (1,2)"] = terminsgebuehr
        details["Auslagenpauschale"] = auslagenpauschale
        details["MwSt (19%)"] = anwaltskosten_netto * 0.19
        
        gerichtskosten = gebuehr * self.GKG_FAKTOR
        details["Gerichtskosten (2,0-fach)"] = gerichtskosten
        
        gesamt_1_instanz = anwaltskosten_brutto * 2 + gerichtskosten
        gesamt_2_instanz = gesamt_1_instanz * 1.3
        
        einigungsgebuehr = gebuehr * 1.0
        mit_vergleich = anwaltskosten_brutto + einigungsgebuehr * 1.19
        details["Einigungsgebühr (1,0)"] = einigungsgebuehr
        
        return Prozesskostenberechnung(
            streitwert=streitwert, gerichtskosten=gerichtskosten,
            anwaltskosten_eigen=anwaltskosten_brutto,
            anwaltskosten_gegner=anwaltskosten_brutto,
            gesamt_1_instanz=gesamt_1_instanz, gesamt_2_instanz=gesamt_2_instanz,
            mit_vergleich=mit_vergleich, ohne_rsvg=gesamt_1_instanz, details=details
        )


class UrlaubsRechner:
    """Berechnet Urlaubsansprüche und -abgeltung"""
    
    GESETZLICHER_MINDESTURLAUB = 20
    
    def berechne_anteilig(self, jahresurlaub: int, eintrittsdatum: date,
                          austrittsdatum: date = None,
                          bereits_genommen: int = 0) -> Urlaubsberechnung:
        jahr = eintrittsdatum.year
        
        if eintrittsdatum.month > 1 or eintrittsdatum.day > 1:
            monate_im_jahr = 12 - eintrittsdatum.month + 1
            if eintrittsdatum.day > 15:
                monate_im_jahr -= 1
        else:
            monate_im_jahr = 12
        
        if austrittsdatum:
            if austrittsdatum.year == eintrittsdatum.year:
                monate_beschaeftigt = austrittsdatum.month - eintrittsdatum.month + 1
                if austrittsdatum.day < 15:
                    monate_beschaeftigt -= 1
                monate_im_jahr = monate_beschaeftigt
            else:
                monate_im_jahr = austrittsdatum.month
                if austrittsdatum.day < 15:
                    monate_im_jahr -= 1
        
        anteilig = (jahresurlaub / 12) * monate_im_jahr
        anteilig = math.ceil(anteilig * 2) / 2
        resturlaub = max(0, anteilig - bereits_genommen)
        
        berechnung = f"""Jahresurlaub: {jahresurlaub} Tage
Beschäftigungsmonate: {monate_im_jahr}
Anteiliger Urlaub: {jahresurlaub} ÷ 12 × {monate_im_jahr} = {anteilig:.1f} Tage
Bereits genommen: {bereits_genommen} Tage
Resturlaub: {resturlaub:.1f} Tage"""
        
        return Urlaubsberechnung(
            jahresurlaub=jahresurlaub, anteiliger_urlaub=anteilig,
            resturlaub=resturlaub, urlaubsabgeltung=0, berechnung=berechnung
        )
    
    def berechne_abgeltung(self, resturlaub: float, bruttogehalt: float,
                           wochenstunden: float = 40,
                           arbeitstage_pro_woche: int = 5) -> float:
        tagesverguetung = (bruttogehalt * 3) / 13 / arbeitstage_pro_woche
        return tagesverguetung * resturlaub


class UeberstundenRechner:
    """Berechnet Überstundenansprüche"""
    
    STANDARD_ZUSCHLAEGE = {
        "normal": 0.0, "tariflich_25": 0.25, "tariflich_50": 0.50,
        "nacht": 0.25, "sonntag": 0.50, "feiertag": 1.00,
    }
    
    def berechne_stundenlohn(self, bruttogehalt: float, wochenstunden: float = 40) -> float:
        return bruttogehalt / (wochenstunden * 4.33)
    
    def berechne(self, bruttogehalt: float, ueberstunden: float,
                 wochenstunden: float = 40, zuschlag_art: str = "normal",
                 verjaehrung_pruefen: bool = True) -> Ueberstundenberechnung:
        stundenlohn = self.berechne_stundenlohn(bruttogehalt, wochenstunden)
        zuschlag_prozent = self.STANDARD_ZUSCHLAEGE.get(zuschlag_art, 0.0)
        
        grundverguetung = stundenlohn * ueberstunden
        zuschlag_betrag = grundverguetung * zuschlag_prozent
        gesamt = grundverguetung + zuschlag_betrag
        
        verjaehrt_ab = None
        if verjaehrung_pruefen:
            heute = date.today()
            verjaehrt_ab = date(heute.year - 3, 12, 31)
        
        return Ueberstundenberechnung(
            anzahl_stunden=ueberstunden, stundenlohn=stundenlohn,
            grundverguetung=grundverguetung, zuschlag_prozent=zuschlag_prozent * 100,
            zuschlag_betrag=zuschlag_betrag, gesamt_brutto=gesamt, verjaehrt_ab=verjaehrt_ab
        )


class VerjaehrungsRechner:
    """Berechnet Verjährungsfristen im Arbeitsrecht"""
    
    FRISTEN = {
        "lohn": (3, "Jahre", "Regelverjährung § 195 BGB"),
        "urlaub": (3, "Jahre", "BAG-Rechtsprechung"),
        "zeugnis": (3, "Jahre", "Regelverjährung"),
        "kuendigungsschutzklage": (3, "Wochen", "§ 4 KSchG - AUSSCHLUSSFRIST!"),
        "schadensersatz": (3, "Jahre", "Regelverjährung"),
        "arbeitszeugnis_berichtigung": (5, "Monate", "Rechtsprechung LAG"),
    }
    
    def berechne(self, anspruchs_art: str, entstehungsdatum: date) -> Dict:
        if anspruchs_art not in self.FRISTEN:
            return {"fehler": "Unbekannte Anspruchsart"}
        
        dauer, einheit, hinweis = self.FRISTEN[anspruchs_art]
        
        if einheit == "Jahre":
            verjährung_start = date(entstehungsdatum.year, 12, 31)
            verjährung_ende = date(entstehungsdatum.year + dauer, 12, 31)
        elif einheit == "Wochen":
            verjährung_ende = entstehungsdatum + timedelta(weeks=dauer)
            verjährung_start = entstehungsdatum
        elif einheit == "Monate":
            verjährung_start = entstehungsdatum
            monat = entstehungsdatum.month + dauer
            jahr = entstehungsdatum.year
            while monat > 12:
                monat -= 12
                jahr += 1
            verjährung_ende = date(jahr, monat, min(entstehungsdatum.day, 28))
        
        heute = date.today()
        verbleibend = (verjährung_ende - heute).days
        
        return {
            "anspruch": anspruchs_art, "entstehung": entstehungsdatum,
            "verjährung_beginn": verjährung_start, "verjährung_ende": verjährung_ende,
            "verbleibende_tage": max(0, verbleibend), "verjährt": verbleibend < 0,
            "hinweis": hinweis, "warnung": "⚠️ Bald verjährt!" if 0 < verbleibend < 90 else None
        }


# Convenience-Funktionen
def berechne_kuendigungsfrist(eintritt: date, kuendigung: date, arbeitgeber: bool = True) -> Kuendigungsfrist:
    return KuendigungsfristenRechner().berechne_frist(eintritt, kuendigung, arbeitgeber)

def berechne_abfindung(gehalt: float, jahre: float, alter: int = None) -> Abfindungsberechnung:
    return AbfindungsRechner().berechne(gehalt, jahre, alter)

def berechne_prozesskosten(streitwert: float) -> Prozesskostenberechnung:
    return ProzesskostenRechner().berechne(streitwert)

def berechne_3_wochen_frist(zugang: date) -> Dict:
    return KuendigungsfristenRechner().berechne_3_wochen_frist(zugang)
