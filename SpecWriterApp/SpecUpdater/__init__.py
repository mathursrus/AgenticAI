import logging
import os
import json
import openai
import re
import azure.functions as func

openai.api_type = "azure"
openai.api_base = "https://agentworkflows.openai.azure.com/"
openai.api_version = "2023-12-01-preview"
openai.api_key = os.getenv("AZURE_OPENAI_KEY")

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        body = req.get_json()
        spec = body.get("spec")
        answers = body.get("answers")
        updates = body.get("updates")

        if not spec:
            return func.HttpResponse("Missing 'spec' in request body.", status_code=400)

        client = openai.AzureOpenAI(
            api_key=openai.api_key,
            api_version=openai.api_version,
            azure_endpoint=openai.api_base
        )            
       
        current_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_path = os.path.join(current_dir, "updater_prompt.txt")
        with open(prompt_path, "r", encoding="utf-8") as f:
          SYSTEM_PROMPT = f.read()
        # Call Azure OpenAI
        response = client.chat.completions.create(
            model="gpt-35-turbo",  # use your deployment name
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Spec:\n{spec}\n\nUser Answers:\n{json.dumps(answers, indent=2)}\n\nUpdates:\n{json.dumps(updates, indent=2)}"}
            ],
            temperature=0.3,
            max_tokens=3000
        )

        raw_content = response.choices[0].message.content if response.choices else "{}"
        logging.info("Raw model output: %s", raw_content)

        return func.HttpResponse(raw_content, status_code=200, mimetype="text/plain")
    
    except Exception as e:
        logging.exception("Error in SpecUpdater")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500)

