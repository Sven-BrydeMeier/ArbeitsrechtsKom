"""
JuraConnect - Arbeitgeber-Dashboard
====================================
Tools für Arbeitgeber im Arbeitsrecht
"""

import streamlit as st
from datetime import date, timedelta
import sys
sys.path.insert(0, '..')

from modules.arbeitgeber import (
    SozialauswahlRechner, KuendigungsAssistent, AbmahnungsGenerator,
    ArbeitsvertragsGenerator, ComplianceCheckliste, Mitarbeiter,
    KuendigungsgrundAG
)


def render():
    st.title("🏢 Arbeitgeber-Dashboard")
    st.markdown("Tools und Assistenten für Arbeitgeber im Arbeitsrecht")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Kündigungs-Assistent",
        "📊 Sozialauswahl",
        "⚠️ Abmahnung",
        "📝 Arbeitsvertrag",
        "✅ Compliance-Checklisten"
    ])
    
    with tab1:
        render_kuendigungsassistent()
    
    with tab2:
        render_sozialauswahl()
    
    with tab3:
        render_abmahnung()
    
    with tab4:
        render_arbeitsvertrag()
    
    with tab5:
        render_compliance()


def render_kuendigungsassistent():
    st.header("📋 Kündigungs-Assistent")
    st.info("Schritt-für-Schritt durch den Kündigungsprozess")
    
    # Schritt 1: Grunddaten
    st.subheader("1️⃣ Grunddaten")
    
    col1, col2 = st.columns(2)
    with col1:
        kuendigungsgrund = st.selectbox("Kündigungsgrund", [
            ("BETRIEBSBEDINGT", "Betriebsbedingt"),
            ("VERHALTENSBEDINGT", "Verhaltensbedingt"),
            ("PERSONENBEDINGT", "Personenbedingt"),
            ("AUSSERORDENTLICH", "Außerordentlich (fristlos)"),
            ("PROBEZEIT", "Probezeit")
        ], format_func=lambda x: x[1])
        
        mitarbeiter_name = st.text_input("Name des Mitarbeiters")
    
    with col2:
        betriebsrat = st.checkbox("Betriebsrat vorhanden")
        besonderer_schutz = st.selectbox("Besonderer Kündigungsschutz", [
            (None, "Keiner"),
            ("schwerbehindert", "Schwerbehindert"),
            ("schwanger", "Schwanger / Mutterschutz"),
            ("elternzeit", "Elternzeit"),
            ("betriebsrat", "Betriebsratsmitglied"),
            ("datenschutz", "Datenschutzbeauftragter")
        ], format_func=lambda x: x[1])
    
    mitarbeiter_anzahl = st.number_input("Anzahl Mitarbeiter im Betrieb", min_value=1, value=50)
    
    if st.button("📋 Checkliste erstellen", type="primary"):
        assistent = KuendigungsAssistent()
        grund_mapping = {
            "BETRIEBSBEDINGT": KuendigungsgrundAG.BETRIEBSBEDINGT,
            "VERHALTENSBEDINGT": KuendigungsgrundAG.VERHALTENSBEDINGT,
            "PERSONENBEDINGT": KuendigungsgrundAG.PERSONENBEDINGT,
            "AUSSERORDENTLICH": KuendigungsgrundAG.AUSSERORDENTLICH,
            "PROBEZEIT": KuendigungsgrundAG.PROBEZEIT
        }
        
        checkliste = assistent.erstelle_checkliste(
            grund=grund_mapping[kuendigungsgrund[0]],
            hat_betriebsrat=betriebsrat,
            besonderer_schutz=besonderer_schutz[0],
            mitarbeiter_anzahl=mitarbeiter_anzahl
        )
        
        st.divider()
        st.subheader("📋 Ihre Checkliste")
        
        for i, punkt in enumerate(checkliste, 1):
            pflicht_badge = "🔴 Pflicht" if punkt.erforderlich else "🟡 Optional"
            with st.expander(f"{punkt.schritt} [{pflicht_badge}]"):
                st.write(punkt.hinweis)
                if punkt.frist:
                    st.warning(f"⏰ Frist: {punkt.frist.strftime('%d.%m.%Y')}")
                st.checkbox("Erledigt", key=f"check_{i}")
        
        # Betriebsrats-Anhörung generieren
        if betriebsrat and mitarbeiter_name:
            st.divider()
            st.subheader("📄 Betriebsrats-Anhörung (Vorlage)")
            
            details = st.text_area("Kündigungsdetails für BR-Anhörung", 
                                   placeholder="Beschreiben Sie den Sachverhalt...")
            kuendigungsfrist = st.text_input("Kündigungsfrist", value="zum Monatsende")
            
            if st.button("📝 Anhörung generieren"):
                anhoerung = assistent.generiere_anhoerung_betriebsrat(
                    mitarbeiter_name=mitarbeiter_name,
                    grund=grund_mapping[kuendigungsgrund[0]],
                    details=details,
                    kuendigungsfrist=kuendigungsfrist
                )
                st.code(anhoerung, language=None)
                st.download_button("📥 Als Text herunterladen", anhoerung, 
                                   file_name="betriebsrat_anhoerung.txt")


