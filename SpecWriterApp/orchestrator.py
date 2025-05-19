import requests
import json
import base64
import logging
from docx2markdown_custom import docx_to_markdown_custom
# Agent endpoints
WRITER_URL = "http://localhost:7071/api/SpecWriter"
REVIEWER_URL = "http://localhost:7071/api/SpecReviewer"
GATHERER_URL = "http://localhost:7071/api/SpecInformationGatherer"
UPDATER_URL = "http://localhost:7071/api/SpecUpdater"

# Input artifact
artifact = """
Our meeting notes say we plan to build a new AI chat search that integrates with Outlook and Teams. 
The goal is to help users quickly find relevant information in long message threads, especially when conversations span multiple days or participants.
"""

# Step 1: Call SpecWriter
#print("\n🔧 Generating initial spec from artifact...")
#writer_res = requests.post(WRITER_URL, json={"input": artifact})
#spec = writer_res.text.strip()
#print("\n📝 Initial Spec:\n" + spec)

DOCX_PATH = "../Test_Spec.docx"

# Step 1: Read and encode the DOCX file as base64
with open(DOCX_PATH, "rb") as f:
    docx_bytes = f.read()
    spec = base64.b64encode(docx_bytes).decode("utf-8")
    try:
        decoded_bytes = base64.b64decode(spec)
        spec = docx_to_markdown_custom(decoded_bytes)
    except Exception as decode_err:
        logging.exception("Failed to decode base64 .docx file")

# Run up to 5 review–update passes
for round_num in range(1, 6):
    print(f"\n🌀 Iteration {round_num}: Reviewing spec...")

    # Step 2: Call Reviewer
    review_res = requests.post(REVIEWER_URL, json={"spec": spec})
    feedback = review_res.json().get("reviewer_feedback", [])

    if not feedback:
        print("\n✅ No more feedback — spec is finalized.")
        break

    print(f"\n🧠 Reviewer Feedback ({len(feedback)} items):")
    for f in feedback:
        print(f" - [{f['section']}] {f['suggestion']}")

    # Step 3: Call Information Gatherer
    gather_res = requests.post(GATHERER_URL, json={"spec": spec, "feedback": feedback})
    try:
        gather_data = gather_res.json()
    except json.JSONDecodeError:
        print("\n🚨 Error decoding Updater Phase 1 response. Raw content was:\n")
        print(gather_res.text)
        raise

    questions = gather_data.get("questions", [])
    updates = gather_data.get("updates", spec)
    
    # Step 4: Ask user for missing inputs
    answers = []
    if questions:
        print("\n❓ Missing info — please answer the following:")
        for q in questions:
            ans = input(f" → {q['question']}\nYour answer: ")
            # If user says Ignore, skip this question without adding it to the answers
            if ans.lower() == "ignore":
                continue
            answers.append({"section": q["section"], "answer": ans})

    # Step 5: Call Updater
    if len(answers) > 0 or len(updates) > 0:
        print("🧩 Applying updates...")
        update_res = requests.post(UPDATER_URL, json={"spec": spec, "answers": answers, "updates": updates})
        spec = update_res.text.strip()
        print("\n📝 Spec After Updater:")
        print(spec)    
    else:
        print("🚫 No updates needed — spec is finalized.")
        break

# Final spec
print("\n✅✅ Final Spec After Review Loop:")
print(spec)
