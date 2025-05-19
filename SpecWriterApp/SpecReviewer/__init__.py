import logging
import os
import openai
import base64
import azure.functions as func
from io import BytesIO

openai.api_type = "azure"
openai.api_base = "https://agentworkflows.openai.azure.com/"
openai.api_version = "2023-12-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")



def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        # Read the system prompt file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "reviewer_prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
            SYSTEM_PROMPT = f.read()

        req_body = req.get_json()
        user_input = req_body.get("spec")  

        if not user_input:
            return func.HttpResponse("No input provided", status_code=400)

        print(f"User input: {user_input}")
        client = openai.AzureOpenAI(
            api_key=openai.api_key,
            api_version=openai.api_version,
            azure_endpoint=openai.api_base
        )

        response = client.chat.completions.create(
            model="gpt-35-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.4,
            max_tokens=2000
        )

        content = response.choices[0].message.content if response.choices else "{}"
        print(f"ReviewerContent: {content}")
        return func.HttpResponse(content, status_code=200, mimetype="application/json")

    except Exception as e:
        logging.exception("Error in SpecReviewer")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)
