from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from database import get_db
from models.contract_dates import ContractDates
from services.configs import contract_dates_logger as logger


# Criar roteador
router = APIRouter(prefix="/contract_dates", tags=["Contract Dates"])


# Listar datas de contrato paginado
@router.get("/")
def list_contract_dates(page: Optional[int] = Query(1, gt=0), length: Optional[int] = Query(100, gt=0), db: Session = Depends(get_db)):
    try:
        contract_dates = db.exec(select(ContractDates).offset((page - 1) * length).limit(length)).all()
    except Exception as e:
        logger.error(f"Erro ao listar datas dos contratos: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao listar datas dos contratos")

    total = db.exec(select(func.count(ContractDates.id))).one()
    total_pages = (total // length) + (1 if total % length > 0 else 0)
    pagination = {
        "page": page,
        "total_pages": total_pages,
        "length": length,
        "total": total,
        "data": [item.model_dump() for item in contract_dates]
    }
    logger.info(f'listando datas dos contratos da página {page} com {length} itens por página')
    return pagination

# Obter data de contrato por id
@router.get("/{contract_date_id}")
def get_contract_date_by_id(contract_date_id: int, db: Session = Depends(get_db)):
    try:
        contract_date = db.get(ContractDates, contract_date_id)
    except Exception as e:
        logger.error(f"Erro ao obter data de contrato: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao obter data de contrato")

    if contract_date is None:
        logger.error(f"Data de contrato não encontrada: {contract_date_id}")
        raise HTTPException(status_code=404, detail="Data de contrato não encontrada")

    logger.info(f'obtendo data de contrato {contract_date_id}')
    return contract_date.model_dump()

# Atualiza data de contrato
@router.put("/{contract_date_id}")
def update_contract_date(contract_date_id: int, new_date: ContractDates, db: Session = Depends(get_db)):
    try:
        contract_date = db.get(ContractDates, contract_date_id)
        if contract_date is None:
            logger.error(f"Data de contrato não encontrada: {contract_date_id}")
            raise HTTPException(status_code=404, detail="Data de contrato não encontrada")

        # Atualizando os campos da data de contrato
        contract_date.contract_id = new_date.contract_id

        # Salvando as alterações no banco de dados
        db.commit()
        db.refresh(contract_date)
    except Exception as e:
        logger.error(f"Erro ao atualizar data de contrato: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao atualizar data de contrato")

    logger.info(f'atualizando data de contrato {contract_date_id}')
    return contract_date.model_dump()

# Deleta data de contrato
@router.delete("/{contract_date_id}")
def delete_contract_date(contract_date_id: int, db: Session = Depends(get_db)):
    try:
        contract_date = db.get(ContractDates, contract_date_id)
        if contract_date is None:
            logger.error(f"Data de contrato não encontrada: {contract_date_id}")
            raise HTTPException(status_code=404, detail="Data de contrato não encontrada")
        db.delete(contract_date)
        db.commit()
    except Exception as e:
        logger.error(f"Erro ao deletar data de contrato: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao deletar data de contrato")

    logger.info(f'deletando data de contrato {contract_date_id}')
    return {"message": f"Data de contrato {contract_date_id} deletada com sucesso"}

@router.get('/atributos')
def get_contract_dates_by_attributes(contract_id: Optional[int] = None, db: Session = Depends(get_db)):
    try:
        query = select(ContractDates)
        if contract_id is not None:
            query = query.where(ContractDates.contract_id == contract_id)

        contract_dates = db.exec(query).all()
    except Exception as e:
        logger.error(f"Erro ao buscar datas dos contratos: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao buscar datas dos contratos")

    logger.info('buscando datas dos contratos com os atributos fornecidos')
    result = [item.model_dump() for item in contract_dates]
    return result

@router.get('/quantidade')
def get_contract_dates_quantity(db: Session = Depends(get_db)):
    try:
        quantity = db.exec(select(func.count(ContractDates.id))).one()
    except Exception as e:
        logger.error(f"Erro ao buscar quantidade de datas dos contratos: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao buscar quantidade de datas dos contratos")

    logger.info('buscando quantidade de datas dos contratos')
    return {'quantidade de datas dos contratos': quantity}