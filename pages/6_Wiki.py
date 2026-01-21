"""
JuraConnect - Arbeitsrecht-Wiki
================================
Wissensdatenbank mit Rechtsbegriffen, Rechtsprechung und KI-Assistent
"""

import streamlit as st
from datetime import datetime
import sys
sys.path.insert(0, '..')

from modules.wiki import (
    WikiManager, WikiFragenManager, WikiEintrag, WikiFrage,
    WikiKategorie, WikiStatus, get_wiki_manager, get_fragen_manager
)
from modules.ki_assistent import render_ki_assistent, AktenAssistent
from modules.auth import (
    init_session_state, is_authenticated, get_current_user, is_demo_mode,
    render_user_menu, render_demo_banner, can_admin, has_role,
    UserRole, FULL_ACCESS
)


def render():
    init_session_state()
    
    st.title("📚 Arbeitsrecht-Wiki")
    st.markdown("Wissensdatenbank mit Rechtsbegriffen, Rechtsprechung und KI-Assistent")
    
    render_demo_banner()
    render_user_menu()
    
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "🔍 Suche",
        "📖 Rechtsprechung",
        "📝 Begriffe",
        "⚖️ Verfahrensrecht",
        "🤖 KI-Assistent"
    ])
    
    with tab1:
        render_suche()
    
    with tab2:
        render_rechtsprechung()
    
    with tab3:
        render_begriffe()
    
    with tab4:
        render_verfahrensrecht()
    
    with tab5:
        render_ki_bereich()


def render_suche():
    st.header("🔍 Wiki durchsuchen")
    
    wiki = get_wiki_manager()
    
    query = st.text_input(
        "Suchbegriff eingeben",
        placeholder="z.B. 'Urlaub', 'Kündigung', 'EuGH'..."
    )
    
    if query:
        results = wiki.search(query)
        
        if results:
            st.success(f"✅ {len(results)} Treffer gefunden")
            
            for entry in results:
                kategorie_icons = {
                    WikiKategorie.RECHTSPRECHUNG: "⚖️",
                    WikiKategorie.BEGRIFF: "📝",
                    WikiKategorie.VERFAHREN: "🏛️",
                    WikiKategorie.KOSTEN: "💰",
                    WikiKategorie.PRAXISTIPP: "💡"
                }
                icon = kategorie_icons.get(entry.kategorie, "📄")
                
                with st.expander(f"{icon} **{entry.titel}**"):
                    st.markdown(f"*{entry.zusammenfassung}*")
                    st.markdown("---")
                    st.markdown(entry.inhalt)
                    
                    if entry.rechtsgrundlage:
                        st.caption(f"📜 Rechtsgrundlage: {entry.rechtsgrundlage}")
                    if entry.aktenzeichen:
                        st.caption(f"📋 Az.: {entry.aktenzeichen} ({entry.gericht})")
                    
                    st.caption(f"🏷️ Schlagworte: {', '.join(entry.schlagworte)}")
        else:
            st.warning("Keine Treffer gefunden. Versuchen Sie andere Suchbegriffe.")
            
            # Frage an Anwalt weiterleiten
            st.markdown("---")
            st.markdown("### ❓ Frage an Anwalt stellen")
            
            if st.button("Diese Frage an einen Anwalt weiterleiten"):
                fragen_mgr = get_fragen_manager()
                user = get_current_user()
                username = user.name if user else "Anonym"
                
                frage = fragen_mgr.stelle_frage(query, username)
                st.success("✅ Ihre Frage wurde weitergeleitet!")
                st.info(frage.ki_antwort)


def render_rechtsprechung():
    st.header("⚖️ Wichtige Rechtsprechung")
    
    wiki = get_wiki_manager()
    entries = wiki.get_all_entries(
        kategorie=WikiKategorie.RECHTSPRECHUNG,
        status=WikiStatus.FREIGEGEBEN
    )
    
    if not entries:
        st.info("Noch keine Rechtsprechung im Wiki.")
        return
    
    # Nach Gericht gruppieren
    gerichte = {}
    for entry in entries:
        gericht = entry.gericht or "Sonstige"
        if gericht not in gerichte:
            gerichte[gericht] = []
        gerichte[gericht].append(entry)
    
    for gericht, gericht_entries in gerichte.items():
        st.subheader(f"🏛️ {gericht}")
        
        for entry in gericht_entries:
            with st.expander(f"**{entry.titel}** ({entry.datum[:4] if entry.datum else 'o.D.'})"):
                st.markdown(f"**Aktenzeichen:** {entry.aktenzeichen}")
                st.markdown(f"**Leitsatz:** {entry.zusammenfassung}")
                st.markdown("---")
                st.markdown(entry.inhalt)
                st.caption(f"📜 {entry.rechtsgrundlage}")


