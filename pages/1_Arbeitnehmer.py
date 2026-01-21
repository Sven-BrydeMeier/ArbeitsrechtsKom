"""
JuraConnect - Arbeitnehmer-Dashboard
=====================================
Tools und Rechner für Arbeitnehmer
"""

import streamlit as st
from datetime import date, timedelta
import sys
sys.path.insert(0, '..')

from modules.rechner import (
    KuendigungsfristenRechner, AbfindungsRechner, 
    ProzesskostenRechner, UrlaubsRechner, UeberstundenRechner
)
from modules.kuendigungsschutz import KuendigungsschutzPruefer, MandantDaten, Kuendigungsart
from modules.zeugnis_analyse import ZeugnisAnalysator


def render():
    st.title("👷 Arbeitnehmer-Dashboard")
    st.markdown("Tools und Rechner für Arbeitnehmer im Arbeitsrecht")
    
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🚨 Kündigungsschutz-Check",
        "💰 Abfindungsrechner", 
        "📄 Zeugnis-Analyse",
        "⏰ Überstundenrechner",
        "🏖️ Urlaubsrechner",
        "⚖️ Prozesskostenrechner"
    ])
    
    # === TAB 1: Kündigungsschutz-Check ===
    with tab1:
        render_kuendigungsschutz_check()
    
    # === TAB 2: Abfindungsrechner ===
    with tab2:
        render_abfindungsrechner()
    
    # === TAB 3: Zeugnis-Analyse ===
    with tab3:
        render_zeugnis_analyse()
    
    # === TAB 4: Überstundenrechner ===
    with tab4:
        render_ueberstundenrechner()
    
    # === TAB 5: Urlaubsrechner ===
    with tab5:
        render_urlaubsrechner()
    
    # === TAB 6: Prozesskostenrechner ===
    with tab6:
        render_prozesskostenrechner()


