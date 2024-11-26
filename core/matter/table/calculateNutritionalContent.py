def calculate_nutritional_content(self, oPhase):
    """
    Calculate the nutritional content of a given phase.
    Returns a dictionary containing the nutritional data.
    """
    # Initialize
    ttxResults = {}

    # Initialize totals
    ttxResults['EdibleTotal'] = {
        'Substance': 'Total',
        'Mass': 0,
        'DryMass': 0,
        'ProteinMass': 0,
        'LipidMass': 0,
        'CarbohydrateMass': 0,
        'AshMass': 0,
        'TotalEnergy': 0,
        'ProteinEnergy': 0,
        'LipidEnergy': 0,
        'CarbohydrateEnergy': 0,
        'CalciumMass': 0,
        'IronMass': 0,
        'MagnesiumMass': 0,
        'PhosphorusMass': 0,
        'PotassiumMass': 0,
        'SodiumMass': 0,
        'ZincMass': 0,
        'CopperMass': 0,
        'ManganeseMass': 0,
        'SeleniumMass': 0,
        'FluorideMass': 0,
        'VitaminCMass': 0,
        'ThiaminMass': 0,
        'RiboflavinMass': 0,
        'NiacinMass': 0,
        'PantothenicAcidMass': 0,
        'VitaminB6Mass': 0,
        'FolateMass': 0,
        'VitaminB12Mass': 0,
        'VitaminAMass': 0,
        'VitaminEMass': 0,
        'VitaminDMass': 0,
        'VitaminKMass': 0,
        'TryptophanMass': 0,
        'ThreonineMass': 0,
        'IsoleucineMass': 0,
        'LeucineMass': 0,
        'LysineMass': 0,
        'MethionineMass': 0,
        'CystineMass': 0,
        'PhenylalanineMass': 0,
        'TyrosineMass': 0,
        'ValineMass': 0,
        'HistidineMass': 0,
    }

    # Calculate for each edible substance
    for sSubstance in self.csEdibleSubstances:
        if oPhase.afMass[self.tiN2I[sSubstance]] != 0:
            # Get nutrient data
            txNutrientData = self.ttxMatter[sSubstance]['txNutrientData']

            # Initialize substance-specific results
            ttxResults[sSubstance] = {
                'Substance': sSubstance,
                'Mass': oPhase.afMass[self.tiN2I[sSubstance]],
                'DryMass': oPhase.afMass[self.tiN2I[sSubstance]] * (1 - txNutrientData['fWaterMass']),
            }

            # Protein, lipid, carbohydrate, and ash content
            dry_mass = ttxResults[sSubstance]['DryMass']
            ttxResults[sSubstance]['ProteinMass'] = dry_mass * txNutrientData['fProteinDMF']
            ttxResults[sSubstance]['LipidMass'] = dry_mass * txNutrientData['fLipidDMF']
            ttxResults[sSubstance]['CarbohydrateMass'] = dry_mass * txNutrientData['fCarbohydrateDMF']
            ttxResults[sSubstance]['AshMass'] = dry_mass - (
                ttxResults[sSubstance]['ProteinMass'] +
                ttxResults[sSubstance]['LipidMass'] +
                ttxResults[sSubstance]['CarbohydrateMass']
            )

            # Energy content
            ttxResults[sSubstance]['TotalEnergy'] = txNutrientData['fEnergyMass'] * ttxResults[sSubstance]['Mass']
            ttxResults[sSubstance]['ProteinEnergy'] = ttxResults[sSubstance]['ProteinMass'] * 17e6
            ttxResults[sSubstance]['LipidEnergy'] = ttxResults[sSubstance]['LipidMass'] * 37e6
            ttxResults[sSubstance]['CarbohydrateEnergy'] = ttxResults[sSubstance]['CarbohydrateMass'] * 17e6

            # Mineral content
            for mineral in ['Calcium', 'Iron', 'Magnesium', 'Phosphorus', 'Potassium', 'Sodium', 'Zinc',
                            'Copper', 'Manganese', 'Selenium', 'Fluoride']:
                ttxResults[sSubstance][f'{mineral}Mass'] = dry_mass * txNutrientData[f'f{mineral}DMF']

            # Vitamin content
            for vitamin in ['VitaminC', 'Thiamin', 'Riboflavin', 'Niacin', 'PantothenicAcid', 'VitaminB6', 'Folate',
                            'VitaminB12', 'VitaminA', 'VitaminE', 'VitaminD', 'VitaminK']:
                ttxResults[sSubstance][f'{vitamin}Mass'] = dry_mass * txNutrientData[f'f{vitamin}DMF']

            # Amino acid content
            for amino_acid in ['Tryptophan', 'Threonine', 'Isoleucine', 'Leucine', 'Lysine', 'Methionine', 'Cystine',
                               'Phenylalanine', 'Tyrosine', 'Valine', 'Histidine']:
                ttxResults[sSubstance][f'{amino_acid}Mass'] = dry_mass * txNutrientData[f'f{amino_acid}DMF']

            # Update totals
            for key in ttxResults[sSubstance]:
                if key != 'Substance':
                    ttxResults['EdibleTotal'][key] += ttxResults[sSubstance][key]

    return ttxResults
