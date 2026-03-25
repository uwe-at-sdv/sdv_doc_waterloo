const WTRL_DATA = __DATA_JSON__;
const WTRL_INDEX = __INDEX_JSON__;
const WTRL_EXAMPLES_HTML = __EXAMPLES_HTML_JSON__;

function byId(id) { return document.getElementById(id); }
const TARGET_TO_ANCHOR = new Map();
for (const e of WTRL_INDEX) {
  if (e.anchor) TARGET_TO_ANCHOR.set(e.target, e.anchor);
}
const NORM_RE = /\|(?:Must|must|Must_not|must_not|Should|should|Should_not|should_not|May|may)\|/g;
const TOK_RE = /(\|(?:Must|must|Must_not|must_not|Should|should|Should_not|should_not|May|may)\|)|(\|(?:None|Self|True|False)\|)|(\|([A-Za-z_][A-Za-z0-9_]*)\|`([^`]*)`)/g;
const ROLE_CLASS = {
  "func": "wtrl-func wtrl_func",
  "type": "wtrl-type wtrl_type",
  "var": "wtrl-var wtrl_var",
  "label": "wtrl-label wtrl_label",
  "value": "wtrl-value wtrl_value",
  "mod": "wtrl-mod wtrl_mod",
  "attr": "wtrl-attr wtrl_attr",
  "lit": "wtrl-lit wtrl_lit",
  "dfn": "wtrl-dfn wtrl_dfn",
  "term": "wtrl-term wtrl_term",
  "op": "wtrl-op wtrl_op",
  "file": "wtrl-file wtrl_file",
  "cmd": "wtrl-cmd wtrl_cmd",
  "opt": "wtrl-opt wtrl_opt",
  "tag": "wtrl-tag wtrl_tag",
  "ref": "wtrl-ref wtrl_ref"
};

function buildAnchorMap() {
  const m = new Map();
  for (const e of WTRL_INDEX) {
    if (e.anchor) m.set(e.anchor, e.target);
  }
  return m;
}

const anchorMap = buildAnchorMap();

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
  const d = document.createElement("div");
  d.className = "wtrl-signature-line";
  return d;
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
      const mod = document.createElement("span");
      mod.className = "wtrl-mod wtrl_mod";
      mod.textContent = parts.mod + ".";
      head.appendChild(mod);
    }
    if (parts.cls) {
      const cls = document.createElement("span");
      cls.className = "wtrl-type wtrl_type";
      cls.textContent = parts.cls + ".";
      head.appendChild(cls);
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
    const sp = document.createElement("span");
    sp.className = "wtrl-attr wtrl_attr";
    sp.textContent = String(deco);
    line.appendChild(sp);
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
    const mod = document.createElement("span");
    mod.className = "wtrl-mod wtrl_mod";
    mod.textContent = mod_name + ".";
    head.appendChild(mod);
  }

// Render class segment if we have one.
  if (class_name) {
    const cls = document.createElement("span");
    cls.className = "wtrl-type wtrl_type";
    cls.textContent = class_name + ".";
    head.appendChild(cls);
  }


  const fn = document.createElement("span");
  fn.className = "wtrl-func wtrl_func";
  fn.textContent = func_name;
  head.appendChild(fn);
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
    const psp = document.createElement("span");
    psp.className = "wtrl-var wtrl_var";
    psp.textContent = pname;
    line.appendChild(psp);

    const ann = p && p.annotation;
    if (ann !== null && ann !== undefined && String(ann).trim() !== "") {
      line.appendChild(document.createTextNode(": "));
      const asp = document.createElement("span");
      asp.className = "wtrl-type wtrl_type";
      asp.textContent = stripOuterQuotes(String(ann));
      line.appendChild(asp);
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
    const rsp = document.createElement("span");
    rsp.className = "wtrl-type wtrl_type";
    rsp.textContent = stripOuterQuotes(String(ret));
    tail.appendChild(rsp);
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
  if (section === "Preamble" && subsection === "normative_sections") return "wtrl-label wtrl_label";
  return "";
}

function appendMaybeStyledText(parent, txt, roleCls) {
  if (!roleCls) {
    appendInlineTokens(parent, txt);
    return;
  }
  const sp = document.createElement("span");
  sp.className = roleCls;
  appendInlineTokens(sp, txt);
  parent.appendChild(sp);
}

const FREEFORM_SECTIONS = new Set(["Description", "Definitions", "Terminology", "Returns", "Notes"]);

function isFreeformPath(path) {
  const section = String((path && path.length > 0) ? path[0] : "");
  return FREEFORM_SECTIONS.has(section);
}

function renderFreeformText(container, txt) {
  const lines = String(txt).split(/\r?\n/);
  const RE_BULLET = /^([*+\-#])\s(.*)$/;

  function flushParagraph(parts) {
    if (!parts || parts.length === 0) return;
    const p = document.createElement("p");
    p.className = "wtrl-text";
    appendInlineTokens(p, parts.join(" "));
    container.appendChild(p);
  }

  function genList(symbol) {
    const node = document.createElement(symbol === "#" ? "ol" : "ul");
    node.className = "wtrl-list";
    return node;
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

      const li = document.createElement("li");
      appendInlineTokens(li, text);
      nodeStack[nodeStack.length - 1].appendChild(li);
      lastItemStack[lastItemStack.length - 1] = li;
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

    let m = raw.match(RE_BULLET);
    if (m) {
      flushParagraph(paragraphParts);
      paragraphParts = [];

      const block = [];
      while (i < lines.length) {
        const mm = lines[i].match(RE_BULLET);
        if (!mm) break;
        block.push({ symbol: mm[1], text: mm[2] });
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

function renderCompactNormativeSections(container, items) {
  const vals = items.map(v => String(v));
  for (let i = 0; i < vals.length; i += 6) {
    const row = vals.slice(i, i + 6);
    const p = document.createElement("p");
    p.className = "wtrl-text";
    for (let j = 0; j < row.length; j += 1) {
      const sp = document.createElement("span");
      sp.className = "wtrl-label wtrl_label";
      sp.textContent = row[j];
      p.appendChild(sp);
      if (j < row.length - 1) p.appendChild(document.createTextNode(", "));
    }
    container.appendChild(p);
  }
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
  const anchor = srcQid ? TARGET_TO_ANCHOR.get(srcQid) : "";
  const terms = Array.isArray(obj.terms) ? obj.terms : [];

  const ul = document.createElement("ul");
  ul.className = "wtrl-list";
  for (const term of terms) {
    const li = document.createElement("li");
    if (anchor) {
      const a = document.createElement("a");
      a.className = "wtrl-ref wtrl_ref wtrl-dfn wtrl_dfn";
      a.href = "#" + anchor;
      a.textContent = String(term);
      li.appendChild(a);
    } else {
      const sp = document.createElement("span");
      sp.className = "wtrl-dfn wtrl_dfn";
      sp.textContent = String(term);
      li.appendChild(sp);
    }
    ul.appendChild(li);
  }
  container.appendChild(ul);
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
  const a = document.createElement("a");
  a.className = "wtrl-ref wtrl_ref wtrl-func wtrl_func";
  a.href = "#" + anchor;
  a.textContent = raw;
  parent.appendChild(a);
}

function appendInlineTokens(parent, txt) {
  let cur = 0;
  let m;
  TOK_RE.lastIndex = 0;
  while ((m = TOK_RE.exec(txt)) !== null) {
    if (m.index > cur) parent.appendChild(document.createTextNode(txt.slice(cur, m.index)));
    if (m[1]) {
      const s = document.createElement("span");
      s.className = "wtrl-norm wtrl_norm";
      s.textContent = m[1];
      parent.appendChild(s);
    } else if (m[2]) {
      const s = document.createElement("span");
      s.className = "wtrl-value wtrl_value";
      s.textContent = m[2];
      parent.appendChild(s);
    } else if (m[3]) {
      const role = m[4];
      const body = m[5];
      const cls = ROLE_CLASS[role];
      if (!cls) {
        parent.appendChild(document.createTextNode(m[3]));
      } else if (role === "ref") {
        const rb = parseRefBody(body);
        const a = document.createElement("a");
        a.className = cls;
        a.textContent = rb.label || body;
        if (rb.target.startsWith("http://") || rb.target.startsWith("https://")) {
          a.href = rb.target;
          a.target = "_blank";
          a.rel = "noopener noreferrer";
        } else if (rb.target.startsWith("wtrl://")) {
          const qid = rb.target.slice("wtrl://".length);
          const anchor = TARGET_TO_ANCHOR.get(qid);
          if (anchor) a.href = "#" + anchor;
        }
        if (!a.getAttribute("href")) {
          const sp = document.createElement("span");
          sp.className = cls;
          sp.textContent = m[3];
          parent.appendChild(sp);
        } else {
          parent.appendChild(a);
        }
      } else if (role === "lit" && (body === "None" || body === "Self" || body === "True" || body === "False")) {
        const s = document.createElement("span");
        s.className = "wtrl-value wtrl_value";
        s.textContent = body;
        parent.appendChild(s);
      } else {
        const s = document.createElement("span");
        s.className = cls;
        s.textContent = body;
        parent.appendChild(s);
      }
    }
    cur = TOK_RE.lastIndex;
  }
  if (cur < txt.length) parent.appendChild(document.createTextNode(txt.slice(cur)));
}

function renderValue(value, container, depth, path, currentQid) {
  const pth = Array.isArray(path) ? path : [];
  const leafRoleCls = getRoleClassForLeaf(pth);
  if (value === null || value === undefined) {
    const p = document.createElement("p");
    p.className = "wtrl-text";
    appendMaybeStyledText(p, "null", leafRoleCls);
    container.appendChild(p);
    return;
  }
  if (typeof value === "string") {
    if (isSeeAlsoPath(pth)) {
      const p = document.createElement("p");
      p.className = "wtrl-text";
      const vals = value.split(",").map(s => s.trim()).filter(Boolean);
      for (let i = 0; i < vals.length; i += 1) {
        appendSeeAlsoEntry(p, vals[i], currentQid);
        if (i < vals.length - 1) p.appendChild(document.createTextNode(", "));
      }
      container.appendChild(p);
      return;
    }
    if (isNormativeSectionsPath(pth)) {
      const vals = value.split(",").map(s => s.trim()).filter(Boolean);
      renderCompactNormativeSections(container, vals);
      return;
    }
    if (isFreeformPath(pth)) {
      renderFreeformText(container, value);
      return;
    }
    const p = document.createElement("p");
    p.className = "wtrl-text";
    appendMaybeStyledText(p, value, leafRoleCls);
    container.appendChild(p);
    return;
  }
  if (Array.isArray(value)) {
    if (isSeeAlsoPath(pth) && value.every(item => typeof item === "string")) {
      const ul = document.createElement("ul");
      ul.className = "wtrl-list";
      for (const item of value) {
        const li = document.createElement("li");
        appendSeeAlsoEntry(li, String(item), currentQid);
        ul.appendChild(li);
      }
      container.appendChild(ul);
      return;
    }
    if (isNormativeSectionsPath(pth) && value.every(item => typeof item === "string")) {
      renderCompactNormativeSections(container, value);
      return;
    }
    if (isFreeformPath(pth) && value.every(item => typeof item === "string")) {
      renderFreeformText(container, value.join("\n"));
      return;
    }
    const ul = document.createElement("ul");
    ul.className = "wtrl-list";
    for (const item of value) {
      const li = document.createElement("li");
      if (typeof item === "string") appendMaybeStyledText(li, item, leafRoleCls);
      else renderValue(item, li, depth + 1, pth, currentQid);
      ul.appendChild(li);
    }
    container.appendChild(ul);
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
        const block = document.createElement("div");
        block.className = "wtrl-subsection";

        const h = document.createElement("div");
        h.className = "wtrl-subsection-head";

        const spTerm = document.createElement("span");
        spTerm.className = "wtrl-dfn wtrl_dfn";
        spTerm.textContent = String(k);
        h.appendChild(spTerm);

        const vars = vv.variations.map(x => String(x)).filter(Boolean);
        if (vars.length > 0) {
          h.appendChild(document.createTextNode(" ["));
          const spVar = document.createElement("span");
          spVar.className = "wtrl-term wtrl_term";
          spVar.textContent = vars.join(", ");
          h.appendChild(spVar);
          h.appendChild(document.createTextNode("]"));
        }
        block.appendChild(h);

        renderFreeformText(block, vv.text.join("\n"));
        container.appendChild(block);
        continue;
      }

      const block = document.createElement("div");
      block.className = depth === 0 ? "wtrl-section" : "wtrl-subsection";
      const h = document.createElement("div");
      h.className = depth === 0 ? "wtrl-section-head" : "wtrl-subsection-head";
      if (depth === 0) {
        h.textContent = formatSectionHead(k);
      } else {
        if (k === "normative_sections") h.textContent = formatSectionHead(k);
        else h.textContent = k;
        const roleCls = getRoleClassForSubsectionHead(pth, k);
        if (roleCls) h.className += " " + roleCls;
      }
      block.appendChild(h);
      renderValue(v, block, depth + 1, pth.concat([k]), currentQid);
      container.appendChild(block);
    }
    return;
  }
  const p = document.createElement("p");
  p.className = "wtrl-text";
  appendMaybeStyledText(p, String(value), leafRoleCls);
  container.appendChild(p);
}

function renderHitList(entries) {
  const host = byId("wtrl-hitlist");
  host.innerHTML = "";
  for (const e of entries) {
    const btn = document.createElement("button");
    btn.className = "wtrl-hit";
    btn.type = "button";
    btn.innerHTML = `<span class="wtrl-kind">${e.kind}</span>${e.label}`;
    btn.addEventListener("click", () => selectTarget(e.target, true));
    host.appendChild(btn);
  }
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

function renderDocLines(node, targetQid, host) {
  const lines = Array.isArray(node.doc_lines) ? node.doc_lines : [];
  if (lines.length === 0) return false;

  const kind = inferDocLinesKind(targetQid);
  const sec = document.createElement("div");
  sec.className = "wtrl-section";

  const h = document.createElement("div");
  h.className = "wtrl-section-head";
  if (kind === "type") {
    h.textContent = "Type";
    h.className += " wtrl-type wtrl_type";
  } else if (kind === "variable") {
    h.textContent = "Variable";
    h.className += " wtrl-var wtrl_var";
  } else if (kind === "constant") {
    h.textContent = "Constant";
    h.className += " wtrl-var wtrl_var";
  } else {
    h.textContent = "Entry";
  }
  sec.appendChild(h);

  const ul = document.createElement("ul");
  ul.className = "wtrl-list";
  for (const line of lines) {
    const li = document.createElement("li");
    appendInlineTokens(li, String(line));
    ul.appendChild(li);
  }
  sec.appendChild(ul);
  host.appendChild(sec);
  return true;
}

function renderDoc(targetQid) {
  const objects = WTRL_DATA.objects || {};
  const examples = WTRL_DATA.examples || {};
  const node = objects[targetQid];
  byId("wtrl-title").textContent = targetQid || "(no selection)";
  if (!node) {
    byId("wtrl-sub").textContent = "No object found.";
    byId("wtrl-signature").innerHTML = "";
    byId("wtrl-doc").innerHTML = "";
    byId("wtrl-examples").innerHTML = "";
    byId("wtrl-obj").textContent = "";
    return;
  }
  byId("wtrl-sub").textContent = "Waterloo docstring";
  renderSignature(node, targetQid, byId("wtrl-signature"));
  const docHost = byId("wtrl-doc");
  docHost.innerHTML = "";
  const hasDocLines = renderDocLines(node, targetQid, docHost);
  if (node.doc && typeof node.doc === "object" && Object.keys(node.doc).length > 0) {
    renderValue(node.doc, docHost, 0, [], targetQid);
  } else if (!hasDocLines) {
    const p = document.createElement("p");
    p.className = "wtrl-text";
    p.textContent = "(no doc node)";
    docHost.appendChild(p);
  }
/*----- render examples --------------------------------------*/
  const exHost = byId("wtrl-examples");
// All example blocks are appended to this element.
  exHost.innerHTML = "";
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
    const sec = document.createElement("div");
    sec.className = "wtrl-section wtrl-examples";
// Render a headline
    const h = document.createElement("div");
    h.className = "wtrl-section-head";
    h.textContent = "Example";
    sec.appendChild(h);
// If we know the path to the example source file, render the path
    if (typeof exNode.path === "string" && exNode.path) {
      const head = document.createElement("div");
      head.className = "wtrl-example-head";
      const sp = document.createElement("span");
      sp.className = "wtrl-file wtrl_file";
      sp.textContent = exNode.path;
      head.appendChild(sp);
      sec.appendChild(head);
    }
// Finally render the code segment. The code is already HTML
// from pygments, so we use innerHTML to embed it here.
    const code = document.createElement("div");
    code.className = "wtrl-example-code";
    code.innerHTML = WTRL_EXAMPLES_HTML[exKey] || "<pre><code>(no code)</code></pre>";
// Append code segment to example section box.
    sec.appendChild(code);
// Done. Append to examples block.
    exHost.appendChild(sec);
  }
  byId("wtrl-obj").textContent = JSON.stringify(node, null, 2);
}

function selectTarget(targetQid, updateHash) {
  if (updateHash) {
    const hit = WTRL_INDEX.find(x => x.target === targetQid && x.anchor);
    if (hit && hit.anchor) {
      location.hash = hit.anchor;
    } else {
      location.hash = "";
    }
  }
  byId("wtrl-search").value = targetQid;
  renderDoc(targetQid);
}

function handleHashNavigation() {
  const h = (location.hash || "").replace(/^#/, "");
  if (!h) return false;
  const target = anchorMap.get(h);
  if (!target) return false;
  selectTarget(target, false);
  return true;
}

function setupSearch() {
  const inp = byId("wtrl-search");
  const clr = byId("wtrl-search-clear");
  const dl = byId("wtrl-search-list");
  for (const e of WTRL_INDEX) {
    const o = document.createElement("option");
    o.value = e.label;
    dl.appendChild(o);
  }
  inp.addEventListener("input", () => {
    const q = inp.value.trim().toLowerCase();
    if (!q) {
      renderHitList(WTRL_INDEX);
      return;
    }
    const hit = WTRL_INDEX.filter(e => e.label.toLowerCase().includes(q));
    renderHitList(hit);
    const exact = WTRL_INDEX.find(e => e.label === inp.value);
    if (exact) {
      selectTarget(exact.target, true);
    }
  });
  if (clr) {
    clr.addEventListener("click", () => {
      inp.value = "";
      renderHitList(WTRL_INDEX);
      inp.focus();
    });
  }
}

window.addEventListener("hashchange", () => { handleHashNavigation(); });
window.addEventListener("DOMContentLoaded", () => {
  byId("wtrl-scope").textContent = String((WTRL_DATA.meta || {}).scope || "");
  byId("wtrl-flavour").textContent = String((WTRL_DATA.meta || {}).flavour || "");
  byId("wtrl-modules").textContent = ((WTRL_DATA.meta || {}).modules || []).join(", ");
  byId("wtrl-num-classes").textContent = String(Object.keys(WTRL_DATA.toc_classes || {}).length);
  byId("wtrl-num-callables").textContent = String(Object.keys(WTRL_DATA.toc_callables || {}).length);
  setupSearch();
  renderHitList(WTRL_INDEX);
  if (!handleHashNavigation()) {
    const first = WTRL_INDEX.find(e => e.kind === "mod") || WTRL_INDEX[0];
    if (first) selectTarget(first.target, true);
  }
});
