from typing import Any
from fastapi import APIRouter, status, HTTPException

from app.api.deps import SessionDep, CurrentUser
from app.models.review import ReviewCreate, ReviewPublic, ReviewUpdate
from app.services import review_service, product_service

router = APIRouter()

@router.post("/{product_id}/reviews", response_model=ReviewPublic, status_code=status.HTTP_201_CREATED, summary="Dejar una Reseña")
def create_review(
    session: SessionDep,
    current_user: CurrentUser,
    product_id: int,
    review_in: ReviewCreate,
) -> Any:
    """
    Permite a un usuario autenticado dejar una reseña (calificación de 1 a 5 y un comentario) para un producto.
    
    **Nota de Seguridad**: El ID del usuario se inyecta desde el token de la sesión de manera obligatoria y segura.
    """
    return review_service.create_review(
        session=session,
        review_in=review_in,
        user_id=current_user.id,
        product_id=product_id
    )

@router.get("/{product_id}/reviews", response_model=list[ReviewPublic], summary="Listar Reseñas")
def get_reviews(
    session: SessionDep,
    product_id: int,
    skip: int = 0,
    limit: int = 100,
) -> Any:
    """
    Recupera la lista de reseñas asociadas a un producto. Endpint público.
    """
    product = product_service.get_product_by_id(session=session, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
        
    return review_service.get_reviews_by_product(session=session, product_id=product_id, skip=skip, limit=limit)

@router.patch("/{product_id}/reviews/{review_id}", response_model=ReviewPublic, summary="Actualizar Reseña")
def update_review(
    session: SessionDep,
    current_user: CurrentUser,
    product_id: int,
    review_id: int,
    review_in: ReviewUpdate,
) -> Any:
    """
    Permite al autor original actualizar su reseña (calificación y/o comentario).
    """
    try:
        review_db = review_service.update_review(
            session=session,
            review_id=review_id,
            review_in=review_in,
            user_id=current_user.id
        )
        if not review_db:
            raise HTTPException(status_code=404, detail="Reseña no encontrada")
        # Validación de que la reseña realmente pertenece a este producto
        if review_db.product_id != product_id:
            raise HTTPException(status_code=400, detail="La reseña no pertenece a este producto")
        return review_db
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))

@router.delete("/{product_id}/reviews/{review_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Eliminar Reseña")
def delete_review(
    session: SessionDep,
    current_user: CurrentUser,
    product_id: int,
    review_id: int,
) -> None:
    """
    Permite al autor original eliminar permanentemente su reseña.
    """
    try:
        deleted = review_service.delete_review(
            session=session,
            review_id=review_id,
            user_id=current_user.id
        )
        if not deleted:
            raise HTTPException(status_code=404, detail="Reseña no encontrada")
        return None
    except ValueError as e:
        raise HTTPException(status_code=403, detail=str(e))
