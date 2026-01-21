"""
JuraConnect - Arbeitsrecht-Wiki
================================
Wissensdatenbank mit Rechtsbegriffen, Rechtsprechung und Verfahrenshinweisen.
KI-gestützte Ergänzung mit Anwalts-Freigabe.
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from enum import Enum


class WikiStatus(Enum):
    ENTWURF = "entwurf"           # KI-generiert, nicht freigegeben
    FREIGEGEBEN = "freigegeben"   # Vom Anwalt geprüft
    ARCHIVIERT = "archiviert"     # Veraltet


class WikiKategorie(Enum):
    BEGRIFF = "begriff"
    RECHTSPRECHUNG = "rechtsprechung"
    VERFAHREN = "verfahren"
    KOSTEN = "kosten"
    PRAXISTIPP = "praxistipp"


@dataclass
class WikiEintrag:
    id: str
    titel: str
    kategorie: WikiKategorie
    inhalt: str
    zusammenfassung: str
    schlagworte: List[str]
    rechtsgrundlage: str = ""
    aktenzeichen: str = ""          # Bei Rechtsprechung
    gericht: str = ""               # Bei Rechtsprechung
    datum: str = ""                 # Entscheidungsdatum
    status: WikiStatus = WikiStatus.ENTWURF
    erstellt_von: str = ""
    erstellt_am: str = ""
    freigegeben_von: str = ""
    freigegeben_am: str = ""
    
    def __post_init__(self):
        if not self.erstellt_am:
            self.erstellt_am = datetime.now().isoformat()


class WikiManager:
    """Verwaltet das Arbeitsrecht-Wiki"""
    
    def __init__(self, wiki_file: str = None):
        if wiki_file is None:
            data_dir = Path.home() / ".juraconnect"
            data_dir.mkdir(exist_ok=True)
            self.wiki_file = data_dir / "wiki.json"
        else:
            self.wiki_file = Path(wiki_file)
        
        self._init_default_wiki()
    
    def _init_default_wiki(self):
        """Standard-Wiki-Einträge anlegen"""
        if not self.wiki_file.exists():
            default_entries = self._get_default_entries()
            self._save_wiki(default_entries)
    
    def _get_default_entries(self) -> Dict[str, WikiEintrag]:
        """Vordefinierte Wiki-Einträge"""
        entries = {}
        
        # ========== RECHTSPRECHUNG ==========
        
        # EuGH Urlaubsverfall
        entries["eugh_urlaub_verfall"] = WikiEintrag(
            id="eugh_urlaub_verfall",
            titel="Kein Urlaubsverfall ohne Hinweis des Arbeitgebers",
            kategorie=WikiKategorie.RECHTSPRECHUNG,
            zusammenfassung="Urlaub verfällt nicht automatisch zum Jahresende, wenn der Arbeitgeber den Arbeitnehmer nicht rechtzeitig auf den Resturlaub und dessen drohenden Verfall hingewiesen hat.",
            inhalt="""
## EuGH: Urlaubsverfall nur bei Hinweispflicht

### Leitsatz
Der Anspruch auf bezahlten Jahresurlaub kann am Ende des Bezugszeitraums oder eines Übertragungszeitraums nur dann erlöschen, wenn der Arbeitgeber den Arbeitnehmer tatsächlich in die Lage versetzt hat, diesen Urlaub rechtzeitig zu nehmen.

### Hinweispflicht des Arbeitgebers
Der Arbeitgeber muss:
1. Den Arbeitnehmer **konkret auffordern**, den Urlaub zu nehmen
2. Über den **drohenden Verfall** informieren (am besten schriftlich)
3. Dies **rechtzeitig** tun (spätestens zu Beginn des letzten Quartals)

### Rechtsfolge bei Verstoß
- Urlaub verfällt **nicht** zum 31.12.
- Ansprüche können sich über Jahre ansammeln
- Bei Beendigung: Abgeltungsanspruch

