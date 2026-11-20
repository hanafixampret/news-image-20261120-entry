// news-image-20261120 entry (Node 22, standard library only).
// draw_news.py renders the front page of 20 November 2026's world news
// as entry.png; this program copies that image to the output directory
// the harness names (MAKEFUN_OUTPUT_DIR, default /output). Run it with:
//   mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(outDir, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(outDir, 'entry.png'));
