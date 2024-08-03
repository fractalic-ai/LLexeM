# Its a test-case-0001 {id=block1}
This is test case that tests import operations
Next we'll import whole file

@import sub-tests/sub-test-case-import.md

# Here is hierarchy test 1.0 {id=block2}
We are going to import one block by id
@import sub-tests/sub-test-case-import.md/test-block1/*

# Here is hierarchy test 2.0 {id=block3}
We are going to import one block by id and include hierarchy (it should talke +1 block)
TODO: Its not working with asteriks suffix !
@import sub-tests/sub-test-case-import.md/test-block2/*

# Here is hierarchy test 3.0 {id=block3}
We are going to import one block by id, explicitly setting its path
@import sub-tests/sub-test-case-import.md/test-block1/test-block2/test-block3/*

# just some test temp block
just a stub block

# This block would recieve import results for replace {id=recieve-replace}
This block should be replaced by the import instruction

# Last block that would call import with replace
After this block we replace previous block with part of import

@import sub-tests/sub-test-case-import.md/test-block2/* => recieve-replace