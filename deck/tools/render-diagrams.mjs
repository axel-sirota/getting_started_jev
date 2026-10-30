// Render deck/moduleNN/diagrams/slide-NN.mmd to slide-NN.svg with mermaid-cli, brand themed,
// Inter measured and embedded into each SVG so it renders the same inside <img>.
// Usage: DECK_MODULE=1 node tools/render-diagrams.mjs 2 3   (or no slide args for every .mmd)
import fs from "node:fs";
import path from "node:path";
import { pathToFileURL } from "node:url";
import puppeteer from "puppeteer";
import { renderMermaid } from "@mermaid-js/mermaid-cli";
import { deck, overridesFile, tools as here } from "./paths.mjs";

const dir = path.join(deck, "diagrams");
const config = JSON.parse(fs.readFileSync(path.join(here, "mermaid-config.json"), "utf8"));
// Per-slide layout tuning, keyed by slide number (deck/moduleNN/mermaid-overrides.json if it
// exists, else tools/mermaid-overrides.json). The .mmd files stay byte-exact.
const overrides = JSON.parse(fs.readFileSync(overridesFile, "utf8"));

function merge(base, extra) {
  const out = { ...base };
  for (const [k, v] of Object.entries(extra || {})) {
    out[k] = v && typeof v === "object" && !Array.isArray(v) ? merge(base[k] || {}, v) : v;
  }
  return out;
}

const pad = (n) => String(n).padStart(2, "0");
const args = process.argv.slice(2);
const files = args.length
  ? args.map((n) => `slide-${pad(n)}.mmd`)
  : fs.readdirSync(dir).filter((f) => /^slide-\d+\.mmd$/.test(f)).sort(); // skips *.original.mmd

// Mermaid emits <svg width="100%" style="max-width: Npx">. Inside an <img> that caps
// the drawing at N px, so give the root its real size and let the deck scale it.
function fixRootSize(svg) {
  const open = svg.match(/^<svg\b[^>]*>/)[0];
  const [, , , w, h] = open.match(/viewBox="([-\d.]+) ([-\d.]+) ([-\d.]+) ([-\d.]+)"/).slice(0).map(Number);
  let tag = open
    .replace(/\swidth="[^"]*"/, "")
    .replace(/\sheight="[^"]*"/, "")
    .replace(/\sstyle="[^"]*"/, "");
  tag = tag.replace(/^<svg\b/, `<svg width="${w}" height="${h}"`);
  return tag + svg.slice(open.length);
}

// Dagre lays out disconnected subgraphs right to left (last declared on the left).
// "_clusterOrder": "source" moves each top-level cluster, with its nodes, edges and
// labels, so clusters read left to right in the order the .mmd declares them.
async function orderClustersAsSource(browser, svgText, order) {
  const p = await browser.newPage();
  try {
    await p.setContent(`<!doctype html><body style="margin:0">${svgText}</body>`);
    return await p.evaluate((order) => {
      const svg = document.querySelector("svg");
      const vb = svg.viewBox.baseVal;
      const box = (el) => {
        const r = el.getBoundingClientRect(), s = svg.getBoundingClientRect();
        const k = vb.width / s.width;
        return { l: (r.left - s.left) * k + vb.x, r: (r.right - s.left) * k + vb.x };
      };
      const clusters = [...svg.querySelectorAll("g.cluster")].map((g) => ({ g, ...box(g) }));
      // Declared order comes from the .mmd subgraph ids; cluster ids are "<svgId>-<name>".
      const declared = order.map((name) => clusters.find((c) => c.g.id.endsWith("-" + name))).filter(Boolean);
      const byX = clusters.slice().sort((a, b) => a.l - b.l);
      const gap = byX.length > 1 ? byX[1].l - byX[0].r : 0;
      let x = byX[0].l;
      for (const c of declared) { c.dx = x - c.l; x += (c.r - c.l) + gap; }
      const owner = (el) => {
        const b = box(el), mid = (b.l + b.r) / 2;
        return clusters.find((c) => mid >= c.l - 1 && mid <= c.r + 1);
      };
      const movers = svg.querySelectorAll("g.cluster, g.node, g.edgePaths > path, path.flowchart-link, g.edgeLabels > g.edgeLabel, g.edgeLabel");
      const done = new Set();
      for (const el of movers) {
        if (done.has(el)) continue;
        done.add(el);
        const c = el.classList.contains("cluster") ? clusters.find((k) => k.g === el) : owner(el);
        if (!c || !c.dx) continue;
        const t = el.getAttribute("transform") || "";
        el.setAttribute("transform", `translate(${c.dx},0) ${t}`.trim());
      }
      return new XMLSerializer().serializeToString(svg);
    }, order);
  } finally {
    await p.close();
  }
}

