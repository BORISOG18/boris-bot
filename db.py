import json
import os

DB_FILE = "customers.json"

def _load():
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, "r") as f:
        return json.load(f)

def _save(data):
    with open(DB_FILE, "w") as f:
        json.dump(data, f, indent=2)

def save_customer(customer: dict):
    data = _load()
    data.append(customer)
    _save(data)

def get_all_customers():
    return _load()

def get_customer(query: str):
    data = _load()
    query = query.lower()
    return [c for c in data if query in c.get('name','').lower() or query in c.get('customer_id','').lower()]

def update_payment_status(customer_id: str, status: str) -> bool:
    data = _load()
    found = False
    for c in data:
        if c.get('customer_id') == customer_id:
            c['paid'] = status
            found = True
    if found:
        _save(data)
    return found
