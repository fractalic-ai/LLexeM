# Its a test-case-0002 {id=block1}
This is test case that tests run operations
Next we'll import whole file

@run sub-tests/run-test-agent.md("What is sun?")

# Here is run test 1.0 {id=block2}
We are going to run 

@run sub-tests/run-test-agent-2.md("Here gonna be the same return as param")

    ## Here is run test 2.0 {id=block3}
    We are going to run 

# Here is run test 3.0 {id=block4-proto}
I would be replaced by data of next node using proxy agent

# Here is run test 3.0 {id=block4}
Ill be back next)) we'll pass block as pararm to agent and it should return it back

# Here is run test 4.0 {id=block5}
we'll pass block as pararm to agent and it should return it back

-not-run sub-tests/run-test-agent-2.md(block4) .> block4-proto
-not-run sub-tests/run-test-agent-2.md(block4) +> block4-proto
-not-run sub-tests/run-test-agent-2.md(block5) => block4-proto

# Here is run test 5.0 {id=block5}
eof node