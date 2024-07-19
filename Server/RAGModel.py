from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_community.document_loaders import WebBaseLoader
from langchain_huggingface import HuggingFaceEmbeddings
from langchain.tools.retriever import create_retriever_tool
from langchain_community.agent_toolkits.load_tools import load_tools
from langchain.prompts import StringPromptTemplate
from typing import List
from langchain.tools import Tool
import time
import asyncio

class RAGModel:
    # Static
    start_time = time.time()

    load_dotenv()

    zhipu_chat_model = ChatZhipuAI(
        model="glm-4",
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

    # 加载其他工具
    tools = load_tools(
        tool_names=["serpapi"],
        llm=chat_model
    )
    tools.append(retriever_tool)

    # Set up the base template
    template = """Answer the following questions as best you can,
            You can answer the question by yourself , or also can use the following tools:
            {tools}

            The following section is about the dialogue history, which may be helpful:
            {chat_history}

            Use the following format while answering questions:

            Question: the input question you must answer
            Thought: you should always think about what to do and which tool to use
            Action: the tool to use, should be one of [{tools}]
            Action Input: the input to the tool (according to the description of the tool)
            Observation: the result of the action
            ... (this Thought/Action/Action Input/Observation can repeat N times， that is to say, you can solve the question though many steps) ...
            Thought: I now know the final answer
            Final Answer: the final answer to the original input question

            Now please answer the question below! Remember to give your answer strictly according to the format.

            Question: {input}
            {agent_scratchpad}
    """

    class CustomPromptTemplate(StringPromptTemplate):
        # The template to use
        template: str
        # The list of tools available
        tools: List[Tool]

        def format(self, **kwargs) -> str:
            # Get the intermediate steps (AgentAction, Observation tuples)
            # Format them in a particular way
            intermediate_steps = kwargs.pop("intermediate_steps")
            thoughts = ""
            for action, observation in intermediate_steps:
                thoughts += action.log
                thoughts += f"\nObservation: {observation}\nThought: "
            # Set the agent_scratchpad variable to that value
            kwargs["agent_scratchpad"] = thoughts
            # Create a tools variable from the list of tools provided
            kwargs["tools"] = "\n".join([f"{tool.name}: {tool.description}" for tool in self.tools])
            # Create a list of tool names for the tools provided
            kwargs["tool_names"] = ", ".join([tool.name for tool in self.tools])
            return self.template.format(**kwargs)

    end_time = time.time()
    print("VectorStoreDone", "(", end_time - start_time, "s)!")

    def preload_vectorstore(self):
        # 目前想法是尝试将向量数据库预先以文件形式存储，但还有点问题
        return
