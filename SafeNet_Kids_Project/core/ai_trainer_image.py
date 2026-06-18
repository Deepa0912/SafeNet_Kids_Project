import os
import tensorflow as tf
from tensorflow.keras import layers, models, optimizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator

def build_model(num_classes=4):
    """ Builds a multi-class image moderation model using MobileNetV2 as a backbone. """
    base_model = tf.keras.applications.MobileNetV2(
        input_shape=(224, 224, 3), include_top=False, weights='imagenet'
    )
    base_model.trainable = False  # Freeze the backbone initially

    model = models.Sequential([
        base_model,
        layers.GlobalAveragePooling2D(),
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.2),
        layers.Dense(num_classes, activation='softmax')
    ])

    return model

def train_image_moderator(data_dir, epochs=10, batch_size=32):
    """
    Trains the moderation model on a dataset organized in subfolders by class.
    Expected structure:
    data_dir/
        Safe/
        Adult/
        Violence/
        Gore/
    """
    if not os.path.exists(data_dir):
        print(f"Error: Dataset directory {data_dir} not found.")
        return

    # Data Augmentation
    datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        width_shift_range=0.2,
        height_shift_range=0.2,
        horizontal_flip=True,
        validation_split=0.2
    )

    train_generator = datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        subset='training'
    )

    val_generator = datagen.flow_from_directory(
        data_dir,
        target_size=(224, 224),
        batch_size=batch_size,
        class_mode='categorical',
        subset='validation'
    )

    num_classes = train_generator.num_classes
    model = build_model(num_classes)
    
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=['accuracy']
    )

    print(f"Starting training for {epochs} epochs...")
    model.fit(
        train_generator,
        validation_data=val_generator,
        epochs=epochs
    )

    # Save the model
    os.makedirs("data", exist_ok=True)
    save_path = "data/moderation_model.h5"
    model.save(save_path)
    print(f"Success: Model saved to {save_path}")

if __name__ == "__main__":
    # Example usage:
    # train_image_moderator("data/training_images")
    print("AI Image Trainer: Ready. Place your dataset in subfolders and call train_image_moderator().")
