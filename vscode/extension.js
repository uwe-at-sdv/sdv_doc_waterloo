// Package version is declared in package.json.

const vscode = require('vscode');
const { execFile, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const MAX_HEADER_LINES = 100;
const MAX_HEADER_CHARS = 65536;

// Keep one output channel for activation messages, errors, and provider tracing.
const fout = vscode.window.createOutputChannel('Channel.Waterloo');

// Fatal error codes for activation failures.
// Phase A: backend script and Python availability.
const FATAL_BACKEND_NOT_FOUND = "WTRL_VSCODE_PYTHON_BACKEND_NOT_AVAILABLE";
const FATAL_BACKEND_NOT_READABLE = "WTRL_VSCODE_PYTHON_BACKEND_NOT_READABLE";
const FATAL_PYTHON_NOT_AVAILABLE = "WTRL_VSCODE_PYTHON_NOT_AVAILABLE";
const FATAL_WATERLOO_PACKAGE_NOT_AVAILABLE = "WTRL_VSCODE_WATERLOO_PACKAGE_NOT_AVAILABLE";
// Phase B: backend ping / protocol checks.
const FATAL_BACKEND_PING_FAILED = "WTRL_VSCODE_PYTHON_BACKEND_PING_FAILED";
const FATAL_BACKEND_PROTOCOL_ERROR = "WTRL_VSCODE_PYTHON_BACKEND_PROTOCOL_ERROR";
// Capability strings that the backend can report.
// They are used to enable or hide commands and menu entries.
const CAP_GENERATE_MINIMAL = "generateMinimalDocstring";
const CAP_GENERATE_FULL = "generateFullDocstring";
const CAP_VALIDATE = "validateDocstring";
const CAP_COVERAGE = "validateCoverageDocstring";

function shouldShowSuccessNotifications() {
	const cfg = vscode.workspace.getConfiguration("waterloo");
	return cfg.get("showSuccessNotifications", true);
}

function getIgnoreList() {
	const cfg = vscode.workspace.getConfiguration("waterloo");
	const configured = cfg.get("ignoreList", ["VLII-001"]);
	if (!Array.isArray(configured)) {
		return ["VLII-001"];
	}
	return configured
		.map((item) => String(item).trim())
		.filter((item) => item.length > 0);
}

function getPythonExecutable() {
	const cfg = vscode.workspace.getConfiguration("waterloo");
	return String(cfg.get("pythonExecutable", "python3")).trim() || "python3";
}

function getInstalledWaterlooPackageRoot() {
	const pythonExecutable = getPythonExecutable();
	const pythonOutput = execFileSync(pythonExecutable, [
		'-c',
		'import pathlib\n' +
		'try: import sdv.doc.waterloo.docitem_helper as h\n' +
		'except ModuleNotFoundError as e:\n' +
		'    if e.name in {"sdv.doc", "sdv.doc.waterloo"}: raise SystemExit(1)\n' +
		'    raise\n' +
		'print(pathlib.Path(h.__file__).resolve().parent)'
	], { encoding: 'utf-8', timeout: 5000, stdio: ['pipe', 'pipe', 'pipe'] }).trim();
	return pythonOutput.length > 0 ? pythonOutput : null;
}

function formatMissingWaterlooPackageDetail() {
	const pythonExecutable = getPythonExecutable();
	return	`-- sdv.doc.waterloo is not installed for the environment of executable '${pythonExecutable}'.\n\n` +
		`Install sdv-doc-waterloo in that Python environment from one of\n\n` +
		`++ Github: pip install "git+https://github.com/uwe-at-sdv/sdv_doc_waterloo.git@main"\n` +
		`++ PyPI:   pip install sdv-doc-waterloo\n` +
		`\n` +
		"Depending on your Python environment, you might need to use `pip install`, `uv add`, or `poetry add` in your project terminal."
		;
}

function getClassKind(text) {
	if (/^\s*class\b/.test(text)) {
		return "class";
	}
	return null;
}
function getDefKind(text) {
	if (/^\s*def\b/.test(text)) {
		return "def";
	}
	return null;
}
function getDefOrClassKind(text) {
	return getDefKind(text) || getClassKind(text);
}
function isDefOrClassLine(text)	{
	return getDefKind(text) !== null || getClassKind(text) !== null;
}

function isFuncClassOrModuleLine(document, line, text) {
	return isDefOrClassLine(text) || isModuleDocstringPosition(document, line);
}

function isClassOrModuleLine(document, line, text) {
	return getClassKind(text) !== null || isModuleDocstringPosition(document, line);
}

function isEncodingCommentLine(text) {
	return /^\s*#.*coding[:=]\s*[-\w.]+/i.test(text);
}

function isModuleDocstringPosition(document, line) {
	if (line < 0 || line >= document.lineCount) {
		return false;
	}
	for (let i = 0; i < line; i++) {
		const text = document.lineAt(i).text;
		if (/^\s*$/.test(text)) {
			continue;
		}
		if (i === 0 && /^\s*#!.*/.test(text)) {
			continue;
		}
		if (i <= 1 && isEncodingCommentLine(text)) {
			continue;
		}
		if (/^\s*#/.test(text)) {
			continue;
		}
		return false;
	}
	return true;
}

function countChar(text, ch) {
	return (text.match(new RegExp(`\\${ch}`, 'g')) || []).length;
}

// text must be sanitized from string literals.
function hasTopLevelColon(text) {
	let parenDepth = 0;
	let bracketDepth = 0;
	let braceDepth = 0;
	for (const ch of text) {
		if (ch === '(') {
			parenDepth += 1;
			continue;
		}
		if (ch === ')') {
			parenDepth = Math.max(0, parenDepth - 1);
			continue;
		}
		if (ch === '[') {
			bracketDepth += 1;
			continue;
		}
		if (ch === ']') {
			bracketDepth = Math.max(0, bracketDepth - 1);
			continue;
		}
		if (ch === '{') {
			braceDepth += 1;
			continue;
		}
		if (ch === '}') {
			braceDepth = Math.max(0, braceDepth - 1);
			continue;
		}
		if (ch === ':' && parenDepth === 0 && bracketDepth === 0 && braceDepth === 0) {
			return true;
		}
	}
	return false;
}

function enforceHeaderLimits(headerText, linesRead, kind) {
	if (linesRead > MAX_HEADER_LINES) {
		throw new Error(`Waterloo: ${kind} header exceeds ${MAX_HEADER_LINES} lines.`);
	}
	if (headerText.length > MAX_HEADER_CHARS) {
		throw new Error(`Waterloo: ${kind} header exceeds ${MAX_HEADER_CHARS} characters.`);
	}
}

function collectDecoratorLines(document, startLine) {
	let decoratorLines = [];
	// We walk upward because decorators are written above the def/class line
	// they belong to. We stop as soon as we hit real code.
	for (let i = startLine - 1; i >= 0; i--) {
		const line = document.lineAt(i).text;
		const stripped = line.trim();
		// Decorators belong to the next def/class header, but only as long as we
		// do not cross a real code line. Blank lines and comment lines are safe.
		if (/^\s*@/.test(line)) {
			decoratorLines.unshift(document.lineAt(i).text);
		} else if (stripped !== "" && !stripped.startsWith('#')) {
			break;
		}
	}
	return decoratorLines;
}

function scanHeader(document, startLine, startRegex, kindLabel) {
	let headerText = "";
	let openDelimiters = 0;
	let foundStart = false;
	let currentLine = startLine;
	let linesRead = 0;

	// Walk forward from the selected line until we have seen the full header.
	// The scanner is intentionally lightweight: it does not parse Python ASTs.
	// It only wants enough text to reconstruct a minimal valid header.
	//
	// This supports multiline signatures such as:
	//   def f(
	//       x: int,
	//       y: str,
	//   ) -> None:
	while (currentLine < document.lineCount) {
		let lineText = document.lineAt(currentLine).text;

		// Replace quoted strings with neutral placeholders so brackets, commas,
		// or colons inside default values do not confuse the header scanner.
		const lineSanitized = lineText.replace(/(["'])(?:(?=(\\?))\2.)*?\1/g, "''");

		// Wait until the selected line or a later line actually looks like the
		// start of a class/def header.
		if (!foundStart && lineSanitized.match(startRegex)) {
			foundStart = true;
		}

		if (foundStart) {
			headerText += lineText + "\n";
			linesRead += 1;
			enforceHeaderLimits(headerText, linesRead, kindLabel);

			// Track open delimiters so we do not stop too early on a colon that is
			// inside parentheses, brackets, or braces.
			openDelimiters += countChar(lineSanitized, '(');
			openDelimiters -= countChar(lineSanitized, ')');
			openDelimiters += countChar(lineSanitized, '[');
			openDelimiters -= countChar(lineSanitized, ']');
			openDelimiters += countChar(lineSanitized, '{');
			openDelimiters -= countChar(lineSanitized, '}');

			// When the delimiters balance and the line has a top-level colon, the
			// header is complete.
			if (openDelimiters <= 0 && hasTopLevelColon(lineSanitized)) {
				return { headerText, endLine: currentLine };
			}
		}
		currentLine++;
	}

	if (!foundStart) {
		throw new Error(`Waterloo: Could not find ${kindLabel} header start.`);
	}
	throw new Error(`Waterloo: Could not find end of ${kindLabel} header.`);
}

function getClassHeaderInfo(document, startLine) {
	// Collect decorators first, because they logically belong to the class.
	let decoratorLines = collectDecoratorLines(document, startLine);
	const headerScan = scanHeader(document, startLine, /^\s*class\s+/, "class");

	// Rebuild a minimal but syntactically valid class definition for backend use.
	const headerText = headerScan.headerText;
	const draft_code = (decoratorLines.join("\n") + "\n" + headerText).trim();
	// Strip inline comments so the synthetic snippet stays compact and parseable.
	const final_code = draft_code.replace(/\s*#.*$/m, "");

	return {
		sourceFragment: final_code.trim() + " pass\n",
		endLine: headerScan.endLine,
	};
}

function getFunctionHeaderInfo(document, startLine) {
	// Collect decorators first, because they logically belong to the function.
	let decoratorLines = collectDecoratorLines(document, startLine);
	const headerScan = scanHeader(document, startLine, /^\s*def\s+/, "function");

	// Rebuild a minimal but syntactically valid function definition for backend use.
	const headerText = headerScan.headerText.trim();
	const draft_code = (decoratorLines.join("\n") + "\n" + headerText).trim();
	// Strip inline comments so the synthetic snippet stays compact and parseable.
	const final_code = draft_code.replace(/\s*#.*$/m, "");
	return {
		sourceFragment: final_code.trim() + " pass\n",
		endLine: headerScan.endLine,
		headerText: headerText,
		decoratorLines: decoratorLines,
	};
}

function splitTopLevelComma(text) {
	let parts = [];
	let current = "";
	let parenDepth = 0;
	let bracketDepth = 0;
	let braceDepth = 0;
	// Split only at commas that are not nested inside brackets or braces.
	for (const ch of text) {
		if (ch === ',' && parenDepth === 0 && bracketDepth === 0 && braceDepth === 0) {
			parts.push(current);
			current = "";
			continue;
		}
		current += ch;
		if (ch === '(') parenDepth += 1;
		if (ch === ')') parenDepth = Math.max(0, parenDepth - 1);
		if (ch === '[') bracketDepth += 1;
		if (ch === ']') bracketDepth = Math.max(0, bracketDepth - 1);
		if (ch === '{') braceDepth += 1;
		if (ch === '}') braceDepth = Math.max(0, braceDepth - 1);
	}
	parts.push(current);
	return parts;
}

function extractFirstParameterNameFromFunctionHeader(headerText) {
	// This is a heuristic, not a parser. We just need to detect the first
	// positional parameter well enough to distinguish function from method in
	// the common cases.
	const sanitized = headerText.replace(/(["'])(?:(?=(\\?))\2.)*?\1/g, "''");
	const defMatch = sanitized.match(/\bdef\s+[A-Za-z_][A-Za-z0-9_]*\s*\(/);
	if (!defMatch || defMatch.index === undefined) {
		return null;
	}
	const parenStart = sanitized.indexOf('(', defMatch.index);
	if (parenStart < 0) {
		return null;
	}
	let i = parenStart + 1;
	let parenDepth = 0;
	let bracketDepth = 0;
	let braceDepth = 0;
	let paramsText = "";
	// Read the parameter list of the function header one character at a time.
	// We stop at the matching ')' that closes the outer def(...).
	while (i < sanitized.length) {
		const ch = sanitized[i];
		if (ch === ')' && parenDepth === 0 && bracketDepth === 0 && braceDepth === 0) {
			break;
		}
		paramsText += ch;
		if (ch === '(') parenDepth += 1;
		if (ch === ')') parenDepth = Math.max(0, parenDepth - 1);
		if (ch === '[') bracketDepth += 1;
		if (ch === ']') bracketDepth = Math.max(0, bracketDepth - 1);
		if (ch === '{') braceDepth += 1;
		if (ch === '}') braceDepth = Math.max(0, braceDepth - 1);
		i += 1;
	}
	const parts = splitTopLevelComma(paramsText);
	for (const part of parts) {
		const p = part.trim();
		if (p === "" || p === "/" || p === "*") {
			continue;
		}
		const m = p.match(/^\*{0,2}\s*([A-Za-z_][A-Za-z0-9_]*)/);
		if (m) {
			return m[1];
		}
	}
	return null;
}

function classifyFunctionVsMethod(lineText, headerInfo) {
	// The backend needs to know whether the generated docstring should be for a
	// function or a method. This is only heuristic, so we try the strongest
	// signals first and keep the fallback behavior simple.
	// 1. Decorator-based detection.
	for (const decLineRaw of headerInfo.decoratorLines) {
		const decLine = decLineRaw.trim();
		if (/^@\s*(?:[A-Za-z_][A-Za-z0-9_]*\.)*(?:classmethod|staticmethod)\b/.test(decLine)) {
			return { kind: "method", confidence: "high", reason: "decorator classmethod/staticmethod" };
		}
	}

	// 2. First-parameter heuristic.
	const firstParam = extractFirstParameterNameFromFunctionHeader(headerInfo.headerText);
	if (firstParam === "self" || firstParam === "cls") {
		return { kind: "method", confidence: "high", reason: `first parameter '${firstParam}'` };
	}

	// 3. Indentation fallback.
	const indent = (lineText.match(/^\s*/) || [""])[0];
	if (indent.length > 0) {
		return { kind: "method", confidence: "low", reason: "indented def line fallback" };
	}

	// 4. Default fallback. We classify this as high for the time being because it is
	// one of the most common cases and the messages annoy a little. We know indent is 0,
	// so it's not really a bad guess.
	return { kind: "function", confidence: "high", reason: "default function fallback" };
}

function getIndentUnit(editor) {
	const insertSpaces = editor.options.insertSpaces === true;
	if (!insertSpaces) {
		// Keep tab indentation when the file uses tabs.
		return "\t";
	}
	else {
		// Otherwise use four spaces, which is the project's default style.
		return "    ";
	}
}

// Normalize user-facing text to the indentation style of the current file.
function normalizeDocstringIndent(rawDocstring, editor) {
	return rawDocstring.replace(/\t/g, getIndentUnit(editor));
}

function indentNonEmptyLines(text, prefix) {
	return text
		.split("\n")
		.map((line) => (line.length > 0 ? prefix + line : line))
		.join("\n");
}

function buildDocstringForInsertion(rawDocstring, kind, editor, lineTextForIndent) {
	const normalized = normalizeDocstringIndent(rawDocstring, editor);
	// Module docstrings are inserted at top level.
	if (kind === "module") {
		return normalized;
	}
	// For class/function/method docstrings we indent one level deeper than the
	// current declaration line, in line with PEP 257.
	const currentIndent = (lineTextForIndent.match(/^\s*/) || [""])[0];
	const bodyIndent = currentIndent + getIndentUnit(editor);
	return indentNonEmptyLines(normalized, bodyIndent);
}

// Update context variables used by package.json "when" clauses for the editor menu.
function updateFuncClassModuleContext(editor) {
	if (!editor || editor.document.languageId !== 'python') {
		void vscode.commands.executeCommand('setContext', 'waterloo.isFuncClassOrModuleLine', false);
		void vscode.commands.executeCommand('setContext', 'waterloo.isClassOrModuleLine', false);
		return;
	}
	const position = editor.selection.active;
	const lineText = editor.document.lineAt(position.line).text;
	// This context key drives the right-click menu. We recompute it often, so
	// the check stays deliberately cheap and only inspects the current cursor
	// position plus a small amount of surrounding context.
	void vscode.commands.executeCommand(
		'setContext',
		'waterloo.isFuncClassOrModuleLine',
		isFuncClassOrModuleLine(editor.document, position.line, lineText)
	);
	void vscode.commands.executeCommand(
		'setContext',
		'waterloo.isClassOrModuleLine',
		isClassOrModuleLine(editor.document, position.line, lineText)
	);
}

// The function is invoked with await, which is correct because
// it returns a(n explicitly constructed) promise. All this is done
// in order to ensure the extension does not block under any circumstances.
function runPythonJsonCommand(scriptPath, payload) {
	return new Promise((resolve, reject) => {
		const pythonExecutable = getPythonExecutable();
		// The Python backend is treated as a short-lived helper: we send one JSON
		// payload on stdin and expect one JSON object on stdout.
		// This keeps the Node side simple and avoids having to keep a long-lived
		// Python process in sync with the editor state.
		const child = execFile(
			pythonExecutable,
			[scriptPath],
			{
				timeout: 5000,
				maxBuffer: 1024 * 1024,
				encoding: 'utf8',
			},
			(error, stdout, stderr) => {
				const stdoutText = typeof stdout === "string" ? stdout.trim() : "";
				if (stdoutText.length > 0) {
					try {
						resolve(JSON.parse(stdoutText));
						return;
					} catch (_parseError) {
						// Fall through to process-error handling below.
					}
				}
				if (error) {
					const details = stderr ? ` ${stderr}` : "<nostderr>";
					fout.appendLine("payload:");
					fout.appendLine(JSON.stringify(payload, null, 2));
					fout.show(true);
					reject(new Error(`${pythonExecutable} failed:${details}, ${error}`));
					return;
				}
				try {
					resolve(JSON.parse(stdoutText));
				} catch (parseError) {
					reject(new Error(`Invalid JSON response from parser: ${parseError}`));
				}
			}
		);

		if (!child.stdin) {
			reject(new Error("Could not open stdin for python3 process."));
			return;
		}
		child.stdin.write(JSON.stringify(payload));
		child.stdin.end();
	});
}

function setBackendReady(value) {
	void vscode.commands.executeCommand('setContext', 'waterloo.backendReady', value);
}

// This function updates the context keys related to the capabilities supported by the backend.
// In package.json, rendering the context submenu items is connected to these
// context variables (see field "when" in "contributes->menus->waterloo.context").
function setCapabilities(capabilities) {
	const caps = new Set(Array.isArray(capabilities) ? capabilities : []);
	void vscode.commands.executeCommand('setContext', 'waterloo.cap.generateMinimalDocstring', caps.has(CAP_GENERATE_MINIMAL));
	void vscode.commands.executeCommand('setContext', 'waterloo.cap.generateFullDocstring', caps.has(CAP_GENERATE_FULL));
	void vscode.commands.executeCommand('setContext', 'waterloo.cap.validateDocstring', caps.has(CAP_VALIDATE));
	void vscode.commands.executeCommand('setContext', 'waterloo.cap.validateCoverageDocstring', caps.has(CAP_COVERAGE));
	void vscode.commands.executeCommand('setContext', 'waterloo.cap.any', caps.size > 0);
}

function resolveWaterlooMcpConfigPath() {
	const cfg = vscode.workspace.getConfiguration("waterloo");
	const configured = String(cfg.get("mcpConfigPath", "")).trim();

	// Absolute paths are the simplest case: use them as-is when they exist.
	if (configured.length > 0 && path.isAbsolute(configured)) {
		if (fs.existsSync(configured)) {
			return configured;
		}
		fout.appendLine(`Waterloo MCP provider: configured absolute path not found yet, passing through: ${configured}`);
		return configured;
	}

	// If the package is installed in editable mode, ask Python where the package
	// root lives and try the package-local etc/ directory next.
	// This makes the extension work both from the source tree and from an
	// editable install without forcing the user to enter a long path manually.
	try {
		const pkgRoot = getInstalledWaterlooPackageRoot();
		if (pkgRoot) {
			// This is the canonical location for the MCP provider config file for a properly installed package.
			const candidate = path.join(pkgRoot, 'etc', 'wtrl_mcp.stdio.toml');
			if (fs.existsSync(candidate)) {
				fout.appendLine(`Waterloo MCP provider: found TOML at package root: ${candidate}`);
				return candidate;
			}
		}
	} catch (_err) {
		// If Python or the package is unavailable, we still try workspace-relative fallbacks below.
	}

	// If the user supplied a relative path, interpret it against every open
	// workspace folder before falling back to canned locations.
	// This is helpful when the workspace already contains a local copy of the
	// config file and the user does not want to type an absolute path.
	if (configured.length > 0 && !path.isAbsolute(configured)) {
		const workspaceFolders = vscode.workspace.workspaceFolders || [];
		for (const folder of workspaceFolders) {
			const candidate = path.join(folder.uri.fsPath, configured);
			if (fs.existsSync(candidate)) {
				fout.appendLine(`Waterloo MCP provider: found TOML at configured relative path: ${candidate}`);
				return candidate;
			}
		}
	}

	return null;
}

function createWaterlooMcpServerDefinition() {
	const cfg = vscode.workspace.getConfiguration("waterloo");
	const command = String(cfg.get("mcpCommand", "wtrl_mcp")).trim() || "wtrl_mcp";
	const label = String(cfg.get("mcpServerLabel", "Waterloo Docs (stdio)")).trim() || "Waterloo Docs (stdio)";
	const configured = String(cfg.get("mcpConfigPath", "")).trim();
	const resolvedPath = resolveWaterlooMcpConfigPath();
	const configArg = resolvedPath || configured || "etc/wtrl_mcp.stdio.toml";
	if (!resolvedPath) {
		fout.appendLine(`Waterloo MCP provider: using fallback config argument: ${configArg}`);
	}
	fout.appendLine(
		`Waterloo MCP provider: advertising '${label}' via '${command} --config ${configArg}'.`
	);

	// Visual Studio Code's MCP API wants a stdio server definition, so we hand it the
	// command plus the config path we resolved above.
	const args = ["--config", configArg];
	return new vscode.McpStdioServerDefinition(label, command, args);
}

function registerWaterlooMcpProvider(context) {
	if (!vscode.lm || typeof vscode.lm.registerMcpServerDefinitionProvider !== "function") {
		fout.appendLine("Waterloo MCP provider: VS Code MCP API not available in this host/version.");
		return;
	}

	const cfg = vscode.workspace.getConfiguration("waterloo");
	if (cfg.get("mcpProvideServer", true) !== true) {
		fout.appendLine("Waterloo MCP provider: disabled by setting waterloo.mcpProvideServer.");
		return;
	}

	const provider = {
		provideMcpServerDefinitions: () => {
			const server = createWaterlooMcpServerDefinition();
			return server ? [server] : [];
		}
	};

	try {
		const disposable = vscode.lm.registerMcpServerDefinitionProvider("waterloo.mcpProvider", provider);
		context.subscriptions.push(disposable);
		fout.appendLine("Waterloo MCP provider: registered.");
	} catch (err) {
		fout.appendLine(`Waterloo MCP provider: registration failed: ${err}`);
	}
}

function emitFatalActivationError(code, detail) {
	const msg = `Waterloo fatal activation error: ${code}${detail ? `\n\n${detail}\n` : ""}`;
	fout.appendLine(msg);
	fout.show(true);
	vscode.window.showErrorMessage(msg);
}

// This function checks for the presence and readability of the Python backend script,
// as well as the availability of Python itself. It returns an object indicating
// success or failure and details (full path of the backend script).
function checkActivationPrerequisites(context) {
	const backendScript = path.join(context.extensionPath, 'extension_waterloo_commands.py');
	try {
		fs.accessSync(backendScript, fs.constants.F_OK);
	} catch (_err) {
		return { ok: false, code: FATAL_BACKEND_NOT_FOUND, detail: backendScript };
	}
	try {
		fs.accessSync(backendScript, fs.constants.R_OK);
	} catch (_err) {
		return { ok: false, code: FATAL_BACKEND_NOT_READABLE, detail: backendScript };
	}
	try {
		execFileSync(getPythonExecutable(), ['--version'], { timeout: 3000, stdio: 'ignore' });
	} catch (_err) {
		return { ok: false, code: FATAL_PYTHON_NOT_AVAILABLE, detail: getPythonExecutable() };
	}
	try {
		const pkgRoot = getInstalledWaterlooPackageRoot();
		if (!pkgRoot) {
			return { ok: false, code: FATAL_WATERLOO_PACKAGE_NOT_AVAILABLE, detail: formatMissingWaterlooPackageDetail() };
		}
		return { ok: true, backendScript, pkgRoot };
	} catch (err) {
		return { ok: false, code: FATAL_WATERLOO_PACKAGE_NOT_AVAILABLE, detail: formatMissingWaterlooPackageDetail() };
	}
}

async function installWaterlooBackendPackage(skipPrompt = false) {
	const cfg = vscode.workspace.getConfiguration("waterloo");
	return cfg.get("showSuccessNotifications", true);
}

function buildGenerationRequestContext(editor) {
	const position = editor.selection.active;
	const currentLineText = editor.document.lineAt(position.line).text;
	let kind = null;
	let sourceFragment = "";
	let insertionPosition = new vscode.Position(0, 0);
	// Determine whether the current line is a function, method, class, or module docstring position.
	const currentKind = getDefOrClassKind(currentLineText);
	if (currentKind === "def") {
		const headerInfo = getFunctionHeaderInfo(editor.document, position.line);
		const classification = classifyFunctionVsMethod(currentLineText, headerInfo);
		kind = classification.kind;
		if (classification.confidence !== "high") {
			fout.appendLine(
				`Heuristic classification is uncertain for def at line ${position.line + 1}: ` +
				`kind=${classification.kind}, reason=${classification.reason}`
			);
		}
		sourceFragment = headerInfo.sourceFragment;
		// For functions/methods, we insert the docstring after the function header, which is the line after the last line of the header.
		insertionPosition = new vscode.Position(headerInfo.endLine + 1, 0);
	} else if (currentKind === "class") {
		kind = "class";
		const headerInfo = getClassHeaderInfo(editor.document, position.line);
		sourceFragment = headerInfo.sourceFragment;
		// For classes, we insert the docstring after the class header, which is the line after the last line of the header.
		insertionPosition = new vscode.Position(headerInfo.endLine + 1, 0);
	} else if (isModuleDocstringPosition(editor.document, position.line)) {
		kind = "module";
		sourceFragment = "";
		// For module docstrings, we insert at the top of the file.
		insertionPosition = new vscode.Position(0, 0);
	} else {
		throw new Error("Current line is neither 'def' nor 'class' and not a module-docstring position.");
	}
	return { kind, sourceFragment, insertionPosition, currentLineText };
}

function logBackendErrorRules(data) {
	const errs = data?.diagnostics?.__WTRL_ERROR__;
	if (!Array.isArray(errs) || errs.length === 0) {
		return;
	}
	const rules = errs
		.map((entry) => entry && entry["rule-id"])
		.filter((rule) => typeof rule === "string");
	if (rules.length > 0) {
		fout.appendLine(`Backend error rules: ${rules.join(", ")}`);
	}
}

function stringifyDiagValue(value) {
	if (Array.isArray(value)) {
		return value.map((item) => stringifyDiagValue(item)).join("\n");
	}
	if (value && typeof value === "object") {
		return JSON.stringify(value, null, 2);
	}
	return String(value);
}

function formatDiagnosticEntryMessage(entry) {
	if (!entry || typeof entry !== "object") {
		return "";
	}
	const kind = typeof entry.kind === "string" ? entry.kind : "diagnostic";
	const origin = typeof entry.origin === "string" ? entry.origin : "tool";
	const ruleId = typeof entry["rule-id"] === "string" ? ` [Rule ${entry["rule-id"]}]` : "";
	const msg = typeof entry.msg === "string" ? entry.msg : "";
	return `- ${kind} [${origin}]${ruleId} ${msg}`.trim();
}

function formatDiagnosticEntryWithDetails(entry) {
	if (!entry || typeof entry !== "object") {
		return "";
	}
	const lines = [formatDiagnosticEntryMessage(entry)];
	for (const key of ["found", "expected", "hint"]) {
		if (!(key in entry)) {
			continue;
		}
		const raw = entry[key];
		if (raw === undefined || raw === null || raw === "") {
			continue;
		}
		lines.push(`  ${key}:`);
		for (const line of stringifyDiagValue(raw).split(/\r?\n/)) {
			lines.push(`    ${line}`);
		}
	}
	return lines.join("\n");
}

function logDiagnosticsToChannel(diag, label = "") {
	if (!diag || typeof diag !== "object") {
		return;
	}
	const sections = [
		["__WTRL_ERROR__", "Errors"],
		["__WTRL_WARNING__", "Warnings"],
	];
	const blocks = [];
	if (label) {
		blocks.push(`${label} diagnostics:`);
	}
	for (const [key, label] of sections) {
		const entries = Array.isArray(diag[key]) ? diag[key] : [];
		if (entries.length === 0) {
			continue;
		}
		blocks.push(`${label} (${entries.length}):`);
		for (const entry of entries) {
			const formatted = formatDiagnosticEntryWithDetails(entry);
			if (formatted) {
				blocks.push(formatted);
			}
		}
	}
	fout.appendLine(blocks.join("\n"));
}

function buildValidationTerminalHint(request, data) {
	const payload = data?.data && typeof data.data === "object" ? data.data : {};
	const basedir = typeof payload?.module_dir === "string" && payload.module_dir.trim() !== ""
		? payload.module_dir
		: "<basedir>";
	let obj = typeof payload?.qualified_identifier === "string" ? payload.qualified_identifier.trim() : "";
	if (!obj && request?.kind === "module" && typeof request?.source_file === "string" && request.source_file.trim() !== "") {
		obj = path.basename(request.source_file, path.extname(request.source_file));
	}
	if (!obj) {
		obj = "<obj>";
	}
	const ignoreList = Array.isArray(request?.ignore) ? request.ignore : [];
	const ignoreArg = ignoreList.length > 0 ? ` --ignore "${ignoreList.join(" ")}"` : "";
	return `For a formatted terminal view of these messages, run:\nwaterlint validate --basedir ${basedir} --obj ${obj}${ignoreArg}`;
}

function pluralizeCount(count, singular, plural = `${singular}s`) {
	return `${count} ${count === 1 ? singular : plural}`;
}

function buildValidationPopupMessage(status, numErr = 0, numWarn = 0) {
	if (status === "failed") {
		if (numErr > 0 || numWarn > 0) {
			return `Waterloo: Validation failed. ${pluralizeCount(numWarn, "warning")}, ${pluralizeCount(numErr, "error")}. See Output Channel.Waterloo.`;
		}
		return "Waterloo: Validation failed. See Output Channel.Waterloo.";
	}
	if (status === "warnings") {
		return `Waterloo: Validation resulted in warnings. ${pluralizeCount(numWarn, "warning")}, ${pluralizeCount(numErr, "error")}. See Output Channel.Waterloo.`;
	}
	return "Waterloo: Validation passed.";
}

async function generateDocstringFromBackend(prereq, commandName, successModeLabel) {
	const editor = vscode.window.activeTextEditor;
	if (!editor) {
		vscode.window.showErrorMessage("Waterloo: No active editor.");
		return;
	}
	let generationContext;
	try {
		generationContext = buildGenerationRequestContext(editor);
	} catch (err) {
		vscode.window.showErrorMessage("Waterloo: " + err);
		return;
	}
	const request = {
		version: 1,
		command: commandName,
		kind: generationContext.kind,
		source_fragment: generationContext.sourceFragment,
	};
	try {
		const data = await runPythonJsonCommand(prereq.backendScript, request);
		const payload = data && data.data ? data.data : null;
		if (data.ok && payload && payload.tmp_file) {
			const rawDocstring = fs.readFileSync(payload.tmp_file, "utf-8");
			const docstring = buildDocstringForInsertion(
				rawDocstring,
				generationContext.kind,
				editor,
				generationContext.currentLineText
			);
			const applied = await editor.edit((editBuilder) => {
				editBuilder.insert(generationContext.insertionPosition, docstring);
			});
			if (!applied) {
				vscode.window.showErrorMessage("Waterloo: Could not apply edit in editor.");
				return;
			}
			if (shouldShowSuccessNotifications()) {
				vscode.window.showInformationMessage(
					`Waterloo: ${successModeLabel} docstring inserted (${generationContext.kind}).`
				);
			}
		} else {
			logBackendErrorRules(data);
			vscode.window.showErrorMessage(`Waterloo: ${data.error || "Unknown parser error."}`);
		}
	} catch (err) {
		vscode.window.showErrorMessage(`Waterloo: Error generating ${successModeLabel.toLowerCase()} docstring: ${err}`);
	}
}

async function validateDocstringInBackend(prereq, commandName) {
	const editor = vscode.window.activeTextEditor;
	if (!editor) {
		vscode.window.showErrorMessage("Waterloo: No active editor.");
		return;
	}
	if (editor.document.isDirty) {
		const saved = await editor.document.save();
		if (!saved) {
			vscode.window.showErrorMessage("Waterloo: Could not save the active document before validation.");
			return;
		}
	}
	let generationContext;
	try {
		generationContext = buildGenerationRequestContext(editor);
	} catch (err) {
		vscode.window.showErrorMessage("Waterloo: " + err);
		return;
	}
	const request = {
		version: 1,
		command: commandName,
		kind: generationContext.kind,
		source_fragment: generationContext.sourceFragment,
		include_diagnostics: true,
		ignore: getIgnoreList(),
		source_file: editor.document.uri.fsPath,
		line: editor.selection.active.line,
	};
	try {
		const data = await runPythonJsonCommand(prereq.backendScript, request);
		const summary = data?.diagnostics_summary || {};
		const numErr = Number(summary.error || 0);
		const numWarn = Number(summary.warning || 0);
		const diag = data?.diagnostics || {};
		logDiagnosticsToChannel(diag);
		if (numErr > 0 || numWarn > 0) {
			fout.appendLine(buildValidationTerminalHint(request, data));
		}
		fout.show(true);
		if (!data || data.ok !== true) {
			vscode.window.showErrorMessage(buildValidationPopupMessage("failed", numErr, numWarn));
			return;
		}
		if (numErr > 0) {
			vscode.window.showErrorMessage(buildValidationPopupMessage("failed", numErr, numWarn));
			return;
		}
		if (numWarn > 0) {
			vscode.window.showWarningMessage(buildValidationPopupMessage("warnings", numErr, numWarn));
			return;
		}
		vscode.window.showInformationMessage(buildValidationPopupMessage("passed", numErr, numWarn));
	} catch (err) {
		vscode.window.showErrorMessage(`Waterloo: Error validating docstring: ${err}`);
	}
}

async function activate(context) {
	fout.appendLine('Activating Waterloo extension...');
	fout.show(true);
	setBackendReady(false);
	setCapabilities([]);
	registerWaterlooMcpProvider(context);
	const prereq = checkActivationPrerequisites(context);
	// Phase-A: Existence and permissions checks, and Python availability check.
	if (!prereq.ok) {
		emitFatalActivationError(prereq.code, prereq.detail);
		fout.appendLine('Waterloo MCP provider remains active; skipping docstring backend setup.');
		return;
	}
	// Phase-B: Ping the backend to check if it is working at all, and that the protocol is compatible.
	try {
			const pingRequest = { version: 1, command: "ping" };
			const pingResponse = await runPythonJsonCommand(prereq.backendScript, pingRequest);
			if (!pingResponse || !pingResponse.ok) {
				const detail = pingResponse && pingResponse.error ? pingResponse.error : "backend returned not-ok for ping";
				emitFatalActivationError(FATAL_BACKEND_PING_FAILED, detail);
				return;
			}
			const pong = pingResponse.data || {};
			if (pong.command !== "pong" || pong.version !== 1) {
				emitFatalActivationError(FATAL_BACKEND_PROTOCOL_ERROR, JSON.stringify(pingResponse));
				return;
			}
			// Build the context with the supported capabilities reported by the backend.
			setCapabilities(pong.capabilities);
			// Details about installed waterloo module
			fout.appendLine("sdv.doc.waterloo    file: " + pong.sdv_doc_waterloo.file)
			fout.appendLine("sdv.doc.waterloo version: " + pong.sdv_doc_waterloo.version)
		}
	catch (err) {
		emitFatalActivationError(FATAL_BACKEND_PING_FAILED, String(err));
		fout.appendLine('Waterloo MCP provider remains active; skipping docstring backend setup.');
		return;
		}
	setBackendReady(true);
	fout.appendLine('done.');
	fout.show(true);

	// Variables are called "disposable" because they have a method .dispose()
	// which explicitly frees any resource acquired.
	let disposableGenerateMinimal = vscode.commands.registerCommand('waterloo.generateMinimalDocstring', async () => {
		await generateDocstringFromBackend(prereq, "generate_minimal_docstring_to_tmp", "Minimal");
	});

	let disposableGenerateFull = vscode.commands.registerCommand('waterloo.generateFullDocstring', async () => {
		await generateDocstringFromBackend(prereq, "generate_full_docstring_to_tmp", "Full");
	});

	let disposableValidate = vscode.commands.registerCommand('waterloo.validateDocstring', async () => {
		await validateDocstringInBackend(prereq, "validate_docstring");
	});

	let disposableValidateCoverage = vscode.commands.registerCommand('waterloo.validateCoverageDocstring', async () => {
		await validateDocstringInBackend(prereq, "validate_coverage_of_docstring");
	});

	updateFuncClassModuleContext(vscode.window.activeTextEditor);
	context.subscriptions.push(
		vscode.window.onDidChangeActiveTextEditor((editor) => {
			updateFuncClassModuleContext(editor);
		})
	);
	context.subscriptions.push(
		vscode.window.onDidChangeTextEditorSelection((event) => {
			updateFuncClassModuleContext(event.textEditor);
		})
	);

	context.subscriptions.push(disposableGenerateMinimal);
	context.subscriptions.push(disposableGenerateFull);
	context.subscriptions.push(disposableValidate);
	context.subscriptions.push(disposableValidateCoverage);
}

exports.activate = activate;
