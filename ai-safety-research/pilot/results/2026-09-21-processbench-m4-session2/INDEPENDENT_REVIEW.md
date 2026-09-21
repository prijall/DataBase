# Independent outcome review — second M4 session, September 21, 2026

**Outcome: preflight passed; calibration stopped after two responses because reported memory free fell below the fixed limit.** Calibration is incomplete, its gate has not passed, and all 40 evaluation cases remain unattempted. This review used saved controller evidence only, without hardware connections, model calls or execution-code changes.

## Provenance and preflight

The manifest records execution commit `d2dd756ce237ab09f504db3f10173fd17040b5cc`, which prospectively documents this second session. Execution sources and the M4 policy remain byte-identical to frozen commit `017f1d708943876bda16bba67cc32b97c9ebaa14`. The complete saved transport binding matches the current source, worker, transformed stream, service-helper and policy hashes.

Independent reconstruction from the pinned dataset, prompt and selection reproduced all 60 jobs and message hashes. The preflight's job hash is `97e9f98f7bfdc9976111b98e8f063447b6f89f2d67a455f582f1264e9420a9d5`; the manifest's preflight hash matches the saved report (`1224bd5d4a6f3932f6a67b34ca90994436445fdf12aea4ccdb927bdb50738223`).

All 60 token records correspond to the selected jobs. Prompt lengths are **308–778 tokens**, with a maximum of **1,802 including the reserved 1,024 output tokens**, within the frozen 8,192-token context. The report contains 308 received non-generating operations, including 60 debug requests and 60 tokenizer requests. All 183 recorded resource observations satisfy the unchanged guards: pressure level 1 throughout, minimum reported free memory 20%, and no positive swap-usage or swapout growth relative to this session's baseline. The preflight lasted **13.221 seconds** and ended with idle confirmation.

The service log contains 122 successful `/api/chat` HTTP requests, consistent with the reviewed execution path: the initial 60 debug requests, 60 repeated debug checks during preflight verification, and two subject responses. These debug operations must not be counted as 120 additional benchmark answers. Ordinary runtime loading/warmup is also distinct from subject completions.

## Raw response verification

Both unique attempt starts, finishes, stream hashes, response hashes, raw concatenated contents, terminal events, prompt-token expectations and saved scores pass recomputation. Independent last-boxed-integer extraction agrees with the frozen parser. The complete saved `ANALYSIS.json` also matches recomputation.

| Case | Gold earliest error | Extracted integer | Stop | Output tokens | Prompt tokens | Usable / match |
|---|---:|---:|---|---:|---:|---|
| `gsm8k-160` | 2 | 2 | normal | 399 | 543 | yes / yes |
| `gsm8k-109` | 1 | 1,600,000 | length | 1,024 | 622 | no / no |

Both observed cases are from the erroneous-solution class. The second integer is out of range and comes from a length-limited response; it is not a valid error-location prediction. There are **2/20 recorded calibration responses, one usable response and one exact match**, with 18 calibration cases missing and no error-free-class observations. There is no completed-cohort score or estimable two-class harmonic mean. The displayed conditional 100% refers only to the single usable erroneous-solution response and must not be presented as benchmark accuracy.

## Resource stop, cleanup and archive

After the second response, pressure remained normal and swap had not grown, but reported free memory was **19%**, below the fixed 20% floor. The journal records this resource stop; there is no third attempt. Subject client elapsed time totals **39.289 seconds**; server-reported durations total **34.749 seconds**. Calibration stopped **120.737 seconds after preflight start**.

The service log records requested STOP, return code 0 and owned group absence. A separate cleanup observation **165.277 seconds after preflight start** reports ports 11435, 58808 and 59236 closed, no owned processes, pressure level 1 and 41% free memory. Published lifecycle records and their full-log hash agree with the controller log. The archived preflight, cleanup, manifest, journal, responses, both raw streams, analysis and summary are byte-identical to their original run files.

## Prospective smaller-context work

A 2,048-token context would arithmetically accommodate the recorded maximum prompt plus the existing output allowance, but requires a new frozen protocol, fresh rendering/tokenization checks and a successful resource preflight. It does not guarantee generation quality or memory fit. The two viewed cases are consumed development observations. For any redesigned calibration, use a newly frozen balanced 20-case selection whose problem groups are disjoint from all original 60; preserve the original 40 evaluation cases. Do not describe the remaining 18 old calibration cases as a new complete balanced calibration, or merge configurations into one score.
