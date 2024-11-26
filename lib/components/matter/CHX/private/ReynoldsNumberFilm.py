def ReynoldsNumberFilm(MassFlowRate_Film, dynViscosity_Film, CharactLength, CHX_Type):
    """
    ReynoldsNumberFilm:
    Calculates the Reynolds number of the film as a function of the condensate mass flow.
    """
    if CHX_Type in {'VerticalTube', 'HorizontalTube'}:
        Re_Film = MassFlowRate_Film / (3.14159 * CharactLength * dynViscosity_Film)
        return Re_Film
    else:
        print("Re_Film: Only VerticalTube or HorizontalTube implemented yet")
        return None
