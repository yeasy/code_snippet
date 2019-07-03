#include<stdio.h>

void main(){

    FILE* f_gid = fopen("/tmp/lc_gid.dat","r");
    unsigned int gid = 0;
    if(f_gid != NULL) {
        fscanf(f_gid,"%u",&gid);
        //fread(&gid,sizeof(unsigned int),1,f_gid);
        printf("ovsd bf_gdt_init with outside id=%u\n",gid);
        fclose(f_gid);
    } else {
        return;
    }
}
