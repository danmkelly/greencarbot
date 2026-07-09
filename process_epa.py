import pandas as pd
import numpy as np

PATH = r'C:\Users\dan_m\OneDrive\Education\PGDip Science AI for Business\S3 01 Emerging AI Technologies and Sustainability\CA1\Prototype\20250814 MY25 ICE,EV,PHEV For DOE R2public.xlsx'
OUTPUT = r'C:\Users\dan_m\OneDrive\Education\PGDip Science AI for Business\S3 01 Emerging AI Technologies and Sustainability\CA1\Prototype\epa_vehicle_catalogue.csv'

FACTOR = 1.60934

# ===========================================================================
# Helper: build column rename dict from {original_name: new_name} for cols
# that exist in a DataFrame
# ===========================================================================


def select_and_rename(df, col_map):
    """Rename columns using col_map {old: new}, keep only mapped+existing cols."""
    existing = {k: v for k, v in col_map.items() if k in df.columns}
    return df[list(existing.keys())].rename(columns=existing)


# ===========================================================================
# 1.  FEguide  (ICE + HEV)
# ===========================================================================
df_ice = pd.read_excel(PATH, sheet_name='FEguide')

ice_map = {
    'Mfr Name':                        'Make',
    'Carline':                         'Model',
    'Carline Class Desc':              'Vehicle Class',
    'Fuel Usage Desc - Conventional Fuel': 'Fuel Type',
    'City FE (Guide) - Conventional Fuel':  'City MPG',
    'Hwy FE (Guide) - Conventional Fuel':   'Highway MPG',
    'Comb FE (Guide) - Conventional Fuel':  'Combined MPG',
    'Comb CO2 Rounded Adjusted (as shown on FE Label)': 'CO2 Emissions (g/mi)',
    'Drive Desc':                      'Drive Type',
    'Police/Emerg?':                   'Police/Emerg',
}
df_ice = select_and_rename(df_ice, ice_map)
df_ice['Battery Capacity (kWh)'] = 0.0
df_ice['Electric Range (miles)'] = 0.0

# ===========================================================================
# 2.  EV
# ===========================================================================
df_ev = pd.read_excel(PATH, sheet_name='EV')

ev_map = {
    'Mfr Name':                        'Make',
    'Carline':                         'Model',
    'Carline Class Desc':              'Vehicle Class',
    'City FE (Guide) - Conventional Fuel':  'City MPG',
    'Hwy FE (Guide) - Conventional Fuel':   'Highway MPG',
    'Comb FE (Guide) - Conventional Fuel':  'Combined MPG',
    'Comb CO2 Rounded Adjusted (as shown on FE Label)': 'CO2 Emissions (g/mi)',
    'Drive Desc':                      'Drive Type',
    'Police/Emerg?':                   'Police/Emerg',
    'Comb Range as shown on FE Label (miles)': 'Electric Range (miles)',
}
df_ev = select_and_rename(df_ev, ev_map)
df_ev['Fuel Type'] = 'Electricity'

# Battery capacity from voltage × Ah / 1000
df_ev_full = pd.read_excel(PATH, sheet_name='EV')
volt_ev = pd.to_numeric(df_ev_full['Total Voltage for Battery Pack(s)'], errors='coerce')
ah_ev   = pd.to_numeric(df_ev_full['Batt Energy Capacity (Amp-hrs)'], errors='coerce')
df_ev['Battery Capacity (kWh)'] = (volt_ev * ah_ev / 1000.0).fillna(0)

# ===========================================================================
# 3.  PHEV  (positional approach because of duplicate headers)
# ===========================================================================
df_raw = pd.read_excel(PATH, sheet_name='PHEV', header=None)
phev_headers = df_raw.iloc[8].tolist()   # row 8 = column names

# Start data from row 11 (skip title rows)
df_phev_data = df_raw.iloc[11:].copy()
df_phev_data.columns = phev_headers

# Keep only rows where col 0 (Model Year) is numeric
mask = pd.to_numeric(df_phev_data.iloc[:, 0], errors='coerce').notna()
df_phev_data = df_phev_data[mask].copy().reset_index(drop=True)

# Each vehicle has TWO consecutive rows; keep the FIRST (CD/electric) of each pair
df_phev_data = df_phev_data.iloc[::2].copy().reset_index(drop=True)

# Build PHEV result DataFrame with explicit position → name mapping
df_phev = pd.DataFrame()

df_phev['Make']         = df_phev_data.iloc[:, 1].values
df_phev['Model']        = df_phev_data.iloc[:, 3].values
df_phev['Vehicle Class'] = df_phev_data.iloc[:, 69].values
df_phev['Fuel Type']    = df_phev_data.iloc[:, 33].values
df_phev['City MPG']     = pd.to_numeric(df_phev_data.iloc[:, 9], errors='coerce').values
df_phev['Highway MPG']  = pd.to_numeric(df_phev_data.iloc[:, 10], errors='coerce').values
df_phev['Combined MPG'] = pd.to_numeric(df_phev_data.iloc[:, 11], errors='coerce').values
df_phev['CO2 Emissions (g/mi)'] = pd.to_numeric(df_phev_data.iloc[:, 155], errors='coerce').values
df_phev['Drive Type']   = df_phev_data.iloc[:, 28].values
df_phev['Police/Emerg'] = df_phev_data.iloc[:, 80].values

# Electric range (combined, miles) – col 167
er = pd.to_numeric(df_phev_data.iloc[:, 167], errors='coerce')
df_phev['Electric Range (miles)'] = er.fillna(0).values

