/*
 * headers.h
 *
 */

#include <pcap.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
/* ethernet headers are always exactly 14 bytes  */
#ifndef SIZE_ETHERNET
#define SIZE_ETHERNET 14
#endif

/* ethernet addresses are 6 bytes */
#ifndef ETHER_ADDR_LEN
#define ETHER_ADDR_LEN	6
#endif

/* Ethernet header */
struct sniff_ethernet {
	u_char  ether_dhost[ETHER_ADDR_LEN];    /* destination host address */
	u_char  ether_shost[ETHER_ADDR_LEN];    /* source host address */
	u_short ether_type;                     /* IP? ARP? RARP? etc */
};

/* IP header */
struct sniff_ip {
	u_char  ip_vhl;                 /* version << 4 | header length >> 2 */
	u_char  ip_tos;                 /* type of service */
	u_short ip_len;                 /* total length */
	u_short ip_id;                  /* identification */
	u_short ip_off;                 /* fragment offset field */
	#define IP_RF 0x8000            /* reserved fragment flag */
	#define IP_DF 0x4000            /* dont fragment flag */
	#define IP_MF 0x2000            /* more fragments flag */
	#define IP_OFFMASK 0x1fff       /* mask for fragmenting bits */
	u_char  ip_ttl;                 /* time to live */
	u_char  ip_p;                   /* protocol */
	u_short ip_sum;                 /* checksum */
	struct  in_addr ip_src,ip_dst;  /* source and dest address */
};
#define IP_HL(ip)               (((ip)->ip_vhl) & 0x0f)
#define IP_V(ip)                (((ip)->ip_vhl) >> 4)

/* ARP Header, (assuming Ethernet+IPv4)            */ 
#define ARP_REQUEST 1   /* ARP Request             */ 
#define ARP_REPLY 2     /* ARP Reply               */ 
struct arphdr { 
    u_int16_t htype;    /* Hardware Type           */ 
    u_int16_t ptype;    /* Protocol Type           */ 
    u_char hlen;        /* Hardware Address Length */ 
    u_char plen;        /* Protocol Address Length */ 
    u_int16_t oper;     /* Operation Code          */ 
    u_char sha[6];      /* Sender hardware address */ 
    u_char spa[4];      /* Sender IP address       */ 
    u_char tha[6];      /* Target hardware address */ 
    u_char tpa[4];      /* Target IP address       */ 
}; 

#define MAXBYTES2CAPTURE 2048 

/* TCP header */
typedef u_int tcp_seq;

struct sniff_tcp {
    u_short th_sport;               /* source port */
    u_short th_dport;               /* destination port */
    tcp_seq th_seq;                 /* sequence number */
    tcp_seq th_ack;                 /* acknowledgement number */
    u_char  th_offx2;               /* data offset, rsvd */
#define TH_OFF(th)      (((th)->th_offx2 & 0xf0) >> 4)
    u_char  th_flags;
#define TH_FIN  0x01
#define TH_SYN  0x02
#define TH_RST  0x04
#define TH_PUSH 0x08
#define TH_ACK  0x10
#define TH_URG  0x20
#define TH_ECE  0x40
#define TH_CWR  0x80
#define TH_FLAGS        (TH_FIN|TH_SYN|TH_RST|TH_ACK|TH_URG|TH_ECE|TH_CWR)
    u_short th_win;                 /* window */
    u_short th_sum;                 /* checksum */
    u_short th_urp;                 /* urgent pointer */
};

/* UDP header */
struct sniff_udp {
    unsigned short int uh_sport;
    unsigned short int uh_dport;
    unsigned short int uh_len;
    unsigned short int uh_check;
}; /* total udp header length: 8 bytes (=64 bits) */

#define APP_NAME		"EtherBridge 0.1"
#define APP_DESC		"Ethernet packet capture and forward application based on libpcap, can connect two ports bidirectionally."
#define APP_COPYRIGHT	"Copyright (c)"

/* default snap length (maximum bytes per packet to capture) */
#ifndef BUFSIZ
#define BUFSIZ 2048
#endif

void print_payload(const u_char *payload, int len);
void fprint_ascii_line(const u_char *payload, int len, int offset); 
void print_hex_ascii_line(const u_char *payload, int len, int offset);
void print_info(void);
void print_usage(char *name);
void send_packet(pcap_t *handle_dev2, const u_char *packet, size_t size);
int parse_pkt(const u_char *packet,int hide_header,int hide_payload);
int parse_ip(const u_char *packet, int hide_header,int hide_payload);
int parse_arp(const u_char *packet, int hide_header,int hide_payload);
void parse_tcp(const u_char *packet,const struct sniff_ip *ip,int size_ip,int hide_header,int hide_payload);
void parse_udp(const u_char *packet,const struct sniff_ip *ip,int size_ip, int hide_header,int hide_payload);
