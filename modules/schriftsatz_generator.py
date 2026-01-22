"""
JuraConnect - KI-Schriftsatz-Generator
=======================================
Automatische Erstellung von arbeitsrechtlichen Schriftsätzen:
- Kündigungsschutzklage
- Lohnklage
- Urlaubsklage / Urlaubsabgeltungsklage
- Zeugnisklage
- Weiterbeschäftigungsantrag
- Abmahnungs-Gegendarstellung
- Aufhebungsvertrag (Entwurf)

Die Schriftsätze werden aus Aktendaten generiert und können 
manuell angepasst werden.

Version: 2.0.0
"""

from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple
from enum import Enum
import re


class SchriftsatzTyp(Enum):
    KUENDIGUNGSSCHUTZKLAGE = "kuendigungsschutzklage"
    LOHNKLAGE = "lohnklage"
    URLAUBSKLAGE = "urlaubsklage"
    URLAUBSABGELTUNG = "urlaubsabgeltung"
    ZEUGNISKLAGE = "zeugnisklage"
    WEITERBESCHAEFTIGUNG = "weiterbeschaeftigung"
    ABMAHNUNG_GEGENDARSTELLUNG = "abmahnung_gegendarstellung"
    AUFHEBUNGSVERTRAG = "aufhebungsvertrag"
    KLAGEERWIDERUNG = "klageerwiderung"
    VERGLEICHSVORSCHLAG = "vergleichsvorschlag"


@dataclass
class Parteidaten:
    """Daten einer Partei (Kläger/Beklagter)"""
    name: str = ""
    strasse: str = ""
    plz: str = ""
    ort: str = ""
    
    @property
    def adresse(self) -> str:
        return f"{self.strasse}, {self.plz} {self.ort}"
    
    @property
    def adresse_block(self) -> str:
        return f"{self.name}\n{self.strasse}\n{self.plz} {self.ort}"


@dataclass
class Arbeitsverhältnis:
    """Daten zum Arbeitsverhältnis"""
    eintrittsdatum: date = None
    position: str = ""
    bruttogehalt: float = 0.0
    wochenstunden: float = 40.0
    urlaubstage_jahr: int = 30
    tarifvertrag: str = ""
    befristet: bool = False
    befristung_bis: date = None


@dataclass
class Kuendigungsdaten:
    """Daten zur Kündigung"""
    kuendigung_datum: date = None
    zugang_datum: date = None
    kuendigungsart: str = "ordentlich"  # ordentlich, außerordentlich, Änderung
    kuendigungsgrund: str = ""
    kuendigung_zum: date = None
    betriebsrat_angehoert: bool = False
    abmahnung_vorhanden: bool = False
    schriftform_eingehalten: bool = True


@dataclass
class Lohndaten:
    """Daten für Lohnklage"""
    offene_monate: List[str] = field(default_factory=list)
    offener_betrag_brutto: float = 0.0
    offene_ueberstunden: float = 0.0
    ueberstunden_stundenlohn: float = 0.0


@dataclass
class Urlaubsdaten:
    """Daten für Urlaubsklage"""
    urlaubsjahr: int = 0
    gesamtanspruch_tage: int = 30
    genommen_tage: int = 0
    offene_tage: int = 0
    bereits_abgegolten: bool = False


@dataclass
class Zeugnisdaten:
    """Daten für Zeugnisklage"""
    zeugnis_erhalten: bool = False
    zeugnis_art: str = "qualifiziert"  # einfach, qualifiziert
    maengel: List[str] = field(default_factory=list)
    gewuenschte_note: str = "gut"


@dataclass
class Akteninhalt:
    """Gesamtdaten einer Akte für Schriftsatzerstellung"""
    aktenzeichen: str = ""
    mandant: Parteidaten = None
    gegner: Parteidaten = None
    gericht: str = ""
    gericht_adresse: str = ""
    arbeitsverhaeltnis: Arbeitsverhältnis = None
    kuendigung: Kuendigungsdaten = None
    lohn: Lohndaten = None
    urlaub: Urlaubsdaten = None
    zeugnis: Zeugnisdaten = None
    sachverhalt_zusatz: str = ""
    
    def __post_init__(self):
        if self.mandant is None:
            self.mandant = Parteidaten()
        if self.gegner is None:
            self.gegner = Parteidaten()
        if self.arbeitsverhaeltnis is None:
            self.arbeitsverhaeltnis = Arbeitsverhältnis()
        if self.kuendigung is None:
            self.kuendigung = Kuendigungsdaten()
        if self.lohn is None:
            self.lohn = Lohndaten()
        if self.urlaub is None:
            self.urlaub = Urlaubsdaten()
        if self.zeugnis is None:
            self.zeugnis = Zeugnisdaten()


@dataclass
class GenerierterSchriftsatz:
    """Ein generierter Schriftsatz"""
    typ: SchriftsatzTyp
    titel: str
    inhalt_html: str
    inhalt_text: str
    streitwert: float = 0.0
    generiert_am: datetime = None
    aktenzeichen: str = ""
    hinweise: List[str] = field(default_factory=list)


