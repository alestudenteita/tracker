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
