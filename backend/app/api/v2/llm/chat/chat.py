import dotenv, os
dotenv.load_dotenv()

from langchain.chat_models import init_chat_model
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.graph import START, MessagesState, StateGraph

model = init_chat_model("gpt-4o-mini", model_provider="openai", api_key=os.getenv("OPENAI_API_KEY"))

'''
Use LangGraph to make persist memory
'''
# Define a new graph
workflow = StateGraph(state_schema=MessagesState)

# Define the function that calls the model
def call_model(state: MessagesState):
    response = model.invoke(state["messages"])
    return {"messages": response}

# Define the (single) node in the graph
workflow.add_edge(START, "model")
workflow.add_node("model", call_model)

# Add memory
memory = MemorySaver()
app = workflow.compile(checkpointer=memory)

# api handler
async def chat(query: str, thread_id=None):
    
    ## config - allow multiple threads to run with a single app
    if thread_id is None:
        thread_id = "abc123"
    config = {"configurable": {"thread_id": thread_id}}

    input_messages = [HumanMessage(query)]

    async for msg, metadata in app.astream({"messages": input_messages}, config, stream_mode="messages"):
        # print(metadata)
        yield msg.content