import io
from math import ceil
import os
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from matplotlib import pyplot as plt
import pandas as pd
from sqlmodel import Session, and_, select
from sqlalchemy.sql import func
from database import get_db
from models.administrative_process import AdministrativeProcess
from services.configs import administrative_processes_logger as logger
 
# Criar roteador
router = APIRouter(prefix="/administrative_processes", tags=["Administrative Processes"])

# Criar um processo administrativo
@router.post("/")
async def create_administrative_processes(db: Session = Depends(get_db)):
    try:
        file_name = "Contratos 2016 - 2020.xlsx"  

        caminho_arquivo = os.path.join("data", file_name)

        df = pd.read_excel(caminho_arquivo)

        df.columns = df.columns.str.strip()

        print(df.columns)

        colunas_desejadas = [
            'Nº do Processo - SPU',
            'Modalidade de licitação',
            'Justificativa',
            'Status str',
            'Situação Física'
        ]

        for coluna in colunas_desejadas:
            if coluna not in df.columns:
                raise ValueError(f"A coluna '{coluna}' não foi encontrada no arquivo {file_name}.")

        df_filtrado = df[colunas_desejadas]

        for _, row in df_filtrado.iterrows():
            administrative_process = AdministrativeProcess(
                n_do_processo_spu=row['Nº do Processo - SPU'] if pd.notna(row['Nº do Processo - SPU']) else None,
                modalidade_de_licitacao=row['Modalidade de licitação'] if pd.notna(row['Modalidade de licitação']) else None,
                justificativa=row['Justificativa'] if pd.notna(row['Justificativa']) else None,
                status_str=row['Status str'] if pd.notna(row['Status str']) else None,
                situacao_fisica=row['Situação Física'] if pd.notna(row['Situação Física']) else None
            )

            db.add(administrative_process)

        db.commit()

        return {"message": "Processos administrativos criados com sucesso!"}

    except Exception as e:
        db.rollback()  
        return {"message": f"Erro ao criar processos administrativos: {str(e)}"}


