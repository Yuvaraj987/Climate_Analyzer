from app.services.hazard_service import _runs


def test_three_consecutive_days():
    assert _runs([False, True, True, True, False], 3) == [(1, 3)]


def test_short_run_is_not_event():
    assert _runs([True, True, False], 3) == []


def test_two_separate_events():
    assert _runs([True, True, True, False, True, True, True], 3) == [(0, 2), (4, 6)]
