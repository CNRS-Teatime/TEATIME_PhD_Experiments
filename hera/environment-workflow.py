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

    # TODO: Créer un config map les identifiants de ArangoDB (pour éviter qu'ils soient en clair dans les manifestes)
    with WorkflowTemplate(
        name="environment-dag",
        entrypoint="environment-dag",
        tolerations=[Toleration(
            key="gpu", operator="Exists", effect="PreferNoSchedule")],
    ) as wt:

        arango_db = Container(
            name="arango-db",
            image=constants.arango_db_image,
            image_pull_policy=ImagePullPolicy.if_not_present,
            env={"ARANGO_NO_AUTH": True}, #FIXME : Change for authentified use ?
            daemon=True
        )

        frontend = Container(
            name="frontend",
            image=constants.front_end_image,
            image_pull_policy=ImagePullPolicy.if_not_present,
            daemon=True
        )

        with DAG(name="environment-dag") as dag:

            task_arango_db = Task(
                name="arango-db",
                template=arango_db
            )

            task_frontend = Task(
                name="frontend",
                template=frontend
            )

            task_arango_db >> task_frontend

        wt.create()
