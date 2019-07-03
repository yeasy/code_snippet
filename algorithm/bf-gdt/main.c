#ifdef __KERNEL__
#include<linux/module.h>
#include<linux/init.h>
#include<linux/kernel.h>
#else
#include<stdio.h>
#include<string.h>
#endif

#include "bf-gdt.h"

#ifdef __KERNEL__
int __init start(void)
#else
int main(void)
#endif
{
    struct bf_gdt *gdt;

    if(!(gdt=bf_gdt_init(0))) {
#ifdef __KERNEL__
        printk("ERROR: Could not create bf-gdt\n");
#else
        printf("ERROR: Could not create bf-gdt\n");
#endif
        return -1;
    } else {
#ifdef __KERNEL__
        printk("created bf-gdt.\n");
#else
        printf("created bf-gdt.\n");
#endif
    }

    bf_gdt_add_filter(gdt,0,1024);
    bf_gdt_add_filter(gdt,1,2048);
#ifdef __KERNEL__
    printk("add bf into bf-gdt.\n");
#else
    printf("add bf into bf-gdt.\n");
#endif

    unsigned char q1[] = {0x0a,0x00,0x27,0x00,0x00,0x01};
    unsigned char q2[] = {0x08,0x00,0x27,0xab,0xb6,0xa5};
    unsigned char p1[13]={0};
    unsigned char p2[13]={0};
    sprintf(p1,"%02x%02x%02x%02x%02x%02x",q1[0],q1[1],q1[2],q1[3],q1[4],q1[5]);
    sprintf(p2,"%02x%02x%02x%02x%02x%02x",q2[0],q2[1],q2[2],q2[3],q2[4],q2[5]);
    bf_gdt_add_item(gdt,0, p2);

    struct bloom_filter *result = bf_gdt_check(gdt,p2);
    if(!result) {
#ifdef __KERNEL__
        printk("No match word \"%s\"\n", p2);
#else
        printf("len=%u,No match word \"%s\"\n",strlen(p2), p2);
#endif
    } else {
#ifdef __KERNEL__
        printk("[Match] word \"%s\" in bf %u\n", p2,result->bf_id);
#else
        printf("[Match] word \"%s\" in bf %u\n", p2,result->bf_id);
#endif
    }

    bf_gdt_destroy(gdt);
    return 0;
}

#ifdef __KERNEL__
void __exit end(void)
{
    printk("Unload module successful.\n");
    return;
}

MODULE_LICENSE("GPL");
MODULE_AUTHOR("author");

module_init(start);
module_exit(end);
#endif
