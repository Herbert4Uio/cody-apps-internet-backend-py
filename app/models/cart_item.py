from sqlmodel import SQLModel, Field

class CartItemBase(SQLModel):
    product_id: int = Field(foreign_key="product.id")
    quantity: int = Field(default=1, ge=1)

# Modelo principal para la Base de Datos
class CartItem(CartItemBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    
# Schema Público para Lectura
class CartItemPublic(CartItemBase):
    id: int
    user_id: int

# Schema para Crear
# No incluye user_id por diseño y seguridad
class CartItemCreate(CartItemBase):
    pass

# Schema Envoltorio para recibir múltiples items en una sola petición
class CartBulkCreate(SQLModel):
    items: list[CartItemCreate]
