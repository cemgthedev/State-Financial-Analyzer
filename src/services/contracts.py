from math import ceil
import os
import pandas as pd
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pandas import read_excel
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from unidecode import unidecode
from database import get_db
from models.administrative_process import AdministrativeProcess
from models.contract import Contract
from models.contract_dates import ContractDates
from models.contract_values import ContractValues
from services.configs import contracts_logger as logger
from services.configs import contract_values_logger as logger_values
from services.configs import contract_dates_logger as logger_dates
from services.configs import administrative_processes_logger as logger_processes
from utils.convert_date import convert_date

# Criar roteador
router = APIRouter(prefix="/contracts", tags=["Contracts"])

# Cria os contratos
@router.post("/", description="Cria todos os contratos e valores de contratos")
def create_contracts(db: Session = Depends(get_db)):
    columns_contracts = ['numero_contrato', 'cpf/cnpj', 'contratante', 'contratado', 'tipo_objeto', 'objeto']
    columns_values = ['valor_original', 'valor_aditivo', 'valor_atualizado', 'valor_empenhado', 'valor_pago']
    columns_dates = ['data_de_assinatura', 'data_de_termino_original', 'data_de_termino_apos_aditivo', 'data_de_rescisao', 'data_publicacao_no_doe']
    columns_admnistrative_process = ['no_do_processo_-_spu', 'modalidade_de_licitacao', 'justificativa', 'status_str', 'situacao_fisica']
    
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
            df = df.where(pd.notna(df), None)
            
            data_contract = [df[col] for col in columns_contracts if col in df.columns]
            data_values = [df[col] for col in columns_values if col in df.columns]
            data_dates = [df[col] for col in columns_dates if col in df.columns]
            data_admnistrative_process = [df[col] for col in columns_admnistrative_process if col in df.columns]
            
            for num, cpf_cnpj, cont, cond, tip, obj, vo, va, vat, ve, vp, da, dto, dta, dr, dp, np, ml, j, si, sf in zip(*data_contract, *data_values, *data_dates, *data_admnistrative_process):
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
                
                # Converte datas
                da = convert_date(da) if da else None
                dto = convert_date(dto) if dto else None
                dta = convert_date(dta) if dta else None
                dr = convert_date(dr) if dr else None
                dp = convert_date(dp) if dp else None
                
                # Cria as datas dos contratos
                contract_date = ContractDates(contract_id=contract.id, data_de_assinatura=da, data_de_termino_original=dto, data_de_termino_apos_aditivo=dta, data_de_rescisao=dr, data_publicacao_no_doe=dp)
                db.add(contract_date)
                db.commit()
                db.refresh(contract_date)
                logger_dates.info(f'Criando data de contrato {contract_date.id}')
                
                # Cria os processos administrativos dos contratos
                contract_process = AdministrativeProcess(contract_id=contract.id, n_do_processo_spu=np, modalidade_de_licitacao=ml, justificativa=j, status_do_instrumento=si, situacao_fisica=sf)
                db.add(contract_process)
                db.commit()
                db.refresh(contract_process)
                logger_processes.info(f'Criando processo administrativo de contrato {contract_process.id}')
        
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