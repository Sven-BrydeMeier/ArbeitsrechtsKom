"""
JuraConnect - Kanzlei-Tools
============================
Interne Tools für die Kanzlei
"""

import streamlit as st
from datetime import date, timedelta
import sys
sys.path.insert(0, '..')

from modules.vorlagen import VorlagenManager, VorlagenDaten
from modules.rechner import KuendigungsfristenRechner, ProzesskostenRechner


def render():
    st.title("⚖️ Kanzlei-Tools")
    st.markdown("Interne Werkzeuge für die arbeitsrechtliche Praxis")
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Schriftsätze",
        "📅 Fristenrechner",
        "📬 RSV-Deckung",
        "💼 Aktenanlage",
        "📊 Vergleichsrechner"
    ])
    
    with tab1:
        render_schriftsaetze()
    
    with tab2:
        render_fristenrechner()
    
    with tab3:
        render_rsv_deckung()
    
    with tab4:
        render_aktenanlage()
    
    with tab5:
        render_vergleichsrechner()


def render_schriftsaetze():
    st.header("📝 Schriftsatz-Generator")
    
    schriftsatz_typ = st.selectbox("Schriftsatztyp", [
        "kuendigungsschutzklage",
        "zeugnisklage_erteilung",
        "zeugnisklage_berichtigung",
        "lohnklage",
        "mandantenanschreiben"
    ], format_func=lambda x: {
        "kuendigungsschutzklage": "📋 Kündigungsschutzklage",
        "zeugnisklage_erteilung": "📄 Zeugnisklage (Erteilung)",
        "zeugnisklage_berichtigung": "📄 Zeugnisklage (Berichtigung)",
        "lohnklage": "💰 Lohnklage",
        "mandantenanschreiben": "✉️ Mandantenanschreiben"
    }.get(x, x))
    
    st.divider()
    
    # Gemeinsame Daten
    st.subheader("📋 Mandantendaten")
    col1, col2 = st.columns(2)
    
    with col1:
        mandant_name = st.text_input("Mandant (Name)")
        mandant_anschrift = st.text_input("Straße/Nr.")
        mandant_plz_ort = st.text_input("PLZ/Ort")
    
    with col2:
        mandant_telefon = st.text_input("Telefon")
        mandant_email = st.text_input("E-Mail")
    
    st.subheader("🏢 Gegner")
    col1, col2 = st.columns(2)
    
    with col1:
        gegner_name = st.text_input("Gegner (Name/Firma)")
        gegner_anschrift = st.text_input("Gegner Straße/Nr.")
    
    with col2:
        gegner_plz_ort = st.text_input("Gegner PLZ/Ort")
    
    st.subheader("📂 Aktenzeichen")
    col1, col2 = st.columns(2)
    
    with col1:
        az_kanzlei = st.text_input("Unser Zeichen", value="")
    
    with col2:
        az_gericht = st.text_input("Gericht Az. (falls bekannt)")
    
    # Arbeitsverhältnis-Daten
    st.subheader("💼 Arbeitsverhältnis")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        eintrittsdatum = st.date_input("Eintrittsdatum", value=date.today() - timedelta(days=730))
        position = st.text_input("Position")
    
    with col2:
        austrittsdatum = st.date_input("Austrittsdatum", value=date.today())
        bruttogehalt = st.number_input("Bruttogehalt €", value=3500.0, key="ss_gehalt")
    
    with col3:
        kuendigung_datum = st.date_input("Kündigung vom", value=date.today() - timedelta(days=5))
        kuendigung_zugang = st.date_input("Zugang Kündigung", value=date.today() - timedelta(days=3))
    
    # Kanzleidaten
    st.subheader("⚖️ Kanzleidaten")
    col1, col2 = st.columns(2)
    
    with col1:
        kanzlei_name = st.text_input("Kanzleiname", value="Kanzlei RHM")
        kanzlei_anschrift = st.text_input("Kanzlei Anschrift", value="Musterstraße 1")
        kanzlei_plz_ort = st.text_input("Kanzlei PLZ/Ort", value="12345 Musterstadt")
    
    with col2:
        kanzlei_telefon = st.text_input("Kanzlei Telefon")
        kanzlei_fax = st.text_input("Kanzlei Fax")
        kanzlei_email = st.text_input("Kanzlei E-Mail")
    
    # Typ-spezifische Eingaben
    zusatz_input = None
    forderungen = None
    
    if schriftsatz_typ == "lohnklage":
        st.subheader("💰 Forderungen")
        
        if 'forderungen' not in st.session_state:
            st.session_state.forderungen = []
        
        col1, col2, col3 = st.columns([3, 2, 1])
        with col1:
            ford_beschreibung = st.text_input("Beschreibung", key="ford_beschr")
        with col2:
            ford_betrag = st.number_input("Betrag €", value=0.0, key="ford_betrag")
        with col3:
            if st.button("➕ Hinzufügen"):
                if ford_beschreibung and ford_betrag > 0:
                    st.session_state.forderungen.append({
                        "beschreibung": ford_beschreibung,
                        "betrag": ford_betrag
                    })
        
        if st.session_state.forderungen:
            st.write("**Erfasste Forderungen:**")
            for i, f in enumerate(st.session_state.forderungen):
                st.write(f"- {f['beschreibung']}: {f['betrag']:,.2f} €")
            forderungen = st.session_state.forderungen
    
    elif schriftsatz_typ in ["zeugnisklage_berichtigung"]:
        st.subheader("📄 Zeugnis-Mängel")
        zusatz_input = st.text_area("Mängel des Zeugnisses", height=150)
    
    elif schriftsatz_typ == "kuendigungsschutzklage":
        st.subheader("📋 Klagebegründung")
        zusatz_input = st.text_area("Zusätzliche Klagebegründung", height=150)
    
    elif schriftsatz_typ == "mandantenanschreiben":
        st.subheader("✉️ Anschreiben")
        betreff = st.text_input("Betreff")
        zusatz_input = st.text_area("Inhalt des Anschreibens", height=200)
    
    # Generieren
    if st.button("📝 Schriftsatz generieren", type="primary"):
        # Daten zusammenstellen
        daten = VorlagenDaten(
            mandant_name=mandant_name,
            mandant_anschrift=mandant_anschrift,
            mandant_plz_ort=mandant_plz_ort,
            mandant_telefon=mandant_telefon,
            mandant_email=mandant_email,
            gegner_name=gegner_name,
            gegner_anschrift=gegner_anschrift,
            gegner_plz_ort=gegner_plz_ort,
            kanzlei_name=kanzlei_name,
            kanzlei_anschrift=kanzlei_anschrift,
            kanzlei_plz_ort=kanzlei_plz_ort,
            kanzlei_telefon=kanzlei_telefon,
            kanzlei_fax=kanzlei_fax,
            kanzlei_email=kanzlei_email,
            az_kanzlei=az_kanzlei,
            az_gericht=az_gericht,
            eintrittsdatum=eintrittsdatum.strftime("%d.%m.%Y"),
            austrittsdatum=austrittsdatum.strftime("%d.%m.%Y"),
            bruttogehalt=f"{bruttogehalt:,.2f}",
            position=position,
            kuendigung_datum=kuendigung_datum.strftime("%d.%m.%Y"),
            kuendigung_zugang=kuendigung_zugang.strftime("%d.%m.%Y"),
            kuendigungsfrist_ende=austrittsdatum.strftime("%d.%m.%Y")
        )
        
        manager = VorlagenManager()
        
        if schriftsatz_typ == "kuendigungsschutzklage":
            dokument = manager.kuendigungsschutzklage(daten, zusatz_input or "")
        elif schriftsatz_typ == "zeugnisklage_erteilung":
            dokument = manager.zeugnisklage(daten, "erteilung")
        elif schriftsatz_typ == "zeugnisklage_berichtigung":
            dokument = manager.zeugnisklage(daten, "berichtigung", zusatz_input or "")
        elif schriftsatz_typ == "lohnklage":
            dokument = manager.lohnklage(daten, forderungen)
        elif schriftsatz_typ == "mandantenanschreiben":
            dokument = manager.mandantenanschreiben(daten, betreff if 'betreff' in dir() else "", zusatz_input or "")
        else:
            dokument = "Unbekannter Schriftsatztyp"
        
        st.divider()
        st.subheader("📄 Generierter Schriftsatz")
        st.code(dokument, language=None)
        
        st.download_button(
            "📥 Als Text herunterladen",
            dokument,
            file_name=f"{schriftsatz_typ}_{date.today().isoformat()}.txt",
            mime="text/plain"
        )


