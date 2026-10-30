# Notebook Edit Protocol

Canonical procedure for safely reading, editing, inserting, and verifying
Jupyter `.ipynb` cells. Every notebook-touching skill (in any repo) references
this file. Single source of truth - do not fork it per repo.

## Why this exists

Editing notebooks naively fails in three documented ways:

1. **The Read gate.** Claude Code's `NotebookEdit` requires the file to be
   `Read` first. The `Read` tool rejects any notebook over ~25k tokens, and
   `offset`/`limit` are IGNORED for `.ipynb` (Read treats a notebook as one
   unit). There is no env var to lift the notebook limit
   (claude-code issue #16984). So on a large notebook `NotebookEdit` is simply
   unusable.
2. **The insert-order bug.** `NotebookEdit` with `edit_mode=insert` can place
   cells in arbitrary positions even with an explicit `cell_id`
   (claude-code issues #5197, #18538). `cell_id` reduces but does not
   eliminate this.
3. **Missing cell ids.** Cells created by earlier tooling may have no `id`
   field. `NotebookEdit`'s `cell_id` targeting cannot address them, and any
   id-based verification silently skips them.

The conclusion: no single tool is safe by itself. Safety comes from the
VERIFICATION GATES below, applied regardless of which mechanism does the edit.

## The mechanism, by notebook size

Check size first: `wc -c <notebook>` and estimate tokens (~3.3 chars/token),
or just try to `Read` it.

- **Notebook fits under the Read limit (~25k tokens):** `NotebookEdit` is
  usable. Still apply every gate below. Still never trust `insert` order -
  read back and assert position.
- **Notebook exceeds the Read limit:** `NotebookEdit` cannot be used (its Read
  precondition fails). Edit the notebook as JSON in place with a small,
  AUDITED Python step: load with `json` or `nbformat`, locate the target cell
  by `id` AND by matching its current content, modify, write back. This is NOT
  a blind bulk script - it is a single targeted edit with the gates below.

Either way, the gates are mandatory. The mechanism is secondary.

## Step 0 - Normalize cell ids (always, before any edit)

Every cell must have an `id`. Backfill missing ids once, up front:

```python
import nbformat
nb = nbformat.read(path, as_version=4)
nbformat.validate(nb)          # raises if structurally broken
nb = nbformat.normalize(nb)[1] # normalize() returns (changes, normalized_nb)
nbformat.write(nb, path)       # now every cell has an id
```

`nbformat.normalize()` (nbformat >= 5.5.0) generates ids for any cell missing
one. Do this before locating cells, so id-based targeting is reliable.

## Step 0.5 - Snapshot the id order BEFORE the edit (mandatory, Axel's rule)

Cell order is the thing that silently breaks. Before EVERY edit, insert or delete, print and
keep the full id map:

```python
import json
def id_map(path):
    nb = json.load(open(path))
    return [(c["id"], c["cell_type"], "".join(c["source"])[:50]) for c in nb["cells"]]
before = id_map(path)
for i, (cid, kind, head) in enumerate(before):
    print(i, cid, kind, repr(head))
```

Write down the expected AFTER order before touching anything: which id is new and right
after which id, which id is gone, which ids are unchanged.

## Step 1 - Locate by id AND content

Never address a cell by bare index alone - inserts shift indices. To target a
cell:

1. Find it by `id`.
2. Assert its current source contains the exact text you expect to change
   (the "OLD text" from the design doc / plan). If the assertion fails, STOP -
   the notebook is not in the state you assumed.

## Step 2 - Order-safe insert

To insert a new cell after cell with id `X`:

1. Find the index `i` of the cell whose `id == X`.
2. Splice the new cell into `nb.cells` at exactly `i + 1`.
3. Give the new cell a fresh `id` (uuid4 hex, or let `nbformat.normalize` do it).

Never rely on `NotebookEdit`'s append/insert to land the cell in the right
place. Always control the index explicitly and verify in Step 4.

## Step 3 - Apply the edit

Apply exactly the change specified (the design doc's EDIT / NEW / DELETE /
MERGE action, or the plan's cell content). One logical change at a time.
Preserve nbformat's source-as-list-of-strings convention
(`source = text.splitlines(keepends=True)`).

## Step 4 - Read-back assertion (mandatory)

After writing, RE-READ the file from disk, RE-LOCATE the cell by id, and
assert its content is exactly what you intended. This is the single most
important gate - it catches wrong-cell edits and insert-order bugs that the
edit tool will not report.

### Step 4b - Compare the id order AFTER against BEFORE (mandatory)

```python
after = id_map(path)
b_ids = [x[0] for x in before]
a_ids = [x[0] for x in after]
# insert after X:  a_ids == b_ids[:i+1] + [new_id] + b_ids[i+1:]
# delete Y:        a_ids == [x for x in b_ids if x != Y]
# edit in place:   a_ids == b_ids
assert a_ids == expected_ids, f"ORDER CHANGED:\nexpected {expected_ids}\ngot      {a_ids}"
```

Every id not touched by the edit must keep its relative order. If the assertion fails,
STOP, restore order from the BEFORE map (re-splice by id), and re-verify before any
further edit. Print the AFTER map so the change is visible in the transcript.

## Step 5 - Structural gate

`nbformat.validate(nb)` must pass. A notebook that fails schema validation is
broken regardless of how good the content looks.

## Step 6 - Static code gate (no kernel, no execution)

Per-cell syntax check is not enough - it misses a cell using a name defined in
another cell. Concatenate ALL code cells IN ORDER into one string and check
the whole:

```python
import ast
from pyflakes import api as pyflakes_api

code = "\n\n".join(
    "".join(c["source"]) for c in nb.cells if c.cell_type == "code"
)
ast.parse(code)                       # SyntaxError if broken
pyflakes_api.check(code, "notebook")  # 0 = no undefined names / unused imports
```

`ast.parse` catches syntax errors. `pyflakes` on the concatenated code catches
undefined-name errors ACROSS cells - the orphaned-variable class of bug - with
no kernel and no execution. Lines that are Jupyter magics (`!pip`, `%load`)
must be stripped or commented before this check, since they are not valid
Python. Zero pyflakes undefined-name warnings is the bar.

## Step 7 - Pair parity (course repos)

This repo keeps `exercises.ipynb` + `solutions.ipynb` twins. After editing one,
apply the same structural change to the twin. Rule: solutions = exercises minus
`# SAFETY-NET` cells, same order; LAB cells become SOLUTION cells at the same
position. `validate_notebooks.py <N> --pair` must pass.

## Hard rules (summary)

- BEFORE map printed, expected AFTER order written down, AFTER map printed and
  asserted. Every edit, every time.
- Never more than 5 cells per batch without approval.

## Hard rules

- Never edit a notebook you have not located cell-by-cell with Step 1.
- Never skip Step 4 (read-back assertion) - it is the real safety net.
- Never insert without controlling the index (Step 2).
- A blind bulk script that rewrites cells by index without per-cell content
  assertion is FORBIDDEN. A targeted, audited, gated edit is fine even when it
  is implemented in Python because the notebook is too large for NotebookEdit.
- The notebook must still run top-to-bottom after "Restart and Run All" - the
  static gates reduce risk but do not replace a real run before declaring done.
