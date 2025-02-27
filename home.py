import streamlit as st
import pandas as pd
import base64
from utils.supabase_db import init_db, get_branding_settings
from utils.auth import init_auth, check_auth, login, logout

# Importa il componente grid dalla libreria streamlit_extras
from streamlit_extras.grid import grid

st.set_page_config(
    page_title="Gestione Studenti",
    page_icon="📚",
    layout="wide"
)

# Inizializza auth e DB
init_auth()
init_db()

# Inizializza le variabili di sessione
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
if 'studenti' not in st.session_state:
    st.session_state.studenti = pd.DataFrame()
if 'custom_links' not in st.session_state:
    st.session_state.custom_links = pd.DataFrame()
if 'giorni_lezione' not in st.session_state:
    st.session_state.giorni_lezione = pd.DataFrame()

# Stili CSS personalizzati
st.markdown("""
<style>
/* Calendario compatto */
.calendar-section {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 10px;
    margin-bottom: 15px;
}
.days-container {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 5px;
    text-align: center;
}
.day-column {
    background-color: white;
    padding: 5px;
    border-radius: 5px;
    border: 1px solid #e0e0e0;
    font-size: 0.9rem;
}

/* Riquadro per i Quick Links */
.links-section {
    background-color: #f8f9fa;
    border-radius: 10px;
    padding: 15px;
    margin-bottom: 15px;
}
</style>
""", unsafe_allow_html=True)

# Branding
try:
    logo_bytes, welcome_message = get_branding_settings()
except Exception as e:
    st.error(f"Errore nel caricamento delle impostazioni: {str(e)}")
    logo_bytes, welcome_message = None, None

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
    st.markdown('<div style="max-width: 1200px; margin:auto;">', unsafe_allow_html=True)
    
    # Header con logo e logout
    st.markdown('<div style="position: relative; text-align: center; margin-bottom: 15px;">', unsafe_allow_html=True)
    if logo_bytes:
        try:
            st.image(logo_bytes, width=160)
        except:
            st.markdown("<div style='font-size:2rem;'>📚 💬 🎓</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:2rem;'>📚 💬 🎓</div>", unsafe_allow_html=True)
    st.markdown('<div style="position: absolute; right: 10px; top: 50%; transform: translateY(-50%);">', unsafe_allow_html=True)
    if st.button("Logout"):
        logout()
        st.rerun()
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Calendario compatto in griglia (7 colonne)
    st.markdown('<div class="calendar-section">', unsafe_allow_html=True)
    st.markdown('<h2 style="text-align: center;">📅 Lezioni Settimanali</h2>', unsafe_allow_html=True)
    st.markdown('<div class="days-container">', unsafe_allow_html=True)
    giorni = ["Lun", "Mar", "Mer", "Gio", "Ven", "Sab", "Dom"]
    for giorno in giorni:
        st.markdown(f'<div class="day-column">{giorno}</div>', unsafe_allow_html=True)
    st.markdown('</div></div>', unsafe_allow_html=True)
    
    # Quick Links: utilizzo del componente Grid per una griglia a 5 colonne
    st.markdown('<div class="links-section">', unsafe_allow_html=True)
    if not st.session_state.custom_links.empty:
        ordered_links = st.session_state.custom_links.sort_values('ordine')
        # Crea un grid a 5 colonne; se ci sono più elementi verranno create nuove righe automaticamente
        my_grid = grid(5, gap="small", vertical_align="top")
        for _, link in ordered_links.iterrows():
            # Prepara l'icona
            if link.icona:
                try:
                    if isinstance(link.icona, bytes):
                        encoded_image = base64.b64encode(link.icona).decode()
                    elif isinstance(link.icona, str):
                        encoded_image = link.icona
                    else:
                        raise ValueError("Formato icona non supportato")
                    image_html = f'<img src="data:image/png;base64,{encoded_image}" alt="{link.titolo}" style="width:40px;height:40px;display:block;margin:0 auto;"/>'
                except Exception as e:
                    image_html = '🔗'
            else:
                image_html = '🔗'
            cell_content = f"{image_html}<br><span style='font-size:0.85rem;text-align:center;'>{link.titolo}</span>"
            my_grid.markdown(cell_content, unsafe_allow_html=True)
    else:
        st.info("🔗 Aggiungi i tuoi link rapidi nella sezione Impostazioni")
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Sezione statistiche (opzionale)
    st.markdown('<div style="background-color:#f8f9fa; border-radius:10px; padding:15px; margin-top:10px;">', unsafe_allow_html=True)
    if 'studenti' in st.session_state and not st.session_state.studenti.empty:
        st.markdown('<h2 style="text-align:center;">📊 Panoramica</h2>', unsafe_allow_html=True)
        num_studenti = len(st.session_state.studenti)
        num_canali = len(st.session_state.studenti['canale'].unique())
        media = round(num_studenti/num_canali, 1) if num_canali > 0 else 0
        col1, col2, col3 = st.columns(3)
        col1.metric("Totale Studenti", num_studenti)
        col2.metric("Canali Attivi", num_canali)
        col3.metric("Media Studenti/Canale", media)
    else:
        st.info("👋 Inizia aggiungendo il tuo primo studente dalla sezione 'Studenti'!")
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
