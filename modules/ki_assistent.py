"""
JuraConnect - KI-Aktenassistent
================================
Beantwortet Fragen zu Akteninhalten aus der internen Datenbank.
Keine externen Suchen - nur interne Mandantendaten.
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional


@dataclass
class AktenNotiz:
    """Eine Notiz/Dokument in einer Akte"""
    id: str
    akte_id: str
    typ: str  # notiz, schriftsatz, dokument, protokoll, email
    titel: str
    inhalt: str
    erstellt_von: str
    erstellt_am: str
    schlagworte: List[str] = None
    
    def __post_init__(self):
        if self.schlagworte is None:
            self.schlagworte = []


@dataclass
class KIAnfrage:
    """Eine KI-Anfrage zu einer Akte"""
    id: str
    akte_id: str
    frage: str
    antwort: str
    quellen: List[str]  # IDs der verwendeten Notizen
    gestellt_von: str
    gestellt_am: str
    kosten: float = 0.0  # Für Abrechnung


class AktenAssistent:
    """KI-Assistent für Aktenfragen"""
    
    def __init__(self, data_file: str = None):
        if data_file is None:
            data_dir = Path.home() / ".juraconnect"
            data_dir.mkdir(exist_ok=True)
            self.data_file = data_dir / "akten_notizen.json"
        else:
            self.data_file = Path(data_file)
        
        self._init_demo_data()
    
    def _init_demo_data(self):
        """Demo-Daten erstellen"""
        if not self.data_file.exists():
            demo_notizen = {
                # Akte 2024-001-KS (Kündigungsschutz Müller)
                "notiz_001": AktenNotiz(
                    id="notiz_001",
                    akte_id="2024-001-KS",
                    typ="notiz",
                    titel="Erstgespräch mit Mandant",
                    inhalt="""
Mandant Max Müller, 45 Jahre, seit 15.03.2018 bei TechCorp GmbH beschäftigt.
Position: Senior Developer, Bruttogehalt 5.500 €/Monat.
Kündigung erhalten am 10.01.2024, ordentlich zum 31.03.2024.
Kündigungsgrund lt. AG: Betriebsbedingt wegen Restrukturierung.
Betriebsrat wurde angehört (Schreiben vom 05.01.2024).
Mandant bestreitet betriebsbedingte Gründe - keine erkennbare Auftragsreduzierung.
Sozialauswahl zweifelhaft: Kollege Schmidt (32 J., ledig, 3 Jahre BZ) bleibt.
Ziel: Kündigungsschutzklage, ggf. Abfindung.
                    """,
                    erstellt_von="RA Mustermann",
                    erstellt_am="2024-01-12T10:30:00",
                    schlagworte=["Erstgespräch", "Kündigung", "Betriebsbedingt", "Sozialauswahl"]
                ),
                "notiz_002": AktenNotiz(
                    id="notiz_002",
                    akte_id="2024-001-KS",
                    typ="dokument",
                    titel="Kündigungsschreiben",
                    inhalt="""
Kündigung vom 08.01.2024, Zugang 10.01.2024.
"...kündigen wir das mit Ihnen bestehende Arbeitsverhältnis ordentlich 
unter Einhaltung der vertraglichen Kündigungsfrist zum 31.03.2024.
Grund: Notwendige Restrukturierungsmaßnahmen machen den Wegfall Ihres 
Arbeitsplatzes erforderlich..."
Unterschrift: Geschäftsführer Dr. Meier
Betriebsratsanhörung beigefügt, Stellungnahme: "Widerspruch"
                    """,
                    erstellt_von="System",
                    erstellt_am="2024-01-12T10:35:00",
                    schlagworte=["Kündigung", "Dokument", "Betriebsrat"]
                ),
                "notiz_003": AktenNotiz(
                    id="notiz_003",
                    akte_id="2024-001-KS",
                    typ="protokoll",
                    titel="Gütetermin 25.01.2024",
                    inhalt="""
Gütetermin vor dem ArbG Frankfurt, Az. 5 Ca 123/24
Anwesend: Kläger mit RA Mustermann, Beklagte mit RA Schmidt
Gericht regt Vergleich an.
Beklagte bietet: 0,5 Gehälter pro Jahr = 16.500 €
Unser Gegenvorschlag: 1,0 Gehälter pro Jahr = 33.000 €
Keine Einigung. Kammertermin: 15.03.2024, 10:00 Uhr
Hinweis Gericht: Sozialauswahl erscheint problematisch.
                    """,
                    erstellt_von="RA Mustermann",
                    erstellt_am="2024-01-25T14:00:00",
                    schlagworte=["Gütetermin", "Vergleich", "Abfindung"]
                ),
                
                # Akte 2024-002-Z (Zeugnis Schmidt)
                "notiz_004": AktenNotiz(
                    id="notiz_004",
                    akte_id="2024-002-Z",
                    typ="notiz",
                    titel="Mandantenaufnahme",
                    inhalt="""
