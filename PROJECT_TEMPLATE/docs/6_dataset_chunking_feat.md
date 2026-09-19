# 6. Dataset Cleaning — Chunked Multi-File Implementation

**Deliverable:** chunked, multi-file, LLM-backed dataset cleaning
**Status:** implemented, tested, verified
**Scope:** backend dataset pipeline + API + extension client method

---

## 1. What Was There Before and How It Worked

### 1.1 Answer to the direct question: does the agent use an LLM for data cleaning?

**No.** Before this change the agent had **no data-cleaning capability at all**.
The only dataset component was `DatasetAnalyzer`
(`PROJECT_TEMPLATE/backend/analyzers/dataset_analyzer.py`), and it *analysed*
datasets; it never modified, rewrote or exported a single record.

The one and only LLM call in that component was a **quality assessment of 5 sample
records**, not a cleaning pass:

```python
# dataset_analyzer.analyze() — before this change
if self._llm.is_available:
    llm_result = await self._llm_enhance(full_path, records[:5], {...})
```

```python
# dataset_analyzer._llm_enhance() — before this change
sample_text = "\n\n".join(json.dumps(r, ensure_ascii=False) for r in sample_records[:5])
prompt = f"""Analyze the following dataset samples and quality statistics..."""
return await self._llm.call_structured(prompt, temperature=0.3)
```

Consequences that matter for the requirement:

* The **entire dataset was never sent to the LLM** — only the first **5 records**
  plus aggregate statistics.
* The LLM was used only to *describe* quality (`quality_score`, `findings`,
  `warnings`, `recommendations`, `confidence`). Only `findings` and `warnings`
  were merged back into the result; no record was ever changed.
* Because the sample was hard-coded to `records[:5]`, the design dodged the
  "too much data in one request" problem by ignoring 99%+ of the dataset.

