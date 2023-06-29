import os
import sys
import io
import app.print_format as pf

from flask import Flask, request, jsonify, render_template, Response, abort
from google.cloud import bigquery
from langchain.agents import create_sql_agent, AgentExecutor
from langchain.agents.agent_toolkits import SQLDatabaseToolkit
from langchain.llms.openai import OpenAI
from langchain.sql_database import SQLDatabase
from langchain.chat_models import ChatOpenAI


# Load configuration from environment variables
def load_config():
    x_auth = os.environ.get("X_AUTH", "")
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
        "verbose": verbose,
        "x_auth": x_auth
    }

def execute_and_capture_output(func, *args, **kwargs):
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = io.StringIO()
    sys.stdout = redirected_output
    sys.stderr = redirected_output
    result = None
    try:
        result = func(*args, **kwargs)
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
    output = redirected_output.getvalue()
    return result, output

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
# sys.stdout = open('output.log', 'w')
# sys.stderr = sys.stdout

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/stream')
def stream():
    def generate():
        log_file = open('output.log', 'r')  # Open a log file for appending

        while True:
            line = log_file.readline()  # Read a line from the log file
            if not line:
                continue
            yield f"data: {line}\n\n"  # Yield the line as a server-sent event (SSE)

    return Response(generate(), mimetype='text/event-stream')

@app.route('/execute', methods=['POST'])
def execute():

    x_auth_header = request.headers.get('x-auth')
    expected_x_auth = config["x_auth"]
    
    if expected_x_auth and x_auth_header != expected_x_auth:
        abort(401)  # Unauthorized

    with open('output.log', 'w') as file:
        file.truncate()

    query = request.json.get('query')

    # Create SQLDatabase and language model instances
    db = create_sql_database()
    llm = create_language_model()
   
    # Create SQLDatabaseToolkit
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # Create SQL Agent Executor
    agent_executor = create_agent_executor(llm=llm, toolkit=toolkit, verbose=config["verbose"], top_k=config["top_k"])

    # Execute query
    result, output = execute_and_capture_output(agent_executor.run, query)
   
    queryResult = pf.get_query(output)
    output = pf.remove_colors(output)

    return jsonify({"print": output, "output": result, "query": queryResult })

def create_sql_database():
    sqlalchemy_url = f'bigquery://{config["project"]}/{config["dataset"]}?credentials_path={config["service_account_file"]}'
    return SQLDatabase.from_uri(sqlalchemy_url)

def create_language_model():
    temperature = 0
    model = config["model"]
    if model.startswith("gpt"):
        return ChatOpenAI(temperature=temperature, model=model)
    else:
        return OpenAI(temperature=temperature, model=model)

def create_agent_executor(llm, toolkit, verbose, top_k):
    return create_sql_agent(llm=llm, toolkit=toolkit, verbose=verbose, top_k=top_k)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