def render_kuendigungsschutz_check():
    st.header("🚨 Kündigungsschutz-Schnellcheck")
    st.info("Prüfen Sie Ihre Kündigungsschutzsituation in wenigen Minuten")
    
    with st.form("kuendigungsschutz_form"):
        st.subheader("1️⃣ Persönliche Daten")
        col1, col2 = st.columns(2)
        with col1:
            alter = st.number_input("Ihr Alter", min_value=16, max_value=100, value=35)
            geschlecht = st.selectbox("Geschlecht", ["männlich", "weiblich", "divers"])
        with col2:
            eintrittsdatum = st.date_input("Eintrittsdatum", value=date.today() - timedelta(days=730))
            bruttogehalt = st.number_input("Bruttogehalt (€/Monat)", min_value=0.0, value=3500.0, step=100.0)
        
        st.subheader("2️⃣ Kündigung")
        col1, col2 = st.columns(2)
        with col1:
            kuendigung_zugang = st.date_input("Zugang der Kündigung", value=date.today())
            kuendigung_art = st.selectbox("Art der Kündigung", [
                "ordentlich", "außerordentlich", "Änderungskündigung"
            ])
        with col2:
            kuendigung_schriftlich = st.checkbox("Kündigung war schriftlich", value=True)
            kuendigungsgrund = st.text_input("Genannter Kündigungsgrund (falls bekannt)")
        
        st.subheader("3️⃣ Betrieb")
        col1, col2 = st.columns(2)
        with col1:
            mitarbeiter_anzahl = st.number_input("Anzahl Mitarbeiter im Betrieb", min_value=1, value=50)
            betriebsrat = st.checkbox("Betriebsrat vorhanden")
        with col2:
            betriebsrat_angehoert = st.checkbox("Betriebsrat wurde angehört", disabled=not betriebsrat)
            probezeit = st.checkbox("Noch in Probezeit")
        
        st.subheader("4️⃣ Besonderer Kündigungsschutz")
        col1, col2, col3 = st.columns(3)
        with col1:
            schwerbehindert = st.checkbox("Schwerbehindert")
            schwerbehindert_grad = st.number_input("GdB", min_value=0, max_value=100, value=50, 
                                                    disabled=not schwerbehindert)
        with col2:
            schwanger = st.checkbox("Schwanger")
            elternzeit = st.checkbox("In Elternzeit")
        with col3:
            betriebsratsmitglied = st.checkbox("Betriebsratsmitglied")
            datenschutzbeauftragter = st.checkbox("Datenschutzbeauftragter")
        
        st.subheader("5️⃣ Abmahnungen")
        abmahnung_erhalten = st.checkbox("Abmahnung(en) erhalten")
        anzahl_abmahnungen = st.number_input("Anzahl", min_value=0, value=0, 
                                              disabled=not abmahnung_erhalten)
        
        submitted = st.form_submit_button("🔍 Kündigungsschutz prüfen", type="primary")
    
    if submitted:
        # Art der Kündigung umwandeln
        art_mapping = {
            "ordentlich": Kuendigungsart.ORDENTLICH,
            "außerordentlich": Kuendigungsart.AUSSERORDENTLICH,
            "Änderungskündigung": Kuendigungsart.AENDERUNGSKUENDIGUNG
        }
        
        # Daten erstellen
        daten = MandantDaten(
            alter=alter,
            geschlecht=geschlecht,
            eintrittsdatum=eintrittsdatum,
            bruttogehalt=bruttogehalt,
            wochenstunden=40.0,
            kuendigung_zugang=kuendigung_zugang,
            kuendigung_art=art_mapping.get(kuendigung_art, Kuendigungsart.ORDENTLICH),
            kuendigung_schriftlich=kuendigung_schriftlich,
            kuendigung_begruendung=kuendigungsgrund,
            mitarbeiter_anzahl=mitarbeiter_anzahl,
            betriebsrat_vorhanden=betriebsrat,
            betriebsrat_angehoert=betriebsrat_angehoert,
            schwerbehindert=schwerbehindert,
            schwerbehindert_grad=schwerbehindert_grad,
            schwanger=schwanger,
            elternzeit=elternzeit,
            betriebsratsmitglied=betriebsratsmitglied,
            datenschutzbeauftragter=datenschutzbeauftragter,
            probezeit=probezeit,
            abmahnung_erhalten=abmahnung_erhalten,
            anzahl_abmahnungen=anzahl_abmahnungen,
            kuendigungsgrund_genannt=kuendigungsgrund
        )
        
        # Prüfung durchführen
        pruefer = KuendigungsschutzPruefer()
        ergebnis = pruefer.pruefe(daten)
        
        # Ergebnis anzeigen
        st.divider()
        st.header("📊 Ergebnis der Prüfung")
        
        # Frist-Warnung
        if ergebnis.klagefrist_tage_verbleibend <= 0:
            st.error(f"🚨 **FRIST ABGELAUFEN!** Die 3-Wochen-Klagefrist ist am {ergebnis.klagefrist_bis.strftime('%d.%m.%Y')} abgelaufen!")
        elif ergebnis.klagefrist_tage_verbleibend <= 7:
            st.warning(f"⚠️ **DRINGEND:** Nur noch **{ergebnis.klagefrist_tage_verbleibend} Tage** bis Fristablauf ({ergebnis.klagefrist_bis.strftime('%d.%m.%Y')})!")
        else:
            st.info(f"📅 Klagefrist bis: **{ergebnis.klagefrist_bis.strftime('%d.%m.%Y')}** ({ergebnis.klagefrist_tage_verbleibend} Tage)")
        
        # Erfolgsaussichten
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Erfolgsaussichten", f"{ergebnis.erfolgsaussichten_prozent}%")
        with col2:
            st.metric("KSchG anwendbar", "✅ Ja" if ergebnis.kschg_anwendbar else "❌ Nein")
        with col3:
            schutz_emojis = {
                "absoluter_schutz": "🛡️ Absolut",
                "besonderer_schutz": "🔒 Besonders",
                "allgemeiner_schutz": "✅ Allgemein",
                "kein_schutz": "⚠️ Kein"
            }
            st.metric("Schutzstatus", schutz_emojis.get(ergebnis.schutzstatus.value, "❓"))
        
        # Besonderer Schutz
        if ergebnis.besondere_schutzrechte:
            st.subheader("🛡️ Besondere Schutzrechte")
            for schutz in ergebnis.besondere_schutzrechte:
                st.success(f"**{schutz.art}** ({schutz.gesetz}): {schutz.beschreibung}")
        
        # Formfehler
        if ergebnis.formfehler:
            st.subheader("❌ Erkannte Formfehler")
            for fehler in ergebnis.formfehler:
                severity = "error" if fehler.schwere == "schwer" else "warning"
                if severity == "error":
                    st.error(f"**{fehler.fehler}**: {fehler.rechtsfolge}")
                else:
                    st.warning(f"**{fehler.fehler}**: {fehler.rechtsfolge}")
        
        # Warnungen
        if ergebnis.warnungen:
            st.subheader("⚠️ Wichtige Hinweise")
            for warnung in ergebnis.warnungen:
                st.warning(warnung)
        
        # Nächste Schritte
        st.subheader("📋 Nächste Schritte")
        for schritt in ergebnis.naechste_schritte:
            st.markdown(f"- {schritt}")
        
        # Zusammenfassung
        with st.expander("📄 Vollständige Analyse anzeigen"):
            st.code(ergebnis.zusammenfassung)


