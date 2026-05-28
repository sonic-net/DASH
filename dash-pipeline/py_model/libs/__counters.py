from enum import Enum
from typing import Dict, List, Optional, Any

from py_model.libs.__utils import *
from py_model.data_plane.dash_metadata import *

class CounterType(Enum):
    PACKETS = "PACKETS"
    BYTES = "BYTES"
    PACKETS_AND_BYTES = "BOTH"

class SaiCounter:
    def __init__(self, name: Optional[str] = None, type: Optional[str] = None, isresourcetype: Optional[bool] = None,
        objects: Optional[List[str]] = None, isreadonly: Optional[bool] = None, default_value: Optional[int] = None,
        ctr_name: Optional[str] = None, size: Optional[int] = None, counter_type: Optional[CounterType] = None,
        attr_type: str = "stats", action_names: Optional[List[str]] = None, no_suffix: bool = False,
    ):
        self.name = name
        self.type = type
        self.isresourcetype = isresourcetype
        self.objects = objects
        self.isreadonly = isreadonly
        self.default_value = default_value

        self.ctr_name = ctr_name
        self.size = size
        self.counter_type = counter_type
        self.attr_type = attr_type
        self.action_names = action_names if action_names is not None else []
        self.no_suffix = no_suffix

class Counter:
    def __init__(self, config: SaiCounter):
        self.config = config
        self._counters = [0] * config.size

    def count(self, index: int, value: int = 1) -> None:
        if 0 <= index < self.config.size:
            self._counters[index] += value
        else:
            py_log("INFO", f"Counter index {index} out of range for {self.config.ctr_name}")

class DashCounters:
    _counters: Dict[str, Counter] = {}

    @classmethod
    def get(cls, name: str) -> Optional[Counter]:
        return cls._counters.get(name)

    @classmethod
    def put(cls, name: str, counter: Counter) -> None:
        cls._counters[name] = counter

class DirectCounter:
    def __init__(self, name: str, counter_type: CounterType = CounterType.PACKETS_AND_BYTES):
        self.name = name
        self.counter_type = counter_type
        self._values: Dict[Any, int] = {}

    def count(self, entry_key: Any, value: int = 1) -> None:
        self._values[entry_key] = self._values.get(entry_key, 0) + value

class DashTableCounters:
    _counters: Dict[str, DirectCounter] = {}
    _attachments: Dict[str, str] = {}  # table_name -> counter_name

    @classmethod
    def get(cls, name: str) -> Optional[DirectCounter]:
        return cls._counters.get(name)

    @classmethod
    def put(cls, name: str, counter: DirectCounter) -> None:
        cls._counters[name] = counter

    @classmethod
    def attach(cls, table_name: str, counter_name: str) -> None:
        cls._attachments[table_name] = counter_name

def DEFINE_COUNTER(ctr_name: str, count: int, name: Optional[str] = None, counter_type: CounterType = CounterType.PACKETS_AND_BYTES,
                    attr_type: str = "stats", action_names: Optional[List[str]] = None, no_suffix: bool = False, **kwargs,) -> Counter:
    cfg = SaiCounter(ctr_name=ctr_name, name=name, size=count, counter_type=counter_type,
                    attr_type=attr_type, action_names=action_names, no_suffix=no_suffix, **kwargs,)

    existing = DashCounters.get(ctr_name)
    if existing:
        py_log("INFO", f"Counter already defined: {ctr_name}")
        return existing

    counter = Counter(cfg)
    DashCounters.put(ctr_name, counter)
    # py_log("INFO", f"Created counter: {ctr_name}")
    return counter


def DEFINE_PACKET_COUNTER(ctr_name: str, count: int, name: Optional[str] = None, **kwargs) -> Counter:
    return DEFINE_COUNTER(ctr_name, count, name, CounterType.PACKETS, **kwargs)

def DEFINE_BYTE_COUNTER(ctr_name: str, count: int, name: Optional[str] = None, **kwargs) -> Counter:
    return DEFINE_COUNTER(ctr_name, count, name, CounterType.BYTES, **kwargs)

def DEFINE_HIT_COUNTER(ctr_name: str, count: int, name: Optional[str] = None, **kwargs) -> Counter:
    return DEFINE_COUNTER(ctr_name, count, name, CounterType.PACKETS, no_suffix=True, **kwargs)

def UPDATE_COUNTER(ctr_name: str, index: int, value: int = 1) -> None:
    ctr = DashCounters.get(ctr_name)
    if ctr:
        ctr.count(index, value)
    else:
        py_log("INFO", f"Counter {ctr_name} not found")

def DEFINE_ENI_COUNTER(ctr_name: str, name: Optional[str] = None, **kwargs) -> Counter:
    return DEFINE_COUNTER(ctr_name, MAX_ENI, name, CounterType.PACKETS_AND_BYTES, action_names="set_eni_attrs", **kwargs,)

def DEFINE_ENI_PACKET_COUNTER(ctr_name: str, name: Optional[str] = None, **kwargs) -> Counter:
    return DEFINE_PACKET_COUNTER(ctr_name, MAX_ENI, name, action_names="set_eni_attrs", **kwargs)

def DEFINE_ENI_BYTE_COUNTER(ctr_name: str, name: Optional[str] = None, **kwargs) -> Counter:
    return DEFINE_BYTE_COUNTER(ctr_name, MAX_ENI, name, action_names="set_eni_attrs", **kwargs)

def DEFINE_ENI_HIT_COUNTER(ctr_name: str, name: Optional[str] = None, **kwargs) -> Counter:
    return DEFINE_HIT_COUNTER(ctr_name, MAX_ENI, name, action_names="set_eni_attrs", **kwargs)

# ENI-level data plane flow sync request counters:
# - Depends on implementations, the flow sync request could be batched, hence they need to tracked separately.
# - The counters are defined as combination of following things:
#   - 3 flow sync operations: create, update, delete.
#   - 2 ways of sync: Inline sync and timed sync.
#   - Request result: succeeded, failed (unexpected) and ignored (expected and ok to ignore, e.g., more packets arrives before flow sync is acked).
def DEFINE_ENI_FLOW_SYNC_COUNTERS(counter_name: str) -> list[str]:
    parts = [
        "req_sent", "req_recv", "req_failed", "req_ignored",
        "ack_recv", "ack_failed", "ack_ignored",
    ]
    for prefix in ("inline", "timed"):
        for p in parts:
            name = f"{prefix}_{counter_name}_{p}"
            DEFINE_ENI_HIT_COUNTER(name)


def UPDATE_ENI_COUNTER(ctr_name: str, value: int = 1) -> None:
    UPDATE_COUNTER(ctr_name, meta.eni_id, value)


def DEFINE_TABLE_COUNTER(ctr_name: str, counter_type: CounterType = CounterType.PACKETS_AND_BYTES) -> DirectCounter:
    ctr = DirectCounter(ctr_name, counter_type)
    DashTableCounters.put(ctr_name, ctr)
    # py_log("INFO", f"Created direct counter: {ctr_name}")
    return ctr


def ATTACH_TABLE_COUNTER(ctr_name: str, table_name: Optional[str] = None) -> None:
    DashTableCounters.attach(table_name, ctr_name)
    # py_log("INFO", f"Attached direct counter '{ctr_name}' to table '{table_name}'")
