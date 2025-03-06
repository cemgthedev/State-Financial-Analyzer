from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, select
from sqlalchemy.sql import func
from database import get_db
from models.agreement_dates import AgreementDates
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

@router.get('/atributos', description="Lista os atributos do modelo de valores de convênios")
def get_agreement_values_attributes(
    agreement_id: Optional[int],
    valor_inicial_total: Optional[float],
    valor_inicial_repasse_concedente: Optional[float],
    valor_inicial_contrapartida_convenente: Optional[float],
    valor_atualizado_total: Optional[float],
    valor_pago: Optional[float], db: Session = Depends(get_db)):
    try:
        query = select(AgreementValues)
        if agreement_id is not None:
            query = query.where(AgreementValues.agreement_id == agreement_id)
        if valor_inicial_total is not None:
            query = query.where(AgreementValues.valor_inicial_total == valor_inicial_total)
        if valor_inicial_repasse_concedente is not None:
            query = query.where(AgreementValues.valor_inicial_repasse_concedente == valor_inicial_repasse_concedente)
        if valor_inicial_contrapartida_convenente is not None:
            query = query.where(AgreementValues.valor_inicial_contrapartida_convenente == valor_inicial_contrapartida_convenente)
        if valor_atualizado_total is not None:
            query = query.where(AgreementValues.valor_atualizado_total == valor_atualizado_total)
        if valor_pago is not None:
            query = query.where(AgreementValues.valor_pago == valor_pago)
        
        agreement_values = db.exec(query).all()
    except Exception as e:
        logger.error(f"Erro ao buscar valores dos convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao buscar valores dos convênios")
    
    logger.info('buscando valores dos convênios com os atributos fornecidos')
    result = [item.model_dump() for item in agreement_values]
    return result

@router.get('/quantity', description="Quantidade de valores de convênios")
def get_agreement_values_quantity(db: Session = Depends(get_db)):
    try:
        quantity = db.exec(select(func.count(AgreementValues.id))).one()        
    except Exception as e:
        logger.error(f"Erro ao buscar quantidade de valores dos convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao buscar quantidade de valores dos convênios")
    
    logger.info('buscando quantidade de valores dos convênios')
    return {'quantidade de valores dos convênios': quantity}

@router.get('/search/valor_inicial_total', description='Faz uma pesquisa por valor inicial total de convênios')
def get_search_valor_inicial_total(min_value: Optional[float] = None, max_value: Optional[float] = None, db: Session = Depends(get_db)):
    try:
        query = select(AgreementValues)
        if min_value is not None:
            query = query.where(AgreementValues.valor_inicial_total >= min_value)
        if max_value is not None:
            query = query.where(AgreementValues.valor_inicial_total <= max_value)
        
        data = db.exec(query).all()
    except Exception as e:
        logger.error(f'Erro ao listar os valores de convênios pelo valor inicial total. Erro: {str(e)}')
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao listar os valores de convênios pelo valor inicial total. Erro: {str(e)}')
    
    return [
        {
            'id': item.id,
            'agreement_id': item.agreement_id,
            'valor_inicial_total': item.valor_inicial_total,
            'valor_inicial_repasse_concedente': item.valor_inicial_repasse_concedente,
            'valor_inicial_contrapartida_convenente': item.valor_inicial_contrapartida_convenente,
            'valor_atualizado_total': item.valor_atualizado_total,
            'valor_pago': item.valor_pago
        } for item in data
    ]

@router.get('/search/valor_inicial_repasse_concedente', description='Faz uma pesquisa por valor inicial repasse concedente de convênios')
def get_search_valor_inicial_repasse_concedente(min_value: Optional[float] = None, max_value: Optional[float] = None, db: Session = Depends(get_db)):
    try:
        query = select(AgreementValues)
        if min_value is not None:
            query = query.where(AgreementValues.valor_inicial_repasse_concedente >= min_value)
        if max_value is not None:
            query = query.where(AgreementValues.valor_inicial_repasse_concedente <= max_value)
        
        data = db.exec(query).all()
    except Exception as e:
        logger.error(f'Erro ao listar os valores de convênios pelo valor inicial repasse concedente. Erro: {str(e)}')
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao listar os valores de convênios pelo valor inicial repasse concedente. Erro: {str(e)}')
    
    return [
        {
            'id': item.id,
            'agreement_id': item.agreement_id,
            'valor_inicial_total': item.valor_inicial_total,
            'valor_inicial_repasse_concedente': item.valor_inicial_repasse_concedente,
            'valor_inicial_contrapartida_convenente': item.valor_inicial_contrapartida_convenente,
            'valor_atualizado_total': item.valor_atualizado_total,
            'valor_pago': item.valor_pago
        } for item in data
    ]

