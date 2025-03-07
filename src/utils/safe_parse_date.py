import pandas as pd

def safe_parse_date(date_str):
    try:
        if pd.notna(date_str):
            parsed_date = pd.to_datetime(date_str, errors='coerce')
            if pd.notna(parsed_date):
                print(parsed_date)
                return parsed_date.date()
        return None
    except Exception as e:
        print(f"Erro ao converter data: {date_str} - {e}")
        return None