#include "config.h"
#include "logger.h"
#include "saidash.h"

#include <cstdlib>
#include <sstream>

using namespace dash;

Config::Config():
            m_grpcTarget(DEFAULT_GRPC_TARGET),
            m_pipelineJson(DEFAULT_PIPELINE_JSON),
            m_pipelineProto(DEFAULT_PIPELINE_PROTO),
            m_deviceId(DEFAULT_DEVICE_ID),
            m_bmv2NumPorts(DEFAULT_BMV2_NUM_PORTS)
{
    DASH_LOG_ENTER();

    // empty intentionally
}

std::shared_ptr<Config> Config::getDefaultConfig()
{
    DASH_LOG_ENTER();

    return std::make_shared<Config>();
}

std::shared_ptr<Config> Config::getConfig(
        const sai_service_method_table_t* serviceMethodTable)
{
    DASH_LOG_ENTER();

    auto cfg = getDefaultConfig();

    if (serviceMethodTable == nullptr)
    {
        DASH_LOG_NOTICE("service method table is null, returning default config");

        return cfg;
    }

    if (serviceMethodTable->profile_get_value == nullptr)
    {
        DASH_LOG_NOTICE("profile_get_value member is null, returning default config");

        return cfg;
    }

    auto grpcTarget = serviceMethodTable->profile_get_value(0, SAI_KEY_DASH_GRPC_TARGET);

    if (grpcTarget)
    {
        DASH_LOG_NOTICE("%s: %s", SAI_KEY_DASH_GRPC_TARGET, grpcTarget);

        cfg->m_grpcTarget = grpcTarget;
    }

    auto pipelineJson = serviceMethodTable->profile_get_value(0, SAI_KEY_DASH_PIPELINE_JSON);

    if (pipelineJson)
    {
        DASH_LOG_NOTICE("%s: %s", SAI_KEY_DASH_PIPELINE_JSON, pipelineJson);

        cfg->m_pipelineJson = pipelineJson;
    }

    auto pipelineProto = serviceMethodTable->profile_get_value(0, SAI_KEY_DASH_PIPELINE_PROTO);

    if (pipelineProto)
    {
        DASH_LOG_NOTICE("%s: %s", SAI_KEY_DASH_PIPELINE_JSON, pipelineProto);

        cfg->m_pipelineProto = pipelineProto;
    }

    auto deviceId = serviceMethodTable->profile_get_value(0, SAI_KEY_DASH_DEVICE_ID);

    if (deviceId)
    {
        int devId = atoi(deviceId);

        cfg->m_deviceId = devId;

        DASH_LOG_NOTICE("%s: %s (%d)", SAI_KEY_DASH_DEVICE_ID, deviceId, devId);
    }

    auto numPorts = serviceMethodTable->profile_get_value(0, SAI_KEY_DASH_BMV2_NUM_PORTS);

    if (numPorts)
    {
        uint32_t num = (uint32_t)atoi(numPorts);

        if (num > MAX_BMV2_NUM_PORTS)
        {
            DASH_LOG_ERROR("%s: %s (%u > %u), setting to default %u",
                    SAI_KEY_DASH_BMV2_NUM_PORTS,
                    numPorts,
                    num,
                    MAX_BMV2_NUM_PORTS,
                    DEFAULT_BMV2_NUM_PORTS);

            num = DEFAULT_BMV2_NUM_PORTS;
        }

        cfg->m_bmv2NumPorts = num;

        DASH_LOG_NOTICE("%s: %s (%u)", SAI_KEY_DASH_BMV2_NUM_PORTS, numPorts, num);
    }

    return cfg;
}

std::string Config::getConfigString() const
{
    DASH_LOG_ENTER();

    std::stringstream ss;

    ss << " GrpcTarget=" << m_grpcTarget;
    ss << " PipelineJson=" << m_pipelineJson;
    ss << " PipelineProto=" << m_pipelineProto;
    ss << " DeviceId=" << m_deviceId;
    ss << " Bmv2NumPorts=" << m_bmv2NumPorts;

    return ss.str();
}