@router.get('/search/valor_inicial_contrapartida_convenente', description='Faz uma pesquisa por valor inicial contrapartida convenente de convênios')
def get_search_valor_inicial_contrapartida_convenente(min_value: Optional[float] = None, max_value: Optional[float] = None, db: Session = Depends(get_db)):
    try:
        query = select(AgreementValues)
        if min_value is not None:
            query = query.where(AgreementValues.valor_inicial_contrapartida_convenente >= min_value)
        if max_value is not None:
            query = query.where(AgreementValues.valor_inicial_contrapartida_convenente <= max_value)
        
        data = db.exec(query).all()
    except Exception as e:
        logger.error(f'Erro ao listar os valores de convênios pelo valor inicial contrapartida convenente. Erro: {str(e)}')
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao listar os valores de convênios pelo valor inicial contrapartida convenente. Erro: {str(e)}')
    
    return [
        {
            'id': item.id,
            'agreement_id': item.agreement_id,
            'valor_inicial_total': item.valor_inicial_total,
            'valor_inicial_repasse_concedente': item.valor_inicial_repasse_concedente,
            'valor_inicial_contrapartida_convenente': item.valor_inicial_contrapartida_convenente,
            'valor_atualizado_total': item.valor_atualizado_total,
            'valor_pago': item.valor_pago
        } for item in data
    ]

@router.get('/search/valor_atualizado_total', description='Faz uma pesquisa por valor atualizado total de convênios')
def get_search_valor_atualizado_total(min_value: Optional[float] = None, max_value: Optional[float] = None, db: Session = Depends(get_db)):
    try:
        query = select(AgreementValues)
        if min_value is not None:
            query = query.where(AgreementValues.valor_atualizado_total >= min_value)
        if max_value is not None:
            query = query.where(AgreementValues.valor_atualizado_total <= max_value)
        
        data = db.exec(query).all()
    except Exception as e:
        logger.error(f'Erro ao listar os valores de convênios pelo valor atualizado total. Erro: {str(e)}')
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao listar os valores de convênios pelo valor atualizado total. Erro: {str(e)}')
    
    return [
        {
            'id': item.id,
            'agreement_id': item.agreement_id,
            'valor_inicial_total': item.valor_inicial_total,
            'valor_inicial_repasse_concedente': item.valor_inicial_repasse_concedente,
            'valor_inicial_contrapartida_convenente': item.valor_inicial_contrapartida_convenente,
            'valor_atualizado_total': item.valor_atualizado_total,
            'valor_pago': item.valor_pago
        } for item in data
    ]

@router.get('/search/valor_pago', description='Faz uma pesquisa por valor pago de convênios')
def get_search_valor_pago(min_value: Optional[float] = None, max_value: Optional[float] = None, db: Session = Depends(get_db)):
    try:
        query = select(AgreementValues)
        if min_value is not None:
            query = query.where(AgreementValues.valor_pago >= min_value)
        if max_value is not None:
            query = query.where(AgreementValues.valor_pago <= max_value)
        
        data = db.exec(query).all()
    except Exception as e:
        logger.error(f'Erro ao listar os valores de convênios pelo valor pago. Erro: {str(e)}')
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao listar os valores de convênios pelo valor pago. Erro: {str(e)}')
    
    return [
        {
            'id': item.id,
            'agreement_id': item.agreement_id,
            'valor_inicial_total': item.valor_inicial_total,
            'valor_inicial_repasse_concedente': item.valor_inicial_repasse_concedente,
            'valor_inicial_contrapartida_convenente': item.valor_inicial_contrapartida_convenente,
            'valor_atualizado_total': item.valor_atualizado_total,
            'valor_pago': item.valor_pago
        } for item in data
    ]

@router.get('/compare_values', description='Compara os valores iniciais com os valores atualizados de convênios por ano')
def get_compare_values(db: Session = Depends(get_db)):
    try:
        data = db.exec(
            select(func.extract('year', AgreementDates.data_assinatura).label('ano'),
                   func.sum(AgreementValues.valor_inicial_total).label('soma_valores_originais'),
                   func.sum(AgreementValues.valor_atualizado_total).label('soma_valores_atualizados'))
            .join(AgreementDates, AgreementValues.agreement_id == AgreementDates.agreement_id)
            .group_by(func.extract('year', AgreementDates.data_assinatura))
            .order_by(func.extract('year', AgreementDates.data_assinatura))
        ).all()
    except Exception as e:
        logger.error(f'Erro ao comparar os valores dos convênios. Erro: {str(e)}')
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao comparar os valores dos convênios. Erro: {str(e)}')
    
    return [
        {
            'ano': item.ano,
            'soma_valores_originais': item.soma_valores_originais,
            'soma_valores_atualizados': item.soma_valores_atualizados
        } for item in data
    ]