def render_fristenrechner():
    st.header("📅 Fristenrechner")
    
    st.subheader("🚨 3-Wochen-Klagefrist (§ 4 KSchG)")
    
    zugang = st.date_input("Zugang der Kündigung", value=date.today())
    
    if st.button("📅 Frist berechnen", type="primary"):
        rechner = KuendigungsfristenRechner()
        ergebnis = rechner.berechne_3_wochen_frist(zugang)
        
        st.divider()
        
        if ergebnis["abgelaufen"]:
            st.error(f"🚨 **FRIST ABGELAUFEN!** Die Frist endete am {ergebnis['fristende'].strftime('%d.%m.%Y')}")
            st.warning(ergebnis["hinweis"])
        elif ergebnis["dringend"]:
            st.warning(f"⚠️ **DRINGEND!** Nur noch **{ergebnis['verbleibende_tage']} Tage** bis zum Fristablauf!")
            st.info(f"Fristende: **{ergebnis['fristende'].strftime('%d.%m.%Y')}**")
        else:
            st.success(f"✅ Fristende: **{ergebnis['fristende'].strftime('%d.%m.%Y')}**")
            st.info(f"Noch {ergebnis['verbleibende_tage']} Tage Zeit")
        
        st.write(ergebnis["hinweis"])
    
    st.divider()
    
    st.subheader("📋 Kündigungsfristen (§ 622 BGB)")
    
    col1, col2 = st.columns(2)
    
    with col1:
        eintritt = st.date_input("Eintrittsdatum", value=date.today() - timedelta(days=1825), key="frist_eintritt")
        kuendigung = st.date_input("Kündigungsdatum", value=date.today(), key="frist_kuend")
    
    with col2:
        ist_ag = st.radio("Wer kündigt?", ["Arbeitgeber", "Arbeitnehmer"])
        probezeit = st.checkbox("Noch in Probezeit")
    
    if st.button("📅 Kündigungsfrist berechnen"):
        rechner = KuendigungsfristenRechner()
        ergebnis = rechner.berechne_frist(
            eintrittsdatum=eintritt,
            kuendigungsdatum=kuendigung,
            ist_arbeitgeber_kuendigung=(ist_ag == "Arbeitgeber"),
            probezeit=probezeit
        )
        
        st.divider()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Kündigungsfrist", ergebnis.frist_text)
        with col2:
            st.metric("Frühester Beendigungstermin", 
                     ergebnis.fruehester_termin.strftime("%d.%m.%Y") if ergebnis.fruehester_termin else "N/A")
        
        st.info(f"Kündigung möglich: **{ergebnis.ende_zum}**")
        
        with st.expander("📋 Details"):
            st.code(ergebnis.berechnung_details)


