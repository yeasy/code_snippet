#include <net/genetlink.h>
#include <linux/module.h>
#include <linux/kernel.h>

#define VERSION_NR 1
#ifndef NL_FAMILY_NAME
#define NL_FAMILY_NAME "CONTROL_EXMPL"
#endif

/* attributes (variables): the index in this enum is used as a reference for the type,
 * userspace application has to indicate the corresponding type
 * the policy is used for security considerations 
 */
enum {
    EXAMP_ATTR_UNSPEC,
    EXAMP_ATTR_MSG,
    __EXAMP_ATTR_MAX,
};
#define EXAMP_ATTR_MAX (__EXAMP_ATTR_MAX - 1)

/* attribute policy: defines which attribute has which type (e.g int, char * etc)
 * possible values defined in net/netlink.h 
 */
static struct nla_policy examp_genl_policy[EXAMP_ATTR_MAX + 1] = {
    [EXAMP_ATTR_MSG] = { .type = NLA_NUL_STRING },
};


/* family definition */
static struct genl_family examp_gnl_family = {
    .id = GENL_ID_GENERATE,         //genetlink should generate an id
    .hdrsize = 0,
    .name = NL_FAMILY_NAME,        //the name of this family, used by userspace application
    .version = VERSION_NR,          //version number  
    .maxattr = EXAMP_ATTR_MAX,
};

/* commands: enumeration of all commands (functions), 
 * used by userspace application to identify command to be ececuted
 */
enum {
    EXMPL_C_UNSPEC,
    EXMPL_C_ECHO,
    __EXMPL_C_MAX,
};
#define EXMPL_C_MAX (__EXMPL_C_MAX - 1)


static int examp_echo(struct sk_buff *skb_2, struct genl_info *info);

/* commands: mapping between the command enumeration and the actual function*/
static struct genl_ops examp_gnl_ops_echo = {
    .cmd = EXMPL_C_ECHO,
    .flags = 0,
    .policy = examp_genl_policy,
    .doit = examp_echo,
    .dumpit = NULL,
};

/* an echo command, receives a message, prints it and sends another message back */
static int examp_echo(struct sk_buff *skb_2, struct genl_info *info)
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
    na = info->attrs[EXAMP_ATTR_MSG];
    if (na) {
        mydata = (char *)nla_data(na);
        if (mydata == NULL)
            printk("error while receiving data\n");
        else
            printk("received: %s\n", mydata);
    } else {
        printk("no info->attrs %i\n", EXAMP_ATTR_MSG);
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
    msg_head = genlmsg_put(skb, 0, info->snd_seq+1, &examp_gnl_family, 0, EXMPL_C_ECHO);
    if (msg_head == NULL) {
        rc = -ENOMEM;
        goto out;
    }
    /* add a EXAMP_ATTR_MSG attribute (actual value to be sent) */
    rc = nla_put_string(skb, EXAMP_ATTR_MSG, "[Kernelspace to Userspace] Received your msg, and hello Userspace.");
    if (rc != 0)
        goto out;

    /* finalize the message */
    genlmsg_end(skb, msg_head);

    /* send the message back */
    rc = genlmsg_unicast(&init_net, skb, info->snd_pid);
    //rc = 0;
    if (rc != 0)
        goto out;
    return 0;

out:
    printk("an error occured in examp_echo:\n");

    return 0;
}

static int __init gnKernel_init(void)
{
    int rc;
    printk("INIT GENERIC NETLINK EXEMPLE MODULE\n");

    /*register new family*/
    rc = genl_register_family(&examp_gnl_family);
    if (rc != 0)
        goto failure;

    /*register functions (commands) of the new family*/
    rc = genl_register_ops(&examp_gnl_family, &examp_gnl_ops_echo);
    if (rc != 0){
        printk("register ops: %i\n",rc);
        genl_unregister_family(&examp_gnl_family);
        goto failure;
    }

    return 0;

failure:
    printk("an error occured while inserting the generic netlink example module\n");
    return -1;
}

static void __exit gnKernel_exit(void)
{
    int ret;
    printk("EXIT GENERIC NETLINK EXEMPLE MODULE\n");

    /*unregister the functions*/
    ret = genl_unregister_ops(&examp_gnl_family, &examp_gnl_ops_echo);
    if(ret != 0){
        printk("unregister ops: %i\n",ret);
        return;
    }

    /*unregister the family*/
    ret = genl_unregister_family(&examp_gnl_family);
    if(ret !=0){
        printk("unregister family %i\n",ret);
    }
}

module_init(gnKernel_init);
module_exit(gnKernel_exit);
MODULE_LICENSE("GPL");
