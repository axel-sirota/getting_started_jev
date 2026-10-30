// Where each deck tool reads and writes. One deck per module:
//   DECK_MODULE=1 node tools/render-diagrams.mjs
// targets deck/module01/ (index.html, diagrams/, checks/, mermaid-overrides.json) and reads
// imp_files/slides/module01_slides.md and module01_diagrams.md. Shared assets (css/, vendor/,
// tools/fonts) stay in deck/ and module decks link them with ../
import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

export const tools = path.dirname(fileURLToPath(import.meta.url));
export const deckRoot = path.resolve(tools, "..");
export const repo = path.resolve(deckRoot, "..");

const raw = process.env.DECK_MODULE;
if (!raw || !/^\d+$/.test(raw)) {
  console.error("Set DECK_MODULE to the module number, e.g. DECK_MODULE=1 node tools/render-diagrams.mjs");
  process.exit(2);
}
export const moduleNo = String(Number(raw)).padStart(2, "0");
export const deck = path.join(deckRoot, `module${moduleNo}`);
export const planFile = path.join(repo, "imp_files", "slides", `module${moduleNo}_slides.md`);
export const diagramsFile = path.join(repo, "imp_files", "slides", `module${moduleNo}_diagrams.md`);

const moduleOverrides = path.join(deck, "mermaid-overrides.json");
export const overridesFile = fs.existsSync(moduleOverrides)
  ? moduleOverrides
  : path.join(tools, "mermaid-overrides.json");

fs.mkdirSync(path.join(deck, "diagrams"), { recursive: true });
