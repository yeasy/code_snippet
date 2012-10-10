#include <linux/sockios.h>

#include <stdio.h>
#include <sys/types.h>
#include <net/if.h>
#include <netinet/in.h>
#include <sys/socket.h>
#include <sys/ioctl.h>
#include <arpa/inet.h>

int main(void)
{
    char *eth="eth0:d";
    char *ipaddr = malloc(20);
    int sock_fd;
    struct  sockaddr_in my_addr;
    struct ifreq ifr;

    /* Get socket file descriptor */
    if ((sock_fd = socket(PF_INET, SOCK_DGRAM, 0)) == -1) {
        perror("socket");
        return -1;
    }

    /* Get IP Address */
    strncpy(ifr.ifr_name, eth, IF_NAMESIZE);
    ifr.ifr_name[IFNAMSIZ-1]='\0';

    if (ioctl(sock_fd, SIOCGIFADDR, &ifr) < 0) {
        printf(":No Such Device %s\n",eth);
        return -1;
    }

    memcpy(&my_addr, &ifr.ifr_addr, sizeof(my_addr));
    strcpy(ipaddr, inet_ntoa(my_addr.sin_addr));
    printf("%s\n",ipaddr);
    free(ipaddr);
    close(sock_fd);
    return 0;
}
