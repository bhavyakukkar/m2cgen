def sigmoid(x: decimal) -> decimal:
    z: decimal = empty(decimal)
    if x < 0.0:
        z = math.exp(x)
        return z / (1.0 + z)
    return 1.0 / (1.0 + math.exp(-x))
