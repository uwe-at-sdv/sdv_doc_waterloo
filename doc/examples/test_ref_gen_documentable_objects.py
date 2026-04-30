import sdv.doc.waterloo.docitem as wtrl
import importlib
import sys

def main(mod_name: str) -> None:
# Configure traversal
	cfg = wtrl.ConfigTraversal()
# Allow recursive traversal
	cfg.enable_include_imported()

# Open module
	mod = importlib.import_module(mod_name)

# Iterate over documentable objects
	objs = wtrl.gen_documentable_objects(mod,cfg)
	for obj in objs:
		print(wtrl.get_obj_name(obj))

if __name__ == "__main__":
	main("pytest_good_inheritance")
