#pragma once

#include "utils.h"
#include "config.h"

namespace dash
{
    class DashSai
    {
        public:

            DashSai();
            virtual ~DashSai();

        public: // sai global api

            sai_status_t apiInitialize(
                    _In_ uint64_t flags,
                    _In_ const sai_service_method_table_t *services);

            sai_status_t apiUninitialize(void);

            sai_object_type_t objectTypeQuery(
                    _In_ sai_object_id_t object_id);

            sai_object_id_t switchIdQuery(
                    _In_ sai_object_id_t object_id);

        public: // QUAD api implementation

            // switch

            sai_status_t createSwitch(
                    _Out_ sai_object_id_t *switch_id,
                    _In_ uint32_t attr_count,
                    _In_ const sai_attribute_t *attr_list);

            sai_status_t removeSwitch(
                    _In_ sai_object_id_t switch_id);

            sai_status_t setSwitchAttribute(
                    _In_ sai_object_id_t switch_id,
                    _In_ const sai_attribute_t *attr);

            sai_status_t getSwitchAttribute(
                    _In_ sai_object_id_t switch_id,
                    _In_ uint32_t attr_count,
                    _Inout_ sai_attribute_t *attr_list);

            // port

            sai_status_t getPortAttribute(
                    _In_ sai_object_id_t port_id,
                    _In_ uint32_t attr_count,
                    _Inout_ sai_attribute_t *attr_list);

        public: // helper methods

            grpc::StatusCode mutateTableEntry(
                    _In_ std::shared_ptr<p4::v1::TableEntry>,
                    _In_ p4::v1::Update_Type updateType);

            sai_object_id_t getNextObjectId(
                    _In_ sai_object_type_t objectType);

            bool insertInTable(
                    _In_ std::shared_ptr<p4::v1::TableEntry> entry,
                    _In_ sai_object_id_t objId);

            bool removeFromTable(
                    _In_ sai_object_id_t id);

        private: // private helper methods

            static std::shared_ptr<p4::config::v1::P4Info> parse_p4info(
                    _In_ const char *path);

            static std::string updateTypeStr(
                    _In_ p4::v1::Update_Type updateType);

        private: // internal sai objects

            sai_object_id_t m_switchId;

            sai_object_id_t m_defaultCpuPortId;

            sai_object_id_t m_defaultVlanId;

            sai_object_id_t m_defaultVrfId;

            sai_object_id_t m_default1QBridgeId;

            sai_object_id_t m_defaultTrapGroup;

        private:

            bool m_apiInitialized;

            const sai_service_method_table_t* m_serviceMethodTable;

            std::shared_ptr<dash::Config> m_cfg;

            std::vector<sai_object_id_t> m_portList;

            std::unordered_multimap<sai_object_id_t, std::shared_ptr<p4::v1::TableEntry> > m_tableEntryMap;

            std::mutex m_tableLock;

            std::atomic<sai_object_id_t> m_nextId;

            std::shared_ptr<grpc::Channel> m_grpcChannel;

            std::unique_ptr<p4::v1::P4Runtime::Stub> m_stub;
    };
}
