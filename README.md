# Wiki Server

A lightweight local web server that serves `.txt` files with markdown-like
formatting, automatically rendered into styled HTML.

## Features

- Header support (`#`, `##`, `###`)
- Ordered and unordered lists
- Inline and standalone links `[text](url)`
- Code blocks using triple backticks (```...```)
- Basic error handling (404 page)
- Graceful shutdown with `/quit` endpoint

## Getting Started

### Requirements

- Python 3.x

### Run the Server

```bash
python wiki-server.py