def render_rsv_deckung():
    st.header("📬 RSV-Deckungsanfrage")
    st.info("Generieren Sie Deckungsanfragen an Rechtsschutzversicherungen")
    
    manager = VorlagenManager()
    
    st.subheader("📋 Mandant")
    col1, col2 = st.columns(2)
    
    with col1:
        mandant_name = st.text_input("Name", key="rsv_mandant")
        mandant_anschrift = st.text_input("Anschrift", key="rsv_anschrift")
        mandant_plz_ort = st.text_input("PLZ/Ort", key="rsv_plz")
    
    with col2:
        position = st.text_input("Position (im AV)", key="rsv_position")
        eintrittsdatum = st.date_input("Eintrittsdatum", key="rsv_eintritt")
    
    st.subheader("🏢 Gegner")
    gegner_name = st.text_input("Arbeitgeber (Name)", key="rsv_gegner")
    gegner_anschrift = st.text_input("Gegner Anschrift", key="rsv_gegner_adr")
    gegner_plz_ort = st.text_input("Gegner PLZ/Ort", key="rsv_gegner_plz")
    
    st.subheader("🛡️ Rechtsschutzversicherung")
    col1, col2 = st.columns(2)
    
    with col1:
        rsv_name = st.text_input("Name der RSV")
        rsv_adresse = st.text_input("Adresse der RSV")
    
    with col2:
        versicherungsnummer = st.text_input("Versicherungsnummer")
    
    st.subheader("📋 Streitgegenstand")
    streitgegenstand = st.text_area("Beschreibung", 
                                     placeholder="z.B. Kündigungsschutzklage, Zeugnisklage, Lohnklage...")
    
    if mandant_name and rsv_name and versicherungsnummer and st.button("📬 Deckungsanfrage generieren", type="primary"):
        daten = VorlagenDaten(
            mandant_name=mandant_name,
            mandant_anschrift=mandant_anschrift,
            mandant_plz_ort=mandant_plz_ort,
            gegner_name=gegner_name,
            gegner_anschrift=gegner_anschrift,
            gegner_plz_ort=gegner_plz_ort,
            position=position,
            eintrittsdatum=eintrittsdatum.strftime("%d.%m.%Y")
        )
        
        dokument = manager.rsv_deckungsanfrage(
            daten,
            rsv_name=rsv_name,
            rsv_adresse=rsv_adresse,
            versicherungsnummer=versicherungsnummer,
            streitgegenstand=streitgegenstand
        )
        
        st.divider()
        st.subheader("📄 Deckungsanfrage")
        st.code(dokument, language=None)
        
        st.download_button(
            "📥 Herunterladen",
            dokument,
            file_name=f"deckungsanfrage_{mandant_name.replace(' ', '_')}_{date.today().isoformat()}.txt"
        )


