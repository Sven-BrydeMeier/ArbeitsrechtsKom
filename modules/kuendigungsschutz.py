"""
JuraConnect - Kündigungsschutz Schnellcheck
"""

from datetime import date, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from enum import Enum


class Kuendigungsart(Enum):
    ORDENTLICH = "ordentlich"
    AUSSERORDENTLICH = "außerordentlich"
    AENDERUNGSKUENDIGUNG = "änderungskündigung"


class Schutzstatus(Enum):
    KEIN_SCHUTZ = "kein_schutz"
    ALLGEMEINER_SCHUTZ = "allgemeiner_schutz"
    BESONDERER_SCHUTZ = "besonderer_schutz"
    ABSOLUTER_SCHUTZ = "absoluter_schutz"


@dataclass
class BesondererSchutz:
    art: str
    gesetz: str
    beschreibung: str
    zustimmung_erforderlich: bool = False
    zustimmung_stelle: str = ""
    kuendigung_moeglich: bool = True


@dataclass
class Formfehler:
    fehler: str
    schwere: str
    rechtsfolge: str
    heilbar: bool


@dataclass
class KuendigungsschutzErgebnis:
    kschg_anwendbar: bool
    schutzstatus: Schutzstatus
    wartezeit_erfuellt: bool
    betriebsgroesse_ok: bool
    besondere_schutzrechte: List[BesondererSchutz] = field(default_factory=list)
    formfehler: List[Formfehler] = field(default_factory=list)
    erfolgsaussichten: str = ""
    erfolgsaussichten_prozent: int = 0
    klagefrist_bis: Optional[date] = None
    klagefrist_tage_verbleibend: int = 0
    empfehlungen: List[str] = field(default_factory=list)
    naechste_schritte: List[str] = field(default_factory=list)
    warnungen: List[str] = field(default_factory=list)
    zusammenfassung: str = ""


@dataclass
class MandantDaten:
    alter: int
    geschlecht: str
    eintrittsdatum: date
    bruttogehalt: float
    wochenstunden: float
    kuendigung_zugang: date
    kuendigung_art: Kuendigungsart
    kuendigung_schriftlich: bool
    kuendigung_begruendung: str = ""
    mitarbeiter_anzahl: int = 0
    betriebsrat_vorhanden: bool = False
    betriebsrat_angehoert: bool = False
    schwerbehindert: bool = False
    schwerbehindert_grad: int = 0
    gleichgestellt: bool = False
    schwanger: bool = False
    elternzeit: bool = False
    elternzeit_beantragt: bool = False
    betriebsratsmitglied: bool = False
    datenschutzbeauftragter: bool = False
    azubi: bool = False
    befristet: bool = False
    probezeit: bool = False
    abmahnung_erhalten: bool = False
    anzahl_abmahnungen: int = 0
    kuendigungsgrund_genannt: str = ""


