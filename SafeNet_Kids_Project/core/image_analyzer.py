import numpy as np
from PIL import ImageGrab
import cv2
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
import tensorflow as tf

class ImageAnalyzer:
    def __init__(self, model_path="data/nsfw_model.h5"):
        self.model_path = model_path
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            if os.path.exists(self.model_path):
                self.model = tf.keras.models.load_model(self.model_path)
        except Exception:
            pass

    def capture_and_analyze(self):
        try:
            screen = ImageGrab.grab()
            img = cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)
            return self.predict_image(img)
        except Exception:
            return False

    def predict_image(self, img):
        if self.model is None:
            return self._fallback_heuristic(img)
        try:
            resized = cv2.resize(img, (224, 224))
            normalized = resized / 255.0
            reshaped = np.reshape(normalized, (1, 224, 224, 3))
            prediction = self.model.predict(reshaped, verbose=0)
            return prediction[0][0] > 0.8
        except Exception:
            return False

    def _fallback_heuristic(self, img):
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        lower_skin = np.array([0, 20, 70], dtype=np.uint8)
        upper_skin = np.array([20, 255, 255], dtype=np.uint8)
        mask = cv2.inRange(hsv, lower_skin, upper_skin)
        skin_ratio = cv2.countNonZero(mask) / (img.shape[0] * img.shape[1])
        return skin_ratio > 0.6