# docx2markdown_custom

Convert .docx files to Markdown, preserving headings, paragraphs, and tables.

## Installation

```sh
pip install docx2markdown_custom 
```

## Usage

```python
from docx2markdown_custom import docx_to_markdown_custom

with open('your_file.docx', 'rb') as f:
    docx_bytes = f.read()

markdown = docx_to_markdown_custom(docx_bytes)
print(markdown)
```

## Features
- Converts headings, paragraphs, and tables from .docx to Markdown
- Handles bold and italic text

## License
MIT 