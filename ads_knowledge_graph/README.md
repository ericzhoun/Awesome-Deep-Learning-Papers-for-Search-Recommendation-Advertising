# Ads Papers — Knowledge Graph

An interactive knowledge graph of the **Ads-related papers** curated in this repository
(`Awesome-Deep-Learning-Papers-for-Search-Recommendation-Advertising`).

## Open it

- **`index.html`** — fully self-contained interactive viewer (no dependencies, works offline).
  Open it directly, or serve the folder:
  ```bash
  python3 -m http.server 8000   # then open /ads_knowledge_graph/index.html
  ```
- **`knowledge_graph.json`** — the raw graph (nodes + edges) for reuse in other tools (Gephi, Neo4j, Observable…).

## What's inside

**104 Ads-related papers**, selected from the repo README:

- titles that explicitly mention ads / advertising / sponsored search / display advertising, plus
- CTR / CVR / conversion papers deployed on ads systems (Alibaba, Meta/Facebook, Google, Kuaishou, Sina Weibo, Baidu, Tencent, JD, Meituan, Criteo, Twitter, eBay, ByteDance…),
- the delayed-feedback conversion-attribution family,
- ranking-model calibration papers for ads systems,
- surveys covering online advertising.

### Nodes (155)

| Type | Count | Meaning |
|---|---|---|
| paper | 104 | an ads paper, colored by pipeline stage (★★ = repo's "industrial + influential" marker) |
| stage hub | 9 | Survey & Systems, Ads Retrieval, Pre-Ranking, CTR Ranking, CVR & Conversion, Delayed Feedback, Calibration, Relevance, Generative & Unified |
| theme hub | 11 | e.g. Attention & Behavior Sequence, Feature Interaction, Multi-task & Entire Space, Multi-domain, Generative & LLM, Distillation, Scaling Laws, Multimodal, GNN, Systems, Debiasing |
| company hub | 16 | Alibaba, Meta/Facebook, Google, Tencent, … |
| venue hub | 15 | KDD, WWW, SIGIR, CIKM, RecSys, AAAI, arXiv, … |

### Relations (494)

| Relation | Count | Meaning |
|---|---|---|
| `lineage` | 70 | **curated** "builds on" links, e.g. `DIN → DIEN → SIM → TWIN → TWINv2`, `ESMM → ESM2 → HM3`, `DFM → ES-DFM/DEFUSE`, `DCN → GDCN`, `MOBIUS → RARE`, `DHEN → Lattice` |
| `covers` | 5 | the repo's TOIS-2026 survey covers a family |
| `stage` | 104 | paper addresses a pipeline stage |
| `theme` | 114 | paper belongs to a research theme |
| `company` | 97 | paper authored/deployed by a company |
| `venue` | 104 | paper published at a venue |

## Viewer features

- Force-directed layout with **stage anchors** (the 9 pipeline hubs sit on a ring; papers cluster around them)
- Hover to highlight a node's neighborhood; **click** for a detail panel (title, venue, stage, themes, note, PDF link, curated *Builds on* / *Extended by* lists — all clickable)
- Filters: relation types, hub types, pipeline stages, **year range**, full-text **search**
- Drag nodes, scroll to zoom, double-click background to fit, pause physics, toggle paper labels

## Regenerating

The graph is generated from `../README.md` by a curated script — if the README changes, re-run:

```bash
python3 build_graph.py
```

Curation rules and the lineage table live in `build_graph.py` (`PAPERS`, `LINEAGE`).
