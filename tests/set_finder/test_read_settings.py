from edh_utils.set_finder.set_finder import read_settings


def write_settings(tmp_path, content: str) -> str:
    path = tmp_path / "settings.toml"
    path.write_text(content)
    return str(path)


def test_all_fields(tmp_path):
    path = write_settings(tmp_path, """
hide = ["lea", "m21"]
collection = "path/to/collection.json"
format = "csv"
""")
    result = read_settings(path)
    assert result["hide"] == ["lea", "m21"]
    assert result["collection"] == "path/to/collection.json"
    assert result["format"] == "csv"


def test_partial_fields(tmp_path):
    path = write_settings(tmp_path, 'format = "json"\n')
    result = read_settings(path)
    assert result["format"] == "json"
    assert "hide" not in result
    assert "collection" not in result


def test_empty_file(tmp_path):
    path = write_settings(tmp_path, "")
    assert read_settings(path) == {}
