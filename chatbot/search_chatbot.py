from typing import List, Dict
from langgraph.graph import StateGraph, START, END
from langchain_ollama.llms import OllamaLLM
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ChatbotEngine:
    def __init__(self):
        self.initialize_chatbot()
        self.conversation_history = []  # Add conversation history

    def initialize_chatbot(self):
        # define state
        class State(Dict):
            messages: List[Dict[str, str]]

        # Initialize the stategraph
        self.graph_builder = StateGraph(State)

        try:
            # Use llama2
            self.llm = OllamaLLM(
                model="llama2", temperature=0.7, top_k=10, top_p=0.9, repeat_penalty=1.1
            )
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

    def format_conversation_history(self):
        formatted_history = ""
        for entry in self.conversation_history:
            formatted_history += (
                f"Human: {entry['user']}\nAssistant: {entry['assistant']}\n\n"
            )
        return formatted_history

    def chatbot(self, state: Dict):
        try:
            # Get the current message
            current_message = state["messages"][0]["content"]

            # Create context with conversation history
            context = f"""Previous conversation:\n{self.format_conversation_history()}
Current message: {current_message}
Please provide a helpful response."""

            response = self.llm.invoke(context)

            # Add to conversation history
            self.conversation_history.append(
                {"user": current_message, "assistant": response}
            )

            state["messages"].append({"role": "assistant", "content": response})
            return {"messages": state["messages"]}
        except Exception as e:
            logger.error(f"Error in chatbot: {str(e)}")
            raise

    def get_response(self, user_input: str):
        try:
            # initialize the state with user's input
            state = {"messages": [{"role": "user", "content": user_input}]}
            result = self.graph.invoke(state)
            return result["messages"][-1]["content"]
        except Exception as e:
            logger.error(f"Error getting response: {str(e)}")
            raise


def main():
    try:
        print("Initializing chatbot...")
        chatbot = ChatbotEngine()
        print("\nChatbot initialized. Type 'quit'.'q', or 'exit' to exit.")
        print("You can start chatting now!")

        while True:
            user_input = input("\nYou: ").strip()
            if user_input.lower() in ["quit", "q", "exit"]:
                print("Goodbye!")
                break

            if not user_input:
                continue

            try:
                response = chatbot.get_response(user_input)
                print(f"\nBot: {response}")
            except Exception as e:
                print(f"\nError: Something went wrong - {str(e)}")
                print("Please try again or type 'quit' to exit.")

    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        raise


if __name__ == "__main__":
    main()
