
# Alias for `just -l`
default:
    @just -l

# Play against a single Ollama LLM
play-ai:
    #!/bin/bash

    set e-u

    source venv/bin/activate
    python play_ollama.py

# Play the original game, against its simplistic computer opponent
play-original:
    #!/bin/bash

    set e-u

    source venv/bin/activate
    python play_original.py

# Create a typical Python virtual environment
venv:
    #!/bin/bash

    set e-u

    virtualenv venv
    source venv/bin/activate
    pip install -r requirements.txt
