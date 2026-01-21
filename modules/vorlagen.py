"""
JuraConnect - Dokumenten-Vorlagen
Vorlagen für arbeitsrechtliche Schriftsätze
"""

from datetime import date
from dataclasses import dataclass


@dataclass
class VorlagenDaten:
    mandant_name: str
    mandant_anschrift: str
    mandant_plz_ort: str
    mandant_telefon: str = ""
    mandant_email: str = ""
    gegner_name: str = ""
    gegner_anschrift: str = ""
    gegner_plz_ort: str = ""
    kanzlei_name: str = "Kanzlei RHM"
    kanzlei_anschrift: str = "Musterstraße 1"
    kanzlei_plz_ort: str = "12345 Musterstadt"
    kanzlei_telefon: str = ""
    az_kanzlei: str = ""
    az_gericht: str = ""
    eintrittsdatum: str = ""
    austrittsdatum: str = ""
    bruttogehalt: str = ""
    position: str = ""
    kuendigung_datum: str = ""
    kuendigung_zugang: str = ""
    kuendigungsfrist_ende: str = ""


class VorlagenManager:
    """Verwaltet und generiert Dokumentenvorlagen"""
    
    def kuendigungsschutzklage(self, daten: VorlagenDaten, klagebegründung: str = "") -> str:
        heute = date.today()
        
        return f"""{daten.kanzlei_name}
{daten.kanzlei_anschrift}
{daten.kanzlei_plz_ort}

An das                                              {heute.strftime('%d.%m.%Y')}
Arbeitsgericht [Ort]
[Anschrift]

Unser Zeichen: {daten.az_kanzlei}

                            KLAGE

des/der {daten.mandant_name}
        {daten.mandant_anschrift}
        {daten.mandant_plz_ort}
                                                    - Kläger/in -

Prozessbevollmächtigte: {daten.kanzlei_name}

gegen

        {daten.gegner_name}
        {daten.gegner_anschrift}
        {daten.gegner_plz_ort}
                                                    - Beklagte/r -

wegen: Kündigungsschutz

Namens und in Vollmacht erheben wir Klage und beantragen:

1. Es wird festgestellt, dass das Arbeitsverhältnis durch die Kündigung 
   vom {daten.kuendigung_datum} nicht aufgelöst worden ist.

2. Die Beklagte wird verurteilt, den Kläger/die Klägerin zu unveränderten 
   Bedingungen als {daten.position} weiterzubeschäftigen.

3. Die Beklagte trägt die Kosten des Rechtsstreits.

                        BEGRÜNDUNG

I. Sachverhalt

Der Kläger/Die Klägerin ist seit dem {daten.eintrittsdatum} bei der Beklagten 
als {daten.position} beschäftigt. Das Bruttogehalt beträgt {daten.bruttogehalt} Euro.

Mit Schreiben vom {daten.kuendigung_datum}, zugegangen am {daten.kuendigung_zugang}, 
kündigte die Beklagte zum {daten.kuendigungsfrist_ende}.

{klagebegründung if klagebegründung else "[Weitere Sachverhaltsdarstellung]"}

II. Rechtliche Würdigung

1. Die Klage ist zulässig (Dreiwochenfrist § 4 KSchG gewahrt).
2. Die Kündigung ist sozial ungerechtfertigt (§ 1 Abs. 2 KSchG).

III. Streitwert

{daten.bruttogehalt} x 3 = [Betrag] Euro (§ 42 Abs. 2 GKG).

{daten.kanzlei_name}
Rechtsanwalt/Rechtsanwältin

Anlagen:
- Arbeitsvertrag (Kopie)
- Kündigungsschreiben (Kopie)
- Vollmacht"""
    
    def zeugnisklage(self, daten: VorlagenDaten, zeugnis_art: str = "erteilung",
                     maengel: str = "") -> str:
        heute = date.today()
        
        if zeugnis_art == "erteilung":
            antrag = """Es wird beantragt:
1. Die Beklagte wird verurteilt, ein qualifiziertes Arbeitszeugnis zu erteilen.
2. Die Beklagte trägt die Kosten."""
            begruendung = "Anspruch auf Zeugnis gemäß § 109 GewO."
        else:
            antrag = """Es wird beantragt:
1. Die Beklagte wird verurteilt, ein berichtigtes Zeugnis zu erteilen.
2. Die Beklagte trägt die Kosten."""
            begruendung = f"Das erteilte Zeugnis enthält folgende Mängel:\n{maengel}"
        
        return f"""{daten.kanzlei_name}
{daten.kanzlei_anschrift}
{daten.kanzlei_plz_ort}

An das Arbeitsgericht [Ort]                         {heute.strftime('%d.%m.%Y')}

                            KLAGE

des/der {daten.mandant_name}, {daten.mandant_plz_ort}
                                                    - Kläger/in -
gegen
        {daten.gegner_name}, {daten.gegner_plz_ort}
                                                    - Beklagte/r -

wegen: Zeugniserteilung/-berichtigung

{antrag}

                        BEGRÜNDUNG

Beschäftigung: {daten.eintrittsdatum} bis {daten.austrittsdatum} als {daten.position}.

{begruendung}

{daten.kanzlei_name}"""
    
    def lohnklage(self, daten: VorlagenDaten, forderungen: list = None) -> str:
        heute = date.today()
        
        if forderungen:
            forderungs_text = "\n".join([f"   - {f['beschreibung']}: {f['betrag']:,.2f} €" 
                                         for f in forderungen])
            gesamt = sum(f['betrag'] for f in forderungen)
        else:
            forderungs_text = "   - [Forderungen]"
            gesamt = 0
        
        return f"""{daten.kanzlei_name}
{daten.kanzlei_anschrift}
{daten.kanzlei_plz_ort}

An das Arbeitsgericht [Ort]                         {heute.strftime('%d.%m.%Y')}

                            KLAGE

des/der {daten.mandant_name}, {daten.mandant_plz_ort}
                                                    - Kläger/in -
gegen
        {daten.gegner_name}, {daten.gegner_plz_ort}
                                                    - Beklagte/r -

wegen: Lohn-/Gehaltszahlung

Es wird beantragt:
1. Die Beklagte wird verurteilt, {gesamt:,.2f} Euro brutto nebst Zinsen zu zahlen.
2. Die Beklagte trägt die Kosten.

                        BEGRÜNDUNG

Beschäftigung seit {daten.eintrittsdatum} als {daten.position}.
Monatsgehalt: {daten.bruttogehalt} Euro.

Geschuldete Beträge:
{forderungs_text}

Summe: {gesamt:,.2f} Euro brutto

{daten.kanzlei_name}"""
    
    def rsv_deckungsanfrage(self, daten: VorlagenDaten, rsv_name: str = "",
                            rsv_adresse: str = "", versicherungsnummer: str = "",
                            streitgegenstand: str = "") -> str:
        heute = date.today()
        
        return f"""{daten.kanzlei_name}
{daten.kanzlei_anschrift}
{daten.kanzlei_plz_ort}

{rsv_name}
{rsv_adresse}

{heute.strftime('%d.%m.%Y')}

Unser Zeichen: {daten.az_kanzlei}
Versicherungsnummer: {versicherungsnummer}
Versicherungsnehmer: {daten.mandant_name}

Betreff: Deckungsanfrage - Arbeitsrechtsschutz

Sehr geehrte Damen und Herren,

wir zeigen an, dass uns Ihr Versicherungsnehmer {daten.mandant_name} 
mit der Wahrnehmung seiner rechtlichen Interessen beauftragt hat.

Wir bitten um Deckungszusage für folgende Angelegenheit:

1. VERSICHERUNGSNEHMER
   {daten.mandant_name}, {daten.mandant_plz_ort}

2. GEGNER
   {daten.gegner_name}, {daten.gegner_plz_ort}

3. STREITGEGENSTAND
   {streitgegenstand if streitgegenstand else "Kündigungsschutzklage"}

4. SACHVERHALT
   Beschäftigung seit {daten.eintrittsdatum} als {daten.position}.
   [Sachverhaltsdarstellung]

5. ERFOLGSAUSSICHTEN
   Als gut zu bewerten.

6. KOSTENPROGNOSE
   Streitwert: ca. {daten.bruttogehalt} x 3 = [Betrag] Euro

Bitte um kurzfristige Deckungszusage (Klagefrist!).

Mit freundlichen Grüßen
{daten.kanzlei_name}"""


def erstelle_kuendigungsschutzklage(daten: VorlagenDaten) -> str:
    return VorlagenManager().kuendigungsschutzklage(daten)

def erstelle_deckungsanfrage(daten: VorlagenDaten, rsv: str, vnr: str) -> str:
    return VorlagenManager().rsv_deckungsanfrage(daten, rsv, "", vnr)
