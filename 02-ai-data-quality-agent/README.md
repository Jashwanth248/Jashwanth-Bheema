# AI Data Quality Investigator

An evidence-first AI-agent pattern for data incidents. Rather than allowing a model to make untraceable claims, the agent retrieves known run evidence, applies deterministic playbooks, and returns an auditable recommendation.

## Agent workflow

1. Receive a failed quality rule and run metrics.
2. Retrieve a matching remediation playbook.
3. Produce a concise, bounded recommendation with evidence IDs.
4. Require human approval for any data-changing action.

This demo contains no external LLM dependency. The `build_prompt` function provides a safe, structured context boundary for connecting an approved LLM provider later, while `investigate` is deterministic and fully testable.

## Run

```bash
python src/agent.py --incident data/incident.json
```

## Guardrails

* No data mutation or credential handling.
* Every conclusion cites source evidence.
* Recommendations use `requires_human_approval: true`.
* Unknown rules are escalated, never guessed.
