from sqlmodel import SQLModel, Field

# Entidade de convênio
class Agreement(SQLModel, table=True):
    __tablename__ = "agreements"  # Table name
    id: int = Field(default=None, primary_key=True)