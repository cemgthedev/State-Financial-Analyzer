from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from sqlalchemy.sql import func
from database import get_db
from models.agreement_values import AgreementValues
from services.configs import agreement_values_logger as logger

# Criar roteador
router = APIRouter(prefix="/agreement_values", tags=["Agreement Values"])

# Listar valores de convênios
@router.get("/", response_model=list[AgreementValues], description="Lista os valores dos convênios")
def list_agreement_values(db: Session = Depends(get_db)):
    try:
        agreement_values = db.exec(select(AgreementValues)).all()
    except Exception as e:
        logger.error(f"Erro ao listar valores dos convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao listar valores dos convênios")
    
    logger.info('listando todos os valores dos convênios')
    result = [item.model_dump() for item in agreement_values]
    return result

# Listar valores de convênios paginado
@router.get("/pagination", description="Lista os valores dos convênios com paginação")
def list_agreement_values_paginated(page: Optional[int] = Query(1, gt=0), length: Optional[int] = Query(100, gt=0), db: Session = Depends(get_db)):
    try:
        agreement_values = db.exec(select(AgreementValues).offset((page - 1) * length).limit(length)).all()
    except Exception as e:
        logger.error(f"Erro ao listar valores dos convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao listar valores dos convênios")
    
    total = db.exec(select(func.count(AgreementValues.id))).one()
    total_pages = (total // length) + (1 if total % length > 0 else 0)
    pagination = {
        "page": page,
        "total_pages": total_pages,
        "length": length,
        "total": total,
        "data": [
            {
                "id": item.id,
                "agreement_id": item.agreement_id,
                "valor_inicial_total": item.valor_inicial_total,
                "valor_inicial_repasse_concedente": item.valor_inicial_repasse_concedente,
                "valor_inicial_contrapartida_convenente": item.valor_inicial_contrapartida_convenente,
                "valor_atualizado_total": item.valor_atualizado_total,
                "valor_pago": item.valor_pago
            }
            for item in agreement_values
        ]
    }
    logger.info(f'listando valores dos convênios da página {page} com {length} itens por página')
    return pagination

# Obter valor de convênio
@router.get("/{agreement_value_id}", response_model=AgreementValues, description="Obtém um valor de convênio")
def get_agreement_value(agreement_value_id: int, db: Session = Depends(get_db)):
    try:
        agreement_value = db.get(AgreementValues, agreement_value_id)
    except Exception as e:
        logger.error(f"Erro ao obter valor de convênio: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao obter valor de convênio")
    
    if agreement_value is None:
        logger.error(f"Valor de convênio não encontrado: {agreement_value_id}")
        raise HTTPException(status_code=404, detail="Valor de convênio não encontrado")
    
    logger.info(f'obtendo valor de convênio {agreement_value_id}')
    return agreement_value

# Atualiza um valor de convênio
@router.put("/{agreement_value_id}", description="Atualiza um valor de convênio")
def update_agreement_value(agreement_value_id: int, new_value: AgreementValues, db: Session = Depends(get_db)):
    try:
        agreement_value = db.get(AgreementValues, agreement_value_id)
        if agreement_value is None:
            logger.error(f"Valor de convênio não encontrado: {agreement_value_id}")
            raise HTTPException(status_code=404, detail="Valor de convênio não encontrado")
        
        # Atualizando os campos do valor de convênio
        agreement_value.valor_inicial_total = new_value.valor_inicial_total
        agreement_value.valor_inicial_repasse_concedente = new_value.valor_inicial_repasse_concedente
        agreement_value.valor_inicial_contrapartida_convenente = new_value.valor_inicial_contrapartida_convenente
        agreement_value.valor_atualizado_total = new_value.valor_atualizado_total
        agreement_value.valor_pago = new_value.valor_pago
        
        # Salvando as alterações no banco de dados
        db.commit()
        db.refresh(agreement_value)
    except Exception as e:
        logger.error(f"Erro ao atualizar valor de convênio: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao atualizar valor de convênio")
    
    logger.info(f'atualizando valor de convênio {agreement_value_id}')
    return agreement_value

# Deleta um valor de convênio
@router.delete("/{agreement_value_id}", description="Deleta um valor de convênio")
def delete_agreement_value(agreement_value_id: int, db: Session = Depends(get_db)):
    try:
        agreement_value = db.get(AgreementValues, agreement_value_id)
        if agreement_value is None:
            logger.error(f"Valor de convênio não encontrado: {agreement_value_id}")
            raise HTTPException(status_code=404, detail="Valor de convênio não encontrado")
        db.delete(agreement_value)
        db.commit()
    except Exception as e:
        logger.error(f"Erro ao deletar valor de convênio: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao deletar valor de convênio")
    
    logger.info(f'deletando valor de convênio {agreement_value_id}')
    return {"message": f"Valor de convênio {agreement_value_id} deletado com sucesso"}