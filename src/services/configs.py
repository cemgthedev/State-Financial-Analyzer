import os
import logging
import logging.config
import yaml

# Caminho absoluto para o diretório de logs
log_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), "../logs"))

# Criar diretório de logs se não existir
os.makedirs(log_directory, exist_ok=True)

# Carregar configuração do arquivo YAML
with open(os.path.abspath(os.path.join(os.path.dirname(__file__), "configs.logs.yaml")), 'r') as file:
    config = yaml.safe_load(file)
    logging.config.dictConfig(config)

# Criar loggers específicos
contracts_logger = logging.getLogger("contracts")
contract_values_logger = logging.getLogger("contract_values")
contract_dates_logger = logging.getLogger("contract_dates")
administrative_processes_logger = logging.getLogger("administrative_processes")
agreements_logger = logging.getLogger("agreements")
agreement_values_logger = logging.getLogger("agreement_values")
agreement_dates_logger = logging.getLogger("agreement_dates")
accountability_logger = logging.getLogger("accountability")
