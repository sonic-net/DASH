#include "dashsai.h"

extern "C" {
#include "saimetadata.h"
}

#include <cstdlib>

using namespace dash;
using namespace dash::utils;

#define DASH_BMV2_CPU_QOS_NUMBER_OF_QUEUES 0

#define DASH_CHECK_API_INITIALIZED()                                        \
    if (!m_apiInitialized) {                                                \
        DASH_LOG_ERROR("%s: api not initialized", __PRETTY_FUNCTION__);     \
        return SAI_STATUS_FAILURE; }

/**
 * @def DASH_USE_NOT_SUPPORTED
 *
 * Name of environment variable, when set to any value, will return proper
 * SAI_STATUS_NOT_SUPPORTED on switch/port GET api.
 *
 * Currently because of limitation of saithrift, GET on switch/port is
 * returning SAI_STATUS_SUCCESS on not implemented attribute.
 *
 * TODO FIXME needs to be addressed in saithrift.
 *
 * This is temporary workaround for syncd, it should be removed when fixed in saithrift.
 */
#define DASH_USE_NOT_SUPPORTED "DASH_USE_NOT_SUPPORTED"

#define MUTEX std::lock_guard<std::mutex> _lock(m_tableLock);

DashSai::DashSai():
    m_apiInitialized(false)
{
    DASH_LOG_ENTER();

    // TODO move to switch state

    m_switchId = SAI_OBJECT_TYPE_NULL;
    m_defaultCpuPortId = SAI_OBJECT_TYPE_NULL;
    m_defaultVlanId = SAI_OBJECT_TYPE_NULL;
    m_defaultVrfId = SAI_OBJECT_TYPE_NULL;
    m_default1QBridgeId = SAI_OBJECT_TYPE_NULL;
    m_defaultTrapGroup = SAI_OBJECT_TYPE_NULL;
}

DashSai::~DashSai()
{
    DASH_LOG_ENTER();

    if (m_apiInitialized)
    {
        apiUninitialize();
    }
}

sai_status_t DashSai::apiInitialize(
        _In_ uint64_t flags,
        _In_ const sai_service_method_table_t *services)
{
    DASH_LOG_ENTER();

    if (m_apiInitialized)
    {
        DASH_LOG_ERROR("api already initialized");

        return SAI_STATUS_FAILURE;
    }

    DASH_LOG_NOTICE("env %s set to: %s", DASH_USE_NOT_SUPPORTED, getenv(DASH_USE_NOT_SUPPORTED));

    m_serviceMethodTable = services;

    m_cfg = dash::Config::getConfig(services);

    DASH_LOG_NOTICE("config: %s", m_cfg->getConfigString().c_str());

    const grpc::string grpcTarget = m_cfg->m_grpcTarget;
    const char* test_json = m_cfg->m_pipelineJson.c_str();
    const char* test_proto_json = m_cfg->m_pipelineProto.c_str();

    DASH_LOG_NOTICE("GRPC call SetForwardingPipelineConfig %s => %s, %s", grpcTarget.c_str(), test_json, test_proto_json);

    auto p4info = parse_p4info(test_proto_json);

    if (p4info == nullptr)
    {
        DASH_LOG_ERROR("failed to parse p4info: %s", test_proto_json);

        return SAI_STATUS_FAILURE;
    }

    auto set_election_id = [](p4::v1::Uint128 *election_id)
    {
        election_id->set_high(0);
        election_id->set_low(1);
    };

    grpc::ClientContext stream_context;

    m_grpcChannel = grpc::CreateChannel(grpcTarget, grpc::InsecureChannelCredentials());

    m_stub = p4::v1::P4Runtime::NewStub(m_grpcChannel);

    auto stream = m_stub->StreamChannel(&stream_context);

    {
        p4::v1::StreamMessageRequest request;
        auto arbitration = request.mutable_arbitration();
        arbitration->set_device_id(m_cfg->m_deviceId);
        set_election_id(arbitration->mutable_election_id());
        stream->Write(request);
        p4::v1::StreamMessageResponse response;
        stream->Read(&response);

        if (response.update_case() != p4::v1::StreamMessageResponse::kArbitration)
        {
            DASH_LOG_ERROR("FATAL: response: %d, expected %d (p4::v1::StreamMessageResponse::kArbitration)",
                    response.update_case(),
                    p4::v1::StreamMessageResponse::kArbitration);

            return SAI_STATUS_FAILURE;
        }

        if (response.arbitration().status().code() != ::google::rpc::Code::OK)
        {
            DASH_LOG_ERROR("FATAL: arbitration status: %d, expected: %d (::google::rpc::Code::OK)",
                    response.arbitration().status().code(),
                    ::google::rpc::Code::OK);

            return SAI_STATUS_FAILURE;
        }
    }

    {
        p4::v1::SetForwardingPipelineConfigRequest request;
        request.set_device_id(m_cfg->m_deviceId);
        request.set_action(
                p4::v1::SetForwardingPipelineConfigRequest_Action_VERIFY_AND_COMMIT);
        set_election_id(request.mutable_election_id());
        auto config = request.mutable_config();
        config->set_allocated_p4info(p4info.get());

        std::ifstream istream(test_json);

        if (!istream.good())
        {
            DASH_LOG_ERROR("failed to open: %s", test_json);

            return SAI_STATUS_FAILURE;
        }

        config->mutable_p4_device_config()->assign(
                (std::istreambuf_iterator<char>(istream)),
                 std::istreambuf_iterator<char>());

        p4::v1::SetForwardingPipelineConfigResponse rep;
        grpc::ClientContext context;

        auto status = m_stub->SetForwardingPipelineConfig(&context, request, &rep);

        if (!status.ok())
        {
            DASH_LOG_ERROR("FATAL: SetForwardingPipelineConfig failed, error code: %d", status.error_code());

            return SAI_STATUS_FAILURE;
        }

        config->release_p4info();
    }

    m_objectIdManager = std::make_shared<ObjectIdManager>();

    m_apiInitialized = true;

    return SAI_STATUS_SUCCESS;
}

