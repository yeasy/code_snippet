/*
 * Based on tcpdump sniffer, arpsniffer code and Micky Holdorf's packetforward project.
 *
 */

#include <pcap.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include <arpa/inet.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
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

void got_packet_dev(u_char *args, const struct pcap_pkthdr *header, const u_char *packet);
void got_packet_dev2(u_char *args, const struct pcap_pkthdr *header, const u_char *packet);
void got_packet(u_char *args, const struct pcap_pkthdr *header, const u_char *packet, pcap_t *fwd_dev);

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
    printf("Received pkt F#%i:\n",count);
    if (parse_pkt(packet,hide_header,hide_payload)>=0) {
        if (!capture_only && fwd_dev != NULL) {
            send_packet(fwd_dev,packet,header->len);
        }
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
             return NULL;
        }
        if (handle_dev != NULL) pcap_close(handle_dev);
    } else if(strcmp(device_name,dev2)==0){
        if(unidirectional==0) {
            if(pcap_loop(handle_dev2, num_packets, got_packet_dev2, NULL)==-1) {
             fprintf(stderr, "ERROR: %s\n", pcap_geterr(handle_dev2));
             return NULL;
            }
            if (handle_dev2 != NULL) pcap_close(handle_dev2);
        }
    }
    return NULL;
}

int main(int argc, char **argv) {
    int c;
    pthread_t t1,t2;

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
        pthread_create(&t1, NULL, cap_and_fwd, (void*) dev);
        pthread_create(&t2, NULL, cap_and_fwd, (void*) dev2);
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