def render_abfindungsrechner():
    st.header("💰 Abfindungsrechner")
    st.info("Berechnen Sie Ihre voraussichtliche Abfindung")
    
    col1, col2 = st.columns(2)
    
    with col1:
        bruttogehalt = st.number_input("Bruttogehalt (€/Monat)", min_value=0.0, value=4000.0, step=100.0)
        betriebszugehoerigkeit = st.number_input("Betriebszugehörigkeit (Jahre)", min_value=0.0, value=5.0, step=0.5)
        alter = st.number_input("Alter", min_value=18, max_value=100, value=45)
    
    with col2:
        branche = st.selectbox("Branche", [
            ("sonstige", "Sonstige"),
            ("industrie", "Industrie"),
            ("handel", "Handel"),
            ("dienstleistung", "Dienstleistung"),
            ("it", "IT / Tech"),
            ("finanzen", "Finanzen / Banken"),
            ("gesundheit", "Gesundheitswesen"),
            ("oeffentlicher_dienst", "Öffentlicher Dienst")
        ], format_func=lambda x: x[1])
        
        kuendigungsgrund = st.selectbox("Kündigungsgrund", [
            "betriebsbedingt", "verhaltensbedingt", "personenbedingt"
        ])
        
        sozialauswahl_fehler = st.checkbox("Fehler bei der Sozialauswahl vermutet")
    
    if st.button("💰 Abfindung berechnen", type="primary"):
        from modules.rechner import Kuendigungsgrund
        
        grund_mapping = {
            "betriebsbedingt": Kuendigungsgrund.BETRIEBSBEDINGT,
            "verhaltensbedingt": Kuendigungsgrund.VERHALTENSBEDINGT,
            "personenbedingt": Kuendigungsgrund.PERSONENBEDINGT
        }
        
        rechner = AbfindungsRechner()
        ergebnis = rechner.berechne(
            bruttogehalt=bruttogehalt,
            betriebszugehoerigkeit_jahre=betriebszugehoerigkeit,
            alter=alter,
            branche=branche[0],
            kuendigungsgrund=grund_mapping.get(kuendigungsgrund),
            sozialauswahl_fehler=sozialauswahl_fehler
        )
        
        st.divider()
        st.subheader("📊 Ergebnis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Regelabfindung", f"{ergebnis.regelabfindung:,.2f} €")
        with col2:
            st.metric("Empfehlung", f"{ergebnis.empfehlung:,.2f} €", 
                     delta=f"{ergebnis.empfehlung - ergebnis.regelabfindung:+,.2f} €")
        with col3:
            st.metric("Maximum", f"{ergebnis.maximum:,.2f} €")
        
        st.info(f"**Verhandlungsspanne:** {ergebnis.minimum:,.2f} € - {ergebnis.maximum:,.2f} €")
        
        # Faktoren anzeigen
        with st.expander("📋 Berechnungsfaktoren"):
            for faktor, wert in ergebnis.faktoren.items():
                st.write(f"- {faktor}: {wert}")
            st.code(ergebnis.begruendung)