Mandantin Anna Schmidt, 38 Jahre.
Arbeitsverhältnis bei Handel AG beendet zum 31.12.2023.
Arbeitszeugnis erhalten, aber unzufrieden.
Probleme:
- Leistungsbeurteilung nur "zur Zufriedenheit" (Note 3-4)
- Verhaltensbeurteilung: "war stets bemüht" (versteckte Kritik!)
- Schlussformel fehlt Dank und Bedauern
- Kein Wunsch für die Zukunft
Ziel: Zeugnisberichtigung auf Note 2
                    """,
                    erstellt_von="RA Mustermann",
                    erstellt_am="2024-01-22T09:00:00",
                    schlagworte=["Zeugnis", "Berichtigung", "Zeugnissprache"]
                ),
                "notiz_005": AktenNotiz(
                    id="notiz_005",
                    akte_id="2024-002-Z",
                    typ="schriftsatz",
                    titel="Aufforderungsschreiben an AG",
                    inhalt="""
Schreiben vom 23.01.2024 an Handel AG:
- Darlegung der Mängel im Zeugnis
- Formulierungsvorschläge für Note 2
- Fristsetzung: 14 Tage
- Androhung Zeugnisklage
Zustellung per beA und Einschreiben.
                    """,
                    erstellt_von="RA Mustermann",
                    erstellt_am="2024-01-23T11:00:00",
                    schlagworte=["Aufforderung", "Frist", "beA"]
                ),
            }
            self._save_notizen(demo_notizen)
    
    def _load_notizen(self) -> Dict[str, AktenNotiz]:
        """Notizen laden"""
        if not self.data_file.exists():
            return {}
        
        with open(self.data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return {nid: AktenNotiz(**ndata) for nid, ndata in data.items()}
    
    def _save_notizen(self, notizen: Dict[str, AktenNotiz]):
        """Notizen speichern"""
        data = {nid: asdict(n) for nid, n in notizen.items()}
        
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_notizen_fuer_akte(self, akte_id: str) -> List[AktenNotiz]:
        """Alle Notizen einer Akte abrufen"""
        notizen = self._load_notizen()
        return [n for n in notizen.values() if n.akte_id == akte_id]
    
    def suche_in_akte(self, akte_id: str, query: str) -> List[AktenNotiz]:
        """In einer Akte suchen"""
        notizen = self.get_notizen_fuer_akte(akte_id)
        query_lower = query.lower()
        
        results = []
        for notiz in notizen:
            if (query_lower in notiz.titel.lower() or
                query_lower in notiz.inhalt.lower() or
                any(query_lower in sw.lower() for sw in notiz.schlagworte)):
                results.append(notiz)
        
        return results
    
    def suche_global(self, query: str) -> List[AktenNotiz]:
        """In allen Akten suchen"""
        notizen = self._load_notizen()
        query_lower = query.lower()
        
        results = []
        for notiz in notizen.values():
            if (query_lower in notiz.titel.lower() or
                query_lower in notiz.inhalt.lower() or
                any(query_lower in sw.lower() for sw in notiz.schlagworte)):
                results.append(notiz)
        
        return results
    
    def beantworte_frage(self, frage: str, akte_id: str = None, 
                         gestellt_von: str = "System") -> KIAnfrage:
        """
        Beantwortet eine Frage basierend auf Akteninhalt.
        Keine externe Suche - nur interne Daten!
        """
        # Relevante Notizen finden
        if akte_id:
            relevante = self.suche_in_akte(akte_id, frage)
        else:
            relevante = self.suche_global(frage)
        
        # Antwort generieren
        antwort = self._generiere_antwort(frage, relevante, akte_id)
        
        # Anfrage erstellen
        anfrage = KIAnfrage(
            id=f"ki_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            akte_id=akte_id or "global",
            frage=frage,
            antwort=antwort,
            quellen=[n.id for n in relevante],
            gestellt_von=gestellt_von,
            gestellt_am=datetime.now().isoformat(),
            kosten=self._berechne_kosten(len(relevante))
        )
        
        return anfrage
    
    def _generiere_antwort(self, frage: str, notizen: List[AktenNotiz], 
                           akte_id: str = None) -> str:
        """Antwort aus Aktennotizen generieren"""
        if not notizen:
            return """❌ **Keine relevanten Informationen gefunden**

