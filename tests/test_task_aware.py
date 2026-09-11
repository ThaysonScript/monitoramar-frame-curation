from monitoramar_curator.models import FrameRecord
from monitoramar_curator.task_aware import compute_event_scores


def test_event_score_records_its_components():
    records = [
        FrameRecord("v", "source", 0, 0.0, embedding_novelty=0.1, people_count=1),
        FrameRecord("v", "source", 1, 1.0, embedding_novelty=0.2, people_count=4),
    ]

    compute_event_scores(records, novelty_weight=1.0, people_change_weight=2.0)

    assert records[0].event_novelty_component == 0.1
    assert records[0].event_people_change_component == 0.0
    assert records[0].people_count_change is None
    assert records[1].event_novelty_component == 0.2
    assert records[1].people_count_change == 3
    assert records[1].event_people_change_component == 1.2
    assert records[1].event_score == 1.0
