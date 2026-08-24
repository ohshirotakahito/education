const expressionEl = document.querySelector('#expression');
const resultEl = document.querySelector('#result');
const historyList = document.querySelector('#history-list');
const emptyHistory = document.querySelector('#empty-history');
const memoryIndicator = document.querySelector('#memory-indicator');
let expression = '';
let memory = 0;
let angleMode = 'DEG';

function render() { expressionEl.textContent = expression || '0'; }
function formatNumber(value) { if (!Number.isFinite(value)) throw new Error('計算できません'); return Number(value.toPrecision(12)).toString(); }
function calculate(source) {
  let formula = source.replaceAll('×', '*').replaceAll('÷', '/').replaceAll('−', '-').replaceAll('π', 'PI').replaceAll('^', '**').replace(/(\d|\))(?=(PI|e|sin|cos|tan|log|ln|sqrt|asin|acos|atan|sinh|cosh|tanh|abs|exp|floor|ceil|inv|fact|\())/g, '$1*');
  formula = formula.replace(/(PI|e|\))(?=\d)/g, '$1*');
  const radians = value => angleMode === 'DEG' ? value * Math.PI / 180 : value;
  const fromRadians = value => angleMode === 'DEG' ? value * 180 / Math.PI : value;
  const factorial = value => { if (!Number.isInteger(value) || value < 0 || value > 170) throw new Error('階乗は0以上170以下の整数のみ'); let result = 1; for (let index = 2; index <= value; index += 1) result *= index; return result; };
  const scope = { PI: Math.PI, e: Math.E, sin: value => Math.sin(radians(value)), cos: value => Math.cos(radians(value)), tan: value => Math.tan(radians(value)), asin: value => fromRadians(Math.asin(value)), acos: value => fromRadians(Math.acos(value)), atan: value => fromRadians(Math.atan(value)), sinh: Math.sinh, cosh: Math.cosh, tanh: Math.tanh, abs: Math.abs, exp: Math.exp, floor: Math.floor, ceil: Math.ceil, inv: value => 1 / value, fact: factorial, log: Math.log10, ln: Math.log, sqrt: Math.sqrt };
  if (!/^[0-9+\-*/%.(),\sA-Za-z_*]+$/.test(formula)) throw new Error('入力を確認してください');
  const value = Function(...Object.keys(scope), `"use strict"; return (${formula})`)(...Object.values(scope));
  return formatNumber(value);
}
function showResult() {
  if (!expression) return;
  try { const value = calculate(expression); resultEl.textContent = value; addHistory(expression, value); }
  catch (error) { resultEl.textContent = 'Error'; }
}
function addHistory(source, value) { emptyHistory.hidden = true; const item = document.createElement('div'); item.className = 'history-item'; item.innerHTML = `<div class="history-expression">${source}</div><div class="history-result">= ${value}</div>`; item.addEventListener('click', () => { expression = source; resultEl.textContent = value; render(); }); historyList.prepend(item); }
function insert(value) { expression += value; render(); }
function clear() { expression = ''; resultEl.textContent = '0'; render(); }
function updateMemory() { memoryIndicator.textContent = `M: ${formatNumber(memory)}`; }

document.querySelectorAll('[data-value]').forEach(button => button.addEventListener('click', () => insert(button.dataset.value)));
document.querySelector('[data-action="clear"]').addEventListener('click', clear);
document.querySelector('[data-action="backspace"]').addEventListener('click', () => { expression = expression.slice(0, -1); render(); });
document.querySelector('[data-action="calculate"]').addEventListener('click', showResult);
document.querySelector('[data-action="angle"]').addEventListener('click', event => { angleMode = angleMode === 'DEG' ? 'RAD' : 'DEG'; event.target.textContent = angleMode; document.querySelector('#angle-mode-label').textContent = angleMode; });
document.querySelector('[data-action="memory-clear"]').addEventListener('click', () => { memory = 0; updateMemory(); });
document.querySelector('[data-action="memory-recall"]').addEventListener('click', () => insert(formatNumber(memory)));
document.querySelector('[data-action="memory-add"]').addEventListener('click', () => { try { memory += Number(calculate(expression)); updateMemory(); } catch {} });
document.querySelector('[data-action="memory-subtract"]').addEventListener('click', () => { try { memory -= Number(calculate(expression)); updateMemory(); } catch {} });
document.querySelector('#clear-history').addEventListener('click', () => { historyList.querySelectorAll('.history-item').forEach(item => item.remove()); emptyHistory.hidden = false; });
document.addEventListener('keydown', event => { const keyMap = { '*': '×', '/': '÷', '-': '−' }; if (/^[0-9().+%]$/.test(event.key) || keyMap[event.key]) { insert(keyMap[event.key] || event.key); } else if (event.key === 'Enter' || event.key === '=') { showResult(); } else if (event.key === 'Backspace') { expression = expression.slice(0, -1); render(); } else if (event.key === 'Escape') clear(); });