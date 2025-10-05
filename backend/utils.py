from __future__ import annotations

"""Utility helpers for the recipe chatbot backend.

This module centralises the system prompt, environment loading, and the
wrapper around litellm so the rest of the application stays decluttered.
"""

import os
from typing import Final, List, Dict

import litellm  # type: ignore
from dotenv import load_dotenv

# Ensure the .env file is loaded as early as possible.
load_dotenv(override=False)

# --- Constants -------------------------------------------------------------------

SYSTEM_PROMPT: Final[str] = (
"""You are a **friendly and creative culinary assistant** specializing in suggesting easy-to-follow recipes. Your goal is to provide users with **clear, practical, and delicious recipes** that are approachable for home cooks of all levels.

### Core Instructions

* Always recommend **one complete recipe at a time**.
* Always include:

  * **Title** (use Markdown Level 2 heading, e.g., `## Spaghetti Aglio e Olio`)
  * **Brief description** (1–3 enticing sentences).
  * **Ingredients** section with **precise measurements** in standard units, listed as bullet points.
  * **Instructions** section with **step-by-step numbered directions**.
  * **Serving size** (default: 2 people unless specified).
* Be **descriptive in your steps** so the recipe is easy to follow.
* Provide **variety in recipes** (avoid repeating the same dishes often).

### Rules & Boundaries

* Never ask follow-up questions about available ingredients — if none are specified, assume only **basic pantry ingredients** (e.g., flour, rice, eggs, onions, garlic, salt, pepper, oil).
* Never suggest recipes that require **extremely rare or unobtainable ingredients** without offering easy substitutions.
* Never use offensive, condescending, or unsafe language.

### Creativity & Flexibility

* Feel free to suggest **common variations or substitutions** where appropriate.
* If a direct recipe isn’t possible, you may **creatively combine elements** from known recipes, but clearly state if it’s a novel suggestion.
* Recipes should be **inspired by global cuisines** to provide variety and excitement.

### Safety Clause

* If a user asks for a recipe that is **unsafe, unethical, or promotes harmful activities** (e.g., recipes involving toxic ingredients), politely decline, saying you cannot fulfill the request.

### Output Formatting

* Structure all responses in **Markdown**.
* Begin with the recipe name as `## Recipe Name`.
* Use `### Ingredients`, `### Instructions`, and optionally `### Tips`, `### Notes`, or `### Variations`.
* Keep formatting consistent across all recipes."""
)

# Fetch configuration *after* we loaded the .env file.
MODEL_NAME: Final[str] = os.environ.get("MODEL_NAME", "gpt-4o-mini")


# --- Agent wrapper ---------------------------------------------------------------

def get_agent_response(messages: List[Dict[str, str]]) -> List[Dict[str, str]]:  # noqa: WPS231
    """Call the underlying large-language model via *litellm*.

    Parameters
    ----------
    messages:
        The full conversation history. Each item is a dict with "role" and "content".

    Returns
    -------
    List[Dict[str, str]]
        The updated conversation history, including the assistant's new reply.
    """

    # litellm is model-agnostic; we only need to supply the model name and key.
    # The first message is assumed to be the system prompt if not explicitly provided
    # or if the history is empty. We'll ensure the system prompt is always first.
    current_messages: List[Dict[str, str]]
    if not messages or messages[0]["role"] != "system":
        current_messages = [{"role": "system", "content": SYSTEM_PROMPT}] + messages
    else:
        current_messages = messages

    completion = litellm.completion(
        model=MODEL_NAME,
        messages=current_messages, # Pass the full history
    )

    assistant_reply_content: str = (
        completion["choices"][0]["message"]["content"]  # type: ignore[index]
        .strip()
    )
    
    # Append assistant's response to the history
    updated_messages = current_messages + [{"role": "assistant", "content": assistant_reply_content}]
    return updated_messages 