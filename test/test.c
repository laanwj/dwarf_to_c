/* gcc test.c -g -o test */
#include <stdio.h>
enum Dier
{
    AAP,
    ZEEHOND
};
typedef enum Dier DierEnum;
typedef enum 
{
    ANON1 = 2
} AnonEnum;
struct teststruct
{
    int a:10;
    int b:10;
    int c;
    char d;
    void *e;
    void **f;
    void *g;
    const char *h;
    /* const void *i;  causes errors */
    enum Dier i;
    DierEnum j;
    int (*the_hook)(int bu);
    int array[4];
    int *pointers[5];
    int (*iii[5])(unsigned long long);
    AnonEnum ntest;
};
static inline __attribute__((always_inline)) int boe(int x)
{
    printf("Hoi! %i\n", x);
}

int main()
{
    struct teststruct t;
    t.a = 3;
    printf("%i\n", t.b);
    boe(t.b);
    return 0;
}

