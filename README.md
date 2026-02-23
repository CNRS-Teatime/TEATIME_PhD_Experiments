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

## Opentheso importer

The opentheso importer uses json configuration files and the opentheso REST API to fetch graph data from an opentheso instance, clean it, and store it in a dedicated arangoDB Graph Database.

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

To run the tool simply run the `create-thesaurus.py` python script inside the virtual environment that you set up in the installation section. Having a valid `config.json` in the same directory as the script is **mandatory**.

```bash
python3 create-thesaurus.py
```


## Roadmap

- [x] [Opentheso](https://opentheso.hypotheses.org/introduction) to ArangoDB importer
- [ ] [Aioli](https://www.map.cnrs.fr/fr/recherche/projets/aioli/) to ArangoDB importer
  * How to build edges between annotations ?
  * What granularity for each information inside the annotation ?
  * Should annotations be nodes or subgraphs ? 
- [ ] Visualising ArangoDB graphs with D3Js (D3 frontend + Backend supported by ArangoDB)

## License
This work is licenced under GNU GPL v3.0

## Project status
Ongoing
