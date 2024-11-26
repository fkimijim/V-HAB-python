def find_generated_mass_errors(oLastSimObj):
    """
    Debugging tool for mass balance errors.
    
    This function displays the system, store, and phase name for the phase
    with the highest mass balance error. It uses oLastSimObj as input
    and is designed to be used when a simulation is completed or paused.
    
    For the function to work, the matterObserver monitor needs to be added
    to the simulation infrastructure.
    """
    # Getting an array of all the phases in the model from the matter observer.
    aoPhases = oLastSimObj.toMonitors.oMatterObserver.aoPhases

    # Combining the afMassGenerated arrays in the phases into a matrix.
    mfMassGeneratedInPhases = [
        phase.afMassGenerated for phase in aoPhases
    ]
    mfMassGeneratedInPhases = list(zip(*mfMassGeneratedInPhases))

    # Calculating the sum of all generated mass per phase.
    afMassGeneratedInPhases = [sum(phase) for phase in mfMassGeneratedInPhases]

    # Finding the index of the phase that has the highest mass balance error.
    max_mass_generated = max(afMassGeneratedInPhases)
    aiMaxLostIndexes = [
        i for i, mass in enumerate(afMassGeneratedInPhases) if mass == max_mass_generated
    ]

    # Some user printouts
    print("\nThe highest mass generation occurred in:")

    # Looping through all phases with the maximum mass error and displaying their information.
    for iI in aiMaxLostIndexes:
        phase = aoPhases[iI]
        system_name = phase.oStore.oContainer.sName
        store_name = phase.oStore.sName
        phase_name = phase.sName
        total_mass_generated = sum(phase.afMassGenerated)
        print(
            f"The system {system_name} in Store {store_name} in Phase {phase_name} generated a total of {total_mass_generated:.2f} kg mass."
        )
