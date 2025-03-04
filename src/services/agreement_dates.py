from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from database import get_db
from models.agreement_dates import AgreementDates
from services.configs import agreement_dates_logger as logger


# Criar roteador
router = APIRouter(prefix="/agreement_dates", tags=["Agreement Dates"])


# Listar datas de convênios
@router.get("/", response_model=list[AgreementDates], description="Lista as datas dos convênios")
def list_agreement_dates(db: Session = Depends(get_db)):
    try:
        agreement_dates = db.exec(select(AgreementDates)).all()
    except Exception as e:
        logger.error(f"Erro ao listar datas dos convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao listar datas dos convênios")

    logger.info('listando todas as datas dos convênios')
    return agreement_dates

# Listar datas de convênios
@router.get("/")
def list_agreement_dates(page: Optional[int] = Query(1, gt=0), length: Optional[int] = Query(100, gt=0), db: Session = Depends(get_db)):
    try:
        agreement_dates = db.exec(select(AgreementDates).offset((page - 1) * length).limit(length)).all()
    except Exception as e:
        logger.error(f"Erro ao listar datas dos convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao listar datas dos convênios")

    total = db.exec(select(func.count(AgreementDates.id))).one()
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
            }
            for item in agreement_dates
        ]
    }
    logger.info(f'listando datas dos convênios da página {page} com {length} itens por página')
    return pagination

# Obter data de convênio
@router.get("/{agreement_date_id}")
def get_agreement_date_by_id(agreement_date_id: int, db: Session = Depends(get_db)):
    try:
        agreement_date = db.get(AgreementDates, agreement_date_id)
    except Exception as e:
        logger.error(f"Erro ao obter data de convênio: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao obter data de convênio")

    if agreement_date is None:
        logger.error(f"Data de convênio não encontrada: {agreement_date_id}")
        raise HTTPException(status_code=404, detail="Data de convênio não encontrada")

    logger.info(f'obtendo data de convênio {agreement_date_id}')
    return agreement_date

# Atualiza data de convênio
@router.put("/{agreement_date_id}")
def update_agreement_date(agreement_date_id: int, new_date: AgreementDates, db: Session = Depends(get_db)):
    try:
        agreement_date = db.get(AgreementDates, agreement_date_id)
        if agreement_date is None:
            logger.error(f"Data de convênio não encontrada: {agreement_date_id}")
            raise HTTPException(status_code=404, detail="Data de convênio não encontrada")

        # Atualizando os campos da data de convênio
        agreement_date.agreement_id = new_date.agreement_id

        # Salvando as alterações no banco de dados
        db.commit()
        db.refresh(agreement_date)
    except Exception as e:
        logger.error(f"Erro ao atualizar data de convênio: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao atualizar data de convênio")

    logger.info(f'atualizando data de convênio {agreement_date_id}')
    return agreement_date

# Deleta uma data de convênio
@router.delete("/{agreement_date_id}")
def delete_agreement_date(agreement_date_id: int, db: Session = Depends(get_db)):
    try:
        agreement_date = db.get(AgreementDates, agreement_date_id)
        if agreement_date is None:
            logger.error(f"Data de convênio não encontrada: {agreement_date_id}")
            raise HTTPException(status_code=404, detail="Data de convênio não encontrada")
        db.delete(agreement_date)
        db.commit()
    except Exception as e:
        logger.error(f"Erro ao deletar data de convênio: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao deletar data de convênio")

    logger.info(f'deletando data de convênio {agreement_date_id}')
    return {"message": f"Data de convênio {agreement_date_id} deletada com sucesso"}

@router.get('/atributos')
def get_agreement_dates_by_attributes(agreement_id: Optional[int], db: Session = Depends(get_db)):
    try:
        query = select(AgreementDates)
        if agreement_id is not None:
            query = query.where(AgreementDates.agreement_id == agreement_id)

        agreement_dates = db.exec(query).all()
    except Exception as e:
        logger.error(f"Erro ao buscar datas dos convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao buscar datas dos convênios")

    logger.info('buscando datas dos convênios com os atributos fornecidos')
    return agreement_dates

@router.get('/quantidade')
def get_agreement_dates_quantity(db: Session = Depends(get_db)):
    try:
        quantity = db.exec(select(func.count(AgreementDates.id))).one()
    except Exception as e:
        logger.error(f"Erro ao buscar quantidade de datas dos convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao buscar quantidade de datas dos convênios")

    logger.info('buscando quantidade de datas dos convênios')
    return {'quantidade de datas dos convênios': quantity}