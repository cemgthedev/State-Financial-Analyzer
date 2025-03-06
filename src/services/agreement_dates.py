from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, asc, select, func
from database import get_db
from models.agreement import Agreement
from models.agreement_dates import AgreementDates
from services.configs import agreement_dates_logger as logger
from datetime import date
from models.agreement_values import AgreementValues

# Criar roteador para AgreementDates
router = APIRouter(prefix="/agreement_dates", tags=["Agreement Dates"])

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
                "data_assinatura": item.data_assinatura,
                "data_termino": item.data_termino,
                "data_publi_ce": item.data_publi_ce,
                "data_publi_doe": item.data_publi_doe
            }
            for item in agreement_dates
        ]
    }
    logger.info(f'listando datas dos convênios da página {page} com {length} itens por página')
    return pagination

# Obter data de convênio
@router.get("/{agreement_date_id}", response_model=AgreementDates)
def get_agreement_date(agreement_date_id: int, db: Session = Depends(get_db)):
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

# Atualiza uma data de convênio
@router.put("/{agreement_date_id}")
def update_agreement_date(agreement_date_id: int, new_date: AgreementDates, db: Session = Depends(get_db)):
    try:
        agreement_date = db.get(AgreementDates, agreement_date_id)
        if agreement_date is None:
            logger.error(f"Data de convênio não encontrada: {agreement_date_id}")
            raise HTTPException(status_code=404, detail="Data de convênio não encontrada")

        # Atualizando os campos da data de convênio
        agreement_date.agreement_id = new_date.agreement_id
        agreement_date.data_assinatura = new_date.data_assinatura
        agreement_date.data_termino = new_date.data_termino
        agreement_date.data_publi_ce = new_date.data_publi_ce
        agreement_date.data_publi_doe = new_date.data_publi_doe

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
def get_agreement_dates_by_attributes(
    agreement_id: Optional[int] = None,
    data_assinatura: Optional[date] = None,
    data_termino: Optional[date] = None,
    data_publi_ce: Optional[date] = None,
    data_publi_doe: Optional[date] = None,
    db: Session = Depends(get_db)
):
    try:
        query = select(AgreementDates)
        if agreement_id is not None:
            query = query.where(AgreementDates.agreement_id == agreement_id)
        if data_assinatura is not None:
            query = query.where(AgreementDates.data_assinatura == data_assinatura)
        if data_termino is not None:
            query = query.where(AgreementDates.data_termino == data_termino)
        if data_publi_ce is not None:
            query = query.where(AgreementDates.data_publi_ce == data_publi_ce)
        if data_publi_doe is not None:
            query = query.where(AgreementDates.data_publi_doe == data_publi_doe)

        agreement_dates = db.exec(query).all()
    except Exception as e:
        logger.error(f"Erro ao buscar datas dos convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao buscar datas dos convênios")

    logger.info('buscando datas dos convênios com os atributos fornecidos')
    return agreement_dates

@router.get('/quantidade')
def get_agreement_dates_quantidade(db: Session = Depends(get_db)):
    try:
        quantity = db.exec(select(func.count(AgreementDates.id))).one()
    except Exception as e:
        logger.error(f"Erro ao buscar quantidade de datas dos convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao buscar quantidade de datas dos convênios: {str(e)}")

    logger.info('buscando quantidade de datas dos convênios')
    return {'quantidade de datas dos convênios': quantity}

@router.get('/values_per_year', description='Exibe a evolução do valor pago de convênios ao longo dos anos')
def get_values_per_year(db: Session = Depends(get_db)):
    try:
        data = db.exec(
            select(func.extract('year', AgreementDates.data_assinatura).label('ano') ,func.sum(AgreementValues.valor_pago).label('valor_pago_ano'))
            .join(AgreementDates, AgreementDates.id == AgreementValues.agreement_id)
            .group_by(func.extract('year', AgreementDates.data_assinatura))
            .order_by(asc(func.extract('year', AgreementDates.data_assinatura)))
        ).all()
        
        logger.info('Buscando a soma dos valores pagos por ano')
    except Exception as e:
        logger.erro(f'Erro ao retornar as soma de valores pagos por ano. Erro: {str(e)}')
        db.rollback()
        HTTPException(status_code=500, detail=f'Erro ao retornar as soma de valores pagos por ano. Erro: {str(e)}')
        
    return [
        {
            "ano": int(item.ano),
            "valor_pago_ano": float(item.valor_pago_ano)
        }
        for item in data
    ]