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
    # import os
    # zhipuai
    # os.environ["ZHIPUAI_API_KEY"] = "7bdc9df887559945f7c508bd61d0ed57.oexUZRGMwfxQbeQ5"

    zhipu_chat_model = ChatZhipuAI(
        temperature=0.2,
        streaming=True,
        # api_key="7bdc9df887559945f7c508bd61d0ed57.oexUZRGMwfxQbeQ5",
    )
    chat_model = zhipu_chat_model
    print("successfully loaded zhipu chat model")


    from langchain_community.vectorstores import FAISS
    EMBEDDING_DEVICE = "cuda"  # 设置嵌入设备的类型为GPU
    embeddings = HuggingFaceEmbeddings(
        model_name="models/m3e-base-huggingface",  # 指定使用的模型名称
        model_kwargs={"device": EMBEDDING_DEVICE},  # 传递模型参数，指定设备类型
        show_progress=True,  # 显示进度条
    )

    # vector = FAISS.from_documents(documents=documents, embedding=embeddings)
    print("start loading vector...")
    vector = FAISS.load_local("../vectors_bin", embeddings, allow_dangerous_deserialization=True)
    print(vector)

    # 创建一个向量检索器实例
    retriever = vector.as_retriever()

    # 创建检索工具
    retriever_tool = create_retriever_tool(
        retriever=retriever,
        name="Tianjin_retriever",
        description="搜索有关天津的信息",
    )

    # 加载工具 此搜索工具不稳定 考虑移除
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
