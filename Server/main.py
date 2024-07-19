import json
from fastapi import FastAPI
import uvicorn  # web server 一个轻量级的 ASGI 服务器，用于运行 FastAPI 应用。
from fastapi import Request
from langchain_core.messages import AIMessageChunk
from starlette.responses import JSONResponse, StreamingResponse

from SingleAgent import SingleAgent
from source import options, generator, idregister

app = FastAPI()

# 这样的话没法多线程，理论上应该在创建新连接时对于每个新连接创建新model
model = SingleAgent()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# 前端应该要传给后端question和自身id，apikey，id用于确定询问者身份和对话编号（比如一个人可以开启多个对话），apikey用于验证是否有权限对话
@app.post("/ask")
async def ask_question(request: Request):
    try:

        data = await request.json()
        print("data:", data)
        question = data.get('question', '')
        if not question:
            return JSONResponse({'error': 'No question provided'}, status_code=400)

        # 使用预加载的RAG模型生成答案
        answer = model.generate_answer(question)
        return JSONResponse({'answer': answer}, status_code=400)

    except Exception as e:
        print(f"An exception occurred: {e}")


@app.post("/stream")
async def stream(request: Request):
    try:

        data = await request.json()
        print("data:", data)
        question = data.get('question', '')
        if not question:
            return JSONResponse({'error': 'No question provided'}, status_code=400)

        # 使用预加载的RAG模型生成答案
        # answer = model.generate_answer(question)
        # return JSONResponse({'answer': answer}, status_code=400)
        async def predict():
            text = ""
            import pprint

            # chunks = []
            start_final: bool = False
            start_stream: bool = False
            print("===============================")
            async for chunk in model.agent_executor.astream_events(
                    input="hello", version="v2", include_names="ChatZhipuAI"
            ):
                # chunks.append(chunk)
                # print("-----------------------")
                # pprint.pprint(chunk, depth=5)
                if "chunk" in chunk["data"]:

                    # pprint.pprint(chunk["data"]["chunk"], depth=5)
                    if isinstance(chunk["data"]["chunk"], AIMessageChunk):
                        # 提取content值
                        content = getattr(chunk["data"]["chunk"], "content", None)
                        if content:
                            # print("-----------------------")
                            # print("Content:", content)

                            if start_stream:
                                print(content, end='')
                                js_data = {
                                    "message": content,
                                }
                                json_data = json.dumps(js_data, ensure_ascii=False)
                                yield f"data: {json_data}\n\n"
                                text += content

                            if "Final" in content:
                                start_final = True

                            if (start_final) and ":" in content:
                                start_stream = True

            json_data = json.dumps({"message": 'done'})
            yield f"data: {json_data}\n\n"  # 按照SSE格式发送数据
            print(text)

        headers = {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }

        generate = predict()
        return StreamingResponse(generate, media_type="text/event-stream", headers=headers)

    except Exception as e:
        print(f"An exception occurred: {e}")


@app.get("/id")
async def get_id():
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
        return JSONResponse({'error': {e}}, status_code=200)
    return JSONResponse({'uid': uid}, status_code=400)


# 当这个脚本作为主程序运行时，这段代码将启动 uvicorn 服务器。
# "fastapi:app" 指定了模块名和实例名
if __name__ == "__main__":
    uvicorn.run("1fastapi:app", host="127.0.0.1", port=8000, reload=True)
    # 想在这里进行一些初始化操作
