
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

/* Calendario più compatto */
.calendar-section {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 8px;
    margin-bottom: 15px;
    overflow-x: hidden;
}
.calendar-header {
    font-size: 1.2rem;
    text-align: center;
    margin-bottom: 8px;
}
.days-container {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 3px;
}
.day-column {
    background-color: white;
    padding: 4px;
    border-radius: 5px;
    border: 1px solid #e0e0e0;
    min-width: 0;
}
.day-column h4 {
    font-size: 0.7rem;
    margin: 0 0 3px 0;
    padding: 0;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}
.student-card {
    padding: 2px;
    margin: 2px 0;
    background: #eef;
    border-radius: 3px;
    font-size: 0.65rem;
    text-align: center;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Sezione statistiche */
.stats-section {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    margin-top: 10px;
}
.stats-section h2 {
    font-size: 1.2rem;
    margin-bottom: 10px;
}
.stats-cards {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
}
.stat-card {
    background-color: white;
    padding: 10px;
    border-radius: 8px;
    text-align: center;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}
.stat-value {
    font-size: 1.5rem;
    font-weight: bold;
    color: #4a86e8;
}
.stat-label {
    font-size: 0.8rem;
    color: #666;
}

/* Layout responsive */
@media (min-width: 992px) {
    .main-content {
        display: grid;
        grid-template-columns: 7fr 3fr;
        gap: 15px;
    }
    .calendar-and-stats {
        grid-column: 1;
    }
    .links-container {
        grid-column: 2;
    }
    /* Manteniamo 5 icone per riga anche su desktop */
    .link-grid {
        grid-template-columns: repeat(5, 1fr);
        max-height: 400px;
    }
}
@media (max-width: 991px) {
    .main-content {
        display: flex;
        flex-direction: column;
    }
    .link-grid {
        grid-template-columns: repeat(5, 1fr);
    }
}
@media (max-width: 767px) {
    .link-grid {
        grid-template-columns: repeat(4, 1fr);
    }
}
@media (max-width: 576px) {
    .link-grid {
        grid-template-columns: repeat(5, 1fr);
    }
    .days-container {
        grid-template-columns: repeat(7, 1fr);
        overflow-x: auto;
    }
    .stats-cards {
        grid-template-columns: 1fr;
    }
}
.emoji-header {
    font-size: 2rem;
    text-align: center;
    margin: 10px 0;
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
    
    # Layout principale (responsive)
    st.markdown('<div class="main-content">', unsafe_allow_html=True)
    
    # Contenitore per calendario e statistiche
    st.markdown('<div class="calendar-and-stats">', unsafe_allow_html=True)
    
    # Sezione Calendario Settimanale (compatta)
    st.markdown('<div class="calendar-section">', unsafe_allow_html=True)
    st.markdown('<h2 class="calendar-header">📅 Lezioni della Settimana</h2>', unsafe_allow_html=True)
    st.markdown('<div class="days-container">', unsafe_allow_html=True)

    giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
    
    if not st.session_state.giorni_lezione.empty:
        for giorno in giorni:
            st.markdown(f'<div class="day-column">', unsafe_allow_html=True)
            st.markdown(f"<h4 title='{giorno}'>{giorno[:3]}</h4>", unsafe_allow_html=True)

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
                st.markdown("<i style='font-size:0.7rem;'>Nessuna lezione</i>", unsafe_allow_html=True)

            st.markdown('</div>', unsafe_allow_html=True)
    else:
        for giorno in giorni:
            st.markdown(f'<div class="day-column">', unsafe_allow_html=True)
            st.markdown(f"<h4 title='{giorno}'>{giorno[:3]}</h4>", unsafe_allow_html=True)
            st.markdown("<i style='font-size:0.7rem;'>Nessuna lezione</i>", unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sezione statistiche generali (in fondo)
    st.markdown('<div class="stats-section">', unsafe_allow_html=True)
    if 'studenti' in st.session_state and not st.session_state.studenti.empty:
        st.markdown('<h2>📊 Panoramica</h2>', unsafe_allow_html=True)
        st.markdown('<div class="stats-cards">', unsafe_allow_html=True)
        
        num_studenti = len(st.session_state.studenti)
        num_canali = len(st.session_state.studenti['canale'].unique())
        media = round(num_studenti/num_canali, 1) if num_canali > 0 else 0
        
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-value">{num_studenti}</div>
          <div class="stat-label">Totale Studenti</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-value">{num_canali}</div>
          <div class="stat-label">Canali Attivi</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="stat-card">
          <div class="stat-value">{media}</div>
          <div class="stat-label">Media Studenti/Canale</div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("👋 Inizia aggiungendo il tuo primo studente dalla sezione 'Studenti'!")
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
                        <span>{link.titolo}</span>
                    </a>
                    """, unsafe_allow_html=True)
                except Exception as e:
                    st.warning(f"Errore nel caricamento dell'icona per {link.titolo}")
            else:
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
    
    st.markdown('</div>', unsafe_allow_html=True)
