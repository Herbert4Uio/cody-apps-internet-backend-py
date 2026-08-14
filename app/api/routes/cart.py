from typing import Any
from fastapi import APIRouter, status, HTTPException

from app.api.deps import SessionDep, CurrentUser
from app.models.cart_item import CartBulkCreate, CartItemPublic
from app.services import cart_service

router = APIRouter()

@router.post("/", response_model=list[CartItemPublic], status_code=status.HTTP_201_CREATED, summary="Añadir Múltiples al Carrito")
def add_to_cart(
    session: SessionDep,
    current_user: CurrentUser,
    cart_bulk: CartBulkCreate,
) -> Any:
    """
    Añade una lista de productos al carrito de compras personal del usuario. 
    Si el producto ya existe en el carrito, se incrementará la cantidad (Upsert).
    
    **Nota de Seguridad**: El sistema lee quién es el usuario directamente del Token JWT y guarda los productos en su carrito.
    """
    try:
        return cart_service.add_to_cart(
            session=session,
            cart_bulk=cart_bulk,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