def render_sozialauswahl():
    st.header("📊 Sozialauswahl-Rechner")
    st.info("Berechnen Sie die Sozialpunkte nach dem Punktesystem (BAG-Rechtsprechung)")
    
    st.markdown("""
    **Standardpunktsystem:**
    - **Alter:** 1 Punkt pro Lebensjahr (ab 18, max. 55)
    - **Betriebszugehörigkeit:** 1 Punkt pro Jahr (max. 30)
    - **Unterhaltspflichten:** 4 Punkte pro Person (max. 20)
    - **Schwerbehinderung:** 5 Punkte ab GdB 50, +1 pro 10 GdB darüber
    """)
    
    # Mitarbeiter eingeben
    st.subheader("Mitarbeiter erfassen")
    
    if 'mitarbeiter_liste' not in st.session_state:
        st.session_state.mitarbeiter_liste = []
    
    with st.form("mitarbeiter_form"):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            name = st.text_input("Name")
            geburtsdatum = st.date_input("Geburtsdatum", value=date(1985, 1, 1))
            eintrittsdatum = st.date_input("Eintrittsdatum", value=date(2018, 1, 1))
        
        with col2:
            bruttogehalt = st.number_input("Bruttogehalt", min_value=0.0, value=3500.0)
            unterhalt = st.number_input("Unterhaltsberechtigte", min_value=0, max_value=10, value=0)
        
        with col3:
            schwerbehindert = st.checkbox("Schwerbehindert")
            gdb = st.number_input("GdB", min_value=0, max_value=100, value=50, disabled=not schwerbehindert)
            leistungstraeger = st.checkbox("Leistungsträger (§ 1 III S.2 KSchG)")
        
        if st.form_submit_button("➕ Mitarbeiter hinzufügen"):
            if name:
                ma = Mitarbeiter(
                    name=name,
                    geburtsdatum=geburtsdatum,
                    eintrittsdatum=eintrittsdatum,
                    bruttogehalt=bruttogehalt,
                    unterhaltspflichten=unterhalt,
                    schwerbehindert=schwerbehindert,
                    schwerbehindert_grad=gdb if schwerbehindert else 0,
                    leistungstraeger=leistungstraeger
                )
                st.session_state.mitarbeiter_liste.append(ma)
                st.success(f"✅ {name} hinzugefügt")
    
    # Liste anzeigen
    if st.session_state.mitarbeiter_liste:
        st.subheader(f"📋 Erfasste Mitarbeiter ({len(st.session_state.mitarbeiter_liste)})")
        
        for i, ma in enumerate(st.session_state.mitarbeiter_liste):
            col1, col2, col3 = st.columns([3, 2, 1])
            with col1:
                st.write(f"**{ma.name}** (Alter: {ma.alter}, BZ: {ma.betriebszugehoerigkeit_jahre:.1f} J.)")
            with col2:
                extras = []
                if ma.schwerbehindert:
                    extras.append(f"GdB {ma.schwerbehindert_grad}")
                if ma.leistungstraeger:
                    extras.append("LT")
                st.write(", ".join(extras) if extras else "-")
            with col3:
                if st.button("🗑️", key=f"del_{i}"):
                    st.session_state.mitarbeiter_liste.pop(i)
                    st.rerun()
        
        # Sozialauswahl durchführen
        st.divider()
        anzahl_kuendigungen = st.number_input("Anzahl geplanter Kündigungen", 
                                               min_value=1, 
                                               max_value=len(st.session_state.mitarbeiter_liste),
                                               value=1)
        
        if st.button("📊 Sozialauswahl durchführen", type="primary"):
            rechner = SozialauswahlRechner()
            ergebnisse = rechner.fuehre_sozialauswahl_durch(
                st.session_state.mitarbeiter_liste,
                anzahl_kuendigungen
            )
            
            st.divider()
            st.subheader("📊 Ergebnis der Sozialauswahl")
            
            for erg in ergebnisse:
                if erg.kuendigung_empfohlen:
                    st.error(f"**Rang {erg.rang}: {erg.mitarbeiter}** - {erg.punkte_gesamt} Punkte → Kündigung empfohlen")
                else:
                    st.success(f"**Rang {erg.rang}: {erg.mitarbeiter}** - {erg.punkte_gesamt} Punkte → Höher schutzwürdig")
                
                with st.expander(f"Details {erg.mitarbeiter}"):
                    for kategorie, punkte in erg.punkte_details.items():
                        st.write(f"- {kategorie}: {punkte} Punkte")
                    st.info(erg.begruendung)
        
        if st.button("🗑️ Alle Mitarbeiter löschen"):
            st.session_state.mitarbeiter_liste = []
            st.rerun()


