# 此类已废弃 用于测试的

class RAGModel:
    def __init__(self):
        load_dotenv()

    def generate_answer(self, question):
        return self.rag.run(question)

    def load_and_initialize(self):
        from langchain_community.chat_models import ChatZhipuAI
        zhipu_chat_model = ChatZhipuAI(
            model="glm-4",
            temperature=0.2,
        )

        # 完成模型的选用 统一封装为chat_model
        chat_model = zhipu_chat_model

        from langchain_community.document_loaders import WebBaseLoader, PDFMinerLoader
        # 加载网页内容
        web_loader = WebBaseLoader(
            web_path="https://baike.baidu.com/item/%E8%AE%A1%E7%AE%97%E6%9C%BA%E7%BB%84%E6%88%90/9237940")
        web_docs = web_loader.load()

        # 加载PDF文件内容
        # pdf_loader = PDFMinerLoader(file_path=".\media\Principles of Computer Organization_3.pdf")
        # pdf_docs = pdf_loader.load()

        # 将网页内容和PDF内容合并到一个列表中
        docs = web_docs  # + pdf_docs

        from langchain_huggingface import HuggingFaceEmbeddings

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

        print("vector:", vector)
        print("-----------------------------------------------------")



        return



from dotenv import load_dotenv
load_dotenv()





# 4. Agent
"""
Agent进行网络资源搜索|检索，实现方式:
1．给出第三方接口的函数（工具）的名称:serpapi
2．封装爬虫工具，爬取指定页面(s)
3. 自行实现一个调用某个搜索引擎（发关键词获取并解析搜索反馈）函数
"""
# https://blog.csdn.net/wenxingchen/article/details/130474611
# 获取 serapi google搜索工具的key


from langchain.tools.retriever import create_retriever_tool
from langchain_community.agent_toolkits.load_tools import load_tools


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

{chat_history}内可能有你需要的对话历史，你可以参考

Use the following format while answering questions:

Question: the input question you must answer
Thought: you should always think about what to do and which tool to use
Action: the tool to use, should be one of [{tools}]
Action Input: the input to the tool (according to the description of the tool)
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times， that is to say, you can solve the question though many steps) ...
Thought: I now know the final answer
Final Answer: the final answer to the original input question

现在开始提问! 记得严格按照format的格式给出你的回答

Question: {input}
{agent_scratchpad}"""

# Set up a prompt template
from langchain.prompts import StringPromptTemplate
from typing import List
from langchain.tools import Tool
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

prompt = CustomPromptTemplate(
    template=template,
    tools=tools,
    # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
    # This includes the `intermediate_steps` variable because that is needed
    input_variables=["input", "intermediate_steps","chat_history"]
)



from langchain.agents import  AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.memory import ConversationBufferMemory
from langchain import  SerpAPIWrapper, LLMChain
from typing import Union
from langchain.schema import AgentAction, AgentFinish, OutputParserException
import re



class CustomOutputParser(AgentOutputParser):
    def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
        # Check if agent should finish
        if "Final Answer:" in llm_output:
            return AgentFinish(
                # Return values is generally always a dictionary with a single `output` key
                # It is not recommended to try anything else at the moment :)
                return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                log=llm_output,
            )
        # Parse out the action and action input
        regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
        match = re.search(regex, llm_output, re.DOTALL)
        if not match:
            return AgentFinish(
                return_values={"一个可能的回答是：": llm_output.strip()},
                log=llm_output,
            )
        action = match.group(1).strip()
        action_input = match.group(2)
        # Return the action and action input
        return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)

output_parser = CustomOutputParser()

# LLM chain consisting of the LLM and a prompt
llm_chain = LLMChain(llm=chat_model, prompt=prompt)

tool_names = [tool.name for tool in tools]

agent = LLMSingleActionAgent(
    llm_chain=llm_chain,
    output_parser=output_parser,
    stop=["\nObservation:","\n\nObservation"],
    allowed_tools=tool_names
)
# 多轮对话
memory = ConversationBufferMemory(memory_key="chat_history")
agent_executor = AgentExecutor.from_agent_and_tools(agent=agent, tools=tools, verbose=True , memory=memory)
print(
    "欢迎使用agent代理的多轮交互机器人，目前我支持通过SerpAPI进行搜索回答、回答指定web网页下、指定路径下PDF文档或指定路径下txt文档相关的问题,并且有处理基础数学问题的能力，对话结束时请输入end结束会话")
while True:
    human_input = input("请输入您的问题：")
    if human_input == "end":
        break
    agent_executor.invoke(human_input)

print("CHAT END....")