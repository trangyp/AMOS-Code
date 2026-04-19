---
description: Deterministic repository review template with formal invariants and verification criteria
---

# DETERMINISTIC REPO REVIEW TEMPLATE

## Header

```
REVIEW ID:
REPOSITORY:
BRANCH / COMMIT:
SCOPE:
REVIEWER / AGENT:
DATE:
GOAL:
CONSTRAINTS:
COMPLETION CRITERIA:
```

---

## 0. TERMINAL RULE

A task may be marked DONE only if all are true:

```
Done = Changed ∧ Reachable ∧ Verified ∧ StateAligned ∧ ReportAligned
```

Definitions:
- **Changed** = relevant artifact actually changed
- **Reachable** = behavior exists on real runtime path
- **Verified** = relevant verifier passed
- **StateAligned** = actual repo/runtime state matches target
- **ReportAligned** = final report says only what evidence supports

Terminal state:
- [ ] VALID
- [ ] BOUNDED
- [ ] INVALID

**VALID:**
- all critical invariants pass

**BOUNDED:**
- all critical invariants pass
- some non-critical items remain unverified
- residual risk explicitly listed

**INVALID:**
- any critical invariant fails
- or any critical invariant remains unverified

---

## 1. GOAL GROUNDING

### 1.1 Target truth
What exact state must become true?

### 1.2 Scope
Which files, commands, routes, handlers, docs, launchers, servers, tests, or configs are in scope?

### 1.3 Constraints
What must not be broken?

### 1.4 Completion criteria
What exact evidence will count as completion?

Checklist:
- [ ] Goal is explicit
- [ ] Scope is explicit
- [ ] Constraints are explicit
- [ ] Completion criteria are measurable

Failure class if not:
- vague goal
- narrative completion risk

---

## 2. FILE DISCOVERY

For each discovered file, record:

| Field | Description |
|-------|-------------|
| path | Absolute or relative path |
| kind | source \| config \| docs \| test \| script \| workflow \| asset \| generated \| vendor |
| language | Programming language |
| user-facing | yes/no |
| execution-facing | yes/no |
| state-facing | yes/no |
| verification-facing | yes/no |

Required surfaces:
- [ ] source files
- [ ] config/build files
- [ ] entrypoints
- [ ] scripts
- [ ] docs/guides/tutorials
- [ ] tests
- [ ] runtime wrappers
- [ ] subprocess targets
- [ ] persistence paths
- [ ] status outputs

Invariant:
```
DocumentedPath -> FileExists
```

Failure class:
- phantom entrypoint
- phantom guide target
- missing runtime surface

---

## 3. FILE TRUTH RECORD

Create one record per relevant file.

```
FILE:
PATH:
KIND:
LANGUAGE:
PARSE STATE: parsed | recoverable | failed

DEFINITIONS:
- functions:
- classes:
- methods:
- commands:
- handlers:
- entrypoints:
- env readers:
- status producers:
- persistence loaders/savers:
- verifier functions:

REFERENCES:
- imports:
- exports used:
- files referenced:
- commands referenced:
- fields accessed:
- methods called:
- subprocess targets:
- env vars referenced:

CLAIMS:
- capability claims:
- status claims:
- workflow claims:
- persistence claims:
- verification claims:

ENTRYPOINTS:
- main:
- parser registration:
- slash command registration:
- package console scripts:
- subprocess launch targets:

STATE SURFACES:
- status outputs:
- mode flags:
- retry logic:
- persistence logic:
- replay logic:

VERIFICATION SURFACES:
- tests:
- parse checks:
- import checks:
- runtime checks:
- contract checks:
- persistence checks:
```

Checklist:
- [ ] Definitions extracted
- [ ] References extracted
- [ ] Claims extracted
- [ ] Entrypoints extracted
- [ ] Status surfaces extracted
- [ ] Verification surfaces extracted

Failure class:
- incomplete parse substrate
- invisible claim path
- invisible state path

---

## 4. GLOBAL INDEX

Build and maintain these index maps.

### SYMBOL INDEX
```
symbol:
defined_in:
used_in:
exported_by:
imported_by:
state: valid | missing | stale
```

### COMMAND INDEX
```
command:
registered_in:
handler:
reachable_from:
documented_in:
help_registered:
autocomplete_registered:
state: valid | missing | stale
```

