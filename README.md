# LLexeM updating in progress
Hello, repo updating is in progress. Please wait for a while.

# Installation
```bash
git clone https://github.com/fractalic-ai/llexem.git
cd llexem
python3 -m venv venv
pip install -r requirements.txt
```

# Running llexem backend server
Required for UI to work. Please run the following command in the terminal.
```bash
./run_server.sh
```

# Settings
First time you run the UI, settings.toml would be created required for parser (at least while working from UI, if you are using it headless from CLI - you can use script CLI params). You should select default provider and enter env keys for external providers (repicate, tavily and etc).