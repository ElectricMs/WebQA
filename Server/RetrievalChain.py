from typing import Dict, List, Any
from langchain_core.runnables import Runnable


class DocumentRetriever:
    def __init__(self):
        print("Initializing new retriever...")
        import time
        start_time = time.time()
        from langchain_huggingface import HuggingFaceEmbeddings
        from langchain_community.vectorstores import FAISS
        from dotenv import load_dotenv
        load_dotenv()

        # 构建语言模型
        from langchain_community.chat_models import ChatZhipuAI

        self.chat_model = ChatZhipuAI(
            temperature=0.2,
            streaming=True,
        )

        EMBEDDING_DEVICE = "cpu"
        embeddings = HuggingFaceEmbeddings(
            model_name="models/m3e-base-huggingface",  # 指定使用的模型名称
            model_kwargs={"device": EMBEDDING_DEVICE},  # 传递模型参数，指定设备类型
            show_progress=True,  # 显示进度条
        )
        # print(embeddings)

        vector = FAISS.load_local("./vectors_bin", embeddings, allow_dangerous_deserialization=True)
        print(vector)

        # 生成一个基于向量存储的检索器
        self.retriever = vector.as_retriever()

        end_time = time.time()
        print("Done", "(", end_time - start_time, "s)!")


class RetrievalChain:
    def __init__(self, document_retriever: DocumentRetriever):
        self.document_retriever = document_retriever

    def chat(self) -> Runnable:
        # 链：接受最近的输入+会话历史
        from langchain.chains import create_history_aware_retriever
        from langchain_core.prompts import MessagesPlaceholder, ChatPromptTemplate
        from langchain.chains.combine_documents import create_stuff_documents_chain
        from langchain.chains.retrieval import create_retrieval_chain

        # 生成ChatModel会话的提示词
        history_prompt = ChatPromptTemplate.from_messages([
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
            ("user", "Given the above conversation, generate a search query to "
                     "look up in order to get information relevant to the conversation")
        ])
        # 生成含有历史信息的检索链
        history_text_retriever_chain = create_history_aware_retriever(self.document_retriever.chat_model,
                                                                      self.document_retriever.retriever,
                                                                      history_prompt)
        prompt = ChatPromptTemplate.from_messages([
<<<<<<< Updated upstream
            ("system", "Answer the user's questions based on the below context:\n\n{context}"),
=======
            ("system", "You are a Tianjin Bear. A prefesssional assistant to answer questions about Tianjin's food, clothing, housing and transportation for xiaoni. Answer the user's questions based on the below context:\n\n{context}"),
>>>>>>> Stashed changes
            MessagesPlaceholder(variable_name="chat_history"),
            ("user", "{input}"),
        ])

        document_chain = create_stuff_documents_chain(self.document_retriever.chat_model, prompt)
        # 最终的检索链
        retrieval_chain = create_retrieval_chain(history_text_retriever_chain, document_chain)

        return retrieval_chain
