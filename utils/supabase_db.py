
import streamlit as st
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv
from supabase import create_client, Client

# Try to load from .env file (for local development)
load_dotenv()

# Initialize Supabase client - check Streamlit secrets first, then environment variables
if "SUPABASE_URL" in st.secrets:
    # Streamlit Cloud - use secrets
    supabase_url = st.secrets["SUPABASE_URL"]
    supabase_key = st.secrets["SUPABASE_KEY"]
else:
    # Local development - use environment variables
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = os.environ.get("SUPABASE_KEY")

if not supabase_url or not supabase_key:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment variables or Streamlit secrets")

supabase: Client = create_client(supabase_url, supabase_key)

def create_tables():
    """Verify database tables exist"""
    tables_exist = True
    missing_tables = []
    
    # Lista di tutte le tabelle necessarie
    required_tables = [
        "studenti", "giorni_lezione", "libreria", "progressi", 
        "pagamenti", "custom_links", "branding_settings", "libri_disponibili"
    ]
    
    # Verifica ogni tabella
    for table_name in required_tables:
        try:
            # Verifica che la tabella esista tentando di selezionare solo l'id
            # Evita l'uso di funzioni come count(*) che non sono supportate direttamente
            response = supabase.table(table_name).select("id").limit(1).execute()
            # Se arriviamo qui senza eccezioni, la tabella esiste
        except Exception as e:
            tables_exist = False
            missing_tables.append(table_name)
            st.error(f"Errore nella verifica della tabella {table_name}: {str(e)}")
    
    # Se mancano tabelle, mostra un messaggio
    if not tables_exist:
        st.error(f"""
            Le seguenti tabelle non sono state trovate: {', '.join(missing_tables)}
            
            Verifica che tutte le tabelle siano create correttamente in Supabase.
        """)
        return False
        
    return True

def init_db():
    """Initialize session state variables"""
    # Verifica che le tabelle esistano
    tables_ok = create_tables()
    
    # Initialize session states
    if 'studenti' not in st.session_state:
        st.session_state.studenti = pd.DataFrame(columns=[
            'id', 'nome', 'cognome', 'canale', 'livello', 
            'metodologia', 'durata_lezione', 'prezzo_lezione', 'commenti', 
            'data_iscrizione', 'slides_url', 'classroom_url', 'meet_url'
        ])
    if 'progressi' not in st.session_state:
        st.session_state.progressi = pd.DataFrame(columns=[
            'id', 'studente_id', 'data', 'contenuto_id', 'descrizione'
        ])
    if 'libreria' not in st.session_state:
        st.session_state.libreria = pd.DataFrame(columns=[
            'id', 'libro', 'titolo', 'url', 'categoria', 'livello', 'descrizione'
        ])
    if 'pagamenti' not in st.session_state:
        st.session_state.pagamenti = pd.DataFrame(columns=[
            'id', 'studente_id', 'data', 'importo', 'mese', 'anno', 'commenti'
        ])
    if 'custom_links' not in st.session_state:
        st.session_state.custom_links = pd.DataFrame(columns=[
            'id', 'titolo', 'url', 'icona', 'ordine'
        ])
    if 'branding_settings' not in st.session_state:
        st.session_state.branding_settings = pd.DataFrame(columns=['id', 'logo', 'welcome_message'])
    
    # Carica i dati solo se le tabelle esistono
    if tables_ok:
        try:
            load_data()
        except Exception as e:
            st.error(f"Errore nel caricamento dei dati: {str(e)}")
            st.info("Prova a rigenerare le tabelle nel database Supabase con i nomi e i campi corretti.")

