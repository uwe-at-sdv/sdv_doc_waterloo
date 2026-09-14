# Changelog

## Current release history

- 0.24.0 [2026-09-14]:
  - Unify the docitem and waterlint release versions as the sdv.doc.waterloo package version.
  - Move the release source of truth to `sdv.doc.waterloo.version`.
  - Merge the former module-local histories below as legacy records.

## Legacy: docitem.py release history

- 0.13.1 [2026-09-14] Authoring-JSON complete
- 0.13.0 [2026-09-13] waterlint render-docstring
- 0.12.16 [2026-09-12] Concept for Authoring-JSON
- 0.12.15 [2026-09-11] Bugfix in wtrl_mcp packaging
- 0.12.14 [2026-09-10] Bugfix in waterlint_common.py, name 
- 0.12.13 [2026-09-10] Bugfix github issue #1
- 0.12.12 [2026-07-26] Infrastructure of build_anchor-functions.
- 0.12.11 [2026-07-25] Added a function build_anchor_from_fully_qualified_name which helps in creating referentiable objects
- 0.12.10 [2026-07-22] Bugfix: docitem_helper.py: Caching now over IDs, not over objects.
- 0.12.9 [2026-07-21] Packaging details
- 0.12.8 [2026-07-20] PyPI packaging now per github workflow.
- 0.12.7 [2026-07-19] Bugfix RE_WTRL_ANGLE_WTRL_REF in docitem_helper.py.
- 0.12.6 [2026-07-18] Version bump: Sphinx extension moved to branch "sphinx".
- 0.12.5 [2026-07-17] Diagnostics improved for sections ..._overview, Public_...
- 0.12.4 [2026-07-10] Version bump for bugfix in wtrl_mcp_admin
- 0.12.3 [2026-07-09] Version bump for wtrl_mcp_admin: standardized diagnostics.
- 0.12.2 [2026-07-07] Version bump for MCP server: unique server identity
- 0.12.1 [2026-07-07] Fix in dependencies
- 0.12.0 [2026-07-07] Version Bump for MCP server: Bearer token authentication and tooling
- 0.11.1 [2026-07-04] Rule PNB-004 exceptions for quotes words: single, double, backtick.
- 0.11.0 [2026-07-03] Rule PNB-004 and pytests for PNB.
- 0.10.8 [2026-06-30] Added missing resources for PyPI.
- 0.10.7 [2026-06-30] Better handling for importlib errors
- 0.10.6 [2026-06-29]	Bugfix: CPVAR-005 and MPVAR-005 now allow annotated but uninstantiated variables, e.g. `x: int` without `x = 0`.
- 0.10.5 [2026-06-28] Refactoring for detailed parsing and validation messages complete
- 0.10.4 [2026-06-27] Removing Github workflow
- 0.10.3 [2026-06-27] Testing Github workflow
- 0.10.2 [2026-06-26] Upload-PyPI-Test
- 0.10.1 [2026-06-26] Upload-PyPI-Test
- 0.10.0 [2026-06-24]	Added DocSession for caching and other session data during docstring parsing and validation.
			A DocSession object is now required for parse_indent_docstring and validate_docstring.
