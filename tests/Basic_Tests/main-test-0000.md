# Question Decomposition and Analysis Agent
You have recieved input request in the previous block with {id = InputParameters}

@import agent-core/question-analyst-core-identity.md

# Here is hierarchy test 1.0 {id=hierarchy_test_010}
Some text on level 1, 1
Some text on level 1, 2

@run folder-file-list-analyser.md("Give me summary of the file list")

    ## Here is hierarchy test 2.0 {id=hierarchy_test_020}
    Some text on level 2.0, 1
    Some text on level 2.0, 2

        ### Here is hierarchy test 3.0 {id=hierarchy_test_030}
        Some text on level 3.0, 1
        Some text on level 3.0, 2


@run agent.md("What is sun?")

    ## Here is hierarchy test 2.1 {id=hierarchy_test_021}
    Some text on level 2.1, 1
    Some text on level 2.1, 2



## Sub-questions:

@llm ("Print top-5 bullets of first steps to create snake game in python")


