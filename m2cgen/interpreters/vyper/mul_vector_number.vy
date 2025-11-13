@view
def mul_vector_number_{size}(v1: decimal[{size}], num: decimal) -> decimal[{size}]:
    v2: decimal[{size}] = empty(decimal[{size}])
    for i: uint96 in range({size}):
        v2[i] = v1[i] * num
    return v2