sai_status_t DashSai::apiUninitialize(void)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    m_cfg = nullptr;

    m_portList.clear(); // TODO move to switch state class

    m_tableEntryMap.clear();

    m_grpcChannel = nullptr;

    m_stub = nullptr;

    m_apiInitialized = false;

    m_serviceMethodTable = nullptr;

    m_objectIdManager = nullptr;

    return SAI_STATUS_SUCCESS;
}

sai_object_type_t DashSai::objectTypeQuery(
        _In_ sai_object_id_t object_id)
{
    DASH_LOG_ENTER();

    if (!m_apiInitialized)
    {
        DASH_LOG_ERROR("api not initialized");

        return SAI_OBJECT_TYPE_NULL;
    }

    return m_objectIdManager->objectTypeQuery(object_id);
}

sai_object_id_t DashSai::switchIdQuery(
        _In_ sai_object_id_t object_id)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    return m_objectIdManager->switchIdQuery(object_id);
}

sai_status_t DashSai::createSwitch(
        _Out_ sai_object_id_t *switch_id,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    std::string hardwareInfo;

    for (uint32_t i = 0; i < attr_count; i++)
    {
        auto *md = sai_metadata_get_attr_metadata(SAI_OBJECT_TYPE_SWITCH, attr_list[i].id);

        const char* attrName = md ? md->attridname : "unknown";

        DASH_LOG_WARN("attr id %d %s is NOT IMPLEMENTED, ignored", attr_list[i].id, attrName);

        if (attr_list[i].id == SAI_SWITCH_ATTR_SWITCH_HARDWARE_INFO)
        {
            DASH_LOG_WARN("attr SAI_SWITCH_ATTR_SWITCH_HARDWARE_INFO specified, but ignored, set to '%s', FIXME",
                    hardwareInfo.c_str());
        }
    }

    // TODO add switch state and init switch method

    m_switchId = m_objectIdManager->allocateNewSwitchObjectId(hardwareInfo);

    if (m_switchId == SAI_NULL_OBJECT_ID)
    {
        DASH_LOG_ERROR("switch OID allocation failed");

        return SAI_STATUS_FAILURE;
    }

    // TODO move to switch state

    m_defaultCpuPortId = m_objectIdManager->allocateNewObjectId(SAI_OBJECT_TYPE_PORT, m_switchId);
    m_defaultVlanId = m_objectIdManager->allocateNewObjectId(SAI_OBJECT_TYPE_VLAN, m_switchId);
    m_defaultVrfId = m_objectIdManager->allocateNewObjectId(SAI_OBJECT_TYPE_VIRTUAL_ROUTER, m_switchId);
    m_default1QBridgeId = m_objectIdManager->allocateNewObjectId(SAI_OBJECT_TYPE_BRIDGE, m_switchId);
    m_defaultTrapGroup = m_objectIdManager->allocateNewObjectId(SAI_OBJECT_TYPE_HOSTIF_TRAP_GROUP, m_switchId);

    m_portList.clear();

    for (uint32_t i = 1; i <= m_cfg->m_bmv2NumPorts; i++)
    {
        // TODO in switch state must be internally calling create on this object
        m_portList.push_back(m_objectIdManager->allocateNewObjectId(SAI_OBJECT_TYPE_PORT, m_switchId));
    }

    *switch_id = m_switchId;

    DASH_LOG_NOTICE("created switch id: 0x%lx", *switch_id);

    return SAI_STATUS_SUCCESS;
}

sai_status_t DashSai::removeSwitch(
        _In_ sai_object_id_t switch_id)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    if (switch_id != m_switchId)
    {
        DASH_LOG_ERROR("invalid switch_id: 0x%lx, switch_id", switch_id);

        return SAI_STATUS_INVALID_PARAMETER;
    }

    m_objectIdManager->releaseObjectId(switch_id);

    // dummy switch remove

    DASH_LOG_NOTICE("removing switch: 0x%lx", switch_id);

    return SAI_STATUS_SUCCESS;
}

sai_status_t DashSai::setSwitchAttribute(
        _In_ sai_object_id_t switch_id,
        _In_ const sai_attribute_t *attr)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    auto *md = sai_metadata_get_attr_metadata(SAI_OBJECT_TYPE_SWITCH, attr->id);

    const char* attrName = md ? md->attridname : "unknown";

    switch (attr->id)
    {
        case SAI_SWITCH_ATTR_SWITCH_STATE_CHANGE_NOTIFY:
        case SAI_SWITCH_ATTR_SHUTDOWN_REQUEST_NOTIFY:
        case SAI_SWITCH_ATTR_FDB_EVENT_NOTIFY:
        case SAI_SWITCH_ATTR_NAT_EVENT_NOTIFY:
        case SAI_SWITCH_ATTR_PORT_STATE_CHANGE_NOTIFY:
        case SAI_SWITCH_ATTR_QUEUE_PFC_DEADLOCK_NOTIFY:
        case SAI_SWITCH_ATTR_BFD_SESSION_STATE_CHANGE_NOTIFY:

            DASH_LOG_NOTICE("setting dummy notification callback (attr id: %d %s)", attr->id, attrName);

            return SAI_STATUS_SUCCESS;

        default:

            DASH_LOG_ERROR("set attr %d %s NOT IMPLEMENTED", attr->id, attrName);

            return SAI_STATUS_NOT_IMPLEMENTED;
    }
}

