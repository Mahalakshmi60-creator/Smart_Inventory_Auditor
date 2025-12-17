def check_inventory(item_name):
    inventory = {
        "laptop": {"status": "low stock", "quantity": 2},
        "mouse": {"status": "available", "quantity": 15},
        "keyboard": {"status": "out of stock", "quantity": 0},
        "monitor": {"status": "available", "quantity": 8}
    }

    return inventory.get(
        item_name.lower(),
        {"status": "unknown", "quantity": 0}
    )
