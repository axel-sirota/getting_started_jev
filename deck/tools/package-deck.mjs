// Package one module's deck for presenting and distributing:
//   1. PDF:    deck/moduleNN/Agentic-AI-Foundations-Module-NN.pdf (decktape, 1920x1080)
//   2. Folder: deck/dist/moduleNN/ with index.html + diagrams + css + vendor (self-contained:
//              open index.html anywhere, no repo needed)
//   3. Zip:    deck/dist/Agentic-AI-Foundations-Module-NN.zip (the folder plus the PDF)
// Usage: DECK_MODULE=1 node tools/package-deck.mjs
import { execFileSync } from "node:child_process";
import fs from "node:fs";
import os from "node:os";
import path from "node:path";
import { deck, deckRoot, moduleNo } from "./paths.mjs";

const name = `Agentic-AI-Foundations-Module-${moduleNo}`;
const index = path.join(deck, "index.html");
if (!fs.existsSync(index)) {
  console.error(`No deck at ${index}. Run /build-slides ${Number(moduleNo)} first.`);
  process.exit(2);
}

// decktape bundles its own Chrome, which can be a half-finished download; prefer a
// complete Chrome for Testing from the puppeteer cache (newest first).
function completeChrome() {
  const base = path.join(os.homedir(), ".cache", "puppeteer", "chrome");
  if (!fs.existsSync(base)) return null;
  const builds = fs.readdirSync(base).filter((d) => d.startsWith("mac_arm-")).sort().reverse();
  for (const b of builds) {
    const app = path.join(base, b, "chrome-mac-arm64", "Google Chrome for Testing.app");
    const bin = path.join(app, "Contents", "MacOS", "Google Chrome for Testing");
    const fw = path.join(app, "Contents", "Frameworks");
    if (fs.existsSync(bin) && fs.existsSync(fw) && fs.readdirSync(fw).length) return bin;
  }
  return null;
}

// 1. PDF
const pdf = path.join(deck, `${name}.pdf`);
const decktape = path.join(deckRoot, "node_modules", ".bin", "decktape");
const args = ["reveal", "--size", "1920x1080", "--pause", "1500"];
const chrome = completeChrome();
if (chrome) args.push("--chrome-path", chrome);
args.push(index, pdf);
console.log(`PDF: decktape ${chrome ? "(Chrome: " + path.basename(path.dirname(path.dirname(path.dirname(chrome)))) + ")" : ""}`);
execFileSync(decktape, args, { stdio: "inherit", cwd: deckRoot });

// 2. Self-contained folder: same layout as the repo (index.html next to css/ and vendor/),
//    so ../vendor/fonts in theme.css still resolves.
const dist = path.join(deckRoot, "dist", `module${moduleNo}`);
fs.rmSync(dist, { recursive: true, force: true });
fs.mkdirSync(dist, { recursive: true });
const html = fs.readFileSync(index, "utf8")
  .replaceAll('href="../vendor/', 'href="vendor/')
  .replaceAll('src="../vendor/', 'src="vendor/')
  .replaceAll('href="../css/', 'href="css/');
if (/(?:src|href)="\.\.\//.test(html)) {
  console.error("index.html still references ../ paths; fix the deck before packaging.");
  process.exit(3);
}
fs.writeFileSync(path.join(dist, "index.html"), html);
fs.cpSync(path.join(deck, "diagrams"), path.join(dist, "diagrams"), {
  recursive: true, filter: (src) => !src.endsWith(".mmd"),
});
fs.cpSync(path.join(deckRoot, "css"), path.join(dist, "css"), { recursive: true });
fs.cpSync(path.join(deckRoot, "vendor"), path.join(dist, "vendor"), { recursive: true });
fs.copyFileSync(pdf, path.join(dist, `${name}.pdf`));
if (fs.existsSync(path.join(deck, "notes.md"))) {
  fs.copyFileSync(path.join(deck, "notes.md"), path.join(dist, "speaker-notes.md"));
}

// 3. Zip
const zip = path.join(deckRoot, "dist", `${name}.zip`);
fs.rmSync(zip, { force: true });
execFileSync("zip", ["-qr", zip, `module${moduleNo}`], { cwd: path.join(deckRoot, "dist") });

const kb = (f) => `${Math.round(fs.statSync(f).size / 1024)} KB`;
console.log(`\nPDF:    ${path.relative(deckRoot, pdf)} (${kb(pdf)})`);
console.log(`Folder: ${path.relative(deckRoot, dist)}/ (open index.html; press S for speaker view)`);
console.log(`Zip:    ${path.relative(deckRoot, zip)} (${kb(zip)})`);
