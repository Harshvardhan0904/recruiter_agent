from agno.agent import Agent
from agno.models.groq import Groq
from dotenv import load_dotenv
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.python import PythonTools
from agno.tools.googlesearch import GoogleSearchTools
import pandas as pd
import openpyxl as xl
import re
import os
import ast

# Load environment variables
load_dotenv()

# Ensure Groq API key is set
API_KEY = os.getenv("GROQ_API_KEY")
if not API_KEY:
    raise ValueError("GROQ_API_KEY is not set. Add it to your .env file or set it manually.")

os.environ["GROQ_API_KEY"] = API_KEY  # Ensure it's available in the environment

agent2 = Agent(
    model=Groq(id="qwen-2.5-32b"),
    description="You are an assistant for writing Python code.",
    tools=[PythonTools()],
    markdown=True
)






def get_jobs(promt):
    agent3 = Agent(
        model=Groq(id="qwen-2.5-32b"),
        description="You are an assistant for Searching MAX 5 jobs.",
        tools=[GoogleSearchTools()],
        instructions=[
            "Given a topic by the user, respond with 5 latest news items about that topic.",
            "Search for 5 Jobs recently posted.",
            "Search in English", "the output should be strictly JSON","title should be the platform name only and desc should be short"
        ],
        debug_mode=False,
    )
    
    res = agent3.run(f"return 5 recent jobs or internships that are in india related to {promt} skills given by user. It should be in JSON format.")
    res = str(res)

    title = re.findall(r'"title":\s*"([^"]+)"', res)
    url = re.findall(r'"url":\s*"([^"]+)"', res)
    desc = re.findall(r'"description":\s*"([^"]+)"', res)

    max_length = max(len(title), len(desc), len(url))

    title += [""] * (max_length - len(title))
    desc += [""] * (max_length - len(desc))
    url += [""] * (max_length - len(url))

    df = pd.DataFrame({"title":title , "desc":desc,"url":url})

    title_list  = [i for i in df["title"].head(5)]
    url_list  =[i for i in df["url"].head(5)]
    desc_list  = [i.replace("\\u00b7 ", ".").replace("\ ","").replace("/","").strip() for i in df["desc"].head(5)]

    return title_list,url_list,desc_list

def get_ques(prompt):
    agent1 = Agent(
    model=Groq(id="qwen-2.5-32b"),  # Use Groq, NOT OpenAI
    description="You are an assistant for providing question to the user related to their skills the user.",
    tools=[GoogleSearchTools()],
    markdown=True
    )

    res = agent1.run(f"return 20 interview questions related to {prompt} skills given by user. It should be in JSON format.")
    res = str(res)
    try:
        pattern = r'```(?:[^\n]*\n)?([\s\S]*?)```'
        matches = re.findall(pattern, res)
        code_blocks = [block.strip() for block in matches]
        code_blocks = [i.replace("\\n","").replace("  ","").replace("'","").strip() for i in code_blocks]
        text = code_blocks[0].replace("json",'')
        text  = ast.literal_eval(text)
    except Exception as e:
        print("error",e)
        
    return text


