import pandas as pd

from monitoramar_curator.review import build_review


def test_build_review_creates_local_page(tmp_path):
    dataset = tmp_path / "curated"
    frames = dataset / "frames"
    manifest_dir = dataset / "manifests"
    frames.mkdir(parents=True)
    manifest_dir.mkdir()
    (frames / "frame.jpg").write_bytes(b"placeholder")
    pd.DataFrame([{
        "timestamp_seconds": 3.5, "output_path": str(frames / "frame.jpg"), "cluster_id": 2,
        "selection_reason": "cluster_representative",
        "frame_index": 105, "video_id": "video-a",
    }]).to_csv(manifest_dir / "selections.csv", index=False)

    result = build_review(dataset)
    page = dataset / "review" / "index.html"

    assert result["frames"] == 1
    assert result["review"] == str(page)
    text = page.read_text(encoding="utf-8")
    assert "../frames/frame.jpg" in text.replace("\\", "/")
    assert "Representa o grupo" in text
