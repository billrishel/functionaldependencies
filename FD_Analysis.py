from build_bitmaps import *
from fd_util import *
from FD import *
from collections import defaultdict
from bitmap_util import *
from copy import deepcopy

class FDCandidate:

    Id_count = 0

    def __init__(self,points, pos_pat, neg_pat, attributes):
        self.id = FDCandidate.Id_count
        FDCandidate.Id_count += 1
        self.givenAttrs_ = None
        self.impliedAttr_ = None
        self.positivePattern = pos_pat
        self.negativePattern = neg_pat
        self.bitmap_ = create_bitmap_from_points_list(points,len(attributes))
        self.bitmap_copy = self.bitmap_.copy()
        self.points_ = points
        self.attrs = attributes
        self.essential = False
        self.benefitBitmap_ = None
        self.noneBm_ = none_bitmap(len(self.attrs))
    
    def noneBm(self):
        return self.noneBm_.copy()

    def order(self):
        ord = 0
        num_pts = len(self.points())
        while num_pts > 1:
            ord += 1
            num_pts /= 2
        return ord

    def givenAttrs(self):
        mask = 0
        # mask of numAttrs bits, all 1's 
        for k in range(len(self.attrs)):
            mask |= 1<<k
        for p in self.points():
            mask &= p
        given_attrs = []
        for i in range(len(self.attrs)):
            if 2**i & mask:
                given_attrs.append(self.attrs[i])
        return given_attrs

    def impliedAttr(self):
        mask = 0
        mask2 = 0
        # mask of numAttrs bits, all 1's 
        for k in range(len(self.attrs)):
            mask2 |= 1<<k
        for p in self.points():
            mask |= p
        mask2 ^= mask
        for i in range(len(self.attrs)):
            if 2**i & mask2:
                return self.attrs[i]
        return None

    def fdAttrs(self):
        return [self.givenAttrs(), self.impliedAttr()]

    def points(self):
        return self.points_[:]

    def bitmap(self):
        return self.bitmap_.copy()
                    
    def reset(self):
        self.benefitBitmap_ = self.noneBm()

    def benefitBitmap(self, needed_bm):
        return self.bitmap() & needed_bm

    # how many benefit bits...
    def benefitCount(self, needed_bm):
        return bitmap_count(self.bitmap() & needed_bm)

    def test(self):
        if self.bitmap_copy != self.bitmap():
            print "ERROR IN BITMAP MATCH!"
            exit()


##########################################################################
class FDCandidateList:

    Id_count = 0

    def __init__(self, fdc_list, attributes, global_union_bm, parent):

        self.id = FDCandidateList.Id_count
        FDCandidateList.Id_count +=1
        self.attributes_ = attributes[:]
        self.globalUnionBitmap_ = global_union_bm
        self.fdcList_ = fdc_list[:]
        self.parent_ = parent
        self.noneBm_ = None
        self.noneBm_ = none_bitmap(len(attributes))
            
        
        if parent != None:
            parent.setChild(self)

        self.child_ = None
        self.listBitmap_ = none_bitmap(len(attributes))
        for fdc in self.fdcList_:
            self.listBitmap_ |= fdc.bitmap()
        self.savedListBitmap_ = self.listBitmap_.copy()

    def noneBm(self):
        return self.noneBm_.copy()

    def setParent(self, parent):
        self.parent_= parent

    def reset(self):
        for fdc in self.fdcList():
            fdc.reset()

    def parent(self):
        return self.parent_
    
    def setChild(self, child):
        self.child_ = child

    def child(self):
        return self.child_

    def fdcList(self):
        return self.fdcList_[:]

    def setFdcList(self, fdcList):
        self.fdcList_ = fdcList[:]

    def listBitmap(self):
        return self.listBitmap_

    def validateListBitmap(self):
        for fdc in self.fdcList_:
            self.listBitmap_ |= fdc.bitmap()
        return self.listBitmap_ == self.savedListBitmap_

    def globalUnionBitmap(self):
        return self.globalUnionBitmap_
    
    def removeFdc(self, fdc):
        self.fdcList_.remove(fdc)

    def len(self):
        return len(self.fdcList_)

