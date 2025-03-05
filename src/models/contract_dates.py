from datetime import datetime
from typing import Optional
from sqlmodel import Relationship, SQLModel, Field

# Entidade de datas de contrato
class ContractDates(SQLModel, table=True):
    __tablename__ = "contract_dates"  # Table name
    
    id: int = Field(default=None, primary_key=True)
    contract_id: int = Field(foreign_key="contracts.id", ondelete='CASCADE') # Foreign key to Contract
    data_de_assinatura: Optional[datetime]
    data_de_termino_original: Optional[datetime]
    data_de_termino_apos_aditivo: Optional[datetime]
    data_de_rescisao: Optional[datetime]
    data_publicacao_no_doe: Optional[datetime]
    
    contract: "Contract" = Relationship(back_populates="dates")