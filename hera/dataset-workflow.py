from hera.workflows import (
    DAG,
    WorkflowTemplate,
    Container,
    Task
)
from hera.shared import global_config
from hera.workflows.models import Toleration, ImagePullPolicy
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
            image_pull_policy=ImagePullPolicy.if_not_present
        )

        with DAG(name="dataset-dag") as dag:
            task_import_dump = Task(
                name="import-dump",
                template=importer
            )

            task_import_theso = Task(
                name="import-theso",
                template=importer
            )

            task_create_graph = Task(
                name="create-graph",
                template=importer
            )

            [task_import_theso, task_import_dump] >> task_create_graph

        wt.create()
