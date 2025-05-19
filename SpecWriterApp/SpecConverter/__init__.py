import azure.functions as func
import logging
import base64
import json
import io
from werkzeug.formparser import parse_form_data
from werkzeug.wrappers import Request
from docx2markdown_custom import docx_to_markdown_custom

def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        content_type = req.headers.get("Content-Type", "")
        markdown = None

        if content_type.startswith("multipart/form-data"):
            environ = {
                "wsgi.input": io.BytesIO(req.get_body()),
                "CONTENT_LENGTH": str(len(req.get_body())),
                "CONTENT_TYPE": content_type,
                "REQUEST_METHOD": "POST"
            }
            request = Request(environ)
            stream, form, files = parse_form_data(request.environ)
            file_storage = files.get("file")
            if not file_storage:
                return func.HttpResponse("Missing 'file' part in upload.", status_code=400)
            file_bytes = file_storage.stream.read()
            markdown = docx_to_markdown_custom(file_bytes)
        else:
            req_body = req.get_json()
            base64_file = req_body.get("base64_file")
            if not base64_file:
                return func.HttpResponse("No file provided.", status_code=400)
            try:
                file_bytes = base64.b64decode(base64_file)
                markdown = docx_to_markdown_custom(file_bytes)
            except Exception as decode_err:
                logging.exception("Failed to decode base64 .docx file")
                return func.HttpResponse("Invalid base64 .docx file.", status_code=400)

        return func.HttpResponse(markdown, status_code=200, mimetype="text/markdown")

    except Exception as e:
        logging.exception("Error in SpecConverter")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500) 