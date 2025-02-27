import streamlit as st
import pandas as pd
from datetime import datetime
from utils.supabase_db import add_pagamento, delete_pagamento
import plotly.express as px

st.set_page_config(page_title="Gestione Pagamenti", page_icon="💶")

# Inizializza la variabile se non esiste
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.warning("Effettua il login per accedere a questa pagina")
    st.stop()

st.title("💶 Gestione Pagamenti")

tab1, tab2, tab3 = st.tabs(["Registrazione Pagamento", "Statistiche", "Storico Pagamenti"])

with tab1:
    st.header("Registrazione Pagamento")

    if st.session_state.studenti.empty:
        st.info("Aggiungi prima uno studente per registrare un pagamento")
    else:
        # Form per nuovo pagamento
        studente = st.selectbox(
            "Seleziona Studente",
            options=st.session_state.studenti['id'].tolist(),
            format_func=lambda x: f"{st.session_state.studenti[st.session_state.studenti['id']==x]['nome'].iloc[0]} {st.session_state.studenti[st.session_state.studenti['id']==x]['cognome'].iloc[0]}"
        )

        col1, col2 = st.columns(2)
        with col1:
            data_pagamento = st.date_input("Data Pagamento", datetime.now())
            importo = st.number_input("Importo", min_value=0.0, step=10.0)

        with col2:
            mesi = ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno",
                   "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
            mese_corrente = datetime.now().month - 1  # -1 perché gli indici partono da 0
            mese = st.selectbox("Mese di riferimento", mesi, index=mese_corrente)
            anno = datetime.now().year

        if st.button("Registra Pagamento"):
            if importo > 0:
                commenti_pagamento = st.text_area("Note sul pagamento")
                add_pagamento(studente, data_pagamento, importo, mese, anno, commenti_pagamento)
                st.success("Pagamento registrato con successo!")
            else:
                st.error("L'importo deve essere maggiore di zero")

with tab2:
    st.header("Statistiche Pagamenti")

    if st.session_state.pagamenti.empty:
        st.info("Non ci sono ancora pagamenti registrati")
    else:
        # Selezione vista statistiche
        vista = st.radio("Visualizza statistiche per:", ["Mensili", "Per Studente"])

        if vista == "Mensili":
            # Statistiche mensili
            stats_mensili = st.session_state.pagamenti.groupby(['anno', 'mese'])['importo'].agg(['sum', 'count']).reset_index()
            stats_mensili.columns = ['Anno', 'Mese', 'Totale Incassato', 'Numero Pagamenti']

            # Calcola media mensile
            media_mensile = stats_mensili['Totale Incassato'].mean()

            # Calcola proiezione annuale
            mesi_registrati = len(stats_mensili)
            if mesi_registrati > 0:
                proiezione_annuale = media_mensile * 12

                # Mostra metriche
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Media Mensile", f"€{media_mensile:.2f}")
                with col2:
                    st.metric("Proiezione Annuale", f"€{proiezione_annuale:.2f}")

            # Grafico mensile
            fig = px.bar(stats_mensili, 
                        x='Mese', 
                        y='Totale Incassato',
                        color='Anno',
                        title='Incassi Mensili')
            st.plotly_chart(fig, use_container_width=True)

            # Tabella dettagliata
            st.dataframe(
                stats_mensili.style.format({
                    'Totale Incassato': '€{:.2f}',
                    'Numero Pagamenti': '{:.0f}'
                }),
                hide_index=True
            )

        else:
            # Statistiche per studente
            stats_studenti = pd.merge(
                st.session_state.pagamenti.groupby('studente_id')['importo'].agg(['sum', 'count', 'mean']).reset_index(),
                st.session_state.studenti[['id', 'nome', 'cognome']],
                left_on='studente_id',
                right_on='id'
            )
            stats_studenti['nome_completo'] = stats_studenti['nome'] + ' ' + stats_studenti['cognome']

            # Grafico per studente
            fig = px.bar(stats_studenti, 
                        x='nome_completo', 
                        y='sum',
                        title='Pagamenti Totali per Studente')
            st.plotly_chart(fig, use_container_width=True)

            # Tabella dettagliata - prima rinominiamo le colonne, poi applichiamo lo stile
            df_display = stats_studenti[['nome_completo', 'sum', 'mean', 'count']].copy()
            df_display.columns = ['Studente', 'Totale Pagato', 'Media Pagamenti', 'Numero Pagamenti']

            # Ora applichiamo lo stile alle colonne rinominate
            st.dataframe(
                df_display.style.format({
                    'Totale Pagato': '€{:.2f}',
                    'Media Pagamenti': '€{:.2f}',
                    'Numero Pagamenti': '{:.0f}'
                }),
                hide_index=True
            )

