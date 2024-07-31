from dotenv import load_dotenv
from langchain_community.chat_models import ChatZhipuAI
from langchain_community.chat_models import ChatOpenAI
from langchain_community.chat_models import ChatSparkLLM


class Model:
    def __init__(self, model_name: str = "ZhipuAI"):
        self.model_name = model_name
        load_dotenv()
        # if model_name == "SparkLLM":
        #     self.chat_model = ChatSparkLLM(
        #         temperature=0.2,
        #         streaming=True,
        #     )
        #     print("initialize SparkLLM")
        if model_name == "OpenAI":
            self.chat_model = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.2,
                streaming=True,
            )
            print("initialize OpenAI")
        else:
            self.chat_model = ChatZhipuAI(
                temperature=0.2,
                streaming=True,
            )
            print("initialize ZhipuAI")
