/* Load the deployed library without an SDK client's transitive dependencies. */
#include <dlfcn.h>
#include <stdio.h>

int main(int argc, char **argv)
{
    if (argc != 2)
        return 2;
    void *library = dlopen(argv[1], RTLD_NOW | RTLD_LOCAL);
    if (!library) {
        fprintf(stderr, "%s\n", dlerror());
        return 1;
    }
    if (!dlsym(library, "sai_api_query"))
        return 3;
    puts("Standalone DASH runtime load passed");
    return dlclose(library) != 0;
}
