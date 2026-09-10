def compute_event_scores(records, novelty_weight=1.0, people_change_weight=2.0):
    previous = None
    for r in records:
        score = novelty_weight * r.embedding_novelty
        if r.people_count is not None and previous is not None:
            score += people_change_weight * min(abs(r.people_count - previous) / 5.0, 1.0)
        r.event_score = min(float(score), 1.0)
        if r.people_count is not None:
            previous = r.people_count

def add_reason(record, reason):
    parts = [x for x in record.selection_reason.split(";") if x]
    if reason not in parts:
        parts.append(reason)
    record.selection_reason = ";".join(parts)
