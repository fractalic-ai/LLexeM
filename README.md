# fractalic updating in progress
Hello, repo updating is in progress. Please wait for a while.

# Requirments
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