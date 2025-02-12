from sqlmodel import SQLModel, Session, create_engine
from models import *

# Configuração da URL do banco de dados
DATABASE_URL = "postgresql://postgres:12345678@localhost:5432/sfa"

# Criação do engine
engine = create_engine(DATABASE_URL)

# Criação das tabelas
SQLModel.metadata.create_all(bind=engine)

# Função para obter uma sessão de banco de dados
def get_db():
    with Session(engine) as session:
        yield session