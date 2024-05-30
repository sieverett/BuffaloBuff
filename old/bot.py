import random
from autogen import ConversableAgent, UserProxyAgent, Agent
# from autogen.agentchat.contrib.web_surfer import WebSurferAgent, UserProxyAgent  # noqa: E402
from dotenv import load_dotenv
import os
load_dotenv('.env')

def send_messages(recipient, messages, sender,config):

    #chat_interface.send(messages[-1]['content'], user=messages[-1]['name'], avatar=avatar[messages[-1]['name']], respond=False)
    msg=f"Messages from: {sender.name} sent to: {recipient.name} | num messages: {len(messages)} | message: {messages[-1]}"

    return msg, None



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
        system_message="you are a helpful assistant. you speak in pirate language. arr!",
        llm_config=llm_config,
        # is_termination_msg=lambda msg: f"{num}" in msg["content"],  # terminate if the number is guessed by the other agent
        human_input_mode="NEVER",  # never ask for human input
        max_consecutive_auto_reply=1
    )

    human_proxy = UserProxyAgent(
        name="human_proxy",
        human_input_mode="ALWAYS",
        code_execution_config=False,
    )

    human_proxy.register_reply(
    [Agent, None],
    reply_func=send_messages, 
    config={"callback": None},
  )

    return human_proxy,agent_with_number