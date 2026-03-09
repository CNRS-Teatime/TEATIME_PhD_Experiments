# TEATIME thesis experiments

Welcome, this repository contains experiments, built inside the TEATIME project.
The data wont be available in this repository and has to be provided by the user.

***

## Description
This project is composed of a few D3Js force graphs implementations and  arangoDB connectors writen in python for data related to Notre-Dame de Paris. (notably the thesaurus and annotation data)

## Installation

Python 3.14 is required to run the scripts (no other versions have been tested but they might work)

We recommend using a virtual python environment through the [venv](https://docs.python.org/3/library/venv.html) python package. Simply replace `{foldername}` in the following command with the desired environment name (for ex Debug).
```bash
python3 -m venv {foldername}
```

Then activate the virtual environment :

### Unix/MacOS

```bash
source {foldername}/bin/activate
```

### Windows

```bash
./{foldername}/bin/activate
```

Finaly you can install the dependencies listed in requirements.txt via this command

```bash
python3 -m pip install -r requirements.txt
```

More info here : https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/

## Usage
Here is a list of all the available options

| Argument           | Description                                                                       | Example                                   |
|--------------------|-----------------------------------------------------------------------------------|-------------------------------------------|
| --thesaurus-config | The path to the thesaurus fetching configuration file                             | --thesaurus-config config/thesarauri.json |
| --graph-config     | The path to the graph creation configuration file                                 | --graph-config config/graphs.json         |
| --cleanup          | A boolean definining if a full db cleanup needs to be perfomed (default is false) | --cleanup True                            |

And the dump import specific option, which all needs to be set for the dump import to work correctly (as of now) but are not needed for the other types of import :

| Argument      | Description                                                                       | Example                                   |
|---------------|-----------------------------------------------------------------------------------|-------------------------------------------|
| --dump-path   | The path to the graph creation configuration file                                 | --dump-path path/to/dump                  |
| --db-address  | The url to the desired arango instance (dump specific)                            | --db-adress http://localhost:8529         |
| --db-name     | The name of the database inside the arango instance (dump specific)               | --db-name NAME                            |
| --db-user     | Your username (dump specific)                                                     | --db-user USERNAME                        |
| --db-password | Your password (dump specific)                                                     | --db-password 1234                        |


example usage : 
```bash
python3 main.py --graph-config [path-to-config]
```

```bash
python3 main.py --thesaurus-config [path-to-config] --cleanup True
```

```bash
python3 main.py --dump-path path/to/dump --db-address http://localhost:8529 --db-name NAME --db-user USERNAME --db-password 1234
```

## Feature specific information

### Opentheso importer

The opentheso importer uses json configuration files and the opentheso REST API to fetch graph data from an opentheso instance, clean it, 
and store it in a dedicated arangoDB Graph Database.
It is used with the `--thesaurus-config` option.

A config file is composed as follows (boilerplate information inside the example, it wont work as is) : 

```json
{
    "credentials": {
        "host" : "http://localhost:8529", 
        "username" : "user",
        "password" : "password", 
        "database" : "DATABASENAME"
    },
    "thesauri" : [
        {
            "name" : "PREFERED NAME 1",

            "source" : "https://your.web.link/openapi/v1/graph/getData?dThesoConcept=ID",
            "type" : "graph" 
        },
        {
            "name" : "PREFERED NAME 2",
            "source" : "https://your.web.link/openapi/v1/thesaurus/ID",
            "type" : "raw" 
        }
    ]
}
```

The JSON Schema is available in `theso-config-schema.json`. All config files given to the tool are validated against it.
The `credentials` section refers to the url and login of the desired ArangoDB instance as well as the database name to use inside of this instance. While the `thesauri` section is a list of graphs to import to ArandoDB, consisting of the associated *GET* Request in the `source` field, a name and the type of import that the Request will return. There are two types of import that are supported (unsupported types are ignored) :

- `'raw'` : These are thesaurus that are not pre-formated as a graph by the opentheso instance. They usually contain much more information and are faster to fetch from the server. This is the recommended format. In opentheso, they are the requests that end with `/thesaurus/ID`
- `'graph'` : These are the pre-formated graphs that represent a thesaurus. They are missing some information. In opentheso, they are the requests that end with `/graph/getData?dThesoConcept=ID`

The database will be created if it doesnt exist if you have the default ArangoDB ROOT username and password, otherwise you will have to use an ==already existing database==.

> You can use the `config-BOILERPLATE.json` file and replace the values with your own to easily start creating a custom config file.

### Graph maker

The graph maker will initialize ArangoDB graphs based on a configuration file, specifying edge and document collections for each graph.
Its purpose is to increase repoducibility, and reduce human errors during experimentations. It is used
with the `--graph-config option`

A config file is composed as follows (boilerplate information inside the example, it wont work as is) :
```JSON
{
    "credentials": {
        "host" : "http://localhost:8529",
        "username" : "user",
        "password" : "password",
        "database" : "DATABASENAME"
    },
    "graphs" : [
        {
            "name" : "PREFERED NAME 1",
            "relations" : [
                {
                    "edge_collection" : "EDGE COLLECTION NAME",
                    "from_vertex_collections" : [
                        "COLLECTION 1",
                        "COLLECTION 2"
                    ],
                    "to_vertex_collections" : [
                        "COLLECTION 3",
                        "COLLECTION 4"
                    ]
                }
            ]
        },
        {
            "name" : "PREFERED NAME 2",
            "relations" : [
                {
                    "edge_collection" : "EDGE COLLECTION NAME",
                    "from_vertex_collections" : [
                        "COLLECTION 1",
                        "COLLECTION 2"
                    ],
                    "to_vertex_collections" : [
                        "COLLECTION 3",
                        "COLLECTION 4"
                    ]
                }
            ]
        }
    ]
}
```

The JSON Schema is available in `graph-config-schema.json`. All config files given to the tool are validated against it.
The credentials section is identical to the one in the thesaurus configuration file. Each graph entry then asks for a name,
a singular edge collection and two list of incoming and outgoing collections (which can be identical). The collections must already
exist in the database, otherwise the graph will not be created.

You can use `config-graph-BOILERPLATE.json` as a base to create your own configuration files.

### Dump importer

The dump impoter will populate a database using an arangoDB dump, contained in a given folder. A dump is simply a collection
of JSON files, in the arangoDB format, which can be obtained by fetching an arangoDB database.
Its primary use is saving Database states for later use.

It is used with the `--dump-path` options and its associated arguments (see usage).

## Roadmap

- [x] [Opentheso](https://opentheso.hypotheses.org/introduction) to ArangoDB importer
- [x] [Aioli](https://www.map.cnrs.fr/fr/recherche/projets/aioli/) to ArangoDB importer
  * It is covered by the dump importer, as Aiolï's API is not adapted to our use case
- [ ] [Semantic distance](https://github.com/VCityTeam/VCity/blob/master/Projects/Phd_Marwan_Ait_Addi_Russier/Recherches/Distance%20thesaurique.md) experiments
- [ ] NLP Experiments
- [ ] Visualizing ArangoDB graphs with D3Js (D3 frontend + Backend supported by ArangoDB)

## License
This work is licenced under GNU GPL v3.0

## Project status
Ongoing
