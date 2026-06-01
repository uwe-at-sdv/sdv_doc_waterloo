r"""
Preamble:
    profile:
        module
    normative_sections:
        Definitions, Contract, Public_classes, Public_functions, Public_types, Public_variables, Public_constants, See_also
    scope:
        public
Definitions:
    ExampleTerm:
        ...
Terminology:
    Example term:
        ...
Contract:
    general:
        |Must| define the externally visible behavior of this module.
Description:
    ...
Notes:
    General note:
        ...
Public_classes:
Class_overview:
Public_functions:
Function_overview:
Public_types:
Public_variables:
Public_constants:
See_also:
"""

class X:
    r"""
    Preamble:
        profile:
            class
        normative_sections:
            Definitions, Contract, Derived_from, Public_classes, Public_methods, Public_types, Public_variables, Public_constants, Factory, See_also
        scope:
            public
    Definitions:
        ExampleTerm:
            ...
    Terminology:
        Example term:
            ...
    Contract:
        general:
            |Must| define the externally visible behavior of this class.
        constructor:
            |Must| define construction requirements and guarantees.
        traits:
    Description:
        ...
    Derived_from:
    Notes:
        General note:
            ...
    Public_classes:
    Class_overview:
    Public_methods:
    Method_overview:
    Public_types:
    Public_variables:
    Public_constants:
    Factory:
    See_also:
    """
    def m(self,a: int) -> int:
        r"""
        Preamble:
            profile:
                method
            normative_sections:
                Definitions, Contract, Parameters, Returns, Raises, See_also
            status:
                stable
            scope:
                public
        Definitions:
            ExampleTerm:
                ...
        Terminology:
            Example term:
                ...
        Contract:
            general:
                |Must| define the externally visible behavior of this method.
            requires:
                |Must| define preconditions for valid input.
            ensures:
                |Must| define postconditions for successful execution.
            invariants:
                |Must| preserve all documented invariants across valid calls.
        Description:
            ...
        Parameters:
            a:
                ...
        Returns:
            |Must| return ...
        Raises:
            BaseException:
                |Must| raise if...
        Notes:
            General note:
                ...
        See_also:
        """

def f(a: int) -> int:
    r"""
    Preamble:
        profile:
            function
        normative_sections:
            Definitions, Contract, Parameters, Returns, Raises, See_also
        status:
            stable
        scope:
            public
    Definitions:
        ExampleTerm:
            ...
    Terminology:
        Example term:
            ...
    Contract:
        general:
            |Must| define the externally visible behavior of this callable.
        requires:
            |Must| define preconditions for valid input.
        ensures:
            |Must| define postconditions for successful execution.
        invariants:
            |Must| preserve all documented invariants across valid calls.
    Description:
        ...
    Parameters:
        a:
            ...
    Returns:
        |Must| return ...
    Raises:
        BaseException:
            |Must| raise if...
    Notes:
        General note:
            ...
    See_also:
    """

