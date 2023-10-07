import psycopg2
import os
import logging
from square.client import Client
from google.cloud import aiplatform
from langchain.llms import VertexAI

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Config:
    _instance = None

    @staticmethod
    def get_instance():
        """Return the singleton instance of Config"""
        if Config._instance is None:
            Config._instance = Config()
        return Config._instance

    def __init__(self):
        if Config._instance is not None:
            raise Exception(
                "Config is a singleton class, use get_instance() to get the instance."
            )

        try:
            self.host = "db.rakjbiwwgvtopczoyvtv.supabase.co"
            self.dbname = "postgres"
            self.port = "5432"
            self.user = "postgres"
            self.password = os.environ.get('SUPABASE_DB')
            self.square_access_token = os.environ.get('SQUARE_ACCESS_TOKEN')
            self.square_applicationid = "sandbox-sq0idb-qqw1PDXOq16d403omj_1_g"
            self.gcp_json = os.environ.get('GOOGLE_APPLICATION_CREDENTIALS')
            self.gcp_project_id = "river-surf-400419"
            self.gcp_location = "us-central1"
            self.gcp_staging_bucket = "gs://river-surf-400419-vertex-ai"
        except KeyError as e:
            raise Exception("Missing environment variable: {}".format(e))

    def get_postgres_connection(self):
        try:
            conn = psycopg2.connect(host=self.host, dbname=self.dbname, user=self.user, password=self.password,
                                    port=self.port)
            logger.info(f"Connected to Postgres")
            return conn
        except Exception as e:
            raise Exception(f"An Exception Occurred while connecting to Postgres --> {e}")

    def get_square_connection(self):
        logger.info(f"Connecting to Square")
        square_client = Client(access_token=self.square_access_token, environment='sandbox')
        result = square_client.locations.list_locations()
        if result.is_success():
            square_location_id = result.body['locations'][0]['id']
            logger.info(f"Connected to Square")
            return square_client, square_location_id
        elif result.is_error():
            for error in result.errors:
                raise Exception(
                    f"Error connecting to Square --> Category :{error['category']} Code: {error['code']} Detail: {error['detail']}")

    def get_vertex_ai_connection(self):
        aiplatform.init(project=self.gcp_project_id, location=self.gcp_location,
                        staging_bucket=self.gcp_staging_bucket)
        try:
            llm = VertexAI(max_output_token=4000, temperature=0.3)
            logger.info(f"Connected to Vertex AI")
            return llm
        except Exception as e:
            raise Exception(f"An Exception Occurred while connecting to Vertex AI --> {e}")
