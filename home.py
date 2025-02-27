import streamlit as st
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
    st.session_state.authenticated = True  # Temporarily set to True to show layout

if 'studenti' not in st.session_state:
    st.session_state.studenti = pd.DataFrame()

if 'custom_links' not in st.session_state:
    st.session_state.custom_links = pd.DataFrame()

if 'giorni_lezione' not in st.session_state:
    st.session_state.giorni_lezione = pd.DataFrame()

# CSS styles for layout
st.markdown("""
<style>
.header-section {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 30px;
}
.brand-logo {
    text-align: center;
    margin: 0 auto 20px auto;
    padding: 10px;
}
.brand-logo img {
    max-width: 180px;
    height: auto;
}
.link-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 15px;
    padding: 10px 0;
    margin: 20px 0;
}
.custom-link {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
    text-decoration: none;
    color: inherit;
    padding: 15px;
    background: #f8f9fa;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    transition: transform 0.2s, box-shadow 0.2s;
    height: 100px;
}
.custom-link:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}
.custom-link .icon {
    width: 40px;
    height: 40px;
    margin-bottom: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
}
.custom-link .icon img {
    width: 100%;
    height: 100%;
    object-fit: contain;
}
.custom-link .icon-emoji {
    font-size: 32px;
    line-height: 1;
}
.custom-link .link-title {
    font-size: 0.9em;
    color: #333;
    font-weight: 500;
    margin-top: 8px;
}
.content-section {
    background-color: white;
    padding: 20px;
    border-radius: 10px;
}
.stats-section {
    margin-bottom: 30px;
    padding: 20px;
    background-color: #f8f9fa;
    border-radius: 10px;
}
.calendar-section {
    padding: 20px;
    background-color: #f8f9fa;
    border-radius: 10px;
}
.calendar-grid {
    display: grid;
    grid-template-columns: repeat(7, 1fr);
    gap: 10px;
    width: 100%;
}
.day-column {
    background-color: white;
    padding: 12px;
    border-radius: 5px;
    text-align: center;
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
.logout-section {
    text-align: right;
    margin-top: 10px;
}
</style>
""", unsafe_allow_html=True)

# Header Section
st.markdown('<div class="header-section">', unsafe_allow_html=True)

# Brand Logo
st.markdown('<div class="brand-logo">', unsafe_allow_html=True)
st.markdown("📚", unsafe_allow_html=True)  # Placeholder emoji for logo
st.markdown('</div>', unsafe_allow_html=True)

# Quick Links Grid
st.markdown('<div class="link-grid">', unsafe_allow_html=True)
for i in range(5):
    st.markdown(f"""
    <a href="#" class="custom-link">
        <div class="icon">
            <div class="icon-emoji">🔗</div>
        </div>
        <div class="link-title">Link {i+1}</div>
    </a>
    """, unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Logout Button
st.markdown('<div class="logout-section">', unsafe_allow_html=True)
if st.button("Logout"):
    st.session_state.authenticated = False
    st.rerun()
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)

# Content Section
st.markdown('<div class="content-section">', unsafe_allow_html=True)

# Stats Section
st.markdown('<div class="stats-section">', unsafe_allow_html=True)
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Totale Studenti", "0")
with col2:
    st.metric("Canali Attivi", "0")
with col3:
    st.metric("Media Studenti/Canale", "0")
st.markdown('</div>', unsafe_allow_html=True)

# Calendar Section
st.markdown('<div class="calendar-section">', unsafe_allow_html=True)
st.markdown('<div class="calendar-grid">', unsafe_allow_html=True)

giorni = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
for giorno in giorni:
    st.markdown(f'<div class="day-column">', unsafe_allow_html=True)
    st.markdown(f"<h4>{giorno}</h4>", unsafe_allow_html=True)
    st.markdown("<i>Nessuna lezione</i>", unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div></div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
