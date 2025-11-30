import webbrowser
import os
from llm_config.llm_config import RETRY_COUNT
from loguru import logger


def visualize_graph_html(app):
    mermaid_code = app.get_graph().draw_mermaid()
    
    html_content = f"""<!DOCTYPE html>
    <html>
    <head>
        <title>Workflow Graph</title>
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 50px auto;
                padding: 20px;
                background: #f5f5f5;
            }}
            .container {{
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                border-bottom: 3px solid #4CAF50;
                padding-bottom: 10px;
            }}
            .mermaid {{
                text-align: center;
                margin: 30px 0;
            }}
            .info {{
                background: #e3f2fd;
                padding: 15px;
                border-radius: 4px;
                margin-top: 20px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>SEO Content Generation Workflow</h1>
            
            <div class="mermaid">
    {mermaid_code}
            </div>
            
            <div class="info">
                <h3>📊 Workflow Description</h3>
                <ul>
                    <li><strong>output_processing:</strong> Generates SEO content using LLM</li>
                    <li><strong>validate:</strong> Validates content quality and constraints</li>
                    <li><strong>retry:</strong> Prepares feedback for regeneration if needed</li>
                </ul>
                <p><strong>Retry Logic:</strong> Up to {RETRY_COUNT} attempts if validation score < 0.7 or critical issues exist</p>
            </div>
        </div>
        
        <script>
            mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        </script>
    </body>
    </html>"""
    
    html_file = "workflow_graph.html"
    with open(html_file, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"\n✅ Interactive graph saved to {html_file}")
    print(f"📌 Open {html_file} in your browser to view the graph\n")

    webbrowser.open('file://' + os.path.abspath(html_file))


def log_validation_report(result):
    validation = result["validation"]

    lines = []
    lines.append("=" * 50)
    lines.append("VALIDATION REPORT")
    lines.append("=" * 50)

    lines.append(f"Passed: {validation.get('passed')}")
    lines.append(f"Overall Score: {validation.get('score', 0):.2f}")

    lines.append("\nCategory Scores:")
    for category, score in validation.get('category_scores', {}).items():
        lines.append(f"  {category}: {score:.2f}")

    if validation.get('issues'):
        lines.append(f"\n❌ Critical Issues ({len(validation['issues'])}):")
        lines += [f"  - {i}" for i in validation['issues']]

    if validation.get('warnings'):
        lines.append(f"\n⚠️  Warnings ({len(validation['warnings'])}):")
        lines += [f"  - {w}" for w in validation['warnings']]

    lines.append(f"\nRetries used: {result['retry_count']}/{RETRY_COUNT}")
    lines.append("=" * 50)

    block = "\n".join(lines)
    logger.opt(raw=True).info(block + "\n")
