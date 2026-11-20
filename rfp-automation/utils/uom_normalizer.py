"""
FMCG Unit of Measure (UoM) & Packaging Normalizer

Normalizes unstructured quantity descriptions (e.g., cartons, cases, dozens, crates, packs)
into standardized consumer retail units for accurate pricing and inventory forecasting.
"""

import re
from typing import Dict, Any, Tuple

# Standard carton / case pack multipliers for FMCG categories
DEFAULT_PACK_MULTIPLIERS = {
    "case": 12,
    "cases": 12,
    "carton": 24,
    "cartons": 24,
    "ctn": 24,
    "box": 12,
    "boxes": 12,
    "dozen": 12,
    "dozens": 12,
    "doz": 12,
    "gross": 144,
    "crate": 20,
    "crates": 20,
    "pallet": 240,
    "pallets": 240,
    "shipper": 24,
    "shippers": 24,
    "pack": 1,
    "packs": 1,
    "unit": 1,
    "units": 1,
    "pcs": 1,
    "pieces": 1,
    "bottle": 1,
    "bottles": 1,
    "tube": 1,
    "tubes": 1,
    "jar": 1,
    "jars": 1,
    "can": 1,
    "cans": 1,
    "bar": 1,
    "bars": 1,
    "tin": 1,
    "tins": 1
}


def normalize_quantity(raw_qty: Any, raw_unit: str = "", description: str = "") -> Dict[str, Any]:
    """
    Normalizes order quantity and packaging unit into standard consumer units.
    
    Args:
        raw_qty: Input quantity (number or string)
        raw_unit: Optional unit string (e.g. "cases", "cartons", "units")
        description: Product description text to extract pack size hints if needed
        
    Returns:
        Dict with keys:
            normalized_units: int (total individual retail units)
            standard_unit: str (e.g. "unit", "bottle", "pack")
            packaging_type: str (e.g. "case", "individual")
            pack_multiplier: int
    """
    # 1. Parse numeric quantity
    qty = 1
    try:
        if isinstance(raw_qty, (int, float)):
            qty = max(1, int(raw_qty))
        elif isinstance(raw_qty, str):
            clean_q = re.sub(r"[^\d.]", "", raw_qty.strip())
            qty = max(1, int(float(clean_q))) if clean_q else 1
    except Exception:
        qty = 1

    unit_str = (raw_unit or "").strip().lower()
    desc_str = (description or "").strip().lower()

    # 2. Check if unit or description specifies packaging multiplier
    multiplier = 1
    detected_package = "individual"

    combined_text = f"{unit_str} {desc_str}"

    for pack_word, mult in DEFAULT_PACK_MULTIPLIERS.items():
        # Match as whole word
        pattern = r"\b" + re.escape(pack_word) + r"\b"
        if re.search(pattern, unit_str):
            multiplier = mult
            detected_package = pack_word
            break
        elif mult > 1 and re.search(pattern, desc_str):
            multiplier = mult
            detected_package = pack_word
            break

    # Look for explicit multipliers like "case of 24", "pack of 6", "12x100g"
    explicit_match = re.search(r"(?:case of|pack of|box of|crate of)\s*(\d+)", combined_text)
    if explicit_match:
        try:
            custom_mult = int(explicit_match.group(1))
            if custom_mult > 0:
                multiplier = custom_mult
                detected_package = f"pack of {custom_mult}"
        except Exception:
            pass

    x_match = re.search(r"(\d+)\s*[xX]\s*\d+", combined_text)
    if x_match and multiplier == 1:
        try:
            custom_mult = int(x_match.group(1))
            if 2 <= custom_mult <= 144:
                multiplier = custom_mult
                detected_package = f"bundle of {custom_mult}"
        except Exception:
            pass

    total_consumer_units = qty * multiplier

    # Determine consumer unit label
    consumer_unit = "unit"
    if "bottle" in combined_text or "shampoo" in combined_text or "lotion" in combined_text:
        consumer_unit = "bottle"
    elif "bar" in combined_text or "soap" in combined_text:
        consumer_unit = "bar"
    elif "tube" in combined_text or "paste" in combined_text:
        consumer_unit = "tube"
    elif "jar" in combined_text or "honey" in combined_text or "coffee" in combined_text:
        consumer_unit = "jar"
    elif "tin" in combined_text or "ghee" in combined_text:
        consumer_unit = "tin"
    elif "pack" in combined_text or "biscuit" in combined_text or "atta" in combined_text:
        consumer_unit = "pack"

    return {
        "raw_quantity": qty,
        "raw_unit": raw_unit or "units",
        "pack_multiplier": multiplier,
        "packaging_type": detected_package,
        "normalized_units": total_consumer_units,
        "consumer_unit": consumer_unit
    }
