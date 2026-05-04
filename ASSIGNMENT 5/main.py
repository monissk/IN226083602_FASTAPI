from fastapi import FastAPI, HTTPException, Query
from typing import Optional

app = FastAPI()

# PRODUCTS DATABASE
products = {
    1: {"name": "Laptop", "price": 500, "stock": 5, "category": "electronics"},
    2: {"name": "Phone", "price": 597, "stock": 3, "category": "electronics"},
    3: {"name": "Headphones", "price": 200, "stock": 0, "category": "electronics"},
    4: {"name": "Shoes", "price": 150, "stock": 10, "category": "fashion"},
    5: {"name": "T-shirt", "price": 50, "stock": 20, "category": "fashion"},
}

cart = {}
orders = []

# FILTER + SEARCH + SORT + PAGINATION

@app.get("/products")
def get_products(
    min_price: Optional[int] = None,
    max_price: Optional[int] = None,
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    sort_by: Optional[str] = None,
    page: int = 1,
    limit: int = 2
):
    result = list(products.items())

    # FILTER BY PRICE
    if min_price is not None:
        result = [(k, v) for k, v in result if v["price"] >= min_price]

    if max_price is not None:
        result = [(k, v) for k, v in result if v["price"] <= max_price]

    # FILTER BY CATEGORY
    if category:
        result = [(k, v) for k, v in result if v["category"] == category]

    # SEARCH BY KEYWORD
    if keyword:
        result = [(k, v) for k, v in result if keyword.lower() in v["name"].lower()]

    # SORT
    if sort_by == "price_asc":
        result.sort(key=lambda x: x[1]["price"])
    elif sort_by == "price_desc":
        result.sort(key=lambda x: x[1]["price"], reverse=True)

    # PAGINATION
    start = (page - 1) * limit
    end = start + limit
    paginated = result[start:end]

    return {
        "page": page,
        "total_items": len(result),
        "products": [{**{"id": k}, **v} for k, v in paginated]
    }


# ADD TO CART
@app.post("/cart/add")
def add_to_cart(product_id: int, quantity: int = 1):

    if product_id not in products:
        raise HTTPException(status_code=404, detail="Product not found")

    product = products[product_id]

    if product["stock"] == 0:
        raise HTTPException(status_code=400, detail="Out of stock")

    if quantity > product["stock"]:
        raise HTTPException(status_code=400, detail="Not enough stock")

    if product_id in cart:
        cart[product_id]["quantity"] += quantity
    else:
        cart[product_id] = {
            "name": product["name"],
            "price": product["price"],
            "quantity": quantity
        }

    return {"message": "Added to cart", "cart": cart}


# VIEW CART
@app.get("/cart")
def view_cart():
    if not cart:
        return {"message": "Cart empty"}

    total = 0
    items = []

    for pid, item in cart.items():
        subtotal = item["price"] * item["quantity"]
        total += subtotal

        items.append({
            "product_id": pid,
            "name": item["name"],
            "quantity": item["quantity"],
            "subtotal": subtotal
        })

    return {"items": items, "total": total}


# REMOVE ITEM
@app.delete("/cart/{product_id}")
def remove_item(product_id: int):
    if product_id not in cart:
        raise HTTPException(status_code=404, detail="Not in cart")

    del cart[product_id]
    return {"message": "Removed", "cart": cart}


# CHECKOUT
@app.post("/cart/checkout")
def checkout():
    if not cart:
        raise HTTPException(status_code=400, detail="Cart empty")

    total = 0

    for pid, item in cart.items():
        total += item["price"] * item["quantity"]
        products[pid]["stock"] -= item["quantity"]

    order = {
        "id": len(orders) + 1,
        "items": cart.copy(),
        "total": total
    }

    orders.append(order)
    cart.clear()

    return {"message": "Order placed", "order": order}


# VIEW ORDERS
@app.get("/orders")
def get_orders():
    return {"orders": orders}
