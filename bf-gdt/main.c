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

    bf_gdt_add_item(gdt,0, "080027abb6a5");
    bf_gdt_add_item(gdt,1, "world");

    char *p="0a0027000001";
    struct bloom_filter *result = bf_gdt_check(gdt,p);
    if(!result) {
#ifdef __KERNEL__
        printk("No match word \"%s\"\n", p);
#else
        printf("No match word \"%s\"\n", p);
#endif
    } else {
#ifdef __KERNEL__
        printk("[Match] word \"%s\" in bf %u\n", p,result->bf_id);
#else
        printf("[Match] word \"%s\" in bf %u\n", p,result->bf_id);
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