### CAPABILITY INDEX
```
capability:
claimed_by:
implemented_by:
reachable_via:
verified_by:
state: valid | open | broken | unverified | degraded
```

### CONTRACT INDEX
```
callable:
defined_signature:
call_sites:
observed_signatures:
return_shape:
state: matched | broken | unknown
```

### STATUS INDEX
```
status_claim:
produced_by:
actual_source_of_truth:
state: honest | misleading | false
```

### PERSISTENCE INDEX
```
object:
save_path:
load_path:
list_path:
replay_path:
state: valid | broken | fake
```

### DELEGATION INDEX
```
wrapper:
handoff:
child_consumer:
reverification_path:
state: valid | broken | unknown
```

Checklist:
- [ ] Every claim linked to implementation or defect
- [ ] Every command linked to registration and handler
- [ ] Every status claim linked to actual state source
- [ ] Every persistence claim linked to save and load path
- [ ] Every wrapper handoff linked to child consumer

Failure class:
- phantom capability
- phantom status
- phantom persistence
- phantom handoff

---

## 5. INVARIANT EVALUATION

Use pass/fail/unknown for each invariant.

Legend:
- **PASS** = 1
- **FAIL** = 0
- **UNKNOWN** = ?

---

### 5A. PARSE INVARIANTS

#### P1. Executable file must parse or be structurally recoverable
- Result:
- Evidence:
- Affected files:

#### P2. Parsed file must expose definitions, references, and claims
- Result:
- Evidence:
- Affected files:

---

### 5B. RESOLUTION INVARIANTS

#### R1. Referenced symbol must exist
```
Expression: Referenced(symbol) -> Defined(symbol)
```
- Result:
- Evidence:
- Affected files:

#### R2. Referenced file/path/module must exist
- Result:
- Evidence:
- Affected files:

#### R3. Referenced command must be registered
- Result:
- Evidence:
- Affected files:

Failure class:
- phantom dependency
- phantom module
- phantom command

---

### 5C. CONTRACT INVARIANTS

#### C1. Call signatures must match actual definitions
```
Expression: Called(fn,args) -> SignatureMatches(fn,args)
```
- Result:
- Evidence:
- Affected files:

#### C2. Return-field accesses must match real return shape
- Result:
- Evidence:
- Affected files:

#### C3. Imported/exported public names must match package surface
- Result:
- Evidence:
- Affected files:

#### C4. Demo/test/doc examples must be valid calls
- Result:
- Evidence:
- Affected files:

Failure class:
- phantom interface
- stale contract
- test drift
- demo drift

---

### 5D. CAPABILITY INVARIANTS

#### K1. Documented capability must be implemented and reachable
```
Expression: Documented(cap) -> Implemented(cap) ∧ Reachable(cap)
```
- Result:
- Evidence:
- Affected files:

#### K2. Launcher-promoted capability must exist in runtime
- Result:
- Evidence:
- Affected files:

#### K3. Status-promoted capability must be real
- Result:
- Evidence:
- Affected files:

#### K4. Tutorial/guide command must exist on taught interface
- Result:
- Evidence:
- Affected files:

Failure class:
- phantom capability
- phantom docs
- phantom tutorial
- phantom launcher

---

### 5E. STATE INVARIANTS

#### S1. Reported ready/initialized/loaded/active must equal actual state
```
Expression: ReportedState = ActualState
```
- Result:
- Evidence:
- Affected files:

#### S2. Retry claims must correspond to real re-entry logic
- Result:
- Evidence:
- Affected files:

#### S3. Enable flag or mode handoff must be consumed by runtime
- Result:
- Evidence:
- Affected files:

#### S4. Listed session/state must be loadable or replayable
- Result:
- Evidence:
- Affected files:

Failure class:
- phantom readiness
- phantom retry
- phantom replay
- phantom state transition

---

### 5F. PERSISTENCE INVARIANTS

#### PP1. Saved object must survive reload with equivalent meaning
```
Expression: Save(x) -> Reload(x) -> Equivalent(x)
```
- Result:
- Evidence:
- Affected files:

#### PP2. Claimed persistent backend must equal actual backend
- Result:
- Evidence:
- Affected files:

#### PP3. Listed session/history must be replayable/readable
- Result:
- Evidence:
- Affected files:

Failure class:
- phantom persistence
- phantom backend
- phantom replay

---

### 5G. VERIFICATION INVARIANTS