sai_status_t DashSai::getSwitchAttribute(
        _In_ sai_object_id_t switch_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    sai_attribute_t *attr = attr_list;

    for (uint32_t i = 0; i < attr_count ; i++, attr++)
    {
        auto *md = sai_metadata_get_attr_metadata(SAI_OBJECT_TYPE_SWITCH, attr->id);

        const char* attrName = md ? md->attridname : "unknown";

        switch(attr->id)
        {
            case SAI_SWITCH_ATTR_NUMBER_OF_ACTIVE_PORTS:

                attr->value.u32 = m_cfg->m_bmv2NumPorts;

                DASH_LOG_NOTICE("[%d] SAI_SWITCH_ATTR_NUMBER_OF_ACTIVE_PORTS = %d", i, attr->value.u32);

                break;

            case SAI_SWITCH_ATTR_PORT_LIST:

                attr->value.objlist.count = std::min(m_cfg->m_bmv2NumPorts, attr->value.objlist.count);

                for (size_t j = 0; j < attr->value.objlist.count; j++)
                {
                    attr->value.objlist.list[j] = m_portList.at(j);
                }

                DASH_LOG_NOTICE("[%d] SAI_SWITCH_ATTR_PORT_LIST = [%d objids]", i, m_cfg->m_bmv2NumPorts);

                break;

            case SAI_SWITCH_ATTR_DEFAULT_VLAN_ID:

                attr->value.oid = m_defaultVlanId;

                DASH_LOG_NOTICE("[%d] SAI_SWITCH_ATTR_DEFAULT_VLAN_ID = 0x%lx", i, attr->value.oid);

                break;

            case SAI_SWITCH_ATTR_DEFAULT_VIRTUAL_ROUTER_ID:

                attr->value.oid = m_defaultVrfId;

                DASH_LOG_NOTICE("[%d] SAI_SWITCH_ATTR_DEFAULT_VIRTUAL_ROUTER_ID = 0x%lx", i, attr->value.oid);

                break;

            case SAI_SWITCH_ATTR_DEFAULT_1Q_BRIDGE_ID:

                attr->value.oid = m_default1QBridgeId;

                DASH_LOG_NOTICE("[%d] SAI_SWITCH_ATTR_DEFAULT_1Q_BRIDGE_ID = 0x%lx", i, attr->value.oid);

                break;

            case SAI_SWITCH_ATTR_CPU_PORT:

                attr->value.oid = m_defaultCpuPortId;

                DASH_LOG_NOTICE("[%d] SAI_SWITCH_ATTR_CPU_PORT = 0x%lx", i, attr->value.oid);

                break;

            case SAI_SWITCH_ATTR_DEFAULT_TRAP_GROUP:

                attr->value.oid = m_defaultTrapGroup;

                DASH_LOG_NOTICE("[%d] SAI_SWITCH_ATTR_DEFAULT_TRAP_GROUP = 0x%lx", i, attr->value.oid);

                break;

            case SAI_SWITCH_ATTR_SRC_MAC_ADDRESS:

                // dummy mac address

                attr->value.mac[0] = 0x00;
                attr->value.mac[1] = 0x12;
                attr->value.mac[2] = 0x34;
                attr->value.mac[3] = 0x56;
                attr->value.mac[4] = 0x78;
                attr->value.mac[5] = 0x9A;

                break;

            default:

                if (getenv(DASH_USE_NOT_SUPPORTED))
                {
                    DASH_LOG_WARN("[%d] attr %d %s is NOT SUPPORTED", i, attr->id, attrName);

                    return SAI_STATUS_NOT_SUPPORTED;
                }

                DASH_LOG_WARN("[%d] attr %d %s is NOT SUPPORTED, but returning SAI_STATUS_SUCCESS", i, attr->id, attrName);

                memset(&attr->value, 0, sizeof(attr->value)); // clear potential caller garbage

                break; // TODO FIXME should return NOT SUPPORTED
        }
    }

    return SAI_STATUS_SUCCESS;
}

sai_status_t DashSai::getPortAttribute(
        _In_ sai_object_id_t port_id,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    sai_attribute_t *attr = attr_list;

    for (uint32_t i = 0; i < attr_count ; i++, attr++)
    {
        auto *md = sai_metadata_get_attr_metadata(SAI_OBJECT_TYPE_PORT, attr->id);

        const char* attrName = md ? md->attridname : "unknown";

        switch(attr->id)
        {
            case SAI_PORT_ATTR_QOS_NUMBER_OF_QUEUES:

                attr->value.u32 = DASH_BMV2_CPU_QOS_NUMBER_OF_QUEUES;

                DASH_LOG_NOTICE("[%d] SAI_PORT_ATTR_QOS_NUMBER_OF_QUEUES = %d", i, attr->value.u32);

                break;

            case SAI_PORT_ATTR_HW_LANE_LIST:

                // dummy hw lane list (required by syncd)

                attr->value.u32list.count = 1;
                attr->value.u32list.list[0] = (uint32_t)(port_id & 0xffff); // get index from port ID to make lanes unique

                break;

            case SAI_PORT_ATTR_OPER_STATUS:

                attr->value.s32 = SAI_PORT_OPER_STATUS_UP;

                DASH_LOG_NOTICE("[%d] setting SAI_PORT_ATTR_OPER_STATUS=SAI_PORT_OPER_STATUS_UP for port 0x%lx", i, port_id);

                break;

            case SAI_PORT_ATTR_PORT_VLAN_ID:

                attr->value.u16 = 1;

                DASH_LOG_NOTICE("[%d] setting SAI_PORT_ATTR_PORT_VLAN_ID=1 for port 0x%lx", i, port_id);

                break;

            default:

                if (getenv(DASH_USE_NOT_SUPPORTED))
                {
                    DASH_LOG_WARN("[%d] attr %d %s is NOT SUPPORTED", i, attr->id, attrName);

                    return SAI_STATUS_NOT_SUPPORTED;
                }

                DASH_LOG_WARN("[%d] attr %d %s is NOT SUPPORTED, but returning SAI_STATUS_SUCCESS", i, attr->id, attrName);

                memset(&attr->value, 0, sizeof(attr->value)); // clear potential caller garbage

                break; // TODO FIXME should return NOT SUPPORTED
        }
    }

    return SAI_STATUS_SUCCESS;
}

