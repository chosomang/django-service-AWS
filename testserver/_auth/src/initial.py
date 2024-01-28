from common.neo4j.handler import Neo4jHandler

class InitDatabase(Neo4jHandler):
    def __init__(self, user_db) -> None:
        super().__init__()
        self.user_db = user_db
    
    def compliance(self) -> bool:
        cypher = """
        LOAD CSV FROM 'file:///isms-p.csv' AS row
        WITH row[0] AS row0, row[1] AS row1, row[2] AS row2, row[3] AS row3, row[4] AS row4, row[5] AS row5, row[6] AS row6, row[7] AS row7, row[8] AS row8
        
        MERGE (n:Compliance{name:'Compliance'})
        MERGE (l:Compliance:Certification {name: 'Isms_p', renew:36, applicable_country:'Korea'})
        MERGE (v:Version:Compliance {name: 'Isms_p', date:date('2023-10-31')})
        MERGE (n)-[:COMPLIANCE]->(l)
        MERGE (l)-[:VERSION]->(v)
        
        WITH row0, row1, row2, row3, row4, row5, row6, row7, row8, n, l, v
        
        CALL apoc.do.case([
            row0 IS NULL AND row2 IS NULL AND row4 IS NOT NULL,
            'MERGE (a:Article:Compliance:Certification {compliance_name: "Isms_p", no: row4, name: row5, comment: row6})
            MERGE (v)-[:ARTICLE]->(a)
            RETURN a',
            row0 IS NOT NULL AND row2 IS NULL AND row4 IS NOT NULL,
            'MERGE (c:Chapter:Compliance:Certification{compliance_name:"Isms_p", no:row0, name:row1})
            MERGE (a:Article:Compliance:Certification {compliance_name: "Isms_p", no: row4, name: row5, comment: row6})
            MERGE (v)-[:CHAPTER]->(c)
            MERGE (c)-[:ARTICLE]->(a)
            RETURN a',
            row0 IS NOT NULL AND row2 IS NOT NULL AND row4 IS NOT NULL,
            'MERGE (c:Chapter:Compliance:Certification{compliance_name:"Isms_p", no:row0, name:row1})
            MERGE (s:Section:Compliance:Certification {compliance_name: "Isms_p", no: row2, name: row3})
            MERGE (a:Article:Compliance:Certification {compliance_name: "Isms_p", no: row4, name: row5, comment: row6})
            MERGE (v)-[:CHAPTER]->(c)
            MERGE (c)-[:SECTION]->(s)
            MERGE (s)-[:ARTICLE]->(a)
            RETURN a'
        ],
            'RETURN row2',
            {
                row0:row0,
                row1:row1,
                row2:row2,
                row3:row3,
                row4:row4,
                row5:row5,
                row6:row6,
                v:v
            }
        )
        YIELD value
        
        WITH row4, row6, row7, row8, value.a AS a, n, l, v
        WHERE row4 CONTAINS a.no
        WITH collect(row7) AS collect, split(replace(row8, "\n", ""), '_')[1..] AS example, a, n, l, v
        SET a.checklist = collect, a.example = example
        RETURN n, l, v
        """
        try:
            self.run(database=self.user_db, query=cypher)
            return True
        except Exception as e:
            print(f'Error: Can not overwrite compliance -> {e}')
            return False