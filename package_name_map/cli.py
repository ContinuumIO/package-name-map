import argparse
import sys


def _get_parser():
    p = argparse.ArgumentParser(
            description="""
            Creates a name-map database or outputs a json file mapping one ecosystem to another
            """,
            epilog="""
    Run --help on the subcommands like 'name-map mkdb --help' to see the
    options available.
            """,
    )

    subparsers = p.add_subparsers(dest="action_name")
    mkdb = subparsers.add_parser("mkdb", help="Create database of mappings from dictionary file input")
    mkdb.add_argument("input", help="File containing groups of similar packages "
                        "with descriptions")
    mkdb.add_argument("--db-uri", help="uri of database for data to be dumped to",
                        default="sqlite:///package_name_map.db")

    json_ = subparsers.add_parser("json", help="Dump data from a database into a specific "
                                  "reference: other json mapping file")
    json_.add_argument("reference", help="Name of the package index that serves as the "
                       "reference for lookup")
    json_.add_argument("other", help="Name of the package index that serves as the "
                       "list of packages associated with entries from the reference index")
    json_.add_argument("--db-url-or-fn", "-d", help="Database URI or filename of sqlite file to "
                       "load data from.  By default, looks for one file with .db extension locally",
                       dest="db_uri")
    json_.add_argument("--output-name", "-o", help="output filename.  Defaults to "
                       "(reference)-(other).json", default=None)
    return p


def main(args=None):
    p = _get_parser()
    if not args:
        args = sys.argv[1:]
    ns = p.parse_args(args)

    subcommand = ns.action_name
    if subcommand == "mkdb":
        from package_name_map import populate_db
        populate_db.create_db_from_toml(ns.input, ns.db_uri)
    elif subcommand == "json":
        from package_name_map import json_output
        json_output.compile_json_to_file(ns.reference, ns.other, ns.db_uri, ns.output_name)
    else:
        # retrieve subparsers from parser
        subparsers_actions = [
            action for action in p._actions
            if isinstance(action, argparse._SubParsersAction)]
        # there will probably only be one subparser_action,
        # but better save than sorry
        sp_names = []
        for subparsers_action in subparsers_actions:
            # get all subparsers and print help
            for choice, subparser in subparsers_action.choices.items():
                sp_names.append(choice)
        print("Subcommand '{}' was not recognized by name-map.  Available subcommands "
                         "are: {}".format(subcommand, sp_names))
        sys.exit(1)


if __name__ == "__main__":
    main()
