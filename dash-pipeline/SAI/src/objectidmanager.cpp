#include "objectidmanager.h"
#include "logger.h"

extern "C" {
#include "saimetadata.h"
}

#define SAI_OBJECT_ID_BITS_SIZE (8 * sizeof(sai_object_id_t))

static_assert(SAI_OBJECT_ID_BITS_SIZE == 64, "sai_object_id_t must have 64 bits");
static_assert(sizeof(sai_object_id_t) == sizeof(uint64_t), "SAI object ID size should be uint64_t");

#define DASH_OID_RESERVED_BITS_SIZE ( 7 )

#define DASH_OBJECT_TYPE_EXTENSIONS_FLAG_BITS_SIZE ( 1 )
#define DASH_OBJECT_TYPE_EXTENSIONS_FLAG_MAX ( (1ULL << DASH_OBJECT_TYPE_EXTENSIONS_FLAG_BITS_SIZE) - 1 )
#define DASH_OBJECT_TYPE_EXTENSIONS_FLAG_MASK (DASH_OBJECT_TYPE_EXTENSIONS_FLAG_MAX)

#define DASH_OBJECT_TYPE_BITS_SIZE ( 8 )
#define DASH_OBJECT_TYPE_MASK ( (1ULL << DASH_OBJECT_TYPE_BITS_SIZE) - 1 )
#define DASH_OBJECT_TYPE_MAX (DASH_OBJECT_TYPE_MASK)

#define DASH_SWITCH_INDEX_BITS_SIZE ( 8 )
#define DASH_SWITCH_INDEX_MASK ( (1ULL << DASH_SWITCH_INDEX_BITS_SIZE) - 1 )
#define DASH_SWITCH_INDEX_MAX (DASH_SWITCH_INDEX_MASK)

#define DASH_OBJECT_INDEX_BITS_SIZE ( 40 )
#define DASH_OBJECT_INDEX_MASK ( (1ULL << DASH_OBJECT_INDEX_BITS_SIZE) - 1 )
#define DASH_OBJECT_INDEX_MAX (DASH_OBJECT_INDEX_MASK)

#define DASH_OBJECT_ID_BITS_SIZE ( \
        DASH_OID_RESERVED_BITS_SIZE + \
        DASH_OBJECT_TYPE_EXTENSIONS_FLAG_BITS_SIZE + \
        DASH_OBJECT_TYPE_BITS_SIZE + \
        DASH_SWITCH_INDEX_BITS_SIZE + \
        DASH_OBJECT_INDEX_BITS_SIZE)

static_assert(DASH_OBJECT_ID_BITS_SIZE == SAI_OBJECT_ID_BITS_SIZE, "dash object id size must be equal to SAI object id size");

static_assert(DASH_OBJECT_TYPE_MAX == 0xff, "invalid object type max size");
static_assert(DASH_SWITCH_INDEX_MAX == 0xff, "invalid switch index max size");
static_assert(DASH_OBJECT_INDEX_MAX == 0xffffffffff, "invalid object index max");

static_assert(SAI_OBJECT_TYPE_MAX < 256, "object type must be possible to encode on 1 byte");
static_assert((SAI_OBJECT_TYPE_EXTENSIONS_RANGE_END - SAI_OBJECT_TYPE_EXTENSIONS_RANGE_START) < 256,
        "extensions object type must be possible to encode on 1 byte");

/*
 * Current OBJECT ID format:
 *
 * bits 63..57 - reserved (must be zero)
 * bits 56..56 - object type extensions flag
 * bits 55..48 - SAI object type
 * bits 47..40 - switch index
 * bits 39..0  - object index
 *
 * So large number of bits is required, otherwise we would need to have map of
 * OID to some struct that will have all those values.  But having all this
 * information in OID itself is more convenient.
 */

#define DASH_GET_OBJECT_INDEX(oid) \
    ( ((uint64_t)oid) & ( DASH_OBJECT_INDEX_MASK ) )

#define DASH_GET_SWITCH_INDEX(oid) \
    ( (((uint64_t)oid) >> ( DASH_OBJECT_INDEX_BITS_SIZE) ) & ( DASH_SWITCH_INDEX_MASK ) )

#define DASH_GET_OBJECT_TYPE(oid) \
    ( (((uint64_t)oid) >> ( DASH_SWITCH_INDEX_BITS_SIZE + DASH_OBJECT_INDEX_BITS_SIZE ) ) & ( DASH_OBJECT_TYPE_MASK ) )

 #define DASH_GET_OBJECT_TYPE_EXTENSIONS_FLAG(oid) \
     ( (((uint64_t)oid) >> ( DASH_OBJECT_TYPE_BITS_SIZE + DASH_SWITCH_INDEX_BITS_SIZE + DASH_OBJECT_INDEX_BITS_SIZE) ) & ( DASH_OBJECT_TYPE_EXTENSIONS_FLAG_MAX ) )

