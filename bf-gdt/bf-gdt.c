/*
 * Copyright (c) 2007-2012 IBM CRL.
 *
 * This program is free software; you can redistribute it and/or
 * modify it under the terms of version 2 of the GNU General Public
 * License as published by the Free Software Foundation.
 *
 * This program is distributed in the hope that it will be useful, but
 * WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
 * General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA
 * 02110-1301, USA
 */

#ifdef __KERNEL__
#include<linux/slab.h>
#include<linux/module.h>
#include<linux/init.h>
#include<linux/kernel.h>
#else
#include<stdarg.h>
#include<stdlib.h>
#endif

#include "bf-gdt.h"

#define SETBIT(array, n) (array[n/sizeof(char)] |= (1<<(n%sizeof(char))))
#define GETBIT(array, n) (array[n/sizeof(char)] & (1<<(n%sizeof(char))))

/**
 * Init an empty bf_gdt
 * @param gid: the group id
 * @return: Pointer to the created bf_gdt. NULL if failed.
 */
struct bf_gdt *bf_gdt_init(u32 gid)
{
    struct bf_gdt *gdt;
#ifdef __KERNEL__
    if(!(gdt=kmalloc(sizeof(struct bf_gdt),GFP_KERNEL))) 
#else
    if(!(gdt=malloc(sizeof(struct bf_gdt)))) 
#endif
    {
        /*printk("Error in kmalloc gdt\n");*/
        return NULL;
    }
#ifdef __KERNEL__
    if(!(gdt->bf_array=kmalloc(BF_GDT_MAX_FILTERS*sizeof(struct bloom_filter*),GFP_KERNEL))) 
#else
    if(!(gdt->bf_array=malloc(BF_GDT_MAX_FILTERS*sizeof(struct bloom_filter*)))) 
#endif
    {
        /*printk("Error in kmalloc gdt\n");*/
        return NULL;
    }

    gdt->gid = gid;
    gdt->nbf = 0;

    return gdt;
}

/**
 * Create and add a new bloom_filter into the given gdt
 * @param gdt: the gdt to update
 * @param port_no: the port_no of the new bloom_filter
 * @param len: the len of the new bloom_filter
 * @return: Pointer to the created bloom_filter. NULL if failed.
 */
struct bloom_filter *bf_gdt_add_filter(struct bf_gdt *gdt, u16 port_no, u32 len)
{
    if (!gdt) {
        return NULL;
    }
    struct bloom_filter *bf = bf_create(gdt->nbf,len,port_no,2);
    if (bf) {
        if(gdt->nbf < BF_GDT_MAX_FILTERS) {
            gdt->bf_array[gdt->nbf++] = bf;
            return bf;
        } else {
            bf_destroy(bf);
        }
    }
    return NULL;
}

/**
 * destroy a bf_gdt.
 * @param gdt: the bf_gdt to destroy.
 */
int bf_gdt_destroy(struct bf_gdt *gdt)
{
    if (gdt->bf_array) {
        u32 i = 0;
        for (i=0;i<gdt->nbf;i++){
            bf_destroy(gdt->bf_array[i]);
        }
    }
#ifdef __KERNEL__
    if (gdt->bf_array)
        kfree(gdt->bf_array);
    if (gdt)
        kfree(gdt);
#else
    if (gdt->bf_array)
        free(gdt->bf_array);
    if (gdt)
        free(gdt);
#endif
    return 0;
}

/**
 * add a new string to gdt's some bf
 * @param gdt: the bf_gdt to update
 * @param bf_id: the dp's content updated
 * @param s: the string to add
 */
int bf_gdt_add_item(struct bf_gdt *gdt, u32 bf_id, const char *s)
{
    if (gdt && gdt->nbf>bf_id && gdt->bf_array) {
        bf_add(gdt->bf_array[bf_id],s);
    }

    return 0;
}

/**
 * test if s is in gdt-gdt.
 * @param gdt: the bf_gdt to test
 * @param s: the string to test
 * @return the bf if true
 */
struct bloom_filter *bf_gdt_check(struct bf_gdt *gdt, const char *s)
{
    u32 i;
    if (gdt && gdt->bf_array) {
        for(i=0; i<gdt->nbf; ++i) {
            if(bf_check(gdt->bf_array[i],s)) return gdt->bf_array[i];
        }
    }

    return NULL;
}
