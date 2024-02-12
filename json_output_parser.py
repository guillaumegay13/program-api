from langchain.schema import BaseOutputParser
import json

class UnescapedJsonOutputParser(BaseOutputParser[dict]):
    """Parse the output of an LLM call to a dictionary."""

    def parse(self, input: str) -> dict:
        """Parse the output of an LLM call."""
        # Convert the input JSON string to a dictionary
        input_dict = json.loads(input)
        return input_dict