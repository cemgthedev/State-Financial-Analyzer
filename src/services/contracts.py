from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from database import get_db
from models.contract import Contract
from services.configs import contracts_logger as logger

# Criar roteador
router = APIRouter()