from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from database import get_db
from models.agreement import Agreement
from models.agreement_values import AgreementValues
from services.configs import agreements_logger as logger
from services.configs import agreement_values_logger as logger_values
from pandas import read_excel
from unidecode import unidecode
import os

# Criar roteador
router = APIRouter(prefix="/agreements", tags=["Agreements"])

# Listar convênios
@router.get("/", response_model=list[Agreement], description="Lista os convênios")
def list_agreements(db: Session = Depends(get_db)):
    try:
        agreements = db.exec(select(Agreement)).all()
    except Exception as e:
        logger.error(f"Erro ao listar convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao listar convênios")
    
    logger.info('listando todos os convênios')
    result = [item.model_dump() for item in agreements]
    return result

# Listar convênios paginado
@router.get("/pagination", description="Lista os convênios com paginação")
def list_agreements_paginated(page: Optional[int] = Query(1, gt=0), length: Optional[int] = Query(100, gt=0), db: Session = Depends(get_db)):
    try:
        agreements = db.exec(select(Agreement).offset((page - 1) * length).limit(length)).all()
    except Exception as e:
        logger.error(f"Erro ao listar convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao listar convênios")
    
    total = db.exec(select(func.count(Agreement.id))).one()
    total_pages = (total // length) + (1 if total % length > 0 else 0)
    pagination = {
        "page": page,
        "total_pages": total_pages,
        "length": length,
        "total": total,
        "data": [
            {
                "id": item.id,
                "codigo_plano_trabalho": item.codigo_plano_trabalho,
                "concedente": item.concedente,
                "convenente": item.convenente,
                "objeto": item.objeto
            }
            for item in agreements
        ]
    }
    logger.info(f'listando convênios da página {page} com {length} itens por página')
    return pagination

# Obter convênio
@router.get("/{agreement_id}", response_model=Agreement, description="Obtém um convênio")
def get_agreement(agreement_id: int, db: Session = Depends(get_db)):
    try:
        agreement = db.get(Agreement, agreement_id)
    except Exception as e:
        logger.error(f"Erro ao obter convênio: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao obter convênio")
    
    if agreement is None:
        logger.error(f"Convênio não encontrado: {agreement_id}")
        raise HTTPException(status_code=404, detail="Convênio não encontrado")
    
    logger.info(f'obtendo convênio {agreement_id}')
    return agreement

# Cria os convênios
@router.post("/", description="Cria todos os convênios e valores de convênios")
def create_agreements(db: Session = Depends(get_db)):
    columns_agreements = ['codigo_plano_de_trabalho', 'concedente', 'convenente', 'objeto']
    columns_values = ['valor_inicial_total', 'valor_inicial_do_repasse_do_concedente', 'valor_inicial_da_contrapartida_do_convenente/beneficiario', 'valor_atualizado_total', 'valor_pago']
    try:
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        excel_file = os.path.join(curr_dir, "../data/Convênios 2007 - Setembro 2023.xlsx")
        df = read_excel(excel_file)
        df.columns = [unidecode(col.lower().replace(' ', '_')) for col in df.columns]
        
        data_agreement = [df[col] for col in columns_agreements if col in df.columns]
        data_values = [df[col] for col in columns_values if col in df.columns]
        for cod, con, conv, obj, vit, virc, vicc, vat, vp in zip(*data_agreement, *data_values):
            # Cria os convênios
            agreement = Agreement(codigo_plano_trabalho=cod, concedente=con, convenente=conv, objeto=obj)
            db.add(agreement)
            db.commit()
            db.refresh(agreement)
            logger.info(f'criando convênio {agreement.id}')
            # Cria os valores dos convênios
            agreement_value = AgreementValues(agreement_id=agreement.id, valor_inicial_total=vit, valor_inicial_repasse_concedente=virc, valor_inicial_contrapartida_convenente=vicc, valor_atualizado_total=vat, valor_pago=vp)
            db.add(agreement_value)
            db.commit()
            db.refresh(agreement_value)
            logger_values.info(f'criando valor de convênio {agreement_value.id}')
    except Exception as e:
        logger.error(f"Erro ao criar convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar convênios. Erro: {str(e)}")
    
    return {"message": "Convênios e seus valores criados com sucesso"}
    
@router.put("/{agreement_id}", description="Atualiza um convênio")
def update_agreement(agreement_id: int, new_agree: Agreement, db: Session = Depends(get_db)):
    try:
        agreement = db.get(Agreement, agreement_id)
        if agreement is None:
            logger.error(f"Convênio não encontrado: {agreement_id}")
            raise HTTPException(status_code=404, detail="Convênio não encontrado")
        agreement.codigo_plano_trabalho = new_agree.codigo_plano_trabalho
        agreement.concedente = new_agree.concedente
        agreement.convenente = new_agree.convenente
        agreement.objeto = new_agree.objeto
        db.commit()
        db.refresh(agreement)
    except Exception as e:
        logger.error(f"Erro ao atualizar convênio: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao obter convênio")
    
    logger.info(f'atualizando convênio {agreement_id}')
    return agreement

@router.delete("/{agreement_id}", description="Deleta um convênio")
def delete_agreement(agreement_id: int, db: Session = Depends(get_db)):
    try:
        agreement = db.get(Agreement, agreement_id)
        if agreement is None:
            logger.error(f"Convênio não encontrado: {agreement_id}")
            raise HTTPException(status_code=404, detail="Convênio não encontrado")
        db.delete(agreement)
        db.commit()
    except Exception as e:
        logger.error(f"Erro ao deletar convênio: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao excluir convênio")
    
    logger.info(f'deletando convênio {agreement_id}')
    return {"message": f"Convênio {agreement_id} deletado com sucesso"}