- 0.9.0 [2026-06-21]	Lots of minor changes and improvements, especially in docitem_validator.py, but also in docitem_helper.py. See commit history for details.
- 0.8.1 [2026-05-22]	Bugfix: Enforce LQID-002 in a tolerant way, new rule LQID-006.
- 0.8.0 [2026-05-08]	read AST in order to extract docstrings since __doc__ has become unusable as of Python 3.13.
- 0.7.0 [2026-05-08]	Rules DER-010 to DER-013 and implementation in docitem_validator.py "Derived_from"
- 0.6.1 [2026-04-02]	Semantic role 'key' for keyboard
- 0.6.0 [2026-03-25]	Definitions now Term plus Variations.
- 0.5.6 [2026-03-20]	Rule SEE-006 restricted to documentable objects.
- 0.5.5 [2026-03-03]	Clickable nodes in Sphinx output.
- 0.5.4 [2026-02-25]	Doctests; Documentation review
- 0.5.3 [2026-02-24]	Doctests; Documentation review
- 0.5.2 [2026-02-22]	Sections "Definitions" and "Terminology": Rules tightened
- 0.5.1 [2026-02-22]	Subsection "_inherited" in "Definitions": JSON rendering implemented.
- 0.5.0 [2026-02-21]	Subsection "_inherited" in "Definitions"; Specification, Sphinx, examples.
- 0.4.1 [2026-02-20]	Improved rendering of "Factory" in sphinx extension; Tests for matching profile vs object, e.g. PRE-019.
- 0.4.0 [2026-02-19]	Major changes in class tracer: Debugging, detailed error records.
- 0.3.0 [2026-02-18]	Partial Normativity Detection (PNB-rules)
- 0.2.0 [2026-02-15]	Sphinx: Clickable references in Public_*, *_overview, See_also, and Derived_from;
			JSON: trait `generator`.
- 0.1.2 [2026-02-14]	Moved Waterloo specific stuff away from docitem_sphinx.py
- 0.1.1 [2026-02-13]	Commented versioning starts

## Legacy: waterlint.py release history

- 0.23.1 [2026-09-14] Authoring JSON: documentation, mcp-prompt, commands gen-[full|miniml]-authoring-json.
- 0.23.0 [2026-09-13] Subcommand 'render-docstring' - render a docstring from Authoring JSON.
- 0.22.3 [2026-09-10] Fixed --basedir resolution for split PEP 420 namespace packages. Waterloo no longer hides sibling namespace portions when constructing intermediate package prefixes.
- 0.22.2 [2026-09-10] Bugfix github issue #1
- 0.22.1 [2026-07-31] Design details and bugfixes in render-html5
- 0.22.0 [2026-07-30] Dark theme for render-html5 output.
- 0.21.0 [2026-07-28]	Option --include-qid-prefix for subcommands walk and render-json
- 0.20.6 [2026-07-27]	Improved resolution for linked objects.
- 0.20.5 [2026-07-27]	Factory items now clickable.
- 0.20.4 [2026-07-05]	Bugfixes in render-docker.
- 0.20.3 [2026-07-04]	render-json: legend updated.
- 0.20.2 [2026-07-04]	More styles and inline markup for render-html5.
- 0.20.1 [2026-07-04]	BNP-004 narrowed.
- 0.20.0 [2026-07-03]	New rule BNP-004
- 0.19.3 [2026-06-29]	Bugfix: CPVAR-005 and MPVAR-005 now allow annotated but uninstantiated variables, e.g. `x: int` without `x = 0`.
- 0.19.2 [2026-06-28] Refactoring for detailed parsing and validation messages complete
- 0.19.1 [2026-06-26] Add docstrings for version-commands; added wtrl_mcp-Version to version-json output.
- 0.19.0 [2026-06-25] Subcommand 'extract' now with syntaax highlighting in terminal output; option --syntax-hl-style to select a Pygments style.
- 0.18.0 [2026-06-25] Subcommand 'render-json': Validation and propagation of errors as standardized warning;
			Option --ignore (as in validate and coverage) to ignore certain warning codes.
- 0.17.0 [2026-06-22] Enhanced JSON output for types, constants, variables;
			Improved html5-rendering for these categories.
- 0.16.3 [2026-06-18] Bugfix which caused a missing error message in case of non-existing path for --basedir.
- 0.16.2 [2026-06-15]	More details in error message (complete);bugfixes in validation.
- 0.16.1 [2026-06-11]	More details in error message (in progress)
- 0.16.0 [2026-06-10]	More details in error message (in progress)
- 0.15.0 [2026-06-05]	Subcommand 'render-docker'
- 0.14.1 [2026-05-26]	Subcommand 'render-html5': Entries in Public_* and *_overview sections are now links.
- 0.14.0 [2026-05-25]	Subcommand `carve` now final, including exhaustive pytests.
- 0.13.3 [2026-05-24]	Subcommands `gen-full` and `gen-minimal` moved to waterlint_generate_common.py, waterlint_gen_minimal.py and waterlint_gen_full.py.
			Documentation in waterlint_gen_full.py and waterlint_gen_minimal.py
			Updated waterlint_render_html5.py.
