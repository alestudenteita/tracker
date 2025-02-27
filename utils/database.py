import sqlite3
import pandas as pd
import streamlit as st
from datetime import datetime

def init_db():
    """Inizializza il database e crea le tabelle necessarie"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    try:
        # Create tables in correct order to avoid foreign key issues
        c.execute('''CREATE TABLE IF NOT EXISTS branding_settings
                     (id INTEGER PRIMARY KEY,
                      logo BLOB,
                      welcome_message TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS custom_links
                     (id INTEGER PRIMARY KEY,
                      titolo TEXT NOT NULL,
                      url TEXT NOT NULL,
                      icona BLOB,
                      ordine INTEGER)''')

        c.execute('''CREATE TABLE IF NOT EXISTS studenti
                     (id INTEGER PRIMARY KEY,
                      nome TEXT NOT NULL,
                      cognome TEXT NOT NULL,
                      canale TEXT NOT NULL,
                      livello TEXT NOT NULL,
                      metodologia TEXT,
                      durata_lezione INTEGER,
                      prezzo_lezione REAL NOT NULL,
                      commenti TEXT,
                      data_iscrizione DATE NOT NULL,
                      slides_url TEXT,
                      classroom_url TEXT,
                      meet_url TEXT)''')

        c.execute('''CREATE TABLE IF NOT EXISTS giorni_lezione
                     (id INTEGER PRIMARY KEY,
                      studente_id INTEGER,
                      giorno TEXT NOT NULL,
                      FOREIGN KEY (studente_id) REFERENCES studenti(id))''')

        c.execute('''CREATE TABLE IF NOT EXISTS progressi
                     (id INTEGER PRIMARY KEY,
                      studente_id INTEGER,
                      data DATE NOT NULL,
                      contenuto_id INTEGER,
                      descrizione TEXT NOT NULL,
                      FOREIGN KEY (studente_id) REFERENCES studenti(id),
                      FOREIGN KEY (contenuto_id) REFERENCES libreria(id))''')

        c.execute('''CREATE TABLE IF NOT EXISTS pagamenti
                     (id INTEGER PRIMARY KEY,
                      studente_id INTEGER,
                      data DATE NOT NULL,
                      importo REAL NOT NULL,
                      mese TEXT NOT NULL,
                      anno INTEGER NOT NULL,
                      commenti TEXT,
                      FOREIGN KEY (studente_id) REFERENCES studenti(id))''')

        c.execute('''CREATE TABLE IF NOT EXISTS libreria
                     (id INTEGER PRIMARY KEY,
                      libro TEXT,
                      titolo TEXT NOT NULL,
                      url TEXT NOT NULL,
                      categoria TEXT NOT NULL,
                      livello TEXT NOT NULL,
                      descrizione TEXT)''')
                      
        c.execute('''CREATE TABLE IF NOT EXISTS libri_disponibili
                     (id INTEGER PRIMARY KEY,
                      nome TEXT NOT NULL UNIQUE)''')

        conn.commit()

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


        # Load data
        load_data()

    except Exception as e:
        st.error(f"Errore nell'inizializzazione del database: {str(e)}")
    finally:
        conn.close()

def load_data():
    """Carica i dati dal database nelle session state"""
    conn = sqlite3.connect('data.db')
    try:
        st.session_state.studenti = pd.read_sql_query("SELECT * FROM studenti", conn)
        st.session_state.progressi = pd.read_sql_query("SELECT * FROM progressi", conn)
        st.session_state.libreria = pd.read_sql_query("SELECT * FROM libreria", conn)
        st.session_state.pagamenti = pd.read_sql_query("SELECT * FROM pagamenti", conn)
        st.session_state.custom_links = pd.read_sql_query("SELECT * FROM custom_links", conn)
        st.session_state.giorni_lezione = pd.read_sql_query("""
            SELECT gl.studente_id, gl.giorno, s.nome, s.cognome, s.livello
            FROM giorni_lezione gl
            JOIN studenti s ON gl.studente_id = s.id
        """, conn)
        
        # Carica anche la lista dei libri disponibili
        libri = pd.read_sql_query("SELECT nome FROM libri_disponibili ORDER BY nome", conn)
        if not libri.empty:
            st.session_state.libri_disponibili = set(libri['nome'].tolist())
        else:
            st.session_state.libri_disponibili = set()

    except Exception as e:
        st.error(f"Errore nel caricamento dei dati: {str(e)}")
    finally:
        conn.close()

def add_studente(nome, cognome, canale, livello, metodologia, durata_lezione, prezzo_lezione, 
                commenti, data_iscrizione, slides_url, classroom_url, meet_url, giorni_lezione=None):
    """Aggiunge un nuovo studente al database"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    try:
        c.execute("""INSERT INTO studenti 
                     (nome, cognome, canale, livello, metodologia, durata_lezione, 
                      prezzo_lezione, commenti, data_iscrizione, slides_url, classroom_url, meet_url)
                     VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", 
                  (nome, cognome, canale, livello, metodologia, durata_lezione, 
                   prezzo_lezione, commenti, data_iscrizione, slides_url, classroom_url, meet_url))

        # Get the ID of the newly inserted student
        studente_id = c.lastrowid

        # Insert giorni_lezione if provided
        if giorni_lezione:
            for giorno in giorni_lezione:
                c.execute("""INSERT INTO giorni_lezione (studente_id, giorno)
                           VALUES (?, ?)""", (studente_id, giorno))

        conn.commit()
    except Exception as e:
        st.error(f"Errore nell'aggiunta dello studente: {str(e)}")
    finally:
        conn.close()
    load_data()

def add_custom_link(titolo, url, icona, ordine):
    """Aggiunge un nuovo link personalizzato"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""INSERT INTO custom_links (titolo, url, icona, ordine)
                 VALUES (?, ?, ?, ?)""",
              (titolo, url, icona, ordine))
    conn.commit()
    conn.close()
    load_data()

def update_custom_link(id, titolo, url, icona, ordine):
    """Aggiorna un link personalizzato"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""UPDATE custom_links 
                 SET titolo = ?, url = ?, icona = ?, ordine = ?
                 WHERE id = ?""",
              (titolo, url, icona, ordine, id))
    conn.commit()
    conn.close()
    load_data()

def delete_custom_link(id):
    """Elimina un link personalizzato"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("DELETE FROM custom_links WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    load_data()

def add_progresso(studente_id, data, contenuto_id, descrizione):
    """Aggiunge un nuovo progresso al database"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""INSERT INTO progressi (studente_id, data, contenuto_id, descrizione)
                 VALUES (?, ?, ?, ?)""",
              (studente_id, data, contenuto_id, descrizione))
    conn.commit()
    conn.close()
    load_data()