def load_data():
    """Load data from Supabase into session state"""
    try:
        # Load studenti
        response = supabase.table('studenti').select('*').execute()
        if response.data:
            st.session_state.studenti = pd.DataFrame(response.data)
        
        # Load progressi
        response = supabase.table('progressi').select('*').execute()
        if response.data:
            st.session_state.progressi = pd.DataFrame(response.data)
        
        # Load libreria
        response = supabase.table('libreria').select('*').execute()
        if response.data:
            st.session_state.libreria = pd.DataFrame(response.data)
        
        # Load pagamenti
        response = supabase.table('pagamenti').select('*').execute()
        if response.data:
            st.session_state.pagamenti = pd.DataFrame(response.data)
        
        # Load custom_links
        response = supabase.table('custom_links').select('*').execute()
        if response.data:
            st.session_state.custom_links = pd.DataFrame(response.data)
        
        # Load giorni_lezione
        response = supabase.table('giorni_lezione').select('id,studente_id,giorno').execute()
        if response.data:
            st.session_state.giorni_lezione = pd.DataFrame(response.data)
        else:
            st.session_state.giorni_lezione = pd.DataFrame(columns=['id', 'studente_id', 'giorno'])
        
        # Load libri_disponibili
        response = supabase.table('libri_disponibili').select('nome').execute()
        if response.data:
            st.session_state.libri_disponibili = set([item['nome'] for item in response.data])
        else:
            st.session_state.libri_disponibili = set()
            
        # Load branding settings
        response = supabase.table('branding_settings').select('*').execute()
        if response.data and len(response.data) > 0:
            st.session_state.branding_settings = pd.DataFrame([response.data[0]])
    
    except Exception as e:
        st.error(f"Errore nel caricamento dei dati: {str(e)}")

