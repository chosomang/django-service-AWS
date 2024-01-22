# 3rd party
from neo4j import GraphDatabase
# django
from django.conf import settings

NEO4J_URI = f"bolt://{settings.NEO4J['HOST']}:{settings.NEO4J['PORT']}"
username = settings.NEO4J['USERNAME']
password = settings.NEO4J['PASSWORD']

class Neo4jHandler:
    def __init__(self) -> None:
        self.uri = f"bolt://{settings.NEO4J['HOST']}:{settings.NEO4J['PORT']}"
        self.user = settings.NEO4J['USERNAME']
        self.pw = settings.NEO4J['PASSWORD']
        
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.pw))
        
    def close(self):
        self.driver.close()
    
    def run(self, database, query):
        with self.driver.session(database=database) as session:
            res = session.write_transaction(self._run, query)
            return res
    
    def create_database(self, database):
        query = f"CREATE DATABASE `{database}`"
        with self.driver.session(database=database) as session:
            res = session.write_transaction(self._run, query)
            return res
    
    @staticmethod
    def _run(tx, database, query):
        res = tx.run(query)
        return res