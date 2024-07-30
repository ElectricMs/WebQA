import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn  # web server 一个轻量级的 ASGI 服务器，用于运行 FastAPI 应用。
from fastapi import Request
from langchain_core.messages import AIMessageChunk
from langchain_core.runnables import Runnable
from starlette.responses import JSONResponse, StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from RetrievalChain import DocumentRetriever, RetrievalChain
from typing import List, Dict, Any, Optional
from contextlib import asynccontextmanager
# from SingleAgent import SingleAgent
from source import options, generator, idregister
from sql_app.Router import router, TokenVerificationMiddleware

# model: SingleAgent
document_retriever: DocumentRetriever
new_retriever_chain: RetrievalChain
retrieval_chain: Runnable
chat_history: List[Any]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    # global: model
    global document_retriever
    global new_retriever_chain
    global retrieval_chain
    global chat_history
    print("lifespan: loading...")
    # 这样的话没法多线程，理论上应该在创建新连接时对于每个新连接创建新model
    # model = SingleAgent()
    document_retriever = DocumentRetriever()
    new_retriever_chain = RetrievalChain(document_retriever)
    retrieval_chain = new_retriever_chain.chat()
    chat_history = []
    yield
    # Clean up the ML models and release the resources
    print("lifespan:stopping...")


app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 替换为你的客户端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# 注册路由
app.include_router(router)
# 添加中间件到FastAPI应用
app.add_middleware(TokenVerificationMiddleware)

@app.get("/")
async def root():
    return {"message": "Hello World"}




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


@app.get("/chat")
async def retrieval_astream(query: str = "你是谁"):
    try:
        human_message: str = query
        if not human_message:
            return JSONResponse({'error': 'No question provided'}, status_code=400)

        async def retrieval_predict():
            ai_message: str = ""
            response_iter = retrieval_chain.astream({
                "chat_history": chat_history,
                "input": human_message
            })
            async for chunk in response_iter:
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


@app.get("/agent")
async def stream(query: str = "你是谁"):
    try:
        question = query
        if not question:
            return JSONResponse({'error': 'No question provided'}, status_code=400)

        async def predict():
            text = ""
            import pprint

            # chunks = []
            start_final: bool = False
            start_stream: bool = False
            print("===============================")
            async for chunk in model.agent_executor.astream_events(
                    input={"input": question}, version="v2", include_names="ChatZhipuAI"
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

                            if start_final and ":" in content:
                                start_stream = True

            json_data = json.dumps({"message": 'done'})
            yield f"data: {json_data}\n\n"  # 按照SSE格式发送数据
            print(text)

        headers = {
            'Content-Type': 'text/event-stream',
            'Cache-Control': 'no-cache',
            'X-Accel-Buffering': 'no',
        }

        generate = stream()
        return StreamingResponse(generate, media_type="text/event-stream", headers=headers)

    except Exception as e:
        print(f"An exception occurred: {e}")


@app.get("/id")
async def get_id():
    uid: int
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
# "main:app" 指定了模块名和实例名
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=5000, reload=True)