def add_studente(nome, cognome, canale, livello, metodologia, durata_lezione, prezzo_lezione, 
                commenti, data_iscrizione, slides_url, classroom_url, meet_url, giorni_lezione=None):
    """Add a new student to Supabase"""
    try:
        # Crea un container per i messaggi di debug, visibile solo se attivo
        debug_container = None
        if st.session_state.get("show_debug", False):
            debug_container = st.container()
            with debug_container:
                st.write("⚙️ DEBUG: Inizio procedura inserimento studente...")
        
        # Insert studente
        studente_data = {
            'nome': nome,
            'cognome': cognome,
            'canale': canale,
            'livello': livello,
            'metodologia': metodologia,
            'durata_lezione': durata_lezione,
            'prezzo_lezione': prezzo_lezione,
            'commenti': commenti,
            'data_iscrizione': data_iscrizione.isoformat(),
            'slides_url': slides_url,
            'classroom_url': classroom_url,
            'meet_url': meet_url
        }
        
        # Log dati solo in modalità debug
        if debug_container:
            with debug_container:
                st.write(f"⚙️ DEBUG: Dati studente da inserire: {studente_data}")
        
        # Inserimento effettivo - conversione esplicita delle date in formato ISO e validazione dei campi
        studente_data['data_iscrizione'] = str(data_iscrizione.isoformat())
        
        # Rimuovi campi vuoti o None che potrebbero causare problemi
        studente_data = {k: v for k, v in studente_data.items() if v is not None and v != ""}
        
        # Debug dei dati effettivamente inviati solo in modalità debug
        if debug_container:
            with debug_container:
                st.write(f"⚙️ DEBUG: Dati studente da inserire (formato finale): {studente_data}")
        
        # In Supabase, gli ID sono spesso di tipo UUID e vengono generati automaticamente
        # Rimuoviamo la gestione manuale dell'ID per lasciare che sia Supabase a gestirlo
        try:
            if debug_container:
                with debug_container:
                    st.write(f"⚙️ DEBUG: Utilizzo UUID generato da Supabase")
        except Exception as e:
            if debug_container:
                with debug_container:
                    st.write(f"⚙️ DEBUG: Errore: {str(e)}")
        
        response = supabase.table('studenti').insert(studente_data).execute()
        if debug_container:
            with debug_container:
                st.write(f"⚙️ DEBUG: Risposta Supabase: {response}")
        
        if response and response.data:
            studente_id = response.data[0]['id']
            
            # Mostra info di debug solo se attivo
            if debug_container:
                with debug_container:
                    st.write(f"⚙️ DEBUG: Studente inserito con ID: {studente_id}")
            
            # Insert giorni_lezione if provided
            if giorni_lezione:
                if debug_container:
                    with debug_container:
                        st.write(f"⚙️ DEBUG: Inserimento giorni lezione: {giorni_lezione}")
                
                for giorno in giorni_lezione:
                    giorno_response = supabase.table('giorni_lezione').insert({
                        'studente_id': studente_id,
                        'giorno': giorno
                    }).execute()
                    
                    if debug_container:
                        with debug_container:
                            st.write(f"⚙️ DEBUG: Giorno {giorno} inserito con risposta: {giorno_response}")
            
            # Ricarica i dati
            if debug_container:
                with debug_container:
                    st.write("⚙️ DEBUG: Ricaricamento dati...")
            
            load_data()
            
            # Verifica finale solo in modalità debug
            if debug_container:
                with debug_container:
                    st.write("⚙️ DEBUG: Verifica dati studenti in session_state...")
                    if hasattr(st.session_state, 'studenti') and not st.session_state.studenti.empty:
                        ultimo_studente = st.session_state.studenti[st.session_state.studenti['id'] == studente_id]
                        if not ultimo_studente.empty:
                            st.write(f"⚙️ DEBUG: Studente trovato in session_state: {ultimo_studente.iloc[0].to_dict()}")
                        else:
                            st.write("⚙️ DEBUG: Studente NON trovato in session_state dopo inserimento!")
            
            # Messaggio di successo standardizzato
            st.success("🌞 Salvato nella nuvola ✅")
            return True
        else:
            # Messaggio di errore standardizzato
            st.error("🌧️ Piove ❌ Risposta vuota dal database")
            return False
    except Exception as e:
        error_msg = str(e)
        
        # Crea un container di debug solo se necessario
        if st.session_state.get("show_debug", False):
            debug_container = st.container()
            with debug_container:
                st.write(f"⚙️ DEBUG: Errore catturato: {error_msg}")
                
                # Mostra dettagli completi dell'errore in debug
                import traceback
                st.write(f"⚙️ DEBUG: Traceback completo:\n{traceback.format_exc()}")
        
        # Messaggio di errore standardizzato
        error_text = "Errore nell'aggiunta dello studente"
        if "duplicate key" in error_msg.lower():
            error_text = "Studente già esistente nel database"
        elif "foreign key constraint" in error_msg.lower():
            error_text = "Riferimento a dati non esistenti"
        elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            error_text = "Problema di connessione con il database"
        elif "permission" in error_msg.lower() or "not authorized" in error_msg.lower():
            error_text = "Permessi insufficienti per questa operazione"
        elif "400" in error_msg.lower() or "bad request" in error_msg.lower():
            error_text = "Formato dati non valido (Errore 400). Controlla i valori inseriti."
        elif "null value in column" in error_msg.lower() and "violates not-null constraint" in error_msg.lower():
            error_text = "Campo obbligatorio mancante"
        else:
            # In modalità non-debug, mostra un messaggio generico
            if not st.session_state.get("show_debug", False):
                error_text = "Errore nell'aggiunta dello studente. Attiva la modalità debug per maggiori dettagli."
            else:
                error_text = f"Errore nell'aggiunta dello studente: {error_msg}"
            
        st.error(f"🌧️ Piove ❌ {error_text}")
        return False

def add_custom_link(titolo, url, icona, ordine):
    """Add a new custom link to Supabase"""
    try:
        supabase.table('custom_links').insert({
            'titolo': titolo,
            'url': url,
            'icona': icona,
            'ordine': ordine
        }).execute()
        load_data()
        st.success("🌞 Salvato nella nuvola ✅")
        return True
    except Exception as e:
        error_msg = str(e)
        if "duplicate key" in error_msg.lower():
            st.error("🌧️ Piove ❌ Link già esistente nel database")
        elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            st.error("🌧️ Piove ❌ Problema di connessione con il database")
        else:
            st.error(f"🌧️ Piove ❌ Errore nell'aggiunta del link: {error_msg}")
        return False

