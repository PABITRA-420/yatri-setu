"""
Canonical Destination Registry & Normalization Engine (Prompt 7).

Enforces the six canonical destinations for the Eastern Himalayan region:
- darjeeling
- kalimpong
- mirik
- lava
- lolegaon
- rishop

Provides strict normalization for aliases, suffixes, and whitespace/case variations.
Rejects any unmapped destination to maintain strict data integrity.
"""

from typing import Tuple, Dict, Optional, Set
import logging

logger = logging.getLogger(__name__)

CANONICAL_DESTINATIONS: Tuple[str, ...] = (
    "darjeeling",
    "kalimpong",
    "mirik",
    "lava",
    "lolegaon",
    "rishop",
)

# Known regional aliases, colloquial names, and administrative variants
DESTINATION_ALIASES: Dict[str, str] = {
    # Darjeeling variants
    "darj": "darjeeling",
    "darjeeling_town": "darjeeling",
    "darjeeling town": "darjeeling",
    "darjeeling_municipality": "darjeeling",
    "darjeeling-district": "darjeeling",
    "darjeeling district": "darjeeling",
    "queen of hills": "darjeeling",

    # Kalimpong variants
    "kalimpong_town": "kalimpong",
    "kalimpong town": "kalimpong",
    "kalimpong_municipality": "kalimpong",
    "kalimpong-district": "kalimpong",
    "kalimpong district": "kalimpong",

    # Mirik variants
    "mirik_lake": "mirik",
    "mirik lake": "mirik",
    "mirik_bazar": "mirik",
    "mirik town": "mirik",

    # Lava variants
    "lava_bazar": "lava",
    "lava bazar": "lava",
    "lava_village": "lava",
    "lava village": "lava",

    # Lolegaon variants
    "lolegaon_forest": "lolegaon",
    "loleygaon": "lolegaon",
    "loleygaon_village": "lolegaon",
    "kaffer": "lolegaon",
    "kaffer_village": "lolegaon",

    # Rishop variants
    "rishop_village": "rishop",
    "rishyap": "rishop",
    "rishyap_village": "rishop",
    "rishyap village": "rishop",
}

COMMON_SUFFIXES = (
    "_town",
    "-town",
    " town",
    "_village",
    "-village",
    " village",
    "_district",
    "-district",
    " district",
    "_lake",
    "-lake",
    " lake",
    "_forest",
    "-forest",
    " forest",
    "_bazar",
    "-bazar",
    " bazar",
    "_municipality",
    "-municipality",
)


def normalize_destination_id(destination_id: Optional[str]) -> str:
    """
    Normalizes any destination identifier to its canonical representation.

    Rules:
    1. Trims whitespace and converts to lower case.
    2. Direct match against canonical tuple.
    3. Alias map lookup.
    4. Suffix stripping (e.g. 'darjeeling_town' -> 'darjeeling').
    5. Raises ValueError for unrecognized destinations.
    """
    if not destination_id:
        raise ValueError("Destination ID cannot be None or empty.")

    raw = str(destination_id).strip().lower()

    # Direct canonical match
    if raw in CANONICAL_DESTINATIONS:
        return raw

    # Exact alias match
    if raw in DESTINATION_ALIASES:
        canonical = DESTINATION_ALIASES[raw]
        logger.debug(f"Normalized alias '{destination_id}' -> '{canonical}'")
        return canonical

    # Standardized delimiter version (replace spaces/hyphens with underscore)
    standardized = raw.replace("-", "_").replace(" ", "_")
    if standardized in CANONICAL_DESTINATIONS:
        return standardized
    if standardized in DESTINATION_ALIASES:
        canonical = DESTINATION_ALIASES[standardized]
        logger.debug(f"Normalized alias '{destination_id}' -> '{canonical}'")
        return canonical

    # Suffix stripping
    for suffix in COMMON_SUFFIXES:
        if raw.endswith(suffix):
            base = raw[:-len(suffix)].strip()
            if base in CANONICAL_DESTINATIONS:
                logger.debug(f"Normalized suffixed destination '{destination_id}' -> '{base}'")
                return base
            if base in DESTINATION_ALIASES:
                return DESTINATION_ALIASES[base]

    raise ValueError(
        f"Unknown destination '{destination_id}'. "
        f"Must be one of the six canonical destinations: {list(CANONICAL_DESTINATIONS)}"
    )


def is_canonical_destination(destination_id: Optional[str]) -> bool:
    """Returns True if the destination ID resolves to one of the six canonical destinations."""
    try:
        normalize_destination_id(destination_id)
        return True
    except (ValueError, TypeError):
        return False
