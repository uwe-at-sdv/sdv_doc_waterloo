r"""
Preamble:
    profile:
        module
    normative_sections:
        Contract
Contract:
    general:
"""

class X:
    r"""
    Preamble:
        profile:
            class
        normative_sections:
            Contract
    Contract:
        general:
        constructor:
    """
    def m(self,a: int) -> int:
        r"""
        Preamble:
            profile:
                method
            normative_sections:
                Contract, Parameters, Returns, Raises
        Contract:
            general:
        Parameters:
            a:
                ...
        Returns:
        Raises:
        """

def f(a: int) -> int:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Returns, Raises
    Contract:
        general:
    Parameters:
        a:
            ...
    Returns:
    Raises:
    """

