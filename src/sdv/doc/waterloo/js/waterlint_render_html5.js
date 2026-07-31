const WTRL_DATA = __DATA_JSON__;
const WTRL_INDEX = __INDEX_JSON__;
const WTRL_EXAMPLES_HTML = __EXAMPLES_HTML_JSON__;
// The above variables are injected by waterlint_render_html5.py, the script
// responsible for waterlint subcommand render-html5. They contain the data and index
// structures for the Waterloo documentation, as well as pre-rendered HTML snippets for examples.

function byId(id) { return document.getElementById(id); }
function setTextIfPresent(id, text) {
	const elem = byId(id);
	if (elem) elem.textContent = text;
}

const THEME_STORAGE_KEY = "wtrl-html5-theme";
const THEME_VALUES = new Set(["light", "auto", "dark"]);

function normalizeThemeValue(value) {
	const theme = String(value || "").trim();
	return THEME_VALUES.has(theme) ? theme : "auto";
}

function loadStoredTheme() {
	try {
		return normalizeThemeValue(window.localStorage.getItem(THEME_STORAGE_KEY));
	} catch (_) {
		return "auto";
	}
}

function storeTheme(theme) {
	try {
		window.localStorage.setItem(THEME_STORAGE_KEY, theme);
	} catch (_) {
		// Static files may be viewed in environments where localStorage is unavailable.
	}
}

function setTheme(theme, persist) {
	const normalized = normalizeThemeValue(theme);
	document.documentElement.dataset.wtrlTheme = normalized;
	if (persist) storeTheme(normalized);
	for (const name of THEME_VALUES) {
		const elemButton = byId(`wtrl-theme-${name}`);
		if (elemButton) elemButton.setAttribute("aria-pressed", name === normalized ? "true" : "false");
	}
}

function setupThemeSwitcher() {
	setTheme(loadStoredTheme(), false);
	for (const name of THEME_VALUES) {
		const elemButton = byId(`wtrl-theme-${name}`);
		if (!elemButton) continue;
		elemButton.addEventListener("click", () => { setTheme(name, true); });
	}
}

// Map fully qualified identifiers to renderable anchor ids.
// This is used e.g. in function resolveLocalTarget() to determine
// whether a given QID can be linked to from the current page.
const TARGET_TO_ANCHOR = new Map();
const TARGET_TO_KIND = new Map();
for (const e of WTRL_INDEX) {
	if (e.anchor) TARGET_TO_ANCHOR.set(e.target, e.anchor);
	if (e.target) TARGET_TO_KIND.set(e.target, String(e.kind || "obj"));
}

