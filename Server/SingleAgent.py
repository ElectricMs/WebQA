from RAGModel import RAGModel

from langchain.agents import AgentExecutor, AgentOutputParser
from langchain.memory import ConversationBufferMemory
from langchain.schema import AgentAction, AgentFinish
from typing import Union
import re
import time
from langchain.agents import create_structured_chat_agent
from langchain import hub


class SingleAgent(RAGModel):
    def __init__(self):

        start_time = time.time()

        from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

        system = '''Respond to the human as helpfully and accurately as possible. You have access to the following tools:

                    {tools}

                    Use a json blob to specify a tool by providing an action key (tool name) and an action_input key (tool input).

                    Valid "action" values: "Final Answer" or {tool_names}

                    Provide only ONE action per $JSON_BLOB, as shown:

                    ```
                    {{
                      "action": $TOOL_NAME,
                      "action_input": $INPUT
                    }}
                    ```

                    Follow this format:

                    Question: input question to answer
                    Thought: consider previous and subsequent steps
                    Action:
                    ```
                    $JSON_BLOB
                    ```
                    Observation: action result
                    ... (repeat Thought/Action/Observation N times)
                    Thought: I know what to respond
                    Action:
                    ```
                    {{
                      "action": "Final Answer",
                      "action_input": "Final response to human"
                    }}

                    Begin! Reminder to ALWAYS respond with a valid json blob of a single action. Use tools if necessary. Respond directly if appropriate. Format is Action:```$JSON_BLOB```then Observation'''

        human = '''Previous conversation history:
                    {chat_history}
                    
                    {input}

                    {agent_scratchpad}

                    (reminder to respond in a JSON blob no matter what)'''

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system),
                # MessagesPlaceholder("chat_history", optional=True),
                ("human", human),
            ]
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

        self.agent = create_structured_chat_agent(
            llm=RAGModel.chat_model,
            tools=RAGModel.tools,
            prompt=self.prompt,
            # prompt=hub.pull("stepbystep/conversational-agent"),
        )

        # 多轮对话
        self.memory = ConversationBufferMemory(memory_key="chat_history")
        self.agent_executor = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=RAGModel.tools,
            memory=self.memory,
            verbose=True,
            handle_parsing_errors=True,
        )

        end_time = time.time()
        print("SingleAgent Init Done", "(", end_time - start_time, "s)!")

    def generate_answer(self, question):
        return self.agent_executor.invoke({"input": question})
