# local
from datetime import datetime
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
            res = session.execute_write(self._run, query)
            return res
    
    def create_database(self, db_name):
        query = f"CREATE DATABASE `{db_name}`"
        with self.driver.session() as session:
            session.execute_write(self._run, query)
        self.close()
    
    @staticmethod
    def _run(tx, query):
        res = tx.run(query)
        return res
    
# neo4j_handler = Neo4jHandler()


class Cypher(Neo4jHandler):
    def __init__(self) -> None:
        super().__init__()
    
    def close(self):
        Neo4jHandler.close(self)
        
    def push_user(self, user, ip):
        query = f"""
MERGE (super:Super:Teiren {{name:'Teiren'}})
WITH super
MERGE (super)-[:SUB]->(a:Teiren:Account {{
    userName: '{user.username}',
    userPassword: '{user.password}',
    email: '{user.email}',
    createdTime: '{str(datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'))}',
    ipAddress: '{ip}',
    uuid: '{user.uuid}',
    failCount: 0,
    emailCheck: 'False'
}})
RETURN ID(a) as id
"""
        res = Neo4jHandler.run(self, user.db_name, query)
        return res
        
# cypherhandler = Cypher()