class KISchriftsatzGenerator:
    """
    KI-gestützter Generator für arbeitsrechtliche Schriftsätze.
    
    Generiert vollständige, anpassbare Schriftsätze basierend auf
    den Daten aus der Mandantenakte.
    """
    
    def __init__(self):
        self.heute = date.today()
    
    # =========================================================================
    # KÜNDIGUNGSSCHUTZKLAGE
    # =========================================================================
    
    def generiere_kuendigungsschutzklage(self, akte: Akteninhalt) -> GenerierterSchriftsatz:
        """Generiert eine vollständige Kündigungsschutzklage."""
        
        # Streitwert berechnen (3 Bruttomonatsgehälter, § 42 Abs. 2 GKG)
        streitwert = akte.arbeitsverhaeltnis.bruttogehalt * 3
        
        # Fristen prüfen
        hinweise = []
        if akte.kuendigung.zugang_datum:
            klagefrist = akte.kuendigung.zugang_datum + timedelta(days=21)
            tage_bis_frist = (klagefrist - self.heute).days
            if tage_bis_frist < 0:
                hinweise.append(f"⚠️ ACHTUNG: Klagefrist am {klagefrist.strftime('%d.%m.%Y')} bereits abgelaufen!")
            elif tage_bis_frist <= 7:
                hinweise.append(f"⚠️ DRINGEND: Nur noch {tage_bis_frist} Tage bis Klagefrist ({klagefrist.strftime('%d.%m.%Y')})!")
        
        # Betriebszugehörigkeit berechnen
        if akte.arbeitsverhaeltnis.eintrittsdatum:
            zugehoerigkeit = (self.heute - akte.arbeitsverhaeltnis.eintrittsdatum).days // 365
            zugehoerigkeit_monate = (self.heute - akte.arbeitsverhaeltnis.eintrittsdatum).days // 30
        else:
            zugehoerigkeit = 0
            zugehoerigkeit_monate = 0
        
        # Kündigungsgründe analysieren
        unwirksamkeitsgruende = self._analysiere_unwirksamkeitsgruende(akte)
        
        # Schriftsatz generieren
        inhalt = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.5; margin: 2cm; }}
        h1 {{ text-align: center; font-size: 14pt; }}
        .header {{ margin-bottom: 2cm; }}
        .absender {{ margin-bottom: 1cm; }}
        .empfaenger {{ margin-bottom: 1cm; }}
        .datum {{ text-align: right; margin-bottom: 1cm; }}
        .betreff {{ font-weight: bold; margin: 1cm 0; }}
        .rubrum {{ margin: 1cm 0; }}
        .antrag {{ margin: 1cm 0; padding-left: 1cm; }}
        .begruendung {{ margin-top: 1cm; }}
        .unterschrift {{ margin-top: 2cm; }}
        p {{ text-align: justify; }}
    </style>
</head>
<body>

<div class="header">
    <div class="absender">
        <strong>Rechtsanwalt/Rechtsanwältin</strong><br>
        [Kanzleiname]<br>
        [Straße]<br>
        [PLZ Ort]<br>
        Tel.: [Telefon] | Fax: [Fax]<br>
        E-Mail: [E-Mail] | beA: [SAFE-ID]
    </div>
    
    <div class="empfaenger">
        <strong>An das</strong><br>
        <strong>Arbeitsgericht {akte.gericht or '[Ort]'}</strong><br>
        {akte.gericht_adresse or '[Adresse des Arbeitsgerichts]'}
    </div>
    
    <div class="datum">
        {self.heute.strftime('%d.%m.%Y')}
    </div>
</div>

<h1>Kündigungsschutzklage</h1>

<div class="rubrum">
    <p>
        <strong>{akte.mandant.name or '[Name des Mandanten]'}</strong><br>
        {akte.mandant.adresse or '[Adresse des Mandanten]'}
    </p>
    <p style="text-align: center;">– Kläger/in –</p>
    <p style="text-align: center;">
        Prozessbevollmächtigte/r: [Rechtsanwalt/Rechtsanwältin]
    </p>
    <p style="text-align: center; font-weight: bold;">gegen</p>
    <p>
        <strong>{akte.gegner.name or '[Name des Arbeitgebers]'}</strong><br>
        {akte.gegner.adresse or '[Adresse des Arbeitgebers]'}
    </p>
    <p style="text-align: center;">– Beklagte/r –</p>
</div>

<p class="betreff">wegen: Feststellung der Unwirksamkeit einer Kündigung</p>
<p><strong>Streitwert: {streitwert:,.2f} € (§ 42 Abs. 2 GKG)</strong></p>

<p>Namens und in Vollmacht des Klägers/der Klägerin erhebe ich</p>

<h2>Klage</h2>

<p>und beantrage:</p>

<div class="antrag">
    <p><strong>1.</strong> Es wird festgestellt, dass das zwischen den Parteien bestehende 
    Arbeitsverhältnis durch die {akte.kuendigung.kuendigungsart}e Kündigung 
    {f"vom {akte.kuendigung.kuendigung_datum.strftime('%d.%m.%Y')}" if akte.kuendigung.kuendigung_datum else "vom [Datum]"}, 
    zugegangen am {akte.kuendigung.zugang_datum.strftime('%d.%m.%Y') if akte.kuendigung.zugang_datum else '[Datum]'}, 
    nicht aufgelöst worden ist.</p>
    
    <p><strong>2.</strong> Es wird festgestellt, dass das Arbeitsverhältnis auch nicht durch 
    andere Beendigungstatbestände endet, sondern zu unveränderten Bedingungen über den 
    {akte.kuendigung.kuendigung_zum.strftime('%d.%m.%Y') if akte.kuendigung.kuendigung_zum else '[Beendigungstermin]'} 
    hinaus fortbesteht.</p>
    
    <p><strong>3.</strong> Die Beklagte wird verurteilt, den Kläger/die Klägerin bis zum 
    rechtskräftigen Abschluss des Rechtsstreits zu unveränderten Arbeitsbedingungen als 
    {akte.arbeitsverhaeltnis.position or '[Position]'} weiterzubeschäftigen.</p>
    
    <p><strong>4.</strong> Die Beklagte trägt die Kosten des Rechtsstreits.</p>
