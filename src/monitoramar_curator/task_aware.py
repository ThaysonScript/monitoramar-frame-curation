def compute_event_scores(records, novelty_weight=1.0, people_change_weight=2.0):
    previous = None
    for r in records:
        novelty_component = novelty_weight * r.embedding_novelty
        people_change_component = 0.0
        people_count_change = None
        if r.people_count is not None and previous is not None:
            people_count_change = abs(r.people_count - previous)
            people_change_component = people_change_weight * min(people_count_change / 5.0, 1.0)
        r.event_novelty_component = float(novelty_component)
        r.event_people_change_component = float(people_change_component)
        r.people_count_change = people_count_change
        r.event_score = min(float(novelty_component + people_change_component), 1.0)
        if r.people_count is not None:
            previous = r.people_count

def add_reason(record, reason):
    parts = [x for x in record.selection_reason.split(";") if x]
    if reason not in parts:
        parts.append(reason)
    record.selection_reason = ";".join(parts)
