import os
import logging
from anthropic import Anthropic
import chromadb
from langchain.text_splitter import RecursiveCharacterTextSplitter
from chromadb.utils import embedding_functions
from dotenv import load_dotenv

load_dotenv(".env")

logger = logging.getLogger(__name__)

SYSTEM_MESSAGE = (
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
    "See Section 'Chain' in the maintenance manual OR "
    "http://www.buffalobicycle.com/storage/documents/wbr_bicycle_maintenance_manual.pdf."
)

# Shared ChromaDB client — initialised once, reused across all user agents
_chroma_client = chromadb.PersistentClient(path="/tmp/chroma_db")

_text_splitter = RecursiveCharacterTextSplitter(
    separators=["\n\n", "\n", "\r", "\t"]
)


class BuffaloBuffAgent:
    """RAG agent that uses ChromaDB for retrieval and Anthropic Claude for generation."""

    def __init__(self):
        self.client = Anthropic()
        self.chat_history = []

        default_ef = embedding_functions.DefaultEmbeddingFunction()

        self.collection = _chroma_client.get_or_create_collection(
            name="buffalo_manual",
            embedding_function=default_ef,
        )

        self._index_manual_if_needed()

        logger.info("Initialized BuffaloBuffAgent successfully.")

    def _index_manual_if_needed(self):
        """Index the Buffalo Bikes Maintenance Manual into ChromaDB if not already done."""
        if self.collection.count() > 0:
            logger.info(
                f"Collection already has {self.collection.count()} documents, skipping indexing."
            )
            return

        manual_url = "http://www.buffalobicycle.com/storage/documents/wbr_bicycle_maintenance_manual.pdf"
        logger.info(f"Downloading and indexing manual from {manual_url}")

        try:
            import urllib.request
            import tempfile

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                urllib.request.urlretrieve(manual_url, tmp.name)
                tmp_path = tmp.name

            try:
                from langchain_community.document_loaders import PyPDFLoader

                loader = PyPDFLoader(tmp_path)
                pages = loader.load()
                full_text = "\n\n".join([page.page_content for page in pages])
            except ImportError:
                logger.warning(
                    "PyPDFLoader not available, attempting basic text extraction."
                )
                full_text = ""

            if full_text:
                chunks = _text_splitter.split_text(full_text)
                ids = [f"chunk_{i}" for i in range(len(chunks))]
                self.collection.add(documents=chunks, ids=ids)
                logger.info(f"Indexed {len(chunks)} chunks from the manual.")
            else:
                logger.warning("No text extracted from manual PDF.")

            os.unlink(tmp_path)
        except Exception as e:
            logger.exception(f"Failed to index manual: {e}")

    def _retrieve_context(self, query: str, n_results: int = 3) -> str:
        """Retrieve relevant context from ChromaDB for the given query."""
        try:
            results = self.collection.query(query_texts=[query], n_results=n_results)
            if results and results["documents"] and results["documents"][0]:
                context_chunks = results["documents"][0]
                return "\n\n---\n\n".join(context_chunks)
        except Exception as e:
            logger.exception(f"Error retrieving context: {e}")
        return ""

    def chat(self, user_message: str) -> str:
        """
        Send a message and get a response using RAG with Anthropic Claude.

        Args:
            user_message: The user's message text.

        Returns:
            The assistant's response text.
        """
        context = self._retrieve_context(user_message)

        augmented_message = user_message
        if context:
            augmented_message = (
                f"Relevant context from the Buffalo Bikes Maintenance Manual:\n\n"
                f"{context}\n\n---\n\n"
                f"User question: {user_message}"
            )

        self.chat_history.append({"role": "user", "content": augmented_message})

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=4096,
                system=SYSTEM_MESSAGE,
                messages=self.chat_history,
            )
            assistant_message = response.content[0].text
            self.chat_history.append(
                {"role": "assistant", "content": assistant_message}
            )
            logger.info(f"Generated response: {assistant_message[:100]}...")
            return assistant_message
        except Exception as e:
            logger.exception(f"Error calling Anthropic API: {e}")
            return "I'm sorry, I couldn't generate a response right now. Please try again later."

    def reset(self):
        """Clear the chat history."""
        self.chat_history = []


def fetch_agent() -> BuffaloBuffAgent:
    """
    Initializes and returns a BuffaloBuffAgent.

    Returns:
        BuffaloBuffAgent: The initialized agent.
    """
    return BuffaloBuffAgent()
