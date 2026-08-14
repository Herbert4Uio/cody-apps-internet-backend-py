from typing import Any
from fastapi import APIRouter, HTTPException, status

from app.api.deps import SessionDep, CurrentUser
from app.models.product import Product, ProductCreate, ProductPublic, ProductUpdate
from app.services import product_service

router = APIRouter()

@router.get("/", response_model=list[ProductPublic], summary="Listar Productos")
def get_products(session: SessionDep, current_user: CurrentUser, skip: int = 0, limit: int = 100) -> Any:
    """
    Recupera una lista paginada de todos los productos disponibles en la base de datos.
    """
    return product_service.get_products(session=session, skip=skip, limit=limit)

@router.get("/{product_id}", response_model=ProductPublic, summary="Obtener un Producto")
def get_product(session: SessionDep, current_user: CurrentUser, product_id: int) -> Any:
    """
    Busca un producto específico mediante su ID. 
    Lanza un error 404 si el producto no es encontrado.
    """
    product = product_service.get_product_by_id(session=session, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product

@router.post("/", response_model=ProductPublic, status_code=status.HTTP_201_CREATED, summary="Crear Producto")
def create_product(session: SessionDep, current_user: CurrentUser, product_in: ProductCreate) -> Any:
    """
    Crea un nuevo producto en el catálogo. Requiere el título, precio y un ID de categoría válida.
    """
    return product_service.create_product(session=session, product_in=product_in)

@router.patch("/{product_id}", response_model=ProductPublic, summary="Actualizar Producto")
def update_product(session: SessionDep, current_user: CurrentUser, product_id: int, product_in: ProductUpdate) -> Any:
    """
    Actualiza parcialmente los datos de un producto.
    Permite modificar únicamente los campos enviados en el cuerpo JSON (Parcheo Parcial).
    """
    product_db = product_service.update_product(session=session, product_id=product_id, product_in=product_in)
    if not product_db:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return product_db

@router.delete("/{product_id}", summary="Eliminar Producto")
def delete_product(session: SessionDep, current_user: CurrentUser, product_id: int) -> dict:
    """
    Elimina de manera permanente un producto a partir de su ID.
    """
    deleted = product_service.delete_product(session=session, product_id=product_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return {"mensaje": f"Producto {product_id} borrado exitosamente"}
