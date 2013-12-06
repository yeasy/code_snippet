#include <ctype.h>
#include "headers.h"
#include <pcap.h>
/*
 * print packet payload data (avoid printing binary data)
 */
void print_payload(const u_char *payload, int len) {

    int len_rem = len;
    int line_width = 16;			/* number of bytes per line */
    int line_len;
    int offset = 0;					/* zero-based offset counter */
    const u_char *ch = payload;

    if (len <= 0)
        return;

    /* data fits on one line */
    if (len <= line_width) {
        print_hex_ascii_line(ch, len, offset);
        return;
    }

    /* data spans multiple lines */
    for ( ;; ) {
        /* compute current line length */
        line_len = line_width % len_rem;
        /* print line */
        print_hex_ascii_line(ch, line_len, offset);
        /* compute total remaining */
        len_rem = len_rem - line_len;
        /* shift pointer to remaining bytes to print */
        ch = ch + line_len;
        /* add offset */
        offset = offset + line_width;
        /* check if we have line width chars or less */
        if (len_rem <= line_width) {
            /* print last line and get out */
            print_hex_ascii_line(ch, len_rem, offset);
            break;
        }
    }

    return;
}

/* print data to file */
void fprint_ascii_line(const u_char *payload, int len, int offset) {

    int i;
    const u_char *ch;
    FILE *file;
    file = fopen("/tmp/payload.txt", "w+");

    /* ascii */
    ch = payload;
    for(i = 0; i < len; i++) {
        fprintf(file, "%c", *ch);
        ch++;
    }
    fclose (file);

    return;
}
/*
 * print data in rows of 16 bytes: offset   hex   ascii
 * 00000   4745 5420 2f20 4854   5450 2f31 2e31 0d0a   GET / HTTP/1.1..
 */
void print_hex_ascii_line(const u_char *payload, int len, int offset) {

    int i;
    int gap;
    const u_char *ch;

    /* offset */
    printf("%05d   ", offset);

    /* hex */
    ch = payload;
    for(i = 0; i < len; i++) {
        printf("%02x", *ch);
        ch++;
        /* print extra space after for visual aid */
        if (i%2 != 0)
            printf(" ");
        if (i == 7)
            printf("   ");
    }
    /* print space to handle_dev line less than 8 bytes */
    if (len < 8)
        printf("   ");

    /* fill hex gap with spaces if not full line */
    if (len < 16) {
        gap = 16 - len;
        for (i = 0; i < gap; i++) {
            printf("  ");
            if (i%2 == 0)
                printf(" ");
        }
    }
    printf("   ");

    /* ascii (if printable) */
    ch = payload;
    for(i = 0; i < len; i++) {
        if (isprint(*ch))
            printf("%c", *ch);
        else
            printf(".");
        ch++;
    }

    printf("\n");

    return;
}

/* app name/banner */
void print_info(void) {

    printf("\n%s\n", APP_NAME);
    printf("%s\n", APP_DESC);
    printf("%s\n", APP_COPYRIGHT);
    printf("\n");

    return;
}

/* print help text */
void print_usage(char *name) {

    print_info();

    printf("usage:\n   %s <interface> [options]\n\n", name);
    printf("interface:\n");
    printf("   -i interface1      Capture packets from interface1.\n\n");
    printf("options:\n");
    printf("   -I interface2      Forward packets to interface2.\n");
    printf("   -n number          Number of packets to capture.\n");
    printf("   -h                 Hide packet headers.\n");
    printf("   -p                 Hide payload.\n");
    printf("   -u                 unidirectional forwarding from interface1 to interface2.\n");
    printf("   -f 'filter'        Tcpdump packet filter expression.\n\n");
    printf("example:\n");
    printf("   sudo etherbridge -i eth0 -I eth1 -f 'udp port 6112 and dst host 192.168.1.2'\n\n'");

    return;
}

/**
* Send out a packet through the handle.
*/
void send_packet(pcap_t *handle, const u_char *packet, size_t size) {
   if (handle == NULL) {
       fprintf(stderr, "Try to send_packet to NULL handle\n");
       return;
   }
   /* Send the packet */
   if (pcap_sendpacket(handle, packet, size) != 0) {
       fprintf(stderr,"\nError sending the packet: %s\n", pcap_geterr(handle));
   }
   return;
}
int parse_pkt(const u_char *packet,int hide_header,int hide_payload){
    const struct sniff_ethernet *ethernet;  /* The ethernet header [1] */
    /* define ethernet header */
    ethernet = (struct sniff_ethernet*)(packet);
    if(ntohs(ethernet->ether_type)==0x0800) {
        return parse_ip(packet,hide_header,hide_payload);
    }else if(ntohs(ethernet->ether_type)==0x0806) {
        return parse_arp(packet,hide_header,hide_payload);
    } else {
        printf("Unknown  Ethernet packet.\n");
        return -1;
    }

}
/**
 * Process the ip packet.
 */