# Atualizar um processo administrativo
@router.put("/{process_id}", description="Atualiza um processo administrativo")
def update_process(process_id: int, updated_process: AdministrativeProcess, db: Session = Depends(get_db)):
    try:
        process = db.get(AdministrativeProcess, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Processo administrativo não encontrado")
        
        for key, value in updated_process.dict(exclude_unset=True).items():
            setattr(process, key, value)
        
        db.commit()
        logger.info(f'Processo Administrativo atualizado: {process_id}')
        return {"message": "Processo Administrativo atualizado com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao atualizar processo administrativo: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao atualizar processo administrativo")

# Deletar um processo administrativo
@router.delete("/{process_id}", description="Deleta um processo administrativo")
def delete_process(process_id: int, db: Session = Depends(get_db)):
    try:
        process = db.get(AdministrativeProcess, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Processo administrativo não encontrado")
        
        db.delete(process)
        db.commit()
        logger.info(f'Processo Administrativo deletado: {process_id}')
        return {"message": "Processo Administrativo deletado com sucesso"}
    except Exception as e:
        logger.error(f"Erro ao deletar processo administrativo: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao deletar processo administrativo")

# Buscar um processo administrativo pelo ID
@router.get("/{process_id}", response_model=AdministrativeProcess, description="Obtém um processo administrativo")
def get_process(process_id: int, db: Session = Depends(get_db)):
    try:
        process = db.get(AdministrativeProcess, process_id)
        if not process:
            raise HTTPException(status_code=404, detail="Processo administrativo não encontrado")
        return process
    except Exception as e:
        logger.error(f"Erro ao obter processo administrativo: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter processo administrativo")

# Listar processos administrativos com paginação e filtros
@router.get("/", description="Lista os processos administrativos")
def list_processes(
    db: Session = Depends(get_db),
    page: Optional[int] = Query(default=1, ge=1, description="Página de processos"),
    limit: Optional[int] = Query(default=100, ge=1, le=100, description="Quantidade de processos a serem retornados"),
    contract_id: Optional[int] = Query(default=None, description="ID do contrato relacionado"),
    status_do_instrumento: Optional[str] = Query(default=None, description="Status do processo"),
    situacao_fisica: Optional[str] = Query(default=None, description="Situação física do processo"),
    modalidade_de_licitacao: Optional[str] = Query(default=None, description="Modalidade de licitação")
):
    try:
        filters = []
        if contract_id:
            filters.append(AdministrativeProcess.contract_id == contract_id)
        if status_do_instrumento:
            filters.append(AdministrativeProcess.status_do_instrumento == status_do_instrumento)
        if situacao_fisica:
            filters.append(AdministrativeProcess.situacao_fisica == situacao_fisica)
        if modalidade_de_licitacao:
            filters.append(AdministrativeProcess.modalidade_de_licitacao == modalidade_de_licitacao)
        
        offset = (page - 1) * limit
        stmt = select(AdministrativeProcess).where(and_(*filters)).offset(offset).limit(limit) if filters else select(AdministrativeProcess).offset(offset).limit(limit)
        processes = db.exec(stmt).all()

        total_processes = db.exec(select(func.count()).select_from(AdministrativeProcess).where(and_(*filters))).first() if filters else db.exec(select(func.count()).select_from(AdministrativeProcess)).first()
        total_pages = ceil(total_processes / limit) if total_processes else 1
        
        return {
            "message": "Processos Administrativos listados com sucesso",
            "data": processes,
            "page": page,
            "limit": limit,
            "total_processes": total_processes,
            "total_pages": total_pages
        }
    except Exception as e:
        logger.error(f"Erro ao listar processos administrativos: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Erro ao listar processos administrativos")
# Contagem de processos por status
@router.get("/stats/status")
def count_by_status(db: Session = Depends(get_db)):
    try:
        stmt = select(AdministrativeProcess.status_str, func.count()).group_by(AdministrativeProcess.status_str)
        results = db.exec(stmt).all()
        return {"status_distribution": dict(results)}
    except Exception as e:
        logger.error(f"Erro ao contar processos por status: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter estatísticas de status")


# Contagem de processos por ano
@router.get("/stats/year")
def count_by_year(db: Session = Depends(get_db)):
    try:
        stmt = select(func.extract('year', AdministrativeProcess.data_criacao), func.count()).group_by(func.extract('year', AdministrativeProcess.data_criacao))
        results = db.exec(stmt).all()
        return {"year_distribution": dict(results)}
    except Exception as e:
        logger.error(f"Erro ao contar processos por ano: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter estatísticas por ano")


# Contagem de processos por modalidade
@router.get("/stats/modality")
def count_by_modality(db: Session = Depends(get_db)):
    try:
        stmt = select(AdministrativeProcess.modalidade_de_licitacao, func.count()).group_by(AdministrativeProcess.modalidade_de_licitacao)
        results = db.exec(stmt).all()
        return {"modality_distribution": dict(results)}
    except Exception as e:
        logger.error(f"Erro ao contar processos por modalidade: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao obter estatísticas de modalidade")


# Buscar processos por múltiplos filtros
@router.get("/search")
def search_processes(
    status: Optional[str] = None,
    modalidade: Optional[str] = None,
    db: Session = Depends(get_db)
):
    try:
        stmt = select(AdministrativeProcess)
        if status:
            stmt = stmt.where(AdministrativeProcess.status_str == status)
        if modalidade:
            stmt = stmt.where(AdministrativeProcess.modalidade_de_licitacao == modalidade)
        results = db.exec(stmt).all()
        return {"data": results}
    except Exception as e:
        logger.error(f"Erro ao buscar processos administrativos: {str(e)}")
        raise HTTPException(status_code=500, detail="Erro ao buscar processos")
    
@router.get("/chart/status")
def chart_status(db: Session = Depends(get_db)):
    data = db.exec(select(AdministrativeProcess.status_str, func.count()).group_by(AdministrativeProcess.status_str)).all()
    labels, values = zip(*data) if data else ([], [])
    plt.figure(figsize=(6,6))
    plt.pie(values, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Distribuição de Processos por Status")
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")

# Gráfico: Evolução de processos ao longo dos anos
@router.get("/chart/evolution")
def chart_evolution(db: Session = Depends(get_db)):
    data = db.exec(select(func.extract('year', AdministrativeProcess.data_criacao), func.count()).group_by(func.extract('year', AdministrativeProcess.data_criacao)).order_by(func.extract('year', AdministrativeProcess.data_criacao))).all()
    years, counts = zip(*data) if data else ([], [])
    plt.figure(figsize=(8,5))
    plt.plot(years, counts, marker='o', linestyle='-')
    plt.xlabel("Ano")
    plt.ylabel("Número de Processos")
    plt.title("Evolução de Processos Administrativos")
    plt.grid()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")

# Gráfico: Distribuição por modalidade de licitação
@router.get("/chart/modalidade")
def chart_modalidade(db: Session = Depends(get_db)):
    data = db.exec(select(AdministrativeProcess.modalidade_de_licitacao, func.count()).group_by(AdministrativeProcess.modalidade_de_licitacao)).all()
    labels, values = zip(*data) if data else ([], [])
    plt.figure(figsize=(10,5))
    plt.bar(labels, values, color='blue')
    plt.xlabel("Modalidade de Licitação")
    plt.ylabel("Quantidade")
    plt.title("Distribuição por Modalidade de Licitação")
    plt.xticks(rotation=45, ha='right')
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    plt.close()
    buf.seek(0)
    return Response(content=buf.getvalue(), media_type="image/png")