### Praxistipp
Arbeitgeber sollten ein standardisiertes Verfahren einführen:
- Jährliche Urlaubsübersicht an alle MA (Oktober)
- Schriftlicher Hinweis auf Verfall
- Dokumentation der Zustellung
            """,
            schlagworte=["Urlaub", "Verfall", "Hinweispflicht", "EuGH", "Resturlaub"],
            rechtsgrundlage="Art. 7 RL 2003/88/EG, § 7 Abs. 3 BUrlG",
            aktenzeichen="C-619/16, C-684/16",
            gericht="EuGH",
            datum="2018-11-06",
            status=WikiStatus.FREIGEGEBEN,
            erstellt_von="System",
            freigegeben_von="Admin"
        )
        
        # BAG Urlaub bei Krankheit
        entries["bag_urlaub_krankheit"] = WikiEintrag(
            id="bag_urlaub_krankheit",
            titel="Urlaubsanspruch bei Langzeiterkrankung",
            kategorie=WikiKategorie.RECHTSPRECHUNG,
            zusammenfassung="Urlaubsansprüche verfallen bei Langzeiterkrankung erst 15 Monate nach Ende des Urlaubsjahres. Bei kürzerer Krankheit gelten die normalen Übertragungsregeln.",
            inhalt="""
## Urlaub und Krankheit

### Grundsatz (EuGH/BAG)
Kann ein Arbeitnehmer seinen Urlaub wegen Krankheit nicht nehmen, verfällt dieser nicht zum Jahresende.

### 15-Monats-Grenze
- Urlaub verfällt **spätestens 15 Monate** nach Ende des Urlaubsjahres
- Beispiel: Urlaub 2024 verfällt am 31.03.2026
- Dies gilt auch bei durchgehender Arbeitsunfähigkeit

### Wichtige Unterscheidung
| Situation | Verfall |
|-----------|---------|
| Ganzjährig krank | 15 Monate nach Jahresende |
| Teilweise krank | Normale Übertragung (31.03.) |
| Krank zum Jahresende | Übertragung bis 31.03. |

### Bei Beendigung
- Abgeltung aller offenen Urlaubstage
- Keine Kürzung wegen Krankheit
- Verjährung: 3 Jahre ab Fälligkeit
            """,
            schlagworte=["Urlaub", "Krankheit", "Langzeiterkrankung", "15 Monate", "Abgeltung"],
            rechtsgrundlage="§ 7 Abs. 3 BUrlG, § 275 BGB",
            aktenzeichen="9 AZR 353/10",
            gericht="BAG",
            datum="2012-05-07",
            status=WikiStatus.FREIGEGEBEN,
            erstellt_von="System",
            freigegeben_von="Admin"
        )
        
        # Widerruf Weihnachtsgeld
        entries["widerruf_weihnachtsgeld"] = WikiEintrag(
            id="widerruf_weihnachtsgeld",
            titel="Widerruf von Sonderzahlungen (Weihnachtsgeld)",
            kategorie=WikiKategorie.RECHTSPRECHUNG,
            zusammenfassung="Ein Freiwilligkeitsvorbehalt bei Sonderzahlungen ist nur wirksam, wenn er klar formuliert ist und keine widersprüchlichen Regelungen (z.B. Stichtagsklauseln) enthält.",
            inhalt="""
## Widerruf von Sonderzahlungen

### Arten von Vorbehalten
1. **Freiwilligkeitsvorbehalt**: Zahlung erfolgt freiwillig, kein Rechtsanspruch
2. **Widerrufsvorbehalt**: Anspruch besteht, kann aber widerrufen werden

### Unwirksamkeit bei Widerspruch
Ein Freiwilligkeitsvorbehalt ist **unwirksam**, wenn:
- Gleichzeitig Stichtagsklauseln gelten (Widerspruch!)
- Rückzahlungsklauseln bei Kündigung vereinbart sind
- Die Formulierung unklar ist