def update_custom_link(id, titolo, url, icona, ordine):
    """Update a custom link in Supabase"""
    try:
        supabase.table('custom_links').update({
            'titolo': titolo,
            'url': url,
            'icona': icona,
            'ordine': ordine
        }).eq('id', id).execute()
        load_data()
        st.success("🌞 Salvato nella nuvola ✅")
        return True
    except Exception as e:
        error_msg = str(e)
        if "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            st.error("🌧️ Piove ❌ Problema di connessione con il database")
        elif "not found" in error_msg.lower():
            st.error("🌧️ Piove ❌ Link non trovato nel database")
        else:
            st.error(f"🌧️ Piove ❌ Errore nell'aggiornamento del link: {error_msg}")
        return False

def delete_custom_link(id):
    """Delete a custom link from Supabase"""
    try:
        supabase.table('custom_links').delete().eq('id', id).execute()
        load_data()
        st.success("🌞 Eliminato dalla nuvola ✅")
        return True
    except Exception as e:
        st.error(f"🌧️ Piove ❌ Errore nell'eliminazione del link: {str(e)}")
        return False

def add_progresso(studente_id, data, contenuto_id, descrizione):
    """Add a new progress record to Supabase"""
    try:
        supabase.table('progressi').insert({
            'studente_id': studente_id,
            'data': data.isoformat(),
            'contenuto_id': contenuto_id,
            'descrizione': descrizione
        }).execute()
        load_data()
        st.success("🌞 Salvato nella nuvola ✅")
        return True
    except Exception as e:
        error_msg = str(e)
        if "foreign key constraint" in error_msg.lower():
            st.error("🌧️ Piove ❌ Studente non trovato nel database")
        elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            st.error("🌧️ Piove ❌ Problema di connessione con il database")
        else:
            st.error(f"🌧️ Piove ❌ Errore nell'aggiunta del progresso: {error_msg}")
        return False

def add_risorsa(libro, titolo, url, categoria, livello, descrizione):
    """Add a new resource to Supabase library"""
    try:
        supabase.table('libreria').insert({
            'libro': libro,
            'titolo': titolo,
            'url': url,
            'categoria': categoria,
            'livello': livello,
            'descrizione': descrizione
        }).execute()
        load_data()
        st.success("🌞 Salvato nella nuvola ✅")
        return True
    except Exception as e:
        error_msg = str(e)
        if "duplicate key" in error_msg.lower():
            st.error("🌧️ Piove ❌ Risorsa già esistente nel database")
        elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            st.error("🌧️ Piove ❌ Problema di connessione con il database")
        else:
            st.error(f"🌧️ Piove ❌ Errore nell'aggiunta della risorsa: {error_msg}")
        return False
    
def delete_risorsa(id):
    """Delete a resource from Supabase library"""
    try:
        supabase.table('libreria').delete().eq('id', id).execute()
        load_data()
        st.success("🌞 Eliminato dalla nuvola ✅")
        return True
    except Exception as e:
        st.error(f"🌧️ Piove ❌ Errore nell'eliminazione della risorsa: {str(e)}")
        return False

def add_pagamento(studente_id, data, importo, mese, anno, commenti):
    """Add a new payment to Supabase"""
    try:
        supabase.table('pagamenti').insert({
            'studente_id': studente_id,
            'data': data.isoformat(),
            'importo': importo,
            'mese': mese,
            'anno': anno,
            'commenti': commenti
        }).execute()
        load_data()
        st.success("🌞 Salvato nella nuvola ✅")
        return True
    except Exception as e:
        error_msg = str(e)
        if "foreign key constraint" in error_msg.lower():
            st.error("🌧️ Piove ❌ Studente non trovato nel database")
        elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
            st.error("🌧️ Piove ❌ Problema di connessione con il database")
        elif "invalid input syntax" in error_msg.lower():
            st.error("🌧️ Piove ❌ Formato dei dati non valido")
        else:
            st.error(f"🌧️ Piove ❌ Errore nell'aggiunta del pagamento: {error_msg}")
        return False

def update_studente(id, nome, cognome, canale, livello, durata_lezione, prezzo_lezione):
    """Update student info in Supabase"""
    try:
        supabase.table('studenti').update({
            'nome': nome,
            'cognome': cognome,
            'canale': canale,
            'livello': livello,
            'durata_lezione': durata_lezione,
            'prezzo_lezione': prezzo_lezione
        }).eq('id', id).execute()
        load_data()
        st.success("🌞 Salvato nella nuvola ✅")
        return True
    except Exception as e:
        st.error(f"🌧️ Piove ❌ Errore nell'aggiornamento dello studente: {str(e)}")
        return False