In den Akten wurden keine Einträge gefunden, die Ihre Frage beantworten könnten.

**Mögliche Gründe:**
- Die Information ist noch nicht erfasst
- Andere Suchbegriffe könnten helfen
- Die Frage bezieht sich auf externe Informationen

*Hinweis: Der KI-Assistent durchsucht nur interne Akteninhalte, keine externen Quellen.*"""
        
        # Antwort zusammenstellen
        antwort = f"""📁 **Antwort basierend auf {len(notizen)} Akteneinträgen**

---

"""
        
        for notiz in notizen[:5]:
            antwort += f"""### 📄 {notiz.titel}
*({notiz.typ.capitalize()} vom {notiz.erstellt_am[:10]})*

{notiz.inhalt[:500]}{'...' if len(notiz.inhalt) > 500 else ''}

---

"""
        
        antwort += """
⚠️ **Hinweis:** Diese Zusammenfassung wurde automatisch aus den Akteninhalten generiert.
Sie basiert ausschließlich auf internen Daten - keine externen Quellen wurden verwendet.
"""
        
        return antwort
    
    def _berechne_kosten(self, anzahl_quellen: int) -> float:
        """Kosten für KI-Anfrage berechnen (für Abrechnung)"""
        # Beispiel: 5€ Grundgebühr + 2€ pro Quelle
        return 5.0 + (anzahl_quellen * 2.0)
    
    def notiz_hinzufuegen(self, notiz: AktenNotiz) -> bool:
        """Neue Notiz zu einer Akte hinzufügen"""
        notizen = self._load_notizen()
        
        if notiz.id in notizen:
            return False
        
        notizen[notiz.id] = notiz
        self._save_notizen(notizen)
        return True
    
    def get_alle_akten_ids(self) -> List[str]:
        """Alle Akten-IDs abrufen, die Notizen haben"""
        notizen = self._load_notizen()
        return list(set(n.akte_id for n in notizen.values()))


# =============================================================================
# Streamlit-Komponente
# =============================================================================

def render_ki_assistent(akte_id: str = None):
    """KI-Assistent Widget für Streamlit"""
    
    st.markdown("### 🤖 KI-Aktenassistent")
    
    if akte_id:
        st.info(f"Durchsucht: Akte **{akte_id}**")
    else:
        st.info("Durchsucht: **Alle Akten**")
    
    assistent = AktenAssistent()
    
    # Frage-Eingabe
    frage = st.text_input(
        "Ihre Frage an den Aktenassistenten:",
        placeholder="z.B. 'Wann war der Gütetermin?' oder 'Was ist der Kündigungsgrund?'"
    )
    
    col1, col2 = st.columns([1, 3])
    with col1:
        suchen = st.button("🔍 Fragen", type="primary")
    
    if suchen and frage:
        with st.spinner("Durchsuche Akten..."):
            # Anfrage stellen
            from modules.auth import get_current_user
            user = get_current_user()
            username = user.name if user else "Unbekannt"
            
            anfrage = assistent.beantworte_frage(frage, akte_id, username)
            
            # Antwort anzeigen
            st.markdown(anfrage.antwort)
            
            # Kosten anzeigen
            st.caption(f"💰 Kosten dieser Anfrage: {anfrage.kosten:.2f} €")
            
            # Zur Abrechnung hinzufügen
            from modules.abrechnung import AbrechnungsManager
            abrechnungs_mgr = AbrechnungsManager()
            abrechnungs_mgr.erfasse_leistung(
                akte_id=akte_id or "allgemein",
                leistung="KI-Aktenrecherche",
                beschreibung=f"Frage: {frage[:50]}...",
                betrag=anfrage.kosten,
                erstellt_von=username
            )
    
    # Verfügbare Notizen anzeigen
    with st.expander("📋 Verfügbare Akteneinträge"):
        if akte_id:
            notizen = assistent.get_notizen_fuer_akte(akte_id)
        else:
            notizen = list(assistent._load_notizen().values())[:10]
        
        if notizen:
            for notiz in notizen:
                st.markdown(f"- **{notiz.titel}** ({notiz.typ}, {notiz.erstellt_am[:10]})")
        else:
            st.write("Keine Einträge vorhanden.")


def get_akten_assistent() -> AktenAssistent:
    """AktenAssistent aus Session State holen"""
    if 'akten_assistent' not in st.session_state:
        st.session_state.akten_assistent = AktenAssistent()
    return st.session_state.akten_assistent