// The NORM_RE regex represents the complete set of normativity keywords.
const NORM_RE = /\|(?:Must|must|Must_not|must_not|Should|should|Should_not|should_not|May|may)\|/g;
// The TOK_RE regex captures three types of tokens:
// 1. Normativity keywords like |Must|, |should_not|, etc. (captured in group 1)
// 2. Literal values like |None|, |True|, etc. (captured in group 2)
// 3. Role-based tokens like |func|`foo.bar` (captured in group 3, with role in group 4 and body in group 5)
const TOK_RE = /(\|(?:Must|must|Must_not|must_not|Should|should|Should_not|should_not|May|may)\|)|(\|(?:None|Self|True|False)\|)|(\|([A-Za-z_][A-Za-z0-9_]*)\|`([^`]*)`)/g;
// The ROLE_CLASS mapping defines CSS classes for different Waterloo semantic roles.
// The keys are the role names as they appear in the token syntax,
// and the values are the corresponding CSS class strings to apply when rendering tokens of that role.
const ROLE_CLASS = {
	"attr": "wtrl-attr wtrl_attr",
	"cmd": "wtrl-cmd wtrl_cmd",
	"class": "wtrl-class wtrl_class",
	"dfn": "wtrl-dfn wtrl_dfn",
	"file": "wtrl-file wtrl_file",
	"func": "wtrl-func wtrl_func",
	"key": "wtrl-key wtrl_key",
	"label": "wtrl-label wtrl_label",
	"lit": "wtrl-lit wtrl_lit",
	"mod": "wtrl-mod wtrl_mod",
	"norm": "wtrl-norm wtrl_norm",
	"opt": "wtrl-opt wtrl_opt",
	"op": "wtrl-op wtrl_op",
	"pkg": "wtrl-pkg wtrl_pkg",
	"ref": "wtrl-ref wtrl_ref",
	"tag": "wtrl-tag wtrl_tag",
	"term": "wtrl-term wtrl_term",
	"type": "wtrl-type wtrl_type",
	"url": "wtrl-special-handling-see-code",
	"value": "wtrl-value wtrl_value",
	"var": "wtrl-var wtrl_var",
	"var_type": "wtrl-special-handling-see-code"
};

function buildAnchorMap() {
	const m = new Map();
	for (const e of WTRL_INDEX) {
		if (e.anchor) m.set(e.anchor, e.target);
	}
	return m;
}

const anchorMap = buildAnchorMap();

function encodeAnchorSegments(parts) {
	const out = [];
	for (const part of parts) {
		const seg = String(part || "").trim();
		if (!seg) continue;
		out.push(`${seg.length}:${seg}`);
	}
	return out.join("-");
}

function buildTermAnchor(targetQid, term) {
	const qid = String(targetQid || "");
	const t = String(term || "").trim();
	if (!qid || !t) return "";
	const parts = qid.split(".").filter(Boolean);
	if (parts.length === 0) return "";
	return `wtrl-term-${encodeAnchorSegments(parts.concat([t]))}`;
}

function buildDefinitionTermAnchorMap() {
	const m = new Map();
	const objects = (WTRL_DATA && WTRL_DATA.objects && typeof WTRL_DATA.objects === "object")
		? WTRL_DATA.objects
		: {};
	for (const [qid, node] of Object.entries(objects)) {
		if (!node || typeof node !== "object") continue;
		const doc = node.doc;
		if (!doc || typeof doc !== "object" || Array.isArray(doc)) continue;
		const defs = doc.Definitions;
		if (!defs || typeof defs !== "object" || Array.isArray(defs)) continue;
		for (const [term, defNode] of Object.entries(defs)) {
			if (term === "Definitions inherited from module") continue;
			if (!defNode || typeof defNode !== "object" || Array.isArray(defNode)) continue;
			const a = buildTermAnchor(qid, term);
			if (a) m.set(a, qid);
		}
	}
	return m;
}

const definitionTermAnchorMap = buildDefinitionTermAnchorMap();

const NAV_BACK_LABEL = "←";
const NAV_FORWARD_LABEL = "→";
const HISTORY_SELECT_PLACEHOLDER = "History";
const HISTORY_MAX = 20;
const historyTargets = [];
let historyCursor = -1;
let currentTargetQid = "";

const DEBUG_REFS_ENABLED = (() => {
	try {
		return new URLSearchParams(window.location.search).get("wtrl_debug_refs") === "1";
	} catch (_) {
		return false;
	}
})();
const DEBUG_REFS_MAX = 200;
const debugRefEvents = [];
let debugRefHost = null;

function ensureDebugRefHost() {
	if (!DEBUG_REFS_ENABLED) return null;
	if (debugRefHost) return debugRefHost;

	const side = document.querySelector(".wtrl-side");
	if (!side) return null;

	const details = document.createElement("details");
	details.id = "wtrl-debug-refs";
	details.className = "wtrl-section";

	const summary = document.createElement("summary");
	summary.textContent = "Debug refs";
	details.appendChild(summary);

	const elemDebugPre = document.createElement("pre");
	elemDebugPre.id = "wtrl-debug-refs-pre";
	elemDebugPre.className = "wtrl-obj";
	elemDebugPre.textContent = "[]";
	details.appendChild(elemDebugPre);

	const elemHitlist = byId("wtrl-hitlist");
	if (elemHitlist && elemHitlist.parentNode === side) {
		side.insertBefore(details, elemHitlist);
	} else {
		side.appendChild(details);
	}
	debugRefHost = elemDebugPre;
	return debugRefHost;
}

function pushDebugRefEvent(kind, data) {
	if (!DEBUG_REFS_ENABLED) return;
	const elemDebugRefHost = ensureDebugRefHost();
	if (!elemDebugRefHost) return;

	const evt = {
		ts: new Date().toISOString(),
		kind: String(kind || ""),
		current_object_qid: String(currentTargetQid || ""),
		...(data && typeof data === "object" ? data : {}),
	};

	debugRefEvents.push(evt);
	if (debugRefEvents.length > DEBUG_REFS_MAX) {
		debugRefEvents.splice(0, debugRefEvents.length - DEBUG_REFS_MAX);
	}
	elemDebugRefHost.textContent = JSON.stringify(debugRefEvents, null, 2);
}

function clearDebugRefEvents() {
	if (!DEBUG_REFS_ENABLED) return;
	debugRefEvents.splice(0, debugRefEvents.length);
	const elemDebugRefHost = ensureDebugRefHost();
	if (elemDebugRefHost) elemDebugRefHost.textContent = "[]";
}

function updateNavigationUi() {
	const elemNavBack = byId("wtrl-nav-back");
	const elemNavForward = byId("wtrl-nav-forward");
	const elemNavHistory = byId("wtrl-nav-history");

	if (elemNavBack) elemNavBack.disabled = historyCursor <= 0;
	if (elemNavForward) elemNavForward.disabled = historyCursor < 0 || historyCursor >= historyTargets.length - 1;

	if (elemNavHistory) {
		elemNavHistory.innerHTML = "";
		const elemPlaceholderOption = document.createElement("option");
		elemPlaceholderOption.value = "";
		elemPlaceholderOption.textContent = HISTORY_SELECT_PLACEHOLDER;
		elemPlaceholderOption.disabled = true;
		elemNavHistory.appendChild(elemPlaceholderOption);

		if (historyTargets.length === 0) {
			elemNavHistory.disabled = true;
			elemNavHistory.value = "";
		} else {
			elemNavHistory.disabled = false;
			for (let i = historyTargets.length - 1; i >= 0; i -= 1) {
				const elemHistoryOption = document.createElement("option");
				elemHistoryOption.value = String(i);
				elemHistoryOption.textContent = historyTargets[i];
				if (i === historyCursor) elemHistoryOption.selected = true;
				elemNavHistory.appendChild(elemHistoryOption);
			}
		}
	}
}

function pushHistory(targetQid) {
	const q = String(targetQid || "").trim();
	if (!q) return;

	// Bash-like history semantics: never truncate "future" entries.
	// Any explicit new selection is appended to the tail.
	if (historyTargets.length > 0 && historyTargets[historyTargets.length - 1] === q) {
		historyCursor = historyTargets.length - 1;
		updateNavigationUi();
		return;
	}

	historyTargets.push(q);
	if (historyTargets.length > HISTORY_MAX) {
		const overflow = historyTargets.length - HISTORY_MAX;
		historyTargets.splice(0, overflow);
	}
	historyCursor = historyTargets.length - 1;
	updateNavigationUi();
}

// This handler is for both the "Back"/"Forward" buttons and the history dropdown.
// The delta parameter is -1 for "Back", +1 for "Forward", and 0 for dropdown selection
// (in which case the new cursor position is read from the dropdown value).
function handlerHistoryDelta(delta) {
	if (historyTargets.length === 0) return;
	const next = historyCursor + delta;
	if (next < 0 || next >= historyTargets.length) return;
	historyCursor = next;
	const target = historyTargets[historyCursor];
	updateNavigationUi();
	selectTarget(target, { updateHash: true, recordHistory: false });
}

function parseRefBody(body) {
	const m = body.match(/^(.*)\s<([^>]+)>$/);
	if (!m) return { label: body, target: "" };
	return { label: m[1].trim(), target: m[2].trim() };
}

function stripOuterQuotes(s) {
	const t = String(s || "");
	if ((t.startsWith("'") && t.endsWith("'")) || (t.startsWith('"') && t.endsWith('"'))) {
		return t.slice(1, -1);
	}
	return t;
}

function inferSigName(node, targetQid) {
	const sig = (node && typeof node.signature === "object") ? node.signature : null;
	const txt = sig && typeof sig.text === "string" ? sig.text : "";
	const i = txt.indexOf("(");
	if (i > 0) return txt.slice(0, i).trim();
	return String(targetQid || "").split(".").slice(-1)[0] || "callable";
}

// Analyze targetQid and find the longest prefix
// that also exists in WTRL_DATA.toc_modules.
function inferModName(node, targetQid) {
	const qid = String(targetQid || "");
	if (!qid) return "";
	const mods = (WTRL_DATA && WTRL_DATA.toc_modules && typeof WTRL_DATA.toc_modules === "object")
		? WTRL_DATA.toc_modules
		: {};
	const parts = qid.split(".").filter(Boolean);
	for (let i = parts.length; i >= 1; i -= 1) {
		const cand = parts.slice(0, i).join(".");
		if (Object.prototype.hasOwnProperty.call(mods, cand)) return cand;
	}
	return "";
}

function inferClassName(node, classQualifiedSigName) {
	const s = String(classQualifiedSigName || "");
	const parts = s.split(".").filter(Boolean);
	if (parts.length <= 1) return "";
	return parts.slice(0, -1).join(".");
}

function inferFuncName(node, className, classQualifiedSigName) {
	const s = String(classQualifiedSigName || "");
	const parts = s.split(".").filter(Boolean);
	if (parts.length === 0) return "callable";
	return parts[parts.length - 1];
}

function splitQidForSignature(targetQid) {
	const qid = String(targetQid || "");
	if (!qid) return { mod: "", cls: "", leaf: "" };

	const mod = inferModName(null, qid);
	let tail = qid;
	if (mod && qid.startsWith(mod + ".")) tail = qid.slice(mod.length + 1);
	else if (mod === qid) tail = "";

	const parts = tail.split(".").filter(Boolean);
	const leaf = parts.length > 0 ? parts[parts.length - 1] : qid;
	const cls = parts.length > 1 ? parts.slice(0, -1).join(".") : "";
	return { mod, cls, leaf };
}

function makeSigLine() {
	const elemSigLine = document.createElement("div");
	elemSigLine.className = "wtrl-signature-line";
	return elemSigLine;
}

function renderSignature(node, targetQid, container) {
	container.innerHTML = "";
	const sig = (node && typeof node.signature === "object") ? node.signature : null;
	if (!sig) {
		const kind = inferDocLinesKind(targetQid);
		if (!kind) return;

		const head = makeSigLine();
		const parts = splitQidForSignature(targetQid);

		if (parts.mod) {
			const elemModule = document.createElement("span");
			elemModule.className = "wtrl-mod wtrl_mod";
			elemModule.textContent = parts.mod + ".";
			head.appendChild(elemModule);
		}
		if (parts.cls) {
			const elemClass = document.createElement("span");
			elemClass.className = "wtrl-type wtrl_type";
			elemClass.textContent = parts.cls + ".";
			head.appendChild(elemClass);
		}

		const name = document.createElement("span");
		name.className = (kind === "type") ? "wtrl-type wtrl_type" : "wtrl-var wtrl_var";
		name.textContent = parts.leaf;
		head.appendChild(name);
		container.appendChild(head);
		return;
	}

	const decorators = Array.isArray(node.decorators) ? node.decorators : [];
	for (const deco of decorators) {
		const line = makeSigLine();
		const elemDecorator = document.createElement("span");
		elemDecorator.className = "wtrl-attr wtrl_attr";
		elemDecorator.textContent = String(deco);
		line.appendChild(elemDecorator);
		container.appendChild(line);
	}

	const head = makeSigLine();

	const class_qualified_sig_name = inferSigName(node, targetQid)
// Build module name by tricky analysis and comparing to TOC.
	const mod_name = inferModName(node, targetQid);
// Build class name by dropping the last segment. The result might
// look like "X.Y" if the callable is a method of a nested class. 
	const class_name = inferClassName(node,class_qualified_sig_name)
// Build function name by extracting the last segment
	const func_name = inferFuncName(node,class_name,class_qualified_sig_name)

// Render module segment if we have one.
	if (mod_name) {
		const elemModule = document.createElement("span");
		elemModule.className = "wtrl-mod wtrl_mod";
		elemModule.textContent = mod_name + ".";
		head.appendChild(elemModule);
	}

// Render class segment if we have one.
	if (class_name) {
		const elemClass = document.createElement("span");
		elemClass.className = "wtrl-type wtrl_type";
		elemClass.textContent = class_name + ".";
		head.appendChild(elemClass);
	}


	const elemFunction = document.createElement("span");
	elemFunction.className = "wtrl-func wtrl_func";
	elemFunction.textContent = func_name;
	head.appendChild(elemFunction);
	head.appendChild(document.createTextNode("("));
	container.appendChild(head);

	const params = Array.isArray(sig.parameters) ? sig.parameters : [];
	for (const p of params) {
		const line = makeSigLine();
		const kind = String(p && p.kind || "");
		const rawName = String((p && p.name) || "");
		let pname = rawName;
		if (kind === "VAR_POSITIONAL") pname = "*" + pname;
		if (kind === "VAR_KEYWORD") pname = "**" + pname;

		line.appendChild(document.createTextNode("    "));
		const elemParam = document.createElement("span");
		elemParam.className = "wtrl-var wtrl_var";
		elemParam.textContent = pname;
		line.appendChild(elemParam);

		const ann = p && p.annotation;
		if (ann !== null && ann !== undefined && String(ann).trim() !== "") {
			line.appendChild(document.createTextNode(": "));
			const elemAnnotation = document.createElement("span");
			elemAnnotation.className = "wtrl-type wtrl_type";
			elemAnnotation.textContent = stripOuterQuotes(String(ann));
			line.appendChild(elemAnnotation);
		}
		if (p && p.default !== null && p.default !== undefined) {
			line.appendChild(document.createTextNode(" = " + String(p.default)));
		}
		container.appendChild(line);
	}

	const tail = makeSigLine();
	tail.appendChild(document.createTextNode(")"));
	const ret = sig.returns;
	if (ret !== null && ret !== undefined && String(ret).trim() !== "") {
		tail.appendChild(document.createTextNode(" -> "));
		const elemReturnType = document.createElement("span");
		elemReturnType.className = "wtrl-type wtrl_type";
		elemReturnType.textContent = stripOuterQuotes(String(ret));
		tail.appendChild(elemReturnType);
	}
	container.appendChild(tail);
}

function formatSectionHead(key) {
	return String(key || "").replaceAll("_", " ");
}

function getRoleClassForSubsectionHead(path, key) {
	const section = String((path && path.length > 0) ? path[0] : "");
	if (section === "Public_types") return "wtrl-type wtrl_type";
	if (section === "Public_variables" || section === "Public_constants") return "wtrl-var wtrl_var";
	if (section === "Class_overview") return "wtrl-type wtrl_type";
	if (section === "Function_overview" || section === "Method_overview") return "wtrl-func wtrl_func";
	if (section === "Factory") return "wtrl-func wtrl_func";
	if (section === "Raises") return "wtrl-type wtrl_type";
	if (section === "Parameters") return "wtrl-var wtrl_var";
	return "";
}

function getRoleClassForLeaf(path) {
	const section = String((path && path.length > 0) ? path[0] : "");
	const subsection = String((path && path.length > 1) ? path[1] : "");
	if (section === "Public_functions" || section === "Public_methods") return "wtrl-func wtrl_func";
	if (section === "Public_classes") return "wtrl-type wtrl_type";
	if (section === "Derived_from") return "wtrl-type wtrl_type";
	if (section === "Contract" && subsection === "base") return "wtrl-func wtrl_func";
	if (section === "Preamble" && (subsection === "profile" || subsection === "scope" || subsection === "status")) {
		return "wtrl-value wtrl_value";
	}
	if (section === "Contract" && subsection === "traits") return "wtrl-value wtrl_value";
	if (section === "Preamble" && subsection === "normative_sections") return "wtrl-label wtrl_label";
	return "";
}

function appendMaybeStyledText(parent, txt, roleCls) {
	if (!roleCls) {
		appendInlineTokens(parent, txt);
		return;
	}
	const elemStyledText = document.createElement("span");
	elemStyledText.className = roleCls;
	appendInlineTokens(elemStyledText, txt);
	parent.appendChild(elemStyledText);
}

function getRoleClassForTargetQid(targetQid) {
	const kind = TARGET_TO_KIND.get(String(targetQid || "")) || "obj";
	if (kind === "mod") return "wtrl-mod wtrl_mod";
	if (kind === "cls") return "wtrl-class wtrl_class";
	if (kind === "func" || kind === "meth") return "wtrl-func wtrl_func";
	if (kind === "type") return "wtrl-type wtrl_type";
	if (kind === "var" || kind === "const") return "wtrl-var wtrl_var";
	return "";
}

function isFreeformPath(path) {
	if (!Array.isArray(path) || path.length === 0) return false;
	const section = String(path[0]);

	// Whole-section freeform:
	// some sections store their complete content directly as a single string
	// or list of strings. These are rendered as freeform text blocks rather
	// than as automatically generated bullet lists.
	if ((section === "Description" || section === "Returns") && path.length === 1) {
		return true;
	}

	// Entry freeform:
	// other sections are maps from subsection/item labels to textual content.
	// For these, only the entry content (path length >= 2) is rendered as
	// freeform. The surrounding section/subsection headings are still built
	// structurally by renderValue().
	if (
		path.length >= 2 &&
		(
			section === "Terminology" ||
			section === "Notes" ||
			section === "Class_overview" ||
			section === "Method_overview" ||
			section === "Function_overview" ||
			section === "Public_types" ||
			section === "Public_variables" ||
			section === "Public_constants" ||
			section === "Parameters"
		)
	) {
		return true;
	}

	return false;
}

// Render a Waterloo freeform text block.
//
// This is intentionally close to the corresponding Sphinx-side rendering:
// - "|" on a line by itself splits paragraphs
// - leading "*", "+", "-", "#" introduce list items
// - inline Waterloo tokens are resolved by appendInlineTokens()
//
// Keep this function in sync with the Sphinx output layer whenever the
// semantics of freeform text change.
function renderFreeformText(container, txt) {
	const lines = String(txt).split(/\r?\n/);
	const RE_BULLET = /^([*+\-#])\s(.*)$/;

	function flushParagraph(parts) {
		if (!parts || parts.length === 0) return;
		const elemParagraph = document.createElement("p");
		elemParagraph.className = "wtrl-text";
		appendInlineTokens(elemParagraph, parts.join(" "));
		container.appendChild(elemParagraph);
	}

	function genList(symbol) {
		const elemList = document.createElement(symbol === "#" ? "ol" : "ul");
		elemList.className = "wtrl-list";
		return elemList;
	}

	function renderListBlock(block) {
		const nodeStack = [];
		const symStack = [];
		const lastItemStack = [];

		for (const entry of block) {
			const symbol = entry.symbol;
			const text = entry.text;

			if (symStack.length === 0) {
				nodeStack.push(genList(symbol));
				symStack.push(symbol);
				lastItemStack.push(null);
			} else if (symbol !== symStack[symStack.length - 1]) {
				if (!symStack.includes(symbol)) {
					const parentItem = lastItemStack[lastItemStack.length - 1];
					if (parentItem) {
						const nested = genList(symbol);
						parentItem.appendChild(nested);
						nodeStack.push(nested);
						symStack.push(symbol);
						lastItemStack.push(null);
					}
				} else {
					while (symStack.length > 0 && symStack[symStack.length - 1] !== symbol) {
						symStack.pop();
						nodeStack.pop();
						lastItemStack.pop();
					}
				}
			}

			const elemListItem = document.createElement("li");
			appendInlineTokens(elemListItem, text);
			nodeStack[nodeStack.length - 1].appendChild(elemListItem);
			lastItemStack[lastItemStack.length - 1] = elemListItem;
		}

		if (nodeStack.length > 0) container.appendChild(nodeStack[0]);
	}

	let paragraphParts = [];
	let i = 0;
	while (i < lines.length) {
		const raw = lines[i];

		if (/^\|\s*$/.test(raw)) {
			flushParagraph(paragraphParts);
			paragraphParts = [];
			i += 1;
			continue;
		}

		let match = raw.match(RE_BULLET);
		if (match) {
			flushParagraph(paragraphParts);
			paragraphParts = [];

			const block = [];
			while (i < lines.length) {
				const lineMatch = lines[i].match(RE_BULLET);
				if (!lineMatch) break;
				block.push({ symbol: lineMatch[1], text: lineMatch[2] });
				i += 1;
			}
			renderListBlock(block);
			continue;
		}

		const t = raw.trim();
		if (t) paragraphParts.push(t);
		i += 1;
	}
	flushParagraph(paragraphParts);
}

function isNormativeSectionsPath(path) {
	return (
		Array.isArray(path) &&
		path.length >= 2 &&
		String(path[0]) === "Preamble" &&
		String(path[1]) === "normative_sections"
	);
}

function isCompactValueListPath(path) {
	if (!Array.isArray(path) || path.length < 2) return false;
	const section = String(path[0]);
	const subsection = String(path[1]);
	return (
		(section === "Preamble" && subsection === "scope") ||
		(section === "Contract" && subsection === "traits")
	);
}

function renderCompactNormativeSections(container, items) {
	const vals = items.map(v => String(v));
	for (let i = 0; i < vals.length; i += 6) {
		const row = vals.slice(i, i + 6);
		const elemRowParagraph = document.createElement("p");
		elemRowParagraph.className = "wtrl-text";
		for (let j = 0; j < row.length; j += 1) {
			const elemLabel = document.createElement("span");
			elemLabel.className = "wtrl-label wtrl_label";
			elemLabel.textContent = row[j];
			elemRowParagraph.appendChild(elemLabel);
			if (j < row.length - 1) elemRowParagraph.appendChild(document.createTextNode(", "));
		}
		container.appendChild(elemRowParagraph);
	}
}

function renderCompactStyledValues(container, items, roleCls) {
	const elemParagraph = document.createElement("p");
	elemParagraph.className = "wtrl-text";
	const vals = items.map(v => String(v)).filter(Boolean);
	for (let i = 0; i < vals.length; i += 1) {
		appendMaybeStyledText(elemParagraph, vals[i], roleCls);
		if (i < vals.length - 1) elemParagraph.appendChild(document.createTextNode(", "));
	}
	container.appendChild(elemParagraph);
}

function _sourcePointerToQid(src) {
	const pfx = "/__WTRL_OBJECTS__/";
	const s = String(src || "");
	if (s.startsWith(pfx)) return s.slice(pfx.length);
	return "";
}

function isDefinitionsInheritedSubsectionPath(path) {
	return (
		Array.isArray(path) &&
		path.length >= 2 &&
		String(path[0]) === "Definitions" &&
		String(path[1]) === "Definitions inherited from module"
	);
}

function renderDefinitionsInheritedContent(container, value) {
	const obj = (value && typeof value === "object" && !Array.isArray(value)) ? value : {};
	const srcQid = _sourcePointerToQid(obj.source || "");
	const moduleAnchor = srcQid ? TARGET_TO_ANCHOR.get(srcQid) : "";
	const terms = Array.isArray(obj.terms) ? obj.terms : [];

	const elemTermsList = document.createElement("ul");
	elemTermsList.className = "wtrl-list";
	for (const term of terms) {
		const elemTermItem = document.createElement("li");
		const termTxt = String(term);
		const termAnchor = srcQid ? buildTermAnchor(srcQid, termTxt) : "";
		const linkAnchor = (termAnchor && definitionTermAnchorMap.has(termAnchor)) ? termAnchor : moduleAnchor;
		const linkTargetQid = linkAnchor
			? (definitionTermAnchorMap.get(linkAnchor) || anchorMap.get(linkAnchor) || "")
			: "";

		pushDebugRefEvent("inherited-definition-link-resolved", {
			source_qid: srcQid || "",
			term: termTxt,
			term_anchor: termAnchor || null,
			module_anchor: moduleAnchor || null,
			chosen_anchor: linkAnchor || null,
			chosen_target_qid: linkTargetQid || null,
		});

		if (linkAnchor) {
			const elemTermLink = document.createElement("a");
			elemTermLink.className = "wtrl-ref wtrl_ref wtrl-dfn wtrl_dfn";
			elemTermLink.href = "#" + linkAnchor;
			elemTermLink.textContent = termTxt;
			elemTermLink.addEventListener("click", () => {
				pushDebugRefEvent("inherited-definition-link-click", {
					source_qid: srcQid || "",
					term: termTxt,
					chosen_anchor: linkAnchor || null,
					chosen_target_qid: linkTargetQid || null,
				});
			});
			elemTermItem.appendChild(elemTermLink);
		} else {
			const elemTermText = document.createElement("span");
			elemTermText.className = "wtrl-dfn wtrl_dfn";
			elemTermText.textContent = termTxt;
			elemTermItem.appendChild(elemTermText);
		}
		elemTermsList.appendChild(elemTermItem);
	}
	container.appendChild(elemTermsList);
}

function isDefinitionsEntryPath(path) {
	return Array.isArray(path) && path.length === 1 && String(path[0]) === "Definitions";
}

function isDefinitionsEntryValue(value) {
	if (!value || typeof value !== "object" || Array.isArray(value)) return false;
	const hasText = Object.prototype.hasOwnProperty.call(value, "text") && Array.isArray(value.text);
	const hasVariations = Object.prototype.hasOwnProperty.call(value, "variations") && Array.isArray(value.variations);
	return hasText && hasVariations;
}

function isSeeAlsoPath(path) {
	return Array.isArray(path) && path.length >= 1 && String(path[0]) === "See_also";
}

function resolveSeeAlsoTarget(entry, currentQid) {
	const raw = String(entry || "").trim();
	if (!raw) return "";
	if (TARGET_TO_ANCHOR.has(raw)) return raw;

	const cur = String(currentQid || "");
	const curParts = cur.split(".").filter(Boolean);
	if (raw.indexOf(".") < 0 && curParts.length > 1) {
		for (let i = curParts.length - 1; i >= 1; i -= 1) {
			const cand = curParts.slice(0, i).concat([raw]).join(".");
			if (TARGET_TO_ANCHOR.has(cand)) return cand;
		}
	}

	let hit = "";
	for (const qid of TARGET_TO_ANCHOR.keys()) {
		if (qid.endsWith("." + raw)) {
			if (hit && hit !== qid) return "";
			hit = qid;
		}
	}
	return hit;
}

// Resolve a local Public_* or *_overview name to a target QID.
// Return the empty string when no unambiguous target can be found.
//
// This resolver is stricter than See_also resolution. It only links when the
// result is obvious from the current scope or already fully qualified.
function resolveLocalTarget(entry, currentQid) {
	const raw = String(entry || "").trim();
	if (!raw) return "";
	if (TARGET_TO_ANCHOR.has(raw)) return raw;
	if (raw.indexOf(".") >= 0) return "";

	// Try to resolve against the current QID.
	// The corresponding rules MPCL-004, MPFN-004, CPCL-004, and CPMT-004
	// ensure that the listed entry names exist and have the expected kind;
	// this helper only creates a link when the resolved target is also
	// unambiguous in the current context.
	const cur = String(currentQid || "").trim();
	if (!cur) return "";

	const candidates = [cur + "." + raw];
	// Prepare a second candidate by dropping the last segment of the current QID, if any.
	const parts = cur.split(".").filter(Boolean);
	if (parts.length > 1) {
		candidates.push(parts.slice(0, -1).concat([raw]).join("."));
	}

	// Resolve against the current scope and the immediate parent scope as a
	// conservative fallback. Return a link only if the result is unambiguous.
	let hit = "";
	for (const cand of candidates) {
		// Discard candidates that are not linkable targets (or do not exist).
		if (!cand || !TARGET_TO_ANCHOR.has(cand)) continue;
		// If name resolution yields multiple candidates, do not link at all to avoid ambiguity.
		if (hit && hit !== cand) return "";
		hit = cand;
	}
	if (hit) return hit;

	// Imported or re-exported Public_* entries may be documented under their
	// defining module, not under the module that lists them as public API.
	for (const qid of TARGET_TO_ANCHOR.keys()) {
		if (qid.endsWith("." + raw)) {
			if (hit && hit !== qid) return "";
			hit = qid;
		}
	}
	return hit;
}

// Render a label as a link only when the target is unambiguous in the current
// scope. Otherwise keep the plain colored text.
function appendLinkedOrStyledText(parent, txt, roleCls, currentQid) {
	const raw = String(txt || "");
	const targetQid = resolveLocalTarget(raw, currentQid);
	if (!targetQid) {
		appendMaybeStyledText(parent, raw, roleCls);
		return;
	}
	const anchor = TARGET_TO_ANCHOR.get(targetQid);
	if (!anchor) {
		appendMaybeStyledText(parent, raw, roleCls);
		return;
	}
	const elemLink = document.createElement("a");
	elemLink.className = "wtrl-ref wtrl_ref" + (roleCls ? " " + roleCls : "");
	elemLink.href = "#" + anchor;
	elemLink.textContent = raw;
	parent.appendChild(elemLink);
}

function appendSeeAlsoEntry(parent, entry, currentQid) {
	const raw = String(entry || "").trim();
	if (!raw) return;
	const targetQid = resolveSeeAlsoTarget(raw, currentQid);
	if (!targetQid) {
		appendMaybeStyledText(parent, raw, "wtrl-func wtrl_func");
		return;
	}
	const anchor = TARGET_TO_ANCHOR.get(targetQid);
	if (!anchor) {
		appendMaybeStyledText(parent, raw, "wtrl-func wtrl_func");
		return;
	}
	const roleCls = getRoleClassForTargetQid(targetQid);
	const elemSeeAlsoLink = document.createElement("a");
	elemSeeAlsoLink.className = "wtrl-ref wtrl_ref" + (roleCls ? " " + roleCls : "");
	elemSeeAlsoLink.href = "#" + anchor;
	elemSeeAlsoLink.textContent = raw;
	parent.appendChild(elemSeeAlsoLink);
}

function _extractSeeAlsoEntries(value) {
	if (typeof value === "string") {
		return value.split(",").map(s => s.trim()).filter(Boolean);
	}
	if (Array.isArray(value)) {
		return value.map(v => String(v).trim()).filter(Boolean);
	}
	return [];
}

function _getSeeAlsoEntriesFromDocNode(docNode) {
	if (!docNode || typeof docNode !== "object" || Array.isArray(docNode)) return [];
	return _extractSeeAlsoEntries(docNode.See_also);
}

function buildReferencedByIndex() {
	const idx = new Map();
	const objects = (WTRL_DATA && WTRL_DATA.objects && typeof WTRL_DATA.objects === "object")
		? WTRL_DATA.objects
		: {};

	for (const [sourceQid, node] of Object.entries(objects)) {
		if (!node || typeof node !== "object") continue;
		const doc = node.doc;
		const entries = _getSeeAlsoEntriesFromDocNode(doc);
		for (const entry of entries) {
			const targetQid = resolveSeeAlsoTarget(entry, sourceQid);
			if (!targetQid) continue;
			if (!idx.has(targetQid)) idx.set(targetQid, new Set());
			idx.get(targetQid).add(sourceQid);
		}
	}
	return idx;
}

const REFERENCED_BY_INDEX = buildReferencedByIndex();

function renderReferencedBySection(container, currentQid) {
	const refs = REFERENCED_BY_INDEX.get(String(currentQid || ""));
	if (!refs || refs.size === 0) return;

	const elemSection = document.createElement("div");
	elemSection.className = "wtrl-section";
	const elemSectionHead = document.createElement("div");
	elemSectionHead.className = "wtrl-section-head";
	elemSectionHead.textContent = "Referenced by";
	elemSection.appendChild(elemSectionHead);

	const elemRefsList = document.createElement("ul");
	elemRefsList.className = "wtrl-list";
	for (const sourceQid of Array.from(refs).sort()) {
		const elemRefItem = document.createElement("li");
		const anchor = TARGET_TO_ANCHOR.get(sourceQid);
		const roleCls = getRoleClassForTargetQid(sourceQid);
		if (anchor) {
			const elemRefLink = document.createElement("a");
			elemRefLink.className = "wtrl-ref wtrl_ref" + (roleCls ? " " + roleCls : "");
			elemRefLink.href = "#" + anchor;
			elemRefLink.textContent = sourceQid;
			elemRefItem.appendChild(elemRefLink);
		} else {
			appendMaybeStyledText(elemRefItem, sourceQid, roleCls);
		}
		elemRefsList.appendChild(elemRefItem);
	}
	elemSection.appendChild(elemRefsList);
	container.appendChild(elemSection);
}

// Agents, please learn my indentation style for this function!
// I use TABs, and curly brackets get their own line.
// Comments start a position 0 in each line.
function appendInlineTokens(parent, txt)
	{
	let cur = 0;
	let m;
	TOK_RE.lastIndex = 0;
	while ((m = TOK_RE.exec(txt)) !== null)
		{
		if (m.index > cur) parent.appendChild(document.createTextNode(txt.slice(cur, m.index)));
		if (m[1])
			{
			const elemNorm = document.createElement("span");
			elemNorm.className = "wtrl-norm wtrl_norm";
			elemNorm.textContent = m[1];
			parent.appendChild(elemNorm);
			}
		else if (m[2])
			{
// The comment on TOK_RE says, this one captures |None|, |Self|, |True|, |False|.
			const elemLiteralValue = document.createElement("span");
			elemLiteralValue.className = "wtrl-value wtrl_value";
			elemLiteralValue.textContent = m[2];
			parent.appendChild(elemLiteralValue);
			}
		else if (m[3])
			{
// We have m[3], so check for semantic role.
			const role = m[4];
			const body = m[5];
			const cls = ROLE_CLASS[role];
			if (!cls)
				{
// None of the knwon roles, append as is.
				parent.appendChild(document.createTextNode(m[3]));
				}
			else if (role === "ref")
				{
// Special handling of references.
				const rb = parseRefBody(body);
				const refText = rb.label || body;
				const elemRefLink = document.createElement("a");
				elemRefLink.className = cls;
				elemRefLink.textContent = refText;
				if (rb.target.startsWith("http://") || rb.target.startsWith("https://"))
					{
					elemRefLink.href = rb.target;
					elemRefLink.target = "_blank";
					elemRefLink.rel = "noopener noreferrer";
					}
				else if (rb.target.startsWith("wtrl://"))
					{
					const qid = rb.target.slice("wtrl://".length);
					const anchor = TARGET_TO_ANCHOR.get(qid);
					if (anchor) elemRefLink.href = "#" + anchor;
					}
				if (!elemRefLink.getAttribute("href"))
					{
					const elemFallback = document.createElement("span");
					elemFallback.className = cls;
					elemFallback.textContent = refText;
					parent.appendChild(elemFallback);
					}
				else
					{
					parent.appendChild(elemRefLink);
					}
				}
			else if (role === "lit" && (body === "None" || body === "Self" || body === "True" || body === "False"))
				{
// Mark might have the form |lit|`abc` or for instance |Self|
// Yet this is not a recommented form in wtrl. Just write |Self|, not |lit|`Self`.
// A form like |value|`Self` is acceptable, but is already covered below in the default branch.
				const elemSpecialLiteral = document.createElement("span");
				elemSpecialLiteral.className = "wtrl-value wtrl_value";
				elemSpecialLiteral.textContent = body;
				parent.appendChild(elemSpecialLiteral);
				}
// More special cases here.
			else if (role === "var_type")
				{
// We are looking for the form variable-colon-type, e.g. |var_type|`x:int`. The colon is the separator.
// Would like to render with wtrl-var/wtrl_var for the variable and wtrl-type/wtrl_type for the type.
				const parts = body.split(":");
				const elemVarType = document.createElement("span");
				if (parts.length === 2)
					{
// Variable
					const elemVar = document.createElement("span");
					elemVar.className = "wtrl-var wtrl_var";
					elemVar.textContent = parts[0];
					elemVarType.appendChild(elemVar);
// Colon
					elemVarType.appendChild(document.createTextNode(":"));
// Type
					const elemType = document.createElement("span");
					elemType.className = "wtrl-type wtrl_type";
					elemType.textContent = parts[1];
					elemVarType.appendChild(elemType);
					}
				else
					{
// Cannot interpret, append as is.
					elemVarType.textContent = body;
					}
				parent.appendChild(elemVarType);
				}
			else if (role === "url")
				{
// For URLs we currently have two styles: wtrl-url and wtrl-url-schema.
// We'd like to render the schema part in wtrl-url-schema and the rest in wtrl-url. The separator is "://".
				const parts = body.split("://");
				const elemUrl = document.createElement("span");
				if (parts.length === 2)
					{
// Schema
					const elemUrlSchema = document.createElement("span");
					elemUrlSchema.className = "wtrl-url-schema wtrl_url_schema";
					elemUrlSchema.textContent = parts[0];
					elemUrl.appendChild(elemUrlSchema);
// Rest
					const elemUrlRest = document.createElement("span");
					elemUrlRest.className = "wtrl-url wtrl_url";
					elemUrlRest.textContent = "://" + parts[1];
					elemUrl.appendChild(elemUrlRest);
					}
				else
					{
// Cannot interpret, append as is.
					elemUrl.textContent = body;
					}
				parent.appendChild(elemUrl);
				}
			else
				{
// The default branch.
				const elemRoleText = document.createElement("span");
				elemRoleText.className = cls;
				elemRoleText.textContent = body;
				parent.appendChild(elemRoleText);
				}
			}
		cur = TOK_RE.lastIndex;
		}
	if (cur < txt.length) parent.appendChild(document.createTextNode(txt.slice(cur)));
	}

function renderValue(value, container, depth, path, currentQid) {
	const pth = Array.isArray(path) ? path : [];
	const leafRoleCls = getRoleClassForLeaf(pth);

	// Rendering strategy:
	// 1. Handle special semantic paths first (See_also, normative_sections,
	//    inherited definitions, Definitions entries with variations).
	// 2. For plain strings / string-arrays, ask isFreeformPath() whether the
	//    current JSON path should be interpreted as freeform text.
	// 3. Otherwise fall back to the generic list / object rendering.
	if (value === null || value === undefined) {
		const elemNullParagraph = document.createElement("p");
		elemNullParagraph.className = "wtrl-text";
		appendMaybeStyledText(elemNullParagraph, "null", leafRoleCls);
		container.appendChild(elemNullParagraph);
		return;
	}
	if (typeof value === "string") {
		if (isSeeAlsoPath(pth)) {
			const elemSeeAlsoParagraph = document.createElement("p");
			elemSeeAlsoParagraph.className = "wtrl-text";
			const vals = value.split(",").map(s => s.trim()).filter(Boolean);
			for (let i = 0; i < vals.length; i += 1) {
				appendSeeAlsoEntry(elemSeeAlsoParagraph, vals[i], currentQid);
				if (i < vals.length - 1) elemSeeAlsoParagraph.appendChild(document.createTextNode(", "));
			}
			container.appendChild(elemSeeAlsoParagraph);
			return;
		}
		if (isNormativeSectionsPath(pth)) {
			const vals = value.split(",").map(s => s.trim()).filter(Boolean);
			renderCompactNormativeSections(container, vals);
			return;
		}
		if (isCompactValueListPath(pth)) {
			const vals = value.split(",").map(s => s.trim()).filter(Boolean);
			renderCompactStyledValues(container, vals, leafRoleCls);
			return;
		}
		if (isFreeformPath(pth)) {
			renderFreeformText(container, value);
			return;
		}
		const elemTextParagraph = document.createElement("p");
		elemTextParagraph.className = "wtrl-text";
		appendMaybeStyledText(elemTextParagraph, value, leafRoleCls);
		container.appendChild(elemTextParagraph);
		return;
	}
	if (Array.isArray(value)) {
		if (isSeeAlsoPath(pth) && value.every(item => typeof item === "string")) {
			const elemSeeAlsoList = document.createElement("ul");
			elemSeeAlsoList.className = "wtrl-list";
			for (const item of value) {
				const elemSeeAlsoItem = document.createElement("li");
				appendSeeAlsoEntry(elemSeeAlsoItem, String(item), currentQid);
				elemSeeAlsoList.appendChild(elemSeeAlsoItem);
			}
			container.appendChild(elemSeeAlsoList);
			return;
		}
		if (isNormativeSectionsPath(pth) && value.every(item => typeof item === "string")) {
			renderCompactNormativeSections(container, value);
			return;
		}
		if (isCompactValueListPath(pth) && value.every(item => typeof item === "string")) {
			renderCompactStyledValues(container, value, leafRoleCls);
			return;
		}
		if (isFreeformPath(pth) && value.every(item => typeof item === "string")) {
			renderFreeformText(container, value.join("\n"));
			return;
		}
		const elemGenericList = document.createElement("ul");
		elemGenericList.className = "wtrl-list";
		for (const item of value) {
			const elemGenericItem = document.createElement("li");
			if (typeof item === "string") {
				// Public_* entries are linked only when the local name resolves
				// unambiguously to a known object in the current scope.
				if (
					pth[0] === "Public_classes" ||
					pth[0] === "Public_functions" ||
					pth[0] === "Public_methods" ||
					pth[0] === "Public_types" ||
					pth[0] === "Public_variables" ||
					pth[0] === "Public_constants"
				) {
					appendLinkedOrStyledText(elemGenericItem, item, leafRoleCls, currentQid);
				} else {
					appendMaybeStyledText(elemGenericItem, item, leafRoleCls);
				}
			}
			else renderValue(item, elemGenericItem, depth + 1, pth, currentQid);
			elemGenericList.appendChild(elemGenericItem);
		}
		container.appendChild(elemGenericList);
		return;
	}
	if (typeof value === "object") {
		if (isDefinitionsInheritedSubsectionPath(pth)) {
			renderDefinitionsInheritedContent(container, value);
			return;
		}

		let entries = Object.entries(value);
		if (depth === 0 && pth.length === 0) {
			let inheritedNode;
			entries = entries.filter(([k, v]) => {
				if (k === "definitions_inherited_from_module") {
					inheritedNode = v;
					return false;
				}
				return true;
			});
			if (inheritedNode !== undefined) {
				let injected = false;
				entries = entries.map(([k, v]) => {
					if (k !== "Definitions") return [k, v];
					injected = true;
					if (v && typeof v === "object" && !Array.isArray(v)) {
						const vv = Object.assign({}, v);
						vv["Definitions inherited from module"] = inheritedNode;
						return [k, vv];
					}
					return [k, { "Definitions inherited from module": inheritedNode }];
				});
				if (!injected) {
					entries.push(["Definitions", { "Definitions inherited from module": inheritedNode }]);
				}
			}
		}

		for (const [k, v] of entries) {
			if (isDefinitionsEntryPath(pth) && isDefinitionsEntryValue(v)) {
				const vv = v;
				const elemDefBlock = document.createElement("div");
				elemDefBlock.className = "wtrl-subsection";
				const termAnchor = buildTermAnchor(currentQid, k);
				if (termAnchor) elemDefBlock.id = termAnchor;

				const elemDefHead = document.createElement("div");
				elemDefHead.className = "wtrl-subsection-head";

				const spTerm = document.createElement("span");
				spTerm.className = "wtrl-dfn wtrl_dfn";
				spTerm.textContent = String(k);
				elemDefHead.appendChild(spTerm);

				const vars = vv.variations.map(x => String(x)).filter(Boolean);
				if (vars.length > 0) {
					elemDefHead.appendChild(document.createTextNode(" ["));
					const spVar = document.createElement("span");
					spVar.className = "wtrl-term wtrl_term";
					spVar.textContent = vars.join(", ");
					elemDefHead.appendChild(spVar);
					elemDefHead.appendChild(document.createTextNode("]"));
				}
				elemDefBlock.appendChild(elemDefHead);

				renderFreeformText(elemDefBlock, vv.text.join("\n"));
				container.appendChild(elemDefBlock);
				continue;
			}

			const elemBlock = document.createElement("div");
			elemBlock.className = depth === 0 ? "wtrl-section" : "wtrl-subsection";
			const elemHead = document.createElement("div");
			elemHead.className = depth === 0 ? "wtrl-section-head" : "wtrl-subsection-head";
			if (depth === 0) {
				elemHead.textContent = formatSectionHead(k);
			} else {
				const section = String((pth && pth.length > 0) ? pth[0] : "");
				const roleCls = getRoleClassForSubsectionHead(pth, k);
				if (k === "normative_sections") {
					elemHead.textContent = formatSectionHead(k);
				} else if (section === "Class_overview" || section === "Function_overview" || section === "Method_overview" || section === "Factory") {
					// Overview entry labels are linked only when the local name resolves
					// unambiguously to a documented object in the current scope.
					appendLinkedOrStyledText(elemHead, k, roleCls, currentQid);
				} else if (section === "Public_types" || section === "Public_variables" || section === "Public_constants") {
					// Public type/variable/constant entries use the same conservative
					// target resolution: link only when the object name is unambiguous.
					appendLinkedOrStyledText(elemHead, k, roleCls, currentQid);
				} else {
					elemHead.textContent = k;
				}
				if (roleCls) elemHead.className += " " + roleCls;
			}
			elemBlock.appendChild(elemHead);
			renderValue(v, elemBlock, depth + 1, pth.concat([k]), currentQid);
			container.appendChild(elemBlock);
			if (depth === 0 && String(k) === "See_also") {
				renderReferencedBySection(container, currentQid);
			}
		}
		return;
	}
	const elemFallbackParagraph = document.createElement("p");
	elemFallbackParagraph.className = "wtrl-text";
	appendMaybeStyledText(elemFallbackParagraph, String(value), leafRoleCls);
	container.appendChild(elemFallbackParagraph);
}

function renderHitList(entries) {
	const elemHitlistHost = byId("wtrl-hitlist");
	elemHitlistHost.innerHTML = "";
	for (const e of entries) {
		const elemHitButton = document.createElement("button");
		elemHitButton.className = "wtrl-hit";
		elemHitButton.type = "button";
		const kindClass = ({
			mod: "wtrl-hit-kind-module",
			cls: "wtrl-hit-kind-class",
			func: "wtrl-hit-kind-callable",
			meth: "wtrl-hit-kind-callable",
			type: "wtrl-hit-kind-type",
			var: "wtrl-hit-kind-assignable",
			const: "wtrl-hit-kind-assignable",
			obj: "wtrl-hit-kind-object",
		})[String(e.kind || "")] || "";
		if (kindClass) elemHitButton.classList.add(kindClass);
		const kindLabel = ({
			mod: "module",
			cls: "class",
			func: "function",
			meth: "method",
			type: "type",
			var: "variable",
			const: "constant",
			obj: "object",
		})[String(e.kind || "")] || String(e.kind || "");
		const elemKind = document.createElement("span");
		elemKind.className = `wtrl-kind ${kindClass ? kindClass + "-label" : ""}`;
		elemKind.textContent = kindLabel;
		elemHitButton.appendChild(elemKind);

		const elemLabel = document.createElement("span");
		elemLabel.textContent = e.label;
		elemHitButton.appendChild(elemLabel);
		elemHitButton.title = e.label;
		elemHitButton.addEventListener("click", () => selectTarget(e.target, { updateHash: true }));
		elemHitlistHost.appendChild(elemHitButton);
	}
}

function getHitSearchText(entry) {
	const e = entry && typeof entry === "object" ? entry : {};
	const kind = String(e.kind || "");
	const kindText = ({
		mod: "module",
		cls: "class",
		func: "function",
		meth: "method",
		type: "type",
		var: "variable",
		const: "constant",
		obj: "object",
	})[kind] || kind;
	const target = String(e.target || "");
	const label = String(e.label || "");
	const leaf = target ? target.split(".").filter(Boolean).slice(-1)[0] || "" : "";
	return [label, target, leaf, kindText].filter(Boolean).join(" ").toLowerCase();
}

function kindMatchesFilter(kind, filterValue) {
	const k = String(kind || "");
	const f = String(filterValue || "*").toLowerCase();
	if (f === "*" || f === "all") return true;
	if (f === "objects") return k === "mod" || k === "cls" || k === "func" || k === "meth";
	if (f === "modules") return k === "mod";
	if (f === "classes") return k === "cls";
	if (f === "callables") return k === "func" || k === "meth";
	if (f === "functions") return k === "func";
	if (f === "methods") return k === "meth";
	if (f === "types") return k === "type";
	if (f === "assignables") return k === "const" || k === "var";
	if (f === "constants") return k === "const";
	if (f === "variables") return k === "var";
	return true;
}

function filterHitEntries(entries, kindFilter, queryText) {
	const q = String(queryText || "").trim().toLowerCase();
	return entries.filter((e) => {
		if (!kindMatchesFilter(e.kind, kindFilter)) return false;
		if (!q) return true;
		return getHitSearchText(e).includes(q);
	});
}

function getModulePrefixes() {
	const tocModules = (WTRL_DATA && WTRL_DATA.toc_modules && typeof WTRL_DATA.toc_modules === "object")
		? WTRL_DATA.toc_modules
		: {};
	return Object.keys(tocModules).sort((a, b) => b.length - a.length);
}

const MODULE_PREFIXES = getModulePrefixes();

function getOwningModulePrefix(qid) {
	const q = String(qid || "");
	if (!q) return "";
	for (const mod of MODULE_PREFIXES) {
		if (q === mod || q.startsWith(mod + ".")) return mod;
	}
	return "";
}

function formatHitLabel(qid, mode) {
	const q = String(qid || "");
	const m = String(mode || "from-module").toLowerCase();
	if (!q || m === "full") return q;

	const mod = getOwningModulePrefix(q);
	if (!mod) return q;
	const modBase = mod.split(".").filter(Boolean).slice(-1)[0] || mod;
	const suffix = (q === mod) ? "" : q.slice(mod.length + 1);
	if (m === "from-module") {
		return suffix ? `${modBase}.${suffix}` : modBase;
	}
	if (m === "no-module") {
		return suffix || modBase;
	}
	return q;
}

function inferDocLinesKind(targetQid) {
	const q = String(targetQid || "");
	if (WTRL_DATA && WTRL_DATA.toc_types && Object.prototype.hasOwnProperty.call(WTRL_DATA.toc_types, q)) {
		return "type";
	}
	if (WTRL_DATA && WTRL_DATA.toc_variables && Object.prototype.hasOwnProperty.call(WTRL_DATA.toc_variables, q)) {
		return "variable";
	}
	if (WTRL_DATA && WTRL_DATA.toc_constants && Object.prototype.hasOwnProperty.call(WTRL_DATA.toc_constants, q)) {
		return "constant";
	}
	return "";
}

function renderDocLines(node, targetQid, elemHost) {
	const lines = Array.isArray(node.doc_lines) ? node.doc_lines : [];
	if (lines.length === 0) return false;

	const kind = String((node && node.doc_lines_kind) || inferDocLinesKind(targetQid) || "");
	const annotation = (node && typeof node.annotation === "string" && node.annotation.trim())
		? node.annotation.trim()
		: "";
	const elemSection = document.createElement("div");
	elemSection.className = "wtrl-section";

	const elemSectionHead = document.createElement("div");
	elemSectionHead.className = "wtrl-section-head";
	const appendKindLabel = (label, kindClass) => {
		const elemLabel = document.createElement("span");
		elemLabel.textContent = label;
		elemSectionHead.appendChild(elemLabel);
		if (annotation) {
			const elemSep = document.createTextNode(" : ");
			elemSectionHead.appendChild(elemSep);
			const elemAnn = document.createElement("span");
			elemAnn.className = kindClass || "wtrl-type wtrl_type";
			elemAnn.textContent = annotation;
			elemSectionHead.appendChild(elemAnn);
		}
	};
	if (kind === "type") {
		elemSectionHead.className += " wtrl-type wtrl_type";
		appendKindLabel("Type", "wtrl-type wtrl_type");
	} else if (kind === "variable") {
		elemSectionHead.className += " wtrl-var wtrl_var";
		appendKindLabel("Variable", "wtrl-type wtrl_type");
	} else if (kind === "constant") {
		elemSectionHead.className += " wtrl-var wtrl_var";
		appendKindLabel("Constant", "wtrl-type wtrl_type");
	} else {
		elemSectionHead.textContent = "Entry";
	}
	elemSection.appendChild(elemSectionHead);

	// Render doc_lines as true freeform text so explicit list markers
	// (*, +, -, #) are interpreted the same way as in other freeform sections.
	renderFreeformText(elemSection, lines.map(line => String(line)).join("\n"));
	elemHost.appendChild(elemSection);
	return true;
}

function renderDoc(targetQid) {
	const objects = WTRL_DATA.objects || {};
	const examples = WTRL_DATA.examples || {};
	const node = objects[targetQid];
	byId("wtrl-title").textContent = targetQid || "(no selection)";
	const elemSubtitle = byId("wtrl-sub");
	if (!node) {
		if (elemSubtitle) elemSubtitle.textContent = "No object found.";
		byId("wtrl-signature").innerHTML = "";
		byId("wtrl-doc").innerHTML = "";
		byId("wtrl-examples").innerHTML = "";
		setTextIfPresent("wtrl-obj", "");
		return;
	}
	if (elemSubtitle) elemSubtitle.textContent = "Waterloo docstring";
	renderSignature(node, targetQid, byId("wtrl-signature"));
	const elemDocHost = byId("wtrl-doc");
	elemDocHost.innerHTML = "";
	const hasDocLines = renderDocLines(node, targetQid, elemDocHost);
	if (node.doc && typeof node.doc === "object" && Object.keys(node.doc).length > 0) {
		renderValue(node.doc, elemDocHost, 0, [], targetQid);
	} else if (!hasDocLines) {
		const elemNoDoc = document.createElement("p");
		elemNoDoc.className = "wtrl-text";
		elemNoDoc.textContent = "(no doc node)";
		elemDocHost.appendChild(elemNoDoc);
	}
/*----- render examples --------------------------------------*/
	const elemExamplesHost = byId("wtrl-examples");
// All example blocks are appended to this element.
	elemExamplesHost.innerHTML = "";
	const exPtrs = Array.isArray(node.examples) ? node.examples : [];
// Iterate over example entries of the current object
	for (const ptr of exPtrs) {
// Robust coding style: ignore entries with wrong type.
		if (typeof ptr !== "string") continue;
		const pfx = "/__WTRL_EXAMPLES__/";
// Similar: Any reference not starting with the prefix would
// be bad format, but it's not our job here to point out bugs,
// since we only want to render.
		if (!ptr.startsWith(pfx)) continue;
// Remove the prefix and extract the example key, which is essentially the sha256 hash.
		const exKey = ptr.slice(pfx.length);
// The example entry.
		const exNode = examples[exKey];
		if (!exNode || typeof exNode !== "object") continue;
// For each example build a section box.
		const elemExampleSection = document.createElement("div");
		elemExampleSection.className = "wtrl-section wtrl-examples";
// Render a headline
		const elemExampleHead = document.createElement("div");
		elemExampleHead.className = "wtrl-section-head";
		elemExampleHead.textContent = "Example";
		elemExampleSection.appendChild(elemExampleHead);
// If we know the path to the example source file, render the path
		if (typeof exNode.path === "string" && exNode.path) {
			const elemPathHead = document.createElement("div");
			elemPathHead.className = "wtrl-example-head";
			const elemPath = document.createElement("span");
			elemPath.className = "wtrl-file wtrl_file";
			elemPath.textContent = exNode.path;
			elemPathHead.appendChild(elemPath);
			elemExampleSection.appendChild(elemPathHead);
		}
// Finally render the code segment. The code is already HTML
// from pygments, so we use innerHTML to embed it here.
		const elemCode = document.createElement("div");
		elemCode.className = "wtrl-example-code";
		elemCode.innerHTML = WTRL_EXAMPLES_HTML[exKey] || "<pre><code>(no code)</code></pre>";
// Append code segment to example section box.
		elemExampleSection.appendChild(elemCode);
// Done. Append to examples block.
	elemExamplesHost.appendChild(elemExampleSection);
	}
	setTextIfPresent("wtrl-obj", JSON.stringify(node, null, 2));
}

// Select a documentation object by its qualified id and bring all
// related UI state in sync. Depending on the flags, this also updates
// the browser hash, mirrors the selection into the search field,
// records the jump in the local navigation history, and triggers rerendering.
// Options used in this source file are:
// - updateHash (default: false): whether to update the browser hash to match
//   the new selection. This also triggers hash-based navigation,
//   but that's handled by a separate event listener.
// - recordHistory (default: true): whether to record this jump in the local
//   navigation history, which is used for the back/forward buttons and the
//   history dropdown. This does not affect the browser history.
function selectTarget(targetQid, opts) {
	const options = opts || {};
	const updateHash = options.updateHash === true;
	const recordHistory = options.recordHistory !== false;
	if (updateHash) {
		const hit = WTRL_INDEX.find(x => x.target === targetQid && x.anchor);
		if (hit && hit.anchor) {
			location.hash = hit.anchor;
		} else {
			location.hash = "";
		}
	}
	byId("wtrl-search").value = targetQid;
	currentTargetQid = String(targetQid || "");
	if (recordHistory) pushHistory(currentTargetQid);
	renderDoc(targetQid);
}

// User has clicked a link which might lead to a different
// object in this document. We strip the leading hash and
// look for the target in our anchor map.
function handlerHashNavigation() {
	const h = (location.hash || "").replace(/^#/, "");
	if (!h) return false;

	clearDebugRefEvents();
	pushDebugRefEvent("hash-navigation-attempt", { hash: h });

	// Find object of the link target.
	const targetObj = anchorMap.get(h);
	// Are we already there? In case of a clicked
	// Definition Term: no, see segment below.
	if (targetObj) {
		pushDebugRefEvent("hash-navigation-object-anchor", {
			hash: h,
			target_qid: targetObj,
			already_selected: targetObj === currentTargetQid,
		});
		if (targetObj === currentTargetQid) return true;
		// Navigate to target object.
		selectTarget(targetObj, { recordHistory: false });
		return true;
	}

	// Now let's handle Definition Terms. We have a separate
	// anchor map for these. Again, find the object and navigate.
	const targetTerm = definitionTermAnchorMap.get(h);
	if (!targetTerm) {
		pushDebugRefEvent("hash-navigation-unresolved", { hash: h });
		return false;
	}
	pushDebugRefEvent("hash-navigation-term-anchor", {
		hash: h,
		target_qid: targetTerm,
		already_selected: targetTerm === currentTargetQid,
	});
	if (targetTerm !== currentTargetQid) {
		selectTarget(targetTerm, { recordHistory: false });
	}
	// Ensure scroll also works when the anchor appeared only after re-render.
	setTimeout(() => {
		// Scroll to the clicked Definition Term.
		const elemTarget = document.getElementById(h);
		const found = !!elemTarget;
		if (elemTarget) elemTarget.scrollIntoView({ block: "start", behavior: "auto" });
		pushDebugRefEvent("hash-navigation-term-scroll", {
			hash: h,
			found_element: found,
		});
	}, 0);
	return true;
}

function setupSearch() {
	const elemSearchInput = byId("wtrl-search");
	if (elemSearchInput) elemSearchInput.value = "";
	const elemSearchClear = byId("wtrl-search-clear");
	const elemNavBack = byId("wtrl-nav-back");
	const elemNavForward = byId("wtrl-nav-forward");
	const elemNavHistory = byId("wtrl-nav-history");
	const elemKindFilter = byId("wtrl-kind-filter");
	const elemLabelMode = byId("wtrl-label-mode");
	const elemSearchList = byId("wtrl-search-list");
	let activeSearchQuery = "";
	let activeKindFilter = elemKindFilter ? String(elemKindFilter.value || "*") : "*";
	let activeLabelMode = elemLabelMode ? String(elemLabelMode.value || "from-module") : "from-module";

	function refreshHitList() {
		const entries = filterHitEntries(WTRL_INDEX, activeKindFilter, activeSearchQuery);
		renderHitList(entries.map((e) => Object.assign({}, e, { label: formatHitLabel(e.label, activeLabelMode) })));
	}

	// Navigation event handlers. Note that we don't update the UI here directly;
	// instead we just update the history cursor and trigger a selectTarget(),
	// which will in turn trigger a re-render and an update of the navigation UI.
	if (elemNavBack) {
		elemNavBack.textContent = NAV_BACK_LABEL;
		elemNavBack.addEventListener("click", () => handlerHistoryDelta(-1));
	}
	if (elemNavForward) {
		elemNavForward.textContent = NAV_FORWARD_LABEL;
		elemNavForward.addEventListener("click", () => handlerHistoryDelta(1));
	}
	if (elemNavHistory) {
		elemNavHistory.addEventListener("change", () => {
			const raw = String(elemNavHistory.value || "").trim();
			if (!raw) return;
			const idx = Number.parseInt(raw, 10);
			if (!Number.isInteger(idx) || idx < 0 || idx >= historyTargets.length) return;
			if (idx === historyCursor) return;
			historyCursor = idx;
			updateNavigationUi();
			selectTarget(historyTargets[historyCursor], { updateHash: true, recordHistory: false });
		});
	}
	updateNavigationUi();
	if (elemKindFilter) {
		elemKindFilter.addEventListener("change", () => {
			activeKindFilter = String(elemKindFilter.value || "*");
			refreshHitList();
		});
	}
	if (elemLabelMode) {
		elemLabelMode.addEventListener("change", () => {
			activeLabelMode = String(elemLabelMode.value || "from-module");
			refreshHitList();
		});
	}
	for (const e of WTRL_INDEX) {
		const elemOption = document.createElement("option");
		elemOption.value = e.label;
		elemSearchList.appendChild(elemOption);
	}
	elemSearchInput.addEventListener("input", () => {
		activeSearchQuery = elemSearchInput.value.trim().toLowerCase();
		refreshHitList();
		const exact = WTRL_INDEX.find(e => e.label === elemSearchInput.value);
		if (exact) {
			selectTarget(exact.target, { updateHash: true });
		}
	});
	if (elemSearchClear) {
		elemSearchClear.addEventListener("click", () => {
			elemSearchInput.value = "";
			activeSearchQuery = "";
			refreshHitList();
			elemSearchInput.focus();
		});
	}
	refreshHitList();
}

window.addEventListener("hashchange", () => { handlerHashNavigation(); });
window.addEventListener("DOMContentLoaded", () => {
	if (DEBUG_REFS_ENABLED) pushDebugRefEvent("debug-enabled", { query: window.location.search || "" });
	setupThemeSwitcher();
	byId("wtrl-scope").textContent = String((WTRL_DATA.meta || {}).scope || "");
	byId("wtrl-flavour").textContent = String((WTRL_DATA.meta || {}).flavour || "");
	byId("wtrl-modules").textContent = ((WTRL_DATA.meta || {}).modules || []).join(", ");
	byId("wtrl-num-classes").textContent = String(Object.keys(WTRL_DATA.toc_classes || {}).length);
	byId("wtrl-num-callables").textContent = String(Object.keys(WTRL_DATA.toc_callables || {}).length);
	setupSearch();
	renderHitList(WTRL_INDEX);
	if (!handlerHashNavigation()) {
		const first = WTRL_INDEX.find(e => e.kind === "mod") || WTRL_INDEX[0];
		if (first) selectTarget(first.target, { updateHash: true });
	}
});