</div>

<div class="begruendung">
    <h2>Begründung</h2>
    
    <h3>I. Sachverhalt</h3>
    
    <p>Der Kläger/Die Klägerin ist seit dem 
    {akte.arbeitsverhaeltnis.eintrittsdatum.strftime('%d.%m.%Y') if akte.arbeitsverhaeltnis.eintrittsdatum else '[Datum]'} 
    bei der Beklagten als {akte.arbeitsverhaeltnis.position or '[Position]'} beschäftigt. 
    Das monatliche Bruttogehalt beträgt {akte.arbeitsverhaeltnis.bruttogehalt:,.2f} €.</p>
    
    <p>Die Betriebszugehörigkeit beträgt damit {zugehoerigkeit} Jahre ({zugehoerigkeit_monate} Monate).</p>
    
    {f'<p>Auf das Arbeitsverhältnis findet der Tarifvertrag {akte.arbeitsverhaeltnis.tarifvertrag} Anwendung.</p>' if akte.arbeitsverhaeltnis.tarifvertrag else ''}
    
    <p>Mit Schreiben vom {akte.kuendigung.kuendigung_datum.strftime('%d.%m.%Y') if akte.kuendigung.kuendigung_datum else '[Datum]'}, 
    dem Kläger/der Klägerin zugegangen am 
    {akte.kuendigung.zugang_datum.strftime('%d.%m.%Y') if akte.kuendigung.zugang_datum else '[Datum]'}, 
    kündigte die Beklagte das Arbeitsverhältnis {akte.kuendigung.kuendigungsart} 
    {f"zum {akte.kuendigung.kuendigung_zum.strftime('%d.%m.%Y')}" if akte.kuendigung.kuendigung_zum else ''}.</p>
    
    {f'<p>Als Kündigungsgrund wurde angegeben: {akte.kuendigung.kuendigungsgrund}</p>' if akte.kuendigung.kuendigungsgrund else ''}
    
    {f'<p>{akte.sachverhalt_zusatz}</p>' if akte.sachverhalt_zusatz else ''}
    
    <p><strong>Beweis:</strong> Kündigungsschreiben (Anlage K1), Arbeitsvertrag (Anlage K2)</p>
    
    <h3>II. Rechtliche Würdigung</h3>
    
    <p>Die Kündigung ist unwirksam.</p>
    
    {unwirksamkeitsgruende}
    
    <h3>III. Weiterbeschäftigungsanspruch</h3>
    
    <p>Der Kläger/Die Klägerin hat einen Anspruch auf Weiterbeschäftigung bis zum 
    rechtskräftigen Abschluss des Rechtsstreits (BAG, Großer Senat, Beschluss vom 27.02.1985 – GS 1/84).</p>
    
    <p>Nach der ständigen Rechtsprechung des Bundesarbeitsgerichts überwiegt nach Ablauf 
    der Kündigungsfrist das Interesse des Arbeitnehmers an der Weiterbeschäftigung, 
    wenn die Kündigung – wie hier – offensichtlich unwirksam ist oder das 
    erstinstanzliche Gericht der Kündigungsschutzklage stattgegeben hat.</p>
    
</div>

<div class="unterschrift">
    <p>_________________________________</p>
    <p>Rechtsanwalt/Rechtsanwältin</p>
</div>

<h3>Anlagenverzeichnis:</h3>
<ul>
    <li>Anlage K1: Kündigungsschreiben</li>
    <li>Anlage K2: Arbeitsvertrag</li>
    <li>Anlage K3: Gehaltsabrechnungen (letzte 3 Monate)</li>
    <li>Vollmacht</li>
</ul>

