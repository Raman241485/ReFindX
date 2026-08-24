import os
import json
import mimetypes

from google import genai
from google.genai import types


# ============================================================
# GEMINI AI
# ============================================================

MODEL_NAME = "gemini-3-flash-preview"

client = None


def get_client():
    global client

    if client is None:

        api_key = os.getenv(
            "GEMINI_API_KEY"
        )

        if not api_key:

            raise RuntimeError(
                "GEMINI_API_KEY environment variable "
                "is not configured."
            )

        client = genai.Client(
            api_key=api_key
        )

    return client


# ============================================================
# IMAGE MIME TYPE
# ============================================================

def get_mime_type(
    image_path: str,
):

    mime_type, _ = mimetypes.guess_type(
        image_path
    )

    if not mime_type:

        mime_type = "image/jpeg"

    return mime_type


# ============================================================
# COMPARE TWO IMAGES
# ============================================================

def compare_images(
    image1_path: str,
    image2_path: str,
):
    """
    Compare two lost/found item images using Gemini.

    Returns:

    {
        "similarity_score": 0.87,
        "reason": "Both images show..."
    }
    """

    # ========================================================
    # CHECK IMAGE 1
    # ========================================================

    if not os.path.exists(
        image1_path
    ):

        raise FileNotFoundError(
            f"Image not found: {image1_path}"
        )


    # ========================================================
    # CHECK IMAGE 2
    # ========================================================

    if not os.path.exists(
        image2_path
    ):

        raise FileNotFoundError(
            f"Image not found: {image2_path}"
        )


    # ========================================================
    # READ IMAGE 1
    # ========================================================

    with open(
        image1_path,
        "rb",
    ) as file:

        image1_bytes = file.read()


    # ========================================================
    # READ IMAGE 2
    # ========================================================

    with open(
        image2_path,
        "rb",
    ) as file:

        image2_bytes = file.read()


    # ========================================================
    # CREATE GEMINI IMAGE PARTS
    # ========================================================

    image1 = types.Part.from_bytes(

        data=image1_bytes,

        mime_type=get_mime_type(
            image1_path
        ),
    )


    image2 = types.Part.from_bytes(

        data=image2_bytes,

        mime_type=get_mime_type(
            image2_path
        ),
    )


    # ========================================================
    # AI PROMPT
    # ========================================================

    prompt = """
You are an AI lost-and-found image matching system.

Compare Image 1 and Image 2.

Determine whether they could represent the SAME
physical item.

Consider:

- object type
- color
- shape
- size
- visible design
- logos
- text
- scratches
- unique marks
- patterns
- accessories
- other identifying visual features

IMPORTANT:

Do not assume two items are the same just because
they belong to the same category.

Look for specific visual evidence.

Give a similarity score from 0 to 1.

Return ONLY valid JSON.

Required format:

{
  "similarity_score": 0.00,
  "reason": "short explanation"
}

Score meaning:

0.00 = completely different
0.50 = uncertain
0.80 = strong possible match
0.90 = very strong possible match
1.00 = extremely strong match
"""


    # ========================================================
    # GEMINI REQUEST
    # ========================================================

    response = get_client().models.generate_content(

        model=MODEL_NAME,

        contents=[
            prompt,
            image1,
            image2,
        ],

        config=types.GenerateContentConfig(

            temperature=0,

            max_output_tokens=200,

        ),
    )


    # ========================================================
    # RESPONSE TEXT
    # ========================================================

    if not response.text:

        raise RuntimeError(
            "Gemini returned an empty response."
        )


    text = response.text.strip()


    # ========================================================
    # REMOVE MARKDOWN CODE FENCES
    # ========================================================

    if text.startswith("```"):

        text = (
            text
            .replace(
                "```json",
                "",
            )
            .replace(
                "```",
                "",
            )
            .strip()
        )


    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        result = json.loads(
            text
        )

    except json.JSONDecodeError:

        raise RuntimeError(
            "Gemini returned invalid JSON: "
            + text
        )


    # ========================================================
    # GET SCORE
    # ========================================================

    try:

        score = float(
            result.get(
                "similarity_score",
                0,
            )
        )

    except (
        TypeError,
        ValueError,
    ):

        score = 0.0


    # ========================================================
    # KEEP SCORE BETWEEN 0 AND 1
    # ========================================================

    score = max(
        0.0,
        min(
            1.0,
            score,
        ),
    )


    # ========================================================
    # GET REASON
    # ========================================================

    reason = str(
        result.get(
            "reason",
            "Visual similarity detected.",
        )
    )


    # ========================================================
    # RETURN RESULT
    # ========================================================

    return {

        "similarity_score":
            score,

        "reason":
            reason,
    }