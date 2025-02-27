import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_db import add_studente, add_progresso, update_studente, delete_studente
from utils.helpers import filter_dataframe

st.set_page_config(page_title="Gestione Studenti", page_icon="👥")

# Inizializza la variabile se non esiste
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.warning("Effettua il login per accedere a questa pagina")
    st.stop()

st.title("👥 Gestione Studenti")

# Pulsante per mostrare/nascondere il pannello di debug
if st.checkbox("Mostra pannello di debug", value=False, key="show_debug"):
    with st.expander("Debug", expanded=True):
        st.info("Questo pannello mostra operazioni e messaggi di debug.")
        if st.button("Test connessione Supabase"):
            try:
                from utils.supabase_db import supabase
                test_response = supabase.table('studenti').select('id').limit(1).execute()
                st.success(f"✅ Connessione a Supabase riuscita! Risposta: {test_response}")
            except Exception as e:
                st.error(f"❌ Errore di connessione a Supabase: {str(e)}")

# Tabs per le diverse funzionalità
tab1, tab2, tab3 = st.tabs(["Registrazione Nuovo Studente", "Lista Studenti", "Registrazione Progresso"])

with tab1:
    st.header("Registrazione Nuovo Studente")

    col1, col2 = st.columns(2)
    with col1:
        nome = st.text_input("Nome")
        cognome = st.text_input("Cognome")
        canale = st.selectbox("Canale", ["Diretto", "Apprentus", "Preply", "iTalki"])
        livello = st.selectbox("Livello", ["A1", "A2", "B1", "B2", "C1", "C2"])

    with col2:
        metodologia = st.text_input("Metodologia di insegnamento")
        durata_lezione = st.number_input("Durata lezione (minuti)", min_value=30, step=15)
        prezzo_lezione = st.number_input("Prezzo concordato a lezione", min_value=0.0, step=5.0)
        data_iscrizione = st.date_input("Data Iscrizione", datetime.now())

    st.subheader("📅 Giorni di Lezione")
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        lunedi = st.checkbox("Lunedì")
        martedi = st.checkbox("Martedì")
    with col2:
        mercoledi = st.checkbox("Mercoledì")
        giovedi = st.checkbox("Giovedì")
    with col3:
        venerdi = st.checkbox("Venerdì")
        sabato = st.checkbox("Sabato")
    with col4:
        domenica = st.checkbox("Domenica")

    st.subheader("📎 Link Studente")
    col1, col2, col3 = st.columns(3)
    with col1:
        slides_url = st.text_input("Link Google Slides", 
                                   placeholder="https://docs.google.com/presentation/...")
    with col2:
        classroom_url = st.text_input("Link Google Classroom",
                                      placeholder="https://classroom.google.com/...")
    with col3:
        meet_url = st.text_input("Link Google Meet",
                                 placeholder="https://meet.google.com/...")

    commenti = st.text_area("Commenti e Note")

    # Container dedicato per i messaggi - sempre visibile
    message_container = st.empty()
    
    if st.button("Salva Studente"):
        if nome and cognome:
            # Raccogli i giorni di lezione selezionati
            giorni_lezione = []
            if lunedi: giorni_lezione.append("Lunedì")
            if martedi: giorni_lezione.append("Martedì")
            if mercoledi: giorni_lezione.append("Mercoledì")
            if giovedi: giorni_lezione.append("Giovedì")
            if venerdi: giorni_lezione.append("Venerdì")
            if sabato: giorni_lezione.append("Sabato")
            if domenica: giorni_lezione.append("Domenica")

            # Mostriamo un messaggio di caricamento in una variabile temporanea
            # che verrà sostituita dal messaggio di successo/errore
            with st.spinner("Salvataggio in corso..."):
                result = add_studente(nome, cognome, canale, livello, metodologia, durata_lezione, prezzo_lezione, 
                               commenti, data_iscrizione, slides_url, classroom_url, meet_url, 
                               giorni_lezione=giorni_lezione)
                
                # Non mostriamo altro messaggio qui, perché sarà già mostrato dalla funzione add_studente
        else:
            # Messaggio di errore per campi obbligatori mancanti
            st.error("Nome e cognome sono obbligatori")