</body>
</html>
"""
        
        # Text-Version für Kopieren
        text_version = self._html_zu_text(inhalt)
        
        return GenerierterSchriftsatz(
            typ=SchriftsatzTyp.KUENDIGUNGSSCHUTZKLAGE,
            titel=f"Kündigungsschutzklage {akte.mandant.name} ./. {akte.gegner.name}",
            inhalt_html=inhalt,
            inhalt_text=text_version,
            streitwert=streitwert,
            generiert_am=datetime.now(),
            aktenzeichen=akte.aktenzeichen,
            hinweise=hinweise
        )
    
    def _analysiere_unwirksamkeitsgruende(self, akte: Akteninhalt) -> str:
        """Analysiert mögliche Unwirksamkeitsgründe und generiert Begründung."""
        
        gruende = []
        
        # 1. Schriftform
        if not akte.kuendigung.schriftform_eingehalten:
            gruende.append("""
            <h4>1. Verstoß gegen das Schriftformerfordernis (§ 623 BGB)</h4>
            <p>Die Kündigung ist bereits aus formellen Gründen nichtig, da sie nicht 
            der gesetzlich vorgeschriebenen Schriftform entspricht. Nach § 623 BGB 
            bedarf die Beendigung eines Arbeitsverhältnisses durch Kündigung der Schriftform. 
            Eine Kündigung per E-Mail, Fax oder WhatsApp ist unwirksam.</p>
            """)
        
        # 2. Betriebsratsanhörung
        if not akte.kuendigung.betriebsrat_angehoert:
            gruende.append("""
            <h4>2. Fehlende/Fehlerhafte Betriebsratsanhörung (§ 102 BetrVG)</h4>
            <p>Die Kündigung ist unwirksam, da der Betriebsrat nicht ordnungsgemäß 
            nach § 102 BetrVG angehört wurde. Eine ohne Anhörung des Betriebsrats 
            ausgesprochene Kündigung ist unwirksam. Die Anhörung muss vor Ausspruch 
            der Kündigung erfolgen und den Betriebsrat über die Person des Arbeitnehmers, 
            die Kündigungsart und die Kündigungsgründe vollständig informieren.</p>
            <p><strong>Beweis:</strong> Zeugnis des Betriebsratsvorsitzenden</p>
            """)
        
        # 3. Fehlende Abmahnung bei verhaltensbedingter Kündigung
        if "verhaltens" in (akte.kuendigung.kuendigungsgrund or "").lower() and not akte.kuendigung.abmahnung_vorhanden:
            gruende.append("""
            <h4>3. Fehlende Abmahnung</h4>
            <p>Bei einer verhaltensbedingten Kündigung ist grundsätzlich eine vorherige 
            einschlägige Abmahnung erforderlich. Die Abmahnung muss das beanstandete 
            Verhalten konkret bezeichnen und für den Wiederholungsfall arbeitsrechtliche 
            Konsequenzen androhen. Eine solche Abmahnung ist vorliegend nicht erfolgt.</p>
            <p>Nach ständiger Rechtsprechung des BAG ist eine verhaltensbedingte Kündigung 
            ohne vorherige Abmahnung nur in Ausnahmefällen bei besonders schweren 
            Pflichtverletzungen zulässig. Ein solcher Ausnahmefall liegt hier nicht vor.</p>
            """)
        
        # 4. KSchG-Schutz
        gruende.append("""
            <h4>{num}. Soziale Rechtfertigung (§ 1 KSchG)</h4>
            <p>Das Kündigungsschutzgesetz findet Anwendung, da der Betrieb mehr als 
            10 Arbeitnehmer beschäftigt und das Arbeitsverhältnis länger als 6 Monate 
            besteht. Die Kündigung ist daher nur wirksam, wenn sie sozial gerechtfertigt ist.</p>
            <p>Die von der Beklagten angeführten Kündigungsgründe rechtfertigen die 
            Kündigung nicht:</p>
            <ul>
                <li>Die behaupteten Gründe sind nicht hinreichend substantiiert.</li>
                <li>Es fehlt an der erforderlichen Abwägung der beiderseitigen Interessen.</li>
                <li>Mildere Mittel als die Kündigung wurden nicht geprüft.</li>
            </ul>
        """.format(num=len(gruende) + 1))
        
        if not gruende:
            gruende.append("""
            <h4>1. Allgemeine Unwirksamkeitsgründe</h4>
            <p>Die Kündigung ist aus den folgenden Gründen unwirksam:</p>
            <p>[Hier sind die konkreten Unwirksamkeitsgründe einzufügen]</p>
            """)
        
        return "\n".join(gruende)
    
    # =========================================================================
    # LOHNKLAGE
    # =========================================================================
    
    def generiere_lohnklage(self, akte: Akteninhalt) -> GenerierterSchriftsatz:
        """Generiert eine Lohnklage."""
        
        streitwert = akte.lohn.offener_betrag_brutto
        ueberstunden_wert = akte.lohn.offene_ueberstunden * akte.lohn.ueberstunden_stundenlohn
        gesamt_forderung = streitwert + ueberstunden_wert
        
        hinweise = []
        if streitwert == 0:
            hinweise.append("⚠️ Kein offener Lohnbetrag angegeben!")
        
        # Monate formatieren
        monate_text = ", ".join(akte.lohn.offene_monate) if akte.lohn.offene_monate else "[Monate einfügen]"
        
        inhalt = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.5; margin: 2cm; }}
        h1 {{ text-align: center; font-size: 14pt; }}
        .antrag {{ margin: 1cm 0; padding-left: 1cm; }}
        p {{ text-align: justify; }}
    </style>
</head>
<body>

<div class="header">
    <p><strong>Rechtsanwalt/Rechtsanwältin</strong><br>[Kanzleidaten]</p>
    <p><strong>An das Arbeitsgericht {akte.gericht or '[Ort]'}</strong></p>
    <p style="text-align: right;">{self.heute.strftime('%d.%m.%Y')}</p>
</div>

<h1>Klage auf Zahlung von Arbeitsentgelt</h1>

<div class="rubrum">
    <p><strong>{akte.mandant.name}</strong>, {akte.mandant.adresse}</p>
    <p style="text-align: center;">– Kläger/in –</p>
    <p style="text-align: center; font-weight: bold;">gegen</p>
    <p><strong>{akte.gegner.name}</strong>, {akte.gegner.adresse}</p>
    <p style="text-align: center;">– Beklagte/r –</p>
</div>

<p class="betreff"><strong>wegen: Zahlung von Arbeitsentgelt</strong></p>
<p><strong>Streitwert: {gesamt_forderung:,.2f} €</strong></p>

<p>Namens und in Vollmacht des Klägers/der Klägerin erhebe ich <strong>Klage</strong> und beantrage:</p>

<div class="antrag">
    <p><strong>1.</strong> Die Beklagte wird verurteilt, an den Kläger/die Klägerin 
    <strong>{gesamt_forderung:,.2f} € brutto</strong> nebst Zinsen in Höhe von 5 Prozentpunkten 
    über dem Basiszinssatz seit Rechtshängigkeit zu zahlen.</p>
    
    <p><strong>2.</strong> Die Beklagte trägt die Kosten des Rechtsstreits.</p>
</div>

<h2>Begründung</h2>

<h3>I. Sachverhalt</h3>

<p>Der Kläger/Die Klägerin ist seit dem 
{akte.arbeitsverhaeltnis.eintrittsdatum.strftime('%d.%m.%Y') if akte.arbeitsverhaeltnis.eintrittsdatum else '[Datum]'} 
bei der Beklagten als {akte.arbeitsverhaeltnis.position or '[Position]'} beschäftigt. 
Das vereinbarte monatliche Bruttogehalt beträgt <strong>{akte.arbeitsverhaeltnis.bruttogehalt:,.2f} €</strong>.</p>

<p>Die Beklagte hat das Arbeitsentgelt für die Monate <strong>{monate_text}</strong> 
nicht bzw. nicht vollständig gezahlt.</p>

<p>Es besteht ein Lohnrückstand von <strong>{streitwert:,.2f} € brutto</strong>.</p>

{f'''<p>Darüber hinaus hat der Kläger/die Klägerin <strong>{akte.lohn.offene_ueberstunden} Überstunden</strong> 
geleistet, die mit einem Stundensatz von {akte.lohn.ueberstunden_stundenlohn:.2f} € zu vergüten sind. 
Dies ergibt einen weiteren Anspruch von <strong>{ueberstunden_wert:,.2f} € brutto</strong>.</p>''' if ueberstunden_wert > 0 else ''}

<p><strong>Beweis:</strong> Arbeitsvertrag (Anlage K1), Gehaltsabrechnungen (Anlage K2), 
Kontoauszüge (Anlage K3){', Überstundennachweise (Anlage K4)' if ueberstunden_wert > 0 else ''}</p>

<h3>II. Rechtliche Würdigung</h3>

<p>Der Anspruch auf Zahlung des Arbeitsentgelts ergibt sich aus § 611a BGB i.V.m. dem Arbeitsvertrag.</p>

<p>Nach § 614 BGB ist das Arbeitsentgelt nach Leistung der Arbeit zu entrichten. 
Die Beklagte ist ihrer Zahlungspflicht nicht nachgekommen.</p>

{f'''<p>Der Anspruch auf Überstundenvergütung ergibt sich aus § 612 BGB. Die Überstunden waren 
betrieblich erforderlich und wurden vom Arbeitgeber angeordnet bzw. geduldet.</p>''' if ueberstunden_wert > 0 else ''}

<p>Der Zinsanspruch folgt aus §§ 288 Abs. 1, 286 Abs. 1 BGB.</p>

<div class="unterschrift">
    <p>_________________________________</p>
    <p>Rechtsanwalt/Rechtsanwältin</p>
</div>

</body>
</html>
"""
        
        return GenerierterSchriftsatz(
            typ=SchriftsatzTyp.LOHNKLAGE,
            titel=f"Lohnklage {akte.mandant.name} ./. {akte.gegner.name}",
            inhalt_html=inhalt,
            inhalt_text=self._html_zu_text(inhalt),
            streitwert=gesamt_forderung,
            generiert_am=datetime.now(),
            aktenzeichen=akte.aktenzeichen,
            hinweise=hinweise
        )
    
    # =========================================================================
    # URLAUBSKLAGE / URLAUBSABGELTUNG
    # =========================================================================
    
    def generiere_urlaubsklage(self, akte: Akteninhalt, abgeltung: bool = False) -> GenerierterSchriftsatz:
        """Generiert eine Urlaubsklage oder Urlaubsabgeltungsklage."""
        
        tagesentgelt = akte.arbeitsverhaeltnis.bruttogehalt / 21.67  # Durchschnittliche Arbeitstage
        streitwert = akte.urlaub.offene_tage * tagesentgelt
        
        typ = SchriftsatzTyp.URLAUBSABGELTUNG if abgeltung else SchriftsatzTyp.URLAUBSKLAGE
        titel_text = "Urlaubsabgeltung" if abgeltung else "Urlaubsgewährung"
        
        inhalt = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.5; margin: 2cm; }}
        h1 {{ text-align: center; font-size: 14pt; }}
        .antrag {{ margin: 1cm 0; padding-left: 1cm; }}
        p {{ text-align: justify; }}
    </style>
