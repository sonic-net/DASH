from typing import Dict
from .sai_type_info import SAITypeInfo


class SAITypeSolver:
    sai_type_info_registry: Dict[str, SAITypeInfo] = {
        "bool": SAITypeInfo("bool", "booldata", default="false"),
        "sai_uint8_t": SAITypeInfo("sai_uint8_t", "u8", default="0"),
        "sai_object_id_t": SAITypeInfo(
            "sai_object_id_t", "u16", default="SAI_NULL_OBJECT_ID"
        ),
        "sai_uint16_t": SAITypeInfo("sai_uint16_t", "u16", default="0"),
        "sai_ip_address_t": SAITypeInfo(
            "sai_ip_address_t", "ipaddr", default="0.0.0.0"
        ),
        "sai_ip_addr_family_t": SAITypeInfo(
            "sai_ip_addr_family_t", "u32", default="SAI_IP_ADDR_FAMILY_IPV4"
        ),
        "sai_uint32_t": SAITypeInfo("sai_uint32_t", "u32", default="0"),
        "sai_uint64_t": SAITypeInfo("sai_uint64_t", "u64", default="0"),
        "sai_mac_t": SAITypeInfo("sai_mac_t", "mac", default="vendor"),
        "sai_ip_prefix_t": SAITypeInfo("sai_ip_prefix_t", "ipPrefix", default="0"),
        "sai_u8_list_t": SAITypeInfo("sai_u8_list_t", "u8list", default="empty"),
        "sai_u16_list_t": SAITypeInfo("sai_u16_list_t", "u16list", default="empty"),
        "sai_u32_list_t": SAITypeInfo("sai_u32_list_t", "u32list", default="empty"),
        "sai_ip_prefix_list_t": SAITypeInfo(
            "sai_ip_prefix_list_t", "ipprefixlist", default="empty"
        ),
        "sai_u32_range_t": SAITypeInfo("sai_u32_range_t", "u32range", default="empty"),
        "sai_u8_range_list_t": SAITypeInfo(
            "sai_u8_range_list_t", "u8rangelist", default="empty"
        ),
        "sai_u16_range_list_t": SAITypeInfo(
            "sai_u16_range_list_t", "u16rangelist", default="empty"
        ),
        "sai_u32_range_list_t": SAITypeInfo(
            "sai_u32_range_list_t", "u32rangelist", default="empty"
        ),
        "sai_u64_range_list_t": SAITypeInfo(
            "sai_u64_range_list_t", "u64rangelist", default="empty"
        ),
        "sai_ipaddr_range_list_t": SAITypeInfo(
            "sai_ipaddr_range_list_t", "ipaddrrangelist", default="empty"
        ),
    }

    @staticmethod
    def register_sai_type(
        name: str,
        sai_attribute_value_field: str,
        default: bool = None,
        is_enum: bool = False,
    ) -> None:
        SAITypeSolver.sai_type_info_registry[name] = SAITypeInfo(
            name,
            sai_attribute_value_field=sai_attribute_value_field,
            default=default,
            is_enum=is_enum,
        )

    @staticmethod
    def get_sai_type(sai_type: str) -> SAITypeInfo:
        if sai_type not in SAITypeSolver.sai_type_info_registry:
            raise ValueError(f"sai_type={sai_type} is not supported")

        return SAITypeSolver.sai_type_info_registry[sai_type]

    @staticmethod
    def get_object_sai_type(object_size: int) -> SAITypeInfo:
        sai_type_name: str = ""

        if object_size == 1:
            sai_type_name = "bool"
        elif object_size <= 8:
            sai_type_name = "sai_uint8_t"
        elif object_size <= 16:
            sai_type_name = "sai_uint16_t"
        elif object_size <= 32:
            sai_type_name = "sai_uint32_t"
        elif object_size == 48:
            sai_type_name = "sai_mac_t"
        elif object_size <= 64:
            sai_type_name = "sai_uint64_t"
        elif object_size == 128:
            sai_type_name = "sai_ip_address_t"
        else:
            raise ValueError(f"key_size={object_size} is not supported")

        return SAITypeSolver.get_sai_type(sai_type_name)

    @staticmethod
    def get_match_key_sai_type(match_type: str, key_size: int) -> SAITypeInfo:
        if match_type == "exact" or match_type == "optional" or match_type == "ternary":
            return SAITypeSolver.get_object_sai_type(key_size)

        sai_type_name: str = ""
        if match_type == "lpm":
            sai_type_name = SAITypeSolver.__get_lpm_match_key_sai_type(key_size)
        elif match_type == "list":
            sai_type_name = SAITypeSolver.__get_list_match_key_sai_type(key_size)
        elif match_type == "range":
            sai_type_name = SAITypeSolver.__get_range_match_key_sai_type(key_size)
        elif match_type == "range_list":
            sai_type_name = SAITypeSolver.__get_range_list_match_key_sai_type(key_size)
        else:
            raise ValueError(f"match_type={match_type} is not supported")

        return SAITypeSolver.get_sai_type(sai_type_name)

    @staticmethod
    def __get_lpm_match_key_sai_type(key_size: int) -> str:
        # LPM match key should always be converted into IP prefix.
        if key_size == 32:
            return "sai_ip_prefix_t"
        elif key_size == 128:
            return "sai_ip_prefix_t"
        else:
            raise ValueError(f"key_size={key_size} is not supported")

    @staticmethod
    def __get_list_match_key_sai_type(key_size: int) -> str:
        if key_size <= 8:
            return "sai_u8_list_t"
        elif key_size <= 16:
            return "sai_u16_list_t"
        elif key_size <= 32:
            return "sai_u32_list_t"
        else:
            raise ValueError(f"key_size={key_size} is not supported")

    @staticmethod
    def __get_range_match_key_sai_type(key_size: int) -> str:
        # In SAI, all ranges that having smaller size than 32-bits are passed as 32-bits, such as port ranges and etc.
        # So, we convert all ranges that is smaller than 32-bits to sai_u32_range_t by default.
        if key_size <= 32:
            return "sai_u32_range_t"
        else:
            raise ValueError(f"key_size={key_size} is not supported")

    @staticmethod
    def __get_range_list_match_key_sai_type(key_size: int) -> str:
        if key_size <= 8:
            return "sai_u8_range_list_t"
        elif key_size <= 16:
            return "sai_u16_range_list_t"
        elif key_size <= 32:
            return "sai_u32_range_list_t"
        elif key_size <= 64:
            return "sai_u64_range_list_t"
        else:
            raise ValueError(f"key_size={key_size} is not supported")
