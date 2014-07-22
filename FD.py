from gen_util import *

# A functional dependency is a relationship between
# attributes of the form A1,..,Ak -> B where A1,...,Ak
# and B are attributes and indicates that for given 
# values of A1,...,Ak the value of B is *determine*
# [that is, the value of B *depends* on the values of
# A1,...,Ak]
# A1,...,Ak are the "given" attributes, B is the "implied"
# attribute
class FunctionalDependency:

    Attr_dict = {}
    Id_count = 1

    def __init__(self, given, implied, attributes=None):
        
        self.id = FunctionalDependency.Id_count
        FunctionalDependency.Id_count += 1
        tmp_list = given[:]
        tmp_list.append(implied)
        self.givenAttrs = given
        self.impliedAttr = implied
        for a in tmp_list:
            if not a in self.Attr_dict:
                self.Attr_dict[a] = len(self.Attr_dict.keys())

        self.given = set()
        for a in given:
            self.given.add(self.Attr_dict[a])

        self.implied = self.Attr_dict[implied]
        self.bitmap = None

    def getId(self):
        return self.id

    def invAttrDict(self):
        inv_dict = {v : k for k,v in self.Attr_dict.items()}
        return inv_dict;

    def givenAttrs():
        return self.given

    def impliedAttr():
        return self.implied

    def setBitmap(self, bm):
        self.bitmap = bm.copy()

    def getBitmap(self):
        return self.bitmap.copy()

    def getPoints(self):
        points = []
        for i in range(len(self.bitmap)):
            if self.bitmap[i] == 1:
                points.append(i)
        return points

    # AttrDict contains the original string
    # representations of the given and implied
    # attributes.
    def Print(self):
        inv_dict = self.invAttrDict()
        for x in list(self.given)[:-1]:
            print inv_dict[x],",",
        print inv_dict[list(self.given)[-1]],
        print "->",
        print inv_dict[self.implied]