</head>
<body>

<div class="header">
    <p><strong>Rechtsanwalt/Rechtsanwältin</strong><br>[Kanzleidaten]</p>
    <p><strong>An das Arbeitsgericht {akte.gericht or '[Ort]'}</strong></p>
    <p style="text-align: right;">{self.heute.strftime('%d.%m.%Y')}</p>
</div>

<h1>Klage auf {titel_text}</h1>

<div class="rubrum">
    <p><strong>{akte.mandant.name}</strong>, {akte.mandant.adresse}</p>
    <p style="text-align: center;">– Kläger/in –</p>
    <p style="text-align: center; font-weight: bold;">gegen</p>
    <p><strong>{akte.gegner.name}</strong>, {akte.gegner.adresse}</p>
    <p style="text-align: center;">– Beklagte/r –</p>
</div>

<p class="betreff"><strong>wegen: {titel_text}</strong></p>
<p><strong>Streitwert: {streitwert:,.2f} €</strong></p>

<p>Namens und in Vollmacht des Klägers/der Klägerin erhebe ich <strong>Klage</strong> und beantrage:</p>

<div class="antrag">
    {f'''<p><strong>1.</strong> Die Beklagte wird verurteilt, an den Kläger/die Klägerin 
    <strong>{streitwert:,.2f} € brutto</strong> als Urlaubsabgeltung für {akte.urlaub.offene_tage} nicht 
    gewährte Urlaubstage nebst Zinsen in Höhe von 5 Prozentpunkten über dem Basiszinssatz 
    seit Rechtshängigkeit zu zahlen.</p>''' if abgeltung else f'''<p><strong>1.</strong> Die Beklagte wird verurteilt, dem Kläger/der Klägerin 
    <strong>{akte.urlaub.offene_tage} Tage</strong> bezahlten Erholungsurlaub zu gewähren.</p>'''}
    
    <p><strong>2.</strong> Die Beklagte trägt die Kosten des Rechtsstreits.</p>
