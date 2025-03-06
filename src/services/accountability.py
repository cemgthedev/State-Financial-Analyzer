from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from sqlalchemy import desc
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from database import get_db
from models.accountability import Accountability
from math import ceil
from services.configs import accountability_logger as logger
from models.agreement import Agreement

router = APIRouter(prefix="/accountability", tags=["Accountability"])

# Criar uma prestação de contas
@router.post("/", description="Cria uma nova prestação de contas")
def create_accountability(accountability: Accountability, db: Session = Depends(get_db)):
    try:
        db.add(accountability)
        db.commit()
        db.refresh(accountability)
        return {"message": "Prestação de contas criada com sucesso", "data": accountability}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar prestação de contas: {str(e)}")

# Atualizar uma prestação de contas
@router.put("/{accountability_id}", description="Atualiza uma prestação de contas")
def update_accountability(accountability_id: int, new_data: Accountability, db: Session = Depends(get_db)):
    try:
        accountability = db.get(Accountability, accountability_id)
        if accountability is None:
            raise HTTPException(status_code=404, detail="Prestação de contas não encontrada")
        
        for key, value in new_data.dict(exclude_unset=True).items():
            setattr(accountability, key, value)
        
        db.commit()
        db.refresh(accountability)
        return {"message": "Prestação de contas atualizada com sucesso", "data": accountability}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao atualizar prestação de contas: {str(e)}")

# Deletar uma prestação de contas
@router.delete("/{accountability_id}", description="Deleta uma prestação de contas")
def delete_accountability(accountability_id: int, db: Session = Depends(get_db)):
    try:
        accountability = db.get(Accountability, accountability_id)
        if accountability is None:
            raise HTTPException(status_code=404, detail="Prestação de contas não encontrada")
        
        db.delete(accountability)
        db.commit()
        return {"message": "Prestação de contas deletada com sucesso"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar prestação de contas: {str(e)}")

# Buscar uma prestação de contas pelo ID
@router.get("/{accountability_id}", response_model=Accountability, description="Obtém uma prestação de contas pelo ID")
def get_accountability(accountability_id: int, db: Session = Depends(get_db)):
    accountability = db.get(Accountability, accountability_id)
    if accountability is None:
        raise HTTPException(status_code=404, detail="Prestação de contas não encontrada")
    return accountability

# Listagem das prestações de contas com paginação e filtros
@router.get("/", description="Lista as prestações de contas")
def list_accountabilities(
    db: Session = Depends(get_db),
    page: Optional[int] = Query(default=1, ge=1, description="Página"),
    limit: Optional[int] = Query(default=100, ge=1, le=100, description="Quantidade por página"),
    agreement_id: Optional[int] = Query(default=None, description="ID do convênio"),
    status: Optional[str] = Query(default=None, description="Status da prestação de contas"),
    report_type: Optional[str] = Query(default=None, description="Tipo de relatório")
):
    try:
        filters = []
        if agreement_id:
            filters.append(Accountability.agreement_id == agreement_id)
        if status:
            filters.append(Accountability.status == status)
        if report_type:
            filters.append(Accountability.report_type == report_type)
        
        offset = (page - 1) * limit
        stmt = select(Accountability).where(and_(*filters)).offset(offset).limit(limit)
        accountabilities = db.exec(stmt).all()
        
        total = db.exec(select(func.count()).select_from(Accountability).where(and_(*filters))).first()
        total_pages = ceil(total / limit)
        
        return {
            "message": "Prestações de contas listadas com sucesso",
            "data": accountabilities,
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": total_pages
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao listar prestações de contas: {str(e)}")


@router.get('/per_status', description='Retorna os convênios pela sua situação em prestação de contas')
def get_per_status(db: Session = Depends(get_db)):
    try:
        data = db.exec(
            select(Agreement, Accountability.status.label('categoria'), func.count(Agreement.id).label('qntd_categoria'))
            .join(Accountability)
            .group_by(Accountability.status)
            .order_by(desc(func.count(Agreement.id)))
        ).all()
        
        logger.info('Listando os convênios pelo status da prestação de contas')
    except Exception as e:
        logger.error(f'Erro ao retornar os convênios. Erro: {str(e)}')
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao retornar os convênios. Erro: {str(e)}')
    
    result = []
    for agreement, status, count in data:
        result.append({
            "status": status,
            "qntd_status": count
            "convenio": agreement.dict(),
        })
    return result