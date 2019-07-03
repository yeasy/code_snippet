#include <stdio.h>
#include <getopt.h>

int main(int argc, char *argv[])
{
    char *l_opt_arg;
    char* const short_options = "vn:";
    struct option long_options[] = {
        {"version",0, NULL,'v'},
        {"name",1, NULL,'n'},
        {0,0,0,0},
    };
    int c;
    while((c = getopt_long(argc, argv, short_options, long_options, NULL)) != -1)
    {
        switch (c) {
            case 'v':
                printf("The version is 0x1.\n");
                break;
            case 'n':
                l_opt_arg = optarg;
                printf("The name input is %s!\n", l_opt_arg);
                break;
        }
    }
    return 0;
}
