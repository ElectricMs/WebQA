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
    vector = FAISS.load_local("./vectors_bin", embeddings, allow_dangerous_deserialization=True)
    print(vector)

    # 创建一个向量检索器实例
    retriever = vector.as_retriever()

    # 链：接受最近的输入+会话历史
    from langchain.chains import create_history_aware_retriever
    from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate

    # 生成ChatModel会话的提示词
    prompt = ChatPromptTemplate.from_messages([
        MessagesPlaceholder(variable_name="chat_history"),
        ("user", "{input}"),
        ("user",
         "Given the above conversation, generate a search query to look up in order to "
         "get information relevant to the conversation")
    ])
    # 模拟历史会话记录
    # chat_history = []
    # 生成含有历史信息的检索链
    retriever_chain = create_history_aware_retriever(chat_model, retriever, prompt)

    @staticmethod
    def retriever_tool_func(query, chat_history):
        return RAGModel.retriever_chain.invoke({
            "chat_history": chat_history,
            "input": query
        })

    retriever_tool = Tool(
        func=retriever_tool_func,
        name="retriever_tool",
        description="Take this tool in priority status,"
                    "This tool handles document retrieval and "
                    "question answering based on context history."
    )

    # 加载工具 此搜索工具不稳定 考虑移除
    # search = SerpAPIWrapper()

    # tools = [Tool(
    #     name="Search",
    #     func=search.run,
    #     description="useful for when you need to answer questions about current events. "
    #                 "You should only pass on the question"
    # ), retriever_tool]
    tools = [retriever_tool]

    end_time = time.time()
    print("VectorStoreDone", "(", end_time - start_time, "s)!")

    def preload_vectorstore(self):
        # 目前想法是尝试将向量数据库预先以文件形式存储，但还有点问题
        return
