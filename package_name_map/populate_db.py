import os

from sqlalchemy import Table, Column, Integer, ForeignKey, String, create_engine
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from six import string_types

_Base = declarative_base()


def _ensure_list(arg):
    if (isinstance(arg, string_types) or not hasattr(arg, '__iter__')):
        if arg:
            arg = [arg]
        else:
            arg = []
    return arg


def load_toml(toml_fn):
    pass


def _get_keys(loaded_records):
    """Each key represents a table.  The set of all keys is the set of tables
    that must be created and associated."""
    keys = set()
    for record in loaded_records:
        keys.update(set(record.keys()))
    keys.remove("description")
    return keys


# dynamic class creation inspired by
#    http://jelly.codes/articles/python-dynamically-creating-classes/
def create_repo_class(table_name):
    association_table = Table('assoc_%s' % table_name, _Base.metadata,
                              Column("description_id", Integer, ForeignKey("description.id")),
                              Column("%s_id" % table_name, Integer, ForeignKey("%s.id" % table_name)))
    NewClass = type(table_name.capitalize(), (_Base,), {
        "__tablename__": table_name,
        "id": Column(Integer, primary_key=True, autoincrement=True),
        "package_name": Column(String(100)),
        "descriptions": relationship("Description",
                                     secondary=association_table,
                                     backref=table_name)
    })
    return NewClass


def create_description_class():
    """Each description is unique.  There is a many-many relationship between
    descriptions and package names.  One description may have many
    packages associated with it.  One package may have many descriptions."""
    return type("Description", (_Base,), {
        "__tablename__": "description",
        "id": Column(Integer, primary_key=True, autoincrement=True),
        "description": Column(String(400))
    })


def create_database_schema(column_names):
    col_classes = {col: create_repo_class(col) for col in column_names}
    Description = create_description_class()
    return Description, col_classes


# easy enough to support other input formats.  We'll do that if it becomes necessary or desirable.
def create_db_from_toml(toml_filename, db_uri):
    # imports done locally to make dependencies optional based on how users want to do their inputs
    import toml
    loaded_records = toml.load(toml_filename)["package"]
    return create_db_from_dict(loaded_records, db_uri)


def create_db_from_dict(loaded_records, db_uri='package_name_map.db'):
    if os.path.isfile(db_uri) or ":" not in db_uri:
        db_uri = "sqlite:///" + db_uri
    engine = create_engine(db_uri)
    columns = _get_keys(loaded_records)
    Description, col_classes = create_database_schema(columns)

    _Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()

    for record in loaded_records:
        description_record = session.query(Description).filter_by(
            description=record['description']).first()
        if not description_record:
            description_record = Description(description=record['description'])
            session.add(description_record)
        for key, values in record.items():
            if key == "description":
                continue
            else:
                values = _ensure_list(values)
            for value in values:
                # look up package name in existing table.  If it exists, just
                #     add this description to it.
                pkg_record = session.query(col_classes[key]).filter_by(
                    package_name=value).first()
                if not pkg_record:
                    pkg_record = col_classes[key](package_name=value)
                pkg_record.descriptions.append(description_record)
                session.add(pkg_record)
    session.commit()


if __name__ == "__main__":
    loaded_records = [{"description": "graphviz python interface",
                       "conda": "python-graphviz",
                       "pypi": "graphviz",
                       "debian": ["python-graphviz", "python3-graphviz"]},
                      {"description": "Graphviz shared libraries",
                       "conda": 'graphviz',
                       "debian": "graphviz"},
                      {"description": "Graphviz development stuff (headers)",
                       "conda": 'graphviz',
                       "debian": ["graphviz-dev", "libgraphviz-dev"]},
    ]
    create_db_from_dict(loaded_records)
