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

        print "Processing FD definitions"
        print
        print "FD definitions in file", self.filename

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