def render_zeugnis_analyse():
    st.header("📄 Zeugnis-Analyse")
    st.info("Laden Sie Ihr Arbeitszeugnis hoch oder fügen Sie den Text ein")
    
    input_method = st.radio("Eingabemethode", ["Text einfügen", "Datei hochladen"])
    
    zeugnis_text = ""
    
    if input_method == "Text einfügen":
        zeugnis_text = st.text_area("Zeugnistext hier einfügen", height=300,
                                     placeholder="Fügen Sie hier den vollständigen Text Ihres Arbeitszeugnisses ein...")
    else:
        uploaded_file = st.file_uploader("Zeugnis hochladen", type=["txt", "pdf"])
        if uploaded_file:
            if uploaded_file.type == "text/plain":
                zeugnis_text = uploaded_file.read().decode("utf-8")
            else:
                st.warning("PDF-Extraktion erfordert zusätzliche Bibliotheken. Bitte Text manuell einfügen.")
    
    if zeugnis_text and st.button("🔍 Zeugnis analysieren", type="primary"):
        analysator = ZeugnisAnalysator()
        analyse = analysator.analysiere(zeugnis_text)
        
        st.divider()
        st.subheader("📊 Analyse-Ergebnis")
        
        # Gesamtnote
        noten_farben = {1: "🟢", 2: "🟢", 3: "🟡", 4: "🟠", 5: "🔴", 6: "🔴"}
        note_emoji = noten_farben.get(analyse.gesamtnote.value, "⚪")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gesamtnote", f"{note_emoji} {analyse.gesamtnote_text}")
        with col2:
            st.metric("Konfidenz", f"{analyse.konfidenz:.0%}")
        with col3:
            vollst = "✅ Vollständig" if analyse.vollstaendig else "❌ Unvollständig"
            st.metric("Vollständigkeit", vollst)
        
        # Empfehlung
        empf_farben = {
            "akzeptieren": ("success", "✅ Zeugnis kann akzeptiert werden"),
            "nachverhandeln": ("warning", "⚖️ Nachverhandlung empfohlen"),
            "klagen": ("error", "⚠️ Korrektur/Klage prüfen")
        }
        farbe, text = empf_farben.get(analyse.empfehlung, ("info", "Prüfung erforderlich"))
        getattr(st, farbe)(text)
        
        # Probleme
        if analyse.probleme:
            st.subheader("⚠️ Erkannte Probleme")
            for problem in analyse.probleme:
                st.warning(problem)
        
        # Geheimcodes
        if analyse.geheimcodes:
            st.subheader("🔐 Versteckte Botschaften (Geheimcodes)")
            for code in analyse.geheimcodes:
                st.error(f"**'{code['formulierung']}'** → Bedeutet: *{code['versteckte_bedeutung']}*")
        
        # Verbesserungsvorschläge
        if analyse.verbesserungen:
            st.subheader("💡 Verbesserungsvorschläge")
            for verbesserung in analyse.verbesserungen:
                st.info(verbesserung)
        
        # Vollständige Analyse
        with st.expander("📄 Vollständige Analyse"):
            st.code(analyse.zusammenfassung)


def render_ueberstundenrechner():
    st.header("⏰ Überstundenrechner")
    
    col1, col2 = st.columns(2)
    
    with col1:
        bruttogehalt = st.number_input("Bruttogehalt (€/Monat)", min_value=0.0, value=3500.0, step=100.0, key="ue_gehalt")
        wochenstunden = st.number_input("Reguläre Wochenstunden", min_value=1.0, max_value=48.0, value=40.0)
    
    with col2:
        ueberstunden = st.number_input("Anzahl Überstunden", min_value=0.0, value=20.0, step=1.0)
        zuschlag = st.selectbox("Überstundenzuschlag", [
            ("normal", "Kein Zuschlag"),
            ("tariflich_25", "25% Zuschlag"),
            ("tariflich_50", "50% Zuschlag"),
            ("nacht", "Nachtzuschlag 25%"),
            ("sonntag", "Sonntagszuschlag 50%"),
            ("feiertag", "Feiertagszuschlag 100%")
        ], format_func=lambda x: x[1])
    
    if st.button("⏰ Berechnen", type="primary"):
        rechner = UeberstundenRechner()
        ergebnis = rechner.berechne(
            bruttogehalt=bruttogehalt,
            ueberstunden=ueberstunden,
            wochenstunden=wochenstunden,
            zuschlag_art=zuschlag[0]
        )
        
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Stundenlohn", f"{ergebnis.stundenlohn:.2f} €")
        with col2:
            st.metric("Grundvergütung", f"{ergebnis.grundverguetung:.2f} €")
        with col3:
            st.metric("Gesamt (brutto)", f"{ergebnis.gesamt_brutto:.2f} €")
        
        if ergebnis.zuschlag_betrag > 0:
            st.info(f"Zuschlag ({ergebnis.zuschlag_prozent:.0f}%): {ergebnis.zuschlag_betrag:.2f} €")
        
        if ergebnis.verjaehrt_ab:
            st.warning(f"⚠️ Überstunden vor dem {ergebnis.verjaehrt_ab.strftime('%d.%m.%Y')} könnten verjährt sein!")


