# Function Call

Tool Agent also supports function call integration with LLMs like Google's Gemini.

## Creating an API

To create an API, import the `tool_api` function from `coala.remote_api` and pass in the path to a CWL file and the name of the tool:

```python
from coala.remote_api import tool_api

api = tool_api(cwl_file='tests/dockstore-tool-md5sum.cwl', tool_name='md5sum')
api.serve()
```

The `api.serve()` method will start a RESTful API as a service, allowing you to run the tool remotely from the cloud or locally.

## Creating a Tool Agent

To create a tool agent, import the `tool_agent` function from `coala.agent` and pass in the API instance:

```python
from coala.agent import tool_agent

ta = tool_agent(api)
md5 = ta.create_tool()
md5(input_file="tests/dockstore-tool-md5sum.cwl")
```

Function `md5` is created automatically based on the `api`.

## Function Call with Gemini

To integrate the tool agent with Gemini, import the `GenerativeModel` class from `google.generativeai` and create a new instance:

```python
import google.generativeai as genai

genai.configure(api_key="******")
model = genai.GenerativeModel(model_name='gemini-1.5-flash', tools=[md5])

chat = model.start_chat(enable_automatic_function_calling=True)
response = chat.send_message("what is md5 of tests/dockstore-tool-md5sum.cwl?")
response.text
```

Output:

```
'The md5sum of tests/dockstore-tool-md5sum.cwl is ad59d9e9ed6344f5c20ee7e0143c6c12. \n'
```

