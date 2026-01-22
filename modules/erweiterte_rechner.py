"""
JuraConnect - Erweiterte Rechner-Module
========================================
- PKH-Rechner (2024 Freibeträge)
- Prozesskostenrechner (3 Instanzen: AG, LAG, BAG)
- Zeiterfassung mit Stoppuhr
- Fristen-Tracker

Version: 2.0.0
"""

from datetime import datetime, timedelta, date
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import math


# =============================================================================
# PKH-RECHNER (Prozesskostenhilfe) - Stand 2024
# =============================================================================

class PKHRechner:
    """
    Berechnet PKH-Anspruch nach § 114 ff. ZPO
    Mit aktuellen Freibeträgen 2024
    """
    
    # Freibeträge 2024 (Stand: 01.01.2024)
    FREIBETRAG_ANTRAGSTELLER = 619  # Grundfreibetrag
    FREIBETRAG_EHEPARTNER = 619
    FREIBETRAG_KIND_BIS_5 = 393
    FREIBETRAG_KIND_6_13 = 451
    FREIBETRAG_KIND_14_17 = 528
    FREIBETRAG_KIND_AB_18 = 619
    
    FREIBETRAG_ERWERBSTAETIGKEIT = 255  # Erwerbstätigenfreibetrag
    WOHNKOSTEN_GRENZE = 572  # Angemessene Unterkunftskosten
    
    # Ratenzahlung
    RATEN_GRENZEN = [
        (0, 20, 0),
        (21, 50, 0),  # Ratenfrei
        (51, 100, 15),
        (101, 150, 30),
        (151, 200, 45),
        (201, 250, 60),
        (251, 300, 75),
        (301, 350, 95),
        (351, 400, 115),
        (401, 450, 135),
        (451, 500, 155),
        (501, 550, 180),
        (551, 600, 205),
        (601, 650, 230),
        (651, 700, 260),
        (701, 750, 290),
        (751, 800, 320),
        (801, 850, 355),
        (851, 900, 390),
        (901, 950, 425),
        (951, 1000, 465),
    ]
    
    @dataclass
    class PKHErgebnis:
        anspruch: str  # "ja", "nein", "raten"
        einzusetzendes_einkommen: float
        freibetraege_gesamt: float
        monatliche_rate: float
        raten_anzahl: int
        begruendung: str
        details: Dict[str, float] = field(default_factory=dict)
    
    def berechne_pkh(
        self,
        bruttoeinkommen: float,
        nettoeinkommen: float,
        ehepartner_einkommen: float = 0,
        kinder: List[Tuple[int, float]] = None,  # [(Alter, eigenes Einkommen)]
        wohnkosten: float = 0,
        sonstige_ausgaben: float = 0,
        unterhaltspflichten: float = 0,
        vermoegen: float = 0,
        schulden: float = 0,
        ist_erwerbstaetig: bool = True
    ) -> 'PKHErgebnis':
        """
        Berechnet PKH-Anspruch.
        
        Args:
            bruttoeinkommen: Monatliches Bruttoeinkommen
            nettoeinkommen: Monatliches Nettoeinkommen
            ehepartner_einkommen: Einkommen des Ehepartners
            kinder: Liste von (Alter, eigenes Einkommen) pro Kind
            wohnkosten: Monatliche Miet-/Wohnkosten
            sonstige_ausgaben: Versicherungen, Fahrtkosten etc.
            unterhaltspflichten: Unterhaltszahlungen
            vermoegen: Vorhandenes Vermögen (über Schonvermögen)
            schulden: Bestehende Schulden/Verbindlichkeiten
            ist_erwerbstaetig: Ob erwerbstätig
            
        Returns:
            PKHErgebnis mit allen Details
        """
        kinder = kinder or []
        
        # 1. Freibeträge berechnen
        freibetraege = self.FREIBETRAG_ANTRAGSTELLER
        
        if ehepartner_einkommen > 0:
            freibetraege += self.FREIBETRAG_EHEPARTNER
        
        for alter, kind_einkommen in kinder:
            if alter <= 5:
                freibetraege += self.FREIBETRAG_KIND_BIS_5
            elif alter <= 13:
                freibetraege += self.FREIBETRAG_KIND_6_13
            elif alter <= 17:
                freibetraege += self.FREIBETRAG_KIND_14_17
            else:
                freibetraege += self.FREIBETRAG_KIND_AB_18
        
        # 2. Erwerbstätigenfreibetrag
        if ist_erwerbstaetig:
            freibetraege += self.FREIBETRAG_ERWERBSTAETIGKEIT
        
        # 3. Wohnkosten (max. angemessen)
        anrechenbare_wohnkosten = min(wohnkosten, self.WOHNKOSTEN_GRENZE)
        
        # 4. Einzusetzendes Einkommen berechnen
        gesamt_einkommen = nettoeinkommen + ehepartner_einkommen
        
        abzuege = (
            freibetraege +
            anrechenbare_wohnkosten +
            sonstige_ausgaben +
            unterhaltspflichten
        )
        
        einzusetzendes_einkommen = max(0, gesamt_einkommen - abzuege)
        
        # 5. PKH-Anspruch prüfen
        if einzusetzendes_einkommen <= 20:
            anspruch = "ja"
            rate = 0
            raten_anzahl = 0
            begruendung = "PKH wird ohne Ratenzahlung bewilligt."
        elif einzusetzendes_einkommen > 1000:
            anspruch = "nein"
            rate = 0
            raten_anzahl = 0
            begruendung = "Einkommen übersteigt die PKH-Grenze."
        else:
            anspruch = "raten"
            rate = self._berechne_rate(einzusetzendes_einkommen)
            raten_anzahl = 48  # Max. 48 Monatsraten
            begruendung = f"PKH wird mit Ratenzahlung von {rate:.2f} € bewilligt."
        
        # 6. Vermögensprüfung
        schonvermoegen = 5000  # Grundschonvermögen
        if vermoegen > schonvermoegen:
            anspruch = "pruefen"
            begruendung += f" Achtung: Vermögen ({vermoegen:.2f} €) übersteigt Schonvermögen."
        
        return self.PKHErgebnis(
            anspruch=anspruch,
            einzusetzendes_einkommen=einzusetzendes_einkommen,
            freibetraege_gesamt=freibetraege,
            monatliche_rate=rate,
            raten_anzahl=raten_anzahl,
            begruendung=begruendung,
            details={
                "nettoeinkommen": nettoeinkommen,
                "ehepartner_einkommen": ehepartner_einkommen,
                "freibetraege": freibetraege,
                "wohnkosten_angerechnet": anrechenbare_wohnkosten,
                "sonstige_ausgaben": sonstige_ausgaben,
                "unterhaltspflichten": unterhaltspflichten,
            }
        )
    
    def _berechne_rate(self, einzusetzendes_einkommen: float) -> float:
        """Berechnet die monatliche Rate."""
        for von, bis, rate in self.RATEN_GRENZEN:
            if von <= einzusetzendes_einkommen <= bis:
                return rate
        return 500  # Maximum bei sehr hohem Einkommen