def render_begriffe():
    st.header("📝 Rechtsbegriffe")
    
    wiki = get_wiki_manager()
    entries = wiki.get_all_entries(
        kategorie=WikiKategorie.BEGRIFF,
        status=WikiStatus.FREIGEGEBEN
    )
    
    if not entries:
        st.info("Noch keine Begriffe im Wiki.")
        return
    
    # Alphabetisch sortieren
    entries_sorted = sorted(entries, key=lambda x: x.titel.lower())
    
    # Buchstaben-Navigation
    buchstaben = sorted(set(e.titel[0].upper() for e in entries_sorted))
    selected_buchstabe = st.selectbox("Anfangsbuchstabe", ["Alle"] + buchstaben)
    
    for entry in entries_sorted:
        if selected_buchstabe != "Alle" and not entry.titel.upper().startswith(selected_buchstabe):
            continue
        
        with st.expander(f"**{entry.titel}**"):
            st.markdown(f"*{entry.zusammenfassung}*")
            st.markdown("---")
            st.markdown(entry.inhalt)
            st.caption(f"📜 {entry.rechtsgrundlage}")


def render_verfahrensrecht():
    st.header("🏛️ Verfahrensrecht & Kosten")
    
    wiki = get_wiki_manager()
    
    # Verfahrenshinweise
    st.subheader("⚖️ Verfahrensablauf")
    verfahren_entries = wiki.get_all_entries(
        kategorie=WikiKategorie.VERFAHREN,
        status=WikiStatus.FREIGEGEBEN
    )
    
    for entry in verfahren_entries:
        with st.expander(f"**{entry.titel}**"):
            st.markdown(entry.inhalt)
            st.caption(f"📜 {entry.rechtsgrundlage}")
    
    # Kostenhinweise
    st.subheader("💰 Kosten")
    kosten_entries = wiki.get_all_entries(
        kategorie=WikiKategorie.KOSTEN,
        status=WikiStatus.FREIGEGEBEN
    )
    
    for entry in kosten_entries:
        with st.expander(f"**{entry.titel}**"):
            st.markdown(entry.inhalt)
            st.caption(f"📜 {entry.rechtsgrundlage}")


def render_ki_bereich():
    st.header("🤖 KI-Assistent")
    
    st.markdown("""
    Der KI-Assistent kann Ihnen auf zwei Arten helfen:
    
    1. **Wiki-Fragen**: Fragen zum Arbeitsrecht basierend auf dem Wiki
    2. **Akten-Fragen**: Fragen zu Ihren Mandantenakten (nur interne Daten)
    """)
    
    assistant_mode = st.radio(
        "Modus auswählen",
        ["📚 Wiki-Fragen", "📁 Akten-Fragen"]
    )
    
    if assistant_mode == "📚 Wiki-Fragen":
        render_wiki_fragen()
    else:
        render_akten_fragen()


def render_wiki_fragen():
    st.subheader("📚 Fragen zum Arbeitsrecht")
    
    frage = st.text_area(
        "Ihre Frage",
        placeholder="z.B. 'Wann verfällt mein Urlaubsanspruch?' oder 'Was muss bei einer Kündigung beachtet werden?'"
    )
    
    if st.button("🤖 Frage stellen", type="primary") and frage:
        with st.spinner("Durchsuche Wiki..."):
            fragen_mgr = get_fragen_manager()
            user = get_current_user()
            username = user.name if user else "Anonym"
            
            antwort = fragen_mgr.stelle_frage(frage, username)
            
            st.markdown("### 📝 Antwort")
            st.markdown(antwort.ki_antwort)
            
            if antwort.relevante_eintraege:
                st.markdown("### 📚 Verwendete Quellen")
                wiki = get_wiki_manager()
                for entry_id in antwort.relevante_eintraege[:3]:
                    entry = wiki.get_entry(entry_id)
                    if entry:
                        st.markdown(f"- {entry.titel}")
    
    # Offene Fragen für Anwälte
    if has_role(FULL_ACCESS):
        st.markdown("---")
        st.subheader("❓ Offene Fragen (für Anwälte)")
        
        fragen_mgr = get_fragen_manager()
        offene = fragen_mgr.get_offene_fragen()
        
        if offene:
            for frage in offene:
                with st.expander(f"**{frage.frage[:50]}...** ({frage.gestellt_am[:10]})"):
                    st.markdown(f"**Von:** {frage.gestellt_von}")
                    st.markdown("**KI-Antwort:**")
                    st.markdown(frage.ki_antwort)
                    
                    st.markdown("---")
                    anwalt_antwort = st.text_area(
                        "Ihre Antwort/Ergänzung",
                        key=f"antwort_{frage.id}"
                    )
                    
                    if st.button("✅ Beantworten", key=f"btn_{frage.id}"):
                        user = get_current_user()
                        fragen_mgr.beantworte_frage(
                            frage.id, 
                            anwalt_antwort,
                            user.name if user else "Anwalt"
                        )
                        st.success("✅ Antwort gespeichert!")
                        st.rerun()
        else:
            st.info("Keine offenen Fragen.")


