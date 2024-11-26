def vacuum():
    """
    Helper to create a vacuum matter phase.

    Returns:
    - cParams: Parameters for constructing the vacuum phase.
    - sDefaultPhase: Default phase type ('matter.phases.boundary.gas').
    """
    # Create cParams for the vacuum phase
    # Vacuum is represented as an empty mass struct, infinite volume,
    # cosmic background temperature (3 K), and zero pressure.
    cParams = [{"mass": {}}, float("inf"), 3, 0]

    # Default phase path for the vacuum phase
    sDefaultPhase = "matter.phases.boundary.gas"

    return cParams, sDefaultPhase