# =============================================================================
# PROZESSKOSTENRECHNER (3 Instanzen: AG, LAG, BAG)
# =============================================================================

class Instanz(Enum):
    ARBEITSGERICHT = "Arbeitsgericht"
    LANDESARBEITSGERICHT = "LAG"
    BUNDESARBEITSGERICHT = "BAG"


@dataclass
class ProzessKostenDetail:
    """Details einer Prozesskostenberechnung"""
    streitwert: float
    instanz: str
    gerichtskosten: float
    anwaltskosten_eigen: float
    anwaltskosten_gegner: float
    gesamt_verlieren: float
    gesamt_gewinnen: float
    gesamt_vergleich: float
    details: Dict[str, float] = field(default_factory=dict)


class ProzesskostenRechner3Instanzen:
    """
    Prozesskostenrechner für alle 3 arbeitsgerichtlichen Instanzen
    nach RVG 2024 und GKG 2024.
    """
    
    # RVG 2024 Gebührentabelle (Anlage 2 zu § 13 Abs. 1 RVG)
    RVG_TABELLE = [
        (500, 49), (1000, 88), (1500, 127), (2000, 166),
        (3000, 222), (4000, 278), (5000, 334), (6000, 390),
        (7000, 446), (8000, 502), (9000, 558), (10000, 614),
        (13000, 698), (16000, 782), (19000, 866), (22000, 950),
        (25000, 1034), (30000, 1134), (35000, 1234), (40000, 1334),
        (45000, 1434), (50000, 1534), (65000, 1734), (80000, 1934),
        (95000, 2134), (110000, 2334), (125000, 2534), (140000, 2734),
        (155000, 2934), (170000, 3134), (185000, 3334), (200000, 3534),
    ]
    
    # GKG Tabelle für Arbeitsgerichte (Anlage 2 zu § 34 GKG)
    GKG_TABELLE = [
        (500, 38), (1000, 58), (1500, 78), (2000, 98),
        (3000, 119), (4000, 140), (5000, 161), (6000, 182),
        (7000, 203), (8000, 224), (9000, 245), (10000, 266),
        (13000, 308), (16000, 350), (19000, 392), (22000, 434),
        (25000, 476), (30000, 539), (35000, 602), (40000, 665),
        (45000, 728), (50000, 791), (65000, 948), (80000, 1105),
        (95000, 1262), (110000, 1419), (125000, 1576), (140000, 1733),
        (155000, 1890), (170000, 2047), (185000, 2204), (200000, 2361),
    ]
    
    # Gebührensätze pro Instanz
    GEBUEHRENSAETZE = {
        Instanz.ARBEITSGERICHT: {
            "verfahren": 1.3,
            "termin": 1.2,
            "einigung": 1.0,
            "gericht_urteil": 2.0,  # Bei streitigem Urteil
            "gericht_vergleich": 0.0,  # Kostenlos bei Vergleich
        },
        Instanz.LANDESARBEITSGERICHT: {
            "verfahren": 1.6,
            "termin": 1.2,
            "einigung": 1.5,
            "gericht_urteil": 4.0,
            "gericht_vergleich": 2.0,
        },
        Instanz.BUNDESARBEITSGERICHT: {
            "verfahren": 1.8,
            "termin": 1.5,
            "einigung": 1.5,
            "gericht_urteil": 5.0,
            "gericht_vergleich": 3.0,
        }
    }
    
    def _get_rvg_grundgebuehr(self, streitwert: float) -> float:
        """Ermittelt die RVG-Grundgebühr für einen Streitwert."""
        for grenze, gebuehr in self.RVG_TABELLE:
            if streitwert <= grenze:
                return gebuehr
        
        # Über 200.000 €: Pro 50.000 € weitere 200 €
        ueber = streitwert - 200000
        zusatz = (ueber // 50000 + 1) * 200
        return 3534 + zusatz
    
    def _get_gkg_grundgebuehr(self, streitwert: float) -> float:
        """Ermittelt die GKG-Grundgebühr für einen Streitwert."""
        for grenze, gebuehr in self.GKG_TABELLE:
            if streitwert <= grenze:
                return gebuehr
        
        # Über 200.000 €
        ueber = streitwert - 200000
        zusatz = (ueber // 50000 + 1) * 157
        return 2361 + zusatz
    
    def berechne_instanz(
        self, 
        streitwert: float, 
        instanz: Instanz,
        mit_vergleich: bool = False,
        mehrere_auftraggeber: int = 1
    ) -> ProzessKostenDetail:
        """
        Berechnet Prozesskosten für eine Instanz.
        
        Args:
            streitwert: Streitwert in Euro
            instanz: Welche Instanz
            mit_vergleich: Ob Vergleich angenommen wird
            mehrere_auftraggeber: Anzahl Auftraggeber (für Erhöhung)
        """
        saetze = self.GEBUEHRENSAETZE[instanz]
        rvg_grund = self._get_rvg_grundgebuehr(streitwert)
        gkg_grund = self._get_gkg_grundgebuehr(streitwert)
        
        # Anwaltskosten
        verfahren = rvg_grund * saetze["verfahren"]
        termin = rvg_grund * saetze["termin"]
        einigung = rvg_grund * saetze["einigung"] if mit_vergleich else 0
        
        # Erhöhung bei mehreren Auftraggebern (30% pro Person)
        if mehrere_auftraggeber > 1:
            erhoehung = 0.3 * (mehrere_auftraggeber - 1)
            verfahren *= (1 + erhoehung)
        
        # Pauschale für Post/Telekommunikation
        pauschale = min((verfahren + termin + einigung) * 0.2, 20)
        
        anwalt_netto = verfahren + termin + einigung + pauschale
        anwalt_brutto = anwalt_netto * 1.19
        
        # Gerichtskosten
        if mit_vergleich:
            gericht = gkg_grund * saetze["gericht_vergleich"]
        else:
            gericht = gkg_grund * saetze["gericht_urteil"]
        
        # Sonderregel AG: Bei Gütetermin keine Gerichtskosten
        if instanz == Instanz.ARBEITSGERICHT and mit_vergleich:
            gericht = 0
        
        return ProzessKostenDetail(
            streitwert=streitwert,
            instanz=instanz.value,
            gerichtskosten=gericht,
            anwaltskosten_eigen=anwalt_brutto,
            anwaltskosten_gegner=anwalt_brutto,
            gesamt_verlieren=gericht + anwalt_brutto * 2,  # Beide Anwälte
            gesamt_gewinnen=anwalt_brutto,  # Nur eigener Anwalt
            gesamt_vergleich=anwalt_brutto + (gericht if gericht > 0 else 0),
            details={
                "rvg_grundgebuehr": rvg_grund,
                "gkg_grundgebuehr": gkg_grund,
                "verfahrensgebuehr": verfahren,
                "terminsgebuehr": termin,
                "einigungsgebuehr": einigung,
                "pauschale": pauschale,
                "netto": anwalt_netto,
                "mwst": anwalt_brutto - anwalt_netto,
            }
        )
    
    def berechne_alle_instanzen(
        self, 
        streitwert: float,
        gewinnchance: float = 0.5  # 50% Gewinnchance
    ) -> Dict[str, any]:
        """
        Berechnet Kosten für alle 3 Instanzen und Risiko.
        
        Returns:
            Dict mit Kosten pro Instanz und Risikoanalyse
        """
        ag = self.berechne_instanz(streitwert, Instanz.ARBEITSGERICHT)
        lag = self.berechne_instanz(streitwert, Instanz.LANDESARBEITSGERICHT)
        bag = self.berechne_instanz(streitwert, Instanz.BUNDESARBEITSGERICHT)
        
        ag_vergleich = self.berechne_instanz(streitwert, Instanz.ARBEITSGERICHT, mit_vergleich=True)
        
        # Risikoberechnung
        risiko_verlieren_1 = ag.gesamt_verlieren
        risiko_verlieren_2 = ag.gesamt_verlieren + lag.gesamt_verlieren
        risiko_verlieren_3 = ag.gesamt_verlieren + lag.gesamt_verlieren + bag.gesamt_verlieren
        
        erwartungswert = (
            gewinnchance * ag.gesamt_gewinnen +
            (1 - gewinnchance) * ag.gesamt_verlieren
        )
        
        return {
            "streitwert": streitwert,
            "1_instanz": {
                "name": "Arbeitsgericht",
                "streitig": ag,
                "vergleich": ag_vergleich,
            },
            "2_instanz": {
                "name": "Landesarbeitsgericht",
                "streitig": lag,
                "kumuliert_verlieren": risiko_verlieren_2,
            },
            "3_instanz": {
                "name": "Bundesarbeitsgericht",
                "streitig": bag,
                "kumuliert_verlieren": risiko_verlieren_3,
            },
            "empfehlung": {
                "vergleich_ersparnis": ag.gesamt_verlieren - ag_vergleich.gesamt_vergleich,
                "erwartungswert_klage": erwartungswert,
                "empfehlung": "vergleich" if ag_vergleich.gesamt_vergleich < erwartungswert else "klage"
            }
        }


# =============================================================================
# ZEITERFASSUNG MIT STOPPUHR
# =============================================================================

@dataclass
class Zeiteintrag:
    """Ein einzelner Zeiteintrag"""
    id: int = 0
    akte_id: str = ""
    akte_name: str = ""
    start_zeit: datetime = None
    end_zeit: datetime = None
    dauer_minuten: int = 0
    taetigkeit: str = ""
    kategorie: str = ""
    stundensatz: float = 250.0
    abrechenbar: bool = True
    notizen: str = ""
    erstellt_von: str = ""


class Zeiterfassung:
    """
    Zeiterfassung für Anwälte mit Stoppuhr-Funktion.
    """
    
    KATEGORIEN = [
        "Beratung",
        "Schriftsatz",
        "Recherche",
        "Aktenstudium",
        "Telefonat",
        "E-Mail",
        "Termin/Verhandlung",
        "Reisezeit",
        "Sonstiges"
    ]
    
    def __init__(self):
        self.eintraege: List[Zeiteintrag] = []
        self.aktive_timer: Dict[str, datetime] = {}  # akte_id -> startzeit
        self.naechste_id = 1
    
    def starte_timer(self, akte_id: str, akte_name: str, taetigkeit: str = "", 
                     kategorie: str = "Sonstiges") -> Zeiteintrag:
        """Startet einen Timer für eine Akte."""
        if akte_id in self.aktive_timer:
            raise ValueError(f"Timer für Akte {akte_id} läuft bereits")
        
        jetzt = datetime.now()
        self.aktive_timer[akte_id] = jetzt
        
        eintrag = Zeiteintrag(
            id=self.naechste_id,
            akte_id=akte_id,
            akte_name=akte_name,
            start_zeit=jetzt,
            taetigkeit=taetigkeit,
            kategorie=kategorie
        )
        self.naechste_id += 1
        return eintrag
    
    def stoppe_timer(self, akte_id: str, notizen: str = "") -> Optional[Zeiteintrag]:
        """Stoppt einen laufenden Timer."""
        if akte_id not in self.aktive_timer:
            return None
        
        start = self.aktive_timer.pop(akte_id)
        jetzt = datetime.now()
        dauer = (jetzt - start).seconds // 60
        
        # Letzten Eintrag finden und aktualisieren
        for eintrag in reversed(self.eintraege):
            if eintrag.akte_id == akte_id and eintrag.end_zeit is None:
                eintrag.end_zeit = jetzt
                eintrag.dauer_minuten = dauer
                eintrag.notizen = notizen
                return eintrag
        
        # Neuen Eintrag erstellen
        eintrag = Zeiteintrag(
            id=self.naechste_id,
            akte_id=akte_id,
            start_zeit=start,
            end_zeit=jetzt,
            dauer_minuten=dauer,
            notizen=notizen
        )
        self.eintraege.append(eintrag)
        self.naechste_id += 1
        return eintrag
    
    def manueller_eintrag(
        self, 
        akte_id: str,
        akte_name: str,
        datum: date,
        dauer_minuten: int,
        taetigkeit: str,
        kategorie: str = "Sonstiges",
        stundensatz: float = 250.0,
        notizen: str = ""
    ) -> Zeiteintrag:
        """Erstellt einen manuellen Zeiteintrag."""
        eintrag = Zeiteintrag(
            id=self.naechste_id,
            akte_id=akte_id,
            akte_name=akte_name,
            start_zeit=datetime.combine(datum, datetime.min.time()),
            dauer_minuten=dauer_minuten,
            taetigkeit=taetigkeit,
            kategorie=kategorie,
            stundensatz=stundensatz,
            notizen=notizen
        )
        self.eintraege.append(eintrag)
        self.naechste_id += 1
        return eintrag
    
    def berechne_wert(self, eintrag: Zeiteintrag) -> float:
        """Berechnet den Wert eines Zeiteintrags."""
        if not eintrag.abrechenbar:
            return 0
        stunden = eintrag.dauer_minuten / 60
        return stunden * eintrag.stundensatz
    
    def statistik_akte(self, akte_id: str) -> Dict:
        """Statistik für eine Akte."""
        eintraege = [e for e in self.eintraege if e.akte_id == akte_id]
        
        gesamt_minuten = sum(e.dauer_minuten for e in eintraege)
        abrechenbar_minuten = sum(e.dauer_minuten for e in eintraege if e.abrechenbar)
        gesamt_wert = sum(self.berechne_wert(e) for e in eintraege)
        
        nach_kategorie = {}
        for e in eintraege:
            if e.kategorie not in nach_kategorie:
                nach_kategorie[e.kategorie] = 0
            nach_kategorie[e.kategorie] += e.dauer_minuten
        
        return {
            "akte_id": akte_id,
            "anzahl_eintraege": len(eintraege),
            "gesamt_minuten": gesamt_minuten,
            "gesamt_stunden": gesamt_minuten / 60,
            "abrechenbar_minuten": abrechenbar_minuten,
            "gesamt_wert": gesamt_wert,
            "nach_kategorie": nach_kategorie
        }
    
    def statistik_zeitraum(self, von: date, bis: date) -> Dict:
        """Statistik für einen Zeitraum."""
        eintraege = [
            e for e in self.eintraege 
            if e.start_zeit and von <= e.start_zeit.date() <= bis
        ]
        
        gesamt_minuten = sum(e.dauer_minuten for e in eintraege)
        gesamt_wert = sum(self.berechne_wert(e) for e in eintraege)
        
        nach_akte = {}
        for e in eintraege:
            if e.akte_id not in nach_akte:
                nach_akte[e.akte_id] = {"name": e.akte_name, "minuten": 0, "wert": 0}
            nach_akte[e.akte_id]["minuten"] += e.dauer_minuten
            nach_akte[e.akte_id]["wert"] += self.berechne_wert(e)
        
        return {
            "von": von.isoformat(),
            "bis": bis.isoformat(),
            "anzahl_eintraege": len(eintraege),
            "gesamt_minuten": gesamt_minuten,
            "gesamt_stunden": gesamt_minuten / 60,
            "gesamt_wert": gesamt_wert,
            "nach_akte": nach_akte
        }


# =============================================================================
# FRISTEN-TRACKER
# =============================================================================

class FristTyp(Enum):
    GESETZLICH = "gesetzlich"
    GERICHTLICH = "gerichtlich"
    VERTRAGLICH = "vertraglich"
    INTERN = "intern"


class FristStatus(Enum):
    OFFEN = "offen"
    ERLEDIGT = "erledigt"
    UEBERFAELLIG = "überfällig"
    KRITISCH = "kritisch"  # < 7 Tage


@dataclass
class Frist:
    """Eine Frist"""
    id: int = 0
    akte_id: str = ""
    akte_name: str = ""
    titel: str = ""
    beschreibung: str = ""
    typ: FristTyp = FristTyp.INTERN
    datum: date = None
    vorfrist_tage: int = 7
    vorfrist_datum: date = None
    status: FristStatus = FristStatus.OFFEN
    erledigt_am: date = None
    erledigt_von: str = ""
    notizen: str = ""
    erinnerung_gesendet: bool = False


class FristenTracker:
    """Verwaltet Fristen mit Warnungen und Erinnerungen."""
    
    # Standard-Fristen im Arbeitsrecht
    STANDARD_FRISTEN = {
        "kuendigungsschutzklage": {
            "titel": "Kündigungsschutzklage (§ 4 KSchG)",
            "tage": 21,
            "typ": FristTyp.GESETZLICH,
            "beschreibung": "Frist zur Erhebung der Kündigungsschutzklage"
        },
        "berufung": {
            "titel": "Berufungsfrist",
            "tage": 30,
            "typ": FristTyp.GESETZLICH,
            "beschreibung": "Frist zur Einlegung der Berufung"
        },
        "berufungsbegruendung": {
            "titel": "Berufungsbegründung",
            "tage": 60,
            "typ": FristTyp.GESETZLICH,
            "beschreibung": "Frist zur Begründung der Berufung"
        },
        "revision": {
            "titel": "Revisionsfrist",
            "tage": 30,
            "typ": FristTyp.GESETZLICH,
            "beschreibung": "Frist zur Einlegung der Revision"
        },
        "klageerwiderung": {
            "titel": "Klageerwiderung",
            "tage": 14,
            "typ": FristTyp.GERICHTLICH,
            "beschreibung": "Frist zur Klageerwiderung (gerichtlich gesetzt)"
        },
    }
    
    def __init__(self):
        self.fristen: List[Frist] = []
        self.naechste_id = 1
    
    def erstelle_frist(
        self,
        akte_id: str,
        akte_name: str,
        titel: str,
        datum: date,
        typ: FristTyp = FristTyp.INTERN,
        beschreibung: str = "",
        vorfrist_tage: int = 7
    ) -> Frist:
        """Erstellt eine neue Frist."""
        frist = Frist(
            id=self.naechste_id,
            akte_id=akte_id,
            akte_name=akte_name,
            titel=titel,
            datum=datum,
            typ=typ,
            beschreibung=beschreibung,
            vorfrist_tage=vorfrist_tage,
            vorfrist_datum=datum - timedelta(days=vorfrist_tage)
        )
        self.fristen.append(frist)
        self.naechste_id += 1
        return frist
    
    def erstelle_standardfrist(
        self,
        akte_id: str,
        akte_name: str,
        frist_typ: str,
        bezugsdatum: date
    ) -> Optional[Frist]:
        """Erstellt eine Standard-Frist basierend auf einem Bezugsdatum."""
        if frist_typ not in self.STANDARD_FRISTEN:
            return None
        
        standard = self.STANDARD_FRISTEN[frist_typ]
        datum = bezugsdatum + timedelta(days=standard["tage"])
        
        return self.erstelle_frist(
            akte_id=akte_id,
            akte_name=akte_name,
            titel=standard["titel"],
            datum=datum,
            typ=standard["typ"],
            beschreibung=standard["beschreibung"]
        )
    
    def aktualisiere_status(self) -> None:
        """Aktualisiert den Status aller Fristen."""
        heute = date.today()
        
        for frist in self.fristen:
            if frist.status == FristStatus.ERLEDIGT:
                continue
            
            if frist.datum < heute:
                frist.status = FristStatus.UEBERFAELLIG
            elif (frist.datum - heute).days <= 7:
                frist.status = FristStatus.KRITISCH
            else:
                frist.status = FristStatus.OFFEN
    
    def erledige_frist(self, frist_id: int, erledigt_von: str = "") -> Optional[Frist]:
        """Markiert eine Frist als erledigt."""
        for frist in self.fristen:
            if frist.id == frist_id:
                frist.status = FristStatus.ERLEDIGT
                frist.erledigt_am = date.today()
                frist.erledigt_von = erledigt_von
                return frist
        return None
    
    def get_kritische_fristen(self) -> List[Frist]:
        """Gibt alle kritischen und überfälligen Fristen zurück."""
        self.aktualisiere_status()
        return [
            f for f in self.fristen 
            if f.status in [FristStatus.KRITISCH, FristStatus.UEBERFAELLIG]
        ]
    
    def get_fristen_akte(self, akte_id: str) -> List[Frist]:
        """Gibt alle Fristen einer Akte zurück."""
        return [f for f in self.fristen if f.akte_id == akte_id]
    
    def get_fristen_zeitraum(self, von: date, bis: date) -> List[Frist]:
        """Gibt alle Fristen in einem Zeitraum zurück."""
        return [f for f in self.fristen if von <= f.datum <= bis]
    
    def statistik(self) -> Dict:
        """Gibt Fristenstatistik zurück."""
        self.aktualisiere_status()
        
        return {
            "gesamt": len(self.fristen),
            "offen": len([f for f in self.fristen if f.status == FristStatus.OFFEN]),
            "kritisch": len([f for f in self.fristen if f.status == FristStatus.KRITISCH]),
            "ueberfaellig": len([f for f in self.fristen if f.status == FristStatus.UEBERFAELLIG]),
            "erledigt": len([f for f in self.fristen if f.status == FristStatus.ERLEDIGT]),
            "nach_typ": {
                t.value: len([f for f in self.fristen if f.typ == t])
                for t in FristTyp
            }
        }