def render_abmahnung():
    st.header("⚠️ Abmahnungs-Generator")
    st.info("Erstellen Sie rechtssichere Abmahnungen")
    
    generator = AbmahnungsGenerator()
    
    col1, col2 = st.columns(2)
    
    with col1:
        mitarbeiter_name = st.text_input("Name des Mitarbeiters", key="abm_name")
        datum_vorfall = st.date_input("Datum des Vorfalls", value=date.today())
    
    with col2:
        grund = st.selectbox("Abmahnungsgrund", [
            ("verspaetung", "Wiederholtes Zuspätkommen"),
            ("arbeitsverweigerung", "Arbeitsverweigerung"),
            ("unentschuldigtes_fehlen", "Unentschuldigtes Fehlen"),
            ("beleidigung", "Beleidigung"),
            ("konkurrenztaetigkeit", "Unerlaubte Konkurrenztätigkeit"),
            ("datenschutz", "Datenschutzverstoß"),
            ("internet_missbrauch", "Private Internetnutzung"),
            ("krankmeldung", "Verspätete Krankmeldung")
        ], format_func=lambda x: x[1])
    
    sachverhalt = st.text_area("Konkreter Sachverhalt", height=150,
                                placeholder="Beschreiben Sie den Vorfall mit Datum, Uhrzeit, Zeugen, etc.:")
    
    if mitarbeiter_name and sachverhalt and st.button("📝 Abmahnung generieren", type="primary"):
        abmahnung = generator.generiere(
            mitarbeiter_name=mitarbeiter_name,
            grund=grund[0],
            sachverhalt=sachverhalt,
            datum_vorfall=datum_vorfall
        )
        
        st.divider()
        st.subheader("📄 Generierte Abmahnung")
        st.code(abmahnung.volltext, language=None)
        
        st.download_button(
            "📥 Als Text herunterladen",
            abmahnung.volltext,
            file_name=f"abmahnung_{mitarbeiter_name.replace(' ', '_')}_{date.today().isoformat()}.txt",
            mime="text/plain"
        )


