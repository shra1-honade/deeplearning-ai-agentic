"""Display helper shared by the labs: renders content in a titled HTML box."""

from IPython.display import HTML, display


def print_html(content: str, title: str = ""):
    html = f"""
    <div style="border:1px solid #ccc; border-radius:6px; padding:10px; margin:6px 0; background:#fafafa; color:#111;">
      <div style="font-weight:bold; margin-bottom:6px;">{title}</div>
      <pre style="white-space:pre-wrap; margin:0;">{content}</pre>
    </div>
    """
    display(HTML(html))
