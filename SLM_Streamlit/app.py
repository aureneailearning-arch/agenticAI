import json
import os
from typing import Any, Iterator
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import streamlit as st


MODELS = {
    "Qwen 2.5 3B Instruct": "qwen2.5:3b",
    "Phi 3.5 Mini Instruct (3.8B)": "phi3.5:3.8b",
}
DEFAULT_SYSTEM_PROMPT = (
    "You are a helpful, accurate assistant. If you are unsure, say so instead "
    "of inventing details."
)


class OllamaError(RuntimeError):
    """An Ollama API request failed or returned an invalid response."""


def _api_url(host: str, path: str) -> str:
    return f"{host.rstrip('/')}{path}"


def _read_json(response: Any) -> dict[str, Any]:
    try:
        data = json.loads(response.read().decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise OllamaError("Ollama returned an invalid JSON response.") from exc
    if not isinstance(data, dict):
        raise OllamaError("Ollama returned an unexpected response.")
    if data.get("error"):
        raise OllamaError(str(data["error"]))
    return data


def _request_json(
    host: str, path: str, payload: dict[str, Any] | None = None
) -> dict[str, Any]:
    body = None if payload is None else json.dumps(payload).encode("utf-8")
    request = Request(
        _api_url(host, path),
        data=body,
        headers={"Content-Type": "application/json"} if body else {},
        method="GET" if body is None else "POST",
    )
    try:
        with urlopen(request, timeout=30) as response:
            return _read_json(response)
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise OllamaError(f"Ollama returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise OllamaError(
            f"Could not connect to Ollama at {host}. Start Ollama and try again "
            f"({exc.reason})."
        ) from exc
    except TimeoutError as exc:
        raise OllamaError("The request to Ollama timed out.") from exc


def _stream_json(
    host: str, path: str, payload: dict[str, Any], timeout: int = 600
) -> Iterator[dict[str, Any]]:
    request = Request(
        _api_url(host, path),
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            for line in response:
                if not line.strip():
                    continue
                try:
                    data = json.loads(line.decode("utf-8"))
                except (UnicodeDecodeError, json.JSONDecodeError) as exc:
                    raise OllamaError(
                        "Ollama returned an invalid streamed response."
                    ) from exc
                if not isinstance(data, dict):
                    raise OllamaError("Ollama returned an unexpected response.")
                if data.get("error"):
                    raise OllamaError(str(data["error"]))
                yield data
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise OllamaError(f"Ollama returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise OllamaError(
            f"Could not connect to Ollama at {host}. Start Ollama and try again "
            f"({exc.reason})."
        ) from exc
    except TimeoutError as exc:
        raise OllamaError("The request to Ollama timed out.") from exc


def _installed_models(host: str) -> set[str]:
    data = _request_json(host, "/api/tags")
    models = data.get("models", [])
    if not isinstance(models, list):
        raise OllamaError("Ollama returned an invalid model list.")
    return {
        name
        for model in models
        if isinstance(model, dict)
        for name in (model.get("name"), model.get("model"))
        if isinstance(name, str)
    }


st.set_page_config(page_title="Local SLM Chat", page_icon="💬", layout="centered")
st.title("Local SLM Chat")
st.caption("Chat privately with a local Qwen 2.5 or Phi 3.5 model using Ollama.")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.header("Settings")
    host = os.environ.get("OLLAMA_HOST", "http://localhost:11434").strip()
    selected_label = st.selectbox("Model", list(MODELS))
    model_name = MODELS[selected_label]
    system_prompt = st.text_area("System prompt", value=DEFAULT_SYSTEM_PROMPT)
    temperature = st.slider(
        "Temperature", min_value=0.0, max_value=2.0, value=0.2, step=0.1
    )
    context_length = st.select_slider(
        "Context window (tokens)",
        options=[2048, 4096, 8192, 16384, 32768, 65536, 131072],
        value=4096,
        format_func=lambda tokens: f"{tokens // 1024}K",
        help=(
            "Sets the requested Ollama context window, up to 128K. Larger contexts "
            "use substantially more memory; usable length depends on the model and hardware."
        ),
    )
    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

try:
    installed_models = _installed_models(host)
    connection_error = None
except OllamaError as exc:
    installed_models = set()
    connection_error = exc

if connection_error is None and model_name in installed_models:
    st.sidebar.success("Ollama is connected; selected model is installed.")
elif connection_error is None:
    st.sidebar.warning("Selected model is not installed.")

download_label = (
    "Update selected model"
    if connection_error is None and model_name in installed_models
    else "Download selected model"
)
if st.sidebar.button(download_label, use_container_width=True):
    progress = st.sidebar.empty()
    try:
        for update in _stream_json(
            host, "/api/pull", {"name": model_name, "stream": True}, timeout=3600
        ):
            status = update.get("status", "Downloading")
            completed = update.get("completed")
            total = update.get("total")
            if isinstance(completed, int) and isinstance(total, int) and total > 0:
                percent = min(completed / total, 1.0)
                progress.progress(percent, text=f"{status}: {percent:.0%}")
            else:
                progress.info(str(status))
        st.sidebar.success("Model is ready.")
        st.rerun()
    except OllamaError as exc:
        st.sidebar.error(str(exc))

if connection_error is not None:
    st.error(str(connection_error))
    st.info(
        "Start Ollama, then click **Download selected model** in Settings. "
        "Installation instructions: https://ollama.com/download"
    )
    st.stop()

if model_name not in installed_models:
    st.info(
        f"Download **{model_name}** from the Settings panel to start chatting. "
        "The first download may take a few minutes."
    )
    st.stop()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Send a message")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    request_messages = [
        {"role": "system", "content": system_prompt},
        *st.session_state.messages,
    ]
    with st.chat_message("assistant"):
        response_area = st.empty()
        response_text = ""
        try:
            for update in _stream_json(
                host,
                "/api/chat",
                {
                    "model": model_name,
                    "messages": request_messages,
                    "stream": True,
                    "options": {
                        "temperature": temperature,
                        "num_ctx": context_length,
                    },
                },
            ):
                chunk = update.get("message", {}).get("content", "")
                if isinstance(chunk, str):
                    response_text += chunk
                    response_area.markdown(response_text + "▌")
            response_area.markdown(response_text)
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
        except OllamaError as exc:
            st.error(str(exc))
