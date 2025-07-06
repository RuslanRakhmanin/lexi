import markdown
import re

def render_markdown_to_html(markdown_text, css_content=""):
    """
    Converts Markdown text to HTML and includes custom CSS.

    Args:
        markdown_text: The input text in Markdown format.
        css_content: A string containing custom CSS rules.

    Returns:
        A string containing the full HTML document with rendered Markdown and embedded CSS.
    """
    # Convert markdown to HTML
    html_body = markdown.markdown(markdown_text, extensions=['tables', 'extra', 'markdown_del_ins'])

    # Create a full HTML document structure
    html_template = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body {{ font-family: sans-serif; margin: 0; padding: 10px; }}
            {css_content}
        </style>
    </head>
    <body>
        {html_body}
    </body>
    </html>
    """
    return html_template


def _markdown_to_plain_text(markdown_text):
    """Converts a basic subset of Markdown to plain text."""
    # This is a simple conversion and might not handle all Markdown complexities.
    # Remove headings (##, ###, etc.)
    plain_text = re.sub(r'^#+\s+', '', markdown_text, flags=re.MULTILINE)
    # Remove bold and italics (*, _)
    plain_text = re.sub(r'[\*_]', '', plain_text)
    # Remove links ([text](url)) - keep only text
    plain_text = re.sub(r'\[(.*?)\]\(.*?\)', r'\1', plain_text)
    # Remove code blocks (```) and inline code (`)
    plain_text = re.sub(r'```.*?```', '', plain_text, flags=re.DOTALL)
    plain_text = re.sub(r'`(.*?)`', r'\1', plain_text)
    # Remove list markers (-, *, +)
    plain_text = re.sub(r'^[\-\*\+]\s+', '', plain_text, flags=re.MULTILINE)
    # Remove horizontal rules (---, ***, etc.)
    plain_text = re.sub(r'^-{3,}$|^\*{3,}$|^_{3,}$', '', plain_text, flags=re.MULTILINE)
    # Basic table handling: replace | with tab or space (simple approach)
    plain_text = re.sub(r'\s*\|\s*', ' | ', plain_text)
    # Remove extra newlines that might result from removal
    plain_text = re.sub(r'\n\s*\n', '\n\n', plain_text).strip()

    return plain_text

if __name__ == '__main__':
    # Example Usage
    example_markdown = """
# Heading 1
## Heading 2

This is **bold** text and this is *italic* text.
This is ~~strikethrough~~ text and this is ==highlighted== text.

- List item 1
- List item 2

Here is a table:

| Header 1 | Header 2 |
|----------|----------|
| Data 1   | Data 2   |
| Data 3   | Data 4   |

And some code:

"""

    example_css = """
body {
    background-color: #f0f0f0;
    color: #333;
}
h1 {
    color: navy;
}
table {
    border-collapse: collapse;
    width: 100%;
}
th, td {
    border: 1px solid #ddd;
    padding: 8px;
    text-align: left;
}
th {
    background-color: #4CAF50;
    color: white;
}
tr:nth-child(even) {
    background-color: #f2f2f2;
}
"""

    rendered_html = render_markdown_to_html(example_markdown, example_css)
    print(rendered_html)
    
