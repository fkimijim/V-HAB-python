import os
import time
import datetime
import requests
import pandas as pd
from collections import defaultdict
from math import exp

# Confirm execution
proceed = input(
    "Are you sure you want to run this script? "
    "You will require an internet connection. Depending on your connection speed, "
    "the script will run for several tens of minutes. This script will overwrite all data files. Proceed? (yes/no): "
)
if proceed.lower() != "yes":
    print("Script execution cancelled.")
    exit()

# NIST Scraper Configuration
substance_data = {
    "Ar": {"ID": 7440371, "THigh": 700, "TLow": 84.0, "DHigh": 1416},
    "CH4": {"ID": 74828, "THigh": 625, "TLow": 91.0, "DHigh": 451},
    "CH4O": {"ID": 67561, "THigh": 620, "TLow": 176.0, "DHigh": 904},
    "CO": {"ID": 630080, "THigh": 500, "TLow": 67.0, "DHigh": 849},
    "CO2": {"ID": 124389, "THigh": 1100, "TLow": 217.0, "DHigh": 1178},
    "H2": {"ID": 1333740, "THigh": 1000, "TLow": 14.0, "DHigh": 77},
    "H2O": {"ID": 7732185, "THigh": 1275, "TLow": 273.16, "DHigh": 1218},
    "N2": {"ID": 7727379, "THigh": 2000, "TLow": 63.15, "DHigh": 867},
    "NH3": {"ID": 7664417, "THigh": 700, "TLow": 195.5, "DHigh": 732},
    "O2": {"ID": 7782447, "THigh": 1000, "TLow": 54.37, "DHigh": 1237},
}

output_path = "NIST_Data/"
os.makedirs(output_path, exist_ok=True)

# Prepare unit conversions
unit_conversion_factors = {
    "-": 1,
    "K": 1,
    "MPa": 1e6,
    "kJ/kg": 1e3,
    "J/g*K": 1e3,
    "kg/m3": 1,
    "m3/kg": 1,
    "m/s": 1,
    "K/MPa": 1e-6,
    "Pa*s": 1,
    "W/m*K": 1,
}
converted_units = {"MPa": "Pa", "kJ/kg": "J/kg", "J/g*K": "J/kg*K", "K/MPa": "K/Pa"}

# Scraper Settings
starting_density = 0
starting_exponent = -7
starting_pressure = 1e-6  # MPa
max_pressure = 30  # MPa

# Calculate the total number of scrapes
total_scrapes = sum(
    [
        sum([exp(starting_exponent + 0.1 * i) for i in range(1000)])
        for _, v in substance_data.items()
    ]
)

current_scrape = 0
error_counter = 0
start_time = datetime.datetime.now()

# Main scraping loop
for key, data in substance_data.items():
    print(f"Processing {key}...")

    # Isochoric Scraping
    isochoric_data = []
    density = starting_density
    exponent = starting_exponent
    while density < data["DHigh"]:
        url = (
            f"http://webbook.nist.gov/cgi/fluid.cgi?Action=Data&Wide=on&ID=C{data['ID']}&"
            f"Type=IsoChor&Digits=12&THigh={data['THigh']}&TLow={data['TLow']}&TInc=5&D={density}&"
            f"RefState=DEF&TUnit=K&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=Pa*s&STUnit=N%2Fm"
        )
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            raw_data = response.text
        except requests.exceptions.RequestException as e:
            print(f"Error during isochoric scrape for {key} at density {density}: {e}")
            error_counter += 1
            break

        raw_data = (
            raw_data.replace("infinite", "Inf")
            .replace("undefined", "NaN")
            .replace("Cv", "Isochoric Heat Capacity")
            .replace("Cp", "Isobaric Heat Capacity")
        )

        # Process raw data
        rows = raw_data.split("\n")
        headers = rows[0].split("\t")
        data_rows = [row.split("\t") for row in rows[1:] if row]

        for row in data_rows:
            isochoric_data.append([float(val) if val not in ("Inf", "NaN") else val for val in row])

        # Increment density
        if density < 5:
            density += exp(exponent)
            exponent += 0.1
        elif density < 50:
            density += 10
        else:
            density += 100

    # Save Isochoric Data
    isochoric_file = os.path.join(output_path, f"{key}_Isochoric.csv")
    pd.DataFrame(isochoric_data, columns=headers).to_csv(isochoric_file, index=False)

    # Isobaric Scraping
    isobaric_data = []
    pressure = starting_pressure
    while pressure < max_pressure:
        url = (
            f"http://webbook.nist.gov/cgi/fluid.cgi?Action=Data&Wide=on&ID=C{data['ID']}&"
            f"Type=IsoBar&Digits=12&THigh={data['THigh']}&TLow={data['TLow']}&TInc=5&P={pressure}&"
            f"RefState=DEF&TUnit=K&PUnit=MPa&DUnit=kg%2Fm3&HUnit=kJ%2Fkg&WUnit=m%2Fs&VisUnit=Pa*s&STUnit=N%2Fm"
        )
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            raw_data = response.text
        except requests.exceptions.RequestException as e:
            print(f"Error during isobaric scrape for {key} at pressure {pressure}: {e}")
            error_counter += 1
            break

        raw_data = (
            raw_data.replace("infinite", "Inf")
            .replace("undefined", "NaN")
            .replace("Cv", "Isochoric Heat Capacity")
            .replace("Cp", "Isobaric Heat Capacity")
        )

        # Process raw data
        rows = raw_data.split("\n")
        headers = rows[0].split("\t")
        data_rows = [row.split("\t") for row in rows[1:] if row]

        for row in data_rows:
            isobaric_data.append([float(val) if val not in ("Inf", "NaN") else val for val in row])

        # Increment pressure
        if pressure < 0.01:
            pressure += 0.001
        elif pressure < 0.2:
            pressure += 0.01
        elif pressure < 1:
            pressure += 0.1
        else:
            pressure += 0.5

    # Save Isobaric Data
    isobaric_file = os.path.join(output_path, f"{key}_Isobaric.csv")
    pd.DataFrame(isobaric_data, columns=headers).to_csv(isobaric_file, index=False)

# Summary
end_time = datetime.datetime.now()
elapsed_time = end_time - start_time
print(f"Scraping completed in {elapsed_time}. Errors encountered: {error_counter}")
