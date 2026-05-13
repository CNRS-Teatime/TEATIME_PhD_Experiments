from hera.workflows import (
    DAG,
    WorkflowTemplate,
    Container,
    Task,
    Resource,
    Parameter,
    SecretEnv
)
from hera.shared import global_config
from hera.workflows.models import Toleration, ImagePullPolicy, ContainerPort
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
        def create_service_manifest(metadata_name: str, selector_name: str, port: int,
                                    target_port: int) -> str:
            """
            Creates a Kubernetes service manifest.

            This method creates a Kubernetes service manifest with the specified metadata name,
            selector name, port, and target port. The manifest is returned as a string.

            Args:
                metadata_name (str): The name of the service metadata.
                selector_name (str): The selector name.
                port (int): The service port.
                target_port (int): The target port.
            """
            return ("apiVersion: v1\n"
                    "kind: Service\n"
                    "metadata:\n"
                    f"   name: {metadata_name}\n"
                    "spec:\n"
                    "   selector:\n"
                    f"       app: {selector_name}\n"
                    "   type: ClusterIP\n"
                    "   ports:\n"
                    f"   - port: {port}\n"
                    f"     targetPort: {target_port}\n")


        arango_db = Container(
            name="arango-db",
            image=constants.arango_db_image,
            image_pull_policy=ImagePullPolicy.if_not_present,
            env=[
                SecretEnv(secret_name="arango-secret", name="ARANGO_ROOT_PASSWORD", secret_key="arango-password")
            ],
            ports=[ContainerPort(container_port=constants.service_port, host_port=constants.service_port)],
            daemon=True
        )

        """frontend = Container(
            name="frontend",
            image=constants.front_end_image,
            image_pull_policy=ImagePullPolicy.if_not_present,
            env=[
                SecretEnv(secret_name="arango-secret", name="ARANGO_ROOT_PASSWORD", secret_key="arango-password")
            ],
            daemon=True
        )"""

        arango_db_service_create = Resource(
            name=f"{constants.arango_name}-service",
            inputs=[
                Parameter(name="arango-name")
            ],
            action="create",
            manifest=create_service_manifest(
                metadata_name="{{inputs.parameters.arango-name}}-service",
                selector_name="{{inputs.parameters.arango-name}}",
                port=constants.service_port,
                target_port=constants.service_port
            )
        )


        with DAG(name="environment-dag") as dag:
            task_arango_db_create = Task(
                name=constants.arango_name,
                template=arango_db,
            )

            task_arango_db_service_create = Task(
                name="arango-service",
                template=arango_db_service_create,
                arguments={
                    "arango-name" : constants.arango_name,
                },
            )

            """task_frontend = Task(
                name="frontend",
                template=frontend
            )"""

            task_arango_db_create >> task_arango_db_service_create

            wt.create()