def render_arbeitsvertrag():
    st.header("📝 Arbeitsvertrags-Generator")
    st.info("Erstellen Sie Arbeitsverträge aus Bausteinen")
    
    generator = ArbeitsvertragsGenerator()
    
    st.subheader("1️⃣ Vertragsparteien")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Arbeitgeber**")
        ag_name = st.text_input("Firmenname", key="ag_name")
        ag_adresse = st.text_input("Adresse", key="ag_adresse")
    
    with col2:
        st.markdown("**Arbeitnehmer**")
        an_name = st.text_input("Name", key="an_name")
        an_geburt = st.date_input("Geburtsdatum", value=date(1990, 1, 1), key="an_geburt")
        an_adresse = st.text_input("Adresse", key="an_adresse")
    
    st.subheader("2️⃣ Vertragsdaten")
    col1, col2 = st.columns(2)
    
    with col1:
        position = st.text_input("Position/Tätigkeit")
        arbeitsort = st.text_input("Arbeitsort", value="[Ort]")
        beginn = st.date_input("Vertragsbeginn", value=date.today())
    
    with col2:
        bruttogehalt = st.number_input("Bruttogehalt (€/Monat)", value=3500.0, key="av_gehalt")
        wochenstunden = st.number_input("Wochenstunden", value=40.0, key="av_stunden")
        urlaubstage = st.number_input("Urlaubstage/Jahr", min_value=20, value=30)
    
    st.subheader("3️⃣ Weitere Regelungen")
    col1, col2 = st.columns(2)
    
    with col1:
        kuendigungsfrist = st.text_input("Kündigungsfrist", value="4 Wochen")
        kuendigungstermin = st.text_input("Kündigungstermin", value="zum 15. oder Monatsende")
        ueberstunden_inkl = st.number_input("Überstunden inkl. im Gehalt", min_value=0, value=10)
    
    with col2:
        bausteine = st.multiselect(
            "Optionale Bausteine",
            [("nebentaetigkeit", "Nebentätigkeitsregelung"),
             ("ausschlussfristen", "Ausschlussfristen")],
            format_func=lambda x: x[1]
        )
    
    if ag_name and an_name and position and st.button("📝 Vertrag generieren", type="primary"):
        # Pflichtbausteine + optionale
        alle_bausteine = generator.get_pflicht_bausteine()
        for b in bausteine:
            alle_bausteine.append(b[0])
        
        # Platzhalter
        platzhalter = {
            "arbeitgeber_name": ag_name,
            "arbeitgeber_adresse": ag_adresse,
            "arbeitnehmer_name": an_name,
            "geburtsdatum": an_geburt.strftime("%d.%m.%Y"),
            "arbeitnehmer_adresse": an_adresse,
            "position": position,
            "arbeitsort": arbeitsort,
            "beginn_datum": beginn.strftime("%d.%m.%Y"),
            "bruttogehalt": f"{bruttogehalt:,.2f}",
            "wochenstunden": str(int(wochenstunden)),
            "urlaubstage": str(urlaubstage),
            "kuendigungsfrist": kuendigungsfrist,
            "kuendigungstermin": kuendigungstermin,
            "ueberstunden_inkl": str(ueberstunden_inkl),
            "ort": arbeitsort.split(",")[0] if "," in arbeitsort else arbeitsort,
            "datum": date.today().strftime("%d.%m.%Y")
        }
        
        vertrag = generator.generiere_vertrag(alle_bausteine, platzhalter)
        
        st.divider()
        st.subheader("📄 Generierter Arbeitsvertrag")
        st.code(vertrag, language=None)
        
        st.download_button(
            "📥 Als Text herunterladen",
            vertrag,
            file_name=f"arbeitsvertrag_{an_name.replace(' ', '_')}.txt",
            mime="text/plain"
        )


def render_compliance():
    st.header("✅ Compliance-Checklisten")
    st.info("Wichtige Checklisten für HR-Compliance")
    
    checklisten = ComplianceCheckliste()
    
    checklisten_info = {
        "neueinstellung": ("👋 Neueinstellung", "Alle Schritte bei Einstellung neuer Mitarbeiter"),
        "kuendigung_durch_ag": ("📤 Kündigung durch AG", "Korrekte Durchführung einer Kündigung"),
        "mutterschutz": ("🤰 Mutterschutz", "Pflichten des AG bei Schwangerschaft"),
        "betriebsrat_wahl": ("🗳️ Betriebsratswahl", "Ablauf einer Betriebsratswahl"),
        "datenschutz_mitarbeiter": ("🔒 Datenschutz Mitarbeiter", "DSGVO-Compliance im HR")
    }
    
    selected = st.selectbox(
        "Checkliste auswählen",
        list(checklisten_info.keys()),
        format_func=lambda x: checklisten_info[x][0]
    )
    
    st.markdown(f"*{checklisten_info[selected][1]}*")
    
    st.divider()
    
    punkte = checklisten.get_checkliste(selected)
    
    st.subheader(f"📋 {checklisten_info[selected][0]}")
    
    for i, (punkt, pflicht) in enumerate(punkte):
        col1, col2, col3 = st.columns([1, 8, 2])
        with col1:
            st.checkbox("", key=f"cl_{selected}_{i}")
        with col2:
            st.write(punkt)
        with col3:
            if pflicht:
                st.error("Pflicht")
            else:
                st.info("Optional")


if __name__ == "__main__":
    render()
