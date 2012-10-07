#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <poll.h>
#include <string.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/socket.h>
#include <sys/types.h>
#include <signal.h>

#include <linux/genetlink.h>
#ifndef NL_FAMILY_NAME
#define NL_FAMILY_NAME "TEST_FAMILY"
#endif

/*
 * Generic macros for dealing with netlink sockets. Might be duplicated
 * elsewhere. It is recommended that commercial grade applications use
 * libnl or libnetlink and use the interfaces provided by the library
 */
#define GENLMSG_DATA(glh) ((void *)(NLMSG_DATA(glh) + GENL_HDRLEN))
#define GENLMSG_PAYLOAD(glh) (NLMSG_PAYLOAD(glh, 0) - GENL_HDRLEN)
#define NLA_DATA(na) ((void *)((char*)(na) + NLA_HDRLEN))
#define NLA_PAYLOAD(len) (len - NLA_HDRLEN)

int done = 0;
int nl_socket; /*the socket*/
/*
 * Create a raw netlink socket and bind.
 * @param family: netlink family type.
 * @param groups: group bitmask.
 */
static int create_nl_socket(int family_type, int groups) {
    //socklen_t addr_len;
    int fd;
    struct sockaddr_nl local;

    /*Create socket.*/
    fd = socket(AF_NETLINK, SOCK_RAW, family_type);
    if (fd < 0){
        perror("socket");
        return -1;
    }

    /*Bind socket.*/
    memset(&local, 0, sizeof(local));
    local.nl_family = AF_NETLINK;
    local.nl_groups = groups;
    if (bind(fd, (struct sockaddr *)&local, sizeof(local)) < 0)
        goto error;

    return fd;
error:
    close(fd);
    return -1;
}

/*
 * Send netlink msg_content to kernel.
 * @param socket: Socket to send through.
 * @param buf: Content buffer.
 * @param bufLen: Length of the buffer.
 * @return: 0 if success.
 */
int send_to_kernel(int socket, const char *buf, int bufLen)
{
    struct sockaddr_nl sa;
    int r;

    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;

    while ((r = sendto(socket, buf, bufLen, 0, (struct sockaddr *) &sa,
                    sizeof(sa))) < bufLen) {
        if (r > 0) {
            buf += r;
            bufLen -= r;
        } else if (errno != EAGAIN)
            return -1;
    }
    return 0;
}

/*
 * Probe the controller in genetlink to find the family id
 * for the CONTROL_TEST family
 */
int get_family_id(int socket)
{
    struct {
        struct nlmsghdr n;
        struct genlmsghdr g;
        char buf[256];
    } req;

    struct {
        struct nlmsghdr n;
        struct genlmsghdr g;
        char buf[256];
    } reply;

    int id;
    struct nlattr *na;
    int reply_len;

    /* netlink header */
    req.n.nlmsg_type = GENL_ID_CTRL;
    req.n.nlmsg_flags = NLM_F_REQUEST;
    req.n.nlmsg_seq = 0;
    req.n.nlmsg_pid = getpid();
    req.n.nlmsg_len = NLMSG_LENGTH(GENL_HDRLEN);
    /* generic netlink header */
    req.g.cmd = CTRL_CMD_GETFAMILY;
    req.g.version = 0x1;

    /* attributes */
    na = (struct nlattr *) GENLMSG_DATA(&req);
    na->nla_type = CTRL_ATTR_FAMILY_NAME;
    /*------change here--------*/
    na->nla_len = strlen(NL_FAMILY_NAME) + 1 + NLA_HDRLEN;
    strcpy(NLA_DATA(na), NL_FAMILY_NAME);

    req.n.nlmsg_len += NLMSG_ALIGN(na->nla_len);

    if (send_to_kernel(socket, (char *) &req, req.n.nlmsg_len) < 0)
        return -1;

    reply_len = recv(socket, &reply, sizeof(reply), 0);
    if (reply_len < 0){
        perror("recv");
        return -1;
    }

    /* Validate response msg_content */
    if (!NLMSG_OK((&reply.n), reply_len)){
        fprintf(stderr, "invalid reply msg_content\n");
        return -1;
    }

    if (reply.n.nlmsg_type == NLMSG_ERROR) { /* error */
        fprintf(stderr, "received error\n");
        return -1;
    }

    na = (struct nlattr *) GENLMSG_DATA(&reply);
    na = (struct nlattr *) ((char *) na + NLA_ALIGN(na->nla_len));
    if (na->nla_type == CTRL_ATTR_FAMILY_ID) {
        id = *(__u16 *) NLA_DATA(na);
    }
    return id;
}

int main() {
    /*create and bind a NETLINK_GENERIC socket.*/
    nl_socket = create_nl_socket(NETLINK_GENERIC,0);
    if(nl_socket < 0){
        printf("create failure\n");
        return -1;
    }
    int id = get_family_id(nl_socket);
    if (id == -1) {
        goto end;
    } 
    printf("get family id = %d\n",id);
    struct {
        struct nlmsghdr n;
        struct genlmsghdr g;
        char buf[256];
    } reply; //reply msg_content

    struct {
        struct nlmsghdr n; //netlink header
        struct genlmsghdr g; //generic netlink header
        char buf[256];
    } req; //request msg_content
    struct nlattr *na;

    /* construct the netlink header. */
    req.n.nlmsg_len = NLMSG_LENGTH(GENL_HDRLEN);
    req.n.nlmsg_type = id; //family id
    req.n.nlmsg_flags = NLM_F_REQUEST;
    req.n.nlmsg_seq = 60;
    req.n.nlmsg_pid = getpid();

    /* construct the generic netlink header. */
    req.g.cmd = 1; //TEST_CMD_ECHO;

    /*construct the attributes.*/
    char * msg_content = "Hello Kernelspace!"; //msg_content content
    int mlength = strlen(msg_content)+1;
    na = (struct nlattr *) GENLMSG_DATA(&req); //attributes
    na->nla_type = 1; //TEST_ATTR_MSG;
    na->nla_len = mlength+NLA_HDRLEN; //msg_content length
    memcpy(NLA_DATA(na), msg_content, mlength);
    req.n.nlmsg_len += NLMSG_ALIGN(na->nla_len); //add new attr len

    /*send the request message.*/
    struct sockaddr_nl sa;
    memset(&sa, 0, sizeof(sa));
    sa.nl_family = AF_NETLINK;
    if (sendto(nl_socket, (char *)&req, req.n.nlmsg_len, 0, (struct sockaddr *) &sa, sizeof(sa))< 0) {
        printf("Error in sending msg to kernel.\n");
        return -1;
    }

    printf("[Userspace]: send msg to kernel: %s.\n",msg_content);

    /*receive the reply message.*/
    int reply_len = recv(nl_socket, &reply, sizeof(reply), 0);
    /* Validate response msg_content */
    if (reply.n.nlmsg_type == NLMSG_ERROR) { /* error */
        printf("error received NACK - leaving \n");
        return -1;
    }
    if (reply_len < 0) {
        printf("error receiving reply msg via Netlink \n");
        return -1;
    }
    if (!NLMSG_OK((&reply.n), reply_len)) {
        printf("invalid reply msg received via Netlink\n");
        return -1;
    }

    reply_len = GENLMSG_PAYLOAD(&reply.n); //get the length of the payload

    /*parse the reply message, print the attribute content.*/
    na = (struct nlattr *) GENLMSG_DATA(&reply);
    printf("[Userspace]: receive msg from kernel: %s\n",NLA_DATA(na));

end:
    close(nl_socket);
    return 0;
}
