r"""
Preamble:
	profile:
		module
	normative_sections:
		Contract, Public_classes, Public_variables, Public_types
Contract:
	general:
		|Must| demonstrate the HTML rendering of tables
Description:
	This module demonstrates the rendering of tables in the Sphinx extension
	and the pipeline JSON -> HTML5.
	|
	Tables can be used in the following sections:
	* |label|`Description`
	* |label|`Definitions.<item>`
	* |label|`Terminology.<item>`
	* |label|`Notes.<item>`
	* |label|`Factory.<item>`
	* |label|`Class_overview.<item>`
	* |label|`Function_overview.<item>`
	* |label|`Method_overview.<item>`
	* |label|`Returns`
	* |label|`Parameters.<item>`
	* |label|`Raises.<item>` (allowed although item-like)
	|
	They are not allowed in lists of strings:
	* |label|`Preamble.*`
	* |label|`Derived_from`
	|
	They are not allowed in item-like (sub)sections like:
	* |label|`Contract.general`
	* |label|`Contract.constructor`
	* |label|`Contract.requires`
	* |label|`Contract.ensures`
	* |label|`Contract.invariants`
Notes:
	Application:
		The following table shows where tables are allowed:
		|begin_table|
		|columns|
		Sections in canonical order |tab| Allowed / Applicable
		|rows|
		|label|`Preamble.*` |tab| no
		|label|`Definitions.<item>` |tab| yes
		|label|`Terminology.<item>` |tab| yes
		|label|`Contract.*` |tab| no
		|label|`Description` |tab| yes
		|label|`Derived_from` |tab| no
		|label|`Factory.<item>` |tab| yes
		|label|`Public_classes` |tab| no
		|label|`Class_overview` |tab| yes
		|label|`Public_functions` |tab| no
		|label|`Function_overview` |tab| yes
		|label|`Public_methods` |tab| no
		|label|`Method_overview` |tab| yes
		|label|`Public_types` |tab| yes
		|label|`Public_variables` |tab| yes
		|label|`Public_constants` |tab| yes
		|label|`Parameters.<item>` |tab| yes
		|label|`Returns` |tab| yes
		|label|`Raises.<item>` |tab| yes
		|label|`Notes.<item>` |tab| yes
		|label|`See_also` |tab| no
		|end_table|
Public_classes:
	X
Class_overview:
	X:
		The plugin controller. Plugins are initialized according to the following table:
		|begin_table|
		|columns|
		Name |tab| Initialization
		|rows|
		fancy_plugin_a |tab| |value|`LAZY`
		fancy_plugin_b |tab| |value|`LOAD`
		|end_table|
Public_variables:
	location:
		|begin_table|
		|title|
		Location for expensive computations
		|columns|
		Symbol |tab| Semantics
		|rows|
		|value|`LOCAL` |tab| Do computations on localhost
		|value|`REMOTE` |tab| Do computations on remote host
		|end_table|
Public_types:
	RemoteAccess_t:
		|begin_table|
		|title|
		Symbols which describe access to remote files
		|columns|
		Symbol |tab| Semantics
		|rows|
		|value|`"SSH"` |tab| Access remote files through ssh, sftp, scp. Requires public key on remote host.
		|value|`"HTTPS"` |tab| Access remote files through https. Requires token from remote host.
		|end_table|
"""

from __future__ import annotations
from typing import Any, Dict, Literal, TypeAlias
from enum import IntEnum

RemoteAccess_t: TypeAlias = Literal["SSH","HTTPS"]

class Location(IntEnum):
	LOCAL = 1,
	REMOTE = 2
	
location: Location = Location.LOCAL

class MyException(Exception):
	def __init__(self,error_code: int):
		self._error_code = error_code

