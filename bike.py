# bike_builder.py

# ==========================================
# BIKE COMPONENT DATABASE (Weights in grams, Prices in USD)
# Note: Prices are approximate MSRPs. Weights vary slightly by size/ratio.
# ==========================================

COMPONENTS_DB = {
    "Shifters": {
        "Dura-Ace R9270": {"weight": 350, "price": 900},
        "Ultegra R8170": {"weight": 391, "price": 550},
        "105 R7170": {"weight": 423, "price": 350},
        "SRAM Red AXS": {"weight": 358, "price": 900},
        "SRAM Force AXS": {"weight": 418, "price": 500},
        "SRAM Rival AXS": {"weight": 490, "price": 350},
    },
    "Rear Derailleur": {
        "Dura-Ace R9250": {"weight": 215, "price": 850},
        "Ultegra R8150": {"weight": 262, "price": 400},
        "105 R7150": {"weight": 302, "price": 250},
        "SRAM Red AXS": {"weight": 277, "price": 750},
        "SRAM Force AXS": {"weight": 328, "price": 375},
        "SRAM Rival AXS": {"weight": 366, "price": 270},
    },
    "Front Derailleur": {
        "Dura-Ace R9250": {"weight": 96, "price": 450},
        "Ultegra R8150": {"weight": 110, "price": 250},
        "105 R7150": {"weight": 142, "price": 150},
        "SRAM Red AXS": {"weight": 170, "price": 450}, # includes battery
        "SRAM Force AXS": {"weight": 182, "price": 250}, # includes battery
        "SRAM Rival AXS": {"weight": 185, "price": 180}, # includes battery
    },
    "Crankset": {
        "Dura-Ace R9200": {"weight": 690, "price": 650},
        "Ultegra R8100": {"weight": 711, "price": 350},
        "105 R7100": {"weight": 765, "price": 180},
        "SRAM Red AXS": {"weight": 560, "price": 750},
        "SRAM Force AXS": {"weight": 741, "price": 450},
        "SRAM Rival AXS": {"weight": 844, "price": 230},
    },
    "Cassette": {
        "Dura-Ace R9200 (11-30)": {"weight": 223, "price": 350},
        "Ultegra R8100 (11-30)": {"weight": 291, "price": 120},
        "105 R7100 (11-34)": {"weight": 361, "price": 75},
        "SRAM Red AXS (10-28)": {"weight": 210, "price": 380},
        "SRAM Force AXS (10-28)": {"weight": 266, "price": 210},
        "SRAM Rival AXS (10-30)": {"weight": 282, "price": 130},
    },
    "Chain": {
        "Dura-Ace / XTR": {"weight": 242, "price": 85},
        "Ultegra / XT": {"weight": 252, "price": 50},
        "105 / SLX": {"weight": 252, "price": 35},
        "SRAM Red Flattop": {"weight": 249, "price": 90},
        "SRAM Force Flattop": {"weight": 266, "price": 45},
        "SRAM Rival Flattop": {"weight": 275, "price": 35},
    },
    "Brakes (Calipers)": {
        "Dura-Ace R9270": {"weight": 233, "price": 350},
        "Ultegra R8170": {"weight": 282, "price": 160},
        "105 R7170": {"weight": 282, "price": 110},
        "SRAM Red AXS": {"weight": 250, "price": 300},
        "SRAM Force AXS": {"weight": 270, "price": 180},
        "SRAM Rival AXS": {"weight": 290, "price": 130},
    },
    "Rotors (Pair)": {
        "Dura-Ace MT900 (160mm)": {"weight": 216, "price": 170},
        "Ultegra MT800 (160mm)": {"weight": 216, "price": 110},
        "105 SM-RT70 (160mm)": {"weight": 266, "price": 70},
        "SRAM Centerline XR (160mm)": {"weight": 236, "price": 180},
        "SRAM Paceline (160mm)": {"weight": 310, "price": 100},
    },
    "Wheelset": {
        "DT Swiss ARC 1100 Dicut 40": {"weight": 1390, "price": 3000},
        "DT Swiss ARC 1100 Dicut 60": {"weight": 1466, "price": 3000},
        "ENVE SES 4.5": {"weight": 1432, "price": 2850},
        "Zipp 303 Firecrest": {"weight": 1352, "price": 2000},
        "Roval Rapide CLX II": {"weight": 1520, "price": 2800},
        "Hunt 50 Carbon Aero Disc": {"weight": 1487, "price": 900},
    },
    "Tires (Pair)": {
        "Continental GP 5000 S TR (28mm)": {"weight": 560, "price": 200},
        "Vittoria Corsa Pro TLR (28mm)": {"weight": 590, "price": 190},
        "Schwalbe Pro One TLE (28mm)": {"weight": 560, "price": 180},
        "Pirelli P Zero Race TLR (28mm)": {"weight": 590, "price": 180},
    }
}


