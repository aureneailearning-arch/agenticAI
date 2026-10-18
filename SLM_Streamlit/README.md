# Local SLM Chat

A Streamlit chat interface for running Qwen 2.5 3B Instruct or Phi 3.5 Mini
Instruct (3.8B) locally with Ollama. Prompts and replies go to the configured
Ollama server; this app does not call a hosted inference API.

## Requirements

- Python 3.10 or newer
- [Ollama](https://ollama.com/download), installed and running
- Enough RAM/VRAM for the selected model and its context length

## Run

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run app.py
```

Open the local URL printed by Streamlit. In the Settings panel, choose Qwen or
Phi, edit the system prompt, and adjust temperature and context window. Use
**Download selected model** the first time you choose a model; Ollama keeps the
downloaded weights for later runs. The model tags are `qwen2.5:3b` and
`phi3.5:3.8b`.

To connect to Ollama at a non-default address, set `OLLAMA_HOST` before
starting Streamlit.

## Context window

The Settings panel offers context windows from 2K up to 128K tokens, and sends
the selected value to Ollama as `num_ctx`. Larger windows can use substantially
more memory, and the usable maximum depends on the selected model and available
hardware. Increase it only when needed.
