# noinspection PyPackageRequirements
import unittest, docker, thesaurusCreator, json
from arango import ArangoClient, database
from docker import DockerClient


class MyTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """
        Creating a new empty ArangoDB container to run the test safely
        Connecting to it through the arango API
        """
        image_name : str = "arangodb/enterprise:3.12.6.1"
        env : dict = {'ARANGO_ROOT_PASSWORD':'test'}
        ports : dict = {'8529':'8529'}
        cls._connection : DockerClient = docker.from_env()
        cls._connection.containers.run(image_name, name="TestArango", detach=True, environment=env, ports=ports)

        cls._credentials: dict = {
            "host": "http://localhost:8529",
            "username": "root",
            "password": "test",
            "database": "TEST"
        }
        cls._client = ArangoClient(cls._credentials['host'])

        sys_db : database.StandardDatabase = cls._client.db('_system', username='root', password='test')

        # Create the database associated with the thesaurus if it does not exist yet
        if not sys_db.has_database(cls._credentials['database']):
            sys_db.create_database(cls._credentials['database'])

        cls._arango_database : database.StandardDatabase = cls._client.db(cls._credentials['database'], username=cls._credentials['username'], password=cls._credentials['password'])

    @classmethod
    def tearDownClass(cls):
        """
        Cleaning up the test container and Arango API Wrapper
        """
        cls._client.close()

        cls._connection.containers.get("TestArango").remove(force=True)
        cls._connection.close()




    def test_insertion(self):
        theso_config : dict = { # We can get by with just a name since we don't have to fetch anything
            "name" : "TEST1"
        }
        with open("tests/th13.json") as file:
            theso : dict = json.load(file)

            skipped, added = thesaurusCreator.insert_thesaurus(self._arango_database, theso_config, theso)

            self.assertEqual(len(skipped), 1130)
            self.assertEqual(len(added), 2249)

    def test_inter_thesori_edges(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
