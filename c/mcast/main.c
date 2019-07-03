#include <unistd.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <signal.h>
#include <sys/types.h>
#include <pthread.h>
#include "mcast.h"

int main(int argc, char *argv[])
{
    extern char *optarg;
    extern int optind,opterr;
    int opt,interval;
    pthread_t send_tid, recv_tid;

    struct mcast_msg msg;
    msg.payload = malloc(1024);
    struct mc_send_arg arg_send={0,0,0,NULL,false};
    struct mc_recv_arg arg_recv={0,0,NULL};

    while ((opt = getopt(argc, argv, "g:p:t:c:")) != -1) {
        switch (opt) {
            case 'g': /*group id*/
                arg_send.group_ip = inet_addr(optarg);
                arg_recv.group_ip = inet_addr(optarg);
                printf("group_ip=%s\n",optarg);
                break;
            case 'p': /*port*/
                arg_send.port = atoi(optarg);
                arg_recv.port = atoi(optarg);
                printf("port=%d\n",arg_send.port);
                break;
            case 't': /*time interval*/
                interval = atoi(optarg);
                printf("interval=%d\n",interval);
                break;
            case 'c': /*msg*/
                msg.hdr = 100;
                memcpy(msg.payload, optarg,strlen(optarg));
                break;
            default: /* '?' */
                fprintf(stderr, "Usage: %s [-t secs] [-g group_ip] [-p port]\n", argv[0]);
                exit(EXIT_FAILURE);
        }
    }

    arg_send.msg = &msg;
    arg_send.len_msg = sizeof(msg);
    bool t1, t2;
    arg_send.stop = &t1;
    *arg_send.stop = false;
    arg_recv.stop = &t2;
    *arg_recv.stop = false;

    printf("ip=%lu,port=%d, interval=%d,msg is %lu:%s\n",arg_send.group_ip,arg_send.port,interval,msg.hdr,msg.payload);

#ifdef __NO__DEF__XXX
    /* now create new process */
    childpid = fork();
    if (childpid >= 0) {/* fork succeeded */
        if (childpid == 0) {/* the child process */
            mc_recv(&arg_recv);
        } else {/* the parent process */
            while (count++ < 10) {
                mc_send(&arg_send);
                sleep(interval); /* wait some sec. */
                msg.hdr ++;
            }
            kill(childpid,SIGUSR1);
        }
    } else {/* fork returns -1 on failure */
        perror("fork"); /* display error message */
    }
#endif

    pthread_create(&send_tid,NULL,mc_send,&arg_send);
    pthread_create(&recv_tid,NULL,mc_recv,&arg_recv);
    sleep(10);
    *arg_send.stop = true;
    *arg_recv.stop = true;
    free(msg.payload);
    return 0;
}
