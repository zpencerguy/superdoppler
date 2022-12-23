import pandas as pd
import pymssql
import psycopg2
from sqlalchemy.engine import create_engine
from dagster import resource

import settings
from utils.log_util import init_logging

logger = init_logging()


class DatabaseConnection:
    def __init__(self, database=None):
        self.engine = create_engine(settings.CONNECTIONS[database])
        self.connection = self.engine.raw_connection()

    @staticmethod
    def get_connection(server: str, database: str, driver: str = 'psycopg2'):
        if driver == 'psycopg2':
            return psycopg2.connect(
                host=server,
                database=database,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
            )
        else:
            return pymssql.connect(
                server=server,
                user=settings.DB_USER,
                password=settings.DB_PASSWORD,
                database=database
            )

    def fetch_data_by_query(self, query: str):
        return pd.read_sql(
            sql=query,
            con=self.engine
        )

    def fetch_data_by_sproc(self, name: str, params: str):
        query = f'EXEC {name} {params};'
        return pd.read_sql_query(
            query,
            self.engine
        )

    def execute_stored_procedure(self, procedure_list):
        with self.engine.begin() as conn:
            for proc in procedure_list:
                # logger.info(proc)
                conn.execute(proc)
        return True

    @staticmethod
    def create_insert_statements(df, table):
        return f"""INSERT INTO {table} ({', '.join(col for col in df.columns)}) 
        VALUES ({','.join('?' for x in range(len(df.columns.to_list())))})"""


@resource(config_schema={"database": str})
def db_resource(init_context):
    database = init_context.resource_config["database"]
    return DatabaseConnection(database)


  # id          Int           @id @default(autoincrement())
  # createdAt   DateTime      @default(now()) @map(name: "created_at")
  # platform    platforms     @relation(fields: [platformId], references: [id])
  # platformId  Int           @map(name: "platform_id")
  # address     String?
  # name        String
  # imageUrl    String?       @map(name: "image_url")
  # slug        String?
  # supply      Int?
  # twitter     String?
  # discord     String?
  # website     String?


if __name__ =='__main__':
    base_stmt = """INSERT INTO public.collections (slug, name, image_url, website, twitter, discord, address, supply, platform, platformId) 
        VALUES ({},{},{},{},{},{},{},{},{},{})"""
    stmts = []