#### V1. Every success claim must have a real verifier
```
Expression: ClaimedFixed -> Exists(relevant verifier)
```
- Result:
- Evidence:
- Affected files:

#### V2. Verifier must match claim type
Examples:
- parse check for syntax
- import check for symbol resolution
- runtime path check for command reachability
- persistence reload check for storage claims
- Result:
- Evidence:
- Affected files:

#### V3. All critical claims must be covered by verification
- Result:
- Evidence:
- Affected files:

#### V4. No success claim may be based only on absence of visible error
- Result:
- Evidence:
- Affected files:

Failure class:
- phantom verification
- misbound verification
- partial verification masquerade
- phantom success

---

### 5H. DELEGATION INVARIANTS

#### D1. Parent must re-verify child result
- Result:
- Evidence:
- Affected files:

#### D2. Wrapper/parent handoff must be consumed by child runtime
- Result:
- Evidence:
- Affected files:

#### D3. False child success must not auto-propagate to parent completion
- Result:
- Evidence:
- Affected files:

Failure class:
- phantom delegation
- phantom handoff
- hallucination cascade

---

### 5I. REPORTING INVARIANTS

#### O1. Every material report claim must be traceable to evidence
```
Expression: ReportClaim -> Evidence
```
- Result:
- Evidence:
- Affected files:

#### O2. Reported done must imply goal satisfied
- Result:
- Evidence:
- Affected files:

#### O3. Status/help/docs/guide text must not exceed implemented reality
- Result:
- Evidence:
- Affected files:

#### O4. Residual unverified claims must be explicitly bounded
- Result:
- Evidence:
- Affected files:

Failure class:
- phantom report
- phantom completion
- hidden residual risk

---

## 6. DEFECT REGISTER

For every defect, create a record.

```
DEFECT ID:
TITLE:
CLASS:
  - parse_defect
  - resolution_defect
  - contract_defect
  - capability_defect
  - wiring_defect
  - state_defect
  - persistence_defect
  - verification_defect
  - delegation_defect
  - reporting_defect

VIOLATED INVARIANT:
SEVERITY:
  - critical
  - high
  - medium
  - low

EVIDENCE:
  - file:
  - line or object:
  - observed state:
  - expected state:

AFFECTED SURFACES:
  - source:
  - config:
  - docs:
  - tests:
  - launcher:
  - runtime:
  - persistence:
  - status/help:

ROOT CAUSE:
TARGET FILES:
MINIMAL PATCH SET:
STATE:
  - open
  - localized
  - patched
  - verified
  - closed
  - bounded
  - invalid
```

---

## 7. REPAIR PLAN

For each defect:

```
REPAIR ID:
DEFECT ID:
PATCH TARGETS:
PATCH INTENT:
EXPECTED STATE CHANGE:
WHAT MUST BECOME TRUE:
WHAT MUST REMAIN TRUE:
RISK OF REGRESSION:
REQUIRED VERIFIERS:
CLOSURE CONDITION:
```

Checklist:
- [ ] Patch targets are minimal
- [ ] Patch is on real execution path
- [ ] Patch closes the exact violated invariant
- [ ] Patch does not rely on narrative success

---

## 8. PATCH LOG

```
PATCH ID:
FILES CHANGED:
OBJECTS CHANGED:
CHANGE TYPE:
  - add
  - delete
  - rename
  - rewire
  - contract fix
  - status fix
  - docs alignment
  - persistence fix
  - verifier fix

REASON:
LINKED DEFECTS:
LINKED INVARIANTS:
OBSERVED DIFF SUMMARY:
```

---

## 9. VERIFICATION RECORD

For each repair, record relevant verifiers only.

```
VERIFIER ID:
TYPE:
  - parse_check
  - resolution_check
  - signature_check
  - entrypoint_check
  - reachability_check
  - state_transition_check
  - persistence_reload_check
  - report_alignment_check
  - runtime_behavior_check

TARGET:
METHOD:
RESULT:
  - pass
  - fail
  - unknown

EVIDENCE:
SCOPE COVERED:
LIMITATIONS:
```

Critical rule:
A repair is not verified unless the verifier matches the claim type.

---

## 10. CLOSURE RECORD

For each defect:

```
DEFECT ID:
PATCHED: yes/no
RELEVANT VERIFIER PASSED: yes/no
STATE ALIGNED: yes/no
REPORT ALIGNED: yes/no
CLOSURE STATE:
  - closed
  - bounded
  - invalid
```