// "_tightFit": true (slide 27 timeline). Shortens the dashed timeline tails to end
// just below the lowest event box, then sets the viewBox to the drawn content plus a
// small margin, so empty space does not shrink the diagram on the slide.
async function tightFit(browser, svgText) {
  const p = await browser.newPage();
  try {
    await p.setContent(`<!doctype html><body style="margin:0">${svgText}</body>`);
    return await p.evaluate(() => {
      const svg = document.querySelector("svg");
      const tails = [...svg.querySelectorAll("line[stroke-dasharray]")];
      if (tails.length) {
        const top = Math.min(...tails.map((l) => Number(l.getAttribute("y1"))));
        let bottom = top;
        for (const n of svg.querySelectorAll("g.timeline-node")) {
          const b = n.getBBox();
          const m = n.getCTM(), r = svg.getCTM().inverse().multiply(m);
          const y = r.f + b.y + b.height;
          if (y > bottom) bottom = y;
        }
        for (const l of tails) l.setAttribute("y2", String(bottom + 24));
        // Centre the chart title over the nodes (Mermaid starts it at a fixed x, so a
        // long title runs far past the right edge of the chart).
        let nx1 = Infinity, nx2 = -Infinity;
        for (const n of svg.querySelectorAll("g.timeline-node")) {
          const r = n.getBoundingClientRect(), sr = svg.getBoundingClientRect();
          const k = svg.viewBox.baseVal.width / sr.width;
          nx1 = Math.min(nx1, (r.left - sr.left) * k + svg.viewBox.baseVal.x);
          nx2 = Math.max(nx2, (r.right - sr.left) * k + svg.viewBox.baseVal.x);
        }
        const title = [...svg.querySelectorAll("text")].find((t) => t.getAttribute("font-weight") === "bold");
        if (title && isFinite(nx1)) {
          title.setAttribute("x", String((nx1 + nx2) / 2));
          title.setAttribute("text-anchor", "middle");
        }
      }
      const root = svg.querySelector(":scope > g") || svg;
      let x1 = Infinity, y1 = Infinity, x2 = -Infinity, y2 = -Infinity;
      for (const el of svg.querySelectorAll(":scope > g, :scope > text")) {
        const b = el.getBBox();
        if (!b.width && !b.height) continue;
        x1 = Math.min(x1, b.x); y1 = Math.min(y1, b.y);
        x2 = Math.max(x2, b.x + b.width); y2 = Math.max(y2, b.y + b.height);
      }
      const pad = 12;
      svg.setAttribute("viewBox", `${x1 - pad} ${y1 - pad} ${x2 - x1 + 2 * pad} ${y2 - y1 + 2 * pad}`);
      return new XMLSerializer().serializeToString(svg);
    });
  } finally {
    await p.close();
  }
}

