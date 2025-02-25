from fastapi import FastAPI, Depends
from sqlmodel import Session
from database import get_db
from models import *
from services.contracts import router as contracts_router
from services.contract_values import router as contract_values_router
from services.contract_dates import router as contract_dates_router
from services.administrative_processes import router as administrative_processes_router
from services.agreements import router as agreements_router
from services.agreement_values import router as agreement_values_router
from services.agreement_dates import router as agreement_dates_router
from services.accountability import router as accountability_router
from utils.generate_logs import generate_logs
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    generate_logs()
    yield

app = FastAPI(
    title="State Financial Analyzer",
    description="API de análise financeira de contratos e convênios do Ceará",
    lifespan=lifespan
)


@app.get("/")
def get_db(db: Session = Depends(get_db)):
    if db is None:
        return {"message": "Database not connected"}
    return {"message": "Database connected"}

# Adicionando rotas de contratos
app.include_router(contracts_router)

# Adicionando rotas de valores de contrato
app.include_router(contract_values_router)

# Adicionando rotas de datas de contrato
app.include_router(contract_dates_router)

# Adicionando rotas de processos administrativos
app.include_router(administrative_processes_router)

# Adicionando rotas de convênios
app.include_router(agreements_router)

# Adicionando rotas de valores de convênio
app.include_router(agreement_values_router)

# Adicionando rotas de datas de convênio
app.include_router(agreement_dates_router)

# Adicionando rotas de prestação de contas
app.include_router(accountability_router)