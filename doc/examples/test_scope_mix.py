r"""
Preamble:
    profile:
        module
    scope:
        public
    normative_sections:
        Contract, Public_classes, Public_functions 
Contract:
    general:
        |Must| represent a public module.
Public_classes:
    X_public, X_extension, X_core
Public_functions:
    f_public, f_extension, f_core
"""

from __future__ import annotations

def f_public() -> None:
    r"""
    Preamble:
        profile:
            function
        scope:
            public
        normative_sections:
            Contract, Parameters, Returns, Raises
    Contract:
        general:
            |Must| represent a public function.
    Parameters:
    Returns:
    Raises:
    """
def f_extension() -> None:
    r"""
    Preamble:
        profile:
            function
        scope:
            extension
        normative_sections:
            Contract, Parameters, Returns, Raises, See_also
    Contract:
        general:
            |Must| represent an extension function.
    Parameters:
    Returns:
    Raises:
    See_also:
        f_public
    """
def f_core() -> None:
    r"""
    Preamble:
        profile:
            function
        scope:
            core
        normative_sections:
            Contract, Parameters, Returns, Raises, See_also
    Contract:
        general:
            |Must| represent a core function.
    Parameters:
    Returns:
    Raises:
    See_also:
        f_public, f_extension
    """

class X_public:
    r"""
    Preamble:
        profile:
            class
        scope:
            public
        normative_sections:
            Contract, Public_classes, Public_methods
    Contract:
        general:
            |Must| represent a public class.
        constructor:
    Public_classes:
        Y_extension, Y_core
    Public_methods:
        m_extension, m_core
    """
    class Y_extension:
        r"""
        Preamble:
            profile:
                class
            scope:
                extension
            normative_sections:
                Contract
        Contract:
            general:
            constructor:
        """
    class Y_core:
        r"""
        Preamble:
            profile:
                class
            scope:
                core
            normative_sections:
                Contract, See_also
        Contract:
            general:
            constructor:
        See_also:
            X_public.Y_extension
        """
    def m_extension(self) -> None:
        r"""
        Preamble:
            profile:
                method
            scope:
                extension
            normative_sections:
                Contract, Parameters, Returns, Raises
        Contract:
            general:
                |Must| represent an extension method.
        Parameters:
        Returns:
        Raises:
        """
    def m_core(self) -> None:
        r"""
        Preamble:
            profile:
                method
            scope:
                core
            normative_sections:
                Contract, Parameters, Returns, Raises, See_also
        Contract:
            general:
                |Must| represent a core method.
        Parameters:
        Returns:
        Raises:
        See_also:
            X_public.m_extension
        """

class X_extension:
    r"""
    Preamble:
        profile:
            class
        scope:
            extension
        normative_sections:
            Contract, Public_classes, Public_methods
    Contract:
        general:
            |Must| represent an extension class.
        constructor:
    Public_classes:
        Y_core
    Public_methods:
        m_core
    """
    class Y_core:
        r"""
        Preamble:
            profile:
                class
            scope:
                core
            normative_sections:
                Contract, See_also
        Contract:
            general:
            constructor:
        See_also:
            X_public.Y_extension, X_public.Y_core
        """
    def m_core(self) -> None:
        r"""
        Preamble:
            profile:
                method
            scope:
                core
            normative_sections:
                Contract, Parameters, Returns, Raises, See_also
        Contract:
            general:
                |Must| represent a core method.
        Parameters:
        Returns:
        Raises:
        See_also:
            X_public.m_extension, X_public.m_core
        """

class X_core:
    r"""
    Preamble:
        profile:
            class
        scope:
            core
        normative_sections:
            Contract, See_also
    Contract:
        general:
            |Must| represent a core class.
        constructor:
    See_also:
        X_public.Y_extension, X_public.Y_core
        X_extension.Y_core
    """
