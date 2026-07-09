'''Add seat counts to the EPA vehicle catalogue using a heuristic mapping
from Vehicle Class, with known exceptions for specific models.

Source: Vehicle class → typical seat count mapping derived from:
  - Vehicle class definitions per EPA/NHTSA
  - Manufacturer specifications (known model-specific overrides)
'''

import pandas as pd
import numpy as np

INPUT = r'C:\Users\dan_m\OneDrive\Education\PGDip Science AI for Business\S3 01 Emerging AI Technologies and Sustainability\CA1\Prototype\epa_vehicle_catalogue.csv'
OUTPUT = r'C:\Users\dan_m\OneDrive\Education\PGDip Science AI for Business\S3 01 Emerging AI Technologies and Sustainability\CA1\Prototype\epa_vehicle_catalogue.csv'

df = pd.read_csv(INPUT)

# ---------------------------------------------------------------------------
# Base mapping: Vehicle Class -> typical seats
# ---------------------------------------------------------------------------
class_seat_map = {
    'Two Seaters': 2,
    'Minicompact Cars': 4,
    'Subcompact Cars': 5,
    'Compact Cars': 5,
    'Midsize Cars': 5,
    'Large Cars': 5,
    'Small Station Wagons': 5,
    'Midsize Station Wagons': 5,
    'Small SUV 2WD': 5,
    'Small SUV 4WD': 5,
    'Standard SUV 2WD': 5,
    'Standard SUV 4WD': 5,
    'Small Pick-up Trucks 2WD': 5,
    'Small Pick-up Trucks 4WD': 5,
    'Special Purpose Vehicle, minivan 2WD': 7,
    'Special Purpose Vehicle, minivan 4WD': 7,
}

df['Seats'] = df['Vehicle Class'].map(class_seat_map)

