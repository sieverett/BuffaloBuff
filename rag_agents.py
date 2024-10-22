import os
import logging
from autogen.agentchat.contrib.retrieve_assistant_agent import RetrieveAssistantAgent
from autogen.agentchat.contrib.retrieve_user_proxy_agent import RetrieveUserProxyAgent
from autogen import ConversableAgent, Agent
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv('.env')

# Configure logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def send_messages(recipient, messages, sender, config):
    """
    Handles sending messages between the assistant and the user.

    Args:
        recipient: The recipient of the message.
        messages: List of message dictionaries.
        sender: The sender of the message.
        config: Configuration dictionary.

    Returns:
        Tuple containing messages and any additional data.
    """
    # For debugging purposes, log the messages
    logger.debug(f"Messages before role fix: {messages}")

    # Fix role assignments
    for message in messages:
        if message["name"] == "ragproxyagent":
            message["role"] = "user"
        elif message["name"] == "assistant":
            message["role"] = "assistant"

    # Log the fixed messages
    logger.debug(f"Messages after role fix: {messages}")

    return messages, None


def fetch_agent() -> ConversableAgent:
    """
    Initializes and returns the RetrieveUserProxyAgent and RetrieveAssistantAgent.

    Returns:
        Tuple containing ragproxyagent and assistant.
    """

    config_list = [
        {
            "model": os.environ.get("DEPLOYMENT_NAME"),
            "api_type": "azure",
            "api_key": os.environ.get("AZURE_OPENAI_API_KEY"),
            "base_url": os.environ.get("AZURE_OPENAI_ENDPOINT"),
            "api_version": "2023-03-15-preview",
            "temperature": 0.8,
        }
    ]

    openai_embedding_function = embedding_functions.OpenAIEmbeddingFunction(
        api_key=os.getenv("AZURE_OPENAI_API_KEY")
    )

    text_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", "\r", "\t"]
    )

    assistant = RetrieveAssistantAgent(
        name="assistant",
        system_message=(
            "Your name is BuffaloBuff. "
            "You offer mechanical support for Buffalo bikes with simple, "
            "concise explanations at a fifth-grade reading level. "
            "Make sure the user has a Buffalo Bike before you dispense advice. "
            "Ask clarifying questions to make sure you understand the problem. "
            "Maintain a friendly and approachable tone. "
            "Remember: only provide SHORT and concise answers. "
            "DO NOT answer questions that are not directly related "
            "to maintenance of a buffalo bike. "
            "Response should be a string not Markdown format. "
            "Avoid technical jargon, but use it if the user is comfortable with it. "
            "Provide methods to diagnose problems one method at a time. "
            "Provide lists of necessary items and tools to fix the problem based "
            "on the Buffalo Bikes Maintenance Manual ONLY. "
            "Cite the section of the manual the info comes from if available, "
            "otherwise if you have not already given the link to the manual, provide it: "
            "Example citation: "
            "See Section 'Chain' in the maintenance manual on page 5. "
            "OR "
            "http://www.buffalobicycle.com/storage/documents/wbr_bicycle_maintenance_manual.pdf. "
            "OR "
            "No reference available."
        ),
        llm_config={
            "timeout": 600,
            "cache_seed": 42,
            "config_list": config_list,
        },
    )

    ragproxyagent = RetrieveUserProxyAgent(
        name="ragproxyagent",
        human_input_mode="ALWAYS",
        max_consecutive_auto_reply=3,
        retrieve_config={
            "task": "code",
            "docs_path": [
                "http://www.buffalobicycle.com/storage/documents/wbr_bicycle_maintenance_manual.pdf"
            ],
            "custom_text_types": ["mdx"],
            "chunk_token_size": 2000,
            "model": config_list[0]["model"],
            "client": chromadb.PersistentClient(path="/tmp"),
            "embedding_model": openai_embedding_function,
            "get_or_create": True,  # set to False if you don't want to reuse an existing collection
            "custom_text_split_function": text_splitter.split_text,
        },
        code_execution_config=False,  # set to False if you don't want to execute the code
    )

    ragproxyagent.register_reply(
        [Agent, None],
        reply_func=send_messages,
        config={"callback": None},
    )

    logger.info(
        "Initialized RetrieveUserProxyAgent and RetrieveAssistantAgent successfully."
    )

    return ragproxyagent, assistant
