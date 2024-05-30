import random
from autogen import ConversableAgent, UserProxyAgent
# from autogen.agentchat.contrib.web_surfer import WebSurferAgent, UserProxyAgent  # noqa: E402
from dotenv import load_dotenv
import os
load_dotenv('.env')


def fetch_agent() -> ConversableAgent:
    config_list = [
      {
        "model": "gpt-4",
        "api_type": "azure",
        "api_key": os.environ['AZURE_OPENAI_API_KEY'],
        "base_url": os.environ['AZURE_OPENAI_ENDPOINT_GPT4o'],
        "api_version": "2023-03-15-preview"
      }
    ]
    llm_config = {
        "config_list": config_list,
       "timeout": 600,
        "cache_seed": 44

    }

    # num=random.randint(1, 100)
    agent_with_number = ConversableAgent(
        "agent_with_number",
        # system_message="You are playing a game of guess-my-number. You have the "
        # f"number {num} in your mind, and I will try to guess it. "
        # "If I guess too high, say 'too high', if I guess too low, say 'too low'. ",
        system_message="you are a helpful assistant.",
        llm_config=llm_config,
        # is_termination_msg=lambda msg: f"{num}" in msg["content"],  # terminate if the number is guessed by the other agent
        human_input_mode="NEVER",  # never ask for human input
        max_consecutive_auto_reply=1
    )

    human_proxy = UserProxyAgent(
        name="Admin",
        human_input_mode="NEVER",
        code_execution_config=False,
    )

    return human_proxy,agent_with_number