# Battery capacity
volt_phev = pd.to_numeric(df_phev_data.iloc[:, 93], errors='coerce')
ah_phev   = pd.to_numeric(df_phev_data.iloc[:, 94], errors='coerce')
df_phev['Battery Capacity (kWh)'] = (volt_phev * ah_phev / 1000.0).fillna(0).values

# ===========================================================================
# 4.  Combine
# ===========================================================================
common_cols = [
    'Make', 'Model', 'Vehicle Class', 'Fuel Type',
    'Battery Capacity (kWh)', 'Electric Range (miles)',
    'City MPG', 'Highway MPG', 'Combined MPG',
    'CO2 Emissions (g/mi)', 'Drive Type', 'Police/Emerg',
]

df_all = pd.concat(
    [df_ice[common_cols], df_ev[common_cols], df_phev[common_cols]],
    ignore_index=True,
)

# ===========================================================================
# 5.  Filter & clean
# ===========================================================================

# Remove police / emergency
df_all = df_all[df_all['Police/Emerg'].astype(str).str.upper() != 'Y']

# Remove rows with missing Fuel Type
df_all = df_all[df_all['Fuel Type'].notna() & (df_all['Fuel Type'].astype(str).str.strip() != '')]

# Coerce CO2 to numeric and drop missing
df_all['CO2 Emissions (g/mi)'] = pd.to_numeric(df_all['CO2 Emissions (g/mi)'], errors='coerce')
df_all = df_all[df_all['CO2 Emissions (g/mi)'].notna()]

# Exclude heavy-duty pickups ("Standard Pick-up Trucks")
df_all = df_all[~df_all['Vehicle Class'].astype(str).str.contains(
    r'Standard Pick-up Trucks', case=False, na=False)]

# Exclude cab-chassis and special-purpose non-minivan
exclude_pattern = r'cab chassis|Special Purpose Vehicle\s*\d*WD$'
df_all = df_all[~df_all['Vehicle Class'].astype(str).str.contains(
    exclude_pattern, case=False, na=False)]

# Drop rows without a Vehicle Class
df_all = df_all[df_all['Vehicle Class'].notna()]

# ===========================================================================
# 6.  Normalise
# ===========================================================================

# Fuel Type simplification
fuel_map = {
    'Gasoline (Regular Unleaded Recommended)':   'Gasoline',
    'Gasoline (Premium Unleaded Required)':      'Gasoline',
    'Gasoline (Premium Unleaded Recommended)':   'Gasoline',
    'Gasoline (Mid Grade Unleaded Recommended)': 'Gasoline',
    'Diesel, ultra low sulfur (15 ppm, maximum)': 'Diesel',
    'Electricity':                                'Electricity',
}
df_all['Fuel Type'] = df_all['Fuel Type'].map(fuel_map).fillna(df_all['Fuel Type'])

# Normalise Body Type from Vehicle Class
def body_type(vc):
    vc = str(vc).lower()
    if 'suv' in vc:
        return 'SUV'
    if 'car' in vc or 'two seater' in vc:
        return 'Car'
    if 'wagon' in vc:
        return 'Wagon'
    if 'van' in vc or 'minivan' in vc:
        return 'Van'
    if 'pick-up' in vc or 'pickup' in vc:
        return 'Pickup'
    return 'Other'

df_all['Body Type'] = df_all['Vehicle Class'].apply(body_type)

# Unit conversions
df_all['Electric Range (miles)'] = pd.to_numeric(df_all['Electric Range (miles)'], errors='coerce').fillna(0)
df_all['Electric Range (km)']  = df_all['Electric Range (miles)'] * FACTOR
df_all['CO2 Emissions (g/km)'] = df_all['CO2 Emissions (g/mi)'] / FACTOR

# Clean MPG columns
for c in ['City MPG', 'Highway MPG', 'Combined MPG']:
    df_all[c] = pd.to_numeric(df_all[c], errors='coerce')

# Clean Make / Model strings
df_all['Make']  = df_all['Make'].astype(str).str.strip().str.title()
df_all['Model'] = df_all['Model'].astype(str).str.strip()
df_all['Vehicle Class'] = df_all['Vehicle Class'].astype(str).str.strip()

# Placeholders for columns not in the EPA dataset
df_all['Seats']     = np.nan
df_all['Footprint'] = np.nan

# ===========================================================================
# 7.  Final columns & save
# ===========================================================================
final_cols = [
    'Make', 'Model', 'Vehicle Class', 'Body Type', 'Seats',
    'Fuel Type', 'Battery Capacity (kWh)', 'Electric Range (km)',
    'City MPG', 'Highway MPG', 'Combined MPG',
    'CO2 Emissions (g/km)', 'Drive Type', 'Footprint',
]

df_out = df_all[final_cols].copy()
df_out = df_out.replace([np.inf, -np.inf], np.nan)
df_out.to_csv(OUTPUT, index=False, na_rep='')

print(f'Done – {len(df_out)} rows written to {OUTPUT}')
print(f'\nVehicle Class distribution ({df_out["Vehicle Class"].nunique()} unique):')
print(df_out['Vehicle Class'].value_counts().to_string())
print(f'\nBody Type distribution:')
print(df_out['Body Type'].value_counts().to_string())
print(f'\nFuel Type distribution:')
print(df_out['Fuel Type'].value_counts().to_string())
print(f'\nFirst 5 rows:')
print(df_out.head().to_string())
