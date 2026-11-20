const fs = require('node:fs');
const vm = require('node:vm');
const assert = require('node:assert/strict');

const [beforePath, afterPath, mode] = process.argv.slice(2);
if (!beforePath || !afterPath || !['legacy', 'jquery'].includes(mode)) {
  throw new Error('usage: node locale_dom_context.cjs BEFORE.js AFTER.js legacy|jquery');
}
const translations = {
  'Re-run Setup': 'Executar a configuração novamente',
  'Default Authentication Server': 'Servidor de autenticação padrão',
  'Role Management': 'Gerenciamento de funções',
  'Settings': 'Configurações',
  'Search...': 'Pesquisar...'
};

function textNode(text) {
  return { nodeType: 3, textContent: text, parentElement: null };
}
function element(tag, children = [], attributes = {}) {
  const node = {
    nodeType: 1,
    tagName: tag.toUpperCase(),
    childNodes: children,
    attributes: { ...attributes },
    hasAttribute(name) { return Object.hasOwn(this.attributes, name); },
    getAttribute(name) { return this.attributes[name] ?? null; },
    setAttribute(name, value) { this.attributes[name] = String(value); },
    toString() { return `[object HTML${tag[0].toUpperCase()}${tag.slice(1)}Element]`; }
  };
  for (const child of children) child.parentElement = node;
  return node;
}
class JQuerySet {
  constructor(nodes, previous = null) { this.nodes = nodes; this.previous = previous; this.jquery = 'test-jquery'; }
  find(selector) {
    assert.equal(selector, '*');
    const result = [];
    const visit = node => {
      for (const child of node.childNodes || []) {
        if (child.nodeType === 1) { result.push(child); visit(child); }
      }
    };
    for (const node of this.nodes) visit(node);
    return new JQuerySet(result, this);
  }
  addBack() {
    const prior = this.previous ? this.previous.nodes : [];
    return new JQuerySet([...new Set([...prior, ...this.nodes])]);
  }
  each(callback) { this.nodes.forEach((node, index) => callback.call(node, index, node)); return this; }
  contents() { return new JQuerySet(this.nodes.flatMap(node => node.childNodes || [])); }
  filter(callback) { return new JQuerySet(this.nodes.filter((node, index) => callback(index, node))); }
}
function createRuntime(source) {
  const root = element('div', [
    textNode('  Re-run Setup  '),
    element('span', [textNode('Default Authentication Server')]),
    element('script', [textNode('Role Management')]),
    element('style', [textNode('Settings')])
  ], { title: 'Re-run Setup', placeholder: 'Search...' });
  root.id = 'roleRoot';
  const body = element('body', [root]);
  const $ = value => {
    if (typeof value === 'string') {
      if (value === 'body') return new JQuerySet([body]);
      if (value === '#roleRoot') return new JQuerySet([root]);
      throw new Error(`Syntax error, unrecognized expression: ${value}`);
    }
    if (value && value.jquery) return value;
    if (value && value.nodeType === 1) return new JQuerySet([value]);
    throw new Error(`unsupported jQuery input: ${String(value)}`);
  };
  let observer;
  class MockMutationObserver {
    constructor(callback) { this.callback = callback; observer = this; }
    observe(target, options) { this.target = target; this.options = options; }
  }
  const context = vm.createContext({
    $, Node: { TEXT_NODE: 3, ELEMENT_NODE: 1 }, MutationObserver: MockMutationObserver,
    document: { readyState: 'complete', body, addEventListener() {} },
    console: { log() {} }, localStorage: {}, fetch: async () => ({ json: async () => ({}) })
  });
  vm.runInContext('String.prototype.contains = function (value) { return this.indexOf(value) !== -1; }', context);
  vm.runInContext(`${source}\n;globalThis.__localeForTest = Locale;`, context);
  return { locale: context.__localeForTest, root, body, get observer() { return observer; } };
}

async function check(source, expectedOldFailure) {
  const runtime = createRuntime(source);
  await runtime.locale.LoadLocale('pt');
  if (expectedOldFailure) {
    assert.throws(
      () => runtime.locale.ApplyLocale(runtime.root),
      /Syntax error, unrecognized expression: \[object HTMLDivElement\] \*/
    );
    const added = element('section', [textNode('Re-run Setup')]);
    runtime.body.childNodes.push(added);
    added.parentElement = runtime.body;
    assert.throws(
      () => runtime.observer.callback([{ type: 'childList', addedNodes: [added] }]),
      /Syntax error, unrecognized expression: \[object HTMLSectionElement\] \*/
    );
    return;
  }

  assert.doesNotThrow(() => runtime.locale.ApplyLocale(runtime.root));
  assert.equal(runtime.root.childNodes[0].textContent, '  Executar a configuração novamente  ');
  assert.equal(runtime.root.childNodes[1].childNodes[0].textContent, 'Servidor de autenticação padrão');
  assert.equal(runtime.root.childNodes[2].childNodes[0].textContent, mode === 'jquery' ? 'Role Management' : 'Gerenciamento de funções');
  assert.equal(runtime.root.childNodes[3].childNodes[0].textContent, mode === 'jquery' ? 'Settings' : 'Configurações');
  assert.equal(runtime.root.attributes.title, mode === 'jquery' ? 'Executar a configuração novamente' : 'Re-run Setup');
  assert.equal(runtime.root.attributes.placeholder, mode === 'jquery' ? 'Pesquisar...' : 'Search...');

  const added = element('section', [textNode('Re-run Setup')]);
  runtime.body.childNodes.push(added);
  added.parentElement = runtime.body;
  assert.doesNotThrow(() => runtime.observer.callback([{ type: 'childList', addedNodes: [added] }]));
  assert.equal(added.childNodes[0].textContent, 'Executar a configuração novamente');
  assert.doesNotThrow(() => runtime.locale.ApplyLocale('#roleRoot'));
  assert.doesNotThrow(() => runtime.locale.ApplyLocale());
}

(async () => {
  const before = fs.readFileSync(beforePath, 'utf8');
  const after = fs.readFileSync(afterPath, 'utf8');
  if (mode === 'legacy') await check(before, true);
  else await check(before, false);
  await check(after, false);
  process.stdout.write(`DOM context checks passed (${mode}).\n`);
})().catch(error => { console.error(error); process.exitCode = 1; });
