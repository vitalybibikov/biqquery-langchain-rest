import os
import sys
import io
import utils as myutils
import logging
import threading
from flask import Flask, request, jsonify, abort
from langchain_community.agent_toolkits import create_sql_agent
from langchain_community.utilities import SQLDatabase
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack import WebClient
from slack_bolt import App
from langchain_community.agent_toolkits import SQLDatabaseToolkit
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAI

logging.basicConfig(level=logging.DEBUG,  # Adjust the level as needed
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Get a logger for this module
logger = logging.getLogger(__name__)

# Add a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(console_handler)

# Set up logging for langchain
logging.getLogger("langchain").setLevel(logging.DEBUG)

# Load configuration from environment variables
def load_config():
    x_auth = os.environ.get("X_AUTH", "")
    slack_bot_app_token = get_env_variable("SLACK_BOT_APP_TOKEN")
    slack_bot_token = get_env_variable("SLACK_BOT_TOKEN")
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
        "x_auth": x_auth,
        "slack_bot_app_token": slack_bot_app_token,
        "slack_bot_token": slack_bot_token
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

# app = Flask(__name__)
# sys.stdout = open('output.log', 'w')
# sys.stderr = sys.stdout


# Event API & Web API
app = App(token=config["slack_bot_token"]) 
client = WebClient(config["slack_bot_token"])
flask = Flask(__name__)

# This gets activated when the bot is tagged in a channel    
@app.event("app_mention")
def handle_message_events(body, logger):

    logger.info("Start")
    logger.info(body)
    # Create prompt for ChatGPT
    prompt = str(body["event"]["text"]).split(">")[1]
    
    # Let the user know that we are busy with the request 
    response = client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"Hello from your bot! :robot_face: \nThanks for your request, I'm on it!")

    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # Create SQL Agent Executor
    agent_executor = create_agent_executor(llm=llm, toolkit=toolkit, verbose=True, top_k=10000)

    # Execute query
    result, output = execute_and_capture_output(agent_executor.run, prompt)

    logger.info(output);
    logger.info(result);

    queryResult = myutils.get_query(output).replace('"', '')
    output = myutils.remove_colors(output)

    # Reply to thread 
    client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"Here you go: \n{output}")
    
    client.chat_postMessage(channel=body["event"]["channel"], 
                                       thread_ts=body["event"]["event_ts"],
                                       text=f"Query: \n{queryResult}")


@flask.route('/hc', methods=['GET'])
def healthcheck():
    return jsonify({"status": "ok"})


def startapp():
    print("Start")
    flask.run(debug=True, use_reloader=False, host='0.0.0.0')

@flask.route('/challenge', methods=['POST'])
def challenge():
    data = request.get_json()
    if data is not None:
        challenge = data.get('challenge')
        return challenge
    else:
        return 'No JSON payload found', 400

@flask.route('/execute', methods=['POST'])
def execute():

    x_auth_header = request.headers.get('x-auth')
    expected_x_auth = config["x_auth"]
    
    if expected_x_auth and x_auth_header != expected_x_auth:
        abort(401)  # Unauthorized

    query = request.json.get('query')

    # Create SQLDatabase and language model instances
    db = create_sql_database()
    llm = create_language_model()
   
    # Create SQLDatabaseToolkit
    toolkit = SQLDatabaseToolkit(db=db, llm=llm)

    # Create SQL Agent Executor
    agent_executor = create_agent_executor(llm=llm, toolkit=toolkit, verbose=True, top_k=config["top_k"])

    # Execute query
    result, output = execute_and_capture_output(agent_executor.run, query)
   
    queryResult = myutils.get_query(output).replace('"', '')
    #output = myutils.remove_colors(output)

    return jsonify({"print": output, "output": result, "query": queryResult })

def create_sql_database():
    sericeFile = config["service_account_file"]
    encoded_string = myutils.save_file(sericeFile)

    sqlalchemy_url = f'bigquery://{config["project"]}/{config["dataset"]}?credentials_path={encoded_string}'
    return SQLDatabase.from_uri(sqlalchemy_url)

def create_language_model():
    temperature = 0
    model = config["model"]
    if model.startswith("gpt"):
        return ChatOpenAI(temperature=temperature, model=model)
    else:
        return OpenAI(temperature=temperature, model=model)

def create_agent_executor(llm, toolkit, verbose, top_k):
    return create_sql_agent(llm=llm, toolkit=toolkit, verbose=True, top_k=top_k)


@flask.errorhandler(Exception)
def handle_exception(error):
    logging.error('Exception occurred: %s', error)
    return "An error occurred: {}".format(error), 500

db = create_sql_database()
llm = create_language_model()

if __name__ == "__main__":
    threading.Thread(target=startapp).start()
    SocketModeHandler(app, config["slack_bot_app_token"]).start()