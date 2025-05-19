import azure.functions as func
import logging
import json
import requests
import os

WRITER_URL = os.environ.get("WRITER_URL", "http://localhost:7071/api/SpecWriter")
REVIEWER_URL = os.environ.get("REVIEWER_URL", "http://localhost:7071/api/SpecReviewer")
GATHERER_URL = os.environ.get("GATHERER_URL", "http://localhost:7071/api/SpecInformationGatherer")
UPDATER_URL = os.environ.get("UPDATER_URL", "http://localhost:7071/api/SpecUpdater")


def main(req: func.HttpRequest) -> func.HttpResponse:
    try:
        req_body = req.get_json()
        artifact = req_body.get("artifact")
        text = req_body.get("text")
        review_history = []

        if not artifact and not text:
            return func.HttpResponse("No artifact or text provided.", status_code=400)

        # Combine artifact and text if both are provided, or use whichever is present
        input_text = artifact if artifact else text

        # Generate initial spec from input text
        writer_res = requests.post(WRITER_URL, json={"input": input_text})
        if writer_res.status_code != 200:
            return func.HttpResponse(f"Writer error: {writer_res.text}", status_code=500)
        spec = writer_res.text.strip()

        # Review/update loop
        for round_num in range(1, 3):
            review_res = requests.post(REVIEWER_URL, json={"spec": spec})
            if review_res.status_code != 200:
                return func.HttpResponse(f"Reviewer error: {review_res.text}", status_code=500)
            feedback = review_res.json().get("reviewer_feedback", [])
            review_history.append({"round": round_num, "feedback": feedback})

            if not feedback:
                break

            gather_res = requests.post(GATHERER_URL, json={"spec": spec, "feedback": feedback})
            if gather_res.status_code != 200:
                return func.HttpResponse(f"Gatherer error: {gather_res.text}", status_code=500)
            try:
                gather_data = gather_res.json()
            except json.JSONDecodeError:
                return func.HttpResponse(f"Error decoding gatherer response: {gather_res.text}", status_code=500)

            questions = gather_data.get("questions", [])
            updates = gather_data.get("updates", spec)

            answers = []
            if questions:
                # For API, just return the questions to the user for now
                return func.HttpResponse(json.dumps({
                    "status": "incomplete",
                    "message": "Missing info, please answer the following questions and resubmit.",
                    "questions": questions,
                    "spec": spec,
                    "review_history": review_history
                }), status_code=200, mimetype="application/json")

            # Call updater
            update_res = requests.post(UPDATER_URL, json={"spec": spec, "answers": answers, "updates": updates})
            if update_res.status_code != 200:
                return func.HttpResponse(f"Updater error: {update_res.text}", status_code=500)
            spec = update_res.text.strip()

        return func.HttpResponse(json.dumps({
            "status": "complete",
            "final_spec": spec,
            "review_history": review_history
        }), status_code=200, mimetype="application/json")

    except Exception as e:
        logging.exception("Error in SpecOrchestrator")
        return func.HttpResponse(f"Internal server error: {str(e)}", status_code=500) 