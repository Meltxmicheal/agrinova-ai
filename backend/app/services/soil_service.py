import random

class SoilService:
    @staticmethod
    def get_soil_by_location(lat: float = None, lon: float = None, district: str = None):
        """
        Smart Mock for Soil API.
        Determines soil type based on Tamil Nadu district mapping or falls back to random coordinate seeding.
        """
        
        # Simple heuristics for Tamil Nadu districts
        district_soil_map = {
            "Thanjavur": "Alluvial Soil",
            "Thiruvarur": "Alluvial Soil",
            "Nagapattinam": "Alluvial Soil",
            "Tiruchirappalli": "Alluvial Soil",
            "Madurai": "Red Soil",
            "Sivaganga": "Red Soil",
            "Ramanathapuram": "Red Soil",
            "Tirunelveli": "Red Soil",
            "Thoothukudi": "Black Soil",
            "Virudhunagar": "Black Soil",
            "Coimbatore": "Black Soil",
            "Erode": "Black Soil",
            "Salem": "Red Soil",
            "Dharmapuri": "Red Soil",
            "The Nilgiris": "Laterite Soil",
            "Kanyakumari": "Laterite Soil"
        }
        
        soil_type = "Red Soil" # Default fallback
        
        if district:
            # Find closest match
            for k, v in district_soil_map.items():
                if k.lower() in district.lower():
                    soil_type = v
                    break
        elif lat and lon:
            # Fake logic based on coords
            if lat < 10.0:
                soil_type = "Red Soil"
            elif lon > 79.0:
                soil_type = "Alluvial Soil"
            else:
                soil_type = "Black Soil"
                
        # Generate other synthetic parameters based on soil_type for the ML models
        params = {
            "Alluvial Soil": {"n": (60, 100), "p": (40, 60), "k": (40, 60), "ph": (6.5, 7.5)},
            "Red Soil": {"n": (20, 50), "p": (10, 30), "k": (20, 40), "ph": (5.5, 6.5)},
            "Black Soil": {"n": (40, 80), "p": (30, 50), "k": (40, 80), "ph": (7.0, 8.5)},
            "Laterite Soil": {"n": (10, 40), "p": (10, 20), "k": (10, 30), "ph": (4.5, 6.0)}
        }
        
        sp = params.get(soil_type, params["Red Soil"])
        
        return {
            "nitrogen": random.randint(*sp["n"]),
            "phosphorus": random.randint(*sp["p"]),
            "potassium": random.randint(*sp["k"]),
            "ph": round(random.uniform(*sp["ph"]), 1),
            "moisture": round(random.uniform(20.0, 60.0), 1),
            "soil_type": soil_type
        }

    @staticmethod
    def parse_soil_report(file_stream=None):
        """
        Mock OCR/AI extraction from a Soil Test Report PDF/Image.
        Returns extracted values.
        """
        return {
            "nitrogen": random.randint(40, 100),
            "phosphorus": random.randint(30, 60),
            "potassium": random.randint(30, 60),
            "ph": round(random.uniform(6.0, 7.5), 1)
        }
