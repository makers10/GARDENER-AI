import datetime

class PlantAdvisor:
    def __init__(self):
        # Database of plant types and their ideal conditions
        self.plant_data = {
            "Tomato": {"temp": (18, 25), "humidity": (50, 70), "watering": "Regular (Deep)", "soil": "Well-drained"},
            "Succulent": {"temp": (15, 30), "humidity": (20, 50), "watering": "Occasional", "soil": "Sandy/Gritty"},
            "Rose": {"temp": (15, 25), "humidity": (60, 80), "watering": "Consistent morning", "soil": "Loamy"},
            "Fern": {"temp": (15, 24), "humidity": (70, 95), "watering": "Frequent misty", "soil": "Moist/High Organic"},
            "Baseline": {"temp": (18, 24), "humidity": (40, 60), "watering": "Moderate", "soil": "Standard"}
        }

    def get_season(self):
        """Estimate current astronomical season (Northern Hemisphere)."""
        month = datetime.datetime.now().month
        if month in [3, 4, 5]: return "Spring"
        if month in [6, 7, 8]: return "Summer"
        if month in [9, 10, 11]: return "Autumn"
        return "Winter"

    def advise(self, plant_name="Baseline", country="US"):
        """Get contextual advice for a specific plant in a specific locale."""
        season = self.get_season()
        plant = self.plant_data.get(plant_name, self.plant_data["Baseline"])
        
        advice = {
            "season_context": f"Currently {season} in {country}.",
            "ideal_params": f"Ideal for {plant_name}: {plant['temp'][0]}-{plant['temp'][1]}°C, {plant['humidity'][0]}-{plant['humidity'][1]}% RH",
            "warnings": [],
            "tips": []
        }

        # Contextual Advice based on Season + Country
        if season == "Summer" and country in ["IN", "PK", "AE"]: # Hot Climates
             advice["warnings"].append(f"High-intensity UV exposure likely in {season}. Use a shade cloth if temp exceeds {plant['temp'][1]}°C.")
        
        if season == "Winter" and country in ["RU", "CA", "DE", "GB"]: # Cold Climates
             advice["warnings"].append(f"Frost danger in {season}. Bring {plant_name} inside or provide mulch protection.")

        # Specific Tips
        advice["tips"].append(f"Watering Strategy: {plant['watering']}")
        advice["tips"].append(f"Recommended Soil: {plant['soil']}")

        return advice

if __name__ == "__main__":
    adv = PlantAdvisor()
    print(adv.advise("Tomato", "IN"))
