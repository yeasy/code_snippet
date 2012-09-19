/*
 *  This program is free software: you can redistribute it and/or modify
 *  it under the terms of the GNU General Public License as published by
 *  the Free Software Foundation, either version 3 of the License, or
 *  (at your option) any later version.
 */

#include <arpa/inet.h>
#include <linux/if_packet.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <net/if.h>
#include <netinet/ether.h>
#include <linux/ip.h>
#include <linux/udp.h>

#define DEST_MAC0	0x00
#define DEST_MAC1	0x11
#define DEST_MAC2	0x22
#define DEST_MAC3	0x33
#define DEST_MAC4	0x44
#define DEST_MAC5	0x55

#define DEFAULT_IF	"eth0"
#define BUF_SIZ		1024

/* this function generates header checksums */
unsigned short csum (unsigned short *buf, int nwords)
{
    unsigned long sum;
    for (sum = 0; nwords > 0; nwords--)
        sum += *buf++;
    sum = (sum >> 16) + (sum & 0xffff);
    sum += (sum >> 16);
    return ~sum;
}

int get_gw_ip(char *eth, char *ipaddr)
{
    int sock_fd;
    struct  sockaddr_in my_addr;
    struct ifreq ifr;

    /**//* Get socket file descriptor */
    if ((sock_fd = socket(PF_INET, SOCK_DGRAM, 0)) == -1) {
        perror("socket");
        return -1;
    }

    /**//* Get IP Address */
    strncpy(ifr.ifr_name, eth, IF_NAMESIZE);
    ifr.ifr_name[IFNAMSIZ-1]='\0';

    if (ioctl(sock_fd, SIOCGIFADDR, &ifr) < 0) {
        printf(":No Such Device %s\n",eth);
        return -1;
    }

    memcpy(&my_addr, &ifr.ifr_addr, sizeof(my_addr));
    strcpy(ipaddr, inet_ntoa(my_addr.sin_addr));
    close(sock_fd);
    return 0;
}

/**
 * main function.
 */
int main(int argc, char *argv[])
{
    int sockfd;
    struct ifreq if_idx;
    struct ifreq if_mac;
    int tx_len = 0;
    char sendbuf[BUF_SIZ];
    struct sockaddr_ll socket_address;
    char ifName[IFNAMSIZ];
    char ipaddr[20];


    /* Get interface name from input parameter */
    if (argc > 1)
        strcpy(ifName, argv[1]);
    else
        strcpy(ifName, DEFAULT_IF);

    /* Open RAW socket to send on */
    if ((sockfd = socket(AF_PACKET, SOCK_RAW, IPPROTO_RAW)) == -1) {
        perror("socket");
    }

    /* Get the index of the interface to send on */
    memset(&if_idx, 0, sizeof(struct ifreq));
    strncpy(if_idx.ifr_name, ifName, IFNAMSIZ-1);
    if (ioctl(sockfd, SIOCGIFINDEX, &if_idx) < 0)
        perror("SIOCGIFINDEX");
    /* Get the MAC address of the interface to send on */
    memset(&if_mac, 0, sizeof(struct ifreq));
    strncpy(if_mac.ifr_name, ifName, IFNAMSIZ-1);
    if (ioctl(sockfd, SIOCGIFHWADDR, &if_mac) < 0)
        perror("SIOCGIFHWADDR");

    memset(sendbuf, 0, BUF_SIZ);
    /* Construct the Ethernet header */
    struct ether_header *eh = (struct ether_header *) sendbuf;
    eh->ether_shost[0] = ((uint8_t *)&if_mac.ifr_hwaddr.sa_data)[0];
    eh->ether_shost[1] = ((uint8_t *)&if_mac.ifr_hwaddr.sa_data)[1];
    eh->ether_shost[2] = ((uint8_t *)&if_mac.ifr_hwaddr.sa_data)[2];
    eh->ether_shost[3] = ((uint8_t *)&if_mac.ifr_hwaddr.sa_data)[3];
    eh->ether_shost[4] = ((uint8_t *)&if_mac.ifr_hwaddr.sa_data)[4];
    eh->ether_shost[5] = ((uint8_t *)&if_mac.ifr_hwaddr.sa_data)[5];
    eh->ether_dhost[0] = DEST_MAC0;
    eh->ether_dhost[1] = DEST_MAC1;
    eh->ether_dhost[2] = DEST_MAC2;
    eh->ether_dhost[3] = DEST_MAC3;
    eh->ether_dhost[4] = DEST_MAC4;
    eh->ether_dhost[5] = DEST_MAC5;
    /* Ethertype field */
    eh->ether_type = htons(ETH_P_IP);
    tx_len += sizeof(struct ether_header);

    /* IP header field */
    get_gw_ip(ifName,ipaddr);
    struct iphdr *iph = (struct iphdr *) (sendbuf + sizeof(struct ether_header));
    iph->ihl=5;
    iph->version=4;
    iph->tos=0;
    iph->id = htonl(12345);
    iph->frag_off = 0;
    iph->ttl = 255;
    iph->protocol = IPPROTO_UDP;
    //iph->protocol = IPPROTO_ENCAP;
    //iph->protocol = IPPROTO_ETHERIP;
    iph->saddr=inet_addr(ipaddr);
    iph->daddr=inet_addr("10.0.0.2");
    iph->check=0; //csum here
    tx_len += sizeof(struct iphdr);

    /* UDP header*/
    struct udphdr *udph = (struct udphdr *) (sendbuf + sizeof(struct iphdr) + sizeof(struct ether_header));
    /* UDP Header */
    udph->source = htons(3423);
    udph->dest = htons(5342);
    udph->check = 0; // skip
    tx_len += sizeof(struct udphdr);

    /* Packet data */
    sendbuf[tx_len++] = 0xde;
    sendbuf[tx_len++] = 0xad;
    sendbuf[tx_len++] = 0xbe;
	sendbuf[tx_len++] = 0xef;

    /* Length of UDP payload and header */
    udph->len = htons(tx_len - sizeof(struct ether_header) - sizeof(struct iphdr));
    /* Length of IP payload and header */
    iph->tot_len = htons(tx_len - sizeof(struct ether_header));
    /* Calculate IP checksum on completed header */
    iph->check = csum((unsigned short *)(sendbuf+sizeof(struct ether_header)), sizeof(struct iphdr)>>1);

	/* Index of the network device */
	socket_address.sll_ifindex = if_idx.ifr_ifindex;
	/* Address length*/
	socket_address.sll_halen = ETH_ALEN;
	/* Destination MAC */
	socket_address.sll_addr[0] = DEST_MAC0;
	socket_address.sll_addr[1] = DEST_MAC1;
	socket_address.sll_addr[2] = DEST_MAC2;
	socket_address.sll_addr[3] = DEST_MAC3;
	socket_address.sll_addr[4] = DEST_MAC4;
	socket_address.sll_addr[5] = DEST_MAC5;

	/* Send packet */
	if (sendto(sockfd, sendbuf, tx_len, 0, (struct sockaddr*)&socket_address, sizeof(struct sockaddr_ll)) < 0)
	    printf("Send failed\n");

	return 0;
}
