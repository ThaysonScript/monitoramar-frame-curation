"""Gera uma página HTML local para revisar visualmente um dataset curado."""

import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote

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
            "id": image_path.name,
            "image": os.path.relpath(image_path, review_dir.resolve()).replace("\\", "/"),
            "video": record.get("video_id") or "—",
            "timestamp": record.get("timestamp_seconds"),
            "cluster": record.get("cluster_id"),
            "reason": record.get("selection_reason") or "",
        })
    return frames


def _page_html(frames, allow_delete=False):
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
.details {{ display: grid; gap: 4px; padding: 11px; font-size: .86rem; }} .motives {{ display: flex; flex-wrap: wrap; gap: 6px; margin-top: 5px; }} .badge {{ padding: 4px 7px; border-radius: 999px; background: #1e3a5f; color: #bfdbfe; font-size: .78rem; }} .delete {{ margin-top: 8px; justify-self: start; background: #b91c1c; }} .delete:hover {{ background: #dc2626; }}
</style></head><body><header><h1>Revisão visual da curadoria</h1><p>Use os filtros para conferir os frames antes da anotação humana.</p>
<div class="filters"><label>Cluster <select id="cluster"><option value="">Todos</option></select></label><label>Motivo <select id="reason"><option value="">Todos</option></select></label><button id="reset" type="button">Limpar filtros</button></div></header>
<main><div id="summary"></div><section id="grid"></section></main><script>
const frames = {payload}; const labels = {labels}; const canDelete = {str(allow_delete).lower()}; const cluster = document.querySelector('#cluster'); const reason = document.querySelector('#reason'); const grid = document.querySelector('#grid'); const summary = document.querySelector('#summary');
function group(f) {{ return `${{f.video}} · ${{f.cluster ?? '—'}}`; }}
function populate(select, values, label = value => value) {{ [...new Set(values.filter(v => v !== null && v !== undefined && v !== ''))].sort((a, b) => String(a).localeCompare(String(b), undefined, {{numeric:true}})).forEach(v => {{ const o=document.createElement('option'); o.value=v; o.textContent=label(v); select.append(o); }}); }}
populate(cluster, frames.map(group)); populate(reason, frames.flatMap(f => f.reason.split(';').filter(Boolean)), value => labels[value] || value);
async function removeFrame(f, card) {{ if (!confirm('Excluir este frame da curadoria? Esta ação remove o JPG e o manifesto.')) return; const response=await fetch(`/api/frames/${{encodeURIComponent(f.id)}}`, {{method:'DELETE'}}); if (!response.ok) {{ alert((await response.json()).error || 'Não foi possível excluir o frame.'); return; }} frames.splice(frames.indexOf(f), 1); card.remove(); render(); }}
function render() {{ const filtered=frames.filter(f => (!cluster.value || group(f)===cluster.value) && (!reason.value || f.reason.split(';').includes(reason.value))); summary.textContent=`${{filtered.length}} de ${{frames.length}} frames exibidos`; grid.replaceChildren(...filtered.map(f => {{ const card=document.createElement('article'); const image=document.createElement('img'); image.src=f.image; image.loading='lazy'; image.alt=`Frame em ${{Number(f.timestamp).toFixed(2)}} segundos`; const details=document.createElement('div'); details.className='details'; [`Vídeo: ${{f.video}}`, `Tempo: ${{Number(f.timestamp).toFixed(2)}} s`, `Grupo visual do vídeo: ${{f.cluster ?? '—'}}`].forEach(t => {{ const line=document.createElement('div'); line.textContent=t; details.append(line); }}); const motives=document.createElement('div'); motives.className='motives'; f.reason.split(';').filter(Boolean).forEach(code => {{ const badge=document.createElement('span'); badge.className='badge'; badge.textContent=labels[code] || code; motives.append(badge); }}); details.append(motives); if (canDelete) {{ const button=document.createElement('button'); button.className='delete'; button.textContent='Excluir frame'; button.addEventListener('click', () => removeFrame(f, card)); details.append(button); }} card.append(image, details); return card; }})); }}
[cluster, reason].forEach(e => e.addEventListener('input', render)); document.querySelector('#reset').addEventListener('click', () => {{ cluster.value=''; reason.value=''; render(); }}); render();
</script></body></html>"""


def build_review(dataset_dir, output_dir=None, allow_delete=False):
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
    index_path.write_text(_page_html(frames, allow_delete), encoding="utf-8")
    return {"frames": len(frames), "review": str(index_path)}


def delete_frame(dataset_dir, frame_name):
    """Exclui um frame do disco e do manifesto da curadoria."""
    dataset_dir = Path(dataset_dir).resolve()
    if Path(frame_name).name != frame_name:
        raise ValueError("Nome de frame inválido.")
    manifest_path = dataset_dir / "manifests" / "selections.csv"
    manifest = pd.read_csv(manifest_path)
    matches = manifest[manifest["output_path"].map(lambda path: Path(path).name == frame_name)]
    if len(matches) != 1:
        raise FileNotFoundError("Frame não encontrado no manifesto.")
    frame_path = Path(matches.iloc[0]["output_path"]).resolve()
    if dataset_dir / "frames" not in frame_path.parents:
        raise ValueError("O frame está fora da pasta permitida.")
    frame_path.unlink()
    manifest.drop(matches.index).to_csv(manifest_path, index=False)
    stats_path = dataset_dir / "manifests" / "dataset_stats.json"
    if stats_path.exists() and "video_id" in manifest.columns:
        stats = json.loads(stats_path.read_text(encoding="utf-8"))
        counts = manifest["video_id"].value_counts().to_dict()
        for video in stats.get("per_video", []):
            video["frames_selected"] = int(counts.get(video.get("video_id"), 0))
        stats.setdefault("totals", {})["frames_selected"] = len(manifest)
        stats_path.write_text(json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")
    return len(manifest) - 1


def serve_review(dataset_dir, host="127.0.0.1", port=8765):
    """Serve a revisão localmente e habilita a exclusão manual de frames."""
    dataset_dir = Path(dataset_dir).resolve()
    build_review(dataset_dir, allow_delete=True)

    class ReviewHandler(SimpleHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, directory=str(dataset_dir), **kwargs)

        def do_GET(self):
            if self.path == "/":
                self.path = "/review/index.html"
            return super().do_GET()

        def do_DELETE(self):
            if not self.path.startswith("/api/frames/"):
                self.send_error(404)
                return
            try:
                remaining = delete_frame(dataset_dir, unquote(self.path.removeprefix("/api/frames/")))
                body = json.dumps({"remaining": remaining}).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)
            except (FileNotFoundError, ValueError) as exc:
                body = json.dumps({"error": str(exc)}).encode()
                self.send_response(404)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(body)))
                self.end_headers()
                self.wfile.write(body)

    server = ThreadingHTTPServer((host, port), ReviewHandler)
    print(f"Revisão com exclusão: http://{host}:{port}")
    server.serve_forever()
