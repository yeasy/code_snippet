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

#ifndef MCAST_H
#define MCAST_H
#include<stdbool.h>

#ifndef MCAST_GROUP_IP
#define MCAST_GROUP_IP "239.0.0.1"
#endif

#ifndef MCAST_GROUP_PORT
#define MCAST_GROUP_PORT 5000
#endif

/**
 * 224.0.0.* reserved
 * 224.0.1.* public multicast for internet
 * 224.0.2.0 ~ 238.255.255.255 temporary multicast for users
 * 239.*.*.* local multicast
 */
struct mcast_msg {
    unsigned long hdr;
    unsigned char *payload;
};

struct mc_send_arg {
    unsigned long group_ip; //multicast group
    unsigned int port; //multicast port
    int len_msg;
    struct mcast_msg *msg;
    bool *stop;
};

struct mc_recv_arg {
    unsigned long group_ip; //multicast group
    unsigned int port;
    bool *stop;
};

void mc_send(struct mc_send_arg* arg);
void mc_recv(struct mc_recv_arg* arg);

#endif
