from math import ceil
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from database import get_db
from models.contract_values import ContractValues
from services.configs import contract_values_logger as logger

# Criar roteador
router = APIRouter(prefix="/contract_values", tags=["Contract Values"])

# Atualizar valor de contrato
@router.put("/{contract_value_id}", description="Atualiza o valor de um contrato")
def update_contract_value(contract_value_id: int, new_value: ContractValues, db: Session = Depends(get_db)):
    try:
        contract_value = db.get(ContractValues, contract_value_id)
        if contract_value is None:
            logger.error(f"Valores de contrato não encontrados: {contract_value_id}")
            raise HTTPException(status_code=404, detail="Valores de contrato não encontrados")
        
        # Atualizando os campos do valor de contrato
        contract_value.valor_original = new_value.valor_original
        contract_value.valor_aditivo = new_value.valor_aditivo
        contract_value.valor_atualizado = new_value.valor_atualizado
        contract_value.valor_empenhado = new_value.valor_empenhado
        contract_value.valor_pago = new_value.valor_pago
        
        logger.info(f'Atualizando valores de contrato {contract_value_id}')
        db.commit()
        logger.info("Valores de contrato atualizados com sucesso")
        return {"message": "Valores de contrato atualizados com sucesso"}
       
    except Exception as e:
        logger.error(f"Erro ao atualizar valores de contrato: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao atualizar valores de contrato")
    
# Deleta um valor de contrato
@router.delete("/{contract_value_id}", description="Deleta um valor de contrato")
def delete_contract_value(contract_value_id: int, db: Session = Depends(get_db)):
    try:
        contract_value = db.get(ContractValues, contract_value_id)
        if contract_value is None:
            logger.error(f"Valores de contrato não encontrados: {contract_value_id}")
            raise HTTPException(status_code=404, detail="Valores de contrato não encontrados")
        
        logger.info(f'Deletando valores de contrato {contract_value_id}')
        db.delete(contract_value)
        db.commit()
        logger.info("Valores de contrato deletados com sucesso")
        return {"message": "Valores de contrato deletados com sucesso"}
       
    except Exception as e:
        logger.error(f"Erro ao deletar valores de contrato: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao deletar valores de contrato")
    
# Busca um valor de contrato pelo id
@router.get("/{contract_value_id}", response_model=ContractValues, description="Busca um valor de contrato pelo id")
def get_contract_value(contract_value_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f'Buscando valores de contrato pelo id {contract_value_id}')
        contract_value = db.get(ContractValues, contract_value_id)
        if contract_value is None:
            logger.error(f"Valores de contrato não encontrados: {contract_value_id}")
            raise HTTPException(status_code=404, detail="Valores de contrato não encontrados")
        
        logger.info("Valores de contrato encontrados com sucesso")
        return contract_value
    except Exception as e:
        logger.error(f"Erro ao obter valores de contrato: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao obter valores de contrato")
    
# Listagem dos valores de contratos com paginação e filtros
@router.get("/", description="Lista os valores de contratos")
def list_contract_values(
    db: Session = Depends(get_db),
    page: Optional[int] = Query(default=1, ge=0, description="Página de valores de contratos"),
    limit: Optional[int] = Query(default=100, ge=0, le=100, description="Quantidade de valores de contratos a serem retornados"),
    min_valor_original: Optional[float] = Query(default=None, ge=0, description="Valor original mínimo"),
    max_valor_original: Optional[float] = Query(default=None, ge=0, description="Valor original máximo"),
    min_valor_aditivo: Optional[float] = Query(default=None, ge=0, description="Valor aditivo mínimo"),
    max_valor_aditivo: Optional[float] = Query(default=None, ge=0, description="Valor aditivo máximo"),
    min_valor_atualizado: Optional[float] = Query(default=None, ge=0, description="Valor atualizado mínimo"),
    max_valor_atualizado: Optional[float] = Query(default=None, ge=0, description="Valor atualizado máximo"),
    min_valor_empenhado: Optional[float] = Query(default=None, ge=0, description="Valor empenhado mínimo"),
    max_valor_empenhado: Optional[float] = Query(default=None, ge=0, description="Valor empenhado máximo"),
    min_valor_pago: Optional[float] = Query(default=None, ge=0, description="Valor pago mínimo"),
    max_valor_pago: Optional[float] = Query(default=None, ge=0, description="Valor pago máximo"),
):
    try:
        logger.info('Listando valores de contratos')
        filters = []
        
        if min_valor_original is not None:
            filters.append(ContractValues.valor_original >= min_valor_original)
        if max_valor_original is not None:
            filters.append(ContractValues.valor_original <= max_valor_original)
        if min_valor_aditivo is not None:
            filters.append(ContractValues.valor_aditivo >= min_valor_aditivo)
        if max_valor_aditivo is not None:
            filters.append(ContractValues.valor_aditivo <= max_valor_aditivo)
        if min_valor_atualizado is not None:
            filters.append(ContractValues.valor_atualizado >= min_valor_atualizado)
        if max_valor_atualizado is not None:
            filters.append(ContractValues.valor_atualizado <= max_valor_atualizado)
        if min_valor_empenhado is not None:
            filters.append(ContractValues.valor_empenhado >= min_valor_empenhado)
        if max_valor_empenhado is not None:
            filters.append(ContractValues.valor_empenhado <= max_valor_empenhado)
        if min_valor_pago is not None:
            filters.append(ContractValues.valor_pago >= min_valor_pago)
        if max_valor_pago is not None:
            filters.append(ContractValues.valor_pago <= max_valor_pago)
        
        offset = (page - 1) * limit
        stmt = select(ContractValues).where(and_(*filters)).offset(offset).limit(limit) if filters else select(ContractValues).offset(offset).limit(limit)
        contract_values = db.exec(stmt).all()

        total_contract_values = db.exec(select(func.count()).select_from(ContractValues).where(and_(*filters))).first() if filters else db.exec(select(func.count()).select_from(ContractValues)).first()
        total_pages = ceil(total_contract_values / limit)
        
        if total_contract_values > 0:
            logger.info(f"Valores de contratos encontrados com sucesso!")
        else:
            logger.warning(f"Nenhum valor de contrato encontrado!")

        return {
            "message": "Valores de contratos encontrados com sucesso",
            "data": contract_values,
            "page": page,
            "limit": limit,
            "total_contract_values": total_contract_values,
            "total_pages": total_pages
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar valores de contratos: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao listar valores de contratos")