from pricing import line_total

def cart_total(items):
    return round(sum(line_total(p, q) for p, q in items), 2)
