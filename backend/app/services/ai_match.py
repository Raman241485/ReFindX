import os
import json
import mimetypes
import re

from google import genai
from google.genai import types

from pydantic import BaseModel


# ============================================================
# GEMINI AI
# ============================================================

MODEL_NAME = "gemini-3-flash-preview"

client = None


# ============================================================
# STRUCTURED RESPONSE MODEL
# ============================================================

class ImageMatchResult(BaseModel):

    similarity_score: float

    reason: str


# ============================================================
# GET GEMINI CLIENT
# ============================================================

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
# EXTRACT JSON FROM RESPONSE
# ============================================================

def extract_json(
    text: str,
):

    if not text:

        raise ValueError(
            "Gemini returned an empty response."
        )


    text = text.strip()


    # --------------------------------------------------------
    # Remove markdown fences
    # --------------------------------------------------------

    text = re.sub(
        r"^```(?:json)?\s*",
        "",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"\s*```$",
        "",
        text,
    ).strip()


    # --------------------------------------------------------
    # Direct JSON
    # --------------------------------------------------------

    try:

        return json.loads(
            text
        )

    except json.JSONDecodeError:

        pass


    # --------------------------------------------------------
    # Find first JSON object
    # --------------------------------------------------------

    start = text.find(
        "{"
    )

    end = text.rfind(
        "}"
    )


    if (
        start != -1
        and end != -1
        and end > start
    ):

        json_text = text[
            start:end + 1
        ]

        try:

            return json.loads(
                json_text
            )

        except json.JSONDecodeError:

            pass


    raise ValueError(
        "Gemini returned invalid JSON: "
        + repr(text)
    )


# ============================================================
# GEMINI COMPARISON REQUEST
# ============================================================

def request_match(
    image1,
    image2,
):

    prompt = """
Compare Image 1 and Image 2 for a lost-and-found
item matching system.

Determine whether they could be the SAME physical item.

Consider:

- object type
- color
- shape
- visible design
- logos
- text
- scratches
- unique marks
- patterns
- accessories
- other identifying visual features

Do NOT consider two items a match merely because
they belong to the same category.

Look for specific visual evidence.

Return:

similarity_score:
A number between 0.0 and 1.0.

reason:
A short explanation of the visual evidence.

IMPORTANT:
Return ONLY the JSON object.
Do not write:
"Here is the JSON"
Do not use markdown.
Do not use ```json.
The first character of your response must be {.

Example:

{
  "similarity_score": 0.87,
  "reason": "Both images show the same blue backpack with the same front logo and zipper pattern."
}
"""


    response = (
        get_client()
        .models
        .generate_content(

            model=MODEL_NAME,

            contents=[
                prompt,
                image1,
                image2,
            ],

            config=types.GenerateContentConfig(

                temperature=0,

                max_output_tokens=500,

                response_mime_type=(
                    "application/json"
                ),

                response_schema=(
                    ImageMatchResult
                ),
            ),
        )
    )


    # ========================================================
    # TRY STRUCTURED PARSED RESPONSE
    # ========================================================

    parsed = getattr(
        response,
        "parsed",
        None,
    )


    if parsed:

        if isinstance(
            parsed,
            ImageMatchResult,
        ):

            return {

                "similarity_score":
                    parsed.similarity_score,

                "reason":
                    parsed.reason,
            }


        if isinstance(
            parsed,
            dict,
        ):

            return parsed


    # ========================================================
    # TEXT RESPONSE
    # ========================================================

    text = (
        getattr(
            response,
            "text",
            None,
        )
        or ""
    ).strip()


    # ========================================================
    # PARSE JSON
    # ========================================================

    try:

        return extract_json(
            text
        )

    except ValueError as error:

        print(
            "GEMINI FIRST RESPONSE:",
            repr(text),
        )

        raise error


# ============================================================
# COMPARE TWO IMAGES
# ============================================================

def compare_images(
    image1_path: str,
    image2_path: str,
):
    """
    Compare two lost/found item images.

    Returns:

    {
        "similarity_score": 0.87,
        "reason": "..."
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
    # CREATE IMAGE PARTS
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
    # REQUEST
    # ========================================================

    try:

        result = request_match(
            image1,
            image2,
        )


    except Exception as first_error:

        # ====================================================
        # RETRY ON BAD MODEL OUTPUT
        # ====================================================

        print(
            "AI MATCH FIRST ATTEMPT FAILED:",
            first_error,
        )

        retry_prompt = """
You are comparing two images for a lost-and-found
application.

Return ONLY one valid JSON object.

The JSON MUST have exactly these fields:

{
  "similarity_score": 0.0,
  "reason": "short explanation"
}

Rules:

- similarity_score must be a number from 0.0 to 1.0
- reason must be a short string
- Do not add any other fields
- Do not add markdown
- Do not add ```json
- Do not write any introduction
- Start the response directly with {
"""


        retry_response = (
            get_client()
            .models
            .generate_content(

                model=MODEL_NAME,

                contents=[
                    retry_prompt,
                    image1,
                    image2,
                ],

                config=types.GenerateContentConfig(

                    temperature=0,

                    max_output_tokens=500,

                    response_mime_type=(
                        "application/json"
                    ),

                    response_schema=(
                        ImageMatchResult
                    ),
                ),
            )
        )


        retry_text = (
            getattr(
                retry_response,
                "text",
                None,
            )
            or ""
        ).strip()


        print(
            "GEMINI RETRY RESPONSE:",
            repr(retry_text),
        )


        try:

            result = extract_json(
                retry_text
            )

        except Exception as retry_error:

            raise RuntimeError(
                "Gemini returned invalid JSON "
                "after retry: "
                + repr(retry_text)
            ) from retry_error


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
    # CLAMP SCORE
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
    ).strip()


    if not reason:

        reason = (
            "Visual similarity detected."
        )


    # ========================================================
    # FINAL RESULT
    # ========================================================

    return {

        "similarity_score":
            score,

        "reason":
            reason,
    }