### BAG-Rechtsprechung
> "Ein Freiwilligkeitsvorbehalt, der im Widerspruch zu anderen Vertragsklauseln steht, ist nach § 307 BGB unwirksam."

### Rechtsfolge
- Bei 3-maliger vorbehaltloser Zahlung: **Betriebliche Übung**
- Anspruch entsteht automatisch
- Widerruf nur noch einvernehmlich möglich

### Praxistipp für Arbeitgeber
- Freiwilligkeitsvorbehalt bei **jeder** Zahlung schriftlich wiederholen
- Keine Stichtagsklauseln kombinieren
- Keine Rückzahlungsvereinbarungen
            """,
            schlagworte=["Weihnachtsgeld", "Sonderzahlung", "Freiwilligkeitsvorbehalt", "Betriebliche Übung"],
            rechtsgrundlage="§ 307 BGB, § 611a BGB",
            aktenzeichen="10 AZR 671/14",
            gericht="BAG",
            datum="2015-09-14",
            status=WikiStatus.FREIGEGEBEN,
            erstellt_von="System",
            freigegeben_von="Admin"
        )
        
        # ========== VERFAHRENSRECHT ==========
        
        entries["arbeitsgericht_verfahren"] = WikiEintrag(
            id="arbeitsgericht_verfahren",
            titel="Das Verfahren vor dem Arbeitsgericht",
            kategorie=WikiKategorie.VERFAHREN,
            zusammenfassung="Das arbeitsgerichtliche Verfahren unterscheidet sich vom Zivilprozess durch schnellere Termine, Güteverhandlung und besondere Kostenregeln.",
            inhalt="""
## Ablauf eines Arbeitsgerichtsprozesses

### 1. Klageeinreichung
- Schriftlich beim zuständigen Arbeitsgericht
- Innerhalb der Fristen (z.B. 3 Wochen bei Kündigungsschutzklage!)
- Gerichtskosten: Erst bei Urteil fällig

### 2. Güteverhandlung (§ 54 ArbGG)
- **Pflichttermin** innerhalb von 2-4 Wochen
- Nur der Vorsitzende Richter (keine Laienrichter)
- Ziel: Einigung/Vergleich
- Ca. 60-70% der Fälle enden hier

### 3. Kammertermin
- Falls keine Einigung
- Vorsitzender + 2 ehrenamtliche Richter (1 AG, 1 AN)
- Beweisaufnahme, Zeugen
- Urteil

### Unterschiede zum Zivilprozess
| Aspekt | Zivilgericht | Arbeitsgericht |
|--------|--------------|----------------|
| Kosten 1. Instanz | Verlierer zahlt alles | Jeder seine Anwaltskosten! |
| Gütetermin | Optional | Pflicht |
| Geschwindigkeit | Monate-Jahre | Wochen-Monate |
| Richterbank | 1-3 Berufsrichter | 1 Berufs- + 2 Laienrichter |

### Rechtsmittel
- **Berufung** zum LAG (Streitwert > 600 € oder zugelassen)
- **Revision** zum BAG (nur bei Zulassung)
            """,
            schlagworte=["Arbeitsgericht", "Verfahren", "Güteverhandlung", "Kammertermin", "Prozess"],
            rechtsgrundlage="§§ 46-72 ArbGG",
            status=WikiStatus.FREIGEGEBEN,
            erstellt_von="System",
            freigegeben_von="Admin"
        )
        
        # Kostenregelung § 12a ArbGG
        entries["kosten_12a_arbgg"] = WikiEintrag(
            id="kosten_12a_arbgg",
            titel="Kostenregelung im Arbeitsrecht (§ 12a ArbGG)",
            kategorie=WikiKategorie.KOSTEN,
            zusammenfassung="In der 1. Instanz trägt jede Partei ihre Anwaltskosten selbst - unabhängig vom Ausgang. Nur Gerichtskosten trägt der Verlierer.",
            inhalt="""
## § 12a ArbGG - Die besondere Kostenregelung

