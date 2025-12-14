def calculate_price(base_price, margin_pct, qty):
    if margin_pct >= 100: margin_pct = 99
    
    sell_price = base_price / (1 - (margin_pct/100))
    line_total = sell_price * qty
    return sell_price, line_total

# Test Case
base_price = 1000
qty = 50
margin_20 = 20

sp, lt = calculate_price(base_price, margin_20, qty)
print(f"Base: {base_price}, Margin: {margin_20}%, Qty: {qty}")
print(f"Sell Price: {sp:.2f} (Expected: 1250.00)")
print(f"Line Total: {lt:.2f} (Expected: 62500.00)")

gst = lt * 0.18
final = lt + gst
print(f"GST (18%): {gst:.2f}")
print(f"Final: {final:.2f}")
