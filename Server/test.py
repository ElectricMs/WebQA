from langchain_core.messages import AIMessageChunk

# from chat_models.SingleAgent import SingleAgent

# model = SingleAgent()


# async def main():
#     chunks = []
#     start_final: bool = False
#     start_stream: bool = False
#     print("===============================")
#     async for chunk in model.agent_executor.astream_events(
#             input={"input": "hello"}, version="v2", include_names="ChatZhipuAI"
#     ):
#         # chunks.append(chunk)
#         # print("-----------------------")
#         # pprint.pprint(chunk, depth=5)
#         if "chunk" in chunk["data"]:
#
#             # pprint.pprint(chunk["data"]["chunk"], depth=5)
#             if isinstance(chunk["data"]["chunk"], AIMessageChunk):
#                 # 提取content值
#                 content = getattr(chunk["data"]["chunk"], "content", None)
#                 if content:
#                     # print("-----------------------")
#                     # print("Content:", content)
#
#                     if start_stream:
#                         print(content, end='')
#
#                     if "Final" in content:
#                         start_final = True
#
#                     if (start_final) and ":" in content:
#                         start_stream = True


import torch

if torch.cuda.is_available():
    print("CUDA is available")
else:
    print("CUDA is not available")

from dotenv import load_dotenv
load_dotenv()
from langchain_community.chat_models import ChatSparkLLM
chat_model = ChatSparkLLM(
    temperature=0.2,
    streaming=True,
    # app_id="8d211386",
    # api_key="b723759ce39a0c046b1afbe4f255662f",
    # api_secret="ZTM5ZDY2YWZkNTI2ZDllNWExZTcyNzFj"
)
print(chat_model.invoke("你好"))


# asyncio.run(main())

# model.agent_executor.stream({"input": "你好"})
# model.agent_executor.astream_events({"input": "你好"})

# answer = model.agent_executor.invoke({"input": "How many people live in canada?"})
# print(answer)

# print(model.agent_executor.memory.buffer)


# answer = model.agent_executor.invoke({"input": "what is their national anthem called?"})


# print(answer)

# print(model.agent_executor.memory.buffer)
# answer = model.agent_executor.invoke({"input": "what is their national anthem called?"})
# print(answer)
