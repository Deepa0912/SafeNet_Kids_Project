import os
import cv2
import numpy as np
import tensorflow as tf
import logging
from datetime import datetime
from PIL import ImageGrab

class AIImageModerator:
    """
    Advanced AI-driven image moderation module.
    Analyzes screenshots for Adult content, Violence, and other inappropriate imagery.
    """

    def __init__(self, model_path="data/moderation_model.h5"):
        self.model_path = model_path
        self.model = None
        self.labels = ["Safe", "Adult", "Violence", "Gore"]
        self.log_file = "data/moderation_history.log"
        self.evidence_dir = "data/evidence/moderation"
        
        self._setup_logging()
        self._load_model()
        os.makedirs(self.evidence_dir, exist_ok=True)

    def _setup_logging(self):
        self.logger = logging.getLogger("AIImageModerator")
        if not self.logger.handlers:
            handler = logging.FileHandler(self.log_file, encoding='utf-8')
            handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
            self.logger.addHandler(handler)
            self.logger.setLevel(logging.INFO)

    def _load_model(self):
        """Loads the pre-trained TensorFlow model."""
        try:
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
                print(f"AI Image Moderator: Model loaded from {self.model_path}")
            else:
                print(f"AI Image Moderator: Warning - Model not found at {self.model_path}. Using fallback heuristics.")
        except Exception as e:
            print(f"AI Image Moderator: Error loading model - {e}")

    def capture_and_analyze(self):
        """Captures screen and performs multi-class moderation analysis."""
        try:
            screen = ImageGrab.grab()
            frame = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
            return self.predict_image(frame, screen)
        except Exception as e:
            self.logger.error(f"Capture error: {e}")
            return "Safe", 1.0

    def predict_image(self, img, original_pil=None):
        """
        Classifies the image and returns (label, confidence).
        If no model is loaded, falls back to a basic color-based heuristic.
        """
        if self.model:
            try:
                # Preprocess for model (typical MobileNet/Inception input)
                resized = cv2.resize(img, (224, 224))
                normalized = resized / 255.0
                reshaped = np.reshape(normalized, (1, 224, 224, 3))
                
                predictions = self.model.predict(reshaped, verbose=0)[0]
                max_idx = np.argmax(predictions)
                label = self.labels[max_idx]
                confidence = float(predictions[max_idx])
                
                if label != "Safe" and confidence > 0.7:
                    self._handle_violation(label, confidence, original_pil or img)
                
                return label, confidence
            except Exception as e:
                self.logger.error(f"Inference error: {e}")
        
        # Fallback heuristic if model is missing or fails
        return self._fallback_heuristic(img)

    def _fallback_heuristic(self, img):
        """Basic skin-tone and color intensity heuristic."""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        # Simple skin detection
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        skin_ratio = cv2.countNonZero(mask) / (img.shape[0] * img.shape[1])
        
        if skin_ratio > 0.45:
            return "Adult (Heuristic)", skin_ratio
        
        return "Safe", 1.0

    def _handle_violation(self, label, confidence, img):
        """Logs the violation and saves the image as evidence."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{label}_{timestamp}.png"
        path = os.path.join(self.evidence_dir, filename)
        
        try:
            if hasattr(img, 'save'): # PIL Image
                img.save(path)
            else: # OpenCV Mat
                cv2.imwrite(path, img)
        except Exception as e:
            path = f"Save failed: {e}"

        self.logger.warning(f"VIOLATION DETECTED: {label} | Confidence: {confidence:.2f} | Evidence: {path}")
