# LLexeM: Design and Execute Cognitive Processes for LLMs and Agentic Systems Using Natural Language and Markdown Syntax

LLexeM is a next-generation framework designed to revolutionize interaction with Large Language Models (LLMs) and agentic systems. This framework facilitates programming of complex, self-replicating systems and dynamic task processes using plain text and natural language.

With LLexeM, managing hierarchical knowledge structures as context for LLMs becomes effortless, enabling the creation of intricate execution flows with ease. The custom Markdown-based syntax streamlines the integration of LLMs into workflows, empowering these models to update and control their own context, knowledge, and execution in real-time.

This results in smarter, self-replicating systems that are easily monitored by humans and continuously adapt and evolve.

# Table of Contents

- [Key Features](#key-features)
- [Installation](#installation)
    - [System Requirements](#system-requirements)
    - [Installation and Quick run](#installation-and-quick-run)
  - [Introduction](#introduction)
    - [Key Concepts](#key-concepts)
  - [Supported Operations](#supported-operations)
    - [General Structure](#general-structure)
    - [Operands](#operands)
    - [@import](#import)
    - [@llm](#llm)
    - [@run](#run)
      - [Parameters Passing](#parameters-passing)
      - [Handling Returned Results](#handling-returned-results)
    - [@shell](#shell)
    - [@return](#return)
    - [@goto](#goto)
  - [Contributing](#contributing)
  - [License](#license)

## Key Features

1. **Intuitive Control**: Manage LLMs using natural language, minimizing the need for advanced programming skills.
2. **Markdown-Based Workflow**: Leverage a custom markdown syntax to define knowledge contexts and execution steps with precision.
3. **Real-Time Context Adaptation**: Dynamically modify and optimize the LLM's accessible context during runtime.
4. **Fine-Grained Knowledge Management**: Exercise precise control over the LLM's visible context, allowing for targeted information access.
5. **Hierarchical Process Architecture**: Construct complex, multi-tiered processes with unlimited nesting capabilities.
6. **Distributed Task Execution**: Orchestrate parallel task distribution across multiple independent agents using LLexeM's syntax.
7. **Comprehensive Git-based Audit Trail**: Maintain full transparency and observability with Git-based change tracking, enabling temporal audits and replays.

## Installation

### System Requirements

- Python 3.x
- pip
- 
### Installation and Quick Run

1. Clone the repository:
```bash
git clone <repository_url>
cd <repository_directory>
```

2. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set Up Environment Variables:
    Ensure you have set your OpenAI API key:
```bash
export OPENAI_API_KEY='your-openai-api-key'
```

Note: Additional providers will be added in future releases, including provider and model selection for each call using our custom syntax.

### Usage

You can run the script from the command line with various arguments. Here is the general format:

``` bash
python llexem.py input_file.md [--task_file task_file.md] [--api_key your_api_key] [--operation your_operation] [--param_input_user_request your_part_path]
```

### Arguments

- `input_file.md`: (Required) Path to the input markdown file.
- `--task_file task_file.md`: (Optional) Path to the task markdown file. If not provided, the script will only parse and print the structure.
- `--api_key your_api_key`: (Optional) OpenAI API key. If not provided, it will use the `OPENAI_API_KEY` environment variable.
- `--operation your_operation`: (Optional) Default operation to perform. Defaults to "append".
- `--param_input_user_request your_part_path`: (Optional) Part path for `ParamInput-UserRequest`. Defaults to "ParamInput-UserRequest".

### Examples

#### Example 1: Basic Usage

Let's run basic test:

``` bash
python python llexem.py tests/Basic_Tests/main-test-0002-shell.md
```

Original `main-test-0002-shell.md` file:
```
# Question Decomposition and Analysis Agent
You have recieved input request in the previous block with {id = InputParameters}

@run macos-bash-assistant.md("get current user location using curl to some geo ip service") => target-block

# Here is block that would replace by output {id=target-block}
Some text on level 1, 1
Some text on level 1, 2

@run macos-bash-assistant.md("what is date and time now?") 
@run macos-bash-assistant.md("get current user weather using curl") 
```

As you can see, we are calling `macos-bash-assistant.md` with different tasks for an agent that generates shell commands (using LLM) to accomplish the task, runs them, summarizes results, and returns them to the main context. After all calls are executed, you can find created context .ctx files which store execution results of the context. Let's compare `main-test-0002-shell.md` and `main-test-0002-shell.ctx`:

![[Pasted image 20240804010908.png]]
All results are by default pasted after the corresponding @run operation, except the first one, which has the syntax: `=> target-block`. This tells the interpreter to replace the block with `{id=target-block}`.

Now, let's check how the last executed context for the `macos-bash-assistant.md` (file named `macos-bash-assistant.ctx`) looks like:
![[Pasted image 20240804011613.png]]
A few things happen here:

1. Our task is appended as a markdown block to the context of the agent.
2. It's being referenced in context for LLM to generate the proper `@shell` call.
3. After generation, the `@shell` call is executed by the interpreter.
4. Results are summarized by a call to the LLM for convenience.
5. The summary is returned as a result using `@return` to the main file execution context.

Previous execution states of `macos-bash-assistant.md` for the task of finding geo IP can be accessed directly from the git repo (a more convenient and easy-to-access method will be implemented in future releases. The roadmap is TBD, subscribe and follow to keep track of upcoming releases).

_**! More examples and tutorials will be added soon**_
### Other examples: 
#### Example 2: With Task File and API Key

Run the script with an input file, task file, and API key:

``` bash
python main.py input_file.md --task_file task_file.md --api_key your_api_key
```

#### Example 3: Specifying Operation and Task block

Run the script with an input file, task file, API key, operation, and a specific part path for `ParamInput-UserRequest`:

``` bash
python main.py input_file.md --task_file task_file.md --api_key your_api_key --operation your_operation --param_input_user_request your_part_path
```

### Environment Variable

You can set the `OPENAI_API_KEY` environment variable to avoid passing the API key every time:

```
export OPENAI_API_KEY="your_api_key"
```

## Introduction

LLexeM enables the definition and execution of complex workflows using a markdown-based syntax. It utilizes an Abstract Syntax Tree (AST) to parse and execute tasks, supporting operations such as importing other files, running shell commands, and interacting with Large Language Models (LLMs) like OpenAI's GPT (more to come soon!).

### Key Concepts

- **Nodes and AST**: The document is parsed into a hierarchical structure of nodes representing headings and operations.
- **Operations and Parsers**: Various operations (`@import`, `@run`, `@llm`, `@shell`, `@goto`, `@return`) are parsed and executed.
- **Flow Control and Execution**: Direct the flow of execution using operations and dynamic context handling.

## Supported Operations

### General Structure

Each operation follows a specific structure:
`@operation source_path (parameter) operand target_path`

- `@operation`: Type of operation.
- `source_path`: Path to the source block or file.
- `parameter`: Optional parameters for the operation.
- `operand`: Action to perform (`=>` for replace, `+>` for append, `.>` for prepend).
- `target_path`: Path to the target block.

### Operands

- `=>`: Replace the target block with the result.
- `+>`: Append the result to the target block.
- `.>`: Prepend the result to the target block.

### `@import`

The `@import` operation loads and parses content from an external markdown file or block, integrating it into the current context's Abstract Syntax Tree (AST). If any operand or target block is omitted, the default action is to append all content immediately after the operation in the current execution context's AST.

**Example:**

```markdown
@import /path/to/source/file.md
```

You can import a specific block by using the block ID after the filename:

```markdown
@import agents/tools.md/web-access-tools
```

To address specific nested blocks:

```markdown
@import agents/tools.md/Results-Validation/goals
```

To get all nested blocks:

```markdown
@import agents/tools.md/Results-Validation/*
```

Specify where and how the results should be applied to the current context:

```markdown
@import agents/tools.md/Results-Validation/* => Target-Block-To-Replace-Id/*
```

### `@llm`

The `@llm` operation calls the API of the selected LLM-provider to execute a prompt using the LLM model, adding part of the context you want the LLM to access.

**Basic syntax:**

```markdown
@llm ("Who is the author of Harry Potter?", # Harry Potter Info)
```

In the round brackets, specify two parameters: (Block or Prompt, Heading of output block). If the first parameter is a prompt (surrounded by single or double quotes), the call to the LLM will concatenate all previous heading blocks (excluding operations) in the current Abstract Syntax Tree (AST), attach your prompt, and pass it to the LLM chat completion endpoint. The return result will be inserted, appended, or prepended to the target specified by the operand and target syntax (e.g., `=>`, `+>`, `.>`).

**Example:**

```markdown

@llm ('Provide your analysis now', # AGENT RESULTS {id=Results})

// You'll get:

# AGENT RESULTS {id=Results}
Answer of LLM depending on the previous markdown blocks
```

or

```markdown
@llm (test-block2/*, # Nested Blocks Analysis Results {id=AI-Results})
```

The @llm operation sends the content of `test-block2` and all its child blocks to the LLM and creates a new block with the result titled `# Nested blocks analysis results {id=AI-Results}`.

### `@run`

The `@run` operation executes a markdown script in its own context, passing parameters and retrieving the returned result (via the `@return` operation).

**Syntax:**

```markdown
@run [script_path] (parameters) [operand] [target_path]
```

**Example:**

```markdown
@run macos-bash-assistant.md("get current user location using curl to some geo IP service") => target-block
```

#### Parameters Passing

Parameter passing is accomplished by appending a block or collection of nested blocks to the Abstract Syntax Tree (AST) of the target file at the start. By default, the head block is marked with `{id=InputParameters}` and can be accessed from the context of the executed file as part of the whole context or directly by addressing this block with `{id=InputParameters}`.

#### Handling Returned Results

For more details, refer to the `@return` operation. The returned block collection is placed in the current context by default after the `@run` operation that received the returned result. Alternatively, you can use the operand and target to specify any location in the context (including using the `/*` selector to address a group of nested blocks).

### `@shell`

The `@shell` operation executes a shell command and captures the output from the command's stdout.

**Syntax:**

```markdown
@shell ("command") [operand] [target_path]
```

**Example:**

```markdown
@shell ("ls -lt --color=never")
```

This executes the `ls` command and captures its output.

List files and save output:

```markdown
@shell ('ls -l') => file_list_block
```

Run OS find command and append the result:

```markdown
@shell ('find . -name "*.md" | xargs wc -l') +> markdown_stats
```

Note: It's recommended to suppress any ANSI codes on output if possible, e.g., using `--color=never` (for macOS).

### `@return`

The `@return` operation returns a block or set of blocks to the caller.

**Syntax:**

```markdown
@return InputParameters/*
```

When the interpreter meets `@return`, execution of the current context stops, and control is passed to the parent script (if present).

### `@goto`

The `@goto` operation passes execution to any block with an identifier.

**Syntax:**

```markdown
@goto SendAlert
```
This moves the execution point to the block with id "SendAlert".

## Contributing

We welcome contributions! We are working on creating a [Contributing Guide](CONTRIBUTING.md).

## License

LLexeM is released under the [MIT License](LICENSE).
