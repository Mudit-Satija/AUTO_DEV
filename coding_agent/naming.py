"""Shared naming helpers for entity prop names.

Centralizes the pattern for deriving plural data prop names and setter
function names from entity names. Used by build_plan, prompt_builder,
prompt_constraints, and bundle_generator.
"""


def _pluralize(name: str) -> str:
    """Simple English pluralization for entity names.

    Handles consonant+y -> ies (Entry -> Entries, Category -> Categories).
    Falls back to simple +s for all other cases (Book -> Books, Toy -> Toys).
    """
    if name.endswith("y") and len(name) > 1 and name[-2].lower() not in "aeiou":
        return name[:-1] + "ies"
    return name + "s"


def entity_prop_name(entity_name: str) -> str:
    """Derive the plural data prop name from an entity name.

    Example: 'Book' -> 'books', 'ReadingEntry' -> 'readingEntries'
    """
    return entity_name[0].lower() + _pluralize(entity_name[1:])


def entity_setter_name(entity_name: str) -> str:
    """Derive the setter function name from an entity name.

    Example: 'Book' -> 'setBooks', 'ReadingEntry' -> 'setReadingEntries'
    """
    return "set" + _pluralize(entity_name)
