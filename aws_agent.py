from langchain import hub
from langchain.agents import AgentExecutor, create_react_agent
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from aws_tools import aws_tools

model = "gpt-4"
llm = ChatOpenAI(temperature=0.1, model=model)

# modified the generic hwchase17/react to only answer questions about aws
prompt_text = '''
Answer the following questions as best you can. You have access to the following tools:

{tools}
Only answer questions related to this Amazon account or AWS. If the tools provided do not cover the question then give the user a generic response to as another question related to this AWS account.

Use the following format:

Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation can repeat N times)
Thought: I now know the final answer
Final Answer: the final answer to the original input question

Begin!

Question: {input}
Thought:{agent_scratchpad}
'''

prompt = PromptTemplate.from_template(prompt_text)

agent = create_react_agent(
    tools=aws_tools,
    llm=llm,
    prompt=prompt

)

# Create an agent executor by passing in the agent and tools
agent_executor = AgentExecutor(agent=agent, tools=aws_tools, verbose=False)

print("\nHi I am a chat bot connected to your AWS account ask me any questions about your account.\n\tType q to quit the program.\n")
question = "" #example: Get public S3 buckets."
while question != "q":
    
    if question != "":
        response = agent_executor.invoke({"input": question})
        print("\nAWS Chatbot:",response['output'])
    
    
    question = input("\nUser: ")
