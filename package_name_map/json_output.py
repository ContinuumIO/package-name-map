import os as _os
import json as _json
from sqlalchemy.ext.automap import automap_base as _automap_base
from sqlalchemy.orm import Session as _Session
from sqlalchemy import create_engine as _create_engine

Base = _automap_base()


def _prepare_engine_and_session(db_uri):
    if _os.path.isfile(db_uri) or ":" not in db_uri:
        db_uri = "sqlite:///" + db_uri
    engine = _create_engine(db_uri)
    # reflect the tables (don't manually redefine scheme)
    if "description" not in Base.classes:
        Base.prepare(engine, reflect=True)
    session = _Session(engine)
    return session


def _load_database(ref_column, other_column):
    # mapped classes are now created with names by default
    # matching that of the table name.
    Description = getattr(Base.classes, "description")
    Ref = getattr(Base.classes, ref_column)
    Other = getattr(Base.classes, other_column)
    return Description, Ref, Other


def find_db_file(folder=_os.getcwd()):
    from glob import glob
    db_files = glob("*.db")
    if len(db_files) == 0:
        raise ValueError("No database file specifed, and no .db file found in cwd.  Please specify "
                         "the database to read from.")
    elif len(db_files) > 1:
        raise ValueError("More than one .db file found.  I don't know which one to use.  Please "
                         "specify the database to read from as a CLI or function argument.")
    return db_files[0]


def compile_json(ref_column, other_column, db_uri=None):
    if not db_uri:
        db_uri = "sqlite:///" + find_db_file()
    session = _prepare_engine_and_session(db_uri)
    Description, Ref, Other = _load_database(ref_column, other_column)
    # link Ref to Other via their shared description(s)
    # https://stackoverflow.com/a/4780595/1170370
    # session.query(User).join((Group, User.groups)) \
    #      .join((Department, Group.departments))
    q = session.query(Ref, Other, Description) \
               .join((Description, Other.description_collection)) \
               .join((Ref, getattr(Description, Ref.__name__ + "_collection")))

    json_map = {}
    for rec in q:
        ref_name = getattr(rec, ref_column).package_name
        other_name = getattr(rec, other_column).package_name
        description = rec.description.description
        json_map[ref_name] = json_map.get(ref_name, [])
        json_map[ref_name].append(other_name)
        print("{}: {}, {}".format(ref_name, other_name, description))
    return json_map


def compile_json_to_file(ref_column, other_column, db_uri=None, output_filename=None):
    mapped_dict = compile_json(ref_column, other_column, db_uri)
    output_filename = output_filename if output_filename else \
                      "-".join((ref_column, other_column)) + ".json"
    with open(output_filename, 'w') as f:
        _json.dump(mapped_dict, f)


if __name__ == "__main__":
    # lookup map from pypi name to conda equivalent
    print("PyPI to conda")
    compile_json("sqlite:///package_name_map.db", "pypi", "conda")
    print("conda to PyPI")
    compile_json("sqlite:///package_name_map.db", "conda", "pypi")
    print("conda to debian")
    compile_json("sqlite:///package_name_map.db", "conda", "debian")