def add_risorsa(libro, titolo, url, categoria, livello, descrizione):
    """Aggiunge una nuova risorsa alla libreria"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""INSERT INTO libreria (libro, titolo, url, categoria, livello, descrizione)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (libro, titolo, url, categoria, livello, descrizione))
    conn.commit()
    conn.close()
    load_data()
    
def delete_risorsa(id):
    """Elimina una risorsa dalla libreria"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("DELETE FROM libreria WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    load_data()

def add_pagamento(studente_id, data, importo, mese, anno, commenti):
    """Aggiunge un nuovo pagamento al database"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""INSERT INTO pagamenti (studente_id, data, importo, mese, anno, commenti)
                 VALUES (?, ?, ?, ?, ?, ?)""",
              (studente_id, data, importo, mese, anno, commenti))
    conn.commit()
    conn.close()
    load_data()

def update_studente(id, nome, cognome, canale, livello, durata_lezione, prezzo_lezione):
    """Aggiorna i dati di uno studente"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("""UPDATE studenti 
                 SET nome = ?, cognome = ?, canale = ?, livello = ?, 
                     durata_lezione = ?, prezzo_lezione = ?
                 WHERE id = ?""",
              (nome, cognome, canale, livello, durata_lezione, prezzo_lezione, id))
    conn.commit()
    conn.close()
    load_data()

def delete_studente(id):
    """Elimina uno studente dal database"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("DELETE FROM studenti WHERE id = ?", (id,))
    # Elimina anche i progressi e i pagamenti associati
    c.execute("DELETE FROM progressi WHERE studente_id = ?", (id,))
    c.execute("DELETE FROM pagamenti WHERE studente_id = ?", (id,))
    c.execute("DELETE FROM giorni_lezione WHERE studente_id = ?", (id,)) #added to delete from new table
    conn.commit()
    conn.close()
    load_data()

def save_branding_settings(logo_bytes=None, welcome_message=None):
    """Salva le impostazioni di branding"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    # Check if settings exist
    c.execute("SELECT COUNT(*) FROM branding_settings")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO branding_settings (logo, welcome_message) VALUES (?, ?)", 
                 (logo_bytes, welcome_message))
    else:
        c.execute("UPDATE branding_settings SET logo = ?, welcome_message = ?", 
                 (logo_bytes, welcome_message))

    conn.commit()
    conn.close()

def get_branding_settings():
    """Recupera le impostazioni di branding"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()

    c.execute("SELECT logo, welcome_message FROM branding_settings LIMIT 1")
    result = c.fetchone()

    conn.close()
    return result if result else (None, None)

def add_libro_disponibile(nome):
    """Aggiunge un nuovo libro alla lista dei libri disponibili"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO libri_disponibili (nome) VALUES (?)", (nome,))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # Il libro esiste già
        return False
    finally:
        conn.close()

def get_libri_disponibili():
    """Recupera la lista dei libri disponibili"""
    conn = sqlite3.connect('data.db')
    libri = []
    try:
        c = conn.cursor()
        c.execute("SELECT nome FROM libri_disponibili ORDER BY nome")
        libri = [row[0] for row in c.fetchall()]
    finally:
        conn.close()
    return libri

def delete_libro_disponibile(nome):
    """Elimina un libro dalla lista dei libri disponibili"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("DELETE FROM libri_disponibili WHERE nome = ?", (nome,))
    conn.commit()
    conn.close()
    
def delete_pagamento(id):
    """Elimina un pagamento dal database"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("DELETE FROM pagamenti WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    load_data()
    
def delete_progresso(id):
    """Elimina un progresso dal database"""
    conn = sqlite3.connect('data.db')
    c = conn.cursor()
    c.execute("DELETE FROM progressi WHERE id = ?", (id,))
    conn.commit()
    conn.close()
    load_data()