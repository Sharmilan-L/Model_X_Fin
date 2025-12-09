INDUSTRIES = [
    "Apparel",
    "FoodBeverage",
    "Water",
    "Retail",
    "Tourism",
    "IT",
    "Agriculture",
    "Logistics",
    "Energy",
    "Banking"
]

SENSITIVITY_MATRIX = {

    # -------------------------------------------------
    # WEATHER EVENTS
    # -------------------------------------------------
    "Flood": {
        "Apparel": -0.55,
        "FoodBeverage": +0.10,
        "Water": +0.65,
        "Retail": -0.10,
        "Tourism": -0.40,
        "IT": -0.05,
        "Agriculture": -0.55,
        "Logistics": -0.70,
        "Energy": -0.10,
        "Banking": -0.05
    },

    "Heavy Rain": {
        "Apparel": -0.30,
        "FoodBeverage": +0.05,
        "Water": +0.40,
        "Retail": -0.05,
        "Tourism": -0.20,
        "IT": -0.02,
        "Agriculture": -0.35,
        "Logistics": -0.40,
        "Energy": -0.05,
        "Banking": -0.02
    },

    "Landslide": {
        "Apparel": -0.45,
        "FoodBeverage": 0.00,
        "Water": +0.20,
        "Retail": -0.10,
        "Tourism": -0.30,
        "IT": 0.00,
        "Agriculture": -0.45,
        "Logistics": -0.60,
        "Energy": -0.05,
        "Banking": 0.00
    },

    "Cyclone": {
        "Apparel": -0.60,
        "FoodBeverage": +0.10,
        "Water": +0.50,
        "Retail": -0.10,
        "Tourism": -0.35,
        "IT": -0.10,
        "Agriculture": -0.45,
        "Logistics": -0.65,
        "Energy": -0.05,
        "Banking": -0.05
    },

    "Strong Wind": {
        "Apparel": -0.20,
        "FoodBeverage": 0.00,
        "Water": +0.10,
        "Retail": -0.05,
        "Tourism": -0.25,
        "IT": 0,
        "Agriculture": -0.25,
        "Logistics": -0.30,
        "Energy": -0.05,
        "Banking": 0.00
    },

    "Lightning": {
        "Apparel": -0.20,
        "FoodBeverage": 0.00,
        "Water": 0.00,
        "Retail": 0.00,
        "Tourism": -0.10,
        "IT": -0.10,
        "Agriculture": -0.10,
        "Logistics": -0.10,
        "Energy": -0.15,
        "Banking": 0.00
    },

    "Drought": {
        "Apparel": -0.05,
        "FoodBeverage": -0.20,
        "Water": +0.70,
        "Retail": -0.10,
        "Tourism": -0.10,
        "IT": 0,
        "Agriculture": -0.70,
        "Logistics": -0.10,
        "Energy": -0.10,
        "Banking": 0.00
    },

    # -------------------------------------------------
    # HEALTH EVENTS
    # -------------------------------------------------
    "Health Alert": {
        "Apparel": -0.05,
        "FoodBeverage": +0.10,
        "Water": +0.25,
        "Retail": +0.30,
        "Tourism": -0.40,
        "IT": 0,
        "Agriculture": -0.10,
        "Logistics": -0.15,
        "Energy": 0,
        "Banking": 0
    },

    # -------------------------------------------------
    # TRANSPORT EVENTS
    # -------------------------------------------------
    "Transport Disruption": {
        "Apparel": -0.30,
        "FoodBeverage": -0.05,
        "Water": 0.00,
        "Retail": -0.20,
        "Tourism": -0.30,
        "IT": 0,
        "Agriculture": -0.20,
        "Logistics": -0.80,
        "Energy": -0.10,
        "Banking": -0.05
    },

    "Train Issue": {
        "Apparel": -0.40,
        "FoodBeverage": 0,
        "Water": 0,
        "Retail": -0.15,
        "Tourism": -0.25,
        "IT": 0,
        "Agriculture": -0.10,
        "Logistics": -0.50,
        "Energy": 0,
        "Banking": -0.05
    },

    "Bus Issue": {
        "Apparel": -0.30,
        "FoodBeverage": 0,
        "Water": 0,
        "Retail": -0.10,
        "Tourism": -0.20,
        "IT": 0,
        "Agriculture": -0.05,
        "Logistics": -0.25,
        "Energy": 0,
        "Banking": -0.05
    },

    "Port Disruption": {
        "Apparel": -0.20,
        "FoodBeverage": -0.10,
        "Water": 0,
        "Retail": -0.10,
        "Tourism": -0.20,
        "IT": 0,
        "Agriculture": -0.10,
        "Logistics": -0.70,
        "Energy": -0.05,
        "Banking": -0.10
    },

    "Airport Issue": {
        "Apparel": 0,
        "FoodBeverage": 0,
        "Water": 0,
        "Retail": 0,
        "Tourism": -0.50,
        "IT": 0,
        "Agriculture": 0,
        "Logistics": -0.30,
        "Energy": 0,
        "Banking": 0
    },

    # -------------------------------------------------
    # ECONOMIC EVENTS
    # -------------------------------------------------
    "Fuel Price Increase": {
        "Apparel": -0.30,
        "FoodBeverage": -0.15,
        "Water": -0.05,
        "Retail": -0.20,
        "Tourism": -0.45,
        "IT": -0.05,
        "Agriculture": -0.20,
        "Logistics": -0.90,
        "Energy": +0.45,
        "Banking": +0.15
    },

    "Policy Change": {
        "Apparel": -0.10,
        "FoodBeverage": -0.05,
        "Water": 0,
        "Retail": -0.15,
        "Tourism": -0.10,
        "IT": -0.05,
        "Agriculture": -0.05,
        "Logistics": -0.10,
        "Energy": -0.05,
        "Banking": +0.30
    },

    "Economic Update": {
        "Apparel": -0.05,
        "FoodBeverage": 0,
        "Water": 0,
        "Retail": 0,
        "Tourism": -0.10,
        "IT": +0.10,
        "Agriculture": -0.10,
        "Logistics": -0.10,
        "Energy": +0.15,
        "Banking": +0.40
    },

    # -------------------------------------------------
    # SOCIAL / PUBLIC EVENTS
    # -------------------------------------------------
    "Strike": {
        "Apparel": -0.20,
        "FoodBeverage": -0.10,
        "Water": 0,
        "Retail": -0.15,
        "Tourism": -0.30,
        "IT": -0.05,
        "Agriculture": -0.10,
        "Logistics": -0.40,
        "Energy": -0.10,
        "Banking": -0.10
    },

    "Crime Event": {
        "Apparel": -0.05,
        "FoodBeverage": 0,
        "Water": 0,
        "Retail": -0.05,
        "Tourism": -0.15,
        "IT": 0,
        "Agriculture": 0,
        "Logistics": -0.05,
        "Energy": 0,
        "Banking": -0.05
    },

    "Political Event": {
        "Apparel": 0,
        "FoodBeverage": 0,
        "Water": 0,
        "Retail": 0,
        "Tourism": -0.05,
        "IT": 0,
        "Agriculture": 0,
        "Logistics": 0,
        "Energy": 0,
        "Banking": +0.10
    },

    # -------------------------------------------------
    # INDUSTRIAL / OPERATIONAL EVENTS
    # -------------------------------------------------
    "Factory Incident": {
        "Apparel": -0.50,
        "FoodBeverage": -0.30,
        "Water": -0.10,
        "Retail": -0.15,
        "Tourism": 0,
        "IT": 0,
        "Agriculture": -0.10,
        "Logistics": -0.20,
        "Energy": 0,
        "Banking": 0
    },

    "Power Cut": {
        "Apparel": -0.10,
        "FoodBeverage": -0.10,
        "Water": 0,
        "Retail": -0.10,
        "Tourism": -0.15,
        "IT": -0.15,
        "Agriculture": 0,
        "Logistics": -0.15,
        "Energy": -0.25,
        "Banking": -0.10
    },

    "Water Supply Issue": {
        "Apparel": 0,
        "FoodBeverage": -0.10,
        "Water": -0.60,
        "Retail": -0.10,
        "Tourism": 0,
        "IT": 0,
        "Agriculture": -0.20,
        "Logistics": -0.05,
        "Energy": 0,
        "Banking": 0
    }
}

