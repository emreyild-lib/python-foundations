## Install requirement:
# pip install tabulate

from datetime import date
from tabulate import tabulate
import csv

today = date.today().isoformat()

# ---------- 1) Track ingredient usage ----------
inventory = {
    "Milk (L)": {"stock": 20, "reorder": 5},
    "Flour (kg)": {"stock": 50, "reorder": 10},
    "Eggs (pcs)": {"stock": 200, "reorder": 50},
    "Butter (kg)": {"stock": 15, "reorder": 4},   # New ingredient
}

usage_today = {
    "Milk (L)": 3,
    "Flour (kg)": 7,
    "Eggs (pcs)": 40,
    "Butter (kg)": 12,   # Butter usage today
}

# Update stock after today's usage
for item, used in usage_today.items():
    inventory[item]["stock"] -= used

# Create inventory rows for reporting
inv_rows = [(k, v["stock"], v["reorder"]) for k, v in inventory.items()]

# Identify low stock items
low_stock = [(k, v["stock"], v["reorder"])
             for k, v in inventory.items()
             if v["stock"] <= v["reorder"]]

# ---------- 2) Print results ----------
print("\n=== Updated Inventory ===")
print(tabulate(inv_rows, headers=["Ingredient", "Stock Left", "Reorder Level"], tablefmt="grid"))

print("\n=== Low Stock Alert ===")
if low_stock:
    print(tabulate(low_stock, headers=["Ingredient", "Stock Left", "Reorder Level"], tablefmt="grid"))
else:
    print("All ingredients are sufficiently stocked.")

# ---------- 3) Save inventory CSV ----------
with open(f"inventory_{today}.csv", "w", newline="") as f:
    w = csv.writer(f)
    w.writerow(["Ingredient", "Stock Left", "Reorder Level"])
    w.writerows(inv_rows)


if low_stock:
    print("\n=== Low Stock Alert ===")
    print(tabulate(low_stock, headers=["Ingredient", "Stock", "Reorder"], tablefmt="grid"))
    with open(f"low_stock_{today}.csv", "w", newline="") as f:
        w = csv.writer(f);
        w.writerow(["Ingredient", "Stock", "Reorder"]);
        w.writerows(low_stock)
else:
    print("\nNo items below reorder level ✅")

# ---------- 2) End-of-day profit report ----------
sales = [
    {"item": "Latte", "qty": 10, "price": 3.5, "cost": 1.1},
    {"item": "Cake", "qty": 12, "price": 2.8, "cost": 1.0},
]
revenue = sum(s["qty"] * s["price"] for s in sales)
cogs = sum(s["qty"] * s["cost"] for s in sales)
profit = revenue - cogs
margin = round(profit / revenue * 100, 2)

profit_row = [revenue, cogs, profit, margin]

print("\n=== Profit Summary ===")
print(tabulate([profit_row], headers=["Revenue", "COGS", "Profit", "Margin %"], tablefmt="grid"))

with open(f"profit_summary_{today}.csv", "w", newline="") as f:
    w = csv.writer(f);
    w.writerow(["Revenue", "COGS", "Profit", "Margin %"]);
    w.writerow(profit_row)

# ---------- 3) Staff Schedule ----------
staff = [
    ["Name", "Role", "Start", "End"],
    ["Ava", "Barista", "09:00", "17:00"],
    ["Noah", "Cashier", "10:00", "18:00"],
]

print("\n=== Staff Schedule ===")
print(tabulate(staff[1:], headers=staff[0], tablefmt="grid"))

with open(f"staff_schedule_{today}.csv", "w", newline="") as f:
    w = csv.writer(f);
    w.writerows(staff)
