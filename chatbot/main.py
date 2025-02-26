from typing import List, Dict
from langgraph.graph import StateGraph, START, END
from langchain_ollama.llms import OllamaLLM
import logging
import tkinter as tk
from chatbot_interface import ChatbotGUI

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatbotEngine:
    def __init__(self):
        self.initialize_chatbot()

    def initialize_chatbot(self):
        # define state
        class State(Dict):
            messages: List[Dict[str, str]]

        # Initialize the stategraph
        self.graph_builder = StateGraph(State)

        try:
            # Use llama2
            self.llm = OllamaLLM(model="llama2", temperature=0.7)
            # Test the connection
            logger.info("Testing LLM connection...")
            self.llm.invoke("Test")
            logger.info("LLM connection successful")
        except ConnectionError:
            logger.error(
                "Could not connect to Ollama. Please ensure Ollama is running."
            )
            raise
        except Exception as e:
            logger.error(f"Error initializing LLM: {str(e)}")
            raise

        # Add nodes and edges to the state machine Stategraph
        self.graph_builder.add_node("chatbot", self.chatbot)
        self.graph_builder.add_edge(START, "chatbot")
        self.graph_builder.add_edge("chatbot", END)

        # compile the graph
        self.graph = self.graph_builder.compile()

    def chatbot(self, state: Dict):
        try:
            response = self.llm.invoke(state["messages"])
            state["messages"].append({"role": "assistant", "content": response})
            return {"messages": state["messages"]}
        except Exception as e:
            logger.error(f"Error in chatbot: {str(e)}")
            raise

    def stream_graph_updates(self, usr_input: str):
        try:
            # initialize the state with user's input
            state = {"messages": [{"role": "user", "content": usr_input}]}
            for event in self.graph.stream(state):
                for value in event.values():
                    yield value["messages"][-1]["content"]
        except Exception as e:
            logger.error(f"Error in stream_graph_updates: {str(e)}")
            raise


def main():
    try:
        root = tk.Tk()
        chatbot_engine = ChatbotEngine()
        app = ChatbotGUI(root, chatbot_engine)
        root.mainloop()
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
