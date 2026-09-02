import json
import re

from llm.openrouter_client import OpenRouterClient

MEMORY_EXTRACTION_PROMPT = """
You are a memory extraction system for a general-purpose chatbot.

Identify information from the user's message that is useful to
remember across future conversations.

Remember:
- Stable personal facts
- User preferences
- Long-term interests
- Skills
- Ongoing projects
- Long-term goals
- Recurring habits

Do NOT remember:
- Temporary requests
- Greetings
- Casual conversation
- Questions without personal information
- Temporary states such as "I am hungry right now"
- Information about unrelated third parties

Return ONLY a JSON object.

Required format:

{
  "should_remember": true,
  "memories": [
    {
      "text": "concise memory",
      "type": "profile",
      "importance": 0.8,
      "confidence": 1.0
    }
  ]
}

Allowed types:
profile, preference, interest, skill, project, goal, habit, other

Importance range [0.0, 1.0]
Confidence range [0.0, 1.0]

If there is nothing worth remembering:

{
  "should_remember": false,
  "memories": []
}

Importance and confidence must be numbers between 0 and 1.
"""


class MemoryExtractor:
    def __init__(self):
        self.llm = OpenRouterClient()

    def _extract_json(self, response):
        response = response.strip()

        # Case 1: Response is already valid JSON
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass

        # Case 2: JSON wrapped in ```json ... ```
        match = re.search(
            r"```(?:json)?\s*(\{.*?\})\s*```",
            response,
            re.DOTALL
        )

        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # Case 3: Find the first JSON object
        start = response.find("{")
        end = response.rfind("}")

        if start != -1 and end != -1 and end > start:
            json_text = response[start:end + 1]
            try:
                return json.loads(json_text)
            except json.JSONDecodeError:
                pass
        return None

    def _validate_result(self, result):
        if not isinstance(result, dict):
            return None
        if "should_remember" not in result:
            return None
        if "memories" not in result:
            return None
        if not isinstance(result["should_remember"], bool):
            return None
        if not isinstance(result["memories"], list):
            return None
        for memory in result["memories"]:
            if not isinstance(memory, dict):
                return None
            required_fields = [
                "text",
                "type",
                "importance",
                "confidence"
            ]

            if not all(field in memory for field in required_fields):
                return None
            if not isinstance(memory["importance"], (int, float)):
                return None
            if not isinstance(memory["confidence"], (int, float)):
                return None
            if not 0 <= memory["importance"] <= 1:
                return None
            if not 0 <= memory["confidence"] <= 1:
                return None

        return result

    def extract(self, user_message):
        messages = [
            {
                "role": "system",
                "content": MEMORY_EXTRACTION_PROMPT
            },
            {
                "role": "user",
                "content": user_message
            }
        ]

        response = self.llm.generate_response(messages)
        result = self._extract_json(response)
        result = self._validate_result(result)

        if result is None:
            print(
                "\nWarning: Memory extractor produced "
                "an invalid response."
            )

            print("Raw response:")
            print(response)

            return {
                "should_remember": False,
                "memories": []
            }

        return result