// "_equalLanes": true (Module 4 slide 6, swimlanes). Gives every top-level cluster the same
// top and bottom, so side-by-side groups read as full-height lanes (BPMN lanes run the whole
// length of the pool), and keeps each group title at its lane's top.
async function equalLanes(browser, svgText) {
  const p = await browser.newPage();
  try {
    await p.setContent(`<!doctype html><body style="margin:0">${svgText}</body>`);
    return await p.evaluate(() => {
      const svg = document.querySelector("svg");
      const lanes = [...svg.querySelectorAll("g.cluster")].map((g) => ({ g, rect: g.querySelector(":scope > rect") })).filter((l) => l.rect);
      if (lanes.length < 2) return new XMLSerializer().serializeToString(svg);
      const top = Math.min(...lanes.map((l) => Number(l.rect.getAttribute("y"))));
      const bottom = Math.max(...lanes.map((l) => Number(l.rect.getAttribute("y")) + Number(l.rect.getAttribute("height"))));
      for (const { g, rect } of lanes) {
        const dy = Number(rect.getAttribute("y")) - top;
        rect.setAttribute("y", String(top));
        rect.setAttribute("height", String(bottom - top));
        const label = g.querySelector(":scope > g.cluster-label");
        const m = label && (label.getAttribute("transform") || "").match(/translate\(\s*([-\d.]+)[ ,]+([-\d.]+)\s*\)/);
        if (m) label.setAttribute("transform", `translate(${m[1]}, ${Number(m[2]) - dy})`);
      }
      return new XMLSerializer().serializeToString(svg);
    });
  } finally {
    await p.close();
  }
}

