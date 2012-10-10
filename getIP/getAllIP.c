#include <stdio.h>
#include <sys/types.h>
#include <net/if.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <linux/sockios.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>

int main(void)
{
    int s;
    struct ifconf conf;
    struct ifreq *ifr;
    char buff[BUFSIZ];
    int num;
    int i;

    s = socket(PF_INET, SOCK_DGRAM, 0);
    conf.ifc_len = BUFSIZ;
    conf.ifc_buf = buff;

    ioctl(s, SIOCGIFCONF, &conf);
    num = conf.ifc_len / sizeof(struct ifreq);
    ifr = conf.ifc_req;

    for(i=0;i < num;i++)
    {
        struct sockaddr_in *sin = (struct sockaddr_in *)(&ifr->ifr_addr);

        ioctl(s, SIOCGIFFLAGS, ifr);
        if(((ifr->ifr_flags & IFF_LOOPBACK) == 0) && (ifr->ifr_flags & IFF_UP))
        {
            printf("%s (%s)\n",
                    ifr->ifr_name,
                    inet_ntoa(sin->sin_addr));
        }
        ifr++;
    }
}