// private helper methods

std::shared_ptr<p4::config::v1::P4Info> DashSai::parse_p4info(
        _In_ const char *path)
{
    DASH_LOG_ENTER();

    std::shared_ptr<p4::config::v1::P4Info> p4info = std::make_shared<p4::config::v1::P4Info>();

    std::ifstream istream(path);

    if (istream.good())
    {
        google::protobuf::io::IstreamInputStream is(&istream);
        google::protobuf::TextFormat::Parse(&is, p4info.get());

        return p4info;
    }

    DASH_LOG_ERROR("failed to open: %s", path);

    return nullptr;
}

std::string DashSai::updateTypeStr(
        _In_ p4::v1::Update_Type updateType)
{
    DASH_LOG_ENTER();

    const google::protobuf::EnumDescriptor *descriptor = p4::v1::Update_Type_descriptor();

    return descriptor->FindValueByNumber(updateType)->name();
}

// helper methods

grpc::StatusCode DashSai::mutateTableEntry(
        _In_ std::shared_ptr<p4::v1::TableEntry> entry,
        _In_ p4::v1::Update_Type updateType)
{
    DASH_LOG_ENTER();

    if (!m_apiInitialized)
    {
        DASH_LOG_ERROR("api not initialized");

        return grpc::StatusCode::CANCELLED;
    }

    p4::v1::WriteRequest request;

    request.set_device_id(m_cfg->m_deviceId);

    auto update = request.add_updates();

    update->set_type(updateType);

    auto entity = update->mutable_entity();

    entity->set_allocated_table_entry(entry.get());

    p4::v1::WriteResponse rep;

    grpc::ClientContext context;

    grpc::Status status = m_stub->Write(&context, request, &rep);

    if (status.ok())
    {
        DASH_LOG_NOTICE("GRPC call Write::%s OK %s", updateTypeStr(updateType).c_str(), entry->ShortDebugString().c_str());
    }
    else
    {
        DASH_LOG_ERROR("GRPC ERROR[%d]: %s, %s", status.error_code(), status.error_message().c_str(), status.error_details().c_str());
        DASH_LOG_ERROR("GRPC call Write::%s ERROR: %s", updateTypeStr(updateType).c_str(), entry->ShortDebugString().c_str());
    }

    //MILIND?? What is this? reference release? memory release?
    entity->release_table_entry();

    return status.error_code();
}

grpc::StatusCode DashSai::readTableEntry(
        _Inout_ std::shared_ptr<p4::v1::TableEntry> entry)
{
    DASH_LOG_ENTER();

    if (!m_apiInitialized)
    {
        DASH_LOG_ERROR("api not initialized");

        return grpc::StatusCode::CANCELLED;
    }

    p4::v1::ReadRequest request;

    request.set_device_id(m_cfg->m_deviceId);

    auto entity = request.add_entities();

    entity->set_allocated_table_entry(entry.get());

    grpc::ClientContext context;

    auto client_reader = m_stub->Read(&context, request);
    assert(client_reader);

    p4::v1::ReadResponse rep;
    if (client_reader->Read(&rep)) {
        assert(rep.entities_size() == 1);
        entity->release_table_entry();
        entity = rep.mutable_entities(0);
        entry->CopyFrom(entity->table_entry());
    }
    else {
        entity->release_table_entry();
    }

    auto status = client_reader->Finish();

    if (status.ok()) {
        DASH_LOG_NOTICE("GRPC call Read OK %s", entry->ShortDebugString().c_str());
    }
    else {
        DASH_LOG_ERROR("GRPC ERROR[%d]: %s, %s", status.error_code(), status.error_message().c_str(), status.error_details().c_str());
    }

    return status.error_code();
}

bool DashSai::insertInTable(
        _In_ std::shared_ptr<p4::v1::TableEntry> entry,
        _In_ sai_object_id_t objId)
{
    DASH_LOG_ENTER();

    if (!m_apiInitialized)
    {
        DASH_LOG_ERROR("api not initialized");

        return false;
    }

    if (objId == SAI_NULL_OBJECT_ID)
    {
        DASH_LOG_ERROR("objId is NULL");

        return false;
    }

    auto retCode = mutateTableEntry(entry, p4::v1::Update_Type_INSERT);

    if (grpc::StatusCode::OK != retCode)
    {
        return false;
    }

    MUTEX;

    m_tableEntryMap.insert(std::make_pair(objId, entry));

    return true;
}

// TODO needs to be converted to create (with attributes)
sai_object_id_t DashSai::getNextObjectId(
        _In_ sai_object_type_t objectType)
{
    DASH_LOG_ENTER();

    if (!m_apiInitialized)
    {
        DASH_LOG_ERROR("api not initialized");

        return SAI_NULL_OBJECT_ID;
    }

    if (m_switchId == SAI_NULL_OBJECT_ID)
    {
        DASH_LOG_ERROR("switch is not created, create switch first");

        return SAI_NULL_OBJECT_ID;
    }

    return m_objectIdManager->allocateNewObjectId(objectType, m_switchId);
}

