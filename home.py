import streamlit as st
import pandas as pd
import base64
from utils.supabase_db import init_db, get_branding_settings
from utils.auth import init_auth, check_auth, login, logout

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

init_auth()
init_db()

st.markdown("""
<style>
/* Layout generale */
.main-layout {
    display: flex;
    flex-direction: column;
    gap: 15px;
    max-width: 1200px;
    margin: 0 auto;
}

/* Calendario compatto */
.calendar-section {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 8px;
    margin-bottom: 15px;
    overflow-x: auto;
    white-space: nowrap;
}
.days-container {
    display: flex;
    gap: 3px;
    justify-content: center;
}
.day-column {
    background-color: white;
    padding: 4px;
    border-radius: 5px;
    border: 1px solid #e0e0e0;
    text-align: center;
    min-width: 50px;
}

/* Quick Links Grid - 5 colonne, massimo 100 righe */
.link-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    grid-auto-rows: auto;
    gap: 10px;
    max-height: 500px;
    overflow-y: auto;
}
.custom-link {
    display: flex;
    flex-direction: column;
    align-items: center;
    text-align: center;
    text-decoration: none;
    color: inherit;
    padding: 8px;
    border-radius: 8px;
    transition: all 0.2s;
}
</style>
""", unsafe_allow_html=True)

if not check_auth():
    st.title("🔐 Login")
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submit = st.form_submit_button("Accedi")
        if submit and login(username, password):
            st.rerun()
else:
    st.markdown('<div class="main-layout">', unsafe_allow_html=True)

    # Calendario Compatto
    st.markdown('<div class="calendar-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="calendar-header">📅 Lezioni</h2>', unsafe_allow_html=True)
    st.markdown('<div class="days-container">', unsafe_allow_html=True)
    giorni = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
    for giorno in giorni:
        st.markdown(f'<div class="day-column">{giorno}</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Quick Links
    if not st.session_state.custom_links.empty:
        st.markdown('<div class="links-section">', unsafe_allow_html=True)
        st.markdown('<div class="link-grid">', unsafe_allow_html=True)
        ordered_links = st.session_state.custom_links.sort_values('ordine').head(500)
        for _, link in ordered_links.iterrows():
            st.markdown(f'<a href="{link.url}" class="custom-link" target="_blank">{link.titolo}</a>', unsafe_allow_html=True)
        st.markdown('</div></div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
