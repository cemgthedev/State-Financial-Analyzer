from math import ceil
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pandas import read_excel
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from unidecode import unidecode
from database import get_db
from models.contract import Contract
from models.contract_values import ContractValues
from services.configs import contracts_logger as logger
from services.configs import contract_values_logger as logger_values

# Criar roteador
router = APIRouter(prefix="/contracts", tags=["Contracts"])

# Cria os contratos
@router.post("/", description="Cria todos os contratos e valores de contratos")
def create_contracts(db: Session = Depends(get_db)):
    columns_contracts = ['numero_contrato', 'cpf/cnpj', 'contratante', 'contratado', 'tipo_objeto', 'objeto']
    columns_values = ['valor_original', 'valor_aditivo', 'valor_atualizado', 'valor_empenhado', 'valor_pago']
    try:
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(curr_dir, "../data")
        files = [
            "Contratos 2007 - 2010.xlsx",
            "Contratos 2011 - 2015.xlsx",
            "Contratos 2016 - 2020.xlsx",
            "Contratos 2021-Julho 2023.xlsx"
        ]
        
        logger.info('Criando contratos')
        for file in files:
            excel_file = os.path.join(data_dir, file)
            df = read_excel(excel_file)
            df.columns = [unidecode(col.lower().replace(' ', '_')) for col in df.columns]
            
            data_contract = [df[col] for col in columns_contracts if col in df.columns]
            data_values = [df[col] for col in columns_values if col in df.columns]
            for num, cpf_cnpj, cont, cond, tip, obj, vo, va, vat, ve, vp in zip(*data_contract, *data_values):
                # Cria os contratos
                contract = Contract(numero_contrato=num, cpf_cnpj=cpf_cnpj, contratante=cont, contratado=cond, tipo_objeto=tip, objeto=obj)
                db.add(contract)
                db.commit()
                db.refresh(contract)
                logger.info(f'Criando contrato {contract.id}')
                
                # Cria os valores dos contratos
                contract_value = ContractValues(contract_id=contract.id, valor_original=vo, valor_aditivo=va, valor_atualizado=vat, valor_empenhado=ve, valor_pago=vp)
                db.add(contract_value)
                db.commit()
                db.refresh(contract_value)
                logger_values.info(f'Criando valor de contrato {contract_value.id}')
        
        logger.info('Contratos criados com sucesso')
        return {"message": "Contratos criados com sucesso"}
        
    except Exception as e:
        logger.error(f"Erro ao criar contratos: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar contratos. Erro: {str(e)}")

# Atualiza um contrato
@router.put("/{contract_id}", description="Atualiza um contrato")
def update_contract(contract_id: int, new_contract: Contract, db: Session = Depends(get_db)):
    try:
        contract = db.get(Contract, contract_id)
        if contract is None:
            logger.error(f"Contrato não encontrado: {contract_id}")
            raise HTTPException(status_code=404, detail="Contrato não encontrado")
        
        contract.numero_contrato = new_contract.numero_contrato
        contract.cpf_cnpj = new_contract.cpf_cnpj
        contract.contratante = new_contract.contratante
        contract.contratado = new_contract.contratado
        contract.tipo_objeto = new_contract.tipo_objeto
        contract.objeto = new_contract.objeto
        
        logger.info(f'Atualizando contrato {contract_id}')
        db.commit()
        logger.info("Contrato atualizado com sucesso")
        return {"message": "Contrato atualizado com sucesso"}
    
    except Exception as e:
        logger.error(f"Erro ao atualizar contrato: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao obter contrato")
    
# Deleta um contrato
@router.delete("/{contract_id}", description="Deleta um contrato")
def delete_contract(contract_id: int, db: Session = Depends(get_db)):
    try:
        contract = db.get(Contract, contract_id)
        if contract is None:
            logger.error(f"Contrato não encontrado: {contract_id}")
            raise HTTPException(status_code=404, detail="Contrato não encontrado")
        
        logger.info(f'Deletando contrato {contract_id}')
        db.delete(contract)
        db.commit()
        logger.info("Contrato deletado com sucesso")
        return {"message": "Contrato deletado com sucesso"}
    
    except Exception as e:
        logger.error(f"Erro ao deletar contrato: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao excluir contrato")
    
# Busca um contrato pelo id
@router.get("/{contract_id}", response_model=Contract, description="Obtém um contrato")
def get_contract(contract_id: int, db: Session = Depends(get_db)):
    try:
        logger.info(f'Buscando contrato pelo id {contract_id}')
        contract = db.get(Contract, contract_id)
        if contract is None:
            logger.error(f"Contrato não encontrado: {contract_id}")
            raise HTTPException(status_code=404, detail="Contrato não encontrado")
    
        logger.info("Contrato encontrado com sucesso")
        return contract
    except Exception as e:
        logger.error(f"Erro ao obter contrato: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao obter contrato")
    
# Listagem dos contratos com paginação e filtros
@router.get("/", response_model=List[Contract], description="Lista os contratos")
def list_contracts(
    db: Session = Depends(get_db),
    page: Optional[int] = Query(default=1, ge=0, description="Página de contratos"),
    limit: Optional[int] = Query(default=100, ge=0, le=100, description="Quantidade de contratos a serem retornados"),
    cpf_cnpj: Optional[str] = Query(default=None, description="CPF/CNPJ do contratante"),
    contratante: Optional[str] = Query(default=None, description="Contratante"),
    contratado: Optional[str] = Query(default=None, description="Contratado"),
    tipo_objeto: Optional[str] = Query(default=None, description="Tipo de objeto"),
    objeto: Optional[str] = Query(default=None, description="Objeto"),
):
    try:
        logger.info('Listando contratos')
        filters = []
        
        if cpf_cnpj:
            filters.append(Contract.cpf_cnpj == cpf_cnpj)
        if contratante:
            filters.append(Contract.contratante == contratante)
        if contratado:
            filters.append(Contract.contratado == contratado)
        if tipo_objeto:
            filters.append(Contract.tipo_objeto == tipo_objeto)
        if objeto:
            filters.append(Contract.objeto.ilike(f"%{objeto}%"))
        
        offset = (page - 1) * limit
        stmt = select(Contract).where(and_(*filters)).offset(offset).limit(limit) if filters else select(Contract).offset(offset).limit(limit)
        contracts = db.exec(stmt).all()

        total_contracts = db.exec(select(func.count()).select_from(Contract).where(and_(*filters))).first() if filters else db.exec(select(func.count()).select_from(Contract)).first()
        total_pages = ceil(total_contracts / limit)
        
        if total_contracts > 0:
            logger.info(f"Contratos encontrados com sucesso!")
        else:
            logger.warning(f"Nenhum contrato encontrado!")

        return {
            "message": "Contratos encontrados com sucesso",
            "data": contracts,
            "page": page,
            "limit": limit,
            "total_contracts": total_contracts,
            "total_pages": total_pages
        }
        
    except Exception as e:
        logger.error(f"Erro ao listar contratos: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao listar contratos")