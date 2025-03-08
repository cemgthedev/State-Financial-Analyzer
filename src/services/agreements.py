from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import text
from sqlmodel import Session, select, delete
from sqlalchemy.sql import func
from database import get_db
from models.agreement import Agreement
from models.agreement_dates import AgreementDates
from models.agreement_values import AgreementValues
from services.configs import agreements_logger as logger
from services.configs import agreement_values_logger as logger_values
from services.configs import agreement_dates_logger as logger_dates # adicionando logger de datas
import pandas as pd
from pandas import read_excel
from unidecode import unidecode
import os
from datetime import datetime

from utils.safe_parse_date import safe_parse_date
import matplotlib.pyplot as plt
import io
from fastapi.responses import Response
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
    columns_dates = ['data_de_assinatura', 'data_de_termino_apos_aditivo/apostilamento', 'data_de_publicacao_na_plataforma_ceara_transparente', 'data_publicacao_no_doe']
    try:
        curr_dir = os.path.dirname(os.path.abspath(__file__))
        excel_file = os.path.join(curr_dir, "../data/Convênios 2007 - Setembro 2023.xlsx")
        df = read_excel(excel_file)
        df.columns = [unidecode(col.lower().replace(' ', '_')) for col in df.columns]
        df = df.where(pd.notna(df), None)
        
        data_agreement = [df[col] for col in columns_agreements if col in df.columns]
        data_values = [df[col] for col in columns_values if col in df.columns]
        data_dates = [df[col] for col in columns_dates if col in df.columns] # Adição de lista data_dates
        for cod, con, conv, obj, vit, virc, vicc, vat, vp, das, dta, dpc, dpd in zip(*data_agreement, *data_values, *data_dates): #incluindo data_dates no loop
            # Tratando dados de convênio e valores de convênio
            cod = None if pd.isna(cod) else cod
            con = None if pd.isna(con) else con
            conv = None if pd.isna(conv) else conv
            obj = None if pd.isna(obj) else obj
            vit = None if pd.isna(vit) else vit
            virc = None if pd.isna(virc) else virc
            vicc = None if pd.isna(vicc) else vicc
            vat = None if pd.isna(vat) else vat
            vp = None if pd.isna(vp) else vp
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
            # Cria as datas dos convênios
            data_assinatura = safe_parse_date(das)
            data_termino = safe_parse_date(dta)
            data_publi_ce = safe_parse_date(dpc)
            data_publi_doe = safe_parse_date(dpd)
            agreement_date = AgreementDates(
                agreement_id=agreement.id,
                data_assinatura=data_assinatura,
                data_termino=data_termino,
                data_publi_ce=data_publi_ce,
                data_publi_doe=data_publi_doe
            )
            db.add(agreement_date)
            db.commit()
            db.refresh(agreement_date)
            logger_dates.info(f'criando data de convênio {agreement_date.id}')
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

@router.get('/count/', description="Retorna a quantidade de convênios")
def count_agreements(db: Session = Depends(get_db)):
    try:
        quantity = db.exec(select(func.count(Agreement.id))).one()
    except Exception as e:
        logger.error(f"Erro ao buscar quantidade de convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao buscar quantidade de convênios")
    
    logger.info('buscando quantidade de convênios')
    return {"quantidade": quantity}

@router.get('/atributos/', description="Lista os atributos do modelo de convênios")
def get_agreements_attributes(
    codigo_plano_trabalho: Optional[str] = None,
    concedente: Optional[str] = None,
    convenente: Optional[str] = None,
    objeto: Optional[str] = None,
    db: Session = Depends(get_db)):
    try:
        query = select(Agreement)
        if codigo_plano_trabalho is not None:
            query = query.where(Agreement.codigo_plano_trabalho == codigo_plano_trabalho)
        if concedente is not None:
            query = query.where(func.lower(Agreement.concedente).contains(func.lower(concedente)))
        if convenente is not None:
            query = query.where(func.lower(Agreement.convenente).contains(func.lower(convenente)))
        if objeto is not None:
            query = query.where(Agreement.objeto == objeto)
        
        agreements = db.exec(query.order_by(Agreement.id)).all()
    except Exception as e:
        logger.error(f"Erro ao buscar convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao buscar convênios")
    
    logger.info('buscando convênios com os atributos fornecidos')
    result = [item.model_dump() for item in agreements]
    return result

