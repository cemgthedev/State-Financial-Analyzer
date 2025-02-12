from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from database import get_db
from models.agreement_dates import AgreementDates
from services.configs import agreement_dates_logger as logger

# Criar roteador
router = APIRouter()