class KuendigungsschutzPruefer:
    """Prüft Kündigungsschutz und bewertet Erfolgsaussichten"""
    
    def pruefe(self, daten: MandantDaten) -> KuendigungsschutzErgebnis:
        ergebnis = KuendigungsschutzErgebnis(
            kschg_anwendbar=False, schutzstatus=Schutzstatus.KEIN_SCHUTZ,
            wartezeit_erfuellt=False, betriebsgroesse_ok=False
        )
        
        self._pruefe_kschg(daten, ergebnis)
        self._pruefe_besonderen_schutz(daten, ergebnis)
        self._pruefe_formfehler(daten, ergebnis)
        self._berechne_fristen(daten, ergebnis)
        self._bewerte_erfolgsaussichten(daten, ergebnis)
        self._generiere_empfehlungen(daten, ergebnis)
        
        return ergebnis
    
    def _pruefe_kschg(self, daten: MandantDaten, ergebnis: KuendigungsschutzErgebnis):
        beschaeftigt_tage = (daten.kuendigung_zugang - daten.eintrittsdatum).days
        ergebnis.wartezeit_erfuellt = beschaeftigt_tage >= 183
        ergebnis.betriebsgroesse_ok = daten.mitarbeiter_anzahl > 10
        ergebnis.kschg_anwendbar = ergebnis.wartezeit_erfuellt and ergebnis.betriebsgroesse_ok
        
        if ergebnis.kschg_anwendbar:
            ergebnis.schutzstatus = Schutzstatus.ALLGEMEINER_SCHUTZ
            ergebnis.empfehlungen.append("✅ KSchG anwendbar - Kündigung muss sozial gerechtfertigt sein")
        else:
            gründe = []
            if not ergebnis.wartezeit_erfuellt:
                gründe.append(f"Wartezeit nicht erfüllt ({beschaeftigt_tage} Tage < 6 Monate)")
            if not ergebnis.betriebsgroesse_ok:
                gründe.append(f"Kleinbetrieb ({daten.mitarbeiter_anzahl} ≤ 10 Mitarbeiter)")
            ergebnis.warnungen.append(f"⚠️ KSchG nicht anwendbar: {', '.join(gründe)}")
    
    def _pruefe_besonderen_schutz(self, daten: MandantDaten, ergebnis: KuendigungsschutzErgebnis):
        if daten.schwanger:
            ergebnis.besondere_schutzrechte.append(BesondererSchutz(
                art="Mutterschutz", gesetz="§ 17 MuSchG",
                beschreibung="Kündigungsverbot während Schwangerschaft",
                zustimmung_erforderlich=True,
                zustimmung_stelle="Gewerbeaufsichtsamt",
                kuendigung_moeglich=False
            ))
            ergebnis.schutzstatus = Schutzstatus.ABSOLUTER_SCHUTZ
            ergebnis.warnungen.append("🛡️ ABSOLUTER KÜNDIGUNGSSCHUTZ durch Schwangerschaft!")
        
        if daten.elternzeit or daten.elternzeit_beantragt:
            ergebnis.besondere_schutzrechte.append(BesondererSchutz(
                art="Elternzeit", gesetz="§ 18 BEEG",
                beschreibung="Kündigungsschutz während Elternzeit",
                zustimmung_erforderlich=True,
                zustimmung_stelle="Gewerbeaufsichtsamt",
                kuendigung_moeglich=False
            ))
            ergebnis.schutzstatus = Schutzstatus.ABSOLUTER_SCHUTZ
        
        if daten.schwerbehindert or daten.gleichgestellt:
            ergebnis.besondere_schutzrechte.append(BesondererSchutz(
                art="Schwerbehinderung", gesetz="§ 168 SGB IX",
                beschreibung=f"GdB {daten.schwerbehindert_grad}%",
                zustimmung_erforderlich=True,
                zustimmung_stelle="Integrationsamt"
            ))
            if ergebnis.schutzstatus != Schutzstatus.ABSOLUTER_SCHUTZ:
                ergebnis.schutzstatus = Schutzstatus.BESONDERER_SCHUTZ
            ergebnis.empfehlungen.append("♿ Prüfen: Zustimmung des Integrationsamts eingeholt?")
        
        if daten.betriebsratsmitglied:
            ergebnis.besondere_schutzrechte.append(BesondererSchutz(
                art="Betriebsratsmitglied", gesetz="§ 15 KSchG",
                beschreibung="Ordentliche Kündigung ausgeschlossen",
                zustimmung_erforderlich=True,
                zustimmung_stelle="Betriebsrat/Arbeitsgericht"
            ))
            if ergebnis.schutzstatus != Schutzstatus.ABSOLUTER_SCHUTZ:
                ergebnis.schutzstatus = Schutzstatus.BESONDERER_SCHUTZ
    
    def _pruefe_formfehler(self, daten: MandantDaten, ergebnis: KuendigungsschutzErgebnis):
        if not daten.kuendigung_schriftlich:
            ergebnis.formfehler.append(Formfehler(
                fehler="Schriftform nicht eingehalten",
                schwere="schwer",
                rechtsfolge="Kündigung ist NICHTIG (§ 125 BGB)",
                heilbar=False
            ))
            ergebnis.warnungen.append("🚨 SCHWERER FORMFEHLER: Kündigung nichtig!")
        
        if daten.betriebsrat_vorhanden and not daten.betriebsrat_angehoert:
            ergebnis.formfehler.append(Formfehler(
                fehler="Betriebsrat nicht angehört",
                schwere="schwer",
                rechtsfolge="Kündigung ist UNWIRKSAM (§ 102 BetrVG)",
                heilbar=False
            ))
            ergebnis.warnungen.append("🚨 Betriebsrat nicht angehört - Kündigung unwirksam!")
    
    def _berechne_fristen(self, daten: MandantDaten, ergebnis: KuendigungsschutzErgebnis):
        klagefrist = daten.kuendigung_zugang + timedelta(days=21)
        if klagefrist.weekday() == 5:
            klagefrist += timedelta(days=2)
        elif klagefrist.weekday() == 6:
            klagefrist += timedelta(days=1)
        
        ergebnis.klagefrist_bis = klagefrist
        ergebnis.klagefrist_tage_verbleibend = (klagefrist - date.today()).days
        
        if ergebnis.klagefrist_tage_verbleibend < 0:
            ergebnis.warnungen.append("🚨 KLAGEFRIST ABGELAUFEN!")
        elif ergebnis.klagefrist_tage_verbleibend <= 3:
            ergebnis.warnungen.append(f"🚨 NUR NOCH {ergebnis.klagefrist_tage_verbleibend} TAGE!")
        elif ergebnis.klagefrist_tage_verbleibend <= 7:
            ergebnis.warnungen.append(f"⚠️ DRINGEND! Noch {ergebnis.klagefrist_tage_verbleibend} Tage")
    
    def _bewerte_erfolgsaussichten(self, daten: MandantDaten, ergebnis: KuendigungsschutzErgebnis):
        punkte = 50
        
        if ergebnis.kschg_anwendbar:
            punkte += 20
        if ergebnis.schutzstatus == Schutzstatus.ABSOLUTER_SCHUTZ:
            punkte += 40
        elif ergebnis.schutzstatus == Schutzstatus.BESONDERER_SCHUTZ:
            punkte += 25
        
        for fehler in ergebnis.formfehler:
            if fehler.schwere == "schwer":
                punkte += 30
            else:
                punkte += 15
        
        zugehoerigkeit = (daten.kuendigung_zugang - daten.eintrittsdatum).days / 365
        if zugehoerigkeit > 10:
            punkte += 10
        elif zugehoerigkeit > 5:
            punkte += 5
        
        if daten.alter >= 55:
            punkte += 10
        elif daten.alter >= 50:
            punkte += 5
        
        punkte = max(0, min(100, punkte))
        ergebnis.erfolgsaussichten_prozent = punkte
        
        if punkte >= 80:
            ergebnis.erfolgsaussichten = "sehr_gut"
        elif punkte >= 60:
            ergebnis.erfolgsaussichten = "gut"
        elif punkte >= 40:
            ergebnis.erfolgsaussichten = "mittel"
        else:
            ergebnis.erfolgsaussichten = "gering"
    
    def _generiere_empfehlungen(self, daten: MandantDaten, ergebnis: KuendigungsschutzErgebnis):
        if ergebnis.klagefrist_tage_verbleibend > 0:
            ergebnis.naechste_schritte.append(
                f"1️⃣ Kündigungsschutzklage bis {ergebnis.klagefrist_bis.strftime('%d.%m.%Y')} einreichen!"
            )
        ergebnis.naechste_schritte.append("2️⃣ Unterlagen sammeln: Arbeitsvertrag, Kündigung, Lohnabrechnungen")
        ergebnis.naechste_schritte.append("3️⃣ Rechtsschutzversicherung prüfen, Deckungszusage einholen")
        ergebnis.naechste_schritte.append("4️⃣ Arbeitssuchendmeldung bei Agentur für Arbeit (3-Tages-Frist!)")


def kuendigungsschutz_check(daten: MandantDaten) -> KuendigungsschutzErgebnis:
    return KuendigungsschutzPruefer().pruefe(daten)
