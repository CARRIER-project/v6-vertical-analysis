import random as rand
def createBSN():
    remainder = 10;
    while remainder > 9:
        bsn = [int(x) for x in list(str(rand.randint(0,99999999)+100000000)[-8:])]
        remainder = sum([x*y for x,y in zip(bsn,range(9,1,-1))])%11
    bsn.append(remainder)
    return ''.join(str(x) for x in bsn)

def getmanyBSNs(numSamples):
        return set([createBSN() for x in range(numSamples)])


allBSNs = set()
for i in range(12):
    x = set(getmanyBSNs(1700000))
    allBSNs = set.union(allBSNs,x)
    del x
    print i, len(allBSNs)

with open('BSNs.txt', 'wt') as file:
    for x in allBSNs:
        file.write(x+"\n")
        