bool DashSai::removeFromTable(
        _In_ sai_object_id_t id)
{
    DASH_LOG_ENTER();

    if (!m_apiInitialized)
    {
        DASH_LOG_ERROR("api not initialized");

        return false;
    }

    MUTEX;

    auto range = m_tableEntryMap.equal_range(id);

    if (range.first == range.second)
    {
        DASH_LOG_ERROR("id: 0x%lx not present in the table for deletion!", id);

        return false;
    }

    grpc::StatusCode retCode = grpc::StatusCode::OK;

    for (auto itr = range.first; itr != range.second; ++itr)
    {
        auto entry = itr->second;
        auto tempRet = mutateTableEntry(entry, p4::v1::Update_Type_DELETE);

        if (grpc::StatusCode::OK != tempRet)
        {
            retCode = tempRet;
        }
    }

    m_tableEntryMap.erase(id);

    return retCode == grpc::StatusCode::OK;
}

bool DashSai::getFromTable(
        _In_ sai_object_id_t id,
        _Out_ std::shared_ptr<p4::v1::TableEntry> &entry)
{
    DASH_LOG_ENTER();

    if (!m_apiInitialized)
    {
        DASH_LOG_ERROR("api not initialized");

        return false;
    }

    MUTEX;

    auto range = m_tableEntryMap.equal_range(id);

    if (range.first == range.second)
    {
        DASH_LOG_ERROR("id: 0x%lx not present in the table for deletion!", id);

        return false;
    }

    for (auto itr = range.first; itr != range.second; ++itr)
    {
        entry = itr->second;
        return true;

    }

    return false;
}

// QUAD generic api implementation

sai_status_t DashSai::create(
        _In_ sai_object_type_t objectType,
        _Out_ sai_object_id_t* objectId,
        _In_ sai_object_id_t switchId,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    if (objectType == SAI_OBJECT_TYPE_SWITCH)
        return createSwitch(objectId, attr_count, attr_list);

    *objectId = m_objectIdManager->allocateNewObjectId(objectType, m_switchId);

    auto* ot = sai_metadata_get_object_type_info(objectType);

    const char* otName = ot ? ot->objecttypename : "unknown";

    DASH_LOG_WARN("creating dummy object for object type %d %s: 0x%lx", objectType, otName, *objectId);

    return SAI_STATUS_SUCCESS;
}

sai_status_t DashSai::remove(
        _In_ sai_object_type_t objectType,
        _In_ sai_object_id_t objectId)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    if (objectType == SAI_OBJECT_TYPE_SWITCH)
        return removeSwitch(objectId);

    DASH_LOG_WARN("dummy remove: 0x%lx", objectId);

    return SAI_STATUS_SUCCESS;
}

sai_status_t DashSai::set(
        _In_ sai_object_type_t objectType,
        _In_ sai_object_id_t objectId,
        _In_ const sai_attribute_t *attr)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    if (objectType == SAI_OBJECT_TYPE_SWITCH)
        return setSwitchAttribute(objectId, attr);

    auto *md = sai_metadata_get_attr_metadata(objectType, attr->id);

    const char* attrName = md ? md->attridname : "unknown";

    DASH_LOG_WARN("dummy set: 0x%lx, attr id: %d %s", objectId, attr->id, attrName);

    return SAI_STATUS_SUCCESS;
}

sai_status_t DashSai::get(
        _In_ sai_object_type_t objectType,
        _In_ sai_object_id_t objectId,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    if (objectType == SAI_OBJECT_TYPE_PORT)
        return getPortAttribute(objectId, attr_count, attr_list);

    if (objectType == SAI_OBJECT_TYPE_SWITCH)
        return getSwitchAttribute(objectId, attr_count, attr_list);

    auto* ot = sai_metadata_get_object_type_info(objectType);

    const char* otName = ot ? ot->objecttypename : "unknown";

    DASH_LOG_ERROR("not implemented for object type %d %s", objectType, otName);

    return SAI_STATUS_NOT_IMPLEMENTED;
}

/**
 * @brief Populate default attributes.
 *
 * Since BMv2 dont's support default attributes, we will add to existing
 * attributes all the ones that have default values, except those that
 * have valid only condition not met, since then BMv2 will fail.
 *
 * @objectType object type for list of attributes
 * @attr_count attributes count
 * @attr_list attributes list
 *
 * @return List of attributes with possible added attributes with default values.
 */
std::vector<sai_attribute_t> DashSai::populateDefaultAttributes(
        _In_ sai_object_type_t objectType,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();

    // populate existing attributes

    std::vector<sai_attribute_t> attrs(attr_list, attr_list + attr_count);

    auto* info = sai_metadata_get_object_type_info(objectType);

    if (info == nullptr)
    {
        DASH_LOG_ERROR("failed to get metadata info for object type %d", objectType);
        return attrs;
    }

    // iterate over all possible attributes

    for (size_t idx = 0; idx < info->attrmetadatalength; idx++)
    {
        auto* md = info->attrmetadata[idx];

        auto* attr = sai_metadata_get_attr_by_id(md->attrid, (uint32_t)attrs.size(), attrs.data());

        if (attr)
            continue;   // attribute already exists on current attribute list

        if (md->isconditional)
            continue;   // conditional attributes should be populated by user

        if (md->isreadonly)
            continue;   // can't be read only

        if (md->ismandatoryoncreate)
            continue;   // can't be mandatory on create

        if (md->defaultvaluetype == SAI_DEFAULT_VALUE_TYPE_NONE)
            continue;   // there is no default value

        if (md->isvalidonly)
        {
            bool haveActionAttribute = false;

            for (size_t i = 0; i < md->validonlylength; i++)
            {
                auto *condmd = sai_metadata_get_attr_metadata(objectType, md->validonly[i]->attrid);

                if (condmd && strstr(condmd->attridname, "_ATTR_ACTION"))
                {
                    haveActionAttribute = true;
                    break;
                }
            }

            if (haveActionAttribute == false)
            {
                // always set default attribute in this case, even if condition is not set
                // (see github discussion https://github.com/sonic-net/DASH/pull/547)
            }
            else if (sai_metadata_is_validonly_met(md, (uint32_t)attrs.size(), attrs.data()) == false)
            {
                // attribute is valid only, but condition is not met based on current attributes
                continue;
            }
        }

        if (md->defaultvaluetype == SAI_DEFAULT_VALUE_TYPE_CONST)
        {
            sai_attribute_t a;

            a.id = md->attrid;
            a.value = *md->defaultvalue;

            DASH_LOG_NOTICE("adding %s with default value", md->attridname);

            attrs.push_back(a);

        }
        else if (md->defaultvaluetype == SAI_DEFAULT_VALUE_TYPE_EMPTY_LIST)
        {
            sai_attribute_t a;

            a.id = md->attrid;
            a.value.objlist.count = 0;
            a.value.objlist.list = nullptr;

            DASH_LOG_NOTICE("adding %s with default value", md->attridname);

            attrs.push_back(a);
        }
        else
        {
            DASH_LOG_WARN("skipping default value for %s, default value type %d is not supported", md->attridname, md->defaultvaluetype);
        }
    }

    return attrs;
}

