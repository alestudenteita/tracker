import streamlit as st
from utils.supabase_db import add_risorsa, delete_risorsa

st.set_page_config(page_title="Libreria Contenuti", page_icon="📚")

# Inizializza la variabile se non esiste
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.warning("Effettua il login per accedere a questa pagina")
    st.stop()

st.title("📚 Libreria Contenuti")

# Tabs per le diverse funzionalità
tab1, tab2, tab3 = st.tabs(["Registrazione Materiale", "Libreria Materiale", "Gestione Libri"])

with tab1:
    st.header("Registrazione Nuovo Materiale")

    from utils.supabase_db import get_libri_disponibili
    
    libro = st.selectbox(
        "Seleziona libro",
        options=get_libri_disponibili()
    )

    titolo = st.text_input("Titolo del capitolo e unità")
    url = st.text_input("URL")
    categoria = st.selectbox(
        "Categoria",
        ["Materiale Didattico", "Esercizi", "Video", "Link Utili", "Altro"]
    )
    livello = st.selectbox(
        "Livello",
        ["A1", "A2", "B1", "B2", "C1", "C2"]
    )
    descrizione = st.text_area("Descrizione")

    if st.button("Salva Materiale"):
        if titolo and url and libro:
            add_risorsa(libro, titolo, url, categoria, livello, descrizione)
            st.success("Materiale aggiunto con successo!")
        else:
            st.error("Libro, titolo e URL sono obbligatori")

with tab2:
    st.header("Libreria Materiale")

    if st.session_state.libreria.empty:
        st.info("Non ci sono ancora materiali nella libreria")
    else:
        # Filtri
        col1, col2, col3 = st.columns(3)
        with col1:
            libro_filter = st.multiselect(
                "Filtra per Libro",
                options=sorted(st.session_state.libreria['libro'].unique())
            )
        with col2:
            categoria_filter = st.multiselect(
                "Filtra per Categoria",
                options=sorted(st.session_state.libreria['categoria'].unique())
            )
        with col3:
            livello_filter = st.multiselect(
                "Filtra per Livello",
                options=sorted(st.session_state.libreria['livello'].unique())
            )

        search = st.text_input("Cerca per titolo o descrizione")

        # Filtra risultati
        filtered_df = st.session_state.libreria.copy()

        if libro_filter:
            filtered_df = filtered_df[filtered_df['libro'].isin(libro_filter)]

        if categoria_filter:
            filtered_df = filtered_df[filtered_df['categoria'].isin(categoria_filter)]

        if livello_filter:
            filtered_df = filtered_df[filtered_df['livello'].isin(livello_filter)]

        if search:
            search = search.lower()
            filtered_df = filtered_df[
                filtered_df['titolo'].str.lower().str.contains(search) |
                filtered_df['descrizione'].str.lower().str.contains(search)
            ]

        # Raggruppa per categoria
        for categoria in sorted(filtered_df['categoria'].unique()):
            st.subheader(f"📚 {categoria}")
            categoria_df = filtered_df[filtered_df['categoria'] == categoria]

            for _, row in categoria_df.iterrows():
                with st.expander(f"{row['libro']} - {row['titolo']} ({row['livello']})"):
                    st.write(f"**Descrizione:** {row['descrizione']}")
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.markdown(f"[Apri Materiale]({row['url']})")
                    with col2:
                        if st.button("🗑️ Elimina", key=f"del_resource_{row['id']}"):
                            delete_risorsa(row['id'])
                            st.success("Materiale eliminato con successo!")
                            st.rerun()

with tab3:
    st.header("📖 Gestione Libri")

    # Ottieni la lista dei libri dal database
    from utils.supabase_db import add_libro_disponibile, get_libri_disponibili, delete_libro_disponibile
    
    # Form per aggiungere nuovo libro
    col1, col2 = st.columns([2,1])
    with col1:
        nuovo_libro = st.text_input("Nome del libro")
    with col2:
        if st.button("Aggiungi Libro") and nuovo_libro:
            if add_libro_disponibile(nuovo_libro):
                st.success(f"Libro '{nuovo_libro}' aggiunto alla lista")
            else:
                st.warning(f"Libro '{nuovo_libro}' già presente nella lista")

    # Lista dei libri esistenti
    st.header("Libri Disponibili")
    libri = get_libri_disponibili()
    if libri:
        for libro in libri:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"- {libro}")
            with col2:
                if st.button("🗑️", key=f"del_libro_{libro}"):
                    delete_libro_disponibile(libro)
                    st.success(f"Libro '{libro}' eliminato dalla lista")
                    st.rerun()
    else:
        st.info("Non ci sono ancora libri nella lista. Aggiungi il tuo primo libro!")