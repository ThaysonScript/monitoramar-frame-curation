from monitoramar_curator.people import create_people_counter, NullPeopleCounter

def test_disabled_returns_null_counter():
    counter = create_people_counter({"enabled": False})
    assert isinstance(counter, NullPeopleCounter)
    assert counter.count([1, 2, 3]) == [None, None, None]

def test_missing_config_defaults_to_disabled():
    counter = create_people_counter(None)
    assert isinstance(counter, NullPeopleCounter)

def test_enabled_without_ultralytics_falls_back_gracefully():
    # Em ambientes sem ultralytics instalado, não deve levantar exceção.
    counter = create_people_counter({"enabled": True, "backend": "yolov8"})
    assert counter.count([1, 2]) == [None, None]