### Grundregel 1. Instanz
> "In Urteilsverfahren des ersten Rechtszugs besteht kein Anspruch der obsiegenden Partei auf Entschädigung wegen Zeitversäumnis und auf Erstattung der Kosten für die Zuziehung eines Prozessbevollmächtigten oder Beistands."

### Was bedeutet das?
- **Jede Partei zahlt ihren eigenen Anwalt** - egal ob gewonnen oder verloren!
- Nur Gerichtskosten zahlt der Verlierer
- Bei Vergleich: Keine Gerichtskosten

### Beispielrechnung (Streitwert 12.000 €)

| Position | Betrag |
|----------|--------|
| Eigene Anwaltskosten | ca. 1.500 € |
| Gegnerische Anwaltskosten | 0 € (keine Erstattung!) |
| Gerichtskosten (bei Urteil) | ca. 500 € |
| **Gesamtrisiko** | **ca. 2.000 €** |

### Ausnahmen (2. Instanz)
Ab dem LAG gelten normale ZPO-Regeln:
- Verlierer zahlt alles
- Auch gegnerische Anwaltskosten

### Praxistipp
Die Kostenregel macht Vergleiche attraktiv:
- Keine Gerichtskosten
- Planbare Kosten
- Schneller Abschluss
            """,
            schlagworte=["Kosten", "§ 12a ArbGG", "Anwaltskosten", "Gerichtskosten", "Prozesskosten"],
            rechtsgrundlage="§ 12a ArbGG",
            status=WikiStatus.FREIGEGEBEN,
            erstellt_von="System",
            freigegeben_von="Admin"
        )
        
        # ========== BEGRIFFE ==========
        
        entries["kuendigungsschutzgesetz"] = WikiEintrag(
            id="kuendigungsschutzgesetz",
            titel="Kündigungsschutzgesetz (KSchG)",
            kategorie=WikiKategorie.BEGRIFF,
            zusammenfassung="Das KSchG schützt Arbeitnehmer vor sozial ungerechtfertigten Kündigungen, wenn das Arbeitsverhältnis länger als 6 Monate besteht und der Betrieb mehr als 10 Mitarbeiter hat.",
            inhalt="""
## Das Kündigungsschutzgesetz

### Anwendungsbereich (§ 1, § 23 KSchG)
Das KSchG gilt, wenn:
1. Arbeitsverhältnis **länger als 6 Monate** besteht
2. Betrieb **mehr als 10 Arbeitnehmer** hat (Vollzeitäquivalente)

### Kündigungsgründe
Eine Kündigung ist nur wirksam bei:
- **Personenbedingten** Gründen (z.B. Krankheit)
- **Verhaltensbedingten** Gründen (z.B. Pflichtverletzung)
- **Betriebsbedingten** Gründen (z.B. Stellenabbau)

### 3-Wochen-Frist (§ 4 KSchG)
- Klage muss **innerhalb 3 Wochen** nach Zugang erhoben werden
- Frist ist **nicht verlängerbar**!
- Versäumnis = Kündigung gilt als wirksam

### Rechtsfolgen
- Unwirksame Kündigung → Arbeitsverhältnis besteht fort
- Weiterbeschäftigungsanspruch
- Annahmeverzugslohn
            """,
            schlagworte=["KSchG", "Kündigungsschutz", "Kündigung", "3-Wochen-Frist", "Sozialauswahl"],
            rechtsgrundlage="KSchG",
            status=WikiStatus.FREIGEGEBEN,
            erstellt_von="System",
            freigegeben_von="Admin"
        )
        
        entries["abmahnung"] = WikiEintrag(
            id="abmahnung",
            titel="Die Abmahnung",
            kategorie=WikiKategorie.BEGRIFF,
            zusammenfassung="Die Abmahnung ist eine formale Rüge des Arbeitgebers und Voraussetzung für eine verhaltensbedingte Kündigung. Sie muss das Fehlverhalten konkret benennen und Konsequenzen androhen.",
            inhalt="""