sai_status_t DashSai::bulk_create_objects(
    _In_ DashSai::sai_create_object_fn create_fn,
    _In_ sai_object_id_t switch_id,
    _In_ uint32_t object_count,
    _In_ const uint32_t *attr_count,
    _In_ const sai_attribute_t **attr_list,
    _In_ sai_bulk_op_error_mode_t mode,
    _Out_ sai_object_id_t *object_id,
    _Out_ sai_status_t *object_statuses)
{
    sai_status_t agg_status = SAI_STATUS_SUCCESS;

    for (uint32_t i = 0; i < object_count; i++)
    {
        object_statuses[i] = create_fn(&object_id[i], switch_id, attr_count[i], attr_list[i]);

        if (object_statuses[i] != SAI_STATUS_SUCCESS)
        {
            agg_status = SAI_STATUS_FAILURE;
        }

        if (agg_status == SAI_STATUS_FAILURE && mode == SAI_BULK_OP_ERROR_MODE_STOP_ON_ERROR)
        {
            return agg_status;
        }
    }

    return agg_status;
}

sai_status_t DashSai::bulk_remove_objects(
    _In_ DashSai::sai_remove_object_fn remove_fn,
    _In_ uint32_t object_count,
    _In_ const sai_object_id_t *object_id,
    _In_ sai_bulk_op_error_mode_t mode,
    _Out_ sai_status_t *object_statuses)
{
    sai_status_t agg_status = SAI_STATUS_SUCCESS;

    for (uint32_t i = 0; i < object_count; i++)
    {
        object_statuses[i] = remove_fn(object_id[i]);

        if (object_statuses[i] != SAI_STATUS_SUCCESS)
        {
            agg_status = SAI_STATUS_FAILURE;
        }

        if (agg_status == SAI_STATUS_FAILURE && mode == SAI_BULK_OP_ERROR_MODE_STOP_ON_ERROR)
        {
            return agg_status;
        }
    }

    return agg_status;
}

sai_status_t DashSai::create(
        _In_ const P4MetaTable &meta_table,
        _In_ sai_object_type_t objectType,
        _Out_ sai_object_id_t* objectId,
        _In_ sai_object_id_t switchId,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    auto attrs = DashSai::populateDefaultAttributes(objectType, attr_count, attr_list);
    attr_count = (uint32_t)attrs.size();
    attr_list = attrs.data();

    std::shared_ptr<p4::v1::TableEntry> matchActionEntry;
    matchActionEntry = std::make_shared<p4::v1::TableEntry>();
    matchActionEntry->set_table_id(meta_table.id);

    sai_object_id_t objId = getNextObjectId(objectType);
    if (objId == SAI_NULL_OBJECT_ID)
    {
        DASH_LOG_ERROR("getNextObjectId failed for OBJECT_TYPE %u", objectType);
        return SAI_STATUS_FAILURE;
    }

    if (auto meta_object_key = meta_table.get_meta_object_key()) {
        auto key_mf = matchActionEntry->add_match();
        auto key_mf_exact = key_mf->mutable_exact();

        key_mf->set_field_id(meta_object_key->id);
        u16SetVal((uint16_t)objId, key_mf_exact, 16);
    }

    pi_p4_id_t action_id = meta_table.find_action_id(attr_count, attr_list);
    if (!action_id) {
        DASH_LOG_ERROR("Not find p4 table action");
        return SAI_STATUS_FAILURE;
    }

    auto action = matchActionEntry->mutable_action()->mutable_action();
    action->set_action_id(action_id);

    for (uint32_t i = 0; i < attr_count; i++) {
        if (auto meta_param = meta_table.get_meta_action_param(action_id, attr_list[i].id)) {
            // attr in table action params
            set_attr_to_p4_action(meta_param, &attr_list[i], action);
        }
        else if (auto meta_key = meta_table.get_meta_key(attr_list[i].id)) {
            // attr in table keys
            set_attr_to_p4_match(meta_key, &attr_list[i], matchActionEntry);
        }
        else {
            // attr in extra fields
            set_attr_to_p4_misc(meta_table, &attr_list[i], matchActionEntry);
        }
    }

    if (insertInTable(matchActionEntry, objId)) {
        mutateSiblingTablesEntry(meta_table, matchActionEntry, p4::v1::Update_Type_INSERT, action_id);
        *objectId = objId;
        return SAI_STATUS_SUCCESS;
    }

    return SAI_STATUS_FAILURE;
}

