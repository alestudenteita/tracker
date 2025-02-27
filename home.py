import streamlit as st

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Gestione Studenti",
    page_icon="📚",
    layout="wide"
)

import pandas as pd
import base64
from utils.supabase_db import init_db, get_branding_settings
from utils.auth import init_auth, check_auth, login, logout

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'studenti' not in st.session_state:
    st.session_state.studenti = pd.DataFrame()

if 'custom_links' not in st.session_state:
    st.session_state.custom_links = pd.DataFrame()

if 'giorni_lezione' not in st.session_state:
    st.session_state.giorni_lezione = pd.DataFrame()


# Initialize auth and database first
init_auth()
init_db()

# Stili CSS globali
st.markdown("""
<style>
.logo-container {
    text-align: center;
    margin: 20px auto;
    padding: 0;
    display: flex;
    justify-content: center;
}
.logo-container img {
    max-width: 180px;
    height: auto;
    margin: 0 auto;
}
.calendar-section {
    margin: 20px 0;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 10px;
}
.calendar-header {
    text-align: center;
    margin-bottom: 15px;
    font-size: 1.1em;
}
.day-column {
    background-color: white;
    padding: 8px;
    border-radius: 5px;
    margin: 2px;
    font-size: 0.8em;
}
.day-column h4 {
    font-size: 0.9em;
    margin-bottom: 6px;
}
.student-card {
    padding: 3px;
    margin: 2px 0;
    background: #eef;
    border-radius: 3px;
    font-size: 0.75em;
}
.custom-link {
    display: inline-block;
    text-align: center;
    margin: 10px;
    text-decoration: none;
    color: inherit;
    width: calc(20% - 20px); /* 5 icone per riga */
    box-sizing: border-box;
}
.custom-link img {
    width: 48px;
    height: 48px;
    margin-bottom: 5px;
    transition: transform 0.2s;
}
.custom-link:hover img {
    transform: scale(1.1);
}
.link-grid {
    display: flex;
    flex-wrap: wrap;
    justify-content: flex-start;
    width: 100%;
    padding: 20px 0;
}
.stats-section {
    margin-top: 30px;
    padding: 20px;
    background-color: #f8f9fa;
    border-radius: 10px;
}
</style>
""", unsafe_allow_html=True)

# Get branding settings
try:
    logo_bytes, welcome_message = get_branding_settings()
except Exception as e:
    st.error(f"Errore nel caricamento delle impostazioni: {str(e)}")
    logo_bytes, welcome_message = None, None

# Gestione Login
if not check_auth():
    st.title("🔐 Login")

    if welcome_message:
        st.markdown(f"### {welcome_message}")

    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Accedi")

        if submit:
            if login(username, password):
                st.success("Login effettuato con successo!")
                st.rerun()
            else:
                st.error("Username o password non validi")
else:
    # Header con logout
    col1, col2 = st.columns([6,1])

    # Logo centrato
    col_logo1, col_logo2, col_logo3 = st.columns([1, 2, 1])
    with col_logo2:
        if logo_bytes:
            try:
                st.markdown('<div class="logo-container">', unsafe_allow_html=True)
                st.image(logo_bytes, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)
            except:
                st.markdown("<div class='emoji-header'>📚 💬 🎓</div>", unsafe_allow_html=True)
        else:
            st.markdown("<div class='emoji-header'>📚 💬 🎓</div>", unsafe_allow_html=True)

    with col2:
        if st.button("Logout"):
            logout()
            st.rerun()

    # Sezione Calendario Settimanale (compatta)
    st.markdown('<div class="calendar-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="calendar-header">📅 Lezioni della Settimana</h2>', unsafe_allow_html=True)

    giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    cols = st.columns(7)

    if not st.session_state.giorni_lezione.empty:
        for idx, (col, giorno) in enumerate(zip(cols, giorni)):
            with col:
                st.markdown(f'<div class="day-column">', unsafe_allow_html=True)
                st.markdown(f"<h4 title='{giorno}'>{giorno}</h4>", unsafe_allow_html=True)

                # Filtra gli studenti per questo giorno
                studenti_giorno = st.session_state.giorni_lezione[
                    st.session_state.giorni_lezione['giorno'] == giorno
                ]

                if not studenti_giorno.empty:
                    for _, studente in studenti_giorno.iterrows():
                        # Get student name from students table
                        if 'studente_id' in studente and studente['studente_id'] in st.session_state.studenti['id'].values:
                            student_record = st.session_state.studenti[st.session_state.studenti['id'] == studente['studente_id']].iloc[0]
                            student_name = student_record['nome']
                            st.markdown(f"""
                            <div class="student-card">
                                {student_name}
                            </div>
                            """, unsafe_allow_html=True)
                else:
                    st.markdown("<i>Nessuna lezione</i>", unsafe_allow_html=True)

                st.markdown('</div>', unsafe_allow_html=True)
    else:
        for idx, (col, giorno) in enumerate(zip(cols, giorni)):
            with col:
                st.markdown(f'<div class="day-column">', unsafe_allow_html=True)
                st.markdown(f"<h4 title='{giorno}'>{giorno}</h4>", unsafe_allow_html=True)
                st.markdown("<i>Nessuna lezione</i>", unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)

    # Sezione Quick Links
    if not st.session_state.custom_links.empty:
        st.markdown('<h2>🔗 Link Utili</h2>', unsafe_allow_html=True)
        st.markdown('<div class="link-grid">', unsafe_allow_html=True)
        ordered_links = st.session_state.custom_links.sort_values('ordine')
        for _, link in ordered_links.iterrows():
            if link.icona:
                try:
                    # Gestisce diversi formati di icona
                    if isinstance(link.icona, bytes):
                        encoded_image = base64.b64encode(link.icona).decode()
                    elif isinstance(link.icona, str):
                        # Se è già una stringa base64, usala direttamente
                        encoded_image = link.icona
                    else:
                        raise ValueError("Formato icona non supportato")

                    st.markdown(f"""
                    <a href="{link.url}" class="custom-link" target="_blank">
                        <img src="data:image/png;base64,{encoded_image}" alt="{link.titolo}"/>
                        <br/>
                        {link.titolo}
                    </a>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Errore nel caricamento dell'icona per {link.titolo}")
            else:
                st.markdown(f"""
                <a href="{link.url}" class="custom-link" target="_blank">
                    <span style="font-size: 2em;">🔗</span>
                    <br/>
                    {link.titolo}
                </a>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("🔗 Aggiungi i tuoi link rapidi nella sezione Impostazioni")

    # Sezione statistiche generali (spostata in fondo)
    st.markdown('<div class="stats-section">', unsafe_allow_html=True)
    if 'studenti' in st.session_state and not st.session_state.studenti.empty:
        st.header("📊 Panoramica")
        col1, col2, col3 = st.columns(3)
        num_studenti = len(st.session_state.studenti)
        num_canali = len(st.session_state.studenti['canale'].unique())

        with col1:
            st.metric("Totale Studenti", num_studenti)
        with col2:
            st.metric("Canali Attivi", num_canali)
        with col3:
            if num_canali > 0:
                media = round(num_studenti/num_canali, 1)
                st.metric("Media Studenti/Canale", media)
    else:
        st.info("👋 Inizia aggiungendo il tuo primo studente dalla sezione 'Studenti'!")
    st.markdown('</div>', unsafe_allow_html=True)
