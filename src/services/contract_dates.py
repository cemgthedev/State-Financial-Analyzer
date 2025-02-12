from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from database import get_db
from models.contract_dates import ContractDates
from services.configs import contract_dates_logger as logger

# Criar roteador
router = APIRouter()