</div>

<h2>Begründung</h2>

<h3>I. Sachverhalt</h3>

<p>Der Kläger/Die Klägerin ist seit dem 
{akte.arbeitsverhaeltnis.eintrittsdatum.strftime('%d.%m.%Y') if akte.arbeitsverhaeltnis.eintrittsdatum else '[Datum]'} 
bei der Beklagten beschäftigt.</p>

<p>Der jährliche Urlaubsanspruch beträgt nach dem Arbeitsvertrag 
<strong>{akte.urlaub.gesamtanspruch_tage} Arbeitstage</strong>.</p>

<p>Für das Jahr {akte.urlaub.urlaubsjahr or datetime.now().year} hat der Kläger/die Klägerin 
{akte.urlaub.genommen_tage} Urlaubstage genommen. Es verbleiben somit 
<strong>{akte.urlaub.offene_tage} offene Urlaubstage</strong>.</p>

{f'<p>Das Arbeitsverhältnis wurde zwischenzeitlich beendet. Der Resturlaub ist daher gemäß § 7 Abs. 4 BUrlG abzugelten.</p>' if abgeltung else '<p>Der Kläger/Die Klägerin hat die Beklagte mehrfach erfolglos zur Urlaubsgewährung aufgefordert.</p>'}

<h3>II. Rechtliche Würdigung</h3>

<p>Der Urlaubsanspruch ergibt sich aus § 1 BUrlG i.V.m. dem Arbeitsvertrag.</p>

{f'''<p>Nach § 7 Abs. 4 BUrlG ist der Urlaub abzugelten, wenn er wegen Beendigung des 
Arbeitsverhältnisses ganz oder teilweise nicht mehr gewährt werden kann. 
Die Urlaubsabgeltung berechnet sich wie folgt:</p>
<p>{akte.urlaub.offene_tage} Tage × {tagesentgelt:.2f} € Tagesentgelt = <strong>{streitwert:,.2f} € brutto</strong></p>''' if abgeltung else '''<p>Nach § 7 Abs. 1 BUrlG hat der Arbeitgeber den Urlaub zu gewähren. Der Arbeitnehmer 
hat einen einklagbaren Anspruch auf Freistellung von der Arbeitspflicht unter 
Fortzahlung des Arbeitsentgelts.</p>'''}

<div class="unterschrift">
    <p>_________________________________</p>
    <p>Rechtsanwalt/Rechtsanwältin</p>
</div>

