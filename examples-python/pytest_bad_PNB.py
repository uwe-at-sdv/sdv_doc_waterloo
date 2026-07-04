r"""
Preamble:
    profile:
        module
    normative_sections:
        Contract
Contract:
    general:
        Must provoke a warning for non-tokenized normativity keyword.
"""

from typing import Self

class X:
    r"""
    Preamble:
        profile:
            class
        normative_sections:
            Contract
    Contract:
        general:
            Must provoke a warning for non-tokenized normativity keyword.
        constructor:
    """
    def m(self) -> Self:
        r"""
        Preamble:
            profile:
                method
            normative_sections:
                Contract, Parameters, Raises, Returns
        Contract:
            general:
                Must provoke a warning for non-tokenized normativity keyword.
        Parameters:
        Raises:
        Returns:
            Must return Self
        """
        return self

def f() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            Must provoke a warning for non-tokenized normativity keyword.
    Parameters:
    Raises:
    Returns:
        Must return None
    """
    pass

def f_pnb_002_must_not() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            |must| not split negated normativity across two tokens.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_pnb_002_should_not() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            |should| not split negated normativity across two tokens.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_pnb_003_may_not() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            |may| not use ambiguous negated permission.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_pnb_004_should() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            The function should provoke a warning for non-tokenized normativity keyword.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_pnb_004_may() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            The function may provoke a warning for non-tokenized normativity keyword.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_pnb_004_hyphenated() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            A Must-Have phrase still uses a suspicious normativity keyword.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_pnb_004_must_period() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            The caller must.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_pnb_004_should_comma() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            The caller should, if possible.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_pnb_004_may_colon() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            May: return early.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_no_pnb_004_tokenized() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            |Must| use tokenized normativity keyword form.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_no_pnb_004_double_quoted() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            The word "must" is quoted here.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_no_pnb_004_single_quoted() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            The word 'should' is quoted here.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_no_pnb_004_backtick_quoted() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            The word `may` is quoted here.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_pnb_004_quoted_and_unquoted() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            The word "must" is quoted, but should is not.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_pnb_004_mixed_single_backtick_quote() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            The malformed quote 'Must` should warn.'
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_pnb_004_mixed_single_double_quote() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            The malformed quote 'Must" should warn.'
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_pnb_004_mixed_double_backtick_quote() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            The malformed quote "Must` should warn."
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_pnb_004_normative_description() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Description, Parameters, Raises, Returns
    Contract:
        general:
            |Must| use tokenized normativity keyword form.
    Description:
        This description must be treated as normative.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_no_pnb_004_informative_description() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            |Must| use tokenized normativity keyword form.
    Description:
        This description must remain ordinary informative prose.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

def f_no_pnb_004_notes() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Contract:
        general:
            |Must| use tokenized normativity keyword form.
    Parameters:
    Raises:
    Returns:
        |None|
    Notes:
        Reminder:
            This note must remain informative.
    """
    pass

def f_no_pnb_004_terminology() -> None:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Contract, Parameters, Raises, Returns
    Terminology:
        natural language:
            The word must can appear in an informative terminology entry.
    Contract:
        general:
            |Must| use tokenized normativity keyword form.
    Parameters:
    Raises:
    Returns:
        |None|
    """
    pass

class Y:
    r"""
    Preamble:
        profile:
            class
        normative_sections:
            Contract, Public_methods
    Contract:
        general:
            |Must| use tokenized normativity keyword form.
        constructor:
    Public_methods:
        m
    Method_overview:
        m:
            This method must be described informatively.
    """
    def m(self) -> None:
        r"""
        Preamble:
            profile:
                method
            normative_sections:
                Contract, Parameters, Raises, Returns
        Contract:
            general:
                |Must| use tokenized normativity keyword form.
        Parameters:
        Raises:
        Returns:
            |None|
        """
        pass
