from collections import defaultdict
from FD import FunctionalDependency
from FD_Analysis import *
from copy import deepcopy

def none_bitmap(num_attrs):
    return BitArray('0b'+'0'*2**num_attrs)

def rac_list_essentials(rac_list, num_bits):

    map = [0 for i in range(num_bits)]
    essentials = set()

    for c in rac_list:
        for i in range(len(c.bitmap())):
            map[i] += c.bitmap()[i]
            
    for c in rac_list:
        for i in range(len(c.bitmap())):
            if c.bitmap()[i] == 1 and map[i] == 1:
                essentials.add(c)

    return essentials

def fd_list_from_list_rac_list(l_rac_list):
    fd_plus_list = []
    for l in l_rac_list:
        for c in l:
            fd_plus_list.append( create_fd_from_rac(c) )
    return fd_plus_list

#def check_bm_empty(bm):
#    for i in range(len(bm)):
        
def reduce_for_size(rac_list, debug=False):
    if len(rac_list) < 3:
        return rac_list
    remove = []
    union_bm = rac_list_union_bitmap(rac_list)
    rac_cand_list = deepcopy(rac_list)
    for cand in rac_cand_list:
#        print cand.givenAttrs(),
#        print cand.impliedAttr(),":", cand.id

    #    print "(",cand.id,")"
        sub_cand_list = [c for c in rac_cand_list if c != cand]

        sub_cand_list_bm = rac_list_union_bitmap(sub_cand_list)
#        print (sub_cand_list_bm ^ union_bm).bin
        if bitmap_covered_by_bitmap(cand.bitmap(), sub_cand_list_bm):
            temp_cand_list = rac_cand_list[:]
            temp_cand_list.remove(cand)
            rac_cand_list = temp_cand_list
            continue

    return rac_cand_list


def reduce_rbs_by_rank(rbs_in):
    rbs = deepcopy(rbs_in)
    result = []
    union_bm = rac_list_union_bitmap(rbs[0])
    for c in rbs[1]:
        if not bitmap_covered_by_bitmap(c.bitmap(), union_bm):
            result.append(c) 
    return result

def reduce_refined_by_size(rbs_in):
    rbs = deepcopy(rbs_in)
    remove = [[] for i in range(len(rbs))]
    for cand in rbs[0]:
        for idx in range(1,len(rbs)):
            for c in rbs[idx]:
                if bitmap_covered_by_bitmap(c.bitmap(), cand.bitmap()):
                    remove[idx].append(c)

    for idx in range(1,len(rbs)):
        for c in remove[idx]:
            if c in rbs[idx]:
                rbs[idx].remove(c)
    return rbs

# is bm1 "covered by" bm2
def bitmap_covered_by_bitmap(bm1, bm2):
    return (bm1 & bm2) == bm1

def union_list_bitmaps(bm_list):
    union_bm = bm_list[0]
    for bm in bm_list[1:]:
        union_bm |= bm
    return union_bm

def list_rac_list_union_bitmap(l_rac_list):
    union_bm = None
    for l in l_rac_list:
        for c in l:
            if union_bm == None:
                union_bm = c.bitmap()
            else:
                union_bm |= c.bitmap()
    return union_bm
    
def rac_list_union_bitmap(rac_list, debug=False):
    if len(rac_list) == 1:
        return rac_list[0].bitmap()

    union_bm = None
    for cand in rac_list:
        if union_bm == None:
            union_bm = cand.bitmap()
        else:
            union_bm |= cand.bitmap()

    return union_bm

#def create_rac_sub_cover_lists(ra_cand_list, target_bm=None):
#    if target_bm == None:
#        target_bm = rac_list_union_bitmap(ra_cand_list)
#    covers = []
#
#    for cand in ra_cand_list:
#        sub_cand_list = [c for c in ra_cand_list if c != cand]
#        
#        sub_cand_list_bm = rac_list_union_bitmap(sub_cand_list)
#        print "sub cand bm"
#        for c in sub_cand_list:
#            print c.points()
#        print "-"*30
#        print sub_cand_list_bm.bin
#        print "target"
#        print target_bm.bin
#        if bitmap_is_contained(target_bm, sub_cand_list_bm):
#            print "TRUE!!!!!!!!!!!!!!!!!!!!"
#        print ((target_bm & sub_cand_list_bm) ^ target_bm).bin
#        print ")"*40
#
#
#
#        if bitmap_is_contained(target_bm, sub_cand_list_bm):
#            covers.append(sub_cand_list)
#
#    print "len covers", len(covers)
#    return covers

