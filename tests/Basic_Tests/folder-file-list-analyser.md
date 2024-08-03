# THIS IS AGENT
- You have recieved input request in the previous block 
- You are the agent that uses shell tool output to answer youser question as a summary over file list


# Its a file list for 6 lines of ls
@shell ("ls -lt --color=never")

@llm ("Provide your summary to user question, two sentences max", # AGENT RESULTS {id=Results})

@return Results