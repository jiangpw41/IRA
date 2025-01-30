from sentence_transformers import SentenceTransformer
import pandas as pd
from tqdm import tqdm
'''
Embedding the files extracted from the underlying database, and the results after embedding are also saved back in the table.
'''
# os.chdir( "/home/jiangpeiwen2/jiangpeiwen2/Text2Cypher/baselines/R3_NL2GQL" )

EMBEDDING_MODEL='m3e-base'
EMBEDDING_BATCH_NUM=10

class Embedding:
    def __init__(self):
        self.batch_size = EMBEDDING_BATCH_NUM
        self.model = SentenceTransformer('/home/jiangpeiwen2/jiangpeiwen2/NL2GQL/methods/baselines/R3_NL2GQL/models/m3e-base').to("cuda:0")

    def embedding(self, text):
        """
        text是一个字符串列表
        """
        # text = list(text_dict.keys())
        embedding_list = []
        # Split based on the batch size and calculate the total number of batches.
        # print(text)
        batch_size = self.batch_size
        while batch_size > 0:  # Ensure it doesn't get stuck in an infinite loop.
            end_idx = min(len(text), batch_size)
            batch = text[:end_idx]

            try:
                output = self.model(batch)
                break  # Exit the inner loop when the current batch is successful. The batch size won't exceed GPU memory.
            except RuntimeError as e:
                # Check if the error is related to GPU memory.
                if 'out of memory' in str(e):
                    print(f"Out of memory with batch size {batch_size}. Reducing batch size and trying again.")
                    batch_size //= 2  # Reduce the batch size for the current batch.
                else:
                    # If it's another error, raise it directly.
                    raise
            except:
                # Handle other unexpected errors.
                print("An unexpected error occurred.")
                break

        # Once the appropriate batch size is determined, perform the actual iteration.
        # print(batch_size, "batch_size")
        num_batches = len(text) // batch_size + (1 if len(text) % batch_size != 0 else 0)
        for i in tqdm( range(num_batches), desc=f"Embedding"):
            # print(i)
            start_idx = i * batch_size
            end_idx = start_idx + batch_size
            batch = text[start_idx:end_idx]
            temp_embedding = self.model.encode(batch, batch_size=batch_size, normalize_embeddings=True)
            embedding_list.extend(temp_embedding)
        
        return embedding_list


    def embedding_query(self, text):
        # Embed the query, and placing it in this class ensures the use of the same embedding model.
        return self.model.encode(text)
    

