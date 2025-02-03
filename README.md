# Fractalic

Program AI in plain language (any language). That's it.

## Vision 🚀

Modern AI workflows shouldn’t be harder than they already are. We have powerful LLMs, yet we still end up wrestling with Python scripts and tangled spaghetti-like node-based editors. **Fractalic** aims to fix this by letting you build AI systems as naturally as writing a simple doc.

## What is Fractalic? ✨

Fractalic combines Markdown and YAML to create agentic AI systems using straightforward, human-readable documents. It lets you grow context step by step, control AI knowledge precisely, and orchestrate complex workflows through simple document structure and syntax.

## Key Features

🧬 **Structured Knowledge & Precision** - Use Markdown heading blocks to form a semantic tree. Reference specific nodes or branches with a simple, path-like syntax.

🧠 **Dynamic Knowledge context** - Each operation can modify specific nodes and branches, allowing your system to evolve dynamically.
    
🤖 **Agentic ready** - The module system (`@run`) isolates execution contexts. It passes parameters and returns results as semantic blocks, enabling both specialized agents and reusable workflows with clear inputs and outputs.

🪄 **Runtime Instruction Generation** Generate instructions dynamically during execution, or delegate this task to the LLM. This enables conditional workflows and supports autonomous agent behavior.
    
🤝 **Multi-Model Collaboration** - You can explicitly specify LLM provider, model, and parameters (e.g., temperature) for each call.
    
🖥️ **Shell Integration** - Execute CLI tools and scripts (Python, curl, Docker, Git, etc.) and automatically update the knowledge context with the results.
    
📝 **Transparent Versioning** - Automatically track every context change and decision using Git-native version control. 
    
📒 **User Interface** - A notebook-like UI provides straightforward parameter selection and operation management.

# Quick intro 0
![alt text](<docs/images/slide_01.png>)

# Quick intro 1
![alt text](<docs/images/slide_02.png>)

# Quick intro 2
![alt text](<docs/images/slide_03.png>)

# Quick intro 3
![alt text](<docs/images/fractalic-demo-0001.png>)


# fractalic updating in progress
Hello, repo updating is in progress. Please wait for a while.

# Requirements
Important: please ensure you have Git installed on your system.
Git dependecy would be removed in future releases. Sessions would be stored on .zip or .tar.gz files.

# Installation (Docker)
As for now, the best way to use Fraxtalic is to install both interpreter with backend server and UI frontend and run it as odcker container, if you dont need docker - please skip that step.

```bash
git clone https://github.com/fractalic-ai/fractalic.git && \
git clone https://github.com/fractalic-ai/fractalic-ui.git  && \
cd fractalic && \
cp -a docker/. .. && \
cd .. && \
docker build -t fractalic-app . && \
docker run -d \
  -p 8000:8000 \
  -p 3000:3000 \
  --name fractalic-app \
  fractalic-app
```
Now UI should be avaliable on http://localhost:3000
Please be aware to connect local folder with .md files to persist changes
Same action is required for settings toml


# Installation (Local)

1. Backend installation
```bash
git clone https://github.com/fractalic-ai/fractalic.git && \
cd fractalic && \
python3 -m venv venv && \
source venv/bin/activate && \
pip install -r requirements.txt 
```
2. Run backend
```bash
./run_server.sh
```

3. Frontend installation
```bash
git clone https://github.com/fractalic-ai/fractalic-ui.git  && \
cd fractalic-ui && \
npm install 
```

4. Run frontend
```bash
npm run dev
```



# Running fractalic backend server
Required for UI to work. Please run the following command in the terminal.
```bash
./run_server.sh
```

# Settings
First time you run the UI, settings.toml would be created required for parser (at least while working from UI, if you are using it headless from CLI - you can use script CLI params). You should select default provider and enter env keys for external providers (repicate, tavily and etc).