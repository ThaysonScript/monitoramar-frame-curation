from monitoramar_curator.compare import _merge, METHOD_OVERRIDES

def test_merge_overrides_nested_keys_only():
    base = {"redundancy": {"enabled": True, "threshold": 8}, "sampling": {"target_fps": 2.0}}
    merged = _merge(base, {"redundancy": {"enabled": False}})
    assert merged["redundancy"]["enabled"] is False
    assert merged["redundancy"]["threshold"] == 8
    assert merged["sampling"]["target_fps"] == 2.0
    # não deve alterar o dict original
    assert base["redundancy"]["enabled"] is True

def test_all_methods_defined_and_progressive():
    assert set(METHOD_OVERRIDES.keys()) == {
        "A_fixed_sampling", "B_temporal_similarity", "C_visual_diversity", "D_task_aware"
    }
    # cada método deve ligar estritamente mais estágios que o anterior
    a, b, c, d = (METHOD_OVERRIDES[k] for k in
                  ["A_fixed_sampling", "B_temporal_similarity", "C_visual_diversity", "D_task_aware"])
    assert a["redundancy"]["enabled"] is False
    assert b["redundancy"]["enabled"] is True and b["clustering"]["enabled"] is False
    assert c["clustering"]["enabled"] is True and c["task_aware"]["enabled"] is False
    assert d["task_aware"]["enabled"] is True
