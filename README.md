# AgenticAI - Custom Function Endpoints with GPT Integration

This repository contains a framework for creating custom Azure Functions endpoints and integrating them with GPT models. It includes a complete example implementation for a specification writing system, which can be used as a template for creating your own custom endpoints.

## Project Structure

```
.
├── SpecWriterApp/              # Example implementation of a spec writing system
│   ├── SpecOrchestrator/      # Main orchestrator function
│   ├── SpecWriter/           # Initial spec generation
│   ├── SpecReviewer/         # Spec review and feedback
│   ├── SpecInformationGatherer/ # Information gathering
│   ├── SpecUpdater/          # Spec updates
│   ├── SpecConverter/        # Format conversion
│   └── openapi.json          # OpenAPI specification
└── SpecCopilotAgent/         # GPT integration files
    └── appPackage/           # GPT configuration files
```

## Getting Started

### Prerequisites

1. Python 3.8 or higher
2. Azure Functions Core Tools
3. Azure CLI (if deploying to Azure)
4. OpenAI API access
5. ngrok (for local development)

### Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd AgenticAI
```

2. Install Azure Functions Core Tools:
```bash
npm install -g azure-functions-core-tools@4 --unsafe-perm true
```

3. Create a Python virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

4. Install dependencies:
```bash
pip install -r SpecWriterApp/requirements.txt
```

5. Configure Azure OpenAI API:
   - Create a `local.settings.json` file in the SpecWriterApp directory if it doesn't exist
   - Add your Azure OpenAI API key and endpoint:
```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "AZURE_OPENAI_API_KEY": "your-api-key-here",
    "AZURE_OPENAI_ENDPOINT": "your-endpoint-here"
  }
}
```

Note: Never commit `local.settings.json` to version control. It's already included in `.gitignore`.

## Running the Functions

You have two options to run the functions:

### Option 1: Local Development with ngrok

1. Start the function app locally:
```bash
cd SpecWriterApp
func start
```

2. In a new terminal, start ngrok to expose your local server:
```bash
ngrok http 7071
```

3. Copy the ngrok URL (e.g., `https://xxxx-xx-xx-xxx-xx.ngrok.io`) and update the `servers` section in `openapi.json`:
```json
{
  "servers": [
    {
      "url": "https://xxxx-xx-xx-xxx-xx.ngrok.io/api",
      "description": "Local development server via ngrok"
    }
  ]
}
```

### Option 2: Deploy to Azure

1. Login to Azure:
```bash
az login
```

2. Create a new Function App in Azure:
```bash
az functionapp create --name your-function-app-name --storage-account your-storage-account --consumption-plan-location eastus --runtime python --runtime-version 3.8 --functions-version 4
```

3. Deploy the functions:
```bash
cd SpecWriterApp
func azure functionapp publish your-function-app-name
```

4. Update the `servers` section in `openapi.json` with your Azure Function App URL:
```json
{
  "servers": [
    {
      "url": "https://your-function-app-name.azurewebsites.net/api",
      "description": "Azure Function App"
    }
  ]
}
```

## Creating a GPT Integration

1. Create a new GPT in the OpenAI platform
2. Give your GPT a name, description. Copy instructions from the SpecGPT/instructions.txt file
3. In the actions dialog, copy/paste the openapi.json file (with the server updated to your end point)

## Testing Your Setup

1. Test the endpoints using the provided curl commands or Postman
2. Verify the GPT integration by making requests through the GPT interface

## Best Practices

1. **Security**: 
   - Use environment variables for sensitive information
   - Implement proper authentication for production deployments
   - Keep your ngrok URL private when using it for development

2. **Monitoring**:
   - Monitor your function app's performance in Azure Portal
   - Check ngrok's web interface for request logs during local development

3. **Error Handling**:
   - Check the function logs for any errors
   - Monitor the GPT's responses for unexpected behavior

## Example Usage

The `SpecWriterApp` implementation provides a complete example of:
- Function endpoint implementation
- OpenAPI specification
- GPT integration
- Error handling
- Input validation

## Contributing

Feel free to submit issues and enhancement requests!
