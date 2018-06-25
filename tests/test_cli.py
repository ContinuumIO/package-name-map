import os

from package_name_map import cli

test_data_folder = os.path.relpath(os.path.join(os.path.dirname(__file__), "data"), os.getcwd())


def test_build_db():
    cli.main(["mkdb", os.path.join(test_data_folder, "example.toml")])
    assert os.path.isfile("package_name_map.db")
    os.remove("package_name_map.db")


def test_read_db_for_json():
    cli.main(["json", "pypi", "conda", "-d", os.path.join(test_data_folder,
                                                          "package_name_map.db")])
    assert os.path.isfile("pypi-conda.json")
    os.remove("pypi-conda.json")
