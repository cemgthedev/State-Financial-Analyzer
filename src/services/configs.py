import logging
import logging.config
import yaml
from utils.generate_logs import generate_logs

# Inicializando arquivos de logs
generate_logs();

# Carregar configuração do arquivo YAML
with open('./services/configs.logs.yaml', 'r') as file:
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