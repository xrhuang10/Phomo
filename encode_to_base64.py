import base64

def encode_image_to_base64(image_path):
    with open(image_path, "rb") as img_file:
        encoded_string = base64.b64encode(img_file.read()).decode("utf-8")
        return encoded_string

if __name__ == "__main__":
    path = "sample.jpg"  # change this to your image file name
    b64 = encode_image_to_base64(path)
    print("\n📸 Base64-encoded image:\n")
    print(b64)
