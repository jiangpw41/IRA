# IRA
Code examples for paper IRA.

# data
## SpCQL
Here is only the schema of database we provide. The main data and DB files of SpCQL can be downloaded from https://github.com/Guoaibo/Text-to-CQL. Your should download it at data/SpCQL and transform the gold queries alone as SpCQL_gold_query_list.json and the gold results alone as SpCQL_gold_result_list.json.

## R3
We provide the processed files at data/R3. The original project can be found at https://github.com/YLiberals/NL2GQL_neo4j. But there are only some CSV files with some problems. We provide the DB construction method at https://github.com/jiangpw41/N3_db_construction, your can run db_construct.py to get a executable Nebula database on your server.

# eval
All metrics used in paper are implemented under dir eval.

# exec_post
Database (Nebula and Neo4j) execution and pre-post-process methods.

# inter_data
Save the query lists and their execution results for evaluation.

# methods
Our IRA method. There are the GQL parser for intentions, prompt and fine-tuning data construction, db alignment methods, and inference scripts.

# results
Save your evaluation results here.

