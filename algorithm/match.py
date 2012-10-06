#!/usr/bin/python
""" 
Pattern matching algorithm testing. 
"""

def kmpGetNext(P):
    """ Generate the overlap function/next array with the given pattern.
    @P: Matching pattern
    @return: Next array
    """
    n,i,j =[-1 for j in range(len(P))],0,-1
    while i < len(P):
        while j>=0 and P[i]!=P[j]:
            j = n[j]
        i+=1
        j+=1
        n[i] = j
        

def BF(P,T):
    """ Brute force searching.
    @P: Pattern
    @T: Text to examine
    """
    collector = []
    for i in range(len(T)):
        for j in range(len(P)):
            if T[i+j] != P[j]:
                break
        if j == len(P)-1 and T[i+j] == P[j]: #matching
            #print P,"match",T[i:]
            collector.append(T[i:])
    return collector

def kmpSearch(P,T):
    """ KMP searching.
    @P: Pattern
    @T: Text to examine
    """
    n = kmpGetNext(P) #generate the next array
    collector = []
    for i in range(len(T)):
        j = 0
        while j < len(P):
            if T[i+j] != P[j]:
                j = n[j]
        i += 1
        j += 1
        if j == len(P):
            collector.append(T[i-j:])
            print T[i-j:]
    return collector

def validate(alg,P,T):
    """Validate if the list is sorted correctly.
    @L: List to validate
    @return: True or False
    """
    if eval(alg+'(P,T)') == BF(P,T):
        return True
    else:
        return False

#The main function starts here.
if __name__ == "__main__":
    P = "abc"
    T = "abcdabcabd"
    print "Brute Force searching"
    print BF(P,T)
    #print "KMP searching"
    #print kmpSearch(P,T)
    print validate('BF',P,T)

