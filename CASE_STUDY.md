# Case study: a reviewable AI-assisted month-end close

**Author:** Karim Lameer — CIMA-qualified accountant.
**Scope:** a reference workflow using a fictional UK distributor and a mock
ERP. This repository does not establish production use by a finance team.

## The finance problem

A close is a sequence of dependent work: reconcile the bank, explain
variances, build the management pack, and retain the evidence. An assistant
needs to do more than produce plausible commentary. The figures must tie,
exceptions need decisions, and the reviewer must see the work they approve.

## My contribution

I built a fictional document estate and mock ERP, Python calculation and
checking scripts, four workflow skills, reviewer instructions and a
handover runbook. Claude coordinates the workflow; the bundled scripts
perform the calculations. The source is MIT licensed.

```mermaid
flowchart LR
    A[ERP and source documents] --> B[Bank reconciliation]
    B --> C[Reviewer gate]
    C --> D[Variance report]
    D --> E[Reviewer gate]
    E --> F[Management pack]
    F --> G[Reviewer gate]
    G --> H[Close log and binder]
```

## Decisions and trade-offs

| Decision | Purpose | Boundary |
| --- | --- | --- |
| Calculate in Python | Reproduce arithmetic and check ties independently of the model. | Correct code still needs correct, complete inputs. |
| Stop for a reviewer between steps | Put accounting judgments and approval with a named person. | The reference kit's gates are workflow instructions; it is not an independently enforced authorisation service. |
| Record file hashes with sign-offs | Preserve a reference to the approved result bytes. | A hash is not reviewer authentication or tamper-proof storage. The binder renderer prints stored hashes; it does not itself rehash every supplied result. |
| Ship fictional data and a mock ERP | Let a reviewer inspect the workflow without client access. | A real ERP integration, access model and operating controls need separate design and validation. |

## Inspect the implementation in five minutes

1. Read the [finance-team runbook](handover/RUNBOOK.md) to see the reviewer experience.
2. Inspect [bank reconciliation](skills/close-pack/bank-rec/scripts/reconcile.py)
   and its [checks](skills/close-pack/bank-rec/scripts/checks.py).
3. Inspect [variance calculation](skills/close-pack/variance-report/scripts/variance.py)
   and the [pack builder](skills/close-pack/pack-build/scripts/build_pack.py).
4. Follow a result into the [audit record](skills/close-pack/bank-rec/scripts/audit_record.py)
   and [binder renderer](skills/close-pack/close-checklist/scripts/binder.py).
5. Read the [six known-answer checks](skills/close-pack/close-checklist/scripts/run_goldens.py)
   and the [API tests](erp-api/tests/test_api.py).

## Run and review

The [setup guide](WIRING.md) connects the skills, document estate and mock
ERP. The API tests can be run separately, with no model calls:

```bash
python -m pip install -r erp-api/requirements.txt pytest httpx
python -m pytest erp-api/tests -q
```

The golden runner requires the step inputs gathered during a close; it is
not a standalone test against an empty folder. Its usage is documented in
[the runner](skills/close-pack/close-checklist/scripts/run_goldens.py).

## What this demonstrates

Finance workflow decomposition, deterministic calculations, explicit
exceptions, a reviewer handover and reproducible checks. The fictional
example is evidence of the design and implementation, not a claim of
measured close-time savings, regulatory certification or production approval.

Before using this pattern in production I would verify approval-state
enforcement, reviewer identity, hash verification at consumption, protected
evidence retention, ERP access, reruns and recovery from a partial close.
Those are concrete implementation requirements, not features this kit has
already demonstrated.

## Interview walkthrough

Explain one reconciliation exception, show the arithmetic and check that
catches it, trace the human decision into the record, and identify the
additional controls required for a real finance team.
