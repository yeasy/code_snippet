#include<stdio.h>

#define SHIFT 5  //64-bit os should change this to 6
#define WORD_LEN 32 //64-bit os should change this to 64
#define MASK 0x1f
#define N 100000 //length of bitmap 

int a[1 + N/WORD_LEN];//memory allocation

//set the bit to 1
void set(int i) {
    a[i>>SHIFT] |=  (1<<(i & MASK));   
}  

//clear the bit to 0
void clear(int i) {
    a[i>>SHIFT] &= ~(1<<(i & MASK));   
}

//test if the bit is 1
int  test(int i){
    return a[i>>SHIFT] & (1<<(i & MASK));   
}

int main()  {  
    int i;
    for (i = 0; i < N; i++)  
        clear(i);
    printf("Please input the bit ids (ctrl+d to finish):", i);  
    while (scanf("%d", &i) != EOF)  
        set(i);
    printf("The bit set: ");  
    for (i = 0; i < N; i++)  
        if (test(i))  
            printf("%d ", i);  
    printf("\n");  
    return 0;
}
