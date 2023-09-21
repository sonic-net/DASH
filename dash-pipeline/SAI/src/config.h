#pragma once

extern "C" {
#include <sai.h>
}

#include <string>
#include <memory>

namespace dash
{
    constexpr char DEFAULT_GRPC_TARGET[] = "0.0.0.0:9559";

    constexpr char DEFAULT_PIPELINE_JSON[] = "/etc/dash/dash_pipeline.json";

    constexpr char DEFAULT_PIPELINE_PROTO[] = "/etc/dash/dash_pipeline_p4rt.txt";

    constexpr int DEFAULT_DEVICE_ID = 0;

    constexpr uint32_t DEFAULT_BMV2_NUM_PORTS = 2;

    constexpr uint32_t MAX_BMV2_NUM_PORTS = 64;

    class Config
    {
        public:

            Config();
            ~Config() = default;

        public:

            static std::shared_ptr<Config> getDefaultConfig();

            static std::shared_ptr<Config> getConfig(
                    const sai_service_method_table_t* serviceMethodTable);

            std::string getConfigString() const;

        public:

            std::string m_grpcTarget;

            std::string m_pipelineJson;

            std::string m_pipelineProto;

            int m_deviceId;

            uint32_t m_bmv2NumPorts;
    };
}
