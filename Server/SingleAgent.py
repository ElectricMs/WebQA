from RAGModel import RAGModel

from langchain.agents import AgentExecutor, LLMSingleActionAgent, AgentOutputParser
from langchain.memory import ConversationBufferMemory
from langchain import LLMChain
from langchain.schema import AgentAction, AgentFinish
from typing import Union
import re
import time
import asyncio

class SingleAgent(RAGModel):
    def __init__(self):

        start_time = time.time()
        self.prompt = RAGModel.CustomPromptTemplate(
            template=RAGModel.template,
            tools=RAGModel.tools,
            # This omits the `agent_scratchpad`, `tools`, and `tool_names` variables because those are generated dynamically
            # This includes the `intermediate_steps` variable because that is needed
            input_variables=["input", "intermediate_steps", "chat_history"]
        )

        class CustomOutputParser(AgentOutputParser):
            def parse(self, llm_output: str) -> Union[AgentAction, AgentFinish]:
                # Check if agent should finish
                if "Final Answer:" in llm_output:
                    return AgentFinish(
                        # Return values is generally always a dictionary with a single `output` key
                        # It is not recommended to try anything else at the moment :)
                        return_values={"output": llm_output.split("Final Answer:")[-1].strip()},
                        log=llm_output,
                    )
                # Parse out the action and action input
                regex = r"Action\s*\d*\s*:(.*?)\nAction\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
                match = re.search(regex, llm_output, re.DOTALL)
                if not match:
                    return AgentFinish(
                        return_values={"一个可能的回答是：": llm_output.strip()},
                        log=llm_output,
                    )
                action = match.group(1).strip()
                action_input = match.group(2)
                # Return the action and action input
                return AgentAction(tool=action, tool_input=action_input.strip(" ").strip('"'), log=llm_output)

        self.output_parser = CustomOutputParser()

        # LLM chain consisting of the LLM and a prompt
        self.llm_chain = LLMChain(llm=RAGModel.chat_model, prompt=self.prompt)

        tool_names = [tool.name for tool in RAGModel.tools]

        self.agent = LLMSingleActionAgent(
            llm_chain=self.llm_chain,
            output_parser=self.output_parser,
            stop=["\nObservation:", "\n\nObservation"],
            allowed_tools=tool_names
        )
        # 多轮对话
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent_executor = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=RAGModel.tools, verbose=True,
                                                                 memory=self.memory)

        end_time = time.time()
        print("Done", "(", end_time - start_time, "s)!")

    def generate_answer(self, question):
        return self.agent_executor.invoke(question)

    def stream_answer(self, question):
        return self.agent_executor.invoke(question)
