"""Gera uma página HTML local para revisar visualmente um dataset curado."""

import json
import os
from pathlib import Path

import pandas as pd

_COLUMNS = {"timestamp_seconds", "output_path", "cluster_id", "selection_reason"}
_REASON_LABELS = {
    "sampled_fixed_interval": "Amostragem fixa",
    "temporal_novelty": "Mudança visual",
    "cluster_representative": "Representa o grupo",
}


def _json_for_html(value):
    """Serializa dados sem permitir que valores do manifest fechem a tag script."""
    return json.dumps(value, ensure_ascii=False).replace("<", "\\u003c")


def _frame_payload(manifest, review_dir):
    frames = []
    for record in manifest.to_dict("records"):
        output_path = record.get("output_path")
        if not output_path:
            continue
        image_path = Path(output_path).resolve()
        frames.append({
            "image": os.path.relpath(image_path, review_dir.resolve()).replace("\\", "/"),
            "timestamp": record.get("timestamp_seconds"),
            "cluster": record.get("cluster_id"),
            "reason": record.get("selection_reason") or "",
        })
    return frames


def _page_html(frames):
    payload = _json_for_html(frames)
    labels = _json_for_html(_REASON_LABELS)
    return f"""<!doctype html>
<html lang="pt-BR"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Revisão de frames — MonitoraMAR</title><style>
:root {{ color-scheme: light dark; font-family: system-ui, sans-serif; }} body {{ margin: 0; background: #111827; color: #e5e7eb; }}
header {{ position: sticky; top: 0; z-index: 1; padding: 18px 24px; background: #172033; border-bottom: 1px solid #374151; }} h1 {{ margin: 0 0 6px; font-size: 1.35rem; }} p {{ margin: 0; color: #cbd5e1; }}
.filters {{ display: flex; flex-wrap: wrap; gap: 10px; margin-top: 14px; align-items: end; }} label {{ display: grid; gap: 4px; font-size: .82rem; color: #cbd5e1; }}
select {{ min-width: 155px; padding: 7px; border: 1px solid #475569; border-radius: 6px; background: #0f172a; color: inherit; }} button {{ padding: 8px 11px; border: 0; border-radius: 6px; background: #2563eb; color: white; cursor: pointer; }}
main {{ padding: 20px 24px; }} #summary {{ margin-bottom: 16px; color: #93c5fd; }} #grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(260px, 1fr)); gap: 16px; }}
article {{ overflow: hidden; border: 1px solid #374151; border-radius: 9px; background: #172033; }} img {{ display: block; width: 100%; aspect-ratio: 16 / 9; object-fit: cover; background: #0f172a; }}
.details {{ display: grid; gap: 4px; padding: 11px; font-size: .86rem; }} .motives {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 5px; }} .badge {{ padding: 4px 7px; border-radius: 999px; background: #1e3a5f; color: #bfdbfe; font-size: .78rem; }}
</style></head><body><header><h1>Revisão visual da curadoria</h1><p>Use os filtros para conferir os frames antes da anotação humana.</p>
<div class="filters"><label>Cluster <select id="cluster"><option value="">Todos</option></select></label><label>Motivo <select id="reason"><option value="">Todos</option></select></label><button id="reset" type="button">Limpar filtros</button></div></header>
<main><div id="summary"></div><section id="grid"></section></main><script>
const frames = {payload}; const labels = {labels}; const cluster = document.querySelector('#cluster'); const reason = document.querySelector('#reason'); const grid = document.querySelector('#grid'); const summary = document.querySelector('#summary');
function populate(select, values, label = value => value) {{ [...new Set(values.filter(v => v !== null && v !== undefined && v !== ''))].sort((a, b) => String(a).localeCompare(String(b), undefined, {{numeric:true}})).forEach(v => {{ const o=document.createElement('option'); o.value=v; o.textContent=label(v); select.append(o); }}); }}
populate(cluster, frames.map(f => f.cluster)); populate(reason, frames.flatMap(f => f.reason.split(';').filter(Boolean)), value => labels[value] || value);
function render() {{ const filtered=frames.filter(f => (!cluster.value || String(f.cluster)===cluster.value) && (!reason.value || f.reason.split(';').includes(reason.value))); summary.textContent=`${{filtered.length}} de ${{frames.length}} frames exibidos`; grid.replaceChildren(...filtered.map(f => {{ const card=document.createElement('article'); const image=document.createElement('img'); image.src=f.image; image.loading='lazy'; image.alt=`Frame em ${{Number(f.timestamp).toFixed(2)}} segundos`; const details=document.createElement('div'); details.className='details'; [`Tempo: ${{Number(f.timestamp).toFixed(2)}} s`, `Cluster: ${{f.cluster ?? '—'}}`].forEach(t => {{ const line=document.createElement('div'); line.textContent=t; details.append(line); }}); const motives=document.createElement('div'); motives.className='motives'; f.reason.split(';').filter(Boolean).forEach(code => {{ const badge=document.createElement('span'); badge.className='badge'; badge.textContent=labels[code] || code; motives.append(badge); }}); details.append(motives); card.append(image, details); return card; }})); }}
[cluster, reason].forEach(e => e.addEventListener('input', render)); document.querySelector('#reset').addEventListener('click', () => {{ cluster.value=''; reason.value=''; render(); }}); render();
</script></body></html>"""


def build_review(dataset_dir, output_dir=None):
    """Cria ``index.html`` para revisar visualmente os frames do manifest."""
    dataset_dir = Path(dataset_dir)
    manifest_path = dataset_dir / "manifests" / "selections.csv"
    if not manifest_path.exists():
        raise FileNotFoundError(f"Manifest não encontrado: {manifest_path}")

    review_dir = Path(output_dir) if output_dir else dataset_dir / "review"
    review_dir.mkdir(parents=True, exist_ok=True)
    manifest = pd.read_csv(manifest_path)
    missing = _COLUMNS - set(manifest.columns)
    if missing:
        raise ValueError(f"Manifest sem colunas necessárias: {', '.join(sorted(missing))}")

    frames = _frame_payload(manifest, review_dir)
    index_path = review_dir / "index.html"
    index_path.write_text(_page_html(frames), encoding="utf-8")
    return {"frames": len(frames), "review": str(index_path)}
