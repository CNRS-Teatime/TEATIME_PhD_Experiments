from tempfile import template

from hera.workflows import (
    DAG,
    WorkflowTemplate,
    script,
    Task
)
from hera.shared import global_config
from hera.workflows.models import Toleration, Arguments, Parameter, TemplateRef
import os


@script()
def compute_visualisation_configurations(nb_clusters: list[int]):
    """
    Computes the configurations for the visualisation experiments
    This function takes in a list: nb_clusters.
    It generates configurations for the visualisation experiments based on the provided list.
    It returns a list of tuples, where each tuple contains the configuration for a specific combination of weight and number of clusters.
    """
    from itertools import product
    import json
    import sys

    narrower_list: list[int] = [0, 1, 2, 3]
    broader_list: list[int] = [0, 1, 2, 3]
    related_list: list[int] = [1, 2, 3, 4, 5]
    close_match_list: list[int] = [0, 0.5, 1, 1.5]
    exact_match_list: list[int] = [0, 1, 2, 3]

    configurations = list(product(
        narrower_list,
        broader_list,
        related_list,
        close_match_list,
        exact_match_list,
        nb_clusters
    ))

    result = [
        {
            "narrower": narrower,
            "broader": broader,
            "related": related,
            "close_match": close_match,
            "exact_match": exact_match,
            "nb_cluster": nb_cluster,
            "key": f"n{narrower}-b{broader}-r{related}-c{close_match}-e{exact_match}-cl{nb_cluster}"
        }
        for narrower, broader, related, close_match, exact_match, nb_cluster in configurations
    ]

    json.dump(result, sys.stdout)


if __name__ == "__main__":
    global_config.host = f'https://{os.environ.get("ARGO_SERVER")}'
    global_config.token = os.environ.get("ARGO_TOKEN")
    global_config.namespace = os.environ.get("ARGO_NAMESPACE", "argo")

    with WorkflowTemplate(
            name="teatime-experiment-dag",
            entrypoint="teatime-experiment-dag",
            tolerations=[Toleration(
                key="gpu", operator="Exists", effect="PreferNoSchedule")],
            arguments=Arguments(parameters=[
                Parameter(name="nb_clusters", description="List of number of clusters", default="[5,10,20]")
            ]),

    ) as wt:
        with DAG(name="teatime-experiment-dag"):
            task_compute_visualisation_configurations = compute_visualisation_configurations(
                arguments={"nb_clusters": "{{workflow.parameters.nb_clusters}}"
                           }
            )

            task_environment = Task(
                name="environment",
                template_ref=TemplateRef(
                    name="environment-dag", template="environment-dag"
                )
            )

            task_dataset = Task(
                name="dataset",
                template_ref=TemplateRef(
                    name="dataset-dag", template="dataset-dag"
                )
            )

            task_clustering = Task(
                name="clustering",
                template_ref=TemplateRef(
                    name="clustering-dag", template="clustering-dag"
                )
            )

            task_environment >> task_dataset >> task_compute_visualisation_configurations >> task_clustering

        wt.create()
