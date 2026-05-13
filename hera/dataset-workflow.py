from hera.events.models.io.k8s.api.core.v1 import Volume
from hera.workflows import (
    DAG,
    WorkflowTemplate,
    Container,
    Task,
    SecretEnv,
    Env,
    Parameter,
    ConfigMapVolume
)
from hera.shared import global_config
from hera.workflows.models import Toleration, ImagePullPolicy, KeyToPath
from experiment_constants import constants
import os

if __name__ == "__main__":

    global_config.host = f'https://{os.environ.get("ARGO_SERVER")}'
    global_config.token = os.environ.get("ARGO_TOKEN")
    global_config.namespace = os.environ.get("ARGO_NAMESPACE", "argo")

    # TODO: Definir si l'on veut vraiment séparer chaque étape
    with WorkflowTemplate(
        name="dataset-dag",
        entrypoint="dataset-dag",
        tolerations=[Toleration(
            key="gpu", operator="Exists", effect="PreferNoSchedule")],
    ) as wt:

        importer = Container( # TODO: Définir les paramètres
            name="importer",
            image=constants.importer_image,
            image_pull_policy=ImagePullPolicy.if_not_present,
            inputs=[
                Parameter(name="thesaurus-config", default=''),
                Parameter(name="graph-config", default=''),
                Parameter(name="dump-path", default='')
            ],
            env=[
                Env(name="DB_NAME", value=constants.database_name),
                Env(name="DB_USER", value=constants.database_user),
                Env(name="DB_ADDRESS", value=f"http://{constants.arango_name}-service:{constants.service_port}"),
                Env(name="THESO_CONFIG", value="{{inputs.parameters.thesaurus-config}}"), #This  is ok because the empty string is catched by the entrypoint.sh
                Env(name="GRAPH_CONFIG", value="{{inputs.parameters.graph-config}}"),
                Env(name="DUMP_PATH", value="{{inputs.parameters.dump-path}}"),
                SecretEnv(secret_name="arango-secret", name="ARANGO_ROOT_PASSWORD", secret_key="arango-password")
            ],
            volumes=[
                ConfigMapVolume(mount_path="/config", name=constants.config_map_name, items=[KeyToPath(key = constants.thesaurus_config, path=constants.thesaurus_config), KeyToPath(key = constants.graph_config, path=constants.graph_config), KeyToPath(key="graph-config-schema.json", path="graph-config-schema.json"), KeyToPath(key="theso-config-schema.json", path="theso-config-schema.json")])
            ]
        )

        with DAG(name="dataset-dag") as dag:
            """task_import_dump = Task(
                name="import-dump",
                template=importer
            )"""

            task_import_theso = Task(
                name="import-theso",
                template=importer,
                arguments={
                    "thesaurus-config" : f"/config/{constants.thesaurus_config}"
                }
            )

            task_create_graph = Task(
                name="create-graph",
                template=importer,
                arguments={
                    "graph-config": f"/config/{constants.graph_config}"
                }
            )

            task_import_theso >> task_create_graph

        wt.create()