def look_for_single_cover(rac_list, target_bm):
    for cand in rac_list:
        if target_bm & cand.bitmap() == target_bm:
            return cand
    return None

#def find_minimum_cover_for_ra_cand_list(rac_list, debug, target_bm=None):
#
#    print "&"*50
#    nr_attrs = len(rac_list[0].attrs)
#    noneBm = BitArray('0b'+'0'*2**nr_attrs)
#
#    if target_bm != None:
#        print "target_bm" 
#        target_bm.bin
#    
#    if target_bm == None:
#        print "$"*50
#        target_bm = rac_list_union_bitmap(rac_list)
#        for c in rac_list:
#            print c.bitmap().bin
#            print c.points()
#        print ">"*50
#
#    cover_lists = []
#    seed_list = rac_list
#    cover_lists = create_rac_sub_cover_lists(seed_list, target_bm)
#    #siphon one off
#    while len(cover_lists) > 0:
#        seed_list = cover_lists[0]
#        cover_lists = create_rac_sub_cover_lists(seed_list, target_bm)
#    for c in seed_list:
#        print c.points()
#    return seed_list

def create_fd_list_from_rac_list_list(rac_lists):
    fd_list = []
    for l in rac_lists:
        fd_list.extend(create_fd_list_from_rac_list(l))
    return fd_list


def create_fd_list_from_rac_list(rac_list):
    fd_list = []
    for cand in rac_list:
        fd_list.append(create_fd_from_rac(cand))

    return fd_list

def get_attributes_for_number(num, attrs):
    letters = []
    for i in range(len(attrs)):
        idx = 2**i
        if idx & num:
            letters.append(attrs[i])
        else:
            letters.append('~'+attrs[i])
    return letters

def create_fd_from_rac(cand):
    given_attrs = []
    implied_attr = None
    attrs = cand.attrs
    pos_pat = cand.positivePattern
    neg_pat = cand.negativePattern

    for i in range(len(attrs)):
        idx = 2**i
        if pos_pat & idx:
            given_attrs.append(attrs[i])
    for i in range(len(attrs)):
        idx = 2**i
        if neg_pat & idx:
            implied_attr = attrs[i]
            break
    fd = FunctionalDependency(given_attrs, implied_attr, attrs)
    fd.setBitmap(cand.bitmap())
    return fd

def print_bitmap_points(bm, msg=None):
    counts = []
    for i in range(len(bm)):
        if bm[i] == 1:
            counts.append(i)
    if msg != None:
        print msg
    print counts

def invert_bitmap(bm):
    result = bm.copy()
    for i in range(len(bm)):
        result[i] ^= 1
    return result
        
# return number of 1's in bitmap
# check if BitArray has support for this
def bitmap_count(bm):
    cnt = 0
    for i in range(len(bm)):
        cnt += bm[i]
    return cnt

def subtract_bm_from_bm(bm1, bm2):
    inv_bm1 = invert_bitmap(bm1)
    return inv_bm1 & bm2

# is bitmap bm1 contained in bitmap bm2
def bitmap_is_contained(bm1, bm2):
    intersect = bm1 & bm2
    return bm1 == intersect & bm1

def create_sub_cover_map_lists(bm_list):
    full_union_bm = union_list_bitmaps(bm_list)
    covers = []
    print "len(bm_list):", len(bm_list)
    for bm in bm_list:
        sub_bm_list = [b for b in bm_list if b!=bm]
        print "len(sub_bm_list):", len(sub_bm_list)
        sub_bm_list_bm = union_list_bitmaps(sub_bm_list)
        
        if bitmap_is_contained(full_union_bm, sub_bm_list_bm):
            covers.append(sub_bm_list)

    return covers

        

