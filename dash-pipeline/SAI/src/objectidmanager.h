#pragma once

extern "C" {
#include <sai.h>
#include <saitypesextensions.h>
}

#include <set>
#include <map>
#include <string>

namespace dash
{
    class ObjectIdManager
    {
        public:

            ObjectIdManager() = default;
            ~ObjectIdManager() = default;

        public:

            /**
             * @brief Switch id query.
             *
             * Return switch object id for given object if. If object type is
             * switch, it will return input value.
             *
             * Returns SAI_NULL_OBJECT_ID if input value is invalid.
             *
             * For SAI_NULL_OBJECT_ID input will return SAI_NULL_OBJECT_ID.
             */
            sai_object_id_t saiSwitchIdQuery(
                    _In_ sai_object_id_t objectId) const;

            /**
             * @brief Object type query.
             *
             * Returns object type for input object id. If object id is invalid
             * then returns SAI_OBJECT_TYPE_NULL.
             */
            sai_object_type_t saiObjectTypeQuery(
                    _In_ sai_object_id_t objectId) const;

            /**
             * @brief Clear switch index set.
             *
             * New switch index allocation will start from the beginning.
             */
            void clear();

            /**
             * @brief Allocate new object id on a given switch.
             *
             * Method can't be used to allocate switch object id.
             *
             * Returns SAI_NULL_OBJECT_ID if there are no more available
             * switch indexes.
             */
            sai_object_id_t allocateNewObjectId(
                    _In_ sai_object_type_t objectType,
                    _In_ sai_object_id_t switchId);

            /**
             * @brief Allocate new switch object id.
             *
             * Return SAI_NULL_OBJECT_ID if allocation failed.
             */
            sai_object_id_t allocateNewSwitchObjectId(
                    _In_ const std::string& hardwareInfo);

            /**
             * @brief Release allocated object id.
             *
             * If object type is switch, then switch index will be released.
             */
            void releaseObjectId(
                    _In_ sai_object_id_t objectId);

        public:

            /**
             * @brief Switch id query.
             *
             * Return switch object id for given object if. If object type is
             * switch, it will return input value.
             *
             * Return SAI_NULL_OBJECT_ID if given object id has invalid object type.
             */
            static sai_object_id_t switchIdQuery(
                    _In_ sai_object_id_t objectId);

            /**
             * @brief Object type query.
             *
             * Returns object type for input object id. If object id is invalid
             * then returns SAI_OBJECT_TYPE_NULL.
             */
            static sai_object_type_t objectTypeQuery(
                    _In_ sai_object_id_t objectId);

        private:

            /**
             * @brief Release given switch index.
             */
            void releaseSwitchIndex(
                    _In_ uint32_t index);

            /**
             * @brief Construct object id.
             *
             * Using all input parameters to construct object id.
             */
            static sai_object_id_t constructObjectId(
                    _In_ sai_object_type_t objectType,
                    _In_ uint32_t switchIndex,
                    _In_ uint64_t objectIndex);

        private:

            /**
             * @brief Set of allocated switch indexes.
             */
            std::set<uint32_t> m_switchIndexes;

            /**
             * @brief Object index indexer map.
             *
             * Each object type have its own starting index from zero for easy
             * count how many objects of each type there are allocated.
             */
            std::map<sai_object_type_t, uint64_t> m_indexer;
    };
}