def delete_studente(id):
    """Delete a student and related records from Supabase"""
    try:
        # Delete child records first to maintain referential integrity
        supabase.table('progressi').delete().eq('studente_id', id).execute()
        supabase.table('pagamenti').delete().eq('studente_id', id).execute()
        supabase.table('giorni_lezione').delete().eq('studente_id', id).execute()
        
        # Then delete the student
        supabase.table('studenti').delete().eq('id', id).execute()
        load_data()
        st.success("🌞 Eliminato dalla nuvola ✅")
        return True
    except Exception as e:
        st.error(f"🌧️ Piove ❌ Errore nell'eliminazione dello studente: {str(e)}")
        return False

def save_branding_settings(logo_bytes=None, welcome_message=None):
    """Save branding settings to Supabase"""
    try:
        # Check if settings exist
        response = supabase.table('branding_settings').select('id').execute()
        if response.data and len(response.data) > 0:
            # Update existing record
            supabase.table('branding_settings').update({
                'logo': logo_bytes,
                'welcome_message': welcome_message
            }).eq('id', response.data[0]['id']).execute()
        else:
            # Insert new record
            supabase.table('branding_settings').insert({
                'logo': logo_bytes,
                'welcome_message': welcome_message
            }).execute()
        load_data()
        st.success("🌞 Salvato nella nuvola ✅")
        return True
    except Exception as e:
        st.error(f"🌧️ Piove ❌ Errore nel salvataggio delle impostazioni: {str(e)}")
        return False

def get_branding_settings():
    """Get branding settings from Supabase"""
    try:
        response = supabase.table('branding_settings').select('logo, welcome_message').execute()
        if response.data and len(response.data) > 0:
            return response.data[0]['logo'], response.data[0]['welcome_message']
        return None, None
    except Exception as e:
        st.error(f"Errore nel recupero delle impostazioni: {str(e)}")
        return None, None

def add_libro_disponibile(nome):
    """Add a new book to Supabase available books list"""
    try:
        # Check if book already exists
        response = supabase.table('libri_disponibili').select('nome').eq('nome', nome).execute()
        if response.data and len(response.data) > 0:
            return False  # Book already exists
        
        supabase.table('libri_disponibili').insert({'nome': nome}).execute()
        load_data()
        st.success("🌞 Salvato nella nuvola ✅")
        return True
    except Exception as e:
        st.error(f"🌧️ Piove ❌ Errore nell'aggiunta del libro: {str(e)}")
        return False

def get_libri_disponibili():
    """Get available books from Supabase"""
    try:
        response = supabase.table('libri_disponibili').select('nome').order('nome').execute()
        return [item['nome'] for item in response.data]
    except Exception as e:
        st.error(f"Errore nel recupero dei libri: {str(e)}")
        return []

def delete_libro_disponibile(nome):
    """Delete a book from Supabase available books list"""
    try:
        supabase.table('libri_disponibili').delete().eq('nome', nome).execute()
        load_data()
        st.success("🌞 Eliminato dalla nuvola ✅")
        return True
    except Exception as e:
        st.error(f"🌧️ Piove ❌ Errore nell'eliminazione del libro: {str(e)}")
        return False
    
def delete_pagamento(id):
    """Delete a payment from Supabase"""
    try:
        supabase.table('pagamenti').delete().eq('id', id).execute()
        load_data()
        st.success("🌞 Eliminato dalla nuvola ✅") 
        return True
    except Exception as e:
        st.error(f"🌧️ Piove ❌ Errore nell'eliminazione del pagamento: {str(e)}")
        return False
    
def delete_progresso(id):
    """Delete a progress record from Supabase"""
    try:
        supabase.table('progressi').delete().eq('id', id).execute()
        load_data()
        st.success("🌞 Eliminato dalla nuvola ✅")
        return True
    except Exception as e:
        st.error(f"🌧️ Piove ❌ Errore nell'eliminazione del progresso: {str(e)}")
        return False
