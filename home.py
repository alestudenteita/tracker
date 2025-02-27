import streamlit as st
from utils.supabase_db import init_db, get_branding_settings
from utils.auth import init_auth, check_auth, login, logout
import pandas as pd
import base64

# Set page config must be the first Streamlit command
st.set_page_config(
    page_title="Gestione Studenti",
    page_icon="📚",
    layout="wide"
)

# Initialize session state variables
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

if 'studenti' not in st.session_state:
    st.session_state.studenti = pd.DataFrame()

if 'custom_links' not in st.session_state:
    st.session_state.custom_links = pd.DataFrame()

if 'giorni_lezione' not in st.session_state:
    st.session_state.giorni_lezione = pd.DataFrame()

# Initialize auth and database
init_auth()
init_db()

# CSS styles for layout
st.markdown("""
<style>
.calendar-section {
    margin: 20px 0;
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 10px;
    display: flex;
    overflow-x: auto;
    gap: 10px;
}
.calendar-header {
    text-align: center;
    margin-bottom: 15px;
    font-size: 1.1em;
}
.day-column {
    background-color: white;
    padding: 12px;
    border-radius: 5px;
    min-width: 120px;
    flex: 1;
}
.day-column h4 {
    font-size: 0.9em;
    margin-bottom: 8px;
    text-align: center;
}
.student-card {
    padding: 6px;
    margin: 4px 0;
    background: #eef;
    border-radius: 3px;
    font-size: 0.75em;
    text-align: center;
}
.link-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 15px;
    padding: 20px;
    background-color: #f8f9fa;
    border-radius: 10px;
    margin: 20px 0;
}
.custom-link {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    text-decoration: none;
    color: inherit;
    padding: 10px;
    background: white;
    border-radius: 8px;
    transition: transform 0.2s, box-shadow 0.2s;
}
.custom-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.custom-link img {
    width: 48px;
    height: 48px;
    margin-bottom: 8px;
    transition: transform 0.2s;
}
.custom-link:hover img {
    transform: scale(1.1);
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

# Login handling
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
    # Main dashboard content
    st.title("📚 Dashboard")

    # Calendar Section
    st.markdown('<div class="calendar-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="calendar-header">📅 Lezioni della Settimana</h2>', unsafe_allow_html=True)

    giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]

    for giorno in giorni:
        st.markdown(f'<div class="day-column">', unsafe_allow_html=True)
        st.markdown(f"<h4>{giorno}</h4>", unsafe_allow_html=True)

        # Filter students for this day
        studenti_giorno = st.session_state.giorni_lezione[
            st.session_state.giorni_lezione['giorno'] == giorno
        ]

        if not studenti_giorno.empty:
            for _, studente in studenti_giorno.iterrows():
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

    st.markdown('</div>', unsafe_allow_html=True)

    # Quick Links Section
    if not st.session_state.custom_links.empty:
        st.markdown('<div class="link-grid">', unsafe_allow_html=True)
        ordered_links = st.session_state.custom_links.sort_values('ordine')
        for _, link in ordered_links.iterrows():
            if link.icona:
                try:
                    encoded_image = base64.b64encode(link.icona).decode()
                    st.markdown(f"""
                    <a href="{link.url}" class="custom-link" target="_blank">
                        <img src="data:image/png;base64,{encoded_image}" alt="{link.titolo}"/>
                        {link.titolo}
                    </a>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Errore nel caricamento dell'icona per {link.titolo}")
            else:
                st.markdown(f"""
                <a href="{link.url}" class="custom-link" target="_blank">
                    <span style="font-size: 2em;">🔗</span>
                    {link.titolo}
                </a>
                """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("🔗 Aggiungi i tuoi link rapidi nella sezione Impostazioni")

    # Stats Section
    st.markdown('<div class="stats-section">', unsafe_allow_html=True)
    if not st.session_state.studenti.empty:
        st.header("📊 Panoramica")
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Totale Studenti", len(st.session_state.studenti))
        with col2:
            st.metric("Canali Attivi", len(st.session_state.studenti['canale'].unique()))
        with col3:
            media = round(len(st.session_state.studenti)/max(1, len(st.session_state.studenti['canale'].unique())), 1)
            st.metric("Media Studenti/Canale", media)
    st.markdown('</div>', unsafe_allow_html=True)
