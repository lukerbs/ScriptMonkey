import codemonkey

codemonkey.run_codemonkey()


def calculate_total(price, quantity):
    return price * quantity


def add_tax(total, tax_rate):
    # Convert tax_rate to float
    return total + float(tax_rate)


total = calculate_total(100, 2)
tax_rate = "0.08"
final_total = add_tax(total, tax_rate)

print(f"Final total with tax: {final_total}")
