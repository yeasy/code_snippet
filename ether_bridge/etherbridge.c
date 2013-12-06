/*
 * Based on tcpdump sniffer, arpsniffer code and Micky Holdorf's packetforward project.
 *
 */

#include <pcap.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <pthread.h>

#include "headers.h"

char *dev = NULL;						/* capture device1 name */
char *dev2 = NULL;						/* capture device2 name */

pcap_t *handle_dev=NULL;			    /* packet capture handle_dev */
pcap_t *handle_dev2=NULL;				/* packet sending handle_dev2 */

int hide_header = 0;
int hide_payload = 1;
int capture_only = 1;
int unidirectional = 0;
int num_packets = -1;					/* number of packets to capture */
char *bpfFilter = NULL;				    /* filter expression */

extern char *optarg;
extern int optind, opterr;

void send_packet(pcap_t *handle_dev2, const u_char *packet, size_t size);
void got_packet_dev(u_char *args, const struct pcap_pkthdr *header, const u_char *packet);
void got_packet_dev2(u_char *args, const struct pcap_pkthdr *header, const u_char *packet);
void got_packet(u_char *args, const struct pcap_pkthdr *header, const u_char *packet, pcap_t *fwd_dev);


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
        fprintf(stderr,"\nError sending the packet: \n", pcap_geterr(handle));
    }
    return;
}

/**
 * Process the tcp packet.
 */
