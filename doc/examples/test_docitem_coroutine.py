from __future__ import annotations
from typing import Any,AsyncGenerator

import asyncio
import time

#-----8<-----1
async def make_coffee() -> str:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| represent a non-blocking asynchronous task.
			|Must| take 3 seconds.
	Parameters:
	Returns:
		|Must| return a string telling what has been prepared.
	Raises:
		asyncio.CancelledError:
			|May| throw if the task running the coroutine is cancelled from outside.
	"""
	print("  [Coffee] Coffee machine started...")
	await asyncio.sleep(3)
	print("  [Coffee] Coffee is ready!")
	return "Hot coffee"
#----->8-----1

#-----8<-----2
async def get_marmalade() -> AsyncGenerator[str,None]:
	"""
	Preamble:
		profile:
			function
		normative_sections:
			Contract, Parameters, Returns, Raises
	Contract:
		general:
			|Must| represent a non-blocking asynchronous task.
			|Must| serve cherry marmalade after a second.
			|Must| serve strawberry marmalade after two seconds.
	Parameters:
	Returns:
		|Must| produce an asynchronous generator yielding strings of marmalade types.
	Raises:
		asyncio.CancelledError:
			|May| be raised if the task is cancelled during an await point.
	"""
	await asyncio.sleep(1)
	yield "Cherry"
	
	await asyncio.sleep(1)
	yield "Strawberry"
#----->8-----2

async def make_toast() -> str:
	print("  [Toast] Toaster started...")
	# Simulates another parallel task
	await asyncio.sleep(2)
	print("  [Toast] Toast is ready!")
	return "Crispy toast"

async def main() -> None:
	print(f"Start time: {time.strftime('%X')}")

	# We start both tasks simultaneously (concurrency)
	# asyncio.gather waits for all passed coroutines.
	ergebnisse = await asyncio.gather(
		make_coffee(),
		make_toast()
	)

	print(f"\nBreakfast is served: {ergebnisse}")
	print(f"End time: {time.strftime('%X')}")
	print("Note: Although it takes 3 seconds for coffee and 2 seconds for toast, the whole process only took about 3 seconds!")

if __name__ == "__main__":
# Start event loop
	asyncio.run(main())
