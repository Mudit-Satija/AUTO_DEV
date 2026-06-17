"""Shared naming helpers for entity prop names.

Centralizes the pattern for deriving plural data prop names and setter
function names from entity names. Used by build_plan, prompt_builder,
prompt_constraints, and bundle_generator.
"""


def entity_prop_name(entity_name: str) -> str:
    """Derive the plural data prop name from an entity name.

    Example: 'Book' -> 'books', 'ReadingEntry' -> 'readingEntries'
    """
    return entity_name[0].lower() + entity_name[1:] + "s"


def entity_setter_name(entity_name: str) -> str:
    """Derive the setter function name from an entity name.

    Example: 'Book' -> 'setBooks', 'ReadingEntry' -> 'setReadingEntries'
    """
    return "set" + entity_name + "s"
