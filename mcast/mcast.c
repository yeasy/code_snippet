/* Copyright (c) 2008, 2009, 2010, 2011, 2012 IBM CRL.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at:
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <errno.h>
#include <pthread.h>
#include <sys/socket.h>
#include <netinet/in.h>
#include "mcast.h"

pthread_mutex_t mutex;

/**
 * send mcast msg.
 * @param group multicast group ip
 * @param port multicast port
 * @param msg content to send
 * @param len_msg length of the content
 * @return 0 if success
 */
void mc_send(struct mc_send_arg* arg)
{
    int sock_id;
    struct sockaddr_in addr;
    socklen_t len;
    int ret;

    if (!arg) {
        return ;
    }

    /* open a socket. only udp support multicast */
    if ((sock_id = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("socket error");
        return;
    }

    /* build address */
    memset((void*)&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
/*addr.sin_addr.s_addr = inet_addr(group_ip);*/ 
    addr.sin_addr.s_addr = arg->group_ip; 
    addr.sin_port = htons(arg->port);

    len = sizeof(addr);
    /* it's very easy, just send the data to the address:port */
    while (!*arg->stop) {
        //printf("Send to %s:%u with %lu:%s\n", inet_ntoa(addr.sin_addr.s_addr), ntohs(addr.sin_port),arg->msg->hdr, arg->msg->payload);
        pthread_mutex_lock (&mutex);
        ret = sendto(sock_id, arg->msg, arg->len_msg, 0, (struct sockaddr *)&addr, len);
        pthread_mutex_unlock(&mutex);
        if (ret < 0) {
            perror("sendto error");
            return;
        }
        sleep(1);
    }

    close(sock_id);
    return;
}

/**
 * receive mcast msg, parse and store it.
 * @param group multicast group
 * @param port multicast port
 */
void mc_recv(struct mc_recv_arg* arg)
{
    int sock_id;
    struct sockaddr_in addr, sender;
    struct ip_mreq ipmr;
    socklen_t len;
    int ret;
    int count;
    struct mcast_msg *msg = malloc(sizeof(struct mcast_msg));

    /* Step 1: open a socket, and bind */
    if ((sock_id = socket(AF_INET, SOCK_DGRAM, 0)) < 0) {
        perror("socket error");
        return;
    }

    memset((void*)&addr, 0, sizeof(addr));
    addr.sin_family = AF_INET;
    addr.sin_addr.s_addr = htonl(INADDR_ANY);
    addr.sin_port = htons(arg->port);

    if (bind(sock_id, (struct sockaddr *)&addr, sizeof(addr)) < 0) {
        perror("bind error");
        return;
    }

    /* Step 2: fill in a struct ip_mreq */
    memset((void*)&ipmr, 0, sizeof(ipmr));
    ipmr.imr_multiaddr.s_addr = arg->group_ip; /* multicast group ip */
    ipmr.imr_interface.s_addr = htonl(INADDR_ANY);

    /* Step 3: call setsockopt with IP_ADD_MEMBERSHIP to support receiving multicast */
    if (setsockopt(sock_id, IPPROTO_IP, IP_ADD_MEMBERSHIP, &ipmr, sizeof(ipmr)) < 0) {
        perror("setsockopt:IP_ADD_MEMBERSHIP");
        if (errno == EBADF)
            printf("EBADF\n");
        else if (errno == EFAULT)
            printf("EFAULT\n");
        else if (errno == EINVAL)
            printf("EINVAL\n");
        else if (errno == ENOPROTOOPT)
            printf("ENOPROTOOPT\n");
        else if (errno == ENOTSOCK)
            printf("ENOTSOCK\n");
        return;
    }

    /* Step 4: call recvfrom to receive multicast packets */
    len = sizeof(sender);
    count = 0;
    while (!*arg->stop) {
        ret = recvfrom(sock_id, msg, sizeof(struct mcast_msg), 0, (struct sockaddr *)&sender, &len);
        pthread_mutex_lock (&mutex);
        pthread_mutex_unlock (&mutex);
        if (ret < 0) {
            perror("recvfrom error");
            return;
        }
        printf("[%d] Receive from %s:%d with %lu:%s\n", count, inet_ntoa(sender.sin_addr.s_addr), ntohs(sender.sin_port),msg->hdr,msg->payload);
        count ++;
    }

    /* Step 5: call setsockopt with IP_DROP_MEMBERSHIP to drop from multicast */
    if (setsockopt(sock_id, IPPROTO_IP, IP_DROP_MEMBERSHIP, &ipmr, sizeof(ipmr)) < 0) {
        perror("setsockopt:IP_DROP_MEMBERSHIP");
        return;
    }

    /* Step 6: close the socket */
    close(sock_id);
    free(msg);

    return;
}
