import json

from edh_utils.set_finder.set_finder import read_collection


def write_collection(tmp_path, data: dict) -> str:
    path = tmp_path / "collection.json"
    path.write_text(json.dumps(data))
    return str(path)


def test_single_location_single_set(tmp_path):
    path = write_collection(tmp_path, {"binder": ["lea"]})
    assert read_collection(path) == {"lea": ["binder"]}


def test_single_location_multiple_sets(tmp_path):
    path = write_collection(tmp_path, {"binder": ["lea", "m21"]})
    result = read_collection(path)
    assert result == {"lea": ["binder"], "m21": ["binder"]}


def test_multiple_locations(tmp_path):
    path = write_collection(tmp_path, {"binder": ["lea"], "box": ["m21"]})
    result = read_collection(path)
    assert result == {"lea": ["binder"], "m21": ["box"]}


def test_set_in_multiple_locations(tmp_path):
    path = write_collection(tmp_path, {"binder": ["lea"], "box": ["lea"]})
    result = read_collection(path)
    assert result == {"lea": ["binder", "box"]}


def test_empty_collection(tmp_path):
    path = write_collection(tmp_path, {})
    assert read_collection(path) == {}
