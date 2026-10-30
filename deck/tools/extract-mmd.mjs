// Extract Mermaid blocks per slide from imp_files/slides/moduleNN_diagrams.md (the diagram
// source), compare each one with the block in moduleNN_slides.md, and write
// deck/moduleNN/diagrams/slide-NN.mmd byte-for-byte from the diagrams file.
// Usage: DECK_MODULE=1 node tools/extract-mmd.mjs 2 3        (write these slides)
//        DECK_MODULE=1 node tools/extract-mmd.mjs --check    (compare all, write nothing)
//        DECK_MODULE=1 node tools/extract-mmd.mjs --all      (write every slide's diagram)
import fs from "node:fs";
import path from "node:path";
import { deck, diagramsFile, planFile } from "./paths.mjs";

function blocksBySlide(file) {
  const text = fs.readFileSync(file, "utf8");
  const out = new Map();
  const heads = [...text.matchAll(/^### Slide (\d+) · .*$/gm)];
  heads.forEach((h, i) => {
    const start = h.index;
    const end = i + 1 < heads.length ? heads[i + 1].index : text.length;
    const chunk = text.slice(start, end);
    const m = chunk.match(/```mermaid\n([\s\S]*?)```/);
    if (m) out.set(Number(h[1]), m[1]);
  });
  return out;
}

const diag = blocksBySlide(diagramsFile);
const plan = blocksBySlide(planFile);
const args = process.argv.slice(2);

let mismatches = 0;
for (const n of [...new Set([...diag.keys(), ...plan.keys()])].sort((a, b) => a - b)) {
  if (diag.get(n) !== plan.get(n)) {
    mismatches++;
    console.log(`MISMATCH slide ${n}: diagrams file and slides file differ`);
  }
}
console.log(`compared ${diag.size} diagrams, ${mismatches} mismatches`);

if (!args.includes("--check")) {
  const wanted = args.includes("--all") ? [...diag.keys()] : args.map(Number);
  for (const n of wanted) {
    const src = diag.get(n);
    if (!src) { console.log(`slide ${n}: no diagram in the diagrams file`); continue; }
    const f = path.join(deck, "diagrams", `slide-${String(n).padStart(2, "0")}.mmd`);
    fs.writeFileSync(f, src);
    console.log(`wrote ${path.relative(deck, f)}`);
  }
}
if (mismatches) process.exitCode = 1;