const browser = await puppeteer.launch({ headless: true });
let failed = 0;
try {
  for (const f of files) {
    const def = fs.readFileSync(path.join(dir, f), "utf8");
    const id = "d" + f.match(/\d+/)[0];
    const { _clusterOrder, _linePlotStroke, _clusterTitleAlign, _tightFit, _labelShift, _equalLanes, ...slideOverride } = overrides[String(Number(f.match(/\d+/)[0]))] || {};
    const mermaidConfig = merge(config, slideOverride);
    try {
      const { data } = await renderMermaid(browser, def, "svg", {
        backgroundColor: "transparent",
        mermaidConfig: mermaidConfig,
        svgId: id,
        fontEmbed: true,
        customFontCSS: [
          { cssUrl: pathToFileURL(path.join(here, "fonts", "mermaid-fonts.css")), allowParentDirectoryLevel: 2 },
        ],
      });
      const out = path.join(dir, f.replace(/\.mmd$/, ".svg"));
      let svgText = new TextDecoder().decode(data);
      // No drop shadows: Chrome rasterises CSS filters when printing to PDF, which
      // turned every node into a bitmap. Flat nodes keep the PDF fully vector.
      svgText = svgText.replace(/filter:\s*(drop-shadow|brightness)\([^)]*\)/g, "filter:none")
        .replace(/\sfilter="url\([^)]*\)"/g, "");
      // One dotted style deck-wide, visible at 1280x720: 2.5 px, dark grey, 6 6 dash.
      // Also fixes a Mermaid bug where some dotted links (e.g. slide 8 SEC -.- IDP)
      // got an inline stroke-dasharray that drew them solid.
      const DOTTED = "stroke-dasharray: 6 6; stroke-width: 2.5px; stroke: #4B5563;";
      svgText = svgText.replace(/<path [^>]*edge-pattern-dotted[^>]*>/g, (tag) =>
        /style="/.test(tag)
          ? tag.replace(/style="[^"]*"/, `style="${DOTTED}"`)
          : tag.replace(/\/?>$/, (end) => ` style="${DOTTED}"${end}`));
      // Sequence diagrams: dotted (reply) messages get the same style.
      svgText = svgText.replace(/<line [^>]*class="messageLine1"[^>]*>/g, (tag) =>
        tag.replace(/style="[^"]*"/, `style="stroke-dasharray: 6 6; stroke-width: 2.5px; stroke: #4B5563; fill: none;"`));
      // Pie charts: Mermaid gives every slice label one colour. Pick white or #111827
      // per slice from the slice fill's luminance, so labels on light slices stay readable.
      if (/class="pieCircle"/.test(svgText)) {
        const fills = [...svgText.matchAll(/<path [^>]*class="pieCircle"[^>]*>/g)]
          .map((m) => (m[0].match(/fill="(#[0-9A-Fa-f]{6})"/) || [])[1]);
        const lum = (hex) => {
          const c = [1, 3, 5].map((i) => parseInt(hex.slice(i, i + 2), 16) / 255)
            .map((v) => (v <= 0.03928 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4));
          return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2];
        };
        // Slice labels: Mermaid rounds to whole percent (37%) while the points and legend
        // say 36.6. Show the share with one decimal, from the .mmd values (data order).
        const vals = [...def.matchAll(/^\s*"[^"]*"\s*:\s*([\d.]+)\s*$/gm)].map((m) => Number(m[1]));
        const sum = vals.reduce((a, b) => a + b, 0);
        let k = 0;
        svgText = svgText.replace(/(<text [^>]*class="slice"[^>]*>)[^<]*/g, (m, open) =>
          `${open}${(vals[k++] / sum * 100).toFixed(1)}%`);
        let i = 0;
        svgText = svgText.replace(/<text ([^>]*)class="slice" style="([^"]*)"/g, (m, pre, st) => {
          const hex = fills[i++];
          const ink = hex && lum(hex) > 0.18 ? "#111827" : "#FFFFFF";
          return `<text ${pre}class="slice" style="${st} fill: ${ink};"`;
        });
      }
      // "_clusterTitleAlign": "left" moves each group title to the group's top-left
      // corner (slide 8: the centred title sat on the incoming arrow). Label only.
      if (_clusterTitleAlign === "left") {
        svgText = svgText.replace(
          /(<g class="cluster"[^>]*><rect [^>]*?x="([-\d.]+)"[^>]*\/><g class="cluster-label" transform="translate\()([-\d.]+)(, [-\d.]+\)")/g,
          (m, pre, rx, _tx, post) => `${pre}${Number(rx) + 20}${post}`);
      }
      // "_linePlotStroke": N thickens xychart line plots (Mermaid has no config for it).
      if (_linePlotStroke) {
        svgText = svgText.replace(/(<g class="line-plot-\d+"><path [^>]*?)stroke-width="[^"]*"/g, `$1stroke-width="${_linePlotStroke}" stroke-linejoin="round" stroke-linecap="round"`);
      }
      // "_labelShift": {"<edge label text>": [dx, dy]} moves one edge label (Module 4
      // slide 12: Dagre put the return label of a two-way pair under the target node).
      if (_labelShift) {
        for (const [text, [dx, dy]] of Object.entries(_labelShift)) {
          svgText = svgText.replace(
            /<g class="edgeLabel"([^>]*?)transform="translate\(([-\d.]+), ?([-\d.]+)\)"([^>]*)>((?:(?!<g class="edgeLabel").)*?)<\/g><\/g>/gs,
            (m, pre, x, y, post, inner) => inner.replace(/<[^>]+>/g, "").trim() === text
              ? `<g class="edgeLabel"${pre}transform="translate(${Number(x) + dx}, ${Number(y) + dy})"${post}>${inner}</g></g>`
              : m);
        }
      }
      if (_tightFit) svgText = await tightFit(browser, svgText);
      if (_equalLanes) svgText = await equalLanes(browser, svgText);
      if (_clusterOrder === "source") svgText = await orderClustersAsSource(browser, svgText, [...def.matchAll(/^\s*subgraph\s+([\w-]+)/gm)].map((m) => m[1]));
      fs.writeFileSync(out, fixRootSize(svgText));
      console.log(`ok   ${f} -> ${path.basename(out)} (${Math.round(data.length / 1024)} KB)`);
    } catch (e) {
      failed++;
      console.log(`FAIL ${f}: ${e.message}${e.cause ? " | cause: " + e.cause.message : ""}`);
    }
  }
} finally {
  await browser.close();
}
if (failed) process.exitCode = 1;