## Die Abmahnung im Arbeitsrecht

### Definition
Die Abmahnung ist eine Erklärung des Arbeitgebers, mit der er:
1. Ein konkretes **Fehlverhalten rügt**
2. Den Arbeitnehmer zur **Verhaltensänderung auffordert**
3. **Konsequenzen androht** (idR Kündigung)

### Funktionen
- **Hinweisfunktion**: Zeigt dem AN sein Fehlverhalten
- **Warnfunktion**: Droht mit Konsequenzen
- **Dokumentationsfunktion**: Beweissicherung

### Anforderungen
| Element | Erforderlich |
|---------|--------------|
| Konkretes Fehlverhalten | ✅ Ja (Datum, Uhrzeit, Ort) |
| Aufforderung zur Besserung | ✅ Ja |
| Kündigungsandrohung | ✅ Ja |
| Schriftform | ❌ Nein (aber empfohlen) |
| Frist | ❌ Keine gesetzliche |

### Entfernung aus Personalakte
- Nach 2-3 Jahren (BAG)
- Früher bei geringfügigen Verstößen
- Auf Antrag des Arbeitnehmers

### Praxistipp
Arbeitnehmer können Gegendarstellung zur Personalakte geben!
            """,
            schlagworte=["Abmahnung", "Kündigung", "Fehlverhalten", "Personalakte"],
            rechtsgrundlage="Richterrecht, § 314 Abs. 2 BGB analog",
            status=WikiStatus.FREIGEGEBEN,
            erstellt_von="System",
            freigegeben_von="Admin"
        )
        
        entries["betriebsuebergang"] = WikiEintrag(
            id="betriebsuebergang",
            titel="Betriebsübergang (§ 613a BGB)",
            kategorie=WikiKategorie.BEGRIFF,
            zusammenfassung="Bei einem Betriebsübergang gehen alle Arbeitsverhältnisse automatisch auf den neuen Inhaber über. Eine Kündigung wegen des Übergangs ist unwirksam.",
            inhalt="""
## Der Betriebsübergang

### Definition (§ 613a BGB)
Ein Betriebsübergang liegt vor, wenn ein Betrieb oder Betriebsteil durch **Rechtsgeschäft** auf einen neuen Inhaber übergeht und seine **Identität wahrt**.

### Rechtsfolgen
1. **Automatischer Übergang** aller Arbeitsverhältnisse
2. Eintritt in alle Rechte und Pflichten
3. **Kündigungsverbot** wegen des Übergangs
4. Gesamtschuldnerische Haftung (1 Jahr)

### Unterrichtungspflicht
Der Arbeitgeber muss informieren über:
- Zeitpunkt des Übergangs
- Grund des Übergangs
- Rechtliche, wirtschaftliche, soziale Folgen
- Geplante Maßnahmen

### Widerspruchsrecht
- Arbeitnehmer kann **innerhalb 1 Monat** widersprechen
- Arbeitsverhältnis bleibt beim alten AG
- Risiko: Betriebsbedingte Kündigung möglich