with tab2:
    st.header("Lista Studenti")

    if st.session_state.studenti.empty:
        st.info("Non ci sono ancora studenti registrati")
    else:
        # Filtri
        col1, col2 = st.columns(2)
        with col1:
            canali_disponibili = st.session_state.studenti['canale'].unique()
            canale_filter = st.multiselect(
                "Filtra per Canale",
                options=canali_disponibili if len(canali_disponibili) > 0 else []
            )
        with col2:
            livelli_disponibili = st.session_state.studenti['livello'].unique()
            livello_filter = st.multiselect(
                "Filtra per Livello",
                options=livelli_disponibili if len(livelli_disponibili) > 0 else []
            )

        # Applica filtri
        filtered_df = filter_dataframe(
            st.session_state.studenti,
            {
                'canale': canale_filter if canale_filter else None,
                'livello': livello_filter if livello_filter else None
            }
        )

        # Visualizza studenti
        for _, studente in filtered_df.iterrows():
            with st.expander(f"{studente['nome']} {studente['cognome']} - {studente['livello']}"):
                col1, col2, col3 = st.columns([2,2,1])
                with col1:
                    nuovo_nome = st.text_input("Nome", value=studente['nome'], key=f"nome_{studente['id']}")
                    nuovo_cognome = st.text_input("Cognome", value=studente['cognome'], key=f"cognome_{studente['id']}")
                    nuovo_canale = st.selectbox("Canale", ["Diretto", "Apprentus", "Preply", "iTalki"], 
                                              index=["Diretto", "Apprentus", "Preply", "iTalki"].index(studente['canale']),
                                              key=f"canale_{studente['id']}")
                with col2:
                    nuovo_livello = st.selectbox("Livello", ["A1", "A2", "B1", "B2", "C1", "C2"],
                                               index=["A1", "A2", "B1", "B2", "C1", "C2"].index(studente['livello']),
                                               key=f"livello_{studente['id']}")
                    nuova_durata = st.number_input("Durata lezione (minuti)", 
                                                 value=float(studente['durata_lezione']),
                                                 step=15.0,
                                                 min_value=0.0,
                                                 key=f"durata_{studente['id']}")
                    nuovo_prezzo = st.number_input("Prezzo a lezione", 
                                                value=studente['prezzo_lezione'],
                                                key=f"prezzo_{studente['id']}")
                with col3:
                    # Bottone per aggiornare
                    if st.button("Aggiorna", key=f"update_{studente['id']}"):
                        update_studente(
                            studente['id'], 
                            nuovo_nome, 
                            nuovo_cognome, 
                            nuovo_canale, 
                            nuovo_livello, 
                            nuova_durata, 
                            nuovo_prezzo
                        )
                        st.success("Studente aggiornato con successo!")
                        st.rerun()

                    # Bottone per eliminare
                    if st.button("Elimina", key=f"delete_{studente['id']}"):
                        st.session_state[f"confirm_delete_{studente['id']}"] = True

                    # Mostra bottoni di conferma solo se richiesto
                    if st.session_state.get(f"confirm_delete_{studente['id']}", False):
                        st.warning("Sei sicuro?")
                        if st.button("Sì", key=f"confirm_yes_{studente['id']}"):
                            delete_studente(studente['id'])
                            st.success("Studente eliminato!")
                            st.rerun()
                        if st.button("No", key=f"confirm_no_{studente['id']}"):
                            st.session_state[f"confirm_delete_{studente['id']}"] = False
                            st.rerun()

                # Link esterni con icone
                if any([studente['slides_url'], studente['classroom_url'], studente['meet_url']]):
                    st.subheader("🔗 Link Rapidi")
                    col1, col2, col3 = st.columns(3)

                    with col1:
                        if studente['slides_url']:
                            st.markdown(f"""
                            <a href="{studente['slides_url']}" target="_blank">
                                <img src="https://img.icons8.com/color/48/000000/google-slides.png" alt="Google Slides"/>
                                <br/>Presentazione
                            </a>
                            """, unsafe_allow_html=True)

                    with col2:
                        if studente['classroom_url']:
                            st.markdown(f"""
                            <a href="{studente['classroom_url']}" target="_blank">
                                <img src="https://img.icons8.com/color/48/000000/google-classroom.png" alt="Google Classroom"/>
                                <br/>Classroom
                            </a>
                            """, unsafe_allow_html=True)

                    with col3:
                        if studente['meet_url']:
                            st.markdown(f"""
                            <a href="{studente['meet_url']}" target="_blank">
                                <img src="https://img.icons8.com/color/48/000000/google-meet.png" alt="Google Meet"/>
                                <br/>Meet
                            </a>
                            """, unsafe_allow_html=True)

                # Mostra progressi dello studente
                st.subheader("📈 Progressi")
                progressi_studente = st.session_state.progressi[
                    st.session_state.progressi['studente_id'] == studente['id']
                ].sort_values('data', ascending=False)

                if progressi_studente.empty:
                    st.info("Non ci sono ancora progressi registrati per questo studente.")
                else:
                    st.write("### Progressi registrati")
                    for _, row in progressi_studente.iterrows():
                        # Recupera i dettagli del contenuto
                        if not st.session_state.libreria.empty and row['contenuto_id'] in st.session_state.libreria['id'].values:
                            contenuto = st.session_state.libreria[st.session_state.libreria['id'] == row['contenuto_id']].iloc[0]
                            with st.expander(f"{row['data']} - {contenuto['titolo']}"):
                                st.write(f"**Contenuto:** {contenuto['titolo']}")
                                st.write(f"**Categoria:** {contenuto['categoria']}")
                                st.write(f"**Livello:** {contenuto['livello']}")
                                st.write(f"**Note:** {row['descrizione']}")
                                col1, col2 = st.columns([3, 1])
                                with col1:
                                    st.markdown(f"[Vedi materiale]({contenuto['url']})")
                                with col2:
                                    if st.button("🗑️ Elimina", key=f"del_progress_{row['id']}"):
                                        from utils.supabase_db import delete_progresso
                                        delete_progresso(row['id'])
                                        st.success("Progresso eliminato con successo!")
                                        st.rerun()
                        else:
                            with st.expander(f"{row['data']} - Contenuto non disponibile"):
                                st.write(f"**Note:** {row['descrizione']}")
                                if st.button("🗑️ Elimina", key=f"del_progress_{row['id']}"):
                                    from utils.supabase_db import delete_progresso
                                    delete_progresso(row['id'])
                                    st.success("Progresso eliminato con successo!")
                                    st.rerun()

                # Mostra pagamenti dello studente
                st.subheader("💶 Pagamenti")
                pagamenti_studente = st.session_state.pagamenti[
                    st.session_state.pagamenti['studente_id'] == studente['id']
                ].sort_values('data', ascending=False)

                if not pagamenti_studente.empty:
                    for _, pagamento in pagamenti_studente.iterrows():
                        st.write(f"**{pagamento['mese']} {pagamento['anno']}:** €{pagamento['importo']:.2f}")
                        if pagamento['commenti']:
                            st.write(f"Note: {pagamento['commenti']}")
                else:
                    st.info("Nessun pagamento registrato")

        # Export CSV
        if st.button("Esporta CSV"):
            csv = filtered_df.to_csv(index=False)
            st.download_button(
                "Download CSV",
                csv,
                "studenti.csv",
                "text/csv"
            )