# ==========================================
# BIKE BUILDER LOGIC
# ==========================================

class BikeBuild:
    def __init__(self, name="My Custom Build"):
        self.name = name
        self.parts = []
        
    def add_from_db(self, category, part_name):
        """Adds a part directly from the built-in database."""
        if category in COMPONENTS_DB and part_name in COMPONENTS_DB[category]:
            part_info = COMPONENTS_DB[category][part_name]
            self.parts.append({
                "category": category,
                "name": part_name,
                "weight": part_info["weight"],
                "price": part_info["price"]
            })
            print(f"Added: {part_name} ({category})")
        else:
            print(f"ERROR: Could not find '{part_name}' in category '{category}'.")

    def add_custom_part(self, category, name, weight, price):
        """Allows you to add any custom part, like a frame, saddle, or pedals."""
        self.parts.append({
            "category": category,
            "name": name,
            "weight": weight,
            "price": price
        })
        print(f"Added Custom: {name} ({category})")

    def print_summary(self):
        """Calculates and prints the final weight and price in a nice format."""
        total_weight = 0
        total_price = 0
        
        print("\n" + "="*50)
        print(f"BIKE BUILD SUMMARY: {self.name}")
        print("="*50)
        
        # Print each part formatted nicely
        for part in self.parts:
            total_weight += part['weight']
            total_price += part['price']
            print(f"{part['category']:<20} | {part['name']:<25} | {part['weight']}g | ${part['price']}")
            
        print("-" * 50)
        
        # Convert weight to kg and lbs for readability
        weight_kg = total_weight / 1000
        weight_lbs = total_weight * 0.00220462
        
        print(f"TOTAL PRICE:  ${total_price:,.2f}")
        print(f"TOTAL WEIGHT: {total_weight}g ({weight_kg:.2f} kg / {weight_lbs:.2f} lbs)")
        print("="*50 + "\n")


# ==========================================
# YOUR CONFIGURATIONS TO TEST
# ==========================================

if __name__ == "__main__":
    # Create a new bike build instance
    my_bike = BikeBuild("Frankenstein 105 / Ultegra Build")

    # 1. Custom Inputs (Frame, Saddle, Cockpit, etc.)
    # You can change the numbers here based on the frame you are looking at
    my_bike.add_custom_part("Frame + Fork", "Quick-Pro ER ONE", weight=900+445, price=2100)
    my_bike.add_custom_part("Cockpit", "Tavelo", weight=330, price=300)
    my_bike.add_custom_part("Seatpost", "Quick Pro", weight=160, price=0)
    my_bike.add_custom_part("Saddle", "Selle San Marco Aspide", weight=212, price=0)
    my_bike.add_custom_part("Pedals", "Shimano Ultegra", weight=248, price=200)

    # 2. Add Groupset (Mixing 105 and Ultegra as requested)
    my_bike.add_from_db("Shifters", "105 R7170")
    my_bike.add_from_db("Rear Derailleur", "105 R7150")
    my_bike.add_from_db("Front Derailleur", "105 R7150")
    my_bike.add_from_db("Crankset", "105 R7100")
    my_bike.add_from_db("Brakes (Calipers)", "105 R7170")
    my_bike.add_from_db("Rotors (Pair)", "105 SM-RT70 (160mm)")
    my_bike.add_from_db("Chain", "105 / SLX")
    
    # Swapping in the Ultegra Cassette!
    my_bike.add_from_db("Cassette", "Ultegra R8100 (11-30)")

    # 3. Add Wheels and Tires
    #my_bike.add_from_db("Wheelset", "DT Swiss ARC 1100 Dicut 40")
    my_bike.add_from_db("Tires (Pair)", "Continental GP 5000 S TR (28mm)")
    
    # Extras (Tubes/Sealant, Bartape)
    my_bike.add_custom_part("Extras", "Sealant, Valves, Bartape", weight=150, price=75)
    my_bike.add_custom_part("Wheelset", "Farsports Wheelset", weight=1180, price=1559)

    # 4. Generate the final receipt
    my_bike.print_summary()