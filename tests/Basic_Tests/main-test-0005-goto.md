# Text block 1
You should ignore previous text and request. It's for testing purposes. Focus on the next questions about the books.

@llm ("Who is the author of the Harry Potter?", # Harry Potter info)

# Text block 1.1
This is text block 

@goto text-block4

# Text block 2
This is text block 

@llm ("Who is the auhtor of the Dune?", # Dune info)

# Text block 3
This is text block 

@llm ("Who is the author of the Stainless Steel Rat?", # SSR info)

# Text block 4 {id=text-block4}   
This is text block 

@llm ("Who is the author of the The Foundation?", # SSR info)
