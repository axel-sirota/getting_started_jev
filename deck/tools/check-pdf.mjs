// Check the exported PDF: page count and size, link annotations per page against the
// <a href> links in each section of index.html, embedded fonts, and images per page
// (the deck has no raster images, so every page should report none).
// Usage: DECK_MODULE=1 node tools/check-pdf.mjs
import fs from "node:fs";
import path from "node:path";
import { PDFDocument, PDFName, PDFDict, PDFArray, PDFRawStream } from "pdf-lib";
import { deck, moduleNo } from "./paths.mjs";

const pdfPath = path.join(deck, `Getting-Started-with-Jev-Module-${moduleNo}.pdf`);
const html = fs.readFileSync(path.join(deck, "index.html"), "utf8");

// Expected links per section, in deck order (speaker notes excluded).
const sections = [...html.matchAll(/<section data-slide="([^"]+)"[\s\S]*?<\/section>/g)].map((m) => {
  const body = m[0].replace(/<aside class="notes">[\s\S]*?<\/aside>/, "");
  return { id: m[1], links: [...body.matchAll(/<a [^>]*href="([^"]+)"/g)].map((a) => new URL(a[1].replace(/&amp;/g, "&")).href) }; // normalised like Chrome (bare origins get a trailing /)
});

const doc = await PDFDocument.load(fs.readFileSync(pdfPath));
const pages = doc.getPages();
const ctx = doc.context;
const deref = (o) => (o ? ctx.lookup(o) : o);

let problems = 0;
const fonts = new Map();
let pageImages = [];

function walkResources(res, seen, acc) {
  res = deref(res);
  if (!(res instanceof PDFDict)) return;
  const f = deref(res.get(PDFName.of("Font")));
  if (f instanceof PDFDict) {
    for (const [, ref] of f.entries()) {
      const fd = deref(ref);
      const base = fd.get(PDFName.of("BaseFont"))?.toString();
      let desc = deref(fd.get(PDFName.of("FontDescriptor")));
      const desc2 = deref(fd.get(PDFName.of("DescendantFonts")));
      if (!desc && desc2 instanceof PDFArray) desc = deref(deref(desc2.get(0)).get(PDFName.of("FontDescriptor")));
      const embedded = !!(desc && (desc.get(PDFName.of("FontFile2")) || desc.get(PDFName.of("FontFile3")) || desc.get(PDFName.of("FontFile"))));
      fonts.set(base, (fonts.get(base) || embedded) && embedded);
    }
  }
  const xo = deref(res.get(PDFName.of("XObject")));
  if (xo instanceof PDFDict) {
    for (const [, ref] of xo.entries()) {
      if (seen.has(ref.toString())) continue;
      seen.add(ref.toString());
      const x = deref(ref);
      const dict = x instanceof PDFRawStream ? x.dict : x.dict || x;
      const sub = dict.get(PDFName.of("Subtype"))?.toString();
      if (sub === "/Image") acc.push(`${dict.get(PDFName.of("Width"))}x${dict.get(PDFName.of("Height"))}`);
      if (sub === "/Form") walkResources(dict.get(PDFName.of("Resources")), seen, acc);
    }
  }
}

pages.forEach((p, i) => {
  const { width, height } = p.getSize();
  const annots = deref(p.node.get(PDFName.of("Annots")));
  const uris = [];
  if (annots instanceof PDFArray) {
    for (let k = 0; k < annots.size(); k++) {
      const a = deref(annots.get(k));
      const act = deref(a.get(PDFName.of("A")));
      const uri = act && deref(act.get(PDFName.of("URI")));
      if (uri) uris.push(uri.decodeText ? uri.decodeText() : uri.toString());
    }
  }
  const imgs = [];
  walkResources(p.node.get(PDFName.of("Resources")), new Set(), imgs);
  pageImages.push(imgs);
  const exp = sections[i]?.links || [];
  const missing = exp.filter((u) => !uris.includes(u));
  const ok = missing.length === 0;
  if (!ok) problems++;
  console.log(`page ${String(i + 1).padStart(2)} slide ${String(sections[i]?.id).padEnd(3)} ${Math.round(width)}x${Math.round(height)} links ${uris.length}/${exp.length}${ok ? "" : " MISSING " + missing.join(" ")} images ${imgs.join(",") || "none"}`);
});

console.log(`\npages: ${pages.length} (sections in index.html: ${sections.length})`);
console.log("fonts:", [...fonts].map(([n, e]) => `${n} ${e ? "embedded" : "NOT EMBEDDED"}`).join("; "));
const rasterOtherThanLogo = pageImages.flat();
console.log(`raster images: ${rasterOtherThanLogo.length ? rasterOtherThanLogo.join(", ") : "none"}`);
console.log(`link problems: ${problems}`);
if (problems || pages.length !== sections.length) process.exitCode = 1;