- 0.13.2 [2026-05-23]	Subcommand `walk` moved to waterlint_walk.py; more functions in waterlint_common.py
- 0.13.1 [2026-05-22]	Moved common functions from waterlint.py and waterlint_carve.py to waterlint_common.py;
			bugfix in docitem.py.
			documentation in waterlint_carve.py and waterlint_render_html5.py
- 0.13.0 [2026-05-21]	Subcommand 'carve': Options --in, --out, --out-diag, --out-diag-json, --simplify,.--recompute
- 0.12.0 [2026-05-20]	Subcommand 'render-json': Option --in.
- 0.11.2 [2026-05-19]	Subcommand 'walk': Option --sort.
- 0.11.1 [2026-05-18]	Pretty format for help text.
- 0.11.0 [2026-05-18]	Subcommand 'walk' MVP
- 0.10.0 [2026-05-15]	Major refactoring in docitem_helper.
- 0.9.2 [2026-05-10]	Minor fixes/changes in subcommand render-html5.
- 0.9.1 [2026-05-01]	Minor changes in static typing
- 0.9.0 [2026-04-25]	Refactoring render-html5: freeform sections
- 0.8.3 [2026-04-24]	Subcommand render-html5: --css and --additional-css are now independent options.
			Subcommand extract: diagnostics now aligned with other subcommands.
- 0.8.2 [2026-04-22]	Options --header-html und --additional-css for subcommand render-html5.
- 0.8.1 [2026-04-18]	Unique $id in add-example-json; MD5 replaced by SHA256 in JSON-artifacts.
- 0.8.0 [2026-04-17]	JSON Schema for example references: this affects
			waterlint add-example-json
			waterlint validate-json
			Automatic JSON Schema inference
- 0.7.1 [2026-04-17]	Public_types/constants/variables are now rendered as free-form text.
- 0.7.0 [2026-04-14]	Anchors for Definition Terms in render-html5.
- 0.6.5 [2026-03-26]	Navigation buttons in render-html5
- 0.6.4 [2026-03-20]	Analyze --ignore parameter upfront, no commas allowed.
- 0.6.3 [2026-03-19]	Subcommand render-html5: Option --no-render-preamble
- 0.6.2 [2026-03-19]	Subcommand render-html5: Types, Constants, Variables
- 0.6.1 [2026-03-19]	Subcommand render-html5: JS-code separated and moved to special directory.
- 0.6.0 [2026-03-18]	Subcommand add-example-json
- 0.5.0 [2026-03-05]	__WTRL_SCOPES__ in JSON which allows future customization of scopes.
- 0.4.0 [2026-02-22]	Subcommand render-json: Node "definition_inherited_from_module", see also sdv.doc.waterloo.docitem_convert.
- 0.3.0 [2026-02-19]	Several refactorings concerning error handling, raw and JSON.
- 0.2.4 [2026-02-12]	Subcommand render-json: traits, decorators, default output filename.
- 0.9.1 [2026-04-27]	Subcommand version-json now prints JSON with all schema categories.
- 0.2.3 [2026-02-12]	Subcommand version-json: prints only the JSON-schema version string.
- 0.2.2 [2026-02-12]	Subcommand version: prints only the waterlint version string.
- 0.2.1 [2026-02-12]	Subcommand validate-json: --schema is now optional; automatic detection applies.
- 0.2.0 [2026-02-12]	Subcommand list-schemas
- 0.1.0 [2026-02-12]	Versioning starts. Subcommands are "validate", "coverage", "extract", "validate-json", "render-json"
