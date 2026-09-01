"""中文嵌入封装（W7）：复用 W5 的 BGEZhEmbedding，适配 chromadb 1.x 协议。

W7 的向量 RAG 检索工具（search_knowledge_base）用它把查询转成向量。
BGE 查询侧要加指令前缀，文档侧不加。
"""
from sentence_transformers import SentenceTransformer

BGE_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："


class BGEZhEmbedding:
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        self.model = SentenceTransformer(model_name)
        self._model_name = model_name.split("/")[-1]

    def name(self) -> str:
        return self._model_name

    def __call__(self, input):
        return self.embed_documents(input)

    @staticmethod
    def _to_list(input):
        return [input] if isinstance(input, str) else list(input)

    def embed_documents(self, input):
        vecs = self.model.encode(self._to_list(input), normalize_embeddings=True)
        return vecs.tolist()

    def embed_query(self, input):
        texts = [BGE_INSTRUCTION + t for t in self._to_list(input)]
        vecs = self.model.encode(texts, normalize_embeddings=True)
        return vecs.tolist()