def render_akten_fragen():
    st.subheader("📁 Fragen zu Akten")
    
    st.warning("""
    ⚠️ **Hinweis:** Der Akten-Assistent durchsucht **nur interne Daten**.
    Es werden keine externen Quellen verwendet.
    """)
    
    # Akte auswählen
    assistent = AktenAssistent()
    akten_ids = assistent.get_alle_akten_ids()
    
    if not akten_ids:
        st.info("Keine Akten mit Einträgen vorhanden.")
        return
    
    selected_akte = st.selectbox(
        "Akte auswählen",
        ["Alle Akten"] + akten_ids
    )
    
    akte_id = None if selected_akte == "Alle Akten" else selected_akte
    
    # KI-Assistent Widget
    render_ki_assistent(akte_id)


# =============================================================================
# Wiki-Verwaltung (nur für Anwälte/Admins)
# =============================================================================

def render_wiki_verwaltung():
    """Zusätzliche Verwaltungsfunktionen für Anwälte"""
    if not has_role(FULL_ACCESS):
        return
    
    st.markdown("---")
    st.subheader("🔧 Wiki-Verwaltung")
    
    wiki = get_wiki_manager()
    
    # Entwürfe anzeigen
    entwuerfe = wiki.get_all_entries(status=WikiStatus.ENTWURF)
    
    if entwuerfe:
        st.warning(f"📝 {len(entwuerfe)} Einträge zur Freigabe")
        
        for entry in entwuerfe:
            with st.expander(f"📝 {entry.titel} (Entwurf)"):
                st.markdown(entry.inhalt)
                
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Freigeben", key=f"approve_{entry.id}"):
                        user = get_current_user()
                        wiki.approve_entry(entry.id, user.name if user else "Admin")
                        st.success("✅ Freigegeben!")
                        st.rerun()
                with col2:
                    if st.button("🗑️ Löschen", key=f"delete_{entry.id}"):
                        wiki.delete_entry(entry.id)
                        st.success("🗑️ Gelöscht!")
                        st.rerun()
    
    # Neuen Eintrag erstellen
    with st.expander("➕ Neuen Wiki-Eintrag erstellen"):
        with st.form("neuer_eintrag"):
            titel = st.text_input("Titel")
            kategorie = st.selectbox("Kategorie", [
                (WikiKategorie.BEGRIFF, "📝 Begriff"),
                (WikiKategorie.RECHTSPRECHUNG, "⚖️ Rechtsprechung"),
                (WikiKategorie.VERFAHREN, "🏛️ Verfahren"),
                (WikiKategorie.KOSTEN, "💰 Kosten"),
                (WikiKategorie.PRAXISTIPP, "💡 Praxistipp")
            ], format_func=lambda x: x[1])
            
            zusammenfassung = st.text_area("Zusammenfassung (kurz)")
            inhalt = st.text_area("Inhalt (Markdown möglich)", height=300)
            
            col1, col2 = st.columns(2)
            with col1:
                rechtsgrundlage = st.text_input("Rechtsgrundlage")
            with col2:
                schlagworte = st.text_input("Schlagworte (kommagetrennt)")
            
            # Bei Rechtsprechung
            if kategorie[0] == WikiKategorie.RECHTSPRECHUNG:
                col1, col2, col3 = st.columns(3)
                with col1:
                    aktenzeichen = st.text_input("Aktenzeichen")
                with col2:
                    gericht = st.text_input("Gericht")
                with col3:
                    datum = st.date_input("Entscheidungsdatum")
            else:
                aktenzeichen = ""
                gericht = ""
                datum = None
            
            if st.form_submit_button("💾 Speichern", type="primary"):
                if titel and inhalt:
                    user = get_current_user()
                    
                    entry = WikiEintrag(
                        id=f"wiki_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                        titel=titel,
                        kategorie=kategorie[0],
                        zusammenfassung=zusammenfassung,
                        inhalt=inhalt,
                        schlagworte=[s.strip() for s in schlagworte.split(",") if s.strip()],
                        rechtsgrundlage=rechtsgrundlage,
                        aktenzeichen=aktenzeichen,
                        gericht=gericht,
                        datum=datum.isoformat() if datum else "",
                        status=WikiStatus.ENTWURF,
                        erstellt_von=user.name if user else "Anonym"
                    )
                    
                    wiki.create_entry(entry)
                    st.success("✅ Eintrag erstellt (als Entwurf)")
                    st.rerun()
                else:
                    st.error("Bitte Titel und Inhalt ausfüllen!")


if __name__ == "__main__":
    render()