### Häufige Fehler
- Unvollständige Unterrichtung → Frist läuft nicht
- Kündigung "wegen" Übergang → Unwirksam
            """,
            schlagworte=["Betriebsübergang", "§ 613a BGB", "Unterrichtung", "Widerspruch"],
            rechtsgrundlage="§ 613a BGB, RL 2001/23/EG",
            status=WikiStatus.FREIGEGEBEN,
            erstellt_von="System",
            freigegeben_von="Admin"
        )
        
        return entries
    
    def _load_wiki(self) -> Dict[str, WikiEintrag]:
        """Wiki aus Datei laden"""
        if not self.wiki_file.exists():
            return {}
        
        with open(self.wiki_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        entries = {}
        for entry_id, entry_data in data.items():
            entry_data['kategorie'] = WikiKategorie(entry_data['kategorie'])
            entry_data['status'] = WikiStatus(entry_data['status'])
            entries[entry_id] = WikiEintrag(**entry_data)
        
        return entries
    
    def _save_wiki(self, entries: Dict[str, WikiEintrag]):
        """Wiki in Datei speichern"""
        data = {}
        for entry_id, entry in entries.items():
            entry_dict = asdict(entry)
            entry_dict['kategorie'] = entry.kategorie.value
            entry_dict['status'] = entry.status.value
            data[entry_id] = entry_dict
        
        with open(self.wiki_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_all_entries(self, kategorie: WikiKategorie = None, 
                        status: WikiStatus = None) -> List[WikiEintrag]:
        """Alle Einträge abrufen, optional gefiltert"""
        entries = self._load_wiki()
        result = list(entries.values())
        
        if kategorie:
            result = [e for e in result if e.kategorie == kategorie]
        if status:
            result = [e for e in result if e.status == status]
        
        return result
    
    def get_entry(self, entry_id: str) -> Optional[WikiEintrag]:
        """Einzelnen Eintrag abrufen"""
        entries = self._load_wiki()
        return entries.get(entry_id)
    
    def search(self, query: str) -> List[WikiEintrag]:
        """Wiki durchsuchen"""
        entries = self._load_wiki()
        query_lower = query.lower()
        
        results = []
        for entry in entries.values():
            if entry.status != WikiStatus.FREIGEGEBEN:
                continue
            
            # In Titel, Zusammenfassung, Inhalt und Schlagworten suchen
            if (query_lower in entry.titel.lower() or
                query_lower in entry.zusammenfassung.lower() or
                query_lower in entry.inhalt.lower() or
                any(query_lower in sw.lower() for sw in entry.schlagworte)):
                results.append(entry)
        
        return results
    
    def create_entry(self, entry: WikiEintrag) -> bool:
        """Neuen Eintrag erstellen"""
        entries = self._load_wiki()
        
        if entry.id in entries:
            return False
        
        entries[entry.id] = entry
        self._save_wiki(entries)
        return True
    
    def update_entry(self, entry_id: str, **kwargs) -> bool:
        """Eintrag aktualisieren"""
        entries = self._load_wiki()
        
        if entry_id not in entries:
            return False
        
        entry = entries[entry_id]
        
        for key, value in kwargs.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        
        entries[entry_id] = entry
        self._save_wiki(entries)
        return True
    
    def approve_entry(self, entry_id: str, approved_by: str) -> bool:
        """Eintrag freigeben"""
        return self.update_entry(
            entry_id,
            status=WikiStatus.FREIGEGEBEN,
            freigegeben_von=approved_by,
            freigegeben_am=datetime.now().isoformat()
        )
    
    def delete_entry(self, entry_id: str) -> bool:
        """Eintrag löschen"""
        entries = self._load_wiki()
        
        if entry_id not in entries:
            return False
        
        del entries[entry_id]
        self._save_wiki(entries)
        return True


# =============================================================================
# KI-gestützte Wiki-Funktionen
# =============================================================================

@dataclass
class WikiFrage:
    """Eine Frage ans Wiki mit KI-Antwort"""
    id: str
    frage: str
    ki_antwort: str
    relevante_eintraege: List[str]
    gestellt_von: str
    gestellt_am: str
    anwalt_antwort: str = ""
    beantwortet_von: str = ""
    beantwortet_am: str = ""
    status: str = "offen"  # offen, beantwortet, archiviert


class WikiFragenManager:
    """Verwaltet Fragen ans Wiki"""
    
    def __init__(self, fragen_file: str = None):
        if fragen_file is None:
            data_dir = Path.home() / ".juraconnect"
            data_dir.mkdir(exist_ok=True)
            self.fragen_file = data_dir / "wiki_fragen.json"
        else:
            self.fragen_file = Path(fragen_file)
        
        if not self.fragen_file.exists():
            self._save_fragen({})
    
    def _load_fragen(self) -> Dict[str, WikiFrage]:
        """Fragen laden"""
        if not self.fragen_file.exists():
            return {}
        
        with open(self.fragen_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {fid: WikiFrage(**fdata) for fid, fdata in data.items()}
    
    def _save_fragen(self, fragen: Dict[str, WikiFrage]):
        """Fragen speichern"""
        data = {fid: asdict(f) for fid, f in fragen.items()}
        
        with open(self.fragen_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def stelle_frage(self, frage: str, gestellt_von: str) -> WikiFrage:
        """Neue Frage stellen und KI-Antwort generieren"""
        wiki = WikiManager()
        
        # Wiki durchsuchen
        relevante = wiki.search(frage)
        
        # KI-Antwort generieren (simuliert)
        ki_antwort = self._generiere_ki_antwort(frage, relevante)
        
        # Frage speichern
        frage_id = f"frage_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        neue_frage = WikiFrage(
            id=frage_id,
            frage=frage,
            ki_antwort=ki_antwort,
            relevante_eintraege=[e.id for e in relevante[:5]],
            gestellt_von=gestellt_von,
            gestellt_am=datetime.now().isoformat()
        )
        
        fragen = self._load_fragen()
        fragen[frage_id] = neue_frage
        self._save_fragen(fragen)
        
        return neue_frage
    
    def _generiere_ki_antwort(self, frage: str, relevante_eintraege: List[WikiEintrag]) -> str:
        """KI-Antwort basierend auf Wiki-Einträgen generieren"""
        if not relevante_eintraege:
            return """⚠️ Zu dieser Frage wurden keine relevanten Wiki-Einträge gefunden.

