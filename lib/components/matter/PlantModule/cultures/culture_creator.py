import pickle

# Number of Cultures
iCulture = 12

# Define a function to create a culture dictionary
def create_culture(sCultureName, sPlantSpecies, fGrowthArea, fHarvestTime, iConsecutiveGenerations, fPPFD, fH, mfSowTime, mfPlantMassInit=None, fCO2=None):
    culture = {
        "sCultureName": sCultureName,
        "sPlantSpecies": sPlantSpecies,
        "fGrowthArea": fGrowthArea,
        "fHarvestTime": fHarvestTime,
        "iConsecutiveGenerations": iConsecutiveGenerations,
        "fPPFD": fPPFD,
        "fH": fH,
        "mfSowTime": mfSowTime,
    }
    if mfPlantMassInit is not None:
        culture["mfPlantMassInit"] = mfPlantMassInit
    if fCO2 is not None:
        culture["fCO2"] = fCO2
    return culture

# Define all cultures
cultures = {
    "Lettuce1": create_culture("Lettuce1", "Lettuce", 0.124, 35, 1, 300, 16, 7257600, [0.0, 0.0]),
    "Lettuce2": create_culture("Lettuce2", "Lettuce", 0.124, 35, 2, 300, 16, [4233600, 7862400], [0.7488, 0.02068]),
    "Lettuce3": create_culture("Lettuce3", "Lettuce", 0.124, 35, 1, 300, 16, 4838400, [0.3879, 0.01118]),
    "Lettuce4": create_culture("Lettuce4", "Lettuce", 0.124, 35, 1, 300, 16, 5443200, [0.1352, 0.004531]),
    "Lettuce5": create_culture("Lettuce5", "Lettuce", 0.124, 35, 1, 300, 16, 6048000, [0.03016, 0.001768]),
    "Lettuce6": create_culture("Lettuce6", "Lettuce", 0.124, 35, 1, 300, 16, 6652800, [0.002825, 0.001049]),
    "Tomato1": create_culture("Tomato1", "Tomato", 0.1925, 77, 1, 625, 12, 7257600, [0.0, 0.0]),
    "Tomato2": create_culture("Tomato2", "Tomato", 0.1925, 77, 1, 625, 12, 1209600, [1.811, 1.541]),
    "Tomato3": create_culture("Tomato3", "Tomato", 0.1925, 77, 1, 625, 12, 2419200, [1.01, 1.335]),
    "Tomato4": create_culture("Tomato4", "Tomato", 0.1925, 77, 1, 625, 12, 3628800, [0.001, 1.075]),
    "Tomato5": create_culture("Tomato5", "Tomato", 0.1925, 77, 1, 625, 12, 4838400, [0.001, 0.2867]),
    "Tomato6": create_culture("Tomato6", "Tomato", 0.1155, 77, 1, 625, 12, 6048000, [0.001, 0.02227]),
    "LettuceGenerations1": create_culture("LettuceGenerations", "Lettuce", 1, 30, 3, 300, 16, 0, fCO2=330),
}

# Select cultures based on iCulture
selected_cultures = {k: v for idx, (k, v) in enumerate(cultures.items()) if idx < iCulture}

# Save the cultures as a binary file
with open('Series3Case1.pkl', 'wb') as file:
    pickle.dump(selected_cultures, file)

print(f"Saved {len(selected_cultures)} cultures to 'Series3Case1.pkl'")
