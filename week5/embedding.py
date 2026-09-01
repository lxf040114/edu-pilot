"""中文嵌入封装：把 BGE-zh 包装成 Chroma 1.x 要求的 EmbeddingFunction。

为什么 W4 用 MiniLM 中文弱、W5 换 BGE-zh？
- MiniLM (all-MiniLM-L6-v2) 是英文模型，向量空间以英文语义为主；中文句子被按字编码后
  语义距离失真 → 检索排序差（W4 实测闭包定义排第 5）。
- BGE-zh (BAAI/bge-small-zh-v1.5) 是专为中文训练的双塔嵌入模型，中文语义距离更准确。

chromadb 1.x 的 EmbeddingFunction 协议需要同时具备：
- __call__(self, input)：主接口，validate 会检查签名必须是 (self, input)
- name()：返回函数名，用于持久化时校验配置冲突
- embed_documents(input)：文档侧嵌入（BGE 文档侧【不加】指令前缀）
- embed_query(input)：查询侧嵌入（BGE 查询侧【加】指令前缀，进入「检索分布」）

关键细节：BGE 系列做「检索」时查询侧要加指令前缀
  "为这个句子生成表示以用于检索相关文章："
这是 BGE 官方用法，不加会掉点。
"""
from sentence_transformers import SentenceTransformer

BGE_INSTRUCTION = "为这个句子生成表示以用于检索相关文章："


class BGEZhEmbedding:
    def __init__(self, model_name: str = "BAAI/bge-small-zh-v1.5"):
        # 首次实例化会下载约 130MB 模型权重，之后缓存在 ~/.cache/huggingface
        self.model = SentenceTransformer(model_name)
        self._model_name = model_name.split("/")[-1]

    def name(self) -> str:
        return self._model_name

    def __call__(self, input):
        # chroma 校验要求 __call__(self, input) 这个签名；默认走文档侧
        return self.embed_documents(input)

    @staticmethod
    def _to_list(input):
        return [input] if isinstance(input, str) else list(input)

    def embed_documents(self, input):
        # 文档侧：BGE 不加指令前缀
        vecs = self.model.encode(self._to_list(input), normalize_embeddings=True)
        return vecs.tolist()

    def embed_query(self, input):
        # 查询侧：BGE 加指令前缀，让查询向量进入「检索分布」
        texts = [BGE_INSTRUCTION + t for t in self._to_list(input)]
        vecs = self.model.encode(texts, normalize_embeddings=True)
        return vecs.tolist()