with tab3:
    st.header("Registrazione Progresso")

    if st.session_state.studenti.empty:
        st.info("Non ci sono ancora studenti registrati")
    else:
        # Form per registrare il progresso
        studente = st.selectbox(
            "Seleziona Studente",
            options=st.session_state.studenti['id'].tolist(),
            format_func=lambda x: f"{st.session_state.studenti[st.session_state.studenti['id']==x]['nome'].iloc[0]} {st.session_state.studenti[st.session_state.studenti['id']==x]['cognome'].iloc[0]}"
        )

        # Seleziona contenuto dalla libreria
        if not st.session_state.libreria.empty:
            contenuto = st.selectbox(
                "Contenuto dalla libreria",
                options=st.session_state.libreria['id'].tolist(),
                format_func=lambda x: f"{st.session_state.libreria[st.session_state.libreria['id']==x]['titolo'].iloc[0]}"
            )
        else:
            st.warning("Non ci sono contenuti disponibili nella libreria")
            st.stop()

        col1, col2 = st.columns(2)
        with col1:
            data = st.date_input("Data", datetime.now())

        with col2:
            descrizione = st.text_area("Note sul progresso")

        if st.button("Salva Progresso"):
            if descrizione:
                add_progresso(studente, data, contenuto, descrizione)
                st.success("Progresso registrato!")
            else:
                st.error("Inserisci una descrizione del progresso")
