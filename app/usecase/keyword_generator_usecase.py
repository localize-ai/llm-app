import os

from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnablePassthrough
from pydantic import BaseModel, Field

# Load the environment variables
load_dotenv()


class KeywordGeneratorResponse(BaseModel):
    """
    Keyword generator response schema.
    """

    keyword: str = Field(description="Generated keyword string")
    is_image_search: bool = Field(
        description="Whether the keyword is for an image search"
    )

# Sometimes the bedrock is not available, so we use the groq API
if (
    os.getenv("AWS_SECRET_ACCESS_KEY") is not None
    and os.getenv("AWS_ACCESS_KEY_ID") is not None
):
    llm = ChatBedrock(
        region_name="ap-south-1",
        aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
        aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        model_id="meta.llama3-70b-instruct-v1:0",
        temperature=0.5,
        max_tokens=1000,
        verbose=True,
    )
else:
    llm = ChatGroq(
        model="llama-3.2-90b-vision-preview",
        temperature=1.5,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=os.getenv("GROQ_API_KEY"),
    )

# Define the system prompt
system_prompt = """
Given the following parameters, generate a JSON object with fields `keyword` and `is_image_search` optimized for vector search to find a specific type of place in a database:

- `q`: (user input text) — the primary search query, which could be a place name, address, or general search term.
- `category` (optional) — a specific style or type of place, such as work-friendly, classic-vibes, hidden-gem, etc.

Instructions:

- If `q` is a place name or address, include it as is in the `keyword` field without modification.
- If `category` is provided, include it as a qualifier in the `keyword` field to narrow down the search intent.
- If `category` is not provided, rely solely on `q` to form the `keyword`.
- Determine the value of `is_image_search`. If the query is a place name or address, set `is_image_search` to `false`. Otherwise, set it to `true`.
- Do not add extra context, and only output the JSON object.
- **Return with the ```json``` tag.**

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
    | llm.with_structured_output(KeywordGeneratorResponse)
)


# Generate a keyword string based on the search phrase and category
def generate_keyword(search_phrase, category=None) -> KeywordGeneratorResponse:
    """
    Generate a keyword string based on the search phrase and category.
    """
    retries = 3
    for attempt in range(retries):
        try:
            # Run the keyword generator chain
            return keyword_generator_chain.invoke({"q": search_phrase, "category": category})
        except Exception as e:
            if attempt < retries - 1:
                print(f"Attempt {attempt + 1} failed: {e}. Retrying...")
            else:
                print(f"Attempt {attempt + 1} failed: {e}. No more retries left.")
                raise
