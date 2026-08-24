import os

import torch

from PIL import Image

from transformers import (
    CLIPModel,
    CLIPProcessor,
)


# ============================================================
# CLIP MODEL
# ============================================================

MODEL_NAME = "openai/clip-vit-base-patch32"


processor = CLIPProcessor.from_pretrained(
    MODEL_NAME
)

model = CLIPModel.from_pretrained(
    MODEL_NAME
)

model.eval()


# ============================================================
# IMAGE EMBEDDING
# ============================================================

def get_image_embedding(
    image_path: str,
):
    """
    Convert an image into a normalized
    CLIP image embedding.
    """

    if not os.path.exists(image_path):
        raise FileNotFoundError(
            f"Image not found: {image_path}"
        )

    image = Image.open(
        image_path
    ).convert("RGB")

    inputs = processor(
        images=image,
        return_tensors="pt",
    )

    with torch.no_grad():

        output = model.get_image_features(
            **inputs
        )

    # --------------------------------------------------------
    # Transformers compatibility
    # --------------------------------------------------------
    # Newer transformers versions may return
    # BaseModelOutputWithPooling instead of a Tensor.
    #
    # The actual CLIP embedding is available through
    # .pooler_output in that output.
    # --------------------------------------------------------

    if hasattr(output, "image_embeds"):

        image_features = output.image_embeds

    elif hasattr(output, "pooler_output"):

        image_features = output.pooler_output

    elif torch.is_tensor(output):

        image_features = output

    elif isinstance(output, tuple):

        image_features = output[0]

    else:

        raise TypeError(
            "Unsupported CLIP output type: "
            f"{type(output)}"
        )

    # --------------------------------------------------------
    # Normalize embedding
    # --------------------------------------------------------

    image_features = (
        image_features
        / image_features.norm(
            p=2,
            dim=-1,
            keepdim=True,
        ).clamp(min=1e-12)
    )

    return image_features


# ============================================================
# COSINE SIMILARITY
# ============================================================

def calculate_similarity(
    embedding1,
    embedding2,
):
    """
    Calculate cosine similarity between
    two normalized CLIP embeddings.
    """

    similarity = torch.nn.functional.cosine_similarity(
        embedding1,
        embedding2,
        dim=-1,
    )

    return float(
        similarity.item()
    )