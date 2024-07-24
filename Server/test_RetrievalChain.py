from langchain_core.messages import HumanMessage, AIMessage
from RetrievalChain import DocumentRetriever, RetrievalChain
from typing import List, Dict, Any

document_retriever = DocumentRetriever()
new_retriever_chain = RetrievalChain(document_retriever)
retrieval_chain = new_retriever_chain.chat()
chat_history: List[Any] = []
# human_message: str = '天津市滨海新区东疆保税港区观澜路(贻海观澜南边)交通指南'
# response = retrieval_chain.invoke({
#     "chat_history": chat_history,
#     "input": human_message
# })
# print(response)


while True:
    human_message: str = input("请输入天津生活问题")
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
                print(chunk['answer'], end="")
    print("\n--------------------------------------------")
    print(chat_history)
    print("--------------------------------------------")
    chat_history.append(HumanMessage(content=human_message))
    chat_history.append(AIMessage(content=ai_message))


