#!/usr/bin/python
"""
Test to implement several efficient functions with bit operations.

Run the script by 
    python alg_bit_op.py
If no outputs, it means all tests are passed.
"""

def setRightestBit(n):
    """
    Set the rightest bit 1 of the number to 0.
    This can be utlized to test if a number is 2-power.
    @param n: The num.
    @return: The set result.

    >>> [setRightestBit(n) for n in range(5)]
    [0, 0, 0, 2, 0]
    """
    return n&(n-1)

def isolateRightPart(n):
    """
    Isolate the right part (starting from bit 1) in the number.
    @param n: The num.
    @return: The set result.

    >>> [isolateRightPart(n) for n in range(5)]
    [0, 1, 2, 1, 4]
    """
    return n&(-1*n)


if __name__ == "__main__":
    import doctest
    doctest.testmod()
