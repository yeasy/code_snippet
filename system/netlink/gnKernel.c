/**
 * This file demo how to register a new generic netlink family in kernel, 
 * using libnl APIs.
 */
#include <net/genetlink.h>
#include <linux/module.h>
#include <linux/kernel.h>

#define VERSION_NR 0x1
#ifndef NL_FAMILY_NAME
#define NL_FAMILY_NAME "TEST_FAMILY"
#endif

/* attributes (variables): the index in this enum is used as a reference for the type,
 * userspace application has to indicate the corresponding type
 * the policy is used for security considerations 
 */
enum {
    TEST_ATTR_UNSPEC,
    TEST_ATTR_MSG,
    __TEST_ATTR_MAX,
};
#define TEST_ATTR_MAX (__TEST_ATTR_MAX - 1)

/* attribute policy: defines which attribute has which type (e.g int, char * etc)
 * possible values defined in net/netlink.h 
 */
static struct nla_policy test_nla_policy[TEST_ATTR_MAX + 1] = {
    [TEST_ATTR_MSG] = { .type = NLA_NUL_STRING },
};

/* family*/
static struct genl_family test_family = {
    .id = GENL_ID_GENERATE,         //genetlink should generate an id
    .hdrsize = 0,
    .name = NL_FAMILY_NAME,        //the name of this family, used by userspace application
    .version = VERSION_NR,          //version number  
    .maxattr = TEST_ATTR_MAX,
};

/* commands: enumeration of all commands (functions), 
 * used by userspace application to identify command to be ececuted
 */
enum {
    TEST_CMD_UNSPEC,
    TEST_CMD_ECHO,
    __TEST_CMD_MAX,
};
#define TEST_CMD_MAX (__TEST_CMD_MAX - 1)


static int test_echo(struct sk_buff *skb_2, struct genl_info *info);

/* commands: mapping between the command enumeration and the actual function*/
static struct genl_ops test_ops_echo = {
    .cmd = TEST_CMD_ECHO,
    .flags = 0,
    .policy = test_nla_policy,
    .doit = test_echo,
    .dumpit = NULL,
};

/* an echo command, receives a message, prints it and sends another message back */
static int test_echo(struct sk_buff *skb_2, struct genl_info *info)
{
    struct nlattr *na;
    struct sk_buff *skb;
    int rc;
    void *msg_head;
    char * mydata;

    if (info == NULL)
        goto out;

    /*for each attribute there is an index in info->attrs which points to a nlattr structure
     *in this structure the data is given
     */
    na = info->attrs[TEST_ATTR_MSG];
    if (na) {
        mydata = (char *)nla_data(na);
        if (mydata == NULL)
            printk("error while receiving data\n");
        else
            printk("[Kernelspace]: received: %s\n", mydata);
    } else {
        printk("no info->attrs %i\n", TEST_ATTR_MSG);
    }

    /* send a message back*/
    /* allocate some memory, since the size is not yet known use NLMSG_GOODSIZE*/	
    skb = genlmsg_new(NLMSG_GOODSIZE, GFP_KERNEL);
    if (skb == NULL)
        goto out;

    /* create the message headers:
       struct sk_buff *, int (sending) pid, int sequence number, struct genl_family *, int flags, 
       u8 command index (why do we need this?)
       */
    msg_head = genlmsg_put(skb, 0, info->snd_seq+1, &test_family, 0, TEST_CMD_ECHO);
    if (msg_head == NULL) {
        rc = -ENOMEM;
        goto out;
    }
    /* add a TEST_ATTR_MSG attribute (actual value to be sent) */
    rc = nla_put_string(skb, TEST_ATTR_MSG, "Received your msg, and hello Userspace.");
    if (rc != 0)
        goto out;

    /* finalize the message */
    genlmsg_end(skb, msg_head);

    /* send the message back */
    rc = genlmsg_unicast(&init_net, skb, info->snd_pid);
    if (rc != 0)
        goto out;
    return 0;

out:
    printk("an error occured in test_echo:\n");
    return 0;
}

static int __init gnKernel_init(void)
{
    int rc;

    /*register new family*/
    rc = genl_register_family(&test_family);
    if (rc != 0) {
        printk("failed in registering new family with error %i.\n",rc);
        return -1;
    }

    /*register functions (commands) of the new family*/
    rc = genl_register_ops(&test_family, &test_ops_echo);
    if (rc != 0){
        printk("failed in registering operations with error %i.\n",rc);
        genl_unregister_family(&test_family);
        return -1;
    }

    printk("TEST GENL MODULE INIT() SUCCESSFULLY.\n");
    return 0;
}

static void __exit gnKernel_exit(void)
{
    int ret;

    /*unregister the operations.*/
    ret = genl_unregister_ops(&test_family, &test_ops_echo);
    if(ret != 0){
        printk("failed in unregistering ops with error %i.\n",ret);
        return;
    }

    /*unregister the family.*/
    ret = genl_unregister_family(&test_family);
    if(ret != 0){
        printk("failed in unregistering family with error %i.\n",ret);
        return;
    }

    printk("TEST GENL MODULE EXIT() SUCCESSFULLY.\n");
}

module_init(gnKernel_init);
module_exit(gnKernel_exit);
MODULE_LICENSE("GPL");
