from build_bitmaps import *

# generator to return integers of n bits
# with k "on" bits.
def k_in_n(k,n):
    if k == n:
        v = 0
        for i in range(n):
            v += 2**i
        yield v
    elif k == 1:
        for i in range(n):
            yield 1 << i
    elif n < 3:
        if k > 0:
            print "k:", k
            yield 1
            yield 2
    else:
        for x in k_in_n(k,n-1):
            yield x
        if k > 1:
            for x in k_in_n(k-1,n-1):
                w = 2**(n-1)
                yield x + w

# will return equal for lists that
# have same elements but not in the
# same order. For lists of lists the
# subordinate lists must still be in
# the same order.
def lists_equal(list_1, list_2):
    for l in list_1:
        if not l in list_2:
            return False
    for l in list_2:
        if not l in list_1:
            return False
    return True

# is bm1 "covered by" bm2
def bitmap_covered_by_bitmap(bm1, bm2):
    return (bm1 & bm2) == bm1

# return intersection bitmap for FDs in fd_list
def intersection_fd_list_bitmaps(fd_list):
    intersection_bm = fd_list[0].getBitmap()
    for fd in fd_list[1:]:
        intersection_bm &= fd.getBitmap()
    return intersection_bm

# return union bitmap for FDs in fd_list
def union_fd_list_bitmaps(fd_list):
    union_bm = fd_list[0].getBitmap()
    for fd in fd_list[1:]:
        union_bm |= fd.getBitmap()
    return union_bm

def numbers_for_fd_list(fd_list):
    nums = []
    for fd in fd_list:
        nums.append(fd.getId())
    return nums

def print_numbers_for_list_of_fd_lists(covers):
    for l in covers:
        print_numbers_for_fd_list(l)

def print_numbers_for_fd_list(fd_list):
    for f in fd_list:
        print f.getId(), " ",
    print

def print_fd_list(fd_list):
    for fd in fd_list:
        fd.Print()

def create_sub_covers_for_fd(fd, fd_list, min_covers):
    
    if ( len(fd_list) < 2):
        return

    if fd_list in min_covers:
        return

    fd_bm = fd.getBitmap()
    covers = []
    for f in fd_list:
        sub_fd_list = [fx for fx in fd_list if fx!=f]
        sub_fd_list_bm = union_fd_list_bitmaps(sub_fd_list)
        if bitmap_is_contained(fd_bm, sub_fd_list_bm):
            covers.append(sub_fd_list)

    if (len(covers)==0):
        if not fd_list in min_covers:
            fd_list_bm = union_fd_list_bitmaps(fd_list)
            if bitmap_is_contained(fd_bm, fd_list_bm):
                min_covers.append(fd_list)
        return
    else:
        covers = eliminate_covers_lists_dups(covers)
        for l in covers:
            create_sub_covers_for_fd(fd, l, min_covers)


# fd_list is assumed to be a "cover" list.
# If fd_list has N items, then there are 
# N subsets of fd_list obtained by removing a
# single item from fd_list. For each of the
# N subsets so obtained, determine if the subset
# itself covers the entirety of fd_list. This
# function returns all such subsets that cover
# fd_list.
def create_sub_cover_lists(fd_list):
    full_union_bm = union_fd_list_bitmaps(fd_list)
    covers = []
    for fd in fd_list:
        sub_fd_list = [f for f in fd_list if f!=fd]
        sub_fd_list_bm = union_fd_list_bitmaps(sub_fd_list)
        
        if bitmap_covered_by_bitmap(full_union_bm, sub_fd_list_bm):
            covers.append(sub_fd_list)

    return covers


def eliminate_covers_lists_dups(covers_lists):
    # eliminate duplicates
    if len(covers_lists) == 0:
        return []
    select = []
    select.append(covers_lists[0])
    for l in covers_lists[1:]:
        if not l in select:
            select.append(l)

    return select




