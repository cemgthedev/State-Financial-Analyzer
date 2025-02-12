from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from database import get_db
from models.agreement_values import AgreementValues
from services.configs import agreement_values_logger as logger

# Criar roteador
router = APIRouter()