from typing import Any
from fastapi import APIRouter, status, HTTPException

from app.api.deps import SessionDep, CurrentUser
from app.models.cart_item import CartBulkCreate, CartItemPublic, CartItemUpdate
from app.services import cart_service

router = APIRouter()

@router.get("/", response_model=list[CartItemPublic], summary="Ver mi Carrito")
def get_cart(
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Obtiene todos los productos en el carrito de compras del usuario actual.
    """
    return cart_service.get_cart(session=session, user_id=current_user.id)

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

@router.patch("/{item_id}", response_model=CartItemPublic, summary="Actualizar Cantidad de un Item")
def update_cart_item(
    item_id: int,
    item_in: CartItemUpdate,
    session: SessionDep,
    current_user: CurrentUser,
) -> Any:
    """
    Actualiza la cantidad de un producto específico en el carrito.
    """
    try:
        return cart_service.update_cart_item(
            session=session,
            item_id=item_id,
            user_id=current_user.id,
            quantity=item_in.quantity
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar Item del Carrito")
def remove_from_cart(
    item_id: int,
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    """
    Elimina un producto específico del carrito del usuario.
    """
    try:
        cart_service.remove_from_cart(
            session=session,
            item_id=item_id,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.delete("/", status_code=status.HTTP_204_NO_CONTENT, summary="Vaciar Carrito")
def clear_cart(
    session: SessionDep,
    current_user: CurrentUser,
) -> None:
    """
    Elimina todos los productos del carrito del usuario actual.
    """
    cart_service.clear_cart(session=session, user_id=current_user.id)