sai_status_t DashSai::create(
        _In_ const P4MetaTable &meta_table,
        _In_ sai_object_type_t objectType,
        _Inout_ std::shared_ptr<p4::v1::TableEntry> matchActionEntry,
        _In_ uint32_t attr_count,
        _In_ const sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    auto attrs = DashSai::populateDefaultAttributes(objectType, attr_count, attr_list);
    attr_count = (uint32_t)attrs.size();
    attr_list = attrs.data();

    matchActionEntry->set_table_id(meta_table.id);

    pi_p4_id_t action_id = meta_table.find_action_id(attr_count, attr_list);
    if (!action_id) {
        DASH_LOG_ERROR("Not find p4 table action");
        return SAI_STATUS_FAILURE;
    }
    auto action = matchActionEntry->mutable_action()->mutable_action();
    action->set_action_id(action_id);

    for (uint32_t i = 0; i < attr_count; i++) {
        if (auto meta_param = meta_table.get_meta_action_param(action_id, attr_list[i].id)) {
            // attr in table action params
            set_attr_to_p4_action(meta_param, &attr_list[i], action);
        }
        else {
            // attr in extra fields
            set_attr_to_p4_misc(meta_table, &attr_list[i], matchActionEntry);
        }
    }

    auto ret = mutateTableEntry(matchActionEntry, p4::v1::Update_Type_INSERT);
    if (grpc::StatusCode::OK == ret) {
        mutateSiblingTablesEntry(meta_table, matchActionEntry, p4::v1::Update_Type_INSERT, action_id);
        return SAI_STATUS_SUCCESS;
    }

    return SAI_STATUS_FAILURE;
}

sai_status_t DashSai::remove(
        _In_ const P4MetaTable &meta_table,
        _In_ sai_object_id_t objectId)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    std::shared_ptr<p4::v1::TableEntry> matchActionEntry = nullptr;
    if (!getFromTable(objectId, matchActionEntry)) {
        return SAI_STATUS_FAILURE;
    }

    if (removeFromTable(objectId)) {
        mutateSiblingTablesEntry(meta_table, matchActionEntry, p4::v1::Update_Type_DELETE);
        return SAI_STATUS_SUCCESS;
    }

    return SAI_STATUS_FAILURE;
}

sai_status_t DashSai::remove(
        _In_ const P4MetaTable &meta_table,
        _Inout_ std::shared_ptr<p4::v1::TableEntry> matchActionEntry)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    auto ret = mutateTableEntry(matchActionEntry, p4::v1::Update_Type_DELETE);

    if (grpc::StatusCode::OK == ret) {
        mutateSiblingTablesEntry(meta_table, matchActionEntry, p4::v1::Update_Type_DELETE);
        return SAI_STATUS_SUCCESS;
    }

    return SAI_STATUS_FAILURE;
}

sai_status_t DashSai::set(
        _In_ const P4MetaTable &meta_table,
        _In_ sai_object_id_t objectId,
        _In_ const sai_attribute_t *attr)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    std::shared_ptr<p4::v1::TableEntry> matchActionEntry = nullptr;
    if (!getFromTable(objectId, matchActionEntry)) {
        return SAI_STATUS_FAILURE;
    }

    // Search attr in table action params
    auto action = matchActionEntry->mutable_action()->mutable_action();
    pi_p4_id_t action_id = action->action_id();
    auto meta_param = meta_table.get_meta_action_param(action_id, attr->id);
    if (meta_param) {
        auto pair_param = get_action_param_with_is_v6_flag_from_p4_table_entry(meta_param, matchActionEntry);
        if (pair_param.second) {
            set_attr_ipaddr_family_to_p4(attr->value, pair_param.second);
        }

        assert(pair_param.first);
        set_attr_value_to_p4(meta_param->field, meta_param->bitwidth, attr->value, pair_param.first);

        auto ret = mutateTableEntry(matchActionEntry, p4::v1::Update_Type_MODIFY);
        if (ret == grpc::StatusCode::OK) {
            mutateSiblingTablesEntry(meta_table, matchActionEntry, p4::v1::Update_Type_MODIFY, action_id);
        }
        return ret == grpc::StatusCode::OK ? SAI_STATUS_SUCCESS : SAI_STATUS_FAILURE;
    }

    // Search attr in table match fields
    auto meta_key = meta_table.get_meta_key(attr->id);
    if (meta_key) {
        std::shared_ptr<p4::v1::TableEntry> new_entry = std::make_shared<p4::v1::TableEntry>();
        new_entry->CopyFrom(*matchActionEntry);

        auto pair_key = get_match_pair_from_p4_table_entry(meta_key, new_entry);
        if (pair_key.second) {
            set_attr_ipaddr_family_to_p4(attr->value, pair_key.second->mutable_exact());
        }

        assert(pair_key.first);
        if (meta_key->match_type == "ternary" && string_ends_with(meta_key->name, "_MASK")) {
            set_attr_value_mask_to_p4_ternary(meta_key->field, meta_key->bitwidth, attr->value,
                     pair_key.first->mutable_ternary());
        }
        else {
            set_attr_value_to_p4_match(*meta_key, attr->value, pair_key.first);
        }

        removeFromTable(objectId);
        mutateSiblingTablesEntry(meta_table, matchActionEntry, p4::v1::Update_Type_DELETE);

        if (insertInTable(new_entry, objectId)) {
            mutateSiblingTablesEntry(meta_table, new_entry, p4::v1::Update_Type_INSERT, action_id);
            return SAI_STATUS_SUCCESS;
        }
    }

    return SAI_STATUS_FAILURE;
}

