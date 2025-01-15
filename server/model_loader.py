import tensorflow as tf

def load_model():
    """Load the pre-trained TensorFlow model."""
    model_path = "server\cnn_model.keras"
    try:
        model = tf.keras.models.load_model(model_path)
        print(f"[INFO] Model loaded successfully from {model_path}.")
        return model
    except Exception as e:
        print(f"[ERROR] Failed to load model: {e}")
        raise

if __name__ == "__main__":
    # Test model loading
    model = load_model()
    print("[INFO] Model is ready for predictions.")