#define DASH_TEST_OID (0x0123456789abcdef)

static_assert(DASH_GET_OBJECT_TYPE_EXTENSIONS_FLAG(DASH_TEST_OID) == 0x1, "object type extension flag");
static_assert(DASH_GET_OBJECT_TYPE(DASH_TEST_OID) == 0x23, "test object type");
static_assert(DASH_GET_SWITCH_INDEX(DASH_TEST_OID) == 0x45, "test switch index");
static_assert(DASH_GET_OBJECT_INDEX(DASH_TEST_OID) == 0x6789abcdef, "test object index");

using namespace dash;

sai_object_id_t ObjectIdManager::saiSwitchIdQuery(
        _In_ sai_object_id_t objectId) const
{
    DASH_LOG_ENTER();

    if (objectId == SAI_NULL_OBJECT_ID)
    {
        return SAI_NULL_OBJECT_ID;
    }

    sai_object_type_t objectType = saiObjectTypeQuery(objectId);

    if (objectType == SAI_OBJECT_TYPE_NULL)
    {
        DASH_LOG_ERROR("invalid object type of oid 0x%lx", objectId);

        return SAI_NULL_OBJECT_ID;
    }

    if (objectType == SAI_OBJECT_TYPE_SWITCH)
    {
        return objectId;
    }

    uint32_t switchIndex = (uint32_t)DASH_GET_SWITCH_INDEX(objectId);

    return constructObjectId(SAI_OBJECT_TYPE_SWITCH, switchIndex, switchIndex);
}

sai_object_type_t ObjectIdManager::saiObjectTypeQuery(
        _In_ sai_object_id_t objectId) const
{
    DASH_LOG_ENTER();

    if (objectId == SAI_NULL_OBJECT_ID)
    {
        return SAI_OBJECT_TYPE_NULL;
    }

    sai_object_type_t objectType = DASH_GET_OBJECT_TYPE_EXTENSIONS_FLAG(objectId)
        ? (sai_object_type_t)(DASH_GET_OBJECT_TYPE(objectId) + SAI_OBJECT_TYPE_EXTENSIONS_RANGE_START)
        : (sai_object_type_t)(DASH_GET_OBJECT_TYPE(objectId));

    if (sai_metadata_is_object_type_valid(objectType) == false)
    {
        DASH_LOG_ERROR("invalid object id 0x%lx", objectId);

        return SAI_OBJECT_TYPE_NULL;
    }

    return objectType;
}

void ObjectIdManager::clear()
{
    DASH_LOG_ENTER();

    DASH_LOG_NOTICE("clearing switch index set");

    m_switchIndexes.clear();
    m_indexer.clear();
}

void ObjectIdManager::releaseSwitchIndex(
        _In_ uint32_t index)
{
    DASH_LOG_ENTER();

    auto it = m_switchIndexes.find(index);

    if (it == m_switchIndexes.end())
    {
        DASH_LOG_ERROR("switch index 0x%x is invalid! programming error", index);
        return;
    }

    m_switchIndexes.erase(it);

    DASH_LOG_NOTICE("released switch index 0x%x", index);
}

sai_object_id_t ObjectIdManager::allocateNewObjectId(
        _In_ sai_object_type_t objectType,
        _In_ sai_object_id_t switchId)
{
    DASH_LOG_ENTER();

    if (sai_metadata_is_object_type_valid(objectType) == false)
    {
        DASH_LOG_ERROR("invalid objct type: %d", objectType);

        return SAI_NULL_OBJECT_ID;
    }

    if (objectType == SAI_OBJECT_TYPE_SWITCH)
    {
        DASH_LOG_ERROR("this function can't be used to allocate switch id");

        return SAI_NULL_OBJECT_ID;
    }

    sai_object_type_t switchObjectType = saiObjectTypeQuery(switchId);

    if (switchObjectType != SAI_OBJECT_TYPE_SWITCH)
    {
        DASH_LOG_ERROR("object type of switch 0x%lx is %d, should be SWITCH", switchId, switchObjectType);

        return SAI_NULL_OBJECT_ID;
    }

    uint32_t switchIndex = (uint32_t)DASH_GET_SWITCH_INDEX(switchId);

    // count from zero
    uint64_t objectIndex = m_indexer[objectType]++; // allocation !

    if (objectIndex > DASH_OBJECT_INDEX_MAX)
    {
        DASH_LOG_ERROR("no more object indexes available, given: 0x%lx but limit is 0x%llx",
                objectIndex,
                DASH_OBJECT_INDEX_MAX);

        return SAI_NULL_OBJECT_ID;
    }

    sai_object_id_t objectId = constructObjectId(objectType, switchIndex, objectIndex);

    DASH_LOG_INFO("allocated new object id 0x%lx", objectId);

    return objectId;
}

