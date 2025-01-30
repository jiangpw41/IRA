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

    def embedding(self, text_dict):
        embedding_list = []
        # Split based on the batch size and calculate the total number of batches.
        text = list(text_dict.keys())
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
    

import os
from enum import Enum
import numpy as np


from collections import OrderedDict

"""
Two levels of retrieval:
One way is to calculate the score by editing the distance
Another way is to calculate scores based on the similarity of embedding vectors
"""
# 检查并导入 FAISS 库（根据系统配置选择是否使用 AVX2 优化）。
def dependable_faiss_import(no_avx2=None):
    """
    检查并导入 FAISS 库（根据系统配置选择是否使用 AVX2 优化）。
    如果 no_avx2 为真，或环境变量 FAISS_NO_AVX2 被设置，则加载非 AVX2 版本的 FAISS。
    如果导入失败，则抛出提示用户安装 FAISS 的异常。

    Args:
        no_avx2: Load Faiss strictly with no AVX2 optimization
            so that the vector store is portable and compatible with other devices.
    """
    if no_avx2 is None and "FAISS_NO_AVX2" in os.environ:
        no_avx2 = bool(os.getenv("FAISS_NO_AVX2"))

    try:
        if no_avx2:
            from faiss import swigfaiss as faiss
        else:
            import faiss
    except ImportError:
        raise ImportError(
            "Could not import the Faiss Python package. "
            "Please install it with `pip install faiss-gpu` (for CUDA supported GPU) "
            "or `pip install faiss-cpu` (depending on Python version)."
        )
    return faiss

# 构建、维护和使用 FAISS 向量检索索引。
class FAISS:
    def __init__(self, embeddings, key_list, topk=1):
        """
        embeddings: 待检索的嵌入向量（一个嵌入向量的列表）。
        doc_store: 节点的元信息（如 CSV 数据），包含其他与嵌入关联的文档信息。
        """
        self.faiss = dependable_faiss_import()
        self.distance_strategy = "EUCLIDEAN_DISTANCE"                          # 根据 DISTANCE_STRATEGY（config中配置为欧氏距离EUCLIDEAN_DISTANCE），初始化 FAISS 索引
        self.embeddings = embeddings
        self.index = None
        self.normalize_L2 = False
        self.top_k = topk
        self.key_list = key_list
        self.index = self.faiss.IndexFlatL2(len(embeddings[0]))


    def add_all(self):
        """将所有的嵌入向量添加到 FAISS 索引中。
        支持向量的 L2 正则化（归一化）
        将 embeddings 转换为 float32 类型以兼容 FAISS。"""
        vector = np.array(self.embeddings, dtype=np.float32)
        if self.normalize_L2:
            self.faiss.normalize_L2(vector)
        self.index.add(vector)

    def search(self, query):
        """基于向量相似性，检索最接近的文档。
        (1)使用 Embedding().embedding_query(query) 将查询转为嵌入向量
        (2)调用 FAISS 索引的 search 方法找到 top_k 个最相似的嵌入。"""
        top_k = self.top_k
        query_emb = Embedding().embedding_query(query)
        query_emb = np.array(query_emb, dtype=np.float32)
        distance, idx = self.index.search(query_emb.reshape(1, -1), k=top_k)
        return [self.key_list[i] for i in idx[0]]