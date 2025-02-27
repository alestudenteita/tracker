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

# Modify the CSS styles for quick links and calendar
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
