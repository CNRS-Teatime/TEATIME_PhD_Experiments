import types

constants = types.SimpleNamespace(
    arango_db_image = "arangodb/enterprise:3.12.6.1",
    front_end_image = "arangodb/enterprise:3.12.6.1", # FIXME: replace with the real image when it's ready
    importer_image = "harbor.pagoda.liris.cnrs.fr/sunlight/arango-importer",
    clustering_image = "arangodb/enterprise:3.12.6.1", # FIXME: replace with the real image when it's ready
    export_image = "arangodb/enterprise:3.12.6.1", # FIXME: replace with the real image when it's ready
    database_name = "TEATIME-Exp",
    database_user = "root",
    arango_name = "arango-db",
    service_port = 8529,
    config_map_name = "configs",
    thesaurus_config = "thesaurus-config.json",
    graph_config = "graph-config.json"
)