from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from database import get_db
from models.accountability import Accountability
from services.configs import accountability_logger as logger

# Criar roteador
router = APIRouter()