########################################################################
class FDCandidateListList:

    Id_count = 0

    def __init__(self, union_bm, num_attrs):
        self.last_ = None
        self.id = FDCandidateListList.Id_count
        FDCandidateListList.Id_count += 1
        self.globalUnionBitmap_ = union_bm.copy()
        self.noneBm_ = none_bitmap(num_attrs)

        self.fdcListList_ = []

    def noneBm(self):
        return self.noneBm_.copy()

    def addFdcList(self, fdcList):
        prev = self.last()
        self.fdcListList_.append(fdcList)
        self.last_ = fdcList

    def fdcListList(self):
        return self.fdcListList_[:]

    def removeFdcList(self, fdcList):
        if fdcList in self.fdcListList_:
            self.fdcListList_.remove(fdcList)

    def globalUnionBitmap(self):
        return self.globalUnionBitmap_.copy()

    def check(self):
        print "CHECK ", "*"*80
        current = self.first()
        while current != None:
            print current.id, len(current.fdcList())
            current = current.child()
        print "==================="
        for fdcList in self.fdcListList():
            print fdcList.id, fdcList.len()
        print "len list list", self.len()

    # assume current != None
    # actually, find non-zero or None child
    def clean_findNonZeroChild(self, current):
        child = current.child()
        while child != None and child.len() == 0:
            child = child.child()
        return child

    def allPriorFdcs(self, current):
        prior_fdcs = []
        fdCandList = self.first()
        while fdCandList != current:
            if fdCandList == None:
                return prior_fdcs
            prior_fdcs.extend(fdCandList.fdcList())
            fdCandList = fdCandList.child()
        return prior_fdcs
        
    # what is needed at this level?
    def neededBitmap(self, current):
        prior_fdcs = self.allPriorFdcs(current)
        prior_fdcs_bm = rac_list_union_bitmap(prior_fdcs)
        return subtract_bm_from_bm(prior_fdcs_bm, self.globalUnionBitmap())

    def clean(self):
        current = self.first()
        while current != None:
            if current.child() == None:
                break
            else:
                child = self.clean_findNonZeroChild(current)
                
                current.setChild(child)
                if child != None:
                    child.setParent(current)
            current = current.child()
        # we've fixed up the references, now 
        # delete zero len fdcList's from list
        remove_list = []
        for fdcList in self.fdcListList_:
            if fdcList.len() == 0:
                remove_list.append(fdcList)
                
        for fdcList in remove_list:
            self.fdcListList_.remove(fdcList)

    def validate(self):
        assert self.fdcListList_[0].parent() == None
        current = self.fdcListList_[0]
        while current.child() != None:
            assert current.child().parent() != None
            current = current.child()
        assert current == self.last()

        current = self.last()
        while current.parent() != None:
            current = current.parent()
        assert current == self.fdcListList_[0]
        # add check on clean method that fdcListList_
        # as same fdcList's as through first(), child() etc.

    def last(self):
        return self.last_

    def first(self):
        return self.fdcListList_[0]

    def len(self):
        return len(self.fdcListList_)
    
    def printListLens(self):
        print "list lens"
        current = self.first()
        while current != None:
            print current.len(),
            current = current.child()
        print

    def combineAndReduce(self):
        combined = []
        for l in self.fdcListList():
            combined.extend(l.fdcList())
        
        return reduce_for_size(combined)

    def createFdList(self):
        reduced = self.combineAndReduce()
        reduced_bm = rac_list_union_bitmap(reduced)

        if reduced_bm != self.globalUnionBitmap():
            print "ERROR, global match failed"
            exit()
        
        return create_fd_list_from_rac_list(reduced)

    # find any single fdc's that cover needed_bm
    def findIdeals(self, fdc_list, needed_bm):
        ideals = []
        for fdc in fdc_list:
            if bitmap_covered_by_bitmap(needed_bm, fdc.bitmap()):
                ideals.append(fdc)
        return ideals

    # find fdc's that contribute to needed_bm
    def contributors(self, fdc_list, needed_bm):
        contributors = []
        for fdc in fdc_list:
            if fdc.bitmap() & needed_bm != self.noneBm():
                contributors.append(fdc)
        return contributors

    # find fdc's that contribute to needed_bm
    def findHelpful(self, fdc_list, needed_bm):
        helpful = []
        for fdc in fdc_list:
            if fdc.bitmap() & needed_bm != self.noneBm():
                helpful.append(fdc)
        return helpful

    def orderByBenefit(self, fdc_list, needed_bm):

        return True

    def mostBeneficial(self, fdc_list, needed_bm):

        # are all equally beneficial?
        max_ben = 0
        for fdc in fdc_list:
            max_ben = max(max_ben, fdc.benefitCount(needed_bm))
        most_beneficial = []
        for fdc in fdc_list:
            if fdc.benefitCount(needed_bm) == max_ben:
                most_beneficial.append(fdc)

        if len(most_beneficial) == len(fdc_list):
            return []
        else:
            return most_beneficial


    def removeNonEssential(self, fdc_list, needed_bm):
        fdc_list_bm = rac_list_union_bitmap(fdc_list)

        essential = []
        not_essential = []
        for fdc in fdc_list:
            sub_list = [f for f in fdc_list if f != fdc]
            sub_list_bm = rac_list_union_bitmap(sub_list)
            new_needed_bm = subtract_bm_from_bm(sub_list_bm, needed_bm)
            if new_needed_bm == self.noneBm():
                not_essential.append(fdc)
                continue
            else:
                continue
        if len(not_essential) < len(fdc_list):
            essential = fdc_list[:]
            for r in not_essential:
                essential.remove(r)
            return essential
        else:
            return []


    def essentialAndHelpful(self, fdc_list, needed_bm):
        fdc_list_bm = rac_list_union_bitmap(fdc_list)

        helpful = self.findHelpful( fdc_list, needed_bm)
        if len(helpful) == len(fdc_list):
            #all are helpful
            # are all equally beneficial?
            max_ben = 0
            for fdc in fdc_list:
                max_ben = max(max_ben, fdc.benefitCount(needed_bm))
            helpful = fdc_list[:]
            for fdc in helpful:
                if fdc.benefitCount(needed_bm) < max_ben:
                    helpful.remove(fdc)
            #check if still OK
            helpful_bm = rac_list_union_bitmap(helpful)
            if helpful_bm & fdc_list_bm == fdc_list_bm:
                # okay, didn't lose anything
                fdc_list = helpful[:]


        print needed_bm.bin
        print
        for fdc in fdc_list:
            print fdc.bitmap().bin


        not_needed = []
        for fdc in fdc_list:
            sub_list = [f for f in fdc_list if f != fdc]
            sub_list_bm = rac_list_union_bitmap(sub_list)
            new_needed_bm = subtract_bm_from_bm(sub_list_bm, needed_bm)
            if new_needed_bm == self.noneBm():
                not_needed.append(fdc)
                continue
            else:
                continue
        essential = fdc_list[:]
        print "len", len(not_needed)
        print "len essential", len(essential)
        for r in not_needed:
            essential.remove(r)

        essential_bm = rac_list_union_bitmap(essential)

        new_needed_bm = subtract_bm_from_bm(essential_bm, needed_bm)

        sub_list = fdc_list[:]
        for f in set(essential):
            sub_list.remove(f)

        helpful = self.findHelpful( sub_list, new_needed_bm)

        return (essential, helpful)

    ##############################################################
    def distill(self):
        print "distill"

        if len(self.fdcListList()) < 2:
            return

        print "lens before distill"
        self.printListLens()

        parent = self.first()
        current = parent.child()

        while current != None:
            print "<"*80

            self.printListLens()
            current.reset()
            needed_bm = self.neededBitmap(current)
            orig_needed_bm = needed_bm.copy()
            fdc_list = current.fdcList()
            print "current len", current.len()
            
            fdc_list_bm = rac_list_union_bitmap(fdc_list)
            print fdc_list_bm.bin
            print needed_bm.bin
            # no benefit at this level
            best_we_can_do_bm = subtract_bm_from_bm(fdc_list_bm, needed_bm)
            print "best_we_can_do_bm"
            print best_we_can_do_bm.bin
            if best_we_can_do_bm == needed_bm:
                print "no benefit at this level, continue to next level"
                self.printListLens()
                current.setFdcList([])
                parent = current
                current = parent.child()
                continue
            solution_parts = []
            essential = self.removeNonEssential(fdc_list, needed_bm[:])
            if len(essential) > 0:
                essential_bm = rac_list_union_bitmap(essential)
                if subtract_bm_from_bm(essential_bm, needed_bm) == \
                        best_we_can_do_bm:
                    print "we're done"
                    # is essential really ALL essential?
                    print "len essential", len(essential)
                    current.setFdcList(essential)

                    parent = current
                    current = parent.child()
                    continue

                solution_parts.append(essential)
                print "essential bm"
                print essential_bm.bin
                needed_bm = subtract_bm_from_bm(essential_bm, needed_bm)
                print "needed"
                print needed_bm.bin
                print "."*80

            else:
                print "removeNonEssential did not help"

            remainder = []
            if len(essential) > 0:
                for fdc in fdc_list:
                    if not fdc in essential:
                        remainder.append(fdc)
            else:
                remainder = fdc_list[:]


            print "len essential", len(essential)
            print "len remainder", len(remainder)

            print needed_bm.bin
            print self.neededBitmap(current).bin
            contributors = self.contributors(remainder, needed_bm)
            if len(contributors) == 0:
                print "we're done at this level"
                print "no more we can do"
                print "len essential", len(essential)
                current.setFdcList(essential)

                parent = current
                current = parent.child()
                continue

            print "len contributors", len(contributors)
            contributors_bm = rac_list_union_bitmap(contributors)

            # solution is essential list plus contributors
            if len(contributors) < len(remainder):
                print "contributors() helped"

            most_beneficial = self.mostBeneficial(contributors, needed_bm)
            print "len most beneficial", len(most_beneficial)

            if len(most_beneficial) > 0:
                most_beneficial_bm = rac_list_union_bitmap(most_beneficial)
                if subtract_bm_from_bm(most_beneficial_bm, needed_bm) == \
                   best_we_can_do_bm:
                    fdc_list = most_beneficial[:]
            
            ideals = self.findIdeals(fdc_list, needed_bm)
            print "len ideals", len(ideals)
            
            if len(ideals) == 1:
                print "one ideal"
                solution_parts.append([ideals[0]])
            elif len(ideals) > 0:
                solution_parts.append([ideals[0]])
                print "hmmmmmmmmmmmmmmm"
            else:
                # did not refine contributors!!!!!!!!!!!!!!!!!!!
                solution_parts.append(fdc_list)

            print "len fdc_list", len(fdc_list)
            solution = []
            for part in solution_parts:
                solution.extend(part)
            current.setFdcList(solution)

            parent = current
            current = parent.child()

        print "lens after distill"
        self.printListLens()

    def removeOvershadowedFdcs(self):
        if len(self.fdcListList()) < 2:
            return
        print "before remove overshadowed"
        self.printListLens()

        current = self.last()
        parent = current.parent()

        while parent != None:

            overshadow_bm = parent.listBitmap()

            remove_list = []
            for fdc in current.fdcList():
                if bitmap_covered_by_bitmap(fdc.bitmap(), \
                                            overshadow_bm):
                    remove_list.append(fdc)
            for fdc in remove_list:
                current.removeFdc(fdc)
            current = parent
            parent = current.parent()

        self.clean()       

        print "after remove overshadowed"
        self.printListLens()

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
        print len(fd_list)
        fd_list_bms = []
        for fd in fd_list:
            fd_list_bms.append(fd.getBitmap())
        fd_plus_list = self.getFdPlusList(fd_list)
        found_list = []
        for f in fd_list:
            found = False
            for fd in fd_plus_list:
                if fd.getBitmap() == f.getBitmap():
                    found = True
            if not found:
                found_list.append(fd)
        print "len found list", len(found_list)

        fd_list.append(found_list[0])
        for fd in fd_plus_list:
            fd.Print()


        print len(fd_list)
        print "#"*90

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

        self.printFds()
        print

        print "FD Optimum Minimum Covers"
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

