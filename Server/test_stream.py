import json
#from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from fastapi import FastAPI
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 替换为你的客户端域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#load_dotenv()

import os
# sparkllm 环境变量配置
os.environ["IFLYTEK_SPARK_APP_ID"] = "acc4dd70"
os.environ["IFLYTEK_SPARK_API_KEY"] = "98f96c834ca0ddfdfc461086a014760c"
os.environ["IFLYTEK_SPARK_API_SECRET"] = "NmIwNzU0ZjY1Mjk5NmZiNDM3NTM0ZWZi"
os.environ["IFLYTEK_SPARK_API_URL"] = "wss://spark-api.xf-yun.com/v3.1/chat"
os.environ["IFLYTEK_SPARK_llm_DOMAIN"] = "generalv3"
# sparkllm model
from langchain_community.chat_models import ChatSparkLLM
llm = ChatSparkLLM(streaming=True)

prompt = ChatPromptTemplate.from_messages(
    [("system", "你是一个专业的AI助手。"), ("human", "{query}")]
)

llm_chain = prompt | llm


@app.get("/chat_stream")
def chat_stream(query: str = "你是谁"):
    def predict():
        text = ""
        ret = llm_chain.stream({"query": query})
        for _token in ret:
            token : str = _token.content
            js_data = {
                       "message": token,
                       }
            json_data = json.dumps(js_data, ensure_ascii=False)
            yield f"data: {json_data}\n\n"
            text += token
            # print(token)
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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app=app, host="localhost", port=5000)


