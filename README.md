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
