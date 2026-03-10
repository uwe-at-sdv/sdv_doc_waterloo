const vscode = require('vscode');
const { execFile } = require('child_process');
const path = require('path');

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

function getClassHeader(document, startLine) {
	let headerText = "";
	let openBrackets = 0;
	let foundStart = false;
	let currentLine = startLine;

	// 1. Collect decorators above
	let decoratorLines = [];
	for (let i = startLine - 1; i >= 0; i--) {
		const line = document.lineAt(i).text.trim();
		if (line.startsWith('@')) {
			decoratorLines.unshift(document.lineAt(i).text);
		} else if (line !== "" && !line.startsWith('#')) {
			break;
		}
	}

	// 2. Read the header (class...:)
	while (currentLine < document.lineCount) {
		let lineText = document.lineAt(currentLine).text;

		// Mask strings (due to possible special chars in default values)
		const sanitized = lineText.replace(/(["'])(?:(?=(\\?))\2.)*?\1/g, "''");

		// Find start (responds to "class ")
		if (!foundStart && sanitized.match(/^\s*class\s+/)) {
			foundStart = true;
		}

		if (foundStart) {
			headerText += lineText + "\n";

			// Count brackets (for inheritance: class MyClass(Base):)
			openBrackets += (sanitized.match(/\(/g) || []).length;
			openBrackets -= (sanitized.match(/\)/g) || []).length;

			// End found when brackets balance AND colon is present
			if (openBrackets <= 0 && sanitized.includes(':')) {
				break;
			}
		}
		currentLine++;
	}

	// 3. Clean and append 'pass' for syntactic correctness
	const draft_code = (decoratorLines.join("\n") + "\n" + headerText).trim();
	// Use your trusty multiline regex for comments
	const final_code = draft_code.replace(/\s*#.*$/m, "");

	return final_code.trim() + " pass\n";
} 

function getFunctionHeader(document, startLine) {
	let headerText = "";
	let openBrackets = 0;
	let foundStart = false;
	let currentLine = startLine;

	// 1. Collect decorators above
	let decoratorLines = [];
	for (let i = startLine - 1; i >= 0; i--) {
		const line = document.lineAt(i).text.trim();
		if (line.startsWith('@')) {
			decoratorLines.unshift(document.lineAt(i).text);
		} else if (line !== "" && !line.startsWith('#')) {
			break;
		}
	}

	// 2. Read the header (def ...:)
	while (currentLine < document.lineCount) {
		let lineText = document.lineAt(currentLine).text;

		// Mask strings (due to possible special chars in default values)
		const sanitized = lineText.replace(/(["'])(?:(?=(\\?))\2.)*?\1/g, "''");

		// Find start (responds to "def ")
		if (!foundStart && sanitized.includes('def ')) {
			foundStart = true;
		}

		if (foundStart) {
			headerText += lineText + "\n";

			// Count brackets (for inheritance: class MyClass(Base):)
			openBrackets += (sanitized.match(/\(/g) || []).length;
			openBrackets -= (sanitized.match(/\)/g) || []).length;

			// End found when brackets balance AND colon is present
			if (openBrackets <= 0 && sanitized.includes(':')) {
				break;
			}
		}
		currentLine++;
	}

	// 3. Clean and append 'pass' for syntactic correctness
	const draft_code = (decoratorLines.join("\n") + "\n" + headerText).trim();
	const final_code = draft_code.replace(/\s*#.*$/m, "");
	return final_code.trim() + " pass\n";
} 

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
// in order to ensure the extansion does not block under any circumstances.
function runPythonJsonCommand(scriptPath, payload) {
	return new Promise((resolve, reject) => {
		const child = execFile(
			'python3',
			[scriptPath],
			{
				timeout: 5000,
				maxBuffer: 1024 * 1024,
			},
			(error, stdout, stderr) => {
				if (error) {
					const details = stderr ? ` ${stderr}` : "";
					reject(new Error(`python3 failed:${details}`));
					return;
				}
				try {
					resolve(JSON.parse(stdout));
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

function activate(context) {
	// Variables are called "disposable" because they have a method .dispose()
	// which explicitly frees any resource acquired.
	let disposableGenerateMinimal = vscode.commands.registerCommand('waterloo.generateMinimalDocstring', async () => {
		const editor = vscode.window.activeTextEditor;
		if (!editor) {
			vscode.window.showErrorMessage("Waterloo: No active editor.");
			return;
		}
		const position = editor.selection.active;
		const currentLineText = editor.document.lineAt(position.line).text;
		const pythonScript = path.join(context.extensionPath, 'funcdef_parser.py');

		let kind = null;
		let sourceFragment = "";
		const currentKind = getDefOrClassKind(currentLineText);
		if (currentKind === "def") {
			kind = "function";
			sourceFragment = getFunctionHeader(editor.document, position.line);
		} else if (currentKind === "class") {
			kind = "class";
			sourceFragment = getClassHeader(editor.document, position.line);
		} else if (isModuleDocstringPosition(editor.document, position.line)) {
			kind = "module";
			sourceFragment = "";
		} else {
			vscode.window.showErrorMessage("Waterloo: Current line is neither 'def' nor 'class' and not a module-docstring position.");
			return;
		}

		const request = {
			version: 1,
			command: "generate_minimal_docstring_to_tmp",
			kind: kind,
			source_fragment: sourceFragment
		};

		try {
			const data = await runPythonJsonCommand(pythonScript, request);
			if (data.ok && data.tmp_file) {
				vscode.window.showInformationMessage(`Waterloo: Minimal docstring saved to ${data.tmp_file}`);
			} else {
				vscode.window.showErrorMessage(`Waterloo: ${data.error || "Unknown parser error."}`);
			}
		} catch (err) {
			vscode.window.showErrorMessage("Waterloo: Error generating minimal docstring: " + err);
		}
	});
	// Register a function referenced in package.json: "contributes->commands->command"
	let disposableTest = vscode.commands.registerCommand('waterloo.testMenu', () => {
		vscode.window.showInformationMessage("Waterloo: Test Menu Item clicked.");
	});

	// Rebuild context menu right now at extension activation, if conditions apply.
	updateFuncClassModuleContext(vscode.window.activeTextEditor);
	// Make sure vscode always tries to rebuild context menu when editor changes and conditions apply.
	// Mouse position and text selection are states of the text editor, so this makes sense.
	context.subscriptions.push(
		vscode.window.onDidChangeActiveTextEditor((editor) => {
			updateFuncClassModuleContext(editor);
		})
	);
	// Make sure vscode always tries to rebuild context menu when user clicks something and conditions apply
	context.subscriptions.push(
		vscode.window.onDidChangeTextEditorSelection((event) => {
			updateFuncClassModuleContext(event.textEditor);
		})
	);

	context.subscriptions.push(disposableGenerateMinimal);
	context.subscriptions.push(disposableTest);
}

exports.activate = activate;
