@view
def add_vectors_{size}(v1: decimal[{size}], v2: decimal[{size}]) -> decimal[{size}]:
    v3: decimal[{size}] = empty(decimal[{size}])
    for i: uint96 in range({size}):
        v3[i] = v1[i] + v2[i]
    return v3