def render_urlaubsrechner():
    st.header("🏖️ Urlaubsrechner")
    
    col1, col2 = st.columns(2)
    
    with col1:
        jahresurlaub = st.number_input("Jahresurlaub (Tage)", min_value=20, max_value=40, value=30)
        eintrittsdatum = st.date_input("Eintrittsdatum", value=date.today() - timedelta(days=365), key="url_eintritt")
    
    with col2:
        austrittsdatum = st.date_input("Austrittsdatum (leer = kein Austritt)", 
                                        value=None, key="url_austritt")
        bereits_genommen = st.number_input("Bereits genommener Urlaub", min_value=0, max_value=40, value=0)
    
    berechne_abgeltung = st.checkbox("Urlaubsabgeltung berechnen")
    
    if berechne_abgeltung:
        bruttogehalt = st.number_input("Bruttogehalt für Abgeltung", min_value=0.0, value=3500.0, key="url_gehalt")
    
    if st.button("🏖️ Berechnen", type="primary"):
        rechner = UrlaubsRechner()
        ergebnis = rechner.berechne_anteilig(
            jahresurlaub=jahresurlaub,
            eintrittsdatum=eintrittsdatum,
            austrittsdatum=austrittsdatum,
            bereits_genommen=bereits_genommen
        )
        
        st.divider()
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Anteiliger Urlaub", f"{ergebnis.anteiliger_urlaub:.1f} Tage")
        with col2:
            st.metric("Bereits genommen", f"{bereits_genommen} Tage")
        with col3:
            st.metric("Resturlaub", f"{ergebnis.resturlaub:.1f} Tage")
        
        if berechne_abgeltung and ergebnis.resturlaub > 0:
            abgeltung = rechner.berechne_abgeltung(ergebnis.resturlaub, bruttogehalt)
            st.success(f"💰 **Urlaubsabgeltung:** {abgeltung:,.2f} € (brutto)")
        
        with st.expander("📋 Berechnungsdetails"):
            st.code(ergebnis.berechnung)


def render_prozesskostenrechner():
    st.header("⚖️ Prozesskostenrechner")
    st.info("Berechnen Sie die voraussichtlichen Kosten eines Arbeitsgerichtsprozesses")
    
    berechnung_art = st.radio("Streitwert-Berechnung", 
                               ["Manuell eingeben", "Aus Bruttogehalt berechnen"])
    
    if berechnung_art == "Aus Bruttogehalt berechnen":
        bruttogehalt = st.number_input("Bruttogehalt (€/Monat)", min_value=0.0, value=4000.0, step=100.0, key="pk_gehalt")
        monate = st.slider("Anzahl Monatsgehälter (Streitwert)", 1, 6, 3)
        streitwert = bruttogehalt * monate
        st.info(f"Berechneter Streitwert: **{streitwert:,.2f} €**")
    else:
        streitwert = st.number_input("Streitwert (€)", min_value=0.0, value=12000.0, step=500.0)
    
    if st.button("⚖️ Kosten berechnen", type="primary"):
        rechner = ProzesskostenRechner()
        ergebnis = rechner.berechne(streitwert)
        
        st.divider()
        st.subheader("📊 Kostenübersicht")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### Bei Urteil (1. Instanz)")
            st.metric("Gerichtskosten", f"{ergebnis.gerichtskosten:,.2f} €")
            st.metric("Eigene Anwaltskosten", f"{ergebnis.anwaltskosten_eigen:,.2f} €")
            st.metric("**Gesamtrisiko**", f"{ergebnis.gesamt_1_instanz:,.2f} €")
        
        with col2:
            st.markdown("### Bei Vergleich")
            st.metric("Kosten bei Vergleich", f"{ergebnis.mit_vergleich:,.2f} €")
            st.success("✅ Bei Vergleich: Keine Gerichtskosten!")
            st.info("💡 Im Arbeitsrecht trägt jede Partei ihre Anwaltskosten selbst (1. Instanz)")
        
        # Details
        with st.expander("📋 Kostendetails"):
            for bezeichnung, betrag in ergebnis.details.items():
                st.write(f"- {bezeichnung}: {betrag:,.2f} €")


if __name__ == "__main__":
    render()
