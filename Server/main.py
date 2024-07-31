import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn  # web server 一个轻量级的 ASGI 服务器，用于运行 FastAPI 应用。
from fastapi import Request
from langchain_core.messages import AIMessageChunk
from langchain_core.runnables import Runnable
from starlette.middleware import Middleware
from starlette.responses import JSONResponse, StreamingResponse
from langchain_core.messages import HumanMessage, AIMessage
from chat_models.RetrievalChain import DocumentRetriever, RetrievalChain
from chat_models.model import Model
from typing import List, Any, Optional
from contextlib import asynccontextmanager
# from SingleAgent import SingleAgent
from source import options, generator
from sql_app.Router import router, TokenVerificationMiddleware

# model: SingleAgent
document_retriever: DocumentRetriever
# new_retriever_chain: RetrievalChain
# retrieval_chain: Runnable
# chat_history: List[Any]
# zhipuai_model: Model
# openai_model: Model
# sparkllm_model: Model


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Load the ML model
    # global: model
    global document_retriever
    # global new_retriever_chain
    # global retrieval_chain
    # global chat_history
    # global zhipuai_model
    # global openai_model
    # global sparkllm_model
    print("lifespan: loading...")
    # 这样的话没法多线程，理论上应该在创建新连接时对于每个新连接创建新model
    # model = SingleAgent()
    document_retriever = DocumentRetriever()
    # new_retriever_chain = RetrievalChain(document_retriever)  # RetrievalChain类 包含DocumentRetriever类的实例
    # retrieval_chain = new_retriever_chain.chat()  # Runnable
    # chat_history = []

    # initialize chat models
    # zhipuai_model = Model("ZhipuAI")
    # openai_model = Model("OpenAI")
    # sparkllm_model = Model("SparkLLM")

    # 注册路由
    app.include_router(router)
    yield
    # Clean up the ML models and release the resources
    print("lifespan:stopping...")


middleware = [
    Middleware(CORSMiddleware,
        allow_origins=["*"],  # 替换为客户端域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"]
    ),
    Middleware(TokenVerificationMiddleware),
]

app = FastAPI(lifespan=lifespan, middleware=middleware)



@app.get("/")
async def root():
    return {"message": "Hello World"}


# ask路由用于直接和大模型对话，不通过检索链和Agent
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


# chat路由通过检索链实现，目前效果最好
# 需要传入query参数代表问题，chat_model参数代表选取模型，chat_id可选参数代表会话id用于读取历史记录
# 默认的chat_model为ZhipuAI，有效的参数为ZhipuAI，OpenAI，SparkLLM和接下来会添加的本地大模型
# 如果传入的字符参数不属于上述四种则默认为ZhipuAI
# 通过chat_id来寻找对话历史，**后续会在该路由上加上token验证**
@app.get("/chat")
async def retrieval_astream(query: str = "你是谁", chat_model: str = "ZhipuAI", chat_id: Optional[int] = None):
    try:
        # 读取历史记录
        if chat_id:
            # 在这里调用函数检索具体历史记录
            history = []  # 修改此处，给history赋值
            print("loading chat history")
        else:
            history = []  # 未传入chat_id参数，将不会有记忆

        # 读取模型
        model: Model = Model(chat_model)

        # 生成检索链
        # RetrievalChain类 包含DocumentRetriever类的实例
        new_retriever_chain = RetrievalChain(document_retriever=document_retriever, model=model)
        # Runnable
        retrieval_chain = new_retriever_chain.chat()

        human_message: str = query
        if not human_message:
            return JSONResponse({'error': 'No question provided'}, status_code=400)

        async def retrieval_predict():
            ai_message: str = ""
            response_iter = retrieval_chain.astream({
                "chat_history": history,
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

            history.append(HumanMessage(content=human_message))
            history.append(AIMessage(content=ai_message))
            # 在此将history写回Redis
            # 写回过程可能比较耗时 最好能异步或挪到其他地方执行？
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
