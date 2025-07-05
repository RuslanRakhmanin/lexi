import markdown

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
    html_body = markdown.markdown(markdown_text, extensions=['tables'])

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

if __name__ == '__main__':
    # Example Usage
    example_markdown = """
# Heading 1
## Heading 2

This is **bold** text and this is *italic* text.

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
    