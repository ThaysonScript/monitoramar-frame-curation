import pandas as pd
from monitoramar_curator.metrics import compute_dataset_metrics, format_report

def _stats(raw=1000, sampled=200, candidates=100):
    return {"totals": {"raw_frame_count": raw, "frames_sampled": sampled,
                        "frames_after_redundancy": candidates, "frames_selected": 0}}

def test_reduction_and_costs():
    manifest = pd.DataFrame({
        "cluster_id": [0, 0, 1, 2],
        "selection_reason": ["cluster_representative", "cluster_representative;critical_event",
                              "cluster_representative", "critical_event"],
        "people_count": [1, 2, None, 3],
    })
    metrics = compute_dataset_metrics(manifest, _stats(), minutes_per_frame=1.0)
    assert metrics["frames_selected"] == 4
    assert metrics["reduction_vs_raw_pct"] == 99.6
    assert metrics["clusters_covered"] == 3
    assert metrics["critical_event_frames"] == 2
    assert metrics["people_count_buckets_selected"] == 3
    assert metrics["estimated_annotation_hours_selected"] == round(4 / 60, 2)
    assert "Frames selecionados" in format_report(metrics)

def test_empty_manifest_does_not_crash():
    metrics = compute_dataset_metrics(pd.DataFrame(), _stats(raw=0, sampled=0, candidates=0))
    assert metrics["frames_selected"] == 0
    assert metrics["reduction_vs_raw_pct"] is None
    assert metrics["clusters_covered"] is None