So the literal scenario in the requirement (*"the entire dataset is being sent to
the LLM at once"*) did **not** exist. What did not exist, and what the requirement
asks for, was a way to actually clean **all** records of **all** data files
without blowing the LLM context window. That capability was implemented.

### 1.2 What the agent actually did with datasets (deterministic only)

`DatasetAnalyzer.analyze(context)` processed **exactly one file** —
`dataset_path or context.dataset_paths[0]` — and computed everything in Python
heuristics:

| Step | Mechanism |
|---|---|
| Read the file | `_read_dataset()`: `.jsonl` (line-wise `json.loads`), `.json` (array or `{"data": [...]}`), `.csv` (`csv.DictReader`), `.txt`/`.tsv` (alternating prompt/response lines). `.parquet` returned an error string (pyarrow absent). |
| Token estimate | `total_chars / 4` (rough 4-chars-per-token heuristic) |
| Prompt/response lengths | `_extract_text()` alias resolution: `prompt/instruction/question/input`, `response/completion/output/answer/text` |
| Exact duplicates | MD5 of `prompt + "|" + response`, counted against a seen-hash set |
| Near duplicates | MD5 of `prompt` only (it shared the **same** `seen_hashes` set as the exact hashes) |
| Missing fields | % of records with empty prompt or response |
| Formatting score | −0.3 if the response does not start uppercase, −0.2 if it does not end in `. ! ?` |
| Language score | non-ASCII characters > 10 % of the text is treated as "non-English" |
| Instruction score | 1.0 when `len(prompt) > 10` |
| Response score | empty → 0.0, `< 20` chars → 0.5, else 1.0 |
| Quality score | `consistency × size_factor − dup/10 − near_dup/20 − missing/5`, clamped to 0–1 |
| Findings / warnings | Threshold rules (`dup > 0`, `near_dup > 5`, `missing > 0`, `fmt < 0.8`, `sample_count < 50`, …) |
| LLM step | 5-record quality assessment (see above) |

**Cleaning itself was only ever *recommended as text*.** The analyzer emitted
strings such as *"Remove duplicate samples to improve training efficiency."* and
`recommendation/engine.py` added a deduplication recommendation with
`suggested_actions=["Run deduplication script", "Verify dataset integrity"]` —
there was no deduplication script anywhere in the repository.

### 1.3 A contract that existed on paper but not in code

`PROJECT_TEMPLATE/docs/api_specification.md` §2.3 already listed:

| Method | Path | Purpose |
|---|---|---|
| POST | `/api/v1/dataset/clean` | Generate cleanup recommendations |

No such route existed in `backend/api/routes.py` (only `/dataset/analyze`), and
`extension/src/services/apiClient.ts` only exposed `analyzeDataset()`. The dataset
part of the published API contract was therefore unimplemented.

---

## 2. Why It Was a Problem

| # | Problem | Impact |
|---|---|---|
| 1 | **No cleaning existed.** The agent diagnosed problems and delegated the work to the user. The endpoint promised in the API spec (`POST /dataset/clean`) was never implemented. | The product could not clean anything; the dataset stayed dirty. |
| 2 | **Single-file blind spot.** Everything was driven by `context.dataset_paths[0]`, although `ProjectScanner._discover_datasets()` already discovered *all* `*.json`, `*.jsonl`, `*.csv`, `*.parquet`, `*.txt`, `*.tsv` files of a project. | A project with `train/val/test` files received statistics for **one** file; the rest were silently ignored — no warning, no error. Any cleaning built on that path would have cleaned one file out of N. |
| 3 | **No chunking contract existed anywhere.** The only dataset→LLM pattern in the codebase was `_llm_enhance()`, which embeds raw records directly into a single prompt. Extending that pattern to "clean the dataset" means one giant request per file. | Context-window overflow, provider `400`/timeouts on large datasets, truncated output, unparsable JSON and — worst — silent, undetectable record loss. The `records[:5]` cap was the only thing hiding this: it "solved" the size problem by discarding data instead of chunking it. |
| 4 | **No integrity guarantee.** Nothing counted records in vs. out, nothing mapped cleaned output back to its source file, and nothing was written to disk. | A cleaned dataset could not be reconstructed or audited; record loss would be invisible. |
| 5 | **Fragile LLM JSON handling.** `LLMHelper.call_structured()` returned `json.loads(...)` verbatim. A model replying with a bare JSON *array* (natural for a batch/rewrite API) would have made existing callers run `llm_result.get(...)` on a `list` → `AttributeError`. Every LLM call also inherited the shared *analyst* system prompt. | Latent crash path, and no way to give a rewriting task its own guardrails — a summarising/analyst persona is exactly what must **not** be applied when the contract is "return the same records unchanged". |

---

## 3. How I Fixed It and What Fixes I Made

The fix keeps the existing architecture (`analyzers/`, `ai/`, `models/schemas.py`,
`api/routes.py`, `scanner/`) intact and adds one cohesive module plus its wiring.
No component was redesigned and `DatasetAnalyzer`'s public behaviour is preserved.

### 3.1 New files

| File | Purpose |
|---|---|
| `backend/cleaning/__init__.py` | Package exports (`DatasetCleaner`, I/O helpers). |
| `backend/cleaning/dataset_io.py` | Shared dataset I/O: `SUPPORTED_SUFFIXES`, `MAX_FILE_BYTES` (200 MB guard), `read_records()` (multi-format, error-collecting), `write_records()` (round-trip per format), `discover_dataset_files()` (multi-file/dir discovery, de-duplicated, sorted), `chunk_records()` (deterministic sequential chunker with record-count **and** character budgets). |
| `backend/cleaning/dataset_cleaner.py` | `DatasetCleaner`: discovery → per-file chunking → one LLM request per chunk → validation → merge → per-file write + manifest, with a deterministic fallback cleaner. |
| `backend/ai/prompts/cleaning/dataset_cleaning.md` | Per-chunk task prompt: what to clean, hard rules (same count, same order, same keys, no merging/splitting/deleting) and the exact output schema. |
| `backend/ai/prompts/system/dataset_cleaner.md` | Task-specific system prompt for the cleaning role (no analyst persona, no rewriting). |
| `backend/tests/test_dataset_cleaner.py` | 17 new tests: chunking, discovery, multi-file isolation, reconstruction, contract violations, no-provider fallback, API endpoints, LLM JSON handling. |

### 3.2 Modified files

| File | Change |
|---|---|
| `backend/models/schemas.py` | Added `ChunkCleaningSummary`, `FileCleaningSummary` (incl. `chunk_summaries`), `DatasetCleaningResult`. |
| `backend/ai/llm.py` | `call()` / `call_structured()` accept an optional `system_prompt` (default = the previous analyst prompt, so all existing callers are unchanged); a bare JSON array is wrapped as `{"items": [...]}`; a response that is neither object nor array now returns `None` instead of crashing callers. |
| `backend/analyzers/dataset_analyzer.py` | `_read_dataset()` now delegates to `cleaning.dataset_io.read_records()` — one parser for analysis and cleaning, no duplicated logic. |
| `backend/scanner/scanner.py` | Added public `discover_datasets()` (same rules as `scan()`, without hardware/model probing) so callers can reuse dataset discovery. |
| `backend/api/routes.py` | New `POST /api/v1/dataset/clean`; optional `cleanDatasets` flag on `POST /api/v1/project/analyze` (response gains a `cleaning` key); `_as_bool()` helper for string/JSON flags. |
| `extension/src/services/apiClient.ts` | Added `cleanDatasets()` (mirrors `analyzeDataset()`). |
| `docs/api_specification.md` | §2.3 documents the implemented endpoint + request/response model. |
| `extension/backend/**` | Regenerated packaged backend copy via `python build_backend_into_extension.py`. |

### 3.3 Key design decisions

1. **Chunks never cross file boundaries.** Discovery produces a file list; each
   file is read and chunked *independently*. A request can therefore only ever
   contain records from one file — mixing files is structurally impossible.
2. **One LLM request per chunk** (default 25 records / 12 000 characters,
   configurable). The full dataset is never part of one request.
3. **Deterministic, order-preserving chunking** so chunk *i* always maps to a
   known record range, which makes reconstruction exact.
4. **Fail-closed validation.** A response is accepted only if it is a list of
   objects with the *same length* as the chunk (order is required by the prompt).
   Otherwise the chunk keeps its original records and a warning is recorded — the
   other chunks are unaffected and no record is lost.
5. **Merge instead of replace.** Cleaned values are merged onto the original
   record: keys the model dropped are restored from the source, keys the model
   invented are ignored. A record can never lose fields or gain schema noise.
6. **Graceful degradation.** No provider (or a broken one) → built-in
   deterministic cleaning (whitespace/newline/control-character normalisation)
   still runs, so the pipeline always produces complete output.
7. **One output artifact per source file** plus a manifest, so the cleaned dataset
   can be reconstructed and audited without guessing.

---

## 4. How It Works Now

### 4.1 End-to-end flow

```
POST /api/v1/dataset/clean   (or /project/analyze with "cleanDatasets": true)
        │
        ▼
1. DISCOVER   ProjectScanner.discover_datasets() → all dataset files, or an
        │     explicit "datasetPaths" list (files and/or directories; a directory
        │     is expanded recursively). De-duplicated, sorted, ≤200 MB each.
        ▼
2. PER FILE   for each file (fully isolated from every other file):
        │        read_records()  → records + parse errors
        │        chunk_records() → sequential chunks (≤ chunkSize records and
        │                          ≤ maxChunkChars characters each)
        ▼
3. PER CHUNK  for each chunk (one LLM request per chunk):
        │        render cleaning prompt (file name, chunk i/N, record count,
        │        format, JSON array of *that chunk only*) + dataset_cleaner
        │        system prompt → call_structured(temperature=0.1)
        ▼
4. VALIDATE   same record count? list of objects?  ── no ──▶ keep originals
        │                                                    (fallback + warning)
        │  yes
        ▼
5. MERGE      cleaned values merged onto the original keys (no key loss,
        │     invented keys ignored)
        ▼
6. RECONSTRUCT  records appended in original order → records_out == records_in
        ▼
7. WRITE      <output>/<relative source path>     (same format as the source)
              <output>/cleaning_manifest.json     (per-file + per-chunk audit)
        ▼
8. RESULT     DatasetCleaningResult (per-file/per-chunk counts, warnings,
              preservation flags, output + manifest paths)
```

### 4.2 Integrity guarantees

* `records_out == records_in` **per file**; `records_preserved` is computed by
  comparing the two, not assumed.
* `cross_file_contamination` is `false` by construction (chunks are built inside
  the per-file loop) and is reported explicitly.
* Original record order is preserved (chunks are sequential and concatenated).
* Every chunk decision is recorded in `chunk_summaries` with status
  `cleaned` / `deterministic` / `fallback` plus its warnings.

### 4.3 Using it

**Whole project (discovers every dataset file):**

```bash
curl -X POST http://127.0.0.1:8000/api/v1/dataset/clean \
  -H "Content-Type: application/json" \
  -d '{ "projectPath": "C:/work/my-llm-project" }'
```

**Explicit files, smaller chunks:**

```json
{
  "projectPath": "C:/work/my-llm-project",
  "datasetPaths": ["data/train.jsonl", "data/val.jsonl"],
  "chunkSize": 20,
  "maxChunkChars": 8000,
  "outputDirectory": ".llm-training-agent/cleaned",
  "maxFiles": 0,
  "useLlm": true
}
```

**Response (abridged):**

```json
{
  "files": [
    {
      "source_file": "C:/work/my-llm-project/data/train.jsonl",
      "relative_path": "data/train.jsonl",
      "output_path": "C:/work/my-llm-project/.llm-training-agent/cleaned/data/train.jsonl",
      "format": "jsonl",
      "records_in": 1200,
      "records_out": 1200,
      "chunks_total": 48,
      "chunks_cleaned": 48,
      "chunks_fallback": 0,
      "chunk_summaries": [
        { "chunk_index": 1, "record_count": 25, "status": "cleaned", "llm_used": true }
      ],
      "records_preserved": true
    }
  ],
  "total_files": 1,
  "total_records_in": 1200,
  "total_records_out": 1200,
  "total_chunks": 48,
  "records_preserved": true,
  "cross_file_contamination": false,
  "llm_used": true,
  "manifest_path": ".../cleaned/cleaning_manifest.json",
  "confidence": "high"
}
```

**Opt-in during project analysis** (default `false`, so existing analysis timing
and provider cost are unchanged):

```json
POST /api/v1/project/analyze
{ "projectPath": "...", "cleanDatasets": true }
```

The response then carries an extra `cleaning` object with the same structure.

**Extension:** `await apiClient.cleanDatasets({ projectPath, chunkSize: 25 })`.

### 4.4 What the LLM receives (and what it must return)

Each request contains **only its own chunk**:

````
- Source file: train.jsonl
- Chunk: 3 of 48
- Records in this chunk: 25

```json
[ { "instruction": "...", "response": "..." }, ... ]
```
````

and the model must return

```json
{ "records": [ { "same_keys_as_input": "cleaned values" } ], "warnings": ["optional"] }
```

Prompt rules: same count, same order, same keys, no merging, splitting, dropping,
de-duplicating, reordering, translating or shortening — and *"do not delete a
record even if it looks empty or low quality; only flag it"*. The validator
independently enforces the count/shape rule, so prompt drift cannot corrupt the
dataset.

### 4.5 Deterministic fallback cleaning (no provider, or rejected chunks)

For a chunk without an accepted LLM response, rule-based normalisation is applied
to every string value (records preserved 1:1):

* `\r\n` → `\n`; trailing spaces/tabs before a newline removed
* runs of 3+ newlines collapsed to 2
* non-printable control characters removed (newlines/tabs kept)
* leading/trailing whitespace trimmed — recursively inside nested objects/lists

In addition, the number of records with an empty prompt or response is counted and
reported as a warning (same field aliases as the analyzer). They are reported,
never removed, because removal would break the count guarantee.

### 4.6 Configuration

| Setting | Default | Meaning |
|---|---|---|
| `chunkSize` | 25 | max records per LLM request |
| `maxChunkChars` | 12000 | max serialised characters per request (a single oversized record still gets its own chunk and is never split) |
| `outputDirectory` | `<project>/.llm-training-agent/cleaned` | cleaned-file destination (relative paths are project-relative) |
| `maxFiles` | 0 (all) | optional cap |
| `useLlm` | true | `false` ⇒ deterministic cleaning only, zero provider calls |

Supported formats: `.jsonl`, `.json`, `.csv`, `.tsv`, `.txt` — round-tripped in
their own format. CSV/TSV headers use the union of record keys in first-seen order,
so no field is dropped. `.parquet` is skipped with an explicit reason until an
optional parser is added.

---

## 5. Verification

| Check | Command | Result |
|---|---|---|
| Backend tests | `python -m pytest -q` (in `backend/`) | **74 passed** (57 before + 17 new) |
| New cleaning tests | `python -m pytest tests/test_dataset_cleaner.py -q` | **17 passed** |
| Extension tests | `npx vitest run` (in `extension/`) | **23 passed** (unchanged) |
| TypeScript | `npx tsc --noEmit -p ./` | **exit 0** |
| Lint | `python -m ruff check .` | 76 findings before **and** after → no new findings (all in pre-existing, untouched code) |
| Packaged copy | `python build_backend_into_extension.py` | backend copy regenerated; `cleaning/` + new prompts present |

Behaviour proven by the new tests:

* 60 records with `chunkSize = 25` ⇒ **3 requests of 25/25/10** records; no request
  ever contains the whole dataset; prompt placeholders are fully substituted and
  the dataset-cleaner system prompt is used.
* Two files (30 + 40 records) ⇒ 2 files processed, 70 records in / 70 out, and
  **every request contains records from exactly one file**.
* Reconstruction: one output file per source file exists, original order is kept
  (`id 0..11`), each output holds only its own file's data, and the manifest
  reports `records_in == records_out` per file with `records_preserved: true`.
* A model returning half the records ⇒ chunk marked `fallback`, **all** originals
  kept, warning mentions the record contract.
* A model returning unparsable text ⇒ fallback, `llm_used: false`, order intact.
* No provider configured ⇒ **zero LLM calls**, deterministic cleanup applied
  (`"  Hello   \n\n\n\nWorld \t\n"` → `"Hello\n\nWorld"`), all records preserved.
* Dropped keys are restored and invented keys ignored during merge.
* API: explicit paths, project discovery (2 files), `400` without a target,
  `404` for a missing project path.
* `LLMHelper` wraps a bare JSON array as `{"items": [...]}` and returns `None`
  (instead of raising) for non-JSON output.

### Side effect worth noting

Analysis and cleaning now share one parser. The only observable behaviour change
is that **`.tsv` files are parsed as tab-separated tables** (`csv.DictReader` with
`delimiter="\t"`) instead of alternating prompt/response lines. This removes a
divergence between the two components rather than introducing one; all pre-existing
tests continue to pass.

---

## 6. Limitations

* Cleaning quality depends on the configured model; the pipeline guarantees
  *structure and record preservation*, not semantic perfection.
* CSV/TSV values remain strings after cleaning (inherent to the format).
* `.parquet` is discovered but skipped (pyarrow is not a project dependency).
* Cleaning writes new files under `.llm-training-agent/cleaned`; source files are
  never modified in place — destructive edits require explicit user approval
  (`backend/editing/` remains the only module that can modify files, and only
  through its propose/apply/rollback flow).
* The opt-in `cleanDatasets` flag on `/project/analyze` issues one LLM request per
  chunk, i.e. runtime and provider usage grow with dataset size. That is exactly
  why it defaults to `false` and has its own dedicated endpoint.