int parse_ip(const u_char *packet,int hide_header,int hide_payload){
    const struct sniff_ip *ip;              /* The IP header */
    int size_ip=0;
    ip = (struct sniff_ip*)(packet + SIZE_ETHERNET);
    size_ip = IP_HL(ip)*4;
    if (size_ip < 20) {
        printf("\n  Error: invalid IP header length: %u bytes\n", size_ip);
        return -1;
    }

    size_ip = SIZE_ETHERNET + ntohs(ip->ip_len);
    /* determine protocol */	
    switch(ip->ip_p) {
        case IPPROTO_TCP:
            parse_tcp(packet,ip,size_ip,hide_header,hide_payload);
            break;
        case IPPROTO_UDP:
            parse_udp(packet,ip,size_ip,hide_header,hide_payload);
            break;
        case IPPROTO_ICMP:
            printf("ICMP Pkt: %s --> %s\n", inet_ntoa(ip->ip_src), inet_ntoa(ip->ip_dst));
            break;
        case IPPROTO_IP:
            printf("IP Pkt: %s --> %s\n", inet_ntoa(ip->ip_src), inet_ntoa(ip->ip_dst));
            break;
        default:
            printf("Unknown header=0x%x\n",ip->ip_p);
    }
    return size_ip;
}

/**
 * Process the arp packet.
 */
int parse_arp(const u_char *packet,int hide_header,int hide_payload){

    struct arphdr *arpheader = NULL;       /* Pointer to the ARP header              */ 
    arpheader = (struct arphdr *)(packet+14); /* Point to the ARP header */ 
    printf("Hardware type: %s\n", (ntohs(arpheader->htype) == 1) ? "Ethernet" : "Unknown"); 
    printf("Protocol type: %s\n", (ntohs(arpheader->ptype) == 0x0800) ? "IPv4" : "Unknown"); 
    printf("Operation: %s\n", (ntohs(arpheader->oper) == ARP_REQUEST)? "ARP Request" : "ARP Reply"); 
    return ntohs(arpheader->oper);
}

/**
 * Process the tcp packet.
 */
void parse_tcp(const u_char *packet,const struct sniff_ip *ip,int size_ip,int hide_header,int hide_payload){
    int size_tcp=0;
    const struct sniff_tcp *tcp;            /* The TCP header */
    int size_payload=0;
    const u_char *payload;                  /* Packet payload */

    /* define/compute tcp header offset */
    tcp = (struct sniff_tcp*)(packet + SIZE_ETHERNET + size_ip);
    size_tcp = TH_OFF(tcp)*4;
    if (size_tcp < 20) {
        printf("\n  Error: invalid TCP header length: %u bytes\n", size_tcp);
        return;
    }

    /* define/compute tcp payload (segment) offset */
    payload = (u_char *)(packet + SIZE_ETHERNET + size_ip + size_tcp);

    /* compute tcp payload (segment) size */
    size_payload = ntohs(ip->ip_len) - (size_ip + size_tcp);

    /* print packet info */
    if (!hide_header) {
        printf("IP header Src Addr: %s, Dst Addr: %s\n", inet_ntoa(ip->ip_src), inet_ntoa(ip->ip_dst));
        printf("            Len: %i   ID: %i   TTL: %i\n", size_ip+size_tcp+size_payload, ip->ip_id, ip->ip_ttl);
        printf("TCP header  Src port: %i   Dst port: %i   Len: %i\n", ntohs(tcp->th_sport), ntohs(tcp->th_dport), size_tcp+size_payload);
    }
    if (!hide_payload) {
        printf("Payload (%d bytes)\n", size_payload);
        print_payload(payload, size_payload);
    }
}

/**
 * Process the udp packet.
 */
void parse_udp(const u_char *packet,const struct sniff_ip *ip,int size_ip, int hide_header,int hide_payload){
    int size_udp=0;
    const struct sniff_udp *udp;            /* The TCP header */
    int size_payload=0;
    const u_char *payload;                  /* Packet payload */

    /* define/compute udp header offset */
    udp = (struct sniff_udp*)(packet + SIZE_ETHERNET + size_ip);
    size_udp = 8;

    /* define/compute tcp payload (segment) offset */
    payload = (u_char *)(packet + SIZE_ETHERNET + size_ip + size_udp);

    /* compute udp payload (segment) size */
    size_payload = ntohs(ip->ip_len) - (size_ip + size_udp);

    if (!hide_header) {
        /* print source and destination IP addresses */
        printf("IP header Src Addr: %s, Dst Addr: %s\n", inet_ntoa(ip->ip_src), inet_ntoa(ip->ip_dst));
        printf("             Len: %i   ID: %i   TTL: %i\n", size_ip+size_udp+size_payload, ip->ip_id, ip->ip_ttl);
        printf("UDP header   Src Port: %i   Dst Port: %i   Len: %i\n", ntohs(udp->uh_sport), ntohs(udp->uh_dport), size_udp+size_payload);
    }
    if (!hide_payload) {
        /* Print payload data; it might be binary, so don't just treat it as a string. */
        printf("Payload (%d bytes)\n", size_payload);
        print_payload(payload, size_payload);
    }
}