@router.get('/search/codigo_plano_trabalho/', description='Faz uma pesquisa por palavra no código plano de trabalho de convênios')
def get_search_codigo_plano_trabalho(word: str = Query(min_length=5), db: Session = Depends(get_db)):
    try:
        data = db.exec(select(Agreement).where(func.lower(Agreement.codigo_plano_trabalho).contains(func.lower(word))).order_by(Agreement.id)).all()
    except Exception as e:
        logger.error(f'Erro ao listar os convenios pelo codigo plano de trabalho. Erro: {str(e)}')
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao listar os convenios pelo codigo plano de trabalho. Erro: {str(e)}')
    
    return [
        {
            'id': item.id,
            'codigo_plano_trabalho': item.codigo_plano_trabalho,
            'concedente': item.concedente,
            'convenente': item.convenente,
            'objeto': item.objeto
        } for item in data
    ]

@router.get('/search/concedente/', description='Faz uma pesquisa por palavra no concedente de convênios')
def get_search_concedente(word: str = Query(min_length=5), db: Session = Depends(get_db)):
    try:
        data = db.exec(select(Agreement).where(func.lower(Agreement.concedente).contains(func.lower(word))).order_by(Agreement.id)).all()
    except Exception as e:
        logger.error(f'Erro ao listar os convenios pelo concedente. Erro: {str(e)}')
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao listar os convenios pelo concedente. Erro: {str(e)}')
    
    return [
        {
            'id': item.id,
            'codigo_plano_trabalho': item.codigo_plano_trabalho,
            'concedente': item.concedente,
            'convenente': item.convenente,
            'objeto': item.objeto
        } for item in data
    ]

@router.get('/search/convenente/', description='Faz uma pesquisa por palavra no convenente de convênios')
def get_search_convenente(word: str = Query(min_length=5), db: Session = Depends(get_db)):
    try:
        data = db.exec(select(Agreement).where(func.lower(Agreement.convenente).contains(func.lower(word))).order_by(Agreement.id)).all()
    except Exception as e:
        logger.error(f'Erro ao listar os convenios pelo convenente. Erro: {str(e)}')
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao listar os convenios pelo convenente. Erro: {str(e)}')
    
    return [
        {
            'id': item.id,
            'codigo_plano_trabalho': item.codigo_plano_trabalho,
            'concedente': item.concedente,
            'convenente': item.convenente,
            'objeto': item.objeto
        } for item in data
    ]

@router.get('/search/objeto/', description='Faz uma pesquisa por palavra no objeto de convênios')
def get_search_objeto(word: str = Query(min_length=5), db: Session = Depends(get_db)):
    try:
        data = db.exec(select(Agreement).where(func.lower(Agreement.objeto).contains(func.lower(word))).order_by(Agreement.id)).all()
    except Exception as e:
        logger.error(f'Erro ao listar os convenios pelo objeto. Erro: {str(e)}')
        db.rollback()
        raise HTTPException(status_code=500, detail=f'Erro ao listar os convenios pelo objeto. Erro: {str(e)}')
    
    return [
        {
            'id': item.id,
            'codigo_plano_trabalho': item.codigo_plano_trabalho,
            'concedente': item.concedente,
            'convenente': item.convenente,
            'objeto': item.objeto
        } for item in data
    ]