Die Frage wurde an einen Anwalt zur Beantwortung weitergeleitet.

**Hinweis:** Diese Antwort ist automatisch generiert und ersetzt keine Rechtsberatung."""
        
        # Antwort aus Wiki-Einträgen zusammenstellen
        antwort = f"""📚 **KI-generierte Antwort** (basierend auf {len(relevante_eintraege)} Wiki-Einträgen)

---

"""
        for entry in relevante_eintraege[:3]:
            antwort += f"""### {entry.titel}

{entry.zusammenfassung}

*Rechtsgrundlage: {entry.rechtsgrundlage}*

---

"""
        
        antwort += """
⚠️ **Wichtiger Hinweis:**
Diese Antwort wurde automatisch aus dem Wiki generiert und muss von einem Anwalt geprüft werden.
Sie ersetzt keine individuelle Rechtsberatung.
"""
        
        return antwort
    
    def get_offene_fragen(self) -> List[WikiFrage]:
        """Alle offenen Fragen abrufen"""
        fragen = self._load_fragen()
        return [f for f in fragen.values() if f.status == "offen"]
    
    def beantworte_frage(self, frage_id: str, antwort: str, beantwortet_von: str) -> bool:
        """Frage vom Anwalt beantworten"""
        fragen = self._load_fragen()
        
        if frage_id not in fragen:
            return False
        
        frage = fragen[frage_id]
        frage.anwalt_antwort = antwort
        frage.beantwortet_von = beantwortet_von
        frage.beantwortet_am = datetime.now().isoformat()
        frage.status = "beantwortet"
        
        fragen[frage_id] = frage
        self._save_fragen(fragen)
        return True


# =============================================================================
# Hilfsfunktionen
# =============================================================================

def get_wiki_manager() -> WikiManager:
    """WikiManager aus Session State holen oder erstellen"""
    if 'wiki_manager' not in st.session_state:
        st.session_state.wiki_manager = WikiManager()
    return st.session_state.wiki_manager


def get_fragen_manager() -> WikiFragenManager:
    """WikiFragenManager aus Session State holen oder erstellen"""
    if 'wiki_fragen_manager' not in st.session_state:
        st.session_state.wiki_fragen_manager = WikiFragenManager()
    return st.session_state.wiki_fragen_manager
