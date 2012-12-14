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

#ifndef BF_H
#define BF_H

/* only for userspace compatibility */
#ifndef __KERNEL__
typedef unsigned int u32;
typedef unsigned short u16;
typedef unsigned char u8;
#endif

typedef unsigned int (*hashfunc_t)(const char *);

struct bloom_filter{
    u32 bf_id; /*id*/
    u32 len; /*length of the bit array*/
    u16 port_no; /*how to reach the switch*/
    u8 *array; /*the bit array*/
    u32 nfuncs; /*number of hash functions*/
    hashfunc_t *funcs; /*hash functions array*/
};

u32 sax_hash(const char *key);
u32 sdbm_hash(const char *key);

struct bloom_filter *bf_create(u32 bf_id, u32 len, u16 port_no, u32 nfuncs); 
int bf_destroy(struct bloom_filter *bf);
int bf_add(struct bloom_filter *bf, const char *s);
int bf_check(struct bloom_filter *bf, const char *s);
int bf_set_array(struct bloom_filter *bf, const u8 *array, u32 len);

#endif
