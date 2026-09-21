# Independent review of the smaller-context implementation

September 21, 2026. **Offline review passed; live execution remains pending.** No hardware connections or model requests were made during this review. The reviewer did not modify execution or selection code.

## Selection verification

An independent implementation of the documented normalization, salted group/record ranking and original-group exclusion derived the same twenty calibration IDs before inspecting the new selector's results:

`gsm8k-63`, `147`, `40`, `143`, `234`, `204`, `75`, `181`, `174`, `61`, `212`, `280`, `350`, `245`, `253`, `242`, `62`, `386`, `283`, `86` (all IDs have the `gsm8k-` prefix).

Using the pinned 400-row source and official prompt, the reviewer independently regenerated the complete new manifest, including a fresh CLI generation in a temporary controller directory. Both reproductions were byte-identical to the saved artifact. Reversing source row order produced the same manifest.

- New calibration contains exactly ten error-free and ten erroneous solutions, with twenty distinct normalized problem groups.
- None belongs to any of the sixty original reserved groups, including their unselected siblings. There are 315 eligible groups before selecting the replacement calibration.
- The forty evaluation records and their complete split metadata are identical to the original manifest, including order, labels, group hashes and message hashes.
- The combined reservation has sixty unique IDs and sixty unique groups. All sixty rendered messages and message hashes match reconstruction from the pinned source; no new label fields enter prompts.
- The original loader rejects the new manifest, and the new loader rejects the original manifest. The original selection artifact remains unchanged.

## Configuration and failure paths

The default profile remains `original` with context 8,192. The explicit `small-context-v1` profile changes only `num_ctx` to **2,048**; `num_predict` remains **1,024**, with unchanged temperature, seed and threads. Real-input integration checks confirm that the controller loads the new sixty jobs and sends the smaller options. The in-memory worker applies those options before metadata, rendering, tokenization or subject actions. It rejects a resident context other than exactly 2,048. The controller's temporary replacements restore the original loader/options afterward; its unmodified preflight module retains the original default.

Reviewed tests reject unknown profiles, modified output settings, an 8,192-context subject payload under the smaller profile, changed jobs and cross-profile reports. A mismatched profile report is refused before the controller dispatches a remote verification request. Plan, selector and new-selection hashes are included in transport and run provenance, and their tracked files are included in the pre-subject Git freeze check. Existing manifest equality checks prevent accepting a changed configuration or selection during resume.

The original resource thresholds, baseline handling, request deadlines, persistent budget, 150-second reserve, durable attempt journal, cancellation uncertainty, parser, completion requirements and calibration/evaluation gates remain unchanged. The earlier archived results are not rewritten or pooled into this new configuration.

## Validation and reviewed hashes

The complete offline suite passed **127 tests**, including 23 transport/profile tests and nine new selection tests. `git diff --check` passed. Independent real-source reconstruction and profile integration checks also passed.

| Artifact | SHA-256 |
|---|---|
| SSH adapter | `011303534c8726d5fe79900939f8ad57b49c0cc1c9601e60f4cbe7841f0eb24f` |
| New selector | `be5081795dc5db74a9249e3b9de4046a6afffccdb12ea6ff1dd640e284bec3b3` |
| New selection | `55e84656d599431ebab9658b6fb40ba2aee283c4c994577f72eceb281832b456` |
| Smaller-context plan | `5260640998f82e107e418b21d50093b8225fb2bc1f2f8d5a03bd5c086dbe2db1` |
| Reconstructed sixty jobs, canonical JSON | `17257b2bfaba6fc51c99fd330842471e570156c5ca1c44839aaaafbcd759e138` |
| Unchanged original selection | `2fb187e84c18bf6587334d72853577b4a94569fe8ad42cab5d739670c433bab8` |

## Remaining live requirements

These checks establish implementation behavior, not measured token fit, sustained memory headroom or benchmark performance. Freeze the reviewed code and manifest before execution. A new session must render/tokenize every newly selected prompt, verify `prompt_tokens + 1024 <= 2048`, confirm the actual loaded context and pass every original resource limit. Any failed check stops that session. Only a complete passing calibration admits the preserved evaluation set.
