import json
import os
import time

from dotenv import load_dotenv
from google import genai
from google.genai import errors as genai_errors

load_dotenv(override=True)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

MAX_RETRIES = 4
RETRY_BACKOFF_SECONDS = 2


PROMPT_TEMPLATE = """Based on the following transcript, generate a quiz in valid JSON format.

The quiz must follow this exact structure:

{{
  "title": "Create a concise quiz title based on the topic of the transcript.",
  "description": "Summarize the transcript in no more than 150 characters. Do not include any quiz questions or answers.",
  "questions": [
    {{
      "question_title": "The question goes here.",
      "question_options": ["Option A", "Option B", "Option C", "Option D"],
      "answer": "The correct answer from the above options"
    }},
    ...
    (exactly 10 questions)
  ]
}}

Requirements:
- Each question must have exactly 4 distinct answer options.
- Only one correct answer is allowed per question, and it must be present in 'question_options'.
- The output must be valid JSON and parsable as-is (e.g., using Python's json.loads).
- Do not include explanations, comments, or any text outside the JSON.

Transcript:
{transcript}
"""


def _parse_response_text(text: str) -> dict:
    """Strip markdown code fences from the response and parse it as JSON."""
    text = text.strip()
    if text.startswith("```"):
        text = text.split("```", 2)[1]
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    return json.loads(text)


def _attempt_generate(prompt: str) -> dict:
    """Send a single request to the Gemini API and return the parsed result."""
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )
    return _parse_response_text(response.text)


def _call_with_retry(prompt: str) -> dict:
    """Retry the Gemini API call on 429/503 or invalid JSON, with exponential backoff."""
    last_exc = None
    for attempt in range(MAX_RETRIES):
        try:
            return _attempt_generate(prompt)
        except (genai_errors.ServerError, genai_errors.ClientError) as exc:
            if hasattr(exc, 'status_code') and exc.status_code not in (429, 503):
                raise
            last_exc = exc
        except json.JSONDecodeError as exc:
            last_exc = exc
        if attempt < MAX_RETRIES - 1:
            time.sleep(RETRY_BACKOFF_SECONDS * (2 ** attempt))
    raise last_exc


def generate_questions(transcript: str) -> dict:
    """Build the prompt from the transcript and return a quiz dict from Gemini."""
    prompt = PROMPT_TEMPLATE.format(transcript=transcript)
    return _call_with_retry(prompt)