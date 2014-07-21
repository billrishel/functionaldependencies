import string
import os
import sys
import optparse
import argparse
from config import *


    ##############  getInput  #############
def getInput():
    print "\n\t\tTYPE 'na' FOR NO ADJUST, 'nr' FOR NO REORDER, 'ro' FOR REORDER ONLY, 'ar' FOR ABS REORDER"
    testMode = raw_input()
    adjustMode = ADJUST
    if testMode == "na":
        adjustMode = NO_ADJUST
        print "no-adjust mode"
        
    elif testMode == "nr":
        adjustMode = NO_REORDER
        print "no-reorder mode"
    elif testMode == "ro":
        adjustMode = REORDER_ONLY
        print "reorder only mode"
    elif testMode == "ar":
        adjustMode = ABS_REORDER
        print "absolute reorder mode"
    else:
        print "full adjust mode"
    return adjustMode
    
###############################
parser = argparse.ArgumentParser()

parser.add_argument('-f', help='%(prog)')
args = parser.parse_args()

print "args:", args
print "name:", sys.argv[0]

