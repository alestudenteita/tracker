import streamlit as st
from datetime import datetime, timedelta

def init_auth():
    """Inizializza le variabili di sessione per l'autenticazione"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'username' not in st.session_state:
        st.session_state.username = None
    if 'last_activity' not in st.session_state:
        st.session_state.last_activity = None

def check_auth():
    """Verifica se l'utente è autenticato e la sessione è valida"""
    init_auth()  # Ensure auth is initialized

    if not st.session_state.authenticated:
        return False

    # Controlla timeout sessione (4 ore)
    if st.session_state.last_activity:
        timeout = datetime.now() - st.session_state.last_activity
        if timeout > timedelta(hours=4):
            logout()
            return False

    st.session_state.last_activity = datetime.now()
    return True

def login(username, password):
    """Gestisce il login dell'utente"""
    init_auth()  # Ensure auth is initialized

    # In un'applicazione reale, questi dovrebbero essere in un database sicuro
    VALID_USERNAME = "admin"
    VALID_PASSWORD = "password123"  # In produzione, usa password hash

    if username == VALID_USERNAME and password == VALID_PASSWORD:
        st.session_state.authenticated = True
        st.session_state.username = username
        st.session_state.last_activity = datetime.now()
        return True
    return False

def logout():
    """Effettua il logout dell'utente"""
    init_auth()  # Ensure auth is initialized
    st.session_state.authenticated = False
    st.session_state.username = None
    st.session_state.last_activity = None