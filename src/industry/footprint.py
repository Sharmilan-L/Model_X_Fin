# src/industry/footprint.py
"""
This file defines where each industry mainly operates.
Used to calculate regional impact.
"""

PROVINCE_MAP = {
    "Western": ["Colombo", "Gampaha", "Kalutara"],
    "Central": ["Kandy", "Matale", "Nuwara Eliya"],
    "Southern": ["Galle", "Matara", "Hambantota"],
    "Northern": ["Jaffna", "Kilinochchi", "Mannar", "Vavuniya", "Mullaitivu"],
    "Eastern": ["Batticaloa", "Trincomalee", "Ampara"],
    "North Western": ["Kurunegala", "Puttalam"],
    "North Central": ["Anuradhapura", "Polonnaruwa"],
    "Uva": ["Badulla", "Monaragala"],
    "Sabaragamuwa": ["Ratnapura", "Kegalle"]
}

# INDUSTRY → MAIN OPERATING PROVINCES
INDUSTRY_REGIONS = {

    # 1. Apparel & Garments – All major factory zones
    "Apparel": [
        "Western",       # Colombo, Gampaha, Kalutara
        "North Western", # Kurunegala, Puttalam
        "Central",       # Kandy, Matale
        "Southern"       # Galle, Matara
    ],

    # 2. Food & Beverage – Agriculture + consumer markets
    "FoodBeverage": [
        "Western",
        "Southern",
        "North Western",
        "Central",
        "Sabaragamuwa"   # Kegalle, Ratnapura
    ],

    # 3. Water Bottling / Distribution
    "Water": [
        "Western",
        "Central",
        "Sabaragamuwa",   # water sources
        "Southern"
    ],

    # 4. Retail – All urban centers
    "Retail": [
        "Western",
        "Central",
        "Southern",
        "North Western",
        "Sabaragamuwa"
    ],

    # 5. Tourism – ALL tourist regions
    "Tourism": [
        "Western",
        "Southern",
        "Central",
        "Eastern",        # Trinco, Batticaloa
        "North Western",  # Kalpitiya
        "Northern",       # Jaffna
        "Uva"             # Ella, Bandarawela
    ],

    # 6. IT / BPO – Sri Lanka’s tech zones
    "IT": [
        "Western",         # Colombo
        "Central"          # Kandy emerging tech hub
    ],

    # 7. Agriculture – All major farming areas
    "Agriculture": [
        "North Central",
        "Uva",
        "Eastern",
        "Central",
        "North Western",
        "Southern"
    ],

    # 8. Logistics – Ports, highways, distribution corridors
    "Logistics": [
        "Western",         # Colombo Port
        "Southern",        # Hambantota Port
        "North Western",   # Kurunegala hub
        "Central"          # Kandy distribution routes
    ],

    # 9. Energy – Hydro, fossil, solar sectors
    "Energy": [
        "Central",         # Hydropower dominion
        "Western",         # CEB, power plants
        "Southern",        # Coal plant area
        "Northern"         # Wind zones
    ],

    # 10. Banking – All commercial centers
    "Banking": [
        "Western",
        "Central",
        "Southern",
        "North Western"
    ]
}

def district_to_province(district):
    for province, districts in PROVINCE_MAP.items():
        if district in districts:
            return province
    return None
