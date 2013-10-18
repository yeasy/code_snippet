__author__ = 'baohua'

import math

class Cutter():
    """
    The Convertor class.

    >>> t=Cutter(0,1)
    >>> t=Cutter(0,-1)
    Invalid input! min=0, max=-1
    >>> t=Cutter(-1,1)
    Invalid input! min=-1, max=1
    """
    def __init__(self, min=0,max=0):
        if min > max or min<0 or max<0:
            print "Invalid input! min=%d, max=%d" %(min,max)
        else:
            self.min,max = min,max

    def genCuttedPrefix(self,prefixes):
        """
        Given two prefixes, calculate the resulted cutted prefixes

        >>> Cutter().genCuttedPrefix(['10.0.0.0/8','10.1.0.0/24'])
        ['10.0.0.0/16', '10.1.0.0/24', '10.1.1.0/24', '10.1.2.0/23', '10.1.4.0/22', '10.1.8.0/21', '10.1.16.0/20', '10.1.32.0/19', '10.1.64.0/18', '10.1.128.0/17', '10.2.0.0/15', '10.4.0.0/14', '10.8.0.0/13', '10.16.0.0/12', '10.32.0.0/11', '10.64.0.0/10', '10.128.0.0/9']
        """
        range_list=self.cutPrefixToRange(prefixes)
        result=[]
        if range_list:
            for range in range_list:
                result.extend(self.getPrefixFromRange(range[0],range[1]))
        return result


    def cutPrefixToRange(self,prefixes):
        """
        Given two prefixes, calculate the range cutted

        >>> Cutter().cutPrefixToRange(['10.0.0.0/8','10.1.0.0/24'])
        [(167772160, 167837695), (167837696, 167837951), (167837952, 184549375)]
        """
        if len(prefixes)!=2:
            print "pls check the input prefixes number ",len(prefixes)
            return None
        result=[]
        ip,ip_start,ip_end,mask,mask_len=['',''],[0,0],[0,0],[0,0],[0,0]
        for i in range(len(prefixes)):
            ip[i],mask_len[i] = prefixes[i].split('/')
            ip[i],mask_len[i] = self.ipToInt(ip[i]),int(mask_len[i])
            if mask_len[i]!=32:
                mask[i] = (1<<(32-mask_len[i]))-1
                ip_start[i]=ip[i]&(~mask[i])
                ip_end[i]=ip[i]|mask[i]
            else:
                ip_start[i],ip_end[i]=ip[i],ip[i]
            #print self.intToIP(ip_start[i]),self.intToIP(ip_end[i])
        if ip_start[0]>ip_start[1]:
            ip_start[0],ip_start[1] = ip_start[1],ip_start[0]
            ip_end[0],ip_end[1] = ip_end[1],ip_end[0]
        if ip_end[0]<ip_start[1]:
            result.append((ip_start[0],ip_end[0]))
            result.append((ip_start[1],ip_end[1]))
        else:
            if(ip_start[1]>ip_start[0]):
                result.append((ip_start[0],ip_start[1]-1))
            result.append((ip_start[1],min(ip_end[0],ip_end[1])))
            if(ip_end[0]!=ip_end[1]):
                result.append((min(ip_end[0],ip_end[1])+1,max(ip_end[0],ip_end[1])))
        return result

    def ipToInt(self,ip):
        """
        Calculate the ip format string into number.

        >>> Cutter().ipToInt('10.0.0.2')
        167772162
        """
        ipseg = ip.split('.')
        assert len(ipseg)==4
        result=0
        for i in range(len(ipseg)):
            result<<=8
            result+=int(ipseg[i])
        return result

    def intToIP(self,value):
        """
        Calculate the ip format string with given number.

        >>> Cutter().intToIP(10*16777216+2)
        '10.0.0.2'
        """
        ip=[]
        for i in range(4):
            ip.insert(0,str(value&0xff))
            value>>=8
        return '.'.join(ip)



    def getPrefixFromRange(self,min,max):
        """
        Get numbers of prefix that can represent the range.

        >>> t= Cutter()
        >>> t.getPrefixFromRange(0,1)
        ['0.0.0.0/31']
        >>> t.getPrefixFromRange(0,7)
        ['0.0.0.0/29']
        >>> t.getPrefixFromRange(1,6)
        ['0.0.0.1/32', '0.0.0.2/31', '0.0.0.4/31', '0.0.0.6/32']
        >>> t.getPrefixFromRange(1,30)
        ['0.0.0.1/32', '0.0.0.2/31', '0.0.0.4/30', '0.0.0.8/29', '0.0.0.16/29', '0.0.0.24/30', '0.0.0.28/31', '0.0.0.30/32']
        """
        if min>max:
            return
        result_range,result_prefix=[],[]
        self.getPrefixFromRangeRun(min,max,result_range)
        for prefix_range in result_range:
            result_prefix.append(self.getPrefixString(prefix_range))
        return result_prefix

    def getPrefixString(self,prefix_range):
        min,max=prefix_range[0],prefix_range[1]
        assert self.isPrefixable(min,max)
        mask=min^max
        mask_len = 32-int(math.log(mask+1,2))
        return str(self.intToIP(min))+'/'+str(mask_len)

    def getPrefixFromRangeRun(self,min,max,result):
        if min==max:
            result.append((min,min))
            return
        if min&0x1:
            tryMax=min
        elif min==0: #margin is due to max
            tryMax = 2**(int(math.log(max+1, 2)))-1
        else: #margin is due to min
            len_min=self.getZeroSuffixLen(min)
            i = len_min
            tryMax = min|((1<<i) -1)
            while tryMax>max:
                tryMax = min|((1<<i) -1)
                i -= 1
        result.append((min,tryMax))
        if tryMax<max:
            self.getPrefixFromRangeRun(tryMax+1,max,result)

    def isPrefixable(self,min,max):
        """
        >>> Cutter().isPrefixable(0,1)
        True
        >>> Cutter().isPrefixable(1,2)
        False
        >>> Cutter().isPrefixable(4,5)
        True
        >>> Cutter().isPrefixable(0,2)
        False
        >>> Cutter().isPrefixable(8,11)
        True
        """
        if min<0 or max<min:
            return False
        if min==0 and self.getZeroSuffixLen(max-min+1)>0 or min==max:
            return True
        len_min = self.getZeroSuffixLen(min)
        len_differ = self.getZeroSuffixLen(max-min+1)
        return len_min >= len_differ and len_differ>0


    def isPowerofTwo(self,num):
        """
        >>> Cutter().isPowerofTwo(-1)
        False
        >>> Cutter().isPowerofTwo(0)
        False
        >>> Cutter().isPowerofTwo(1)
        True
        >>> Cutter().isPowerofTwo(2)
        True
        >>> Cutter().isPowerofTwo(3)
        False
        """
        return num > 0 and (not(num & (num - 1)))

    def getZeroSuffixLen(self,num):
        """
        The good suffix is defined as the '0' suffix string

        >>> Cutter().getZeroSuffixLen(0)
        1
        >>> Cutter().getZeroSuffixLen(1)
        0
        >>> Cutter().getZeroSuffixLen(4)
        2
        """
        tmp= num
        if tmp==0:
            return 1
        len=0
        for i in range(32):
            if tmp==0 or tmp&0x1: #last bit is 1 or the number is 0 already
                break
            else:
                len+=1
                tmp>>=1
        return len

if __name__ == '__main__':
    import doctest
    doctest.testmod()
    c= Cutter()
    print len(c.genCuttedPrefix(['10.0.0.0/8','10.0.0.1/32']))
    print c.genCuttedPrefix(['10.0.0.0/8','10.0.0.1/32'])
