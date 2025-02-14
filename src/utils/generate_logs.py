import os

def generate_logs():
    # Cria o diretório "logs" se ele ainda não existir
    directory_name = "logs"
    os.makedirs(directory_name, exist_ok=True)
    
    # Lista de nomes de arquivos de log
    log_files = [
        "contracts.log",
        "contract_values.log",
        "contract_dates.log",
        "administrative_processes.log",
        "agreements.log",
        "agreement_values.log",
        "agreement_dates.log",
        "accountability.log"
    ]
    
    print("Gerando arquivos de log...");
    # Gera cada arquivo .log caso não exista
    for log_file in log_files:
        filepath = os.path.join(directory_name, log_file)
        if not os.path.exists(filepath):
            with open(filepath, 'w') as file:
                pass  # Cria o arquivo vazio
            print(f"Arquivo '{filepath}' criado");
        else:
            print(f"Arquivo '{filepath}' já existe. Nenhuma ação necessária.");