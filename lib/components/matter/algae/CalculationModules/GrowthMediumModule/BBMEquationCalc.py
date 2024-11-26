import sympy as sp

# Define symbolic variables
fTargetC_Hplus = sp.symbols('fTargetC_Hplus')
fK_EDTA, fK_EDTAminus, fK_EDTA2minus, fK_EDTA3minus = sp.symbols('fK_EDTA fK_EDTAminus fK_EDTA2minus fK_EDTA3minus')
fK_CO2, fK_HCO3, fK_H3PO4, fK_H2PO4, fK_HPO4, fK_w = sp.symbols('fK_CO2 fK_HCO3 fK_H3PO4 fK_H2PO4 fK_HPO4 fK_w')
fC_EDTA_ini, fC_EDTA_tot, fC_Carb_tot = sp.symbols('fC_EDTA_ini fC_EDTA_tot fC_Carb_tot')
fC_H2PO4_ini, fC_HPO4_ini, fC_Phos_tot = sp.symbols('fC_H2PO4_ini fC_HPO4_ini fC_Phos_tot')
fC_KOH_ini, fC_OHminusPS, fC_AddedAcid, fHplusPhotosynthesis = sp.symbols('fC_KOH_ini fC_OHminusPS fC_AddedAcid fHplusPhotosynthesis')

# Define terms
# EDTA reactions
numerator_11 = fK_EDTA * fC_EDTA_tot * fTargetC_Hplus**3
denominator_11 = (
    fTargetC_Hplus**4
    + fTargetC_Hplus**3 * fK_EDTA
    + fTargetC_Hplus**2 * fK_EDTA * fK_EDTAminus
    + fTargetC_Hplus * fK_EDTA * fK_EDTAminus * fK_EDTA2minus
    + fK_EDTA * fK_EDTAminus * fK_EDTA2minus * fK_EDTA3minus
)
term_11 = numerator_11 / denominator_11

numerator_12 = fK_EDTA * fK_EDTAminus * fC_EDTA_tot * fTargetC_Hplus**2
term_12 = numerator_12 / denominator_11

numerator_13 = fK_EDTA * fK_EDTAminus * fK_EDTA2minus * fC_EDTA_tot * fTargetC_Hplus
term_13 = numerator_13 / denominator_11

numerator_14 = fK_EDTA * fK_EDTAminus * fK_EDTA2minus * fK_EDTA3minus * fC_EDTA_tot
term_14 = numerator_14 / denominator_11

# CO2 + H2O reactions
numerator_3 = fK_CO2 * fC_Carb_tot * fTargetC_Hplus
denominator_3 = fTargetC_Hplus**2 + fK_CO2 * fTargetC_Hplus + fK_CO2 * fK_HCO3
term_3 = numerator_3 / denominator_3

numerator_4 = fK_HCO3 * fK_CO2 * fC_Carb_tot
term_4 = numerator_4 / denominator_3

# H3PO4 reactions
numerator_5 = fK_H3PO4 * fC_Phos_tot * fTargetC_Hplus**2
denominator_5 = (
    fTargetC_Hplus**3
    + fTargetC_Hplus**2 * fK_H3PO4
    + fTargetC_Hplus * fK_H3PO4 * fK_H2PO4
    + fK_H3PO4 * fK_H2PO4 * fK_HPO4
)
term_5 = numerator_5 / denominator_5

numerator_6 = fK_H2PO4 * fK_H3PO4 * fC_Phos_tot * fTargetC_Hplus
term_6 = numerator_6 / denominator_5

numerator_7 = fK_H2PO4 * fK_H3PO4 * fK_HPO4 * fC_Phos_tot
term_7 = numerator_7 / denominator_5

# Autoprotolysis of water
numerator_8 = fK_w
denominator_8 = fTargetC_Hplus
term_8 = numerator_8 / denominator_8

# Charge balance equation
left_side = (
    fTargetC_Hplus
    + fC_KOH_ini
    + fC_H2PO4_ini
    + 2 * fC_HPO4_ini
    + fC_OHminusPS
    + fHplusPhotosynthesis
    + 2 * fC_EDTA_ini
)

right_side = (
    term_11
    + 2 * term_12
    + 3 * term_13
    + 4 * term_14
    + term_3
    + 2 * term_4
    + term_5
    + 2 * term_6
    + 3 * term_7
    + term_8
    + fC_AddedAcid
)

# Simplify the right side
right_side_simplified = sp.simplify(right_side)
numerator, denominator = sp.fraction(right_side_simplified)

# Multiply left side with denominator and simplify
left_multiplied = left_side * denominator
final = sp.expand(left_multiplied - numerator)

# Collect terms by powers of H+
final_collected = sp.collect(final, fTargetC_Hplus)

# Extract coefficients
coefficients = sp.Poly(final_collected, fTargetC_Hplus).coeffs()

# Display coefficients
for i, coef in enumerate(reversed(coefficients)):
    print(f"coef{i}: {coef}")