@router.delete("/delete_all/", description="Deleta todos os convênios, valores e datas")
def delete_all_agreements(db: Session = Depends(get_db)):
    try:
        # Deletar todos os registros de agreement_values
        db.exec(delete(AgreementValues))
        db.commit()
        
        # Deletar todos os registros de agreement_dates
        db.exec(delete(AgreementDates))
        db.commit()
        
        # Deletar todos os registros de agreements
        db.exec(delete(Agreement))
        db.commit()
        
        # Resetar o contador de IDs
        db.exec(text("ALTER SEQUENCE agreement_values_id_seq RESTART WITH 1"))
        db.exec(text("ALTER SEQUENCE agreement_dates_id_seq RESTART WITH 1"))
        db.exec(text("ALTER SEQUENCE agreements_id_seq RESTART WITH 1"))
        db.commit()
    except Exception as e:
        logger.error(f"Erro ao deletar todos os convênios: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao deletar todos os convênios. Erro: {str(e)}")
        
    logger.info('deletando todos os convênios, valores e datas')
    return {"message": "Todos os convênios, valores e datas foram deletados com sucesso"}

@router.get("/comparison-original-updated")
def comparacao_valores_originais_atualizados(db: Session = Depends(get_db)):
    # Consulta ao banco de dados
    stmt = (
        select(
            func.strftime('%Y', Agreement.dates[0].data_assinatura).label('Ano_assinatura'),
            func.sum(Agreement.values[0].valor_inicial_total).label('Valor_original'),
            func.sum(Agreement.values[0].valor_atualizado_total).label('Valor_atualizado')
        )
        .group_by('Ano_assinatura')
        .order_by('Ano_assinatura')
    )

    result = db.exec(stmt).all()

    if not result:
        return {"message": "Nenhum convênio encontrado"}

    # Preparação dos dados para o gráfico
    df = pd.DataFrame(result)
    df['Ano_assinatura'] = pd.to_numeric(df['Ano_assinatura'])  # Converter para numérico
    df = df.set_index('Ano_assinatura')

    # Geração do gráfico de barras
    plt.figure(figsize=(12, 6))
    plt.bar(df.index - 0.2, df['Valor_original'], width=0.4, label='Valores Originais', alpha=0.7)
    plt.bar(df.index + 0.2, df['Valor_atualizado'], width=0.4, label='Valores Atualizados', alpha=0.7)
    plt.xlabel('Ano de Assinatura')
    plt.ylabel('Valor')
    plt.title('Comparação de Valores de Convênios por Ano')
    plt.legend()
    plt.xticks(df.index)
    plt.tight_layout()

    # Salvar o gráfico em um buffer de bytes
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)

    # Retornar o gráfico como uma imagem PNG
    return Response(content=buf.getvalue(), media_type="image/png")

@router.get("/evolution-value-paid")
def evolucao_valores_pagos(db: Session = Depends(get_db)):
    # Consulta ao banco de dados
    stmt = (
        select(
            func.strftime('%Y', Agreement.dates[0].data_assinatura).label('Ano de Assinatura'),
            func.sum(Agreement.values[0].valor_pago).label('Valor Pago')
        )
        .group_by('Ano de Assinatura')
        .order_by('Ano de Assinatura')
    )

    result = db.exec(stmt).all()

    if not result:
        return {"message": "Nenhum convênio encontrado"}

    # Preparação dos dados para o gráfico
    df = pd.DataFrame(result)
    df['Ano de Assinatura'] = pd.to_numeric(df['Ano de Assinatura'])  # Converter para numérico
    df = df.set_index('Ano de Assinatura')

    # Geração do gráfico de linhas
    plt.figure(figsize=(12, 6))
    plt.plot(df.index, df['Valor Pago'], marker='o')
    plt.title('Evolução dos Valores Totais Pagos de Convênios por Ano')
    plt.xlabel('Ano de Assinatura')
    plt.ylabel('Valor Pago')
    plt.grid(True)

    # Salvar o gráfico em um buffer de bytes
    buf = io.BytesIO()
    plt.savefig(buf, format="png")
    plt.close()
    buf.seek(0)

    # Retornar o gráfico como uma imagem PNG
    return Response(content=buf.getvalue(), media_type="image/png")