</body>
</html>
"""
        
        return GenerierterSchriftsatz(
            typ=typ,
            titel=f"{titel_text}sklage {akte.mandant.name} ./. {akte.gegner.name}",
            inhalt_html=inhalt,
            inhalt_text=self._html_zu_text(inhalt),
            streitwert=streitwert,
            generiert_am=datetime.now(),
            aktenzeichen=akte.aktenzeichen,
            hinweise=[]
        )
    
    # =========================================================================
    # ZEUGNISKLAGE
    # =========================================================================
    
    def generiere_zeugnisklage(self, akte: Akteninhalt) -> GenerierterSchriftsatz:
        """Generiert eine Zeugnisklage."""
        
        # Streitwert: 1 Bruttomonatsgehalt
        streitwert = akte.arbeitsverhaeltnis.bruttogehalt
        
        # Mängel formatieren
        maengel_text = ""
        if akte.zeugnis.maengel:
            maengel_items = "\n".join([f"<li>{m}</li>" for m in akte.zeugnis.maengel])
            maengel_text = f"<ul>{maengel_items}</ul>"
        
        inhalt = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.5; margin: 2cm; }}
        h1 {{ text-align: center; font-size: 14pt; }}
        .antrag {{ margin: 1cm 0; padding-left: 1cm; }}
        p {{ text-align: justify; }}
    </style>
</head>
<body>

<div class="header">
    <p><strong>Rechtsanwalt/Rechtsanwältin</strong><br>[Kanzleidaten]</p>
    <p><strong>An das Arbeitsgericht {akte.gericht or '[Ort]'}</strong></p>
    <p style="text-align: right;">{self.heute.strftime('%d.%m.%Y')}</p>
</div>

<h1>Klage auf Erteilung eines {akte.zeugnis.zeugnis_art}en Arbeitszeugnisses</h1>

<div class="rubrum">
    <p><strong>{akte.mandant.name}</strong>, {akte.mandant.adresse}</p>
    <p style="text-align: center;">– Kläger/in –</p>
    <p style="text-align: center; font-weight: bold;">gegen</p>
    <p><strong>{akte.gegner.name}</strong>, {akte.gegner.adresse}</p>
    <p style="text-align: center;">– Beklagte/r –</p>
</div>

<p class="betreff"><strong>wegen: Erteilung eines Arbeitszeugnisses</strong></p>
<p><strong>Streitwert: {streitwert:,.2f} €</strong></p>

<p>Namens und in Vollmacht des Klägers/der Klägerin erhebe ich <strong>Klage</strong> und beantrage:</p>

<div class="antrag">
    {f'''<p><strong>1.</strong> Die Beklagte wird verurteilt, dem Kläger/der Klägerin ein 
    {akte.zeugnis.zeugnis_art}es Arbeitszeugnis zu erteilen, das sich auf Art und Dauer 
    der Beschäftigung sowie auf Führung und Leistung erstreckt.</p>''' if not akte.zeugnis.zeugnis_erhalten else f'''<p><strong>1.</strong> Die Beklagte wird verurteilt, dem Kläger/der Klägerin ein 
    berichtigtes {akte.zeugnis.zeugnis_art}es Arbeitszeugnis zu erteilen, das folgende 
    Mängel nicht mehr enthält:</p>
    {maengel_text}'''}
    
    <p><strong>2.</strong> Die Beklagte trägt die Kosten des Rechtsstreits.</p>
</div>

<h2>Begründung</h2>

<h3>I. Sachverhalt</h3>

<p>Der Kläger/Die Klägerin war vom 
{akte.arbeitsverhaeltnis.eintrittsdatum.strftime('%d.%m.%Y') if akte.arbeitsverhaeltnis.eintrittsdatum else '[Datum]'} 
bis zum [Beendigungsdatum] bei der Beklagten als {akte.arbeitsverhaeltnis.position or '[Position]'} beschäftigt.</p>

{f'''<p>Die Beklagte hat trotz Aufforderung kein Arbeitszeugnis erteilt.</p>''' if not akte.zeugnis.zeugnis_erhalten else f'''<p>Das von der Beklagten erteilte Zeugnis weist folgende Mängel auf:</p>
{maengel_text}
<p>Die Leistungen und das Verhalten des Klägers/der Klägerin rechtfertigen eine Bewertung 
mit der Note "{akte.zeugnis.gewuenschte_note}".</p>'''}

<h3>II. Rechtliche Würdigung</h3>

<p>Der Anspruch auf Erteilung eines Arbeitszeugnisses ergibt sich aus § 109 GewO.</p>

<p>Nach § 109 Abs. 1 GewO hat der Arbeitnehmer bei Beendigung des Arbeitsverhältnisses 
Anspruch auf ein schriftliches Zeugnis. Das Zeugnis muss mindestens Angaben zu Art und 
Dauer der Tätigkeit enthalten (einfaches Zeugnis). Auf Verlangen des Arbeitnehmers ist 
das Zeugnis auf die Leistungen und das Verhalten im Arbeitsverhältnis zu erstrecken 
(qualifiziertes Zeugnis).</p>

<p>Das Zeugnis muss klar und verständlich formuliert sein. Es darf keine Merkmale oder 
Formulierungen enthalten, die den Zweck haben, eine andere als aus der äußeren Form 
oder dem Wortlaut ersichtliche Aussage über den Arbeitnehmer zu treffen.</p>

{f'''<p>Das erteilte Zeugnis entspricht nicht diesen Anforderungen. Die Beklagte ist daher 
zur Berichtigung verpflichtet.</p>''' if akte.zeugnis.zeugnis_erhalten else ''}

<div class="unterschrift">
    <p>_________________________________</p>
    <p>Rechtsanwalt/Rechtsanwältin</p>
</div>

</body>
</html>
"""
        
        return GenerierterSchriftsatz(
            typ=SchriftsatzTyp.ZEUGNISKLAGE,
            titel=f"Zeugnisklage {akte.mandant.name} ./. {akte.gegner.name}",
            inhalt_html=inhalt,
            inhalt_text=self._html_zu_text(inhalt),
            streitwert=streitwert,
            generiert_am=datetime.now(),
            aktenzeichen=akte.aktenzeichen,
            hinweise=[]
        )
    
    # =========================================================================
    # VERGLEICHSVORSCHLAG
    # =========================================================================
    
    def generiere_vergleichsvorschlag(
        self, 
        akte: Akteninhalt, 
        abfindung: float,
        beendigungsdatum: date,
        freistellung: bool = True,
        zeugnisnote: str = "gut"
    ) -> GenerierterSchriftsatz:
        """Generiert einen Vergleichsvorschlag."""
        
        inhalt = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        body {{ font-family: 'Times New Roman', serif; font-size: 12pt; line-height: 1.5; margin: 2cm; }}
        h1 {{ text-align: center; font-size: 14pt; }}
        .punkt {{ margin: 0.5cm 0; }}
        p {{ text-align: justify; }}
    </style>
</head>
<body>

<div class="header">
    <p><strong>Rechtsanwalt/Rechtsanwältin</strong><br>[Kanzleidaten]</p>
    <p style="text-align: right;">{self.heute.strftime('%d.%m.%Y')}</p>
