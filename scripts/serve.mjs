// scripts/serve.mjs
// Zero-dependency static file server for the proof-of-concept web UI.
// Serves the repo root so index.html, ./dist/web/main.js, and
// ./data/*.json resolve with simple relative paths.
//   npm run dev   (build + serve)   ->   http://localhost:8000

import { createServer } from "node:http";
import { readFile } from "node:fs/promises";
import { extname, join, normalize } from "node:path";
import { fileURLToPath } from "node:url";

const ROOT = fileURLToPath(new URL("..", import.meta.url));
const PORT = Number(process.env.PORT ?? 8000);

const TYPES = {
  ".html": "text/html; charset=utf-8",
  ".js": "text/javascript; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".xml": "application/xml; charset=utf-8",
  ".jsonld": "application/ld+json; charset=utf-8",
};

const server = createServer(async (req, res) => {
  try {
    const url = new URL(req.url ?? "/", "http://localhost");
    const rel = url.pathname === "/" ? "/index.html" : url.pathname;
    const path = normalize(join(ROOT, rel));
    if (!path.startsWith(ROOT)) {
      res.writeHead(403).end("Forbidden");
      return;
    }
    const body = await readFile(path);
    res.writeHead(200, {
      "Content-Type": TYPES[extname(path)] ?? "application/octet-stream",
    });
    res.end(body);
  } catch {
    res.writeHead(404).end("Not found");
  }
});

server.listen(PORT, () => {
  console.log(`policy-as-data serving on http://localhost:${PORT}`);
});