def log(level: Literal["DEBUG","INFO","WARNING","ERROR","CRITICAL"],msg: str) -> None:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Raises, Returns
	Contract:
		general:
			|Must| demonstrate tables in subsection |label|`Parameters.<item>`.
		requires:
			|var|`msg` |must_not| be empty
		ensures:
			|Must_not| change the state of the module.
	Parameters:
		level:
			A string indicating the minimum severeness of messages to be logged.
			|begin_table|
			|columns|
			Symbol |tab| Semantics
			|rows|
			|value|`"DEBUG"` |tab| Rich debugging output, not recommended in productive environment
			|value|`"INFO"` |tab| Normal behaviour
			|value|`"WARNING"` |tab| Requires attention but most likely the system remains operational
			|value|`"ERROR"` |tab| Administrative action is required
			|value|`"CRITICAL"` |tab| System has become unusable
			|end_table|
		msg:
			The message to be logged
	Raises:
		ValueError:
			|Must| raise if |var|`msg` is empty.
	Returns:
		|None|
	"""
	pass

def init_nothrow() -> int:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Raises, Returns
	Contract:
		general:
			|Must| demonstrate tables in sections |label|`Description` and |label|`Returns`.
	Description:
		This function initializes the module. Relevant files are
		|begin_table|
		|columns|
		Path |tab| Purpose
		|rows|
		|file|`/etc/fancy.conf` |tab| Configuration
		|file|`/var/log/fancy.log` |tab| General log
		|file|`/var/log/fancy.auth.log` |tab| Log for authentication problems
		|end_table|
	Parameters:
	Raises:
	Returns:
		|Must| return one of the following values:
		|begin_table|
		|columns|
		Status |tab| String representation |tab| Semantics
		|rows|
		0 |tab| |value|`ok`		|tab| No error
		1 |tab| |value|`general_error`	|tab| General error
		2 |tab| |value|`io_error`	|tab| Error accessing file system
		3 |tab| |value|`bad_config`	|tab| Invalid configuration
		|end_table|
	"""
	return 0

def init() -> None:
	r"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Raises, Returns
	Contract:
		general:
			|Must| demonstrate tables in sections |label|`Raises`.
	Parameters:
	Raises:
		MyException:
			|Must| raise in case of an error in the controller
			|Must| provide an error codes according to the following scheme:
			|begin_table|
			|columns|
			Value |tab| String representation |tab| Semantics
			|rows|
			1 |tab| |value|`general_error`	|tab| General error
			2 |tab| |value|`io_error`	|tab| Error accessing file system
			3 |tab| |value|`bad_config`	|tab| Invalid configuration
			|end_table|
			|Must| raise if initialization of any of the plugins fails.
		NotImplementedError:
			|May| raise if implementation in any of the plugins is incomplete.
			|May| raise if implementation in any of the plugin registry classes is incomplete.
	Returns:
		|None|
	"""


class X:
	r"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Factory
	Contract:
		general:
			|Must| demonstrate a table with multiple groups
		constructor:
	Factory:
		make_X_minimal:
			|Must| create a minimal instance of |class|`X`.
		make_X_complete:
			|Must| create a complete instance of |class|`X`.
		make_X_by_config:
			|Must| create an instance of |class|`X` based on the configuration passed.
			|Must| accept a single parameter |var_type|`config:Dict[str,Any]`.
			Parameter |var|`config` is map of key-value pairs:
			|begin_table|
			|title|
			Required
			|columns|
			Key |tab| Type |tab| Requirements
			|rows|
			|var|`base_prime` |tab| |type|`int` |tab| Prime used for encryption.
			|title|
			Optional
			|columns|
			Key |tab| Type |tab| Default
			|rows|
			|var|`path_to_log` |tab| |type|`str` |tab| |file|`/var/log/fancy.log`.
			|end_table|
	Notes:
		Test:
			The |label|`Notes` section allows tables. The following is a table
			with two distinct groups, each have a title row.
			|begin_table|
			|title|
			Input Variables
			|columns|
			Name |tab| Type
			|rows|
			in_host |tab| |type|`string`
			in_port |tab| |type|`int`
			|title|
			Output Variables
			|columns|
			Name |tab| Type
			|rows|
			out_length |tab| |type|`int`
			out_payload |tab| |type|`bytes`
			|end_table|
		
	"""

def make_X_minimal():
	pass

def make_X_complete():
	pass

def make_X_by_config(config: Dict[str,Any]):
	pass
