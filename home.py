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

# Initialize auth and database first
init_auth()
init_db()

# Stili CSS globali
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

/* Header e logo */
.header-container {
    text-align: center;
    margin: 0 auto 15px auto;
    width: 100%;
    display: flex;
    justify-content: center;
    align-items: center;
    position: relative;
}
.logo-container {
    max-width: 160px;
    margin: 0 auto;
    padding: 10px 0;
}
.logo-container img {
    max-width: 100%;
    height: auto;
}
.logout-button {
    position: absolute;
    right: 10px;
    top: 50%;
    transform: translateY(-50%);
}

/* Quick Links Grid - 5 colonne fisse */
.links-section {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
}
.links-section h2 {
    font-size: 1.2rem;
    margin-bottom: 10px;
}
.link-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    grid-auto-flow: row;
    grid-auto-rows: auto;
    gap: 10px;
    overflow-y: auto;
    max-height: 300px;
    width: 100%;
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
.custom-link:hover {
    background-color: #f0f0f0;
    transform: translateY(-2px);
}
.custom-link img {
    width: 40px;
    height: 40px;
    margin-bottom: 5px;
}
.custom-link span {
    font-size: 0.85rem;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    max-width: 100%;
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
    # Container principale
    st.markdown('<div class="main-layout">', unsafe_allow_html=True)
    
    # Header con logo e logout
    st.markdown('<div class="header-container">', unsafe_allow_html=True)
    
    # Logo centrato
    if logo_bytes:
        try:
            st.markdown('<div class="logo-container">', unsafe_allow_html=True)
            st.image(logo_bytes, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        except:
            st.markdown("<div class='emoji-header'>📚 💬 🎓</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='emoji-header'>📚 💬 🎓</div>", unsafe_allow_html=True)
    
    # Pulsante Logout
    st.markdown('<div class="logout-button">', unsafe_allow_html=True)
    if st.button("Logout"):
        logout()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Contenitore per i link
    st.markdown('<div class="links-container">', unsafe_allow_html=True)
    
    # Sezione Quick Links
    if not st.session_state.custom_links.empty:
        st.markdown('<div class="links-section">', unsafe_allow_html=True)
        st.markdown('<h2>🔗 Link Utili</h2>', unsafe_allow_html=True)
        st.markdown('<div class="link-grid">', unsafe_allow_html=True)
        
        ordered_links = st.session_state.custom_links.sort_values('ordine')
        for _, link in ordered_links.iterrows():
            st.markdown(f"""
            <a href="{link.url}" class="custom-link" target="_blank">
                <span style="font-size: 1.5em;">🔗</span>
                <span>{link.titolo}</span>
            </a>
            """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="links-section">', unsafe_allow_html=True)
        st.info("🔗 Aggiungi i tuoi link rapidi nella sezione Impostazioni")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
