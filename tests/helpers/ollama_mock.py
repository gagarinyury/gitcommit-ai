"""Mock Ollama HTTP server for testing."""
from typing import Iterator


def mock_ollama_stream() -> Iterator[bytes]:
    """Generate sample Ollama streaming response."""
    responses = [
        b'{"model":"llama3.2","response":"feat","done":false}\n',
        b'{"model":"llama3.2","response":": add","done":false}\n',
        b'{"model":"llama3.2","response":" ollama","done":false}\n',
        b'{"model":"llama3.2","response":" support","done":false}\n',
        b'{"model":"llama3.2","response":"","done":true}\n',
    ]
    for response in responses:
        yield response


def mock_ollama_error_response() -> bytes:
    """Generate Ollama error response (404 model not found)."""
    return b'{"error":"model not found"}\n'


def mock_ollama_models_list() -> str:
    """Generate sample 'ollama list' output."""
    return """NAME                    ID              SIZE      MODIFIED
llama3.2:latest         a80c4f17acd5    2.0 GB    2 days ago
codellama:latest        8fdf8f752f6e    3.8 GB    1 week ago
mistral:latest          2ae6f6dd7a3d    4.1 GB    3 weeks ago
"""
