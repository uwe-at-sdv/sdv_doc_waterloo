Versioning
----------

This section is informative.

Waterloo consists of several components that may evolve independently.
These currently include:

	* the Python library implementing the Waterloo docstring model,
	* the command line tool :wtrl_cmd:`waterlint`,
	* the JSON schema used for interchange and validation,
	* and potentially additional subsystems in the future.

Each subsystem maintains its own semantic version number of the form
:wtrl_value:`X.Y.Z`.

In addition to these subsystem versions, Waterloo defines a single
:wtrl_dfn:`main version`. The main version serves as the externally
communicated compatibility version of the Waterloo specification and
toolchain.

The main version is intended to remain stable over long periods of time.
A change of the major component indicates an intentional incompatibility
with previously valid Waterloo documents or tools.


Subsystem versions
..................

Subsystems may evolve independently and therefore maintain their own
version numbers. A version change in one subsystem does not directly
modify the version numbers of other subsystems.

Subsystem versions exist primarily to track development and internal
evolution of the individual components.


Main version derivation
.......................

The main version reflects the highest-order change among the subsystem
versions that occur within a release. The following interpretation is used:

	* If a subsystem performs a patch update (:wtrl_value:`X.Y.Z -> X.Y.(Z+1)`),
	  the patch component of the main version is increased.

	* If a subsystem performs a minor update (:wtrl_value:`X.Y.Z -> X.(Y+1).0`),
	  the minor component of the main version is increased and the patch
	  component is reset to zero.

	* If a subsystem performs a major update (:wtrl_value:`X.Y.Z -> (X+1).0.0`),
	  the major component of the main version is increased and the minor and
	  patch components are reset to zero.

If several subsystems change within the same release, the main version
reflects the highest-order change (major overrides minor, minor overrides
patch).


Compatibility interpretation
............................

The major component of the main version represents the compatibility
level of the Waterloo specification.

As a design goal, the major version is expected to remain stable for as
long as possible. A major version change would normally correspond to a
deliberate and incompatible modification of the specification, such as:

	* changes that invalidate previously valid Waterloo docstrings,
	* changes that alter the semantic interpretation of existing rules,
	* structural changes requiring modifications to existing documentation.

Such changes are expected to be rare.

Minor and patch updates are used for incremental evolution of the
specification, tooling improvements, clarifications, and additional
features that remain compatible with existing Waterloo documents.
