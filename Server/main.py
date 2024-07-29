import json
from fastapi import FastAPI
import uvicorn  # web server 一个轻量级的 ASGI 服务器，用于运行 FastAPI 应用。
from fastapi import Request
from langchain_core.messages import AIMessageChunk
from starlette.responses import JSONResponse, StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from RetrievalChain import DocumentRetriever, RetrievalChain
from typing import List, Dict, Any
# from SingleAgent import SingleAgent
from source import options, generator, idregister
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 这样的话没法多线程，理论上应该在创建新连接时对于每个新连接创建新model
# model = SingleAgent()
document_retriever = DocumentRetriever()
new_retriever_chain = RetrievalChain(document_retriever)
retrieval_chain = new_retriever_chain.chat()
chat_history: List[Any] = []


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# 前端应该要传给后端question和自身id，apikey，id用于确定询问者身份和对话编号（比如一个人可以开启多个对话），apikey用于验证是否有权限对话



@app.get("/chat")
async def retrieval_stream(query: str = "你是谁"):
    try:
        human_message: str = query
        if not human_message:
            return JSONResponse({'error': 'No question provided'}, status_code=400)

        def retrieval_predict():
            ai_message: str = ""
            response_iter = retrieval_chain.stream({
                "chat_history": chat_history,
                "input": human_message
            })
            for chunk in response_iter:
                # print(chunk, end='', flush=True)
                if isinstance(chunk, dict):
                    if 'answer' in chunk:
                        ai_message = ai_message + chunk['answer']
                        # print(chunk['answer'], end="")
                        js_data = {
                            "message": chunk['answer']
                        }
                        json_data = json.dumps(js_data, ensure_ascii=False)
                        yield f"data: {json_data}\n\n"

            chat_history.append(HumanMessage(content=human_message))
            chat_history.append(AIMessage(content=ai_message))
            json_data = json.dumps({"message": 'done'})
            yield f"data: {json_data}\n\n"  # 按照SSE格式发送数据

        headers = {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }

        generate = retrieval_predict()
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
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
    # 想在这里进行一些初始化操作
