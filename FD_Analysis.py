from build_bitmaps import *
from fd_util import *
from FD import *
from collections import defaultdict
from bitmap_util import *
from copy import deepcopy

##########################################################################
# read in set of FDs from file, generate 
# bitmaps, generate complete set of 
# minimum covers
class FDAnalysis:

    def __init__(self, filename):
        self.noneBm_ = None
        self.FDs = []
        self.attr_set = set()
        self.newAttrs_ = []
        self.impliedAttr = None
        self.points_ = []
        self.given = []
        self.fdData = []
        self.implied = []
        self.unionBitmap_ = None
        #strip off path
        self.filename = filename.split("\\")[-1]
        self.readFDsFromFile(filename)

    def points(self):
        return self.points_[:]

    def attrs(self):
        return self.newAttrs_[:]

    def numAttrs(self):
        return len(self.newAttrs_)

    def noneBm(self):
        return self.noneBm_.copy()

    def readFDsFromFile(self, filename):
        with open(filename) as f:
            lines = f.read().splitlines()
        self.parseFDStrings(lines)
        
    def parseFDStrings(self, strings):
        for s in strings:
            s = s.strip()
            if s == "":
                continue
            l_r = s.split("->")
            left = l_r[0]
            right = l_r[1]
            left = ''.join(left.split())
            right = ''.join(right.split())
            given = left.split(",")
            implied = right
            self.fdData.append([given,implied])
            self.addFd(given, implied)
        # All FD definition strings have been read in.
        # Now can create the bitmaps.
        self.setBitmaps()
        self.setUnionBitmap()

    def fdList(self):
        return list(self.FDs)[:]

    def addFd( self, given, implied ):
        self.FDs.append(FunctionalDependency(given,implied, self.attrs()))

    def createBitmaps(self, nrAttributes):
        build_bitmaps(self.given, self.implied, nrAttributes)

    # Print the FD defintion string with its id number
    # prepended.
    def printFd(self, fd):
        print fd.getId()," ",
        fd.Print()

    def printFds(self):
        fd_list = self.fdList()

        for f in fd_list:
            self.printFd(f)

    def printFdList(self, fd_list):
        for fd in fd_list:
            self.printFd(fd)

    def unionBitmap(self):
        return self.unionBitmap_.copy()

    def setUnionBitmap(self):
        self.unionBitmap_ = self.noneBm()
        for fd in self.fdList():
            self.unionBitmap_ |= fd.getBitmap()
        for i in range(len(self.unionBitmap_)):
            self.points_.append(i)

    def setBitmaps(self):
            
        # @!! change self.given to self.givenBm etc.
        # and fd.given to fd.givenAttributes
        for l in self.fdData:
            self.attr_set.update(l[0])
            self.attr_set.add(l[1])
        self.newAttrs_ = list(self.attr_set)
        self.newAttrs_.sort()
        self.noneBm_ = BitArray('0b'+'0'*2**len(self.newAttrs_))
        nrAttributes = len(self.newAttrs_)
        self.createBitmaps(nrAttributes)

        for fd in self.FDs:
            attr = fd.givenAttrs[0]
            idx = self.newAttrs_.index(attr)
            bm = self.given[idx].copy()
            for attr in fd.givenAttrs[1:]:
                idx = self.newAttrs_.index(attr)
                bm &= self.given[idx]
            attr = fd.impliedAttr
            idx = self.newAttrs_.index(attr)
            bm &= self.implied[idx]
            fd.setBitmap(bm)

        return
        
    def printExpressionForBitmap(self, bm):
        fd = self.fdList()[0]
        inv_attr_dict = fd.invAttrDict()
        given_expression = []
        implied_expression = []
        for i in range(len(self.given)):
            if (bm & self.given[i]) == self.given[i]:
                given_expression.append(inv_attr_dict[i])
            if (bm & self.implied[i]) == self.implied[i]:
                given_expression.append("~"+inv_attr_dict[i])
        print "   ",
        print " ^ ".join(given_expression)

    def generateCoversForGivenFdNumber(self, fd_number):
        fd = self.fdList()[fd_number]

        self.generateCoversForGivenFd(fd)

    # auxiliary method for studying a particular FD
    def generateCoversForGivenFd(self, fd):

        fd_list = self.fdList()

        min_covers = []

        sub_list = [f for f in fd_list if f!=fd]

        create_sub_covers_for_fd(fd, sub_list, min_covers)
        min_covers = eliminate_covers_lists_dups(min_covers)

        covers_bitmaps = []
        for c in min_covers:
            covers_bitmaps.append(union_fd_list_bitmaps(c))

        for b in covers_bitmaps:
            print bitmap_covered_by_bitmap(fd.getBitmap(),b)
            print "^"*20
            self.printExpressionForBitmap(b)

        if len(min_covers) != 0:
            print
            print "="*20
            self.printFd(fd)
            print "min covers = ", len(min_covers)
                
            for fl in min_covers:
                self.printFdList(fl)
                print "."*20

                for f in fl:
                    self.printExpressionForBitmap(f.getBitmap())
        return

    def generateCoversForAllFDs( self ):

        print "FD set:"
        self.printFds()
        fd_list = self.fdList()

        for fd in fd_list:
            self.generateCoversForGivenFd(fd)

    # for given set of FDs (read in from file)
    # generate the minimum subsets of FDs that
    # "cover" the entire set.
    def generateMinimumCovers( self ):

        print "Processing FD definitions in ", self.filename
        print
        print "Functional Dependencies"

        self.printFds()
        print
        
        fd_list = self.fdList()
        fd_list_bms = []
        for fd in fd_list:
            fd_list_bms.append(fd.getBitmap())

        covers_lists = create_sub_cover_lists(fd_list)

        minimum_covers = []

        while (True):
            select = []
            # Each list l in covers_lists is a cover.
            # 'covers' is a list of sublists of l
            # each with one less element than l and
            # that cover list l (if any).
            for l in covers_lists:
                covers = create_sub_cover_lists(l)
                if len(covers) != 0:
                    select.extend(covers)
                else:
                    # if no "sub covers" in list l
                    # then l is a minimum cover
                    minimum_covers.append(l)
            if select == []:
                break
            else:
                covers_lists = select

        if len(minimum_covers) > 0:
            # eliminate duplicates
            select = []
            select.append(minimum_covers[0])
            for l in minimum_covers[1:]:
                if not l in select:
                    select.append(l)

            minimum_covers = select
        else:
            minimum_covers = [fd_list]

        print "FD Minimum Covers"
        print
        for l in minimum_covers:
            for f in l:
                self.printFd(f)
            print
        
        return

    def buildPatternDict(self, fd_list):

        pattern_dict = defaultdict(list)

        for k in range(1,self.numAttrs()):
            for p in k_in_n(k, self.numAttrs()):
                pattern_dict[k].append(p)

        return pattern_dict

    def buildHitsDict(self):

        fd_list = self.fdList()

        pattern_dict = self.buildPatternDict(fd_list)

        points = set()
        hits_dict = defaultdict(list)
        for k in range(1,self.numAttrs()):
            for pat in pattern_dict[k]:
                temp_list = []
                for p in self.points():
                    # if point p fits pattern pat
                    if pat & p == pat:
                        temp_list.append(p)
                #hits_dict[k] has k-bit patterns of 1's
                if len(temp_list) >= 2**(self.numAttrs()-(k+1)):
                    hits_dict[k].append((pat,temp_list))
                    points.update(temp_list)
        return hits_dict
    
    def buildRefinedRACList(self):

        refined = []
        hits_dict = self.buildHitsDict()

        inv_pattern_list = []
        for k in range(self.numAttrs()):
            inv_pattern_list.append(2**k)
        #inv_pattern_list is a list of 
        #single bit patterns

        mask = 0
        # mask of numAttrs bits, all 1's 
        for k in range(self.numAttrs()):
            mask |= 1<<k

        points = set()
        for ky in hits_dict.keys():
            for pair in hits_dict[ky]:
                l = pair[1]
                pos_pat = pair[0]
                for neg_pat in inv_pattern_list:
                    tmp_list = []
                    for p in l:
                        # since neg_pat is negative, & it with
                        # the inverse of p (i.e. neg_pat is actually
                        # positive, but want the negative effect
                        if neg_pat & (p ^ mask) == neg_pat:
                            tmp_list.append(p)
                    if len(tmp_list) == 2**(self.numAttrs()-(ky+1)):
                        tmp_list_bm = create_bitmap_from_points_list(tmp_list, self.numAttrs())
                        if bitmap_covered_by_bitmap(tmp_list_bm,
                                                    self.unionBitmap()):
                            points.update(tmp_list)
                            rac = FDCandidate( \
                                    tmp_list,pos_pat,neg_pat, self.attrs())
                            refined.append(rac)
        points_bm = create_bitmap_from_points_list(list(points),self.numAttrs())
        return refined

    def buildRefinedBySizeList(self):

        refined = self.buildRefinedRACList()
        
        refined_bm = rac_list_union_bitmap(refined)

        refined_by_size = defaultdict(list)
        #sort refined by size of points lists
        for cand in refined:
            refined_by_size[len(cand.points())].append(cand)

        refined_keys = refined_by_size.keys()
        refined_keys.sort(reverse=True)

        rbs = [[] for i in range(len(refined_by_size.keys()))]
        for key in refined_keys:
            idx = refined_keys.index(key)
            rbs[idx].extend(refined_by_size[key])

        return rbs


    #######################################################################
    def reduceRefinedBySize(self, rbs):
#                if c.id in [6, 22, 2]:
#                    print "1:found", c.id

        while [] in rbs:
            rbs.remove([])

        fdcList_list = FDCandidateListList( self.unionBitmap(), self.numAttrs() )
        prev_list = None
        for i in range(len(rbs)):
            fdcList = FDCandidateList(rbs[i], self.attrs(), \
                        self.unionBitmap(), prev_list)
            fdcList_list.addFdcList(fdcList)

            prev_list = fdcList

        fdcList_list.validate()
        fdcList_list.removeOvershadowedFdcs()

        fdcList_list.distill()

        reduced = fdcList_list.combineAndReduce()
        for f in reduced:
            print f.id,
        print

        return fdcList_list.createFdList()
            
    
    #######################################################################
    def getFdPlusList(self, fd_list=None):

        if fd_list == None:
            fd_list = self.fdList()

        # I believe the rbs corresponds to the F+ list
        rbs = self.buildRefinedBySizeList()

        solution_fds = self.reduceRefinedBySize(rbs)
        return solution_fds