sai_status_t DashSai::set(
        _In_ const P4MetaTable &meta_table,
        _Inout_ std::shared_ptr<p4::v1::TableEntry> matchActionEntry,
        _In_ const sai_attribute_t *attr)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    if (grpc::StatusCode::OK != readTableEntry(matchActionEntry)) {
        return SAI_STATUS_FAILURE;
    }

    // Search attr in table action params
    auto action = matchActionEntry->mutable_action()->mutable_action();
    pi_p4_id_t action_id = action->action_id();
    auto meta_param = meta_table.get_meta_action_param(action_id, attr->id);
    if (meta_param) {
        auto pair_param = get_action_param_with_is_v6_flag_from_p4_table_entry(meta_param, matchActionEntry);
        if (pair_param.second) {
            set_attr_ipaddr_family_to_p4(attr->value, pair_param.second);
        }

        assert(pair_param.first);
        set_attr_value_to_p4(meta_param->field, meta_param->bitwidth, attr->value, pair_param.first);

        auto ret = mutateTableEntry(matchActionEntry, p4::v1::Update_Type_MODIFY);
        if (ret == grpc::StatusCode::OK) {
            mutateSiblingTablesEntry(meta_table, matchActionEntry, p4::v1::Update_Type_MODIFY, action_id);
        }
        return ret == grpc::StatusCode::OK ? SAI_STATUS_SUCCESS : SAI_STATUS_FAILURE;
    }

    return SAI_STATUS_FAILURE;
}

sai_status_t DashSai::get(
        _In_ const P4MetaTable &meta_table,
        _In_ sai_object_id_t objectId,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    std::shared_ptr<p4::v1::TableEntry> matchActionEntry = nullptr;
    if (!getFromTable(objectId, matchActionEntry)) {
        return SAI_STATUS_FAILURE;
    }

    auto action = matchActionEntry->mutable_action()->mutable_action();
    pi_p4_id_t action_id = action->action_id();

    for (uint32_t i = 0; i < attr_count; i++) {
        if (auto meta_param = meta_table.get_meta_action_param(action_id, attr_list[i].id)) {
            // attr in table action params
            auto pair_param = get_action_param_with_is_v6_flag_from_p4_table_entry(meta_param, matchActionEntry);
            if (pair_param.second) {
                get_attr_ipaddr_family_from_p4(pair_param.second, attr_list[i].value);
            }

            assert(pair_param.first);
            get_attr_value_from_p4(meta_param->field, meta_param->bitwidth, pair_param.first, attr_list[i].value);
        }
        else if (auto meta_key = meta_table.get_meta_key(attr_list[i].id)) {
            // attr in table keys
            auto pair_key = get_match_pair_from_p4_table_entry(meta_key, matchActionEntry);
            if (pair_key.second) {
                get_attr_ipaddr_family_from_p4(pair_key.second->mutable_exact(), attr_list[i].value);
            }

            assert(pair_key.first);
            if (meta_key->match_type == "ternary" && string_ends_with(meta_key->name, "_MASK")) {
                get_attr_value_mask_from_p4_ternary(meta_key->field, meta_key->bitwidth,
                         pair_key.first->mutable_ternary(), attr_list[i].value);
            }
            else {
                get_attr_value_from_p4_match(*meta_key, pair_key.first, attr_list[i].value);
            }
        }
        else {
            get_attr_from_p4_misc(meta_table, matchActionEntry, &attr_list[i]);
        }
    }

    return SAI_STATUS_SUCCESS;
}

sai_status_t DashSai::get(
        _In_ const P4MetaTable &meta_table,
        _Inout_ std::shared_ptr<p4::v1::TableEntry> matchActionEntry,
        _In_ uint32_t attr_count,
        _Inout_ sai_attribute_t *attr_list)
{
    DASH_LOG_ENTER();
    DASH_CHECK_API_INITIALIZED();

    if (grpc::StatusCode::OK != readTableEntry(matchActionEntry)) {
        return SAI_STATUS_FAILURE;
    }

    auto action = matchActionEntry->mutable_action()->mutable_action();
    pi_p4_id_t action_id = action->action_id();

    for (uint32_t i = 0; i < attr_count; i++) {
        if (auto meta_param = meta_table.get_meta_action_param(action_id, attr_list[i].id)) {
            // attr in table action params
            auto pair_param = get_action_param_with_is_v6_flag_from_p4_table_entry(meta_param, matchActionEntry);
            if (pair_param.second) {
                get_attr_ipaddr_family_from_p4(pair_param.second, attr_list[i].value);
            }

            assert(pair_param.first);
            get_attr_value_from_p4(meta_param->field, meta_param->bitwidth, pair_param.first, attr_list[i].value);
        }
        else {
            get_attr_from_p4_misc(meta_table, matchActionEntry, &attr_list[i]);
        }
    }

    return SAI_STATUS_SUCCESS;
}

void DashSai::mutateSiblingTablesEntry(
        _In_ const P4MetaTable &meta_table,
        _In_ std::shared_ptr<p4::v1::TableEntry> matchActionEntry,
        _In_ p4::v1::Update_Type updateType,
        _In_ uint32_t action_id)
{
    if (meta_table.sibling_tables.empty()) {
        return;
    }

    std::shared_ptr<p4::v1::TableEntry> entry = std::make_shared<p4::v1::TableEntry>();
    entry->CopyFrom(*matchActionEntry);
    auto action = entry->mutable_action()->mutable_action();

    for (auto &sibling: meta_table.sibling_tables) {
        entry->set_table_id(sibling.id);

        if (updateType != p4::v1::Update_Type_DELETE) {
            auto enum_id = meta_table.find_action_enum_id(action_id);
            auto sibling_action_id = sibling.actions.at(enum_id);
            action->set_action_id(sibling_action_id);
        }

        mutateTableEntry(entry, updateType);
    }
}
