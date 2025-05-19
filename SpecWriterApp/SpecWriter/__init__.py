import logging
import os
import openai
import azure.functions as func

openai.api_type = "azure"
openai.api_base = "https://agentworkflows.openai.azure.com/"
openai.api_version = "2023-12-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Read the prompt file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "writer_prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            SYSTEM_PROMPT = f.read()


        req_body = req.get_json()
        logging.info(f"Received input: {req_body}")
        user_input = req_body.get("input")

        if not user_input:
            return func.HttpResponse("No input provided", status_code=400)

        client = openai.AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_KEY"),
            api_version="2023-12-01-preview",
            azure_endpoint="https://agentworkflows.openai.azure.com/"
        )

        response = client.chat.completions.create(
            model="gpt-35-turbo",  # ← your deployment name
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.4,
            max_tokens=2000
        )

        logging.info(f"OpenAI raw response: {response}")

        content = response.choices[0].message.content if response.choices else "OpenAI returned no choices"
        return func.HttpResponse(content, status_code=200)

    except Exception as e:
        logging.exception("Error occurred during function execution")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)
