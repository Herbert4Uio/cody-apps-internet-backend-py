from typing import Optional
from sqlmodel import SQLModel, Field

class ReviewBase(SQLModel):
    rating: int = Field(ge=1, le=5)
    comment: str

# Modelo principal para la Base de Datos
class Review(ReviewBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    product_id: int = Field(foreign_key="product.id")
    
# Schema Público para Lectura
class ReviewPublic(ReviewBase):
    id: int
    user_id: int
    product_id: int

# Schema para Crear
class ReviewCreate(ReviewBase):
    pass

# Schema para Actualizar
class ReviewUpdate(SQLModel):
    rating: int | None = Field(default=None, ge=1, le=5)
    comment: str | None = None
