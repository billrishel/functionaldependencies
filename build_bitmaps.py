from bitstring import BitArray, BitStream

def create_bitmap_from_points_list(points, nr_attributes):

    m = BitArray('0b'+'0'*2**nr_attributes)
    for p in points:
        m[p] = 1
    return m

# this function builds two bitmap tables,
# given & impled, with both tables representing
# 2**nrAttributes bits for nrAttributes rows
def build_bitmaps_1(given, implied, nrAttributes):

    m = BitArray('0b'+'0'*2**nrAttributes)
    n = m.copy()
    n.invert()

    for j in range(nrAttributes):
        b = m.copy()
        step = 2**(j)
        a1=0
        a2=a1+step
        for i in range(0,32,step):
            b[a1:a2] = n[a1:a2]
            a1=a2+step
            a2=a1+step
        given.append(b[:])

    for j in range(nrAttributes):
        implied.append(given[j].copy())

    for j in range(nrAttributes):
        implied[j].invert()


def build_bitmaps(given, implied, nr_attributes):

    for i in range(nr_attributes):
        given.append( BitArray('0b'+'0'*2**nr_attributes) )    
    mask = 1
    for j in range(nr_attributes):
        for i in range(2**nr_attributes):
            given[j][i] = (i & mask) != 0
        mask *= 2

    for j in range(nr_attributes):
        implied.append(given[j].copy())

    for j in range(nr_attributes):
        implied[j].invert()