</div>

<h1>Vergleichsvorschlag</h1>

<p>In dem Rechtsstreit</p>

<p><strong>{akte.mandant.name}</strong> ./. <strong>{akte.gegner.name}</strong></p>

<p>Az.: {akte.aktenzeichen or '[Aktenzeichen]'}</p>

<p>schlagen wir namens und in Vollmacht des Klägers/der Klägerin folgenden</p>

<h2>Vergleich</h2>

<p>vor:</p>

<div class="punkt">
    <p><strong>1.</strong> Die Parteien sind sich einig, dass das zwischen ihnen bestehende 
    Arbeitsverhältnis aufgrund ordentlicher, arbeitgeberseitiger, betriebsbedingter Kündigung 
    mit Ablauf des <strong>{beendigungsdatum.strftime('%d.%m.%Y')}</strong> sein Ende finden wird.</p>
</div>

<div class="punkt">
    <p><strong>2.</strong> Die Beklagte zahlt an den Kläger/die Klägerin für den Verlust des 
    Arbeitsplatzes eine Abfindung gemäß §§ 9, 10 KSchG in Höhe von 
    <strong>{abfindung:,.2f} € brutto</strong> (in Worten: [Betrag in Worten] Euro).</p>
</div>

<div class="punkt">
    <p><strong>3.</strong> Die Beklagte rechnet das Arbeitsverhältnis bis zum Beendigungszeitpunkt 
    ordnungsgemäß ab und zahlt die sich ergebenden Nettobeträge an den Kläger/die Klägerin aus.</p>
</div>

{f'''<div class="punkt">
    <p><strong>4.</strong> Der Kläger/Die Klägerin wird bis zum Beendigungszeitpunkt unter 
    Fortzahlung der Vergütung unwiderruflich von der Erbringung der Arbeitsleistung freigestellt. 
    Urlaubs- und Freizeitausgleichsansprüche werden auf die Freistellung angerechnet.</p>
</div>''' if freistellung else ''}

<div class="punkt">
    <p><strong>{5 if freistellung else 4}.</strong> Die Beklagte erteilt dem Kläger/der Klägerin 
    ein qualifiziertes Arbeitszeugnis mit der Leistungs- und Verhaltensbeurteilung 
    "<strong>{zeugnisnote}</strong>" und einer Bedauerns-, Dankes- und Wunschformel.</p>
</div>

<div class="punkt">
    <p><strong>{6 if freistellung else 5}.</strong> Mit Erfüllung dieses Vergleichs sind 
    sämtliche wechselseitigen Ansprüche der Parteien aus dem Arbeitsverhältnis und seiner 
    Beendigung, gleich aus welchem Rechtsgrund, erledigt.</p>
</div>

<div class="punkt">
    <p><strong>{7 if freistellung else 6}.</strong> Die Kosten des Rechtsstreits werden 
    gegeneinander aufgehoben.</p>
</div>

<p style="margin-top: 2cm;">Wir bitten um Stellungnahme bis zum [Datum].</p>

<div class="unterschrift">
    <p>Mit freundlichen Grüßen</p>
    <p>_________________________________</p>
    <p>Rechtsanwalt/Rechtsanwältin</p>
</div>

</body>
</html>
"""
        
        return GenerierterSchriftsatz(
            typ=SchriftsatzTyp.VERGLEICHSVORSCHLAG,
            titel=f"Vergleichsvorschlag {akte.mandant.name} ./. {akte.gegner.name}",
            inhalt_html=inhalt,
            inhalt_text=self._html_zu_text(inhalt),
            streitwert=abfindung,
            generiert_am=datetime.now(),
            aktenzeichen=akte.aktenzeichen,
            hinweise=[]
        )
    
    # =========================================================================
    # HILFSFUNKTIONEN
    # =========================================================================
    
    def _html_zu_text(self, html: str) -> str:
        """Konvertiert HTML zu reinem Text."""
        # Einfache Konvertierung
        text = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'</p>', '\n\n', text)
        text = re.sub(r'</div>', '\n', text)
        text = re.sub(r'</h[1-6]>', '\n\n', text)
        text = re.sub(r'<li>', '• ', text)
        text = re.sub(r'</li>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        text = text.strip()
        return text
    
    def get_verfuegbare_schriftsaetze(self) -> List[Dict]:
        """Gibt alle verfügbaren Schriftsatztypen zurück."""
        return [
            {"typ": SchriftsatzTyp.KUENDIGUNGSSCHUTZKLAGE, "name": "Kündigungsschutzklage", "icon": "⚖️"},
            {"typ": SchriftsatzTyp.LOHNKLAGE, "name": "Lohnklage", "icon": "💰"},
            {"typ": SchriftsatzTyp.URLAUBSKLAGE, "name": "Urlaubsklage", "icon": "🏖️"},
            {"typ": SchriftsatzTyp.URLAUBSABGELTUNG, "name": "Urlaubsabgeltungsklage", "icon": "💶"},
            {"typ": SchriftsatzTyp.ZEUGNISKLAGE, "name": "Zeugnisklage", "icon": "📄"},
            {"typ": SchriftsatzTyp.WEITERBESCHAEFTIGUNG, "name": "Weiterbeschäftigungsantrag", "icon": "👷"},
            {"typ": SchriftsatzTyp.VERGLEICHSVORSCHLAG, "name": "Vergleichsvorschlag", "icon": "🤝"},
        ]
