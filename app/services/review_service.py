from sqlmodel import Session, select
from app.models.review import Review, ReviewCreate, ReviewUpdate

def create_review(session: Session, review_in: ReviewCreate, user_id: int, product_id: int) -> Review:
    review_db = Review.model_validate(review_in, update={"user_id": user_id, "product_id": product_id})
    
    session.add(review_db)
    session.commit()
    session.refresh(review_db)
    return review_db

def get_reviews_by_product(session: Session, product_id: int, skip: int = 0, limit: int = 100) -> list[Review]:
    statement = select(Review).where(Review.product_id == product_id).offset(skip).limit(limit)
    return session.exec(statement).all()

def update_review(session: Session, review_id: int, review_in: ReviewUpdate, user_id: int) -> Review | None:
    review_db = session.get(Review, review_id)
    if not review_db:
        return None
        
    # Validación de Propiedad
    if review_db.user_id != user_id:
        raise ValueError("No tienes permiso para modificar esta reseña")
        
    update_data = review_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(review_db, key, value)
        
    session.add(review_db)
    session.commit()
    session.refresh(review_db)
    return review_db

def delete_review(session: Session, review_id: int, user_id: int) -> bool:
    review_db = session.get(Review, review_id)
    if not review_db:
        return False
        
    # Validación de Propiedad
    if review_db.user_id != user_id:
        raise ValueError("No tienes permiso para eliminar esta reseña")
        
    session.delete(review_db)
    session.commit()
    return True