def render_aktenanlage():
    st.header("💼 Schnelle Aktenanlage")
    st.info("Neue Akte anlegen (vereinfachte Ansicht)")
    
    with st.form("neue_akte"):
        st.subheader("📋 Mandant")
        col1, col2 = st.columns(2)
        
        with col1:
            mandant_anrede = st.selectbox("Anrede", ["Herr", "Frau", "Firma"])
            mandant_vorname = st.text_input("Vorname")
            mandant_nachname = st.text_input("Nachname")
        
        with col2:
            mandant_strasse = st.text_input("Straße")
            mandant_plz = st.text_input("PLZ")
            mandant_ort = st.text_input("Ort")
        
        col1, col2 = st.columns(2)
        with col1:
            mandant_telefon = st.text_input("Telefon", key="akte_tel")
        with col2:
            mandant_email = st.text_input("E-Mail", key="akte_email")
        
        st.subheader("🏢 Gegner")
        col1, col2 = st.columns(2)
        
        with col1:
            gegner_name = st.text_input("Gegner Name/Firma", key="akte_gegner")
        with col2:
            gegner_adresse = st.text_input("Gegner Adresse", key="akte_gegner_adr")
        
        st.subheader("📂 Akte")
        col1, col2 = st.columns(2)
        
        with col1:
            aktenzeichen = st.text_input("Aktenzeichen", value=f"AN-{date.today().strftime('%Y%m%d')}-001")
            sachgebiet = st.selectbox("Sachgebiet", [
                "Kündigungsschutz",
                "Zeugnis",
                "Lohn/Gehalt",
                "Abmahnung",
                "Aufhebungsvertrag",
                "Sonstiges Arbeitsrecht"
            ])
        
        with col2:
            streitwert = st.number_input("Streitwert (geschätzt)", value=0.0)
            rubrum = st.text_input("Rubrum (kurz)", 
                                   placeholder="z.B. Müller ./. Maier GmbH")
        
        notizen = st.text_area("Notizen", height=100)
        
        submitted = st.form_submit_button("💾 Akte anlegen", type="primary")
    
    if submitted:
        # Hier würde normalerweise die Speicherung in der DB erfolgen
        st.success("✅ Akte erfolgreich angelegt!")
        
        st.json({
            "aktenzeichen": aktenzeichen,
            "mandant": f"{mandant_anrede} {mandant_vorname} {mandant_nachname}",
            "gegner": gegner_name,
            "sachgebiet": sachgebiet,
            "streitwert": streitwert,
            "rubrum": rubrum
        })


