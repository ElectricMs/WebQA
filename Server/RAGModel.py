from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import Tool
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain_community.utilities import SerpAPIWrapper
import time



class RAGModel:
    # Static
    start_time = time.time()

    load_dotenv()

    zhipu_chat_model = ChatZhipuAI(
        temperature=0.2,
        streaming=True,
    )
    chat_model = zhipu_chat_model

    # 加载网页内容
    web_loader = WebBaseLoader(
        web_path="https://baike.baidu.com/item/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BB%84%E6%88%90/9237940")
    web_docs = web_loader.load()

    docs = web_docs

    EMBEDDING_DEVICE = "cuda"  # 设置嵌入设备的类型为GPU
    embeddings = HuggingFaceEmbeddings(
        model_name="models/m3e-base-huggingface",  # 指定使用的模型名称
        model_kwargs={"device": EMBEDDING_DEVICE},  # 传递模型参数，指定设备类型
        show_progress=True,  # 显示进度条
    )

    from langchain_text_splitters import RecursiveCharacterTextSplitter
    # 生成分词/切分器
    text_splitter = RecursiveCharacterTextSplitter()
    # 对load进来的文档进行分词/切分
    documents = text_splitter.split_documents(documents=docs)

    from langchain_community.vectorstores import FAISS

    vector = FAISS.from_documents(documents=documents, embedding=embeddings)

    # 创建一个向量检索器实例
    retriever = vector.as_retriever()

    # 创建检索工具
    retriever_tool = create_retriever_tool(
        retriever=retriever,
        name="Principles of Computer Organization_retriever",
        description="搜索有关计算机组成原理概要的信息，可能不包含精确的信息",
    )

    # 加载工具
    search = SerpAPIWrapper()

    tools = [Tool(
        name="Search",
        func=search.run,
        description="useful for when you need to answer questions about current events. "
                    "You should only pass on the question"
    ), retriever_tool]

    end_time = time.time()
    print("VectorStoreDone", "(", end_time - start_time, "s)!")

    def preload_vectorstore(self):
        # 目前想法是尝试将向量数据库预先以文件形式存储，但还有点问题
        return
