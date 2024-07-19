import asyncio

from langchain_core.messages import AIMessageChunk

from source import options, generator, idregister


def get_id():
    global uid
    try:
        # 连接redis
        # register = idregister.Register(host="127.0.0.1", port=6379)

        # 获取worker id
        # worker_id = register.get_worker_id()

        # 生成id generator
        option = options.IdGeneratorOptions(worker_id=23, seq_bit_length=10)
        option.base_time = 12311111112
        idgen = generator.DefaultIdGenerator()
        idgen.set_id_generator(option)

        uid = idgen.next_id()

        # print(worker_id)
        print(uid)
        print(option.__dict__)

        # 退出注册器线程
        # register.stop()

    except ValueError as e:
        print(e)
    return uid


# get_id()


from SingleAgent import SingleAgent
model = SingleAgent()

async def main():
    import pprint

    chunks = []
    start_final: bool = False
    start_stream:bool = False
    print("===============================")
    async for chunk in model.agent_executor.astream_events(
            input="hello", version="v2",include_names="ChatZhipuAI"
    ):
        #chunks.append(chunk)
        # print("-----------------------")
        # pprint.pprint(chunk, depth=5)
        if "chunk" in chunk["data"]:

            #pprint.pprint(chunk["data"]["chunk"], depth=5)
            if isinstance(chunk["data"]["chunk"], AIMessageChunk):
                # 提取content值
                content = getattr(chunk["data"]["chunk"], "content", None)
                if content:
                    #print("-----------------------")
                    #print("Content:", content)

                    if start_stream:
                        print(content, end='')

                    if "Final" in content:
                        start_final = True

                    if(start_final)and ":" in content:
                        start_stream = True

asyncio.run(main())

# model.agent_executor.stream({"input": "你好"})
# model.agent_executor.astream_events({"input": "你好"})