from __future__ import annotations
from typing import Any

class Vec2d:
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
