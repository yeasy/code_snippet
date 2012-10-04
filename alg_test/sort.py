#!/usr/bin/python
""" Sort algorithm testing. 
    Sort in incremental order.
    """

import random

def genSeq(num=1000):
    """ Generate a random sequence for test.
    @num: The number of elements
    @return: The generated result
    """
    t = range(num)
    random.shuffle(t)
    return t

def validate(L):
    """Validate if the list is sorted correctly.
    @L: List to validate
    @return: True or False
    """
    for i in range(len(L)-1):
        if L[i] > L[i+1]:
            return False
    return True

#InsertSort
def insertSort(L):
    """ Insert Sorting.
    @L: The list to sort
    @return: The sorted result
    """
    for i in range(len(L)-1): #[0,i] is sorted,[i+1,n] is unsorted
        j = i
        while j>=0 and L[j] > L[i+1]:
            L[j+1] = L[j]
            j -= 1
        L [j+1] = L[i+1]
    return L

#BubbleSort
def bubbleSort(L):
    """ bubble Sorting.
    @L: The list to sort
    @return: The sorted result
    """
    for i in range(len(L)-1):
        for j in range(len(L)-1-i):
            if L[j+1] < L[j]:
                L[j+1],L[j] = L[j],L[j+1]
    return L

#QuickSort
def quickSort_partition(L,i,j):
    """ Get the partition value in quickSort.
    @L: List to sort
    @i: Start position
    @j: End position
    @return: Pivot position
    """
    pivot = L[i] #use value in L[i] as the pivot
    while i<j:
        while i<j and L[j] >= pivot: j -= 1 #find L[j] < pivot
        L[i] = L[j]                         #L[j] is temp, candidate for pivot
        while i<j and L[i] <= pivot: i += 1 #find L[i] > pivot
        L[j] = L[i]                         #L[i] is temp, candidate for pivot
    L[i] = pivot
    return i

def quickSort_sub(L,i,j):
    """ Quick Sorting between i and j.
    @L: The list to sort
    @i: The start position
    @j: The end position
    """
    if i<j:
        p = quickSort_partition(L,i,j)
        quickSort_sub(L,i,p-1)
        quickSort_sub(L,p+1,j)

def quickSort(L):
    """ Quick Sorting.
    @L: The list to sort
    @return: Sorted result
    """
    quickSort_sub(L,0,len(L)-1)
    return L

#RadixSort
def radixSort_getKeyValue(e,i):
    """ Get e's value on i-th position. 
        i start at lower key.
    @e: Element to get the key
    @i: Key position to get
    @return: Value on i-th position
    """
    if e < 10**i:
        return 0
    e %= 10**(i+1)
    e /= 10**i
    return e

def radixSort_Key(L,i):
    """ Radix Sorting on the i-th key.
    @L: List to sort
    @i: Key position to sort
    @return: Sorted result
    """
    key_bucket = {}
    for j in range(10):
        key_bucket[j] = []
    for e in L:
        key_bucket[radixSort_getKeyValue(e,i)].append(e)
    T = []
    for j in range(10):
        T.extend(key_bucket[j])
    for i in range(len(L)):
        L[i] = T[i]

def radixSort(L):
    """ Radix Sorting.
    @L: The list to sort
    @return: The sorted result
    """
    max = L[0]
    for i in range(len(L)):
        if max < L[i]:
            max = L[i]
    Keynum = 100
    for i in range(Keynum):
        radixSort_Key(L,i)
    return L

#The main function starts here.
if __name__ == "__main__":
    alg = ['insertSort',
           'bubbleSort',
           'quickSort',
           'radixSort']

    for a in alg:
        if validate(eval(a+"(genSeq())")):
            print "%s Pass." %a
        else:
            print "%s Error." %a
    print quickSort([5,1,2,3,4,5,6,7])
