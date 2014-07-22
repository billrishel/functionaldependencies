from FD_Analysis import *

import argparse

parser = argparse.ArgumentParser()

parser.add_argument('-f', '--filename', '-a','--auto', help='%(prog)')
args = vars(parser.parse_args())

print "args[f]:", args['filename']

path = args['filename']

print "path:", path



FD_analysis = FDAnalysis(path)

#FD_analysis.expmt()

#FD_analysis.generateCoversForAllFDs()
#FD_analysis.generateCoversForGivenFdNumber(4)
print "=============================================="

FD_analysis.generateMinimumCovers()
#FD_analysis.getFdListPlus()
#FD_analysis.reverseAnalysis()




