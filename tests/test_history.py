from dataclasses import replace

from clickpe_pim.monitor.history import Snapshot, detect_changes


def test_first_run_is_baseline(make_observation):
    item = make_observation()
    snap = Snapshot("r1", item.extracted_at, {}, [item], {"s1"}, True, True, "1", "mapping1")
    assert detect_changes(None, snap, {}) == []


def test_failed_source_does_not_remove_field(make_observation):
    item = make_observation()
    old = Snapshot("r1", item.extracted_at, {}, [item], {"s1"}, True, True, "1", "mapping1")
    new = replace(old, run_id="r2", observations=[], healthy_sources=set(), catalogue_complete=False)
    assert detect_changes(old, new, {}) == []


def test_semantic_change_is_detected(make_observation):
    from clickpe_pim.contracts import Value
    item = make_observation()
    old = Snapshot("r1", item.extracted_at, {}, [item], {"s1"}, True, True, "1", "mapping1")
    changed = make_observation(run_id="r2", observation_id="o2", value=Value(kind="money", upper="300000", unit="INR", qualifier="up_to"))
    new = replace(old, run_id="r2", observations=[changed])
    assert [event.type for event in detect_changes(old, new, {})] == ["VALUE_CHANGED"]

