import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

def create_monthly_stats(df):
    """Crea statistiche mensili dai dati degli studenti"""
    df['data_iscrizione'] = pd.to_datetime(df['data_iscrizione'])
    monthly_stats = df.groupby(df['data_iscrizione'].dt.strftime('%Y-%m'))\
                     .agg({'id': 'count', 'prezzo': 'sum'})\
                     .reset_index()
    monthly_stats.columns = ['mese', 'nuovi_studenti', 'ricavi']
    return monthly_stats

def create_class_distribution(df):
    """Crea grafico della distribuzione degli studenti per classe"""
    class_dist = df['classe'].value_counts()
    fig = px.pie(values=class_dist.values, 
                 names=class_dist.index,
                 title='Distribuzione Studenti per Classe')
    return fig

def create_revenue_trend(df):
    """Crea grafico del trend dei ricavi"""
    monthly_stats = create_monthly_stats(df)
    fig = px.line(monthly_stats, 
                  x='mese', 
                  y='ricavi',
                  title='Trend Ricavi Mensili')
    return fig

def filter_dataframe(df, filters):
    """Filtra un DataFrame in base ai criteri specificati"""
    filtered_df = df.copy()
    
    for column, value in filters.items():
        if value:
            if isinstance(value, (list, tuple)):
                filtered_df = filtered_df[filtered_df[column].isin(value)]
            else:
                filtered_df = filtered_df[filtered_df[column] == value]
    
    return filtered_df
