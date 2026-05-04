from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import Optional

app = FastAPI()

# -----------------------------
# DATA
# -----------------------------
menu = [
    {"id": 1, "name": "Pizza", "price": 299, "category": "Pizza", "is_available": True},
    {"id": 2, "name": "Burger", "price": 149, "category": "Burger", "is_available": True},
    {"id": 3, "name": "Pasta", "price": 199, "category": "Pizza", "is_available": False},
    {"id": 4, "name": "Coke", "price": 59, "category": "Drink", "is_available": True},
    {"id": 5, "name": "Brownie", "price": 99, "category": "Dessert", "is_available": True},
    {"id": 6, "name": "Fries", "price": 79, "category": "Burger", "is_available": True}
]

orders = []
cart = []
order_counter = 1

# -----------------------------
# HELPERS
# -----------------------------
def find_item(item_id):
    for item in menu:
        if item["id"] == item_id:
            return item
    return None

def calculate_total(price, quantity):
    return price * quantity

# -----------------------------
# DAY 1 (GET APIs)
# -----------------------------
@app.get("/")
def home():
    return {"message": "Welcome to Food Delivery App"}

@app.get("/menu")
def get_menu():
    return {"menu": menu, "total": len(menu)}

@app.get("/menu/search")
def search_menu(keyword: str):
    result = [i for i in menu if keyword.lower() in i["name"].lower()]
    return {"results": result}

@app.get("/menu/summary")
def summary():
    return {
        "total": len(menu),
        "available": len([i for i in menu if i["is_available"]])
    }

# -----------------------------
# DAY 6 (ADVANCED APIs FIRST)
# -----------------------------
@app.get("/menu/sort")
def sort_menu(order: str = "asc"):
    sorted_menu = sorted(menu, key=lambda x: x["price"], reverse=(order == "desc"))
    return {"sorted": sorted_menu}

@app.get("/menu/page")
def paginate(page: int = 1, limit: int = 3):
    start = (page - 1) * limit
    return {"data": menu[start:start + limit]}

@app.get("/menu/browse")
def browse(keyword: Optional[str] = None, page: int = 1):
    result = menu

    if keyword:
        result = [i for i in result if keyword.lower() in i["name"].lower()]

    start = (page - 1) * 3
    return {"data": result[start:start + 3]}

# -----------------------------
# IMPORTANT → KEEP LAST
# -----------------------------
@app.get("/menu/{item_id}")
def get_item(item_id: int):
    item = find_item(item_id)
    if not item:
        return {"error": "Item not found"}
    return item

# -----------------------------
# DAY 2 (POST + VALIDATION)
# -----------------------------
class Order(BaseModel):
    customer_name: str = Field(..., min_length=2)
    item_id: int
    quantity: int = Field(..., gt=0)

@app.post("/orders")
def create_order(order: Order):
    global order_counter

    item = find_item(order.item_id)
    if not item:
        return {"error": "Item not found"}

    total = calculate_total(item["price"], order.quantity)

    new_order = {
        "order_id": order_counter,
        "customer": order.customer_name,
        "item": item["name"],
        "quantity": order.quantity,
        "total": total
    }

    orders.append(new_order)
    order_counter += 1

    return new_order

# -----------------------------
# CRUD OPERATIONS
# -----------------------------
class MenuItem(BaseModel):
    name: str
    price: int
    category: str
    is_available: bool = True

@app.post("/menu")
def add_item(item: MenuItem):
    new_id = menu[-1]["id"] + 1 if menu else 1

    new_item = item.dict()
    new_item["id"] = new_id

    menu.append(new_item)

    return new_item

@app.put("/menu/{item_id}")
def update_item(item_id: int, price: Optional[int] = None):
    item = find_item(item_id)
    if not item:
        return {"error": "Not found"}

    if price:
        item["price"] = price

    return item

@app.delete("/menu/{item_id}")
def delete_item(item_id: int):
    item = find_item(item_id)
    if not item:
        return {"error": "Not found"}

    menu.remove(item)
    return {"message": "Deleted"}

# -----------------------------
# WORKFLOW (CART)
# -----------------------------
@app.post("/cart/add")
def add_cart(item_id: int, quantity: int):
    item = find_item(item_id)

    if not item:
        return {"error": "Item not found"}

    for c in cart:
        if c["item_id"] == item_id:
            c["quantity"] += quantity
            return {"message": "Cart updated", "cart": cart}

    cart.append({"item_id": item_id, "quantity": quantity})

    return {"message": "Item added", "cart": cart}

@app.get("/cart")
def view_cart():
    total = 0

    for c in cart:
        item = find_item(c["item_id"])
        total += item["price"] * c["quantity"]

    return {"cart": cart, "total": total}

@app.post("/cart/checkout")
def checkout():
    global order_counter

    if not cart:
        return {"error": "Cart empty"}

    for c in cart:
        item = find_item(c["item_id"])
        orders.append({
            "order_id": order_counter,
            "item": item["name"]
        })
        order_counter += 1

    cart.clear()

    return {"message": "Order placed"}
