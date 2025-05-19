from docx2markdown_custom import docx_to_markdown_custom

if __name__ == "__main__":
    import os
    # Adjust path if running from project root
    docx_path = os.path.join(os.path.dirname(__file__), "..", "Test_Spec.docx")
    with open(docx_path, "rb") as f:
        docx_bytes = f.read()
    md = docx_to_markdown_custom(docx_bytes)
    print(md) 