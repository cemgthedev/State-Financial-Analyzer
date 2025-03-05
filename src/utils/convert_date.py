from datetime import datetime
import pandas as pd

'''
Converte uma data no formato dd/mm/aaaa para o formato datetime
'''
def convert_date(date_value):
    """
    Converte um valor de data para datetime, lidando com diferentes tipos de entrada.
    """
    if pd.isna(date_value):  # Verifica se é NaN e retorna None
        return None

    if isinstance(date_value, datetime):  # Se já for datetime, retorna diretamente
        return date_value

    if isinstance(date_value, pd.Timestamp):  # Se for Timestamp, converte para string
        date_value = date_value.strftime("%d/%m/%Y")  

    return datetime.strptime(date_value, "%d/%m/%Y")  # Converte string para datetime