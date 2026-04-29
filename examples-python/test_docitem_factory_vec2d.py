from __future__ import annotations
from typing import Any
import math

#-----8<-----1
class Vec2d:
	"""
	Preamble:
		profile:
			class
		normative_sections:
			Contract, Factory, Public_methods
	Contract:
		general:
			|Must| represent a two-dimensional vector with |type|`float`-valued components.
		constructor:
			Do not use directly; use the factory functions instead.
	Factory:
		Vec2d.from_zero:
			Null vector
		Vec2d.from_comp:
			Vector from components (x, y)
		Vec2d.from_vec2d:
			Vector by copy
		Vec2d.gen:
			All of the above via runtime polymorphism
		make_vec2d_from_zero:
			Null vector
		make_vec2d_from_comp:
			Vector from components (x, y)
		make_vec2d_from_vec2d:
			Vector by copy
		vec2d:
			All of the above via runtime polymorphism
	Public_methods:
		from_zero, from_comp, from_vec2d
		gen
	"""
#----->8-----1
# Not appropriate for public because it allows e.g. Vec2d(3.0)
# with unclear semantics. Is it (3,0), (0,3) or (3,3)?
	def __init__(self,x: float = 0.0,y: float = 0.0):
		self._c = [x,y]
	@classmethod
	def from_zero(cls) -> Vec2d:
		return Vec2d()
	@classmethod
	def from_comp(cls,x: float,y: float) -> Vec2d:
		return Vec2d(x,y)
	@classmethod
	def from_vec2d(cls,v: Vec2d) -> Vec2d:
		return Vec2d(v._c[0],v._c[1])
	@classmethod
	def gen(cls,*arg: Any) -> Vec2d:
		"""
		Preamble:
			profile:
				method
			normative_sections:
				Contract, Parameters, Returns, Raises
		Contract:
			general:
				|Must| delegate to the standalone |func|`vec2d` factory.
				|Must| support all input patterns listed in the |type|`Vec2d` docstring |label|`Factory` section.
		Parameters:
			arg:
				|Must| match one of the patterns supported by |func|`vec2d` (see below).
		Returns:
			|Must| return a new |var|`Vec2d` instance.
		Raises:
			ValueError:
				|May| propagate from |func|`vec2d`.
		"""
		return vec2d(*arg)
	def __str__(self) -> str:
		return str(self._c)

def make_vec2d_from_zero() -> Vec2d:
	return Vec2d()
def make_vec2d_from_comp(x: float,y: float) -> Vec2d:
	return Vec2d(x,y)
def make_vec2d_from_vec2d(v: Vec2d) -> Vec2d:
	return Vec2d(v._c[0],v._c[1])

def vec2d(*arg: Any) -> Vec2d:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| support all input patterns listed in the |type|`Vec2d` docstring |label|`Factory` section.
	Parameters:
		arg:
			|Must| match one of the patterns supported by |func|`vec2d` (see below).
	Returns:
		|Must| return a new |var|`Vec2d` instance.
	Raises:
		ValueError:
			|Must| raise if |var|`arg` does not match any supported pattern.
	"""
	match arg:
		case ():
			return Vec2d()
		case (float() as x, float() as y):
			return Vec2d(x, y)
		case (Vec2d() as other,):
			return Vec2d(other._c[0], other._c[1])
		case _:
			raise ValueError(f"Unsupported input: {arg}")

if __name__ == "__main__":
	print(Vec2d.gen())
	print(Vec2d.gen(2.0,3.0))
	print(Vec2d.gen(Vec2d.gen(5.0,7.0)))

	print(vec2d())
	print(vec2d(2.0,3.0))
	print(vec2d(vec2d(5.0,7.0)))
