# LangChain and GPT Powered Chat with BigQuery: Detailed Instructions

This walkthrough provides step-by-step instructions for building a solution that enables chatting with Google's BigQuery service. 

## Before You Begin

Please note that the primary focus of this guide is to assist you in creating a ChatInterface for Google BigQuery. It does not dive deep into the specifics of Google BigQuery and Google Cloud Management itself. Therefore, it is assumed that you have already set up a Google Cloud project and have billing enabled for the project.

It is crucial to ensure that the following Google Cloud Project APIs are active:

- IAM API
- BigQuery API

### Setting Up Authentication

The following steps will guide you through the process of authentication:

1. Begin by creating a service account. This service account should be assigned the following roles in BigQuery:
   - BigQuery User
   - BigQuery Data Viewer
   - BigQuery Job User

2. The final step involves downloading a JSON key related to your service account.


## Environment Variables

The script uses the following environment variables, which need to be set for successful execution:

1. `SERVICE_ACCOUNT_FILE`: The path to your Google Cloud service account key file. This key file provides the necessary credentials for the script to interact with your BigQuery service.

2. `PROJECT`: The ID of your Google Cloud project where your BigQuery service is hosted.

3. `DATASET`: The specific dataset in BigQuery that you want to query.

4. `OPENAI_API_KEY`: Your OpenAI API key, which is necessary for the script to interact with the OpenAI GPT models.

5. `MODEL`: The specific model provided by OpenAI that you want to use.

6. `TOP_K`: A parameter for the language model that specifies the number of results to consider when predicting the next token.

7. `DEBUG`: Specifies whether to run the Flask application in debug mode.

8. `LANGCHAIN_VERBOSE`: This variable sets the verbosity of the LangChain agent executor. If true, the executor will provide more detailed logs of its operations.

9. `REQUEST_TIMEOUT`: The maximum time in seconds that the application will wait for a request to be processed before it times out.

Please ensure to replace the actual values in the environment variables with your own before running the script.



## How to Obtain OpenAI API Key

In order to use OpenAI's models, you will need to obtain an API key. Here's a step-by-step guide on how to get it:

1. **Create an OpenAI Account**: Go to [OpenAI's website](https://www.openai.com/) and create an account if you don't already have one.

2. **Dashboard Access**: Once you've signed up and logged in, navigate to the dashboard. The dashboard is typically accessible from the user menu.

3. **API Key**: In the dashboard, look for an option to generate an API key. If it's your first time, you might need to create a new key.

4. **Generate and Copy**: Follow the instructions to generate a new key. Once the key is generated, be sure to copy it and keep it secure. This key provides the necessary authentication to interact with OpenAI's models.

Please remember, this API key is sensitive information and should be kept secure. Don't expose it in public repositories or share it with unauthorized individuals.


## How to Use the API

To interact with the API, you need to send a POST request to the `/execute` endpoint. The body of the request should be a JSON object with a `query` field. The value of the `query` field should be a natural language query that you want the model to interpret and execute against the BigQuery dataset.

### Example Request:

Here's an example of how to send a request to the API using `curl` in the command line:

```bash
curl -X POST http://localhost:6000/execute -H "Content-Type: application/json" -d '{"query": "Create a query to get the number of users who have deposited money for the last 7 days from MY_BIGQUERY_TABLE_NAME table"}'
````


Or if you're using Python's requests library, it might look like this:
```
import requests

url = "http://localhost:6000/execute"
data = {
    "query": "Create a query to get the number of users who have deposited money for the last 7 days from fact__depositsuccess table"
}
response = requests.post(url, json=data)
print(response.json())
```

## Example Response:

The response from the API will be a JSON object that contains the result of the query. For example:

```"There are 38 users who have deposited money in the last 14 days."```


