from sqlmodel import SQLModel, Field

class AdministrativeProcess(SQLModel, table=True):
    __tablename__ = "administrative_processes"  # Table name
    
    id: int = Field(default=None, primary_key=True)
    contract_id: int = Field(foreign_key="contracts.id")  # Foreign key to Contract
    status: str = Field(index=True)  # Corresponde à coluna "Status str"
    physical_situation: str = Field(index=True)  # Corresponde à coluna "Situação Física"
    bidding_modality: str = Field(index=True)  # Corresponde à coluna "Modalidade de licitação"
