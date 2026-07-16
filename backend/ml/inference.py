import os
import uuid
import torch
import torch.nn as nn
import numpy as np
from torchvision import models, transforms
from PIL import Image
from pytorch_grad_cam import GradCAM
from pytorch_grad_cam.utils.model_targets import ClassifierOutputTarget
from pytorch_grad_cam.utils.image import show_cam_on_image

# ---- Config ----
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
CLASSES = ["NORMAL", "PNEUMONIA"]
MODEL_PATH = os.path.join(os.path.dirname(__file__), "best_model_densenet121.pth")

GRADCAM_OUTPUT_DIR = "uploads/gradcam"
ORIGINAL_OUTPUT_DIR = "uploads/original"
os.makedirs(GRADCAM_OUTPUT_DIR, exist_ok=True)
os.makedirs(ORIGINAL_OUTPUT_DIR, exist_ok=True)

# ---- Load model once at module import (not per-request) ----
_model = models.densenet121(weights=None)
_model.classifier = nn.Linear(_model.classifier.in_features, len(CLASSES))
_model.load_state_dict(torch.load(MODEL_PATH, map_location=DEVICE))
_model = _model.to(DEVICE)
_model.eval()

_target_layers = [_model.features.norm5]
_cam = GradCAM(model=_model, target_layers=_target_layers)

_preprocess = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])


def _get_risk_tier(pred_class: int, confidence: float) -> str:
    if pred_class == 0:  # NORMAL
        return "Low"
    if confidence >= 0.90:
        return "High"
    elif confidence >= 0.70:
        return "Medium"
    else:
        return "Low-Medium (uncertain)"


def run_inference(image: Image.Image) -> dict:
    """
    Takes a PIL Image, runs prediction + Grad-CAM, saves both original and
    heatmap images to disk, and returns a dict with all result data.
    Caller (scan_routes.py) is responsible for saving this dict to the DB.
    """
    img = image.convert("RGB")
    img_resized = img.resize((224, 224))
    rgb_img = np.float32(img_resized) / 255.0

    input_tensor = _preprocess(img).unsqueeze(0).to(DEVICE)

    # ---- Prediction ----
    with torch.no_grad():
        outputs = _model(input_tensor)
        probs = torch.softmax(outputs, dim=1)[0]
        pred_class = torch.argmax(probs).item()
        confidence = probs[pred_class].item()

    # ---- Grad-CAM ----
    targets = [ClassifierOutputTarget(pred_class)]
    grayscale_cam = _cam(input_tensor=input_tensor, targets=targets)[0]
    cam_image = show_cam_on_image(rgb_img, grayscale_cam, use_rgb=True)

    # ---- Risk tier ----
    risk_tier = _get_risk_tier(pred_class, confidence)

    # ---- Save both images to disk with unique filenames ----
    file_id = str(uuid.uuid4())

    original_filename = f"{file_id}_original.png"
    gradcam_filename = f"{file_id}_gradcam.png"

    original_path = os.path.join(ORIGINAL_OUTPUT_DIR, original_filename)
    gradcam_path = os.path.join(GRADCAM_OUTPUT_DIR, gradcam_filename)

    img_resized.save(original_path)
    Image.fromarray(cam_image).save(gradcam_path)

    return {
        "prediction": CLASSES[pred_class],
        "confidence": round(confidence, 4),
        "risk_tier": risk_tier,
        "original_image_path": original_path,
        "gradcam_image_path": gradcam_path,
    }