with tab3:
    st.header("📜 Storico Pagamenti")

    if st.session_state.pagamenti.empty:
        st.info("Non ci sono ancora pagamenti registrati")
    else:
        # Aggiungi filtri per migliorare la navigazione
        col1, col2, col3 = st.columns(3)
        with col1:
            # Filtro per studente
            studente_filtro = st.selectbox(
                "Filtra per Studente",
                options=["Tutti"] + st.session_state.studenti['id'].tolist(),
                format_func=lambda x: "Tutti" if x == "Tutti" else f"{st.session_state.studenti[st.session_state.studenti['id']==x]['nome'].iloc[0]} {st.session_state.studenti[st.session_state.studenti['id']==x]['cognome'].iloc[0]}"
            )

        with col2:
            # Filtro per anno
            anni = ["Tutti"] + sorted(st.session_state.pagamenti['anno'].unique().tolist(), reverse=True)
            anno_filtro = st.selectbox("Anno", options=anni)

        with col3:
            # Filtro per mese
            mesi = ["Tutti"] + ["Gennaio", "Febbraio", "Marzo", "Aprile", "Maggio", "Giugno", 
                   "Luglio", "Agosto", "Settembre", "Ottobre", "Novembre", "Dicembre"]
            mese_filtro = st.selectbox("Mese", options=mesi)

        # Applica i filtri
        pagamenti_filtrati = st.session_state.pagamenti.copy()

        if studente_filtro != "Tutti":
            pagamenti_filtrati = pagamenti_filtrati[pagamenti_filtrati['studente_id'] == studente_filtro]

        if anno_filtro != "Tutti":
            pagamenti_filtrati = pagamenti_filtrati[pagamenti_filtrati['anno'] == anno_filtro]

        if mese_filtro != "Tutti":
            pagamenti_filtrati = pagamenti_filtrati[pagamenti_filtrati['mese'] == mese_filtro]

        # Unisci con i dati degli studenti per avere il nome completo
        storico_completo = pd.merge(
            pagamenti_filtrati,
            st.session_state.studenti[['id', 'nome', 'cognome']],
            left_on='studente_id',
            right_on='id',
            suffixes=('', '_studente')  # Preserva le colonne originali dei pagamenti
        )

        # Aggiungi colonna nome completo
        storico_completo['studente'] = storico_completo['nome'] + ' ' + storico_completo['cognome']

        # Ordina per data (più recenti in alto)
        storico_completo = storico_completo.sort_values('data', ascending=False)

        # Seleziona e rinomina le colonne da visualizzare
        storico_display = storico_completo[['studente', 'data', 'mese', 'anno', 'importo', 'commenti']].copy()
        storico_display.columns = ['Studente', 'Data', 'Mese', 'Anno', 'Importo', 'Note']

        # Visualizza lo storico
        st.dataframe(
            storico_display.style.format({
                'Importo': '€{:.2f}',
                'Data': lambda x: x.split('T')[0] if 'T' in str(x) else x  # Formatta la data ISO
            }),
            hide_index=True
        )

        # Aggiungi opzione per eliminare pagamenti
        st.subheader("Elimina Pagamento")

        # Mostra solo se ci sono pagamenti dopo il filtraggio
        if not storico_completo.empty:
            pagamento_da_eliminare = st.selectbox(
                "Seleziona pagamento da eliminare",
                options=storico_completo['id'].tolist(),
                format_func=lambda x: f"{storico_completo[storico_completo['id']==x]['studente'].iloc[0]} - {storico_completo[storico_completo['id']==x]['mese'].iloc[0]} {storico_completo[storico_completo['id']==x]['anno'].iloc[0]} - €{storico_completo[storico_completo['id']==x]['importo'].iloc[0]:.2f}"
            )

            # Bottone di eliminazione con conferma
            if st.button("Elimina Pagamento"):
                st.warning("Sei sicuro di voler eliminare questo pagamento? Questa azione non può essere annullata.")
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Conferma Eliminazione"):
                        from utils.supabase_db import delete_pagamento
                        if delete_pagamento(pagamento_da_eliminare):
                            st.success("Pagamento eliminato con successo!")
                            # Forza il ricaricamento dei dati prima di rerun
                            from utils.supabase_db import load_data
                            load_data()
                            st.rerun()
                with col2:
                    if st.button("Annulla"):
                        st.info("Operazione annullata")
        else:
            st.info("Nessun pagamento corrisponde ai filtri selezionati")

        # Opzione per esportare i dati filtrati
        if not storico_completo.empty:
            csv = storico_display.to_csv(index=False)
            st.download_button(
                label="📥 Esporta dati filtrati (CSV)",
                data=csv,
                file_name=f"storico_pagamenti_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv"
            )