void parse_tcp(const u_char *packet,const struct sniff_ip *ip,int size_ip){
    int size_tcp=0;
    const struct sniff_tcp *tcp;            /* The TCP header */
    char *protocol="tcp";
    int size_payload=0;
    const u_char *payload;                  /* Packet payload */
    int sport,dport;

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

    sport=ntohs(tcp->th_sport);
    dport=ntohs(tcp->th_dport);

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
void parse_udp(const u_char *packet,const struct sniff_ip *ip,int size_ip){
    int size_udp=0;
    const struct sniff_udp *udp;            /* The TCP header */
    char *protocol="udp";
    int size_payload=0;
    const u_char *payload;                  /* Packet payload */
    int sport,dport;

    /* define/compute udp header offset */
    udp = (struct sniff_udp*)(packet + SIZE_ETHERNET + size_ip);
    size_udp = 8;

    /* define/compute tcp payload (segment) offset */
    payload = (u_char *)(packet + SIZE_ETHERNET + size_ip + size_udp);

    /* compute udp payload (segment) size */
    size_payload = ntohs(ip->ip_len) - (size_ip + size_udp);

    sport=ntohs(udp->uh_sport);
    dport=ntohs(udp->uh_dport);

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

/**
 * Process the arp packet.
 */
int parse_arp(const u_char *packet, int*size_packet){

    struct arphdr *arpheader = NULL;       /* Pointer to the ARP header              */ 
    arpheader = (struct arphdr *)(packet+14); /* Point to the ARP header */ 
    printf("Hardware type: %s\n", (ntohs(arpheader->htype) == 1) ? "Ethernet" : "Unknown"); 
    printf("Protocol type: %s\n", (ntohs(arpheader->ptype) == 0x0800) ? "IPv4" : "Unknown"); 
    printf("Operation: %s\n", (ntohs(arpheader->oper) == ARP_REQUEST)? "ARP Request" : "ARP Reply"); 
    return ntohs(arpheader->oper);
}

/**
 * Process the ip packet.
 */
void parse_ip(const u_char *packet, int*size_packet){
    const struct sniff_ip *ip;              /* The IP header */
    int size_ip=0;
    ip = (struct sniff_ip*)(packet + SIZE_ETHERNET);
    size_ip = IP_HL(ip)*4;
    if (size_ip < 20) {
        printf("\n  Error: invalid IP header length: %u bytes\n", size_ip);
        return;
    }

    *size_packet = SIZE_ETHERNET + ntohs(ip->ip_len);
    /* determine protocol */	
    switch(ip->ip_p) {
        case IPPROTO_TCP:
            parse_tcp(packet,ip,size_ip);
            break;
        case IPPROTO_UDP:
            parse_udp(packet,ip,size_ip);
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

}

/**
 * got packet at dev.
 */
void got_packet_dev(u_char *args, const struct pcap_pkthdr *header, const u_char *packet) {
    printf("got_packet_dev\n");
    got_packet(args, header, packet,handle_dev2);
}

/**
 * got packet at dev2.
 */
void got_packet_dev2(u_char *args, const struct pcap_pkthdr *header, const u_char *packet) {
    printf("got_packet_dev2\n");
    got_packet(args, header, packet,handle_dev);
}
/*
 * dissect/print packet
 */
void got_packet(u_char *args, const struct pcap_pkthdr *header, const u_char *packet,pcap_t *fwd_dev) {

    static int count = 1;                   /* packet counter */
    const struct sniff_ethernet *ethernet;  /* The ethernet header [1] */
    int size_packet=0;
    char *errbuf=NULL;

    printf("Received pkt F#%i:\n",count);
    /* define ethernet header */
    ethernet = (struct sniff_ethernet*)(packet);
    if(ntohs(ethernet->ether_type)==0x0800) {
        parse_ip(packet,&size_packet);
    }else if(ntohs(ethernet->ether_type)==0x0806) {
        parse_arp(packet,&size_packet);
    } else {
        printf("Unknown  Ethernet packet.\n");
        return;
    }
    
    if (!capture_only && fwd_dev != NULL) {
        send_packet(fwd_dev,packet,header->len);
    }

    count++;
    return;
}

/**
 * Compile and apply the filter expression.
 */
int set_filter(pcap_t *handle,struct bpf_program *fp,const char*bpfFilter){
    if(bpfFilter != NULL) {
        printf("Packet Filter: %s\n", bpfFilter);
        if (pcap_compile(handle, fp, bpfFilter, 0, PCAP_NETMASK_UNKNOWN) == -1) {
            fprintf(stderr, "Couldn't parse filter %s: %s\n", bpfFilter, pcap_geterr(handle));
            return(2);
        }
        if (pcap_setfilter(handle, fp) == -1) {
            fprintf(stderr, "Couldn't install filter %s: %s\n", bpfFilter, pcap_geterr(handle));
            return(2);
        }
    }
    return 0;
}

pcap_t * open_and_init(const char *dev_name, const char *bpfFilter) {
    pcap_t *handle = NULL;
    char errbuf[PCAP_ERRBUF_SIZE];			/* error buffer */
    struct bpf_program fp;					/* compiled filter program (expression) */
    /* open capture device*/
    if((handle= pcap_open_live(dev_name, BUFSIZ, 1, 100, errbuf))==NULL) {
        fprintf(stderr, "Couldn't open device %s: %s\n", dev_name, errbuf);
        return NULL;
    }

    /* make sure we're capturing on an Ethernet device */
    if (pcap_datalink(handle) != DLT_EN10MB) {
        fprintf(stderr, "Device %s doesn't provide Ethernet headers - not supported\n", dev_name);
        return NULL;
    }

    pcap_setdirection(handle,PCAP_D_IN);

    /* compile and apply the filter expression */
    if(set_filter(handle,&fp,bpfFilter)!=0){
        fprintf(stderr, "Error when setting filter to %s\n", dev_name);
        return NULL;
    }
    return handle;
}

void *cap_and_fwd(void *device_name) {
    if(strcmp(device_name,dev)==0){
        if(pcap_loop(handle_dev, num_packets, got_packet_dev, NULL)==-1) {
             fprintf(stderr, "ERROR: %s\n", pcap_geterr(handle_dev));
             return;
        }
        if (handle_dev != NULL) pcap_close(handle_dev);
    } else if(strcmp(device_name,dev2)==0){
        if(unidirectional==0) {
            if(pcap_loop(handle_dev2, num_packets, got_packet_dev2, NULL)==-1) {
             fprintf(stderr, "ERROR: %s\n", pcap_geterr(handle_dev2));
             return;
            }
            if (handle_dev2 != NULL) pcap_close(handle_dev2);
        }
    }
}

int main(int argc, char **argv) {

    bpf_u_int32 mask=0;				/* subnet mask */
    int c;
    pthread_t t1,t2;
    int  iret1, iret2;


    /* check command-line options */
    while ((c = getopt(argc, argv, "i:I:n:uhpf:")) != EOF) {
        switch (c) {
            case 'i':
                dev = optarg;
                dev2 = dev;	
                break;
            case 'I':
                dev2 = optarg;
                if(dev2 == dev){
                    fprintf(stderr, "Should use differnet interface to forward\n");
                    return 0;
                } else {
                    capture_only = 0;
                }
                break;
            case 'n':
                num_packets = atoi(optarg);
                break;
            case 'f':
                printf("num_packets= %d, dev2=%s\n", num_packets, dev2);
                bpfFilter = strdup(optarg);
                break;
            case 'h':
                hide_header = 1;
                break;
            case 'p':
                hide_payload = 1;
                break;
            case 'u':
                unidirectional = 1;
                break;
            default:
                print_usage(argv[0]);
                return 0;
        }
    }

    if (dev == NULL) {
        print_usage(argv[0]);
        return -1;
    }

    if(num_packets > 0) printf("Packets to capture: %d\n", num_packets);

    handle_dev = open_and_init(dev,bpfFilter);
    if (!capture_only){
        handle_dev2 = open_and_init(dev2,bpfFilter);
    }
    if (!unidirectional) {
        if (!capture_only) printf("Capture and forward between: %s, %s\n", dev, dev2);
        iret1 = pthread_create(&t1, NULL, cap_and_fwd, (void*) dev);
        iret2 = pthread_create(&t2, NULL, cap_and_fwd, (void*) dev2);
        pthread_join(t1, NULL);
        pthread_join(t2, NULL);
    } else {
        if (!capture_only) printf("Capture from %s, and forward to %s\n", dev, dev2);
        if(pcap_loop(handle_dev, num_packets, got_packet_dev, NULL)==-1){
            fprintf(stderr, "ERROR: %s\n", pcap_geterr(handle_dev));
            return 2;
        }
        /* cleanup */
        if (handle_dev != NULL) pcap_close(handle_dev);
        if (handle_dev2 != NULL) pcap_close(handle_dev2);
    }
    printf("\n\n--- Process complete. ---\n\n");
    return 0;
}
