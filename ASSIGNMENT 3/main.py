from fastapi import FastAPI

app = FastAPI()

#Product list
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "Monitor", "price": 8999, "category": "Electronics", "in_stock": False},

    #Q1.Add 3 more products
    {"id": 5, "name": "Laptop Stand", "price": 1299, "category": "Electronics", "in_stock": True},
    {"id": 6, "name": "Mechanical Keyboard", "price": 2499, "category": "Electronics", "in_stock": True},
    {"id": 7, "name": "Webcam", "price": 1899, "category": "Electronics", "in_stock": False},
]


#Q1.Endpoint
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


#Q2.Category Filter
@app.get("/products/category/{category_name}")
def get_by_category(category_name: str):

    result = [p for p in products if p["category"] == category_name]

    if not result:
        return {"error": "No products found in this category"}

    return {
        "category": category_name,
        "products": result,
        "total": len(result)
    }


#Q3.In-Stock Products
@app.get("/products/instock")
def get_instock():

    available = [p for p in products if p["in_stock"] == True]

    return {
        "in_stock_products": available,
        "count": len(available)
    }


#Q4.Store Summary
@app.get("/store/summary")
def store_summary():

    in_stock_count = len([p for p in products if p["in_stock"]])
    out_stock_count = len(products) - in_stock_count

    categories = list(set([p["category"] for p in products]))

    return {
        "store_name": "My E-commerce Store",
        "total_products": len(products),
        "in_stock": in_stock_count,
        "out_of_stock": out_stock_count,
        "categories": categories
    }




from fastapi import FastAPI, Query
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

#Initial Product Data
products = [
    {"id": 1, "name": "Wireless Mouse", "price": 599, "category": "Electronics", "in_stock": True},
    {"id": 2, "name": "Notebook", "price": 49, "category": "Stationery", "in_stock": True},
    {"id": 3, "name": "Pen Set", "price": 99, "category": "Stationery", "in_stock": True},
    {"id": 4, "name": "Monitor", "price": 8999, "category": "Electronics", "in_stock": False}
]

#Product Model
class Product(BaseModel):
    name: str
    price: int
    category: str
    in_stock: bool


#GET All Products
@app.get("/products")
def get_products():
    return {"products": products, "total": len(products)}


#GET Product by ID
@app.get("/products/{product_id}")
def get_product(product_id: int):
    for product in products:
        if product["id"] == product_id:
            return product
    return {"error": "Product not found"}


# POST Add Product
@app.post("/products")
def add_product(product: Product):
    new_id = products[-1]["id"] + 1 if products else 1

    new_product = {
        "id": new_id,
        "name": product.name,
        "price": product.price,
        "category": product.category,
        "in_stock": product.in_stock
    }

    products.append(new_product)

    return {
        "message": "Product added successfully",
        "product": new_product,
        "total_products": len(products)
    }


#PUT Update Product
@app.put("/products/{product_id}")
def update_product(product_id: int, price: Optional[int] = None, in_stock: Optional[bool] = None):

    for product in products:
        if product["id"] == product_id:

            if price is not None:
                product["price"] = price

            if in_stock is not None:
                product["in_stock"] = in_stock

            return {"message": "Product updated", "product": product}

    return {"error": "Product not found"}


#DELETE Product
@app.delete("/products/{product_id}")
def delete_product(product_id: int):

    for i, product in enumerate(products):
        if product["id"] == product_id:
            deleted = products.pop(i)
            return {"message": "Product deleted", "product": deleted}

    return {"error": "Product not found"}


#Q5.Product Audit Endpoint
@app.get("/products/audit")
def product_audit():

    in_stock = [p for p in products if p["in_stock"]]
    out_stock = [p for p in products if not p["in_stock"]]

    total_value = sum(p["price"] * 10 for p in in_stock)

    expensive = max(products, key=lambda p: p["price"])

    return {
        "total_products": len(products),
        "in_stock_count": len(in_stock),
        "out_of_stock_names": [p["name"] for p in out_stock],
        "total_stock_value": total_value,
        "most_expensive": {
            "name": expensive["name"],
            "price": expensive["price"]
        }
    }

#BONUS: Apply Discount
@app.put("/products/discount")
def apply_discount(category: str = Query(...), discount_percent: int = Query(...)):

    updated = []

    for p in products:
        if p["category"].lower() == category.lower():
            p["price"] = int(p["price"] * (1 - discount_percent / 100))
            updated.append(p)

    if not updated:
        return {"message": "No products found"}

    return {
        "updated_count": len(updated),
        "products": updated
    }