sai_object_id_t ObjectIdManager::allocateNewSwitchObjectId(
        _In_ const std::string& hardwareInfo)
{
    DASH_LOG_ENTER();

    // TODO currently we support only empty hardware info and 1 switch

    if (hardwareInfo.size())
    {
        DASH_LOG_ERROR("hardware info is '%s', not supported yet, switch OID allocation failed, FIXME", hardwareInfo.c_str());

        return SAI_NULL_OBJECT_ID;
    }

    uint32_t switchIndex = 0; // for empty hardware info

    if (switchIndex > DASH_SWITCH_INDEX_MAX)
    {
        DASH_LOG_ERROR("switch index %u > %llu (max)", switchIndex, DASH_SWITCH_INDEX_MAX);

        return SAI_NULL_OBJECT_ID;
    }

    if (m_switchIndexes.find(switchIndex) != m_switchIndexes.end())
    {
        DASH_LOG_ERROR("switch with index %d is alrady allocated, programming error!", switchIndex);

        return SAI_NULL_OBJECT_ID;
    }

    m_switchIndexes.insert(switchIndex);

    sai_object_id_t objectId = constructObjectId(SAI_OBJECT_TYPE_SWITCH, switchIndex, switchIndex);

    DASH_LOG_NOTICE("allocated switch OID 0x%lx for hwinfo: '%s'", objectId, hardwareInfo.c_str());

    return objectId;
}

void ObjectIdManager::releaseObjectId(
        _In_ sai_object_id_t objectId)
{
    DASH_LOG_ENTER();

    if (saiObjectTypeQuery(objectId) == SAI_OBJECT_TYPE_SWITCH)
    {
        releaseSwitchIndex((uint32_t)DASH_GET_SWITCH_INDEX(objectId));
    }
}

sai_object_id_t ObjectIdManager::constructObjectId(
        _In_ sai_object_type_t objectType,
        _In_ uint32_t switchIndex,
        _In_ uint64_t objectIndex)
{
    DASH_LOG_ENTER();

    uint64_t extensionsFlag = (uint64_t)objectType >= SAI_OBJECT_TYPE_EXTENSIONS_RANGE_START;

    objectType = extensionsFlag
        ? (sai_object_type_t)(objectType - SAI_OBJECT_TYPE_EXTENSIONS_RANGE_START)
        : objectType;

    return (sai_object_id_t)(
            (((uint64_t)extensionsFlag & DASH_OBJECT_TYPE_EXTENSIONS_FLAG_MASK) << ( DASH_OBJECT_TYPE_BITS_SIZE + DASH_SWITCH_INDEX_BITS_SIZE + DASH_OBJECT_INDEX_BITS_SIZE )) |
            (((uint64_t)objectType & DASH_OBJECT_TYPE_MASK)<< ( DASH_SWITCH_INDEX_BITS_SIZE + DASH_OBJECT_INDEX_BITS_SIZE))|
            (((uint64_t)switchIndex & DASH_SWITCH_INDEX_MASK)<< ( DASH_OBJECT_INDEX_BITS_SIZE )) |
            (objectIndex & DASH_OBJECT_INDEX_MASK));
}

sai_object_id_t ObjectIdManager::switchIdQuery(
        _In_ sai_object_id_t objectId)
{
    DASH_LOG_ENTER();

    if (objectId == SAI_NULL_OBJECT_ID)
    {
        return SAI_NULL_OBJECT_ID;
    }

    sai_object_type_t objectType = objectTypeQuery(objectId);

    if (objectType == SAI_OBJECT_TYPE_NULL)
    {
        DASH_LOG_ERROR("invalid object type of oid 0x%lx", objectId);

        return SAI_NULL_OBJECT_ID;
    }

    if (objectType == SAI_OBJECT_TYPE_SWITCH)
    {
        return objectId;
    }

    uint32_t switchIndex = (uint32_t)DASH_GET_SWITCH_INDEX(objectId);

    return constructObjectId(SAI_OBJECT_TYPE_SWITCH, switchIndex, switchIndex);
}

sai_object_type_t ObjectIdManager::objectTypeQuery(
        _In_ sai_object_id_t objectId)
{
    DASH_LOG_ENTER();

    if (objectId == SAI_NULL_OBJECT_ID)
    {
        return SAI_OBJECT_TYPE_NULL;
    }

    sai_object_type_t objectType = DASH_GET_OBJECT_TYPE_EXTENSIONS_FLAG(objectId)
        ? (sai_object_type_t)(DASH_GET_OBJECT_TYPE(objectId) + SAI_OBJECT_TYPE_EXTENSIONS_RANGE_START)
        : (sai_object_type_t)(DASH_GET_OBJECT_TYPE(objectId));

    if (sai_metadata_is_object_type_valid(objectType) == false)
    {
        DASH_LOG_ERROR("invalid object id 0x%lx", objectId);

        return SAI_OBJECT_TYPE_NULL;
    }

    return objectType;
}
