import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough

# Load the environment variables
load_dotenv()

llm = ChatGroq(
    model="llama-3.2-90b-text-preview",
    temperature=1.5,
    max_tokens=None,
    timeout=None,
    max_retries=2,
    api_key=os.getenv("GROQ_API_KEY"),
    verbose=True,
)

# Define the system prompt
system_prompt = """
Given the following parameters, generate a single search keyword string optimized for vector search to find a specific type of place in a database:

- `q`: (user input text) — the primary search query, which could be a place name, address, or general search term.
- `category` (optional) — a specific style or type of place, such as work-friendly, classic-vibes, hidden-gem, etc.

Instructions:

- If `q` is a place name or address, include it as is in the keyword string without modification.
- If `category` is provided, include it as a qualifier in the keyword string to narrow down the search intent.
- If `category` is not provided, rely solely on `q` to form the search keyword.
- Do not add extra context, and only output the keyword string.
- **Just return the keyword string.**

## Input:
- `q`: {q}
- `category`: {category}
"""

# Create a prompt template
prompt = PromptTemplate(
    template=system_prompt,
    input_variables=["q", "category"],
)

# Define the keyword generator chain
keyword_generator_chain = (
    {
        "q": RunnablePassthrough(),
        "category": RunnablePassthrough(),
    }
    | prompt
    | llm
    | StrOutputParser()
)


# Generate a keyword string based on the search phrase and category
def generate_keyword(search_phrase, category=None) -> str:
    """
    Generate a keyword string based on the search phrase and category.
    """
    # Run the keyword generator chain
    output = keyword_generator_chain.invoke({"q": search_phrase, "category": category})
    return output
