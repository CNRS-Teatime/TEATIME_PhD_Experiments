import argparse

import thesaurusCreator, thesaurusCleaner, graphCreator, dumpImporter

def parse_command_line():
    """
    The function `parse_command_line` is a Python function that uses the `argparse` module to parse
    command line arguments and returns the parsed arguments.
    :return: The function `parse_command_line` returns the parsed command line arguments.
    """
    parser = argparse.ArgumentParser(description='ArangoDB data integration and graph creation from dumps and the openTheso API')

    # Thesaurus configuration json
    parser.add_argument('--thesaurus-config', '--thesaurus-path' ,'-t', type=str, help='The path to the thesaurus fetching configuration file')
    # Graph configuration json
    parser.add_argument('--graph-config', '--graph-path', '-g', type=str, help='The path to the graph creation configuration file')
    # Dump folder path
    parser.add_argument('--dump-folder', '--dump-path', '-d', type=str, help='The path a folder containing an arangoDB Dump as a JSON')

    # Credentials, for the cleanup and dump things
    # I should move that to a .env
    parser.add_argument('--db-address', type=str, help='The URL of the target ArangoDB instance')
    parser.add_argument('--db-name', type=str)
    parser.add_argument('--db-user', type=str)
    parser.add_argument('--db-password', type=str)

    # Cleanup boolean
    parser.add_argument('--cleanup', '-c', type=bool, default=False, help='Whether or not to perform cleanup after creating or populating a collection')

    parser.add_argument('--add-weights-to-coll', '-a', type=str, help='A collection, to whom you want to add default weights')

    return parser.parse_known_args()[0]

def main():
    args = parse_command_line()

    if args.thesaurus_config:
        thesaurusCreator.create_thesaurus_from_config(args.thesaurus_config)

    if args.graph_config:
        graphCreator.create_graph_from_config(args.graph_config)

    if args.db_address and args.db_name and args.db_user and args.db_password:
        if args.add_weights_to_coll:
            thesaurusCreator.add_weights_with_args(args.db_address, args.db_name, args.db_user, args.db_password, args.add_weights_to_coll)

        if args.dump_folder:
            dumpImporter.import_from_dump_main(args.db_address, args.db_name, args.db_user, args.db_password, args.dump_folder)

        if args.cleanup:
            thesaurusCleaner.cleanup_database(args.db_address, args.db_name, args.db_user, args.db_password)



if __name__ == "__main__":
    main()