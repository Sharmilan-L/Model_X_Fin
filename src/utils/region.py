# src/utils/region.py

DISTRICTS = [
    "Colombo", "Gampaha", "Kalutara", "Kandy", "Matale", "Nuwara Eliya",
    "Galle", "Matara", "Hambantota", "Jaffna", "Kilinochchi", "Mannar",
    "Vavuniya", "Mullaitivu", "Batticaloa", "Trincomalee", "Ampara",
    "Badulla", "Monaragala", "Kurunegala", "Puttalam", "Anuradhapura",
    "Polonnaruwa", "Ratnapura", "Kegalle"
]

NATIONAL = "NATIONAL"

def normalize_district(name: str) -> str:
    """Very simple normalizer for now."""
    if not name:
        return NATIONAL
    for d in DISTRICTS:
        if d.lower() in name.lower():
            return d
    return NATIONAL


# ⭐ ADD THIS FUNCTION ⭐
def detect_districts(text: str):
    """
    Detects all Sri Lankan districts mentioned in the given text.
    Returns a list of districts. If none found → return [].
    """
    if not text:
        return []

    found = []
    text_lower = text.lower()

    for d in DISTRICTS:
        if d.lower() in text_lower:
            found.append(d)

    return found
