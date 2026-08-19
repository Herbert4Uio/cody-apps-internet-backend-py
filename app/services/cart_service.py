from sqlmodel import Session, select
from app.models.cart_item import CartItem, CartBulkCreate
from app.models.product import Product

def add_to_cart(session: Session, cart_bulk: CartBulkCreate, user_id: int) -> list[CartItem]:
    # Obtener el carrito actual del usuario
    statement = select(CartItem).where(CartItem.user_id == user_id)
    current_items = session.exec(statement).all()
    
    # Diccionario para búsqueda rápida
    current_cart_map = {item.product_id: item for item in current_items}
    
    # Agrupar las cantidades solicitadas por producto (por si el usuario manda duplicados en el mismo payload)
    requested_quantities = {}
    for item_in in cart_bulk.items:
        requested_quantities[item_in.product_id] = requested_quantities.get(item_in.product_id, 0) + item_in.quantity

    # Validaciones de existencia y stock
    for product_id, additional_qty in requested_quantities.items():
        product = session.get(Product, product_id)
        if not product:
            raise ValueError(f"El producto con ID {product_id} no existe.")
            
        existing_quantity = current_cart_map[product_id].quantity if product_id in current_cart_map else 0
        new_total_quantity = existing_quantity + additional_qty
        
        if new_total_quantity > product.stock:
            raise ValueError(f"Stock insuficiente para '{product.title}'. Disponible: {product.stock}, Solicitado en total: {new_total_quantity}.")
    
    updated_or_new_items = []
    
    for product_id, additional_qty in requested_quantities.items():
        if product_id in current_cart_map:
            # Upsert: El producto ya está, sumar cantidad
            existing_item = current_cart_map[product_id]
            existing_item.quantity += additional_qty
            session.add(existing_item)
            updated_or_new_items.append(existing_item)
        else:
            # Crear nuevo CartItem
            new_item = CartItem(user_id=user_id, product_id=product_id, quantity=additional_qty)
            session.add(new_item)
            updated_or_new_items.append(new_item)
            
    session.commit()
    
    # Refrescar los elementos devueltos
    for item in updated_or_new_items:
        session.refresh(item)
        
    return updated_or_new_items

def get_cart(session: Session, user_id: int) -> list[CartItem]:
    statement = select(CartItem).where(CartItem.user_id == user_id)
    return session.exec(statement).all()

def update_cart_item(session: Session, item_id: int, user_id: int, quantity: int) -> CartItem:
    item = session.get(CartItem, item_id)
    if not item or item.user_id != user_id:
        raise ValueError(f"El item del carrito con ID {item_id} no existe o no te pertenece.")
        
    product = session.get(Product, item.product_id)
    if product and quantity > product.stock:
        raise ValueError(f"Stock insuficiente para '{product.title}'. Disponible: {product.stock}.")
        
    item.quantity = quantity
    session.add(item)
    session.commit()
    session.refresh(item)
    return item

def remove_from_cart(session: Session, item_id: int, user_id: int) -> bool:
    item = session.get(CartItem, item_id)
    if not item or item.user_id != user_id:
        raise ValueError(f"El item del carrito con ID {item_id} no existe o no te pertenece.")
        
    session.delete(item)
    session.commit()
    return True

def clear_cart(session: Session, user_id: int) -> bool:
    statement = select(CartItem).where(CartItem.user_id == user_id)
    items = session.exec(statement).all()
    for item in items:
        session.delete(item)
    session.commit()
    return True

