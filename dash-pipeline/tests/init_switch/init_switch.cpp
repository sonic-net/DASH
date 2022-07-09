#include <iostream>
#include "utils.h"

/*
   Run this program to indirectly cause simple_switch_grpc to load its P4 pipeline
 */
int main(int argc, char **argv)
{
    // Make one benign call into libsai; it will force library load and
    // invoke static lib initializer Init() which calls SetForwardingPipelineConfigRequest()
    GetDeviceId();
    std::cout << "Switch is initialized." << std::endl;

    return 0;
}
