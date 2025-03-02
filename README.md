# State-Financial-Analyzer
Projeto da disciplina de Desenvolvimento de Software para Persistência. Trata-se de uma REST API utilizando o framework FastAPI e SQLModel do python consistindo em uma aplicação para persistir dados de contratos e convênios públicos no Ceará.

# Migrações

- Inicialize o alembic:
  ```sh
  alembic init alembic
  ```
- No arquivo `alembic.ini`, configure o `sqlalchemy.url` com as informações do banco de dados. Exemplo:
  ```ini
  sqlalchemy.url = postgresql://postgres:12345678@localhost:5432/sfa
  ```
- No arquivo `env.py`, adicione `SQLModel.metadata` como valor da variável `target_metadata` e `from src.models import *` para importação dos modelos.
- Gere a migração (na configuração do banco de dados e após alterações nas entidades) o bd deve existir na sua máquina:
  ```sh
  alembic revision --autogenerate -m "título da migração"
  ```
- Aplique as alterações ao banco de dados:
  ```sh
  alembic upgrade head
  ```

# Executando

- Criar um ambiente virtual:
  ```sh
  python -m venv .venv
  ```
- Ativar o ambiente no prompt de comando do Windows:
  ```sh
  .venv\Scripts\activate
  ```
- Instalar bibliotecas:
  ```sh
  pip install -r requirements.txt
  ```
- Entrar na pasta `src`:
  ```sh
  cd src
  ```
- Executar o servidor:
  ```sh
  uvicorn main:app --reload
  ```