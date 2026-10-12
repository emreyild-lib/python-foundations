# Mini Sales Calculator

# Welcome message
print("Welcome to the Mini Sales Calculator!")
print("--------------------------------------")

# Step 1: Prices of items
apple_price = 1.2
banana_price = 0.5
milk_price = 2.0
bread_price = 1.5
egg_price = 0.25

# Step 2: Quantities bought
apple_qty = 4
banana_qty = 6
milk_qty = 1
bread_qty = 2
egg_qty = 12

# Step 3: Calculate total for each item
apple_total = apple_price * apple_qty
banana_total = banana_price * banana_qty
milk_total = milk_price * milk_qty
bread_total = bread_price * bread_qty
egg_total = egg_price * egg_qty

# Step 4: Final total
total_bill = apple_total + banana_total + milk_total + bread_total + egg_total


# --- Fixed 10% Discount ---
def apply_discount(amount):
    discount = amount * 0.10  # 10% of the total
    return amount - discount

# Apply discount
discounted_total = apply_discount(total_bill)
print(f"Total Bill (after 10% discount): £{discounted_total:.2f}")
