import streamlit as st
import base64
from utils.supabase_db import (save_branding_settings, add_custom_link, update_custom_link, delete_custom_link,
                          get_branding_settings)
from utils.image_processor import process_upload_image

st.set_page_config(page_title="Impostazioni", page_icon="⚙️")

# Inizializza la variabile se non esiste
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.warning("Effettua il login per accedere a questa pagina")
    st.stop()

st.title("⚙️ Impostazioni")

# Sezione Branding
st.header("🎨 Branding")

current_logo, current_message = get_branding_settings()

col1, col2 = st.columns(2)
with col1:
    logo = st.file_uploader(
        "Logo del sito",
        type=['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff'],
        help="Carica un'immagine per il logo del sito. L'immagine verrà mantenuta in alta risoluzione."
    )
    if logo:
        processed_logo, error = process_upload_image(logo, keep_original=True)
        if processed_logo:
            st.image(processed_logo)
            st.success("Logo processato con successo!")
        else:
            st.error(error)
            logo = None
    elif current_logo:
        try:
            st.image(current_logo)
            st.info("Logo attuale")
            if st.button("🗑️ Elimina logo"):
                save_branding_settings(None, current_message)
                st.success("Logo eliminato con successo!")
                st.rerun()
        except:
            st.warning("Logo attuale non visualizzabile")

with col2:
    welcome_message = st.text_area(
        "Messaggio di benvenuto",
        value=current_message if current_message else "",
        help="Questo messaggio verrà mostrato nella pagina di login"
    )

if st.button("💾 Salva Impostazioni Branding"):
    try:
        save_branding_settings(
            processed_logo if logo else current_logo,
            welcome_message
        )
        st.success("✅ Impostazioni di branding salvate con successo!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Errore nel salvare le impostazioni: {str(e)}")

# Gestione Link Personalizzati
st.header("🔗 Gestione Link Utili")

# Form per aggiungere nuovo link
col1, col2 = st.columns(2)
with col1:
    titolo = st.text_input("Titolo del Link")
    url = st.text_input("URL")
with col2:
    icona = st.file_uploader(
        "Icona del link",
        type=['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff'],
        help="Carica un'icona per il link. Verrà ottimizzata automaticamente."
    )
    if icona:
        processed_image, error = process_upload_image(icona, keep_original=False)
        if processed_image:
            st.image(processed_image, width=48)
            st.success("Icona processata con successo!")
        else:
            st.error(error)
            icona = None
    ordine = st.number_input("Ordine di visualizzazione", min_value=1, step=1)

if st.button("➕ Aggiungi Link") and titolo and url:
    try:
        # Converti l'immagine in base64 prima di salvarla
        import base64
        image_base64 = base64.b64encode(processed_image).decode('utf-8') if processed_image else None
        add_custom_link(titolo, url, image_base64 if icona else None, ordine)
        st.success("✅ Link aggiunto con successo!")
        st.rerun()
    except Exception as e:
        st.error(f"❌ Errore durante l'aggiunta del link: {str(e)}")

# Lista dei link esistenti
if not st.session_state.custom_links.empty:
    st.subheader("Link Esistenti")
    for _, link in st.session_state.custom_links.iterrows():
        cols = st.columns([3, 1, 1])
        with cols[0]:
            st.write(f"**{link['titolo']}** - {link['url']}")
            if link['icona']:
                try:
                    st.image(base64.b64decode(link['icona']), width=48) # Decode base64 image for display
                except:
                    st.warning("⚠️ Icona non visualizzabile")
        with cols[1]:
            if st.button("✏️ Modifica", key=f"edit_{link['id']}"):
                st.session_state.editing_link = link['id']
        with cols[2]:
            if st.button("🗑️ Elimina", key=f"del_{link['id']}"):
                delete_custom_link(link['id'])
                st.success("Link eliminato!")
                st.rerun()

        # Form di modifica
        if st.session_state.get('editing_link') == link['id']:
            with st.container():
                nuovo_titolo = st.text_input("Nuovo titolo", value=link['titolo'], key=f"title_{link['id']}")
                nuovo_url = st.text_input("Nuovo URL", value=link['url'], key=f"url_{link['id']}")
                nuova_icona = st.file_uploader("Nuova icona", type=['png', 'jpg', 'jpeg', 'gif', 'webp', 'bmp', 'tiff'], key=f"icon_{link['id']}")
                if nuova_icona:
                    processed_image, error = process_upload_image(nuova_icona, keep_original=False)
                    if processed_image:
                        st.image(processed_image, width=48)
                        st.success("Nuova icona processata con successo!")
                    else:
                        st.error(error)
                        nuova_icona = None
                nuovo_ordine = st.number_input("Nuovo ordine", value=link['ordine'], min_value=1, step=1, key=f"order_{link['id']}")

                if st.button("💾 Salva modifiche", key=f"save_{link['id']}"):
                    try:
                        # Encode the image as base64 before updating
                        import base64
                        image_base64 = base64.b64encode(processed_image).decode('utf-8') if nuova_icona else link['icona']
                        update_custom_link(
                            link['id'],
                            nuovo_titolo,
                            nuovo_url,
                            image_base64,
                            nuovo_ordine
                        )
                        st.success("✅ Link aggiornato!")
                        st.session_state.editing_link = None
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Errore durante l'aggiornamento del link: {str(e)}")
