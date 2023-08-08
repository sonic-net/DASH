#include "utils.h"

#include <iostream>

// Run this program to indirectly cause simple_switch_grpc to load its P4 pipeline

int main(int argc, char **argv)
{
    // try initialize SAI api, this will load sai library and initialize P4 GRPC

    sai_status_t status = sai_api_initialize(0, nullptr);

    if (status == SAI_STATUS_SUCCESS)
    {
        std::cout << "sai_api_initialize success" << std::endl;

        return 0;
    }

    std::cout << "sai_api_initialize failed: " << status << std::endl;

    return 1;
}
