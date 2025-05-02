# Importing necessary modules
import http.server
import socketserver
import threading
import os
import re

PORT = 8000  # Port on which the server will run

# Function to parse the text files and convert them into HTML format
def parse_text(text):
    lines = text.splitlines()
    html = []
    in_ol = False
    in_ul = False
    in_code = False
    code_block = []

    for line in lines:
        line = line.rstrip()

        # Code block (```...```)
        if line.strip() == "```":
            if in_code:
                html.append("<pre><code>" + '\n'.join(code_block) + "</code></pre>")
                code_block = []
                in_code = False
            else:
                in_code = True
            continue

        if in_code:
            code_block.append(line)
            continue

        # Headers
        if line.startswith("### "):
            html.append(f"<h3>{parse_links(line[4:])}</h3>")
        elif line.startswith("## "):
            html.append(f"<h2>{parse_links(line[3:])}</h2>")
        elif line.startswith("# "):
            html.append(f"<h1>{parse_links(line[2:])}</h1>")

        # Horizontal rule
        elif line == "---":
            if in_ol:
                html.append("</ol>")
                in_ol = False
            if in_ul:
                html.append("</ul>")
                in_ul = False
            html.append("<hr>")

        # Ordered list
        elif line[:2].isdigit() and line[2:4] == '. ':
            if not in_ol:
                html.append("<ol>")
                in_ol = True
            html.append(f"<li>{parse_links(line[4:])}</li>")

        # Unordered list
        elif line.startswith("- ") or line.startswith("* "):
            if not in_ul:
                html.append("<ul>")
                in_ul = True
            html.append(f"<li>{parse_links(line[2:])}</li>")

        # Links
        elif line.startswith('[') and ']' in line and '(' in line and ')' in line:
            html.append(parse_links(line))

        # Empty line → <br>
        elif not line.strip():
            if in_ol:
                html.append("</ol>")
                in_ol = False
            if in_ul:
                html.append("</ul>")
                in_ul = False
            # close open <p> if necessary
            if html and html[-1].startswith("<p>") and not html[-1].endswith("</p>"):
                html[-1] += "</p>"
            html.append("<br>")

        # Regular paragraph line (without handling double spaces as line breaks)
        else:
            if in_ol:
                html.append("</ol>")
                in_ol = False
            if in_ul:
                html.append("</ul>")
                in_ul = False

            line = parse_links(line)
            html.append(f"<p>{line}</p>")

    # Close last tags if needed
    if html and html[-1].startswith("<p>") and not html[-1].endswith("</p>"):
        html[-1] += "</p>"
    if in_ol:
        html.append("</ol>")
    if in_ul:
        html.append("</ul>")

    return '\n'.join(html)

# Function to parse links in markdown format
def parse_links(text):
    pattern = r'\[([^\]]+)\]\(([^)]+)\)'
    return re.sub(pattern, r'<a href="\2">\1</a>', text)

class WikiHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        path = self.path.lstrip('/')

        # If the path is '/quit', we stop the server
        if path == "quit":
            self.send_response(200)
            self.end_headers()
            self.wfile.write(b"Server stopped.")
            threading.Thread(target=shutdown_server).start()
            return

        # Default to 'home.txt' if no path is specified
        if not path or path == "home.txt":
            path = 'home.txt'

        file_path = os.path.join(os.getcwd(), path)

        # If the file doesn't exist, return a 404 error
        if not os.path.isfile(file_path):
            self.send_response(404)
            self.send_header("Content-type", "text/html; charset=utf-8")
            self.end_headers()
            html_page = f"""
            <html>
            <head>
                <meta charset="utf-8">
                <style>
                    body {{
                        background: #333;
                        color: #eee;
                        font-family: "Lucida Console", "PT Mono Regular";
                        font-size: 18px;  
                        text-align: center;
                        padding: 2em;
                    }}
                    a {{
                        color: #8cf;
                        display: inline-block;
                        margin-top: 2em;
                        text-decoration: underline;
                    }}
                </style>
            </head>
            <body>
                <h1>404 - File Not Found</h1>
                <p>The file you are looking for doesn't exist.</p>
                <a href="home.txt">Go Home</a>
            </body>
            </html>
            """
            self.wfile.write(html_page.encode("utf-8"))
            return
            
        # Read the file content and parse it
        with open(file_path, encoding='utf-8') as f:
            raw = f.read()

        # Convert the parsed text into HTML
        html = parse_text(raw)
        self.send_response(200)
        self.send_header("Content-type", "text/html; charset=utf-8")
        self.end_headers()
        html_page = f"""
        <html>
        <head>
            <meta charset="utf-8">
            <style>
                body {{
                    max-width: 900px;
                    margin: 0 auto;
                    box-sizing: border-box;
                    background: #333;
                    color: #eee;
                    font-family: "Lucida Console", "PT Mono Regular";
                    font-size: 18px;
                    padding: 2em;
                }}
                a {{
                    color: #8cf;
                }}
                p {{
                    margin: 0;
                    text-indent: 2em;
                }}
                code, pre {{
                    background: #444;
                    color: #eee;
                    padding: 0.5em 1em;
                    border-radius: 5px;
                    display: block;
                    white-space: pre-wrap;
                }}
                .footer {{
                    display: flex;
                    justify-content: space-between;
                    margin-top: 2em;
                }}
            </style>
        </head>
        <body>
        {html}
        <hr>
        <div class="footer">
            <a href="help.txt">Help</a>
            <a href="home.txt">Home</a>
            <a href="/quit">Quit</a>
        </div>
        </body>
        </html>
        """
        self.wfile.write(html_page.encode("utf-8"))
        return

# Function to shut down the server
def shutdown_server():
    os._exit(0)

# Main entry point to start the server
if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), WikiHandler) as httpd:
        print(f"Server started: 127.0.0.1:{PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nServer stopped.")
