from math import ceil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from database import get_db
from models.administrative_process import AdministrativeProcess
from services.configs import processes_logger as logger

# Criar roteador
router = APIRouter(prefix="/administrative_processes", tags=["Administrative Processes"])

# Criar um processo administrativo
@router.post("/", description="Cria um processo administrativo")
def create_process(new_process: AdministrativeProcess, db: Session = Depends(get_db)):
    try:
        db.add(new_process)
        db.commit()
        db.refresh(new_process)
        logger.info(f'Processo Administrativo criado: {new_process.id}')
        return {"message": "Processo Administrativo criado com sucesso", "data": new_process}
    except Exception as e:
        logger.error(f"Erro ao criar processo administrativo: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao criar processo administrativo")

# Atualizar um processo administrativo
@router.put("/{process_id}", description="Atualiza um processo administrativo")
def update_process(process_id: int, updated_process: AdministrativeProcess, db: Session = Depends(get_db)):
    try:
        process = db.get(AdministrativeProcess, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Processo administrativo não encontrado")
        
        for key, value in updated_process.dict(exclude_unset=True).items():
            setattr(process, key, value)
        
        db.commit()
        logger.info(f'Processo Administrativo atualizado: {process_id}')
        return {"message": "Processo Administrativo atualizado com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao atualizar processo administrativo: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao atualizar processo administrativo")

# Deletar um processo administrativo
@router.delete("/{process_id}", description="Deleta um processo administrativo")
def delete_process(process_id: int, db: Session = Depends(get_db)):
    try:
        process = db.get(AdministrativeProcess, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Processo administrativo não encontrado")
        
        db.delete(process)
        db.commit()
        logger.info(f'Processo Administrativo deletado: {process_id}')
        return {"message": "Processo Administrativo deletado com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao deletar processo administrativo: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao deletar processo administrativo")

# Buscar um processo administrativo pelo ID
@router.get("/{process_id}", response_model=AdministrativeProcess, description="Obtém um processo administrativo")
def get_process(process_id: int, db: Session = Depends(get_db)):
    try:
        process = db.get(AdministrativeProcess, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Processo administrativo não encontrado")
        return process
    except Exception as e:
        logger.error(f"Erro ao obter processo administrativo: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter processo administrativo")

# Listar processos administrativos com paginação e filtros
@router.get("/", response_model=List[AdministrativeProcess], description="Lista os processos administrativos")
def list_processes(
    db: Session = Depends(get_db),
    page: Optional[int] = Query(default=1, ge=1, description="Página de processos"),
    limit: Optional[int] = Query(default=100, ge=1, le=100, description="Quantidade de processos a serem retornados"),
    contract_id: Optional[int] = Query(default=None, description="ID do contrato relacionado")
):
    try:
        filters = []
        if contract_id:
            filters.append(AdministrativeProcess.contract_id == contract_id)
        
        offset = (page - 1) * limit
        stmt = select(AdministrativeProcess).where(and_(*filters)).offset(offset).limit(limit) if filters else select(AdministrativeProcess).offset(offset).limit(limit)
        processes = db.exec(stmt).all()

        total_processes = db.exec(select(func.count()).select_from(AdministrativeProcess).where(and_(*filters))).first() if filters else db.exec(select(func.count()).select_from(AdministrativeProcess)).first()
        total_pages = ceil(total_processes / limit)
        
        return {
            "message": "Processos Administrativos listados com sucesso",
            "data": processes,
            "page": page,
            "limit": limit,
            "total_processes": total_processes,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Erro ao listar processos administrativos: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao listar processos administrativos")
