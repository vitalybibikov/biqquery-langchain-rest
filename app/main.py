import os
from flask import Flask, request, jsonify
from google.cloud import bigquery
from langchain.agents import create_sql_agent, AgentExecutor
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.llms.openai import OpenAIChat, OpenAI
from langchain.sql_database import SQLDatabase

# Load configuration from environment variables
def load_config():
    service_account_file = get_env_variable("SERVICE_ACCOUNT_FILE")
    project = get_env_variable("PROJECT")
    dataset = get_env_variable("DATASET")
    openai_api_key = get_env_variable("OPENAI_API_KEY")
    model = get_env_variable("MODEL")
    top_k = int(get_env_variable("TOP_K"))
    debug = get_env_variable("DEBUG") == "True"
    verbose = get_env_variable("LANGCHAIN_VERBOSE") == "True"

    return {
        "service_account_file": service_account_file,
        "project": project,
        "dataset": dataset,
        "openai_api_key": openai_api_key,
        "model": model,
        "top_k": top_k,
        "debug": debug,
        "verbose": verbose
    }

# Function to check if a configuration value was provided
def get_env_variable(var_name):
    try:
        return os.environ[var_name]
    except KeyError:
        error_msg = f"The environment variable {var_name} was not provided!"
        raise Exception(error_msg)

config = load_config()

# Set Environment Variable
os.environ["OPENAI_API_KEY"] = config["openai_api_key"]

app = Flask(__name__)

@app.route('/execute', methods=['POST'])
def execute():
    query = request.json.get('query')

    # Create SQLDatabase and language model instances
    db = create_sql_database()
    llm = create_language_model()

    # Create SQLDatabaseToolkit
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # Create SQL Agent Executor
    agent_executor = create_agent_executor(llm=llm, toolkit=toolkit, verbose=config["verbose"], top_k=config["top_k"])

    # Execute query
    result = agent_executor.run(query)
    return jsonify(result)

def create_sql_database():
    sqlalchemy_url = f'bigquery://{config["project"]}/{config["dataset"]}?credentials_path={config["service_account_file"]}'
    return SQLDatabase.from_uri(sqlalchemy_url)

def create_language_model():
    temperature = 0
    model = config["model"]
    if model.startswith("gpt"):
        return OpenAIChat(temperature=temperature, model=model)
    else:
        return OpenAI()

def create_agent_executor(llm, toolkit, verbose, top_k):
    return create_sql_agent(llm=llm, toolkit=toolkit, verbose=verbose, top_k=top_k)

if __name__ == '__main__':
    app.run(debug=config["debug"], host='0.0.0.0')
