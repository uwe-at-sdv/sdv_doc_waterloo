// version: see package.json

const vscode = require('vscode');
const { execFile, execFileSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const MAX_HEADER_LINES = 100;
const MAX_HEADER_CHARS = 65536;

// Create an output channel for logging. This is useful for debugging and error reporting.
const fout = vscode.window.createOutputChannel('Channel.Waterloo');

// Define fatal error codes for activation failures.
// Phase-A:
const FATAL_BACKEND_NOT_FOUND = "WTRL_VSCODE_PYTHON_BACKEND_NOT_AVAILABLE";
const FATAL_BACKEND_NOT_READABLE = "WTRL_VSCODE_PYTHON_BACKEND_NOT_READABLE";
const FATAL_PYTHON_NOT_AVAILABLE = "WTRL_VSCODE_PYTHON_NOT_AVAILABLE";
// Phase-B:
const FATAL_BACKEND_PING_FAILED = "WTRL_VSCODE_PYTHON_BACKEND_PING_FAILED";
const FATAL_BACKEND_PROTOCOL_ERROR = "WTRL_VSCODE_PYTHON_BACKEND_PROTOCOL_ERROR";
// Capability strings that the backend can report support for.
// These are used to conditionally enable/disable commands and UI elements.
const CAP_GENERATE_MINIMAL = "generateMinimalDocstring";
const CAP_GENERATE_FULL = "generateFullDocstring";
const CAP_VALIDATE = "validateDocstring";

function shouldShowSuccessNotifications() {
	const cfg = vscode.workspace.getConfiguration("waterloo");
	return cfg.get("showSuccessNotifications", true);
}

function getDefOrClassKind(text) {
	if (/^\s*def\b/.test(text)) {
		return "def";
	}
	if (/^\s*class\b/.test(text)) {
		return "class";
	}
	return null;
}

function isDefOrClassLine(text)	{
	return getDefOrClassKind(text) !== null;
}

function isFuncClassOrModuleLine(document, line, text) {
	return isDefOrClassLine(text) || isModuleDocstringPosition(document, line);
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
	for (let i = startLine - 1; i >= 0; i--) {
		const line = document.lineAt(i).text;
		const stripped = line.trim();
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

	// Read the header (`class ...:` or `def ...:`), including multiline cases.
	while (currentLine < document.lineCount) {
		let lineText = document.lineAt(currentLine).text;

		// Mask strings (due to possible special chars in default values)
		const lineSanitized = lineText.replace(/(["'])(?:(?=(\\?))\2.)*?\1/g, "''");

		// Find start.
		if (!foundStart && lineSanitized.match(startRegex)) {
			foundStart = true;
		}

		if (foundStart) {
			headerText += lineText + "\n";
			linesRead += 1;
			enforceHeaderLimits(headerText, linesRead, kindLabel);

			// Count all delimiters to avoid ending on colons inside [], {}, or ().
			openDelimiters += countChar(lineSanitized, '(');
			openDelimiters -= countChar(lineSanitized, ')');
			openDelimiters += countChar(lineSanitized, '[');
			openDelimiters -= countChar(lineSanitized, ']');
			openDelimiters += countChar(lineSanitized, '{');
			openDelimiters -= countChar(lineSanitized, '}');

			// End found when delimiters balance and a top-level colon exists.
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
	// 1. Collect decorators above
	let decoratorLines = collectDecoratorLines(document, startLine);
	const headerScan = scanHeader(document, startLine, /^\s*class\s+/, "class");

	// 2. Clean and append 'pass' for syntactic correctness
	const headerText = headerScan.headerText;
	const draft_code = (decoratorLines.join("\n") + "\n" + headerText).trim();
	// Use your trusty multiline regex for comments
	const final_code = draft_code.replace(/\s*#.*$/m, "");

	return {
		sourceFragment: final_code.trim() + " pass\n",
		endLine: headerScan.endLine,
	};
}

function getFunctionHeaderInfo(document, startLine) {
	// 1. Collect decorators above
	let decoratorLines = collectDecoratorLines(document, startLine);
	const headerScan = scanHeader(document, startLine, /^\s*def\s+/, "function");

	// 2. Clean and append 'pass' for syntactic correctness
	const headerText = headerScan.headerText.trim();
	const draft_code = (decoratorLines.join("\n") + "\n" + headerText).trim();
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

function classifyFunctionVsMethod(document, startLine, lineText, headerInfo) {
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
// Waterloo indentiation TAB
		return "\t";
	}
	else {
// Waterloo indentiation SPC4
		return "    "
	}
}

// Waterloo allows indentation with TAB or four SPC.
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
// For modules, no further indentation is required.
	if (kind === "module") {
		return normalized;
	}
// For class, function, and method we measure the indentation of the current line
// (as selected by user) and add one indentation unit, in accordance to PEP 257.
	const currentIndent = (lineTextForIndent.match(/^\s*/) || [""])[0];
	const bodyIndent = currentIndent + getIndentUnit(editor);
	return indentNonEmptyLines(normalized, bodyIndent);
}

// The function updates the context variable `waterloo.isFuncClassOrModuleLine`
// based on the current editor state (what is selected; position of the cursor)
// In package.json this context variable is used as a condition for rendering
// the context menu (right mouse button), see field "when".
function updateFuncClassModuleContext(editor)
	{
	if (!editor || editor.document.languageId !== 'python')
		{
		void vscode.commands.executeCommand('setContext', 'waterloo.isFuncClassOrModuleLine', false);
		return;
		}
	const position = editor.selection.active;
	const lineText = editor.document.lineAt(position.line).text;
	void vscode.commands.executeCommand(
		'setContext',
		'waterloo.isFuncClassOrModuleLine',
		isFuncClassOrModuleLine(editor.document, position.line, lineText)
		);
	}

// The function is invoked with await, which is correct because
// it returns a(n explicitly constructed) promise. All this is done
// in order to ensure the extension does not block under any circumstances.
function runPythonJsonCommand(scriptPath, payload) {
	return new Promise((resolve, reject) => {
		const child = execFile(
			'python3',
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
					reject(new Error(`python3 failed:${details}, ${error}`));
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
	void vscode.commands.executeCommand('setContext', 'waterloo.cap.any', caps.size > 0);
}

function emitFatalActivationError(code, detail) {
	const msg = `Waterloo fatal activation error: ${code}${detail ? ` - ${detail}` : ""}`;
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
		execFileSync('python3', ['--version'], { timeout: 3000, stdio: 'ignore' });
	} catch (_err) {
		return { ok: false, code: FATAL_PYTHON_NOT_AVAILABLE, detail: "python3" };
	}
	return { ok: true, backendScript };
}

function buildGenerationRequestContext(editor) {
	const position = editor.selection.active;
	const currentLineText = editor.document.lineAt(position.line).text;
	let kind = null;
	let sourceFragment = "";
	let insertionPosition = new vscode.Position(0, 0);
	const currentKind = getDefOrClassKind(currentLineText);
	if (currentKind === "def") {
		const headerInfo = getFunctionHeaderInfo(editor.document, position.line);
		const classification = classifyFunctionVsMethod(editor.document, position.line, currentLineText, headerInfo);
		kind = classification.kind;
		if (classification.confidence !== "high") {
			fout.appendLine(
				`Heuristic classification is uncertain for def at line ${position.line + 1}: ` +
				`kind=${classification.kind}, reason=${classification.reason}`
			);
		}
		sourceFragment = headerInfo.sourceFragment;
		insertionPosition = new vscode.Position(headerInfo.endLine + 1, 0);
	} else if (currentKind === "class") {
		kind = "class";
		const headerInfo = getClassHeaderInfo(editor.document, position.line);
		sourceFragment = headerInfo.sourceFragment;
		insertionPosition = new vscode.Position(headerInfo.endLine + 1, 0);
	} else if (isModuleDocstringPosition(editor.document, position.line)) {
		kind = "module";
		sourceFragment = "";
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
		fout.appendLine(`Backend diagnostics (error rules): ${rules.join(", ")}`);
	}
}

function collectRuleIdsBySeverity(diagRoot, key) {
	const entries = diagRoot && Array.isArray(diagRoot[key]) ? diagRoot[key] : [];
	return entries
		.map((entry) => entry && entry["rule-id"])
		.filter((rule) => typeof rule === "string");
}

function logBackendDiagnostics(data, label) {
	const diag = data?.diagnostics;
	if (!diag || typeof diag !== "object") {
		return;
	}
	const errorRules = collectRuleIdsBySeverity(diag, "__WTRL_ERROR__");
	const warningRules = collectRuleIdsBySeverity(diag, "__WTRL_WARNING__");
	const infoRules = collectRuleIdsBySeverity(diag, "__WTRL_INFO__");
	if (errorRules.length > 0) {
		fout.appendLine(`${label} diagnostics (error rules): ${errorRules.join(", ")}`);
	}
	if (warningRules.length > 0) {
		fout.appendLine(`${label} diagnostics (warning rules): ${warningRules.join(", ")}`);
	}
	if (infoRules.length > 0) {
		fout.appendLine(`${label} diagnostics (info rules): ${infoRules.join(", ")}`);
	}
}

function buildRuleSummary(diag) {
	const errorRules = collectRuleIdsBySeverity(diag, "__WTRL_ERROR__");
	const warningRules = collectRuleIdsBySeverity(diag, "__WTRL_WARNING__");
	const infoRules = collectRuleIdsBySeverity(diag, "__WTRL_INFO__");
	const fmt = (name, arr) => (arr.length > 0 ? `${name}: ${arr.join(", ")}` : "");
	return {
		errorRules,
		warningRules,
		infoRules,
		text: [fmt("Errors", errorRules), fmt("Warnings", warningRules), fmt("Infos", infoRules)]
			.filter((s) => s.length > 0)
			.join(" | "),
	};
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
	let generationContext;
	try {
		generationContext = buildGenerationRequestContext(editor);
	} catch (err) {
		vscode.window.showErrorMessage("Waterloo: " + err);
		return;
	}
	const position = editor.selection.active;
// Build request
	const request = {
		version: 1,
		command: commandName,
		kind: generationContext.kind,
		source_fragment: generationContext.sourceFragment,
		include_diagnostics: true,
// Get path of edited file
		source_file: editor.document.uri.fsPath,
// Find current line, zero-based in VSCode as it should be.
		line: editor.selection.active.line
	};
	try {
		const data = await runPythonJsonCommand(prereq.backendScript, request);
		const summary = data?.diagnostics_summary || {};
		const numErr = Number(summary.error || 0);
		const numWarn = Number(summary.warning || 0);
		const validatedQid = data?.data?.qualified_identifier || "<unknown>";
		const diag = data?.diagnostics || {};
		const ruleSummary = buildRuleSummary(diag);
		logBackendDiagnostics(data, "Validate");
		fout.show(true);
		if (!data || data.ok !== true) {
			const details = ruleSummary.text ? ` (${ruleSummary.text})` : "";
			vscode.window.showErrorMessage(`Waterloo: Validation failed: ${data?.error || "unknown backend error"}${details}`);
			return;
		}
		if (numErr > 0) {
			const details = ruleSummary.errorRules.length > 0 ? ` Rules: ${ruleSummary.errorRules.join(", ")}.` : "";
			vscode.window.showErrorMessage(`Waterloo: Validation failed for ${validatedQid} (${numErr} error(s)).${details}`);
			return;
		}
		if (numWarn > 0) {
			const details = ruleSummary.warningRules.length > 0 ? ` Rules: ${ruleSummary.warningRules.join(", ")}.` : "";
			vscode.window.showWarningMessage(`Waterloo: Validation finished for ${validatedQid} (${numWarn} warning(s)).${details}`);
			return;
		}
		const infoPart = ruleSummary.infoRules.length > 0 ? ` Infos: ${ruleSummary.infoRules.join(", ")}.` : "";
		vscode.window.showInformationMessage(`Waterloo: Validation passed for ${validatedQid}.${infoPart}`);
	} catch (err) {
		vscode.window.showErrorMessage(`Waterloo: Error validating docstring: ${err}`);
	}
}

async function activate(context) {
	fout.appendLine('Activating Waterloo extension...');
	fout.show(true);
	setBackendReady(false);
	setCapabilities([]);
	const prereq = checkActivationPrerequisites(context);
	// Phase-A: Existence and permissions checks, and Python availability check.
	if (!prereq.ok) {
		emitFatalActivationError(prereq.code, prereq.detail);
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
		}
		catch (err) {
			emitFatalActivationError(FATAL_BACKEND_PING_FAILED, String(err));
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
}

exports.activate = activate;