# ---------------------------------------------------------------------------
# Model-specific overrides: (Make substring, Model substring) -> seats
# These are standard configurations from manufacturer specs (MY2025)
# ---------------------------------------------------------------------------
model_overrides = [
    # Minivans with 8-seat option
    ('Honda', 'ODYSSEY', 8),           # Odyssey seats 8 (except Touring/Elite which are 7)
    ('Toyota', 'SIENNA', 8),           # Sienna seats 8 (except some trims at 7)
    ('Kia', 'Carnival', 8),            # Carnival seats 8 (except SX Prestige at 7)
    ('Fca Us Llc', 'Pacifica', 7),     # Pacifica 7 seats (Stow 'n Go)
    ('Fca Us Llc', 'Voyager', 7),      # Voyager seats 7

    # SUVs with 3-row/7-seat option (standard 3-row SUVs)
    ('Honda', 'PILOT', 8),             # Pilot seats 8
    ('Toyota', 'HIGHLANDER', 8),       # Highlander seats 8
    ('Toyota', 'GRAND HIGHLANDER', 7), # Grand Highlander seats 7
    ('Toyota', 'SEQUOIA', 8),          # Sequoia seats 8
    ('Toyota', '4RUNNER', 7),          # 4Runner (3-row option) → 5 for 2-row, 7 for 3-row - default 5
    ('Toyota', 'LAND CRUISER', 7),     # Land Cruiser seats 7
    ('Ford Motor Company', 'EXPEDITION', 8),  # Expedition seats 8
    ('Ford Motor Company', 'EXPLORER', 7),    # Explorer seats 7
    ('General Motors', 'TAHOE', 8),    # Tahoe seats 8
    ('General Motors', 'SUBURBAN', 8), # Suburban seats 8
    ('General Motors', 'YUKON', 8),    # Yukon seats 8
    ('General Motors', 'ESCALADE', 7), # Escalade seats 7
    ('General Motors', 'TRAVERSE', 8), # Traverse seats 8
    ('General Motors', 'ACADIA', 7),   # Acadia seats 7
    ('General Motors', 'ENCLAVE', 7),  # Enclave seats 7
    ('Nissan', 'ARMADA', 8),           # Armada seats 8
    ('Nissan', 'PATHFINDER', 8),       # Pathfinder seats 8
    ('Kia', 'TELLURIDE', 8),           # Telluride seats 8
    ('Kia', 'SORENTO', 7),             # Sorento seats 7 (3-row)
    ('Hyundai', 'PALISADE', 8),        # Palisade seats 8
    ('Hyundai', 'SANTA FE', 7),        # Santa Fe (3-row trim)
    ('Volkswagen Group Of', 'ATLAS', 7),   # Atlas seats 7
    ('Volkswagen Group Of', 'Q7', 7),      # Q7 seats 7
    ('Bmw', 'X7', 7),                      # X7 seats 7
    ('Bmw', 'X5', 5),                      # X5 seats 5 (3rd row optional, default 5)
    ('Mercedes-Benz', 'GLS', 7),          # GLS seats 7
    ('Mercedes-Benz', 'GLE', 5),          # GLE seats 5 (3rd row optional)
    ('Volvo', 'XC90', 7),                 # XC90 seats 7
    ('Mazda', 'CX-90', 8),                # CX-90 seats 8
    ('Mazda', 'CX-70', 5),                # CX-70 seats 5
    ('Subaru', 'ASCENT', 8),              # Ascent seats 8
    ('Jaguar Land Rover L', 'DEFENDER 130', 8),  # Defender 130 seats 8
    ('Jaguar Land Rover L', 'DISCOVERY', 7),     # Discovery seats 7
    ('Jaguar Land Rover L', 'RANGE ROVER', 5),   # Range Rover seats 5 (LWB optional 7)
    ('Lexus', 'TX', 7),                         # TX seats 7
    ('Lexus', 'GX', 7),                         # GX seats 7
    ('Lexus', 'LX', 7),                         # LX seats 7

    # Pickups - based on typical crew cab
    ('Honda', 'RIDGELINE', 5),          # Ridgeline crew cab
    ('Toyota', 'TACOMA', 5),           # Tacoma crew cab
    ('Ford Motor Company', 'MAVERICK', 5),  # Maverick crew cab
    ('Hyundai', 'SANTA CRUZ', 5),      # Santa Cruz
    ('General Motors', 'CANYON', 5),    # Canyon crew cab
    ('General Motors', 'COLORADO', 5),  # Colorado crew cab

    # Two-seater sports cars that might be misclassified
    ('Porsche', '911', 4),             # Porsche 911 has rear seats
    ('Porsche', '718', 2),             # Porsche 718 Boxster/Cayman
    ('Mazda', 'MX-5', 2),              # MX-5 Miata

    # Electric 3-row SUVs
    ('Kia', 'EV9', 7),                 # EV9 seats 7
    ('Rivian Automotive L', 'R1S', 7),  # R1S seats 7
    ('Tesla', 'MODEL X', 7),           # Model X seats 7
    ('Mercedes-Benz', 'EQS SUV', 7),   # EQS SUV seats 7
    ('Volkswagen Group Of', 'ID. BUZZ', 7),  # ID.Buzz seats 7

    # Wagons that are really SUVs / crossovers
    ('Subaru', 'OUTBACK', 5),           # Outback wagon
    ('Audi', 'A4 ALLROAD', 5),         # A4 Allroad
    ('Audi', 'A6 ALLROAD', 5),         # A6 Allroad

    # Specific EV overrides
    ('Tesla', 'MODEL 3', 5),
    ('Tesla', 'MODEL Y', 5),
    ('Tesla', 'MODEL S', 5),
    ('Tesla', 'CYBERTRUCK', 5),

    # Lucid
    ('Lucid Usa, Inc', 'AIR', 5),
    ('Lucid Usa, Inc', 'GRAVITY', 7),
]

# Apply overrides (case-insensitive matching)
for make_substr, model_substr, seats in model_overrides:
    mask = (df['Make'].str.contains(make_substr, case=False, na=False) &
            df['Model'].str.upper().str.contains(model_substr.upper(), na=False))
    df.loc[mask, 'Seats'] = seats

# --- Fill any remaining NaN with reasonable defaults ---
df['Seats'] = df['Seats'].fillna(5).astype(int)

# ---------------------------------------------------------------------------
# Save
# ---------------------------------------------------------------------------
df.to_csv(OUTPUT, index=False)

print(f'Updated {OUTPUT}')
print('\nSeat distribution:')
print(df['Seats'].value_counts().sort_index().to_string())
print(f'\nSeat coverage: {df["Seats"].notna().sum()} / {len(df)}')
print(f'Unique seat values: {sorted(df["Seats"].unique())}')