def render_vergleichsrechner():
    st.header("📊 Vergleichsrechner")
    st.info("Abfindung vs. Weiterbeschäftigung - Was ist günstiger?")
    
    st.subheader("💼 Ausgangssituation")
    col1, col2 = st.columns(2)
    
    with col1:
        bruttogehalt = st.number_input("Bruttogehalt (€/Monat)", value=4000.0, key="vgl_gehalt")
        alter = st.number_input("Alter", min_value=18, max_value=67, value=50, key="vgl_alter")
        betriebszugehoerigkeit = st.number_input("Betriebszugehörigkeit (Jahre)", value=15.0, key="vgl_bz")
    
    with col2:
        steuerklasse = st.selectbox("Steuerklasse", [1, 2, 3, 4, 5, 6])
        kirchensteuer = st.checkbox("Kirchensteuer", value=True)
    
    st.subheader("💰 Vergleichsszenarien")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Szenario A: Abfindung**")
        abfindung_brutto = st.number_input("Abfindung (brutto)", value=bruttogehalt * betriebszugehoerigkeit * 0.5)
        kuendigungsfrist_monate = st.number_input("Bezahlte Kündigungsfrist (Monate)", value=3)
    
    with col2:
        st.markdown("**Szenario B: Weiterbeschäftigung**")
        prozessdauer_monate = st.number_input("Geschätzte Prozessdauer (Monate)", value=6)
        erfolgsaussichten = st.slider("Erfolgsaussichten (%)", 0, 100, 70)
    
    if st.button("📊 Vergleich berechnen", type="primary"):
        st.divider()
        
        # Vereinfachte Berechnung (ohne echte Steuerberechnung)
        # Szenario A
        gehalt_kuendfrist = bruttogehalt * kuendigungsfrist_monate
        gesamt_a = abfindung_brutto + gehalt_kuendfrist
        
        # Geschätzte Steuer auf Abfindung (Fünftelregelung vereinfacht)
        steuersatz_abfindung = 0.25  # Vereinfacht
        abfindung_netto = abfindung_brutto * (1 - steuersatz_abfindung)
        gesamt_a_netto = abfindung_netto + (gehalt_kuendfrist * 0.6)  # Netto ca. 60%
        
        # Szenario B: Bei Erfolg - Nachzahlung
        nachzahlung_bei_erfolg = bruttogehalt * prozessdauer_monate
        erwartungswert_b = nachzahlung_bei_erfolg * (erfolgsaussichten / 100)
        erwartungswert_b_netto = erwartungswert_b * 0.6
        
        # Anzeige
        st.subheader("📊 Ergebnis")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Szenario A: Abfindung")
            st.metric("Abfindung (brutto)", f"{abfindung_brutto:,.2f} €")
            st.metric("+ Gehalt Kündigungsfrist", f"{gehalt_kuendfrist:,.2f} €")
            st.metric("= Gesamt (brutto)", f"{gesamt_a:,.2f} €")
            st.info(f"Geschätzt netto: **{gesamt_a_netto:,.2f} €**")
        
        with col2:
            st.markdown("### Szenario B: Klage")
            st.metric("Nachzahlung bei Erfolg (brutto)", f"{nachzahlung_bei_erfolg:,.2f} €")
            st.metric("× Erfolgswahrscheinlichkeit", f"{erfolgsaussichten}%")
            st.metric("= Erwartungswert (brutto)", f"{erwartungswert_b:,.2f} €")
            st.info(f"Geschätzt netto: **{erwartungswert_b_netto:,.2f} €**")
        
        # Empfehlung
        st.divider()
        if gesamt_a_netto > erwartungswert_b_netto * 1.1:  # 10% Puffer
            st.success(f"💡 **Empfehlung:** Abfindung annehmen - finanziell günstiger um ca. {gesamt_a_netto - erwartungswert_b_netto:,.2f} €")
        elif erwartungswert_b_netto > gesamt_a_netto * 1.1:
            st.warning(f"💡 **Empfehlung:** Klage prüfen - potentiell günstiger um ca. {erwartungswert_b_netto - gesamt_a_netto:,.2f} €")
        else:
            st.info("💡 **Empfehlung:** Beide Optionen finanziell ähnlich - weitere Faktoren berücksichtigen (Prozessrisiko, Zeit, Nerven)")
        
        st.caption("⚠️ Diese Berechnung ist vereinfacht. Für eine genaue Analyse konsultieren Sie einen Steuerberater.")


if __name__ == "__main__":
    render()
