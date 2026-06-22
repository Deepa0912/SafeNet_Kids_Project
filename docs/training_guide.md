# AI Image Moderation - Training Guide

This guide provides instructions and dataset suggestions for training a custom image moderation model for SafeNet Kids.

## 1. Recommended Datasets

To build a robust multi-class classifier, you should combine several reputable datasets:

### Adult/NSFW Content
- **Yahoo OpenNSFW**: A standard dataset for detecting "not safe for work" images.
- **NSFW Data Scraper**: Available on GitHub, this tool allows you to scrape thousands of balanced images (Safe, Porn, Hentai, Sexy).
- **Kaggle: NSFW Images**: Various community-contributed datasets for explicit content detection.

### Violence & Gore
- **UCF-Crime**: Large dataset for detecting anomalies in surveillance videos, including fighting and robbery.
- **Hockey Fight Dataset**: Specifically for detecting physical altercations.
- **Surveillance Camera Fight Dataset**: High-quality imagery for violent action detection.

### Safe/Neutral Data
- **ImageNet (Random subset)**: Use categories like "nature", "scenery", "animals", and "household objects" to teach the model what is safe.
- **COCO Dataset**: General objects in natural contexts.

## 2. Technical Approach

### Model Architecture
- **Backbone**: Use a pre-trained `MobileNetV2` or `EfficientNetV2B0`. These are lightweight and perfect for real-time monitoring.
- **Head**: Replace the top layer with a Global Average Pooling layer followed by a Dense layer with 4 outputs (Safe, Adult, Violence, Gore) using `softmax` activation.

### Implementation Snippet (TensorFlow)
```python
import tensorflow as tf
from tensorflow.keras import layers, models

base_model = tf.keras.applications.MobileNetV2(
    input_shape=(224, 224, 3), include_top=False, weights='imagenet'
)
base_model.trainable = False # Freeze backbone initially

model = models.Sequential([
    base_model,
    layers.GlobalAveragePooling2D(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.2),
    layers.Dense(4, activation='softmax') # 4 classes
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
```

## 3. Data Preprocessing
- **Resize**: 224x224 pixels.
- **Normalizing**: Scale pixel values to `[0, 1]` or `[-1, 1]`.
- **Augmentation**: Use random flips, rotations, and brightness/contrast adjustments to make the model more generalized.

## 4. Exporting the Model
Save your trained model as `moderation_model.h5` and place it in the `data/` directory. The `AIImageModerator` will automatically detect and load it.
