from typing import Any, List, Callable, Set

sai_acronyms: Set[str] = set()

def load_sai_acronyms() -> None:
    with open("SAI/meta/acronyms.txt", "r") as f:
        for line in f:
            sai_acronyms.add(line.split('-')[0].strip().lower())
    
    sai_acronyms.add("dash")    # DASH
    sai_acronyms.add("vm")      # VM
    sai_acronyms.add("pl")      # Private Link
    sai_acronyms.add("ha")      # High Availability
    sai_acronyms.add("ca")      # CA
    sai_acronyms.add("pa")      # PA

def normalize_sai_comment(s: str) -> str:
    """
    Normalize SAI comment string by removing acronyms and extra spaces.
    """
    if len(sai_acronyms) == 0:
        load_sai_acronyms()
    
    words = [word if word.lower() not in sai_acronyms else word.upper() for word in s.split()]
    return " ".join(words)

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
