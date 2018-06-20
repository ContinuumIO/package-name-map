# import toml

from sqlalchemy import Table, Column, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from six import string_types

Base = declarative_base()


def ensure_list(arg):
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
def create_repo_class(table_name, association_table):
    NewClass = type(table_name.capitalize(), (Base,), {
        "__tablename__": table_name,
        "id": Column(Integer, primary_key=True, autoincrement=True),
        "package_name": Column(String(100)),
        "description": relationship("Description",
                                    secondary=association_table,
                                    back_populates=table_name)
    })
    return NewClass


def create_description_class(other_columns, association_table):
    """Each description is unique.  There is a many-many relationship between
    descriptions and package names.  One description may have many
    packages associated with it.  One package may have many descriptions."""
    other_cols = {col: relationship(col.capitalize(),
                                    secondary=association_table,
                                    back_populates="description")
                  for col in other_columns}
    other_cols.update({
        "__tablename__": "description",
        "id": Column(Integer, primary_key=True, autoincrement=True),
        "description": Column(String(400))
    })
    return type("Description", (Base,), other_cols)


def create_database_schema(loaded_records):
    other_columns = _get_keys(loaded_records)
    association_args = ['association', Base.metadata,
                        Column("description_id", Integer, ForeignKey("description.id"))] + [
        Column('%s_id' % col, Integer, ForeignKey('%s.id' % col))
        for col in other_columns
    ]
    association_table = Table(*association_args)
    col_classes = {col: create_repo_class(col, association_table)
                   for col in other_columns}
    Description = create_description_class(other_columns, association_table)
    return Description, col_classes


if __name__ == "__main__":
    loaded_records = [{"description": "lalalala",
                       "conda": "python-graphviz",
                       "pypi": "graphviz"},
                      {"description": "test2",
                       "conda": ['abc', '123'],
                       "debian": "libabc"}]
    from sqlalchemy import create_engine
    # engine = create_engine('sqlite:///:memory:', echo=True)
    engine = create_engine('sqlite:///package_name_map.db', echo=True)
    Description, col_classes = create_database_schema(loaded_records)

    Base.metadata.create_all(engine)
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
                values = ensure_list(values)
            for value in values:
                # look up package name in existing table.  If it exists, just
                #     add this description to it.
                pkg_record = session.query(col_classes[key]).filter_by(
                    package_name=value).first()
                if not pkg_record:
                    pkg_record = col_classes[key](package_name=value)
                pkg_record.description.append(description_record)
                session.add(pkg_record)
    session.commit()
