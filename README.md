Feeling lucky, punk? Let's dance.

 -- mistral-nemo:12b

# Overview

Playable proof-of-concept for an LLM playing a game against you,
and making colorful comments about its attempts at conquest.

_There are many like it, but this one is mine._

Inspired by https://every.to/p/diplomacy.

The game is based on `Bombardment`, where you are on a 5x5 grid and
you and your opponent picked 4 positions known to you but hidden to
each other. You both lob missiles at each other blindly until one
player gets lucky enough to hit all four.

As a proof-of-concept, some of the input validation and output messages
are unpolished, and it also reveals the LLMs positions to you so you can
experiment with the LLM's reactions to winning or losing. 

# Install Requirements

Requirements:
* Python, e.g. Python 3.12
* Ollama

1. [Install Ollama](https://ollama.com/download) using their guide
2. Download the default model use by the game: `ollama pull llama3-groq-tool-use:8b`
3. Create python virtual environment - `virtualenv venv && source venv/bin/activate && pip install -r requirements.txt` 

# Run

```shell
python play_ollama.py
```

Or

```shell
python play_original.py
```

# Model Support

Supports any Ollama model that can reliably produce structured
output (json) when requested to do so, and does not intermingle
`thinking` output.

Does not require tool support.

# Cheating

The models sometimes appeared to intentionally obscure their
platoons. Even though the prompt specifies an array of four
integers, the models would sometimes provide four strings of
integers (which are not equal in Python), or even withhold
their choices altogether by providing obfuscated values
such as `platoons: ["secret_platoon_1", ..]`.

# Final Thoughts

_You got me this time, but I'll be back! Game's not over yet!_

 -- llama3-groq-tool-use:8b
 
Are you not entertained?
