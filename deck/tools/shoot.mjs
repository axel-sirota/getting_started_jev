// Screenshot slides at 1920x1080 and 1280x720 into deck/moduleNN/checks/, and print checks:
// title and point font sizes (slide px), diagram's smallest text size as shown at
// 1920x1080, overflow of the points column, and whether the diagram image loaded.
// Usage: DECK_MODULE=1 node tools/shoot.mjs 1 2
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import puppeteer from "puppeteer";
import { deck } from "./paths.mjs";

const indexUrl = pathToFileURL(path.join(deck, "index.html")).href;
// Slide ids are plan numbers from data-slide, e.g. 4 or 4b.
const pad = (id) => { const m = String(id).match(/^(\d+)(.*)$/); return m[1].padStart(2, "0") + m[2]; };
const slides = process.argv.slice(2);
fs.mkdirSync(path.join(deck, "checks"), { recursive: true });

const browser = await puppeteer.launch({ headless: true, args: ["--allow-file-access-from-files"] });
const page = await browser.newPage();

async function gotoSlide(n, w, h) {
  await page.setViewport({ width: w, height: h, deviceScaleFactor: 1 });
  await page.goto(indexUrl, { waitUntil: "load" });
  const ok = await page.evaluate(async (id) => {
    await document.fonts.ready;
    const i = Reveal.getSlides().findIndex((s) => s.dataset.slide === id);
    if (i < 0) return false;
    Reveal.slide(i);
    Reveal.layout();
    await Promise.all([...document.images].map((im) => im.decode().catch(() => {})));
    return true;
  }, String(n));
  if (!ok) throw new Error(`no section with data-slide="${n}"`);
  await new Promise((r) => setTimeout(r, 300));
}

// Smallest diagram text in slide px: SVG text sizes times the contain-fit scale.
async function diagramMinFont(svgFile, boxW, boxH) {
  const svg = fs.readFileSync(svgFile, "utf8");
  const p = await browser.newPage();
  await p.setContent(`<!doctype html><body style="margin:0">${svg}</body>`);
  const r = await p.evaluate(async (boxW, boxH) => {
    await document.fonts.ready;
    const s = document.querySelector("svg");
    const vb = s.viewBox.baseVal;
    const scale = Math.min(boxW / vb.width, boxH / vb.height);
    let min = Infinity, sample = "";
    for (const el of s.querySelectorAll("*")) {
      const hasText = [...el.childNodes].some((c) => c.nodeType === 3 && c.textContent.trim());
      if (!hasText || el.closest("style")) continue;
      const box = el.getBoundingClientRect();
      if (box.width === 0 && box.height === 0) continue;
      const fs = parseFloat(getComputedStyle(el).fontSize);
      if (fs < min) { min = fs; sample = el.textContent.trim().slice(0, 40); }
    }
    return { scale, min, sample, vbW: vb.width, vbH: vb.height };
  }, boxW, boxH);
  await p.close();
  return { ...r, effective: +(r.min * r.scale).toFixed(1) };
}

for (const n of slides) {
  const report = { slide: n };
  for (const [w, h] of [[1920, 1080], [1280, 720]]) {
    await gotoSlide(n, w, h);
    const file = path.join(deck, "checks", `slide-${pad(n)}-${w}.png`);
    await page.screenshot({ path: file });
    if (w === 1920) {
      const info = await page.evaluate(() => {
        const sec = Reveal.getCurrentSlide();
        const px = (el) => (el ? parseFloat(getComputedStyle(el).fontSize) : null);
        const pts = sec.querySelector(".points");
        const img = sec.querySelector(".diagram img");
        const r = img ? img.getBoundingClientRect() : null;
        const scale = Reveal.getScale();
        const overflow = [...sec.querySelectorAll(".slide *")].some((el) => {
          const b = el.getBoundingClientRect();
          return b.right > window.innerWidth + 1 || b.bottom > window.innerHeight + 1;
        });
        return {
          dataSlide: sec.dataset.slide,
          template: sec.dataset.template,
          titlePx: px(sec.querySelector("h2.title, h1.deck-title")),
          pointPx: px(sec.querySelector(".points li")),
          points: sec.querySelectorAll(".points li").length,
          pointsOverflow: pts ? pts.scrollHeight > pts.clientHeight + 1 : false,
          img: img ? { src: img.getAttribute("src"), loaded: img.complete && img.naturalWidth > 0, w: r.width / scale, h: r.height / scale } : null,
          notes: (sec.querySelector("aside.notes")?.textContent || "").trim().length > 0,
          slideNumber: document.querySelector(".slide-number")?.textContent.trim(),
          overflowViewport: overflow,
        };
      });
      Object.assign(report, info);
      if (info.img && info.img.loaded) {
        const d = await diagramMinFont(path.join(deck, info.img.src), info.img.w, info.img.h);
        report.diagram = { fitScale: +d.scale.toFixed(3), minSvgFont: d.min, minFontAt1920: d.effective, smallest: d.sample };
      }
    }
    report[`shot${w}`] = path.relative(deck, file);
  }
  console.log(JSON.stringify(report));
}
await browser.close();
