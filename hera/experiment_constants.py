import types

constants = types.SimpleNamespace(
    arango_db_image = "arangodb/enterprise:3.12.6.1",
    front_end_image = "arangodb/enterprise:3.12.6.1", # FIXME: replace with the real image when it's ready
    importer_image = "arangodb/enterprise:3.12.6.1", # FIXME: replace with the real image when it's ready
    clustering_image = "arangodb/enterprise:3.12.6.1", # FIXME: replace with the real image when it's ready
    export_image = "arangodb/enterprise:3.12.6.1" # FIXME: replace with the real image when it's ready
)