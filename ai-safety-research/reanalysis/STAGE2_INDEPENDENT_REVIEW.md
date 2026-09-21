# Independent Stage 2 implementation review

September 21, 2026. **No remaining implementation blocker for the bounded diagnostic after Git freeze.** No released Stage 2 component counts or review-example selection were calculated during this review.

## Checks performed

- Read the prospective protocol and focused literature decision. The fixed model-specific Stage 1 baseline-correct cohorts, K/A/O/U definitions, partition identity, archived WrongFlip numerator closure and finite-corpus interpretation are coherent. No novelty, causal effect or population-prevalence inference follows from this decomposition.
- Independently ran **all 16 synthetic unit tests: passed**. Coverage includes partition/denominator checks, unchanged final parsing despite different first_text, population/order preservation, invalid-input rejection, exact selection/display rules with forced hash ties, empty strata, packet field masking, blank human annotations, literal Markdown handling, dependency/output tampering and failure/no-overwrite behavior.
- Independently checked **all 60 possible valid gold × different suggested choice × final parse combinations** and **60 corresponding contradictory-correctness rejection cases**. All passed. This exhaustive classification check used synthetic records only.
- Exercised the real Stage 1 integrity-verification path without invoking Stage 2 classification or sampling: pinned provenance and five recorded output hashes passed. The imported Stage 1 adapter matches its recorded SHA-256 and original frozen commit `b4e0a27cd9d1575e572f1184c513eade2bb8bd0a` byte for byte.

## Implementation and interpretation

The adapter binds the reviewed Stage 2 source/tests/protocol and unchanged Stage 1 dependency to Git. Source logs and question data are rechecked against the pinned release tree and Stage 1 identities. It preserves ordered trial identities and uses stored final parses, with no retry-first-text substitution. K+A+O+U must equal the archived baseline-correct count; A+O+U must equal the archived wrong-suggestion error numerator. Undefined fractions remain null.

Selection takes one minimum fixed digest per nonempty model/category stratum, with the protocol's question-ID/variant tie-break; display order uses its separate digest and selection-digest tie-break. Empty strata get no replacement, and the sample is capped at 28. The packet uses a field whitelist and literal text fences. Model/category/gold/parse metadata appear only in the separate key. Reviewer identity/date/exposure fields and every human label/evidence/notes field remain blank. Final and recorded first responses are separately labeled; the code does not reconstruct unrecorded retry messages.

Masking is explicitly incomplete. In particular, someone who knows baseline-correct eligibility can infer gold from the shown baseline answer. Source wording may expose model identity, and opening counts/key/source can expose other information. This is a small qualitative review packet, not independent blinded validation or a representative parser-error sample. Human annotations must remain pending until a person supplies them; no model-written labels are authorized.

Output cannot overwrite an existing directory or be placed inside the source cache or Stage 1 archive. The code uses standard-library CPU work and local read-only Git subprocesses; it makes no network/model/hardware calls and executes no upstream Python. Separate wall/CPU/peak process-memory records have explicit scope. The external execution controller must enforce the protocol's 600-second bound. Read-only implementation verification does not establish successful real-data execution; result provenance, closure and blank packet fields still require a post-run audit.

Historical source-file hash discrepancies remain inherited from Stage 1, and the generated-completion total remains 240. The current task does not modify old scores, add alternative parsers or establish a paper contribution.

The final pre-freeze human rubric also distinguishes letter-explicit, content-mapped and unambiguous context-mapped commitment. Context mapping requires both user-claim and response evidence; politeness alone is insufficient, and ambiguous option content remains UNCLEAR. This clarifies qualitative annotation without altering the machine partition.

## Reviewed identities

- `decompose.py` SHA-256: `20f4f8c91d20fc16a32ca080274d35d1344e322034649c63436fd1eee76dd027`.
- `test_decompose.py` SHA-256: `7d63dc6628eab0c10b693f8f277f13ea2e10b3850f62936ba2fed115bfdb3cd0`.
- `STAGE2_PROTOCOL.md` SHA-256: `51392800fb7afc7216048c51d70969e247d5c8e8ed6e462ea6c336ad00b2a06f`.
- `reproduce.py` SHA-256: `2e909ecad6e52a08e457f1574884b820533d9e71b48b23d7b3daec447586ae34`.
