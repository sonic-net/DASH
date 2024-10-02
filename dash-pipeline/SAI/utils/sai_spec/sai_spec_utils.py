from typing import Any, Dict, List, Callable

word_fixers: Dict[str, str] = {}

def load_word_fixers() -> None:
    global word_fixers

    word_fixers = {
        "dash": "DASH",
        "vm": "",
        "pl": "PL",
        "ha": "HA",
        "ca": "CA",
        "pa": "PA",
        "vip": "VIP",
        "cp": "control plane",
        "dp": "data plane",
        "pps": "PPS",
        "cps": "CPS",
        "addr": "address",
        "dmac": "destination MAC",
        "resimulated": "re-simulated",
        "resimulation": "re-simulation",
        "pb": "protocol buffer",
        "proto": "protocol",
        "smac": "source MAC",
        "dpu": "DPU"
    }

    # Load all SAI acronyms
    with open("SAI/meta/acronyms.txt", "r") as f:
        for line in f:
            word = line.split('-')[0].strip().lower()
            word_fixers[word] = word.upper()

    # More command word fixers

def normalize_sai_comment(s: str) -> str:
    """
    Normalize SAI comment string by removing acronyms and extra spaces.
    """
    if len(word_fixers) == 0:
        load_word_fixers()

    words = [word if word.lower() not in word_fixers else word_fixers[word.lower()] for word in s.split()]
    s = " ".join(words)
    # temporary workaround until "DPU" is added to SAI meta acronyms
    return s.replace("DPU driven HA ", "SAI vendor driven HA ")

def merge_sai_value_lists(
    target: List[Any],
    source: List[Any],
    get_key: Callable[[Any], str],
    on_conflict: Callable[[Any, Any], None] = lambda x, y: x,
    on_deprecate: Callable[[Any], bool] = lambda x: False
) -> None:
    """
    Merge 2 SAI value lists from source list into target.

    Since we could not remove the old value or change the order of old values, the merge
    is done as below:
    - Any new values will be added in the end of the list.
    - Any values that collapse with existing values will invoke on_conflict callback to resolve.
    - Any values that needs to be removed will invoke on_deprecate function to deprecate. By default,
      it will not be removed from the old list.
    """
    target_dict = {get_key(item): item for item in target}

    source_keys = set()
    for source_item in source:
        source_key = get_key(source_item)
        source_keys.add(source_key)

        if source_key in target_dict:
            target_item = target_dict[source_key]
            on_conflict(target_item, source_item)
        else:
            target.append(source_item)
            target_dict[source_key] = source_item

    # Remove all items in target, if its key doesn't exist in source_keys and on_deprecate returns True.
    target[:] = [item for item in target if get_key(item) in source_keys or not on_deprecate(item)]


def merge_sai_common_lists(
    target: List[Any],
    source: List[Any],
) -> None:
    merge_sai_value_lists(
        target,
        source,
        get_key=lambda x: x.name,
        on_conflict=lambda x, y: x.merge(y),
        on_deprecate=lambda x: x.deprecate(),
    )
