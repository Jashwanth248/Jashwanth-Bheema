async function start() {
  const cases = await fetch('/api/cases').then(r => r.json());
  document.querySelector('#cases').innerHTML = cases.map(c => `<label><strong>${c.category}</strong><br>${c.question}<textarea data-case="${c.id}" required placeholder="Write the AI answer to test"></textarea><small>Ideal answer: ${c.expected_answer}</small></label>`).join('');
  document.querySelector('#run-form').addEventListener('submit', async event => {
    event.preventDefault();
    const answers = Object.fromEntries([...document.querySelectorAll('textarea')].map(x => [x.dataset.case, x.value]));
    const response = await fetch('/api/runs', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({prompt_version: document.querySelector('#version').value, answers})});
    const run = await response.json();
    document.querySelector('#output').textContent = `Release score: ${Math.round(run.score * 100)}% (${run.passed}/${run.total} passed)\n` + run.results.map(x => `${x.case_id}: ${x.passed ? 'PASS' : 'NEEDS REVIEW'} — ${x.reasons.join(', ')}`).join('\n');
    setTimeout(() => location.reload(), 1200);
  });
}
start();
