import getpass
import os

# sparkllm 环境变量配置
os.environ["IFLYTEK_SPARK_APP_ID"] = "acc4dd70"
os.environ["IFLYTEK_SPARK_API_KEY"] = "98f96c834ca0ddfdfc461086a014760c"
os.environ["IFLYTEK_SPARK_API_SECRET"] = "NmIwNzU0ZjY1Mjk5NmZiNDM3NTM0ZWZi"
os.environ["IFLYTEK_SPARK_API_URL"] = "wss://spark-api.xf-yun.com/v3.1/chat"
os.environ["IFLYTEK_SPARK_llm_DOMAIN"] = "generalv3"


# zhipuai model
from langchain_community.chat_models import ChatZhipuAI
model = ChatZhipuAI(model="glm-4")
# sparkllm model
from langchain_community.chat_models import ChatSparkLLM
model = ChatSparkLLM()


#import message
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
messages = [
    HumanMessage(content="hi! I'm Bob"),
    AIMessage(content="hi! Bob, How can I help you?"),
    HumanMessage(content="Whtat's my name?")
]

from langchain_core.chat_history import(
    BaseChatMessageHistory,
    InMemoryChatMessageHistory
)
from langchain_core.runnables.history import RunnableWithMessageHistory

#后续可以存储在本地
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = InMemoryChatMessageHistory()
    return store[session_id]
with_message_history = RunnableWithMessageHistory(runnable = model, get_session_history = get_session_history)

##每一个config对应一个对话！！！
config = {"configurable": {"session_id": "abc2"}}

response = with_message_history.invoke(
    [HumanMessage(content="Hi! I'm Bob")],
    config=config,
)
response = with_message_history.invoke(
    [HumanMessage(content="What's my name?")],
    config=config,
)

print(response.content)
print("-----------------------------------------------------------------")

config = {"configurable": {"session_id": "abc3"}}
response = with_message_history.invoke(
    [HumanMessage(content="What's my name?")],
    config=config,
)
print(response.content)
print("-----------------------------------------------------------------")
config = {"configurable": {"session_id": "abc2"}}

response = with_message_history.invoke(
    [HumanMessage(content="What's my name?")],
    config=config,
)

print(response.content)
print("-----------------------------------------------------------------")
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

prompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            "You are a helpful assistant. Answer all questions to the best of your ability in {language}.",
        ),
        MessagesPlaceholder(variable_name="messages"),
    ]
)
chain = prompt | model
response = chain.invoke(
    {
        "messages": [HumanMessage(content="Hi I am Bob")]
    }
)

print(response.content)
with_message_history = RunnableWithMessageHistory(chain, get_session_history)

with_message_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="messages",
)
config = {"configurable": {"session_id": "abc30"}}
response = with_message_history.invoke(
    {"messages": [HumanMessage(content="hi! I'm todd")], "language": "Chinese"},
    config=config,
)
print(response.content)
print("-----------------------------------------------------------------")
response = with_message_history.invoke(
    {"messages": [HumanMessage(content="What's my name")], "language": "Chinese"},
    config=config,
)

print(response.content)
print("-----------------------------------------------------------------")

from langchain_core.messages import SystemMessage, trim_messages
from operator import itemgetter

# from langchain_core.runnables import RunnablePassthrough

# trimmer = trim_messages(
#     max_tokens=65,
#     strategy="last",
#     token_counter=model,
#     include_system=True,
#     allow_partial=False,
#     start_on="human",
# )

# chain = (
#     RunnablePassthrough.assign(messages=itemgetter("messages") | trimmer)
#     | prompt
#     | model
# )

