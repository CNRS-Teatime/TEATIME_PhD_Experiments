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
        name="clustering-dag",
        entrypoint="clustering-dag",
        tolerations=[Toleration(
            key="gpu", operator="Exists", effect="PreferNoSchedule")],
    ) as wt:

        clustering = Container( # TODO: Définir les paramètres
            name="cluster-computation",
            image=constants.clustering_image,
            image_pull_policy=ImagePullPolicy.if_not_present
        )

        export = Container(
            # TODO: Définir les paramètres
            name="clustering-results-exporter",
            image=constants.export_image,
            image_pull_policy=ImagePullPolicy.if_not_present
        )

        with DAG(name="clustering-dag") as dag:
            task_compute_clusters = Task(
                name="computer-clusters",
                template=clustering
            )

            task_export_results = Task(
                name="export-clustering-results",
                template=export
            )

            task_compute_clusters >> task_export_results

        wt.create()
