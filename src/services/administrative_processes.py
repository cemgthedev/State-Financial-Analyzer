from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from database import get_db
from models.administrative_process import AdministrativeProcess
from services.configs import administrative_processes_logger as logger

# Criar roteador
router = APIRouter()