Closure law:
```
Closed = patched ∧ verified ∧ state_aligned ∧ report_aligned
```

---

## 11. CRITICAL GATE

A repo review may only claim completion if all critical gates pass.

Critical gates:
- [ ] Parse-critical files pass
- [ ] All critical references resolve
- [ ] All critical contracts match
- [ ] All user-facing promised capabilities are real
- [ ] All status/readiness claims are honest
- [ ] All target persistence/replay claims are real
- [ ] All target fixes have relevant verification
- [ ] Final report aligns with evidence

If any box is false or unknown:
```
Completion state = INVALID or BOUNDED, never VALID
```

---

## 12. FINAL REVIEW SUMMARY

```
GOAL:
FILES REVIEWED:
CRITICAL DEFECTS FOUND:
CRITICAL DEFECTS CLOSED:
NON-CRITICAL DEFECTS CLOSED:
OPEN DEFECTS:
BOUNDED RISKS:

VERIFIED CLAIMS:
- claim:
  - verifier:
  - evidence:

UNVERIFIED CLAIMS:
- claim:
  - reason unverified:
  - risk:

DO NOT CLAIM:
- unsupported capability
- unsupported verification
- unsupported readiness
- unsupported completion
```

FINAL STATE:
- [ ] VALID
- [ ] BOUNDED
- [ ] INVALID

FINAL JUSTIFICATION:
- why this state is correct
- what evidence supports it
- what remains outside proof

---

## 13. COMPACT PASS/FAIL LAW

```
RealCode = Parse ∧ Resolve ∧ MatchContract ∧ RuntimeFit ∧ ReachableBehavior

Hallucination = Claimed ∧ NotSupportedByEvidence

RealFix = PatchExists ∧ ClosesInvariant ∧ RelevantVerifierPasses ∧ ReportAligned

Done = Changed ∧ Reachable ∧ Verified ∧ StateAligned ∧ ReportAligned
```

**No task may be marked done if any critical invariant is FAIL or UNKNOWN.**

---

## Appendix: One-Row Format for Line-by-Line Audits

A tighter variant for line-by-line repo audits:

```
object | kind | claim/ref | invariant | observed | required | defect class | target files | verifier | state
```

Example:
```
/dashboard | command | documented in guide | documented -> implemented -> reachable | guide yes, shell no | shell command + handler + help | capability_defect | clawspring.py, guide.md | reachability_check | open
```

---

## Appendix: CSV Header Set

```csv
object,kind,claim_ref,invariant,observed,required,defect_class,target_files,verifier,state
```

---

## Appendix: JSON Schema

```json
{
  "review": {
    "id": "string",
    "repository": "string",
    "branch": "string",
    "scope": "string",
    "reviewer": "string",
    "date": "string",
    "goal": "string",
    "constraints": "string",
    "completion_criteria": "string"
  },
  "invariants": {
    "parse": [{ "id": "P1", "result": "pass|fail|unknown", "evidence": "..." }],
    "resolution": [{ "id": "R1", "result": "pass|fail|unknown", "evidence": "..." }],
    "contract": [{ "id": "C1", "result": "pass|fail|unknown", "evidence": "..." }],
    "capability": [{ "id": "K1", "result": "pass|fail|unknown", "evidence": "..." }],
    "state": [{ "id": "S1", "result": "pass|fail|unknown", "evidence": "..." }],
    "persistence": [{ "id": "PP1", "result": "pass|fail|unknown", "evidence": "..." }],
    "verification": [{ "id": "V1", "result": "pass|fail|unknown", "evidence": "..." }],
    "delegation": [{ "id": "D1", "result": "pass|fail|unknown", "evidence": "..." }],
    "reporting": [{ "id": "O1", "result": "pass|fail|unknown", "evidence": "..." }]
  },
  "defects": [{
    "id": "string",
    "title": "string",
    "class": "parse_defect|resolution_defect|contract_defect|...",
    "violated_invariant": "string",
    "severity": "critical|high|medium|low",
    "evidence": { "file": "...", "line": "...", "observed": "...", "expected": "..." },
    "state": "open|localized|patched|verified|closed|bounded|invalid"
  }],
  "final_state": "VALID|BOUNDED|INVALID"
}
```
