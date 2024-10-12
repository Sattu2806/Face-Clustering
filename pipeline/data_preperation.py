import face_recognition
import cv2
import numpy as np
from pymongo import MongoClient
from bson.binary import Binary
from bson import ObjectId

# MongoDB connection
client = MongoClient("mongodb+srv://Lokesh:lokesh.1015@faceclustering.0vmes.mongodb.net/FaceClustering?retryWrites=true&w=majority")
db = client["FaceClustering"]
collection = db["uploads"]

def load_and_encode_images(image_ids, detection_method="hog", min_face_size=20):
    data = []

    for (i, image_id) in enumerate(image_ids):
        # print(f"[INFO] Processing image {i + 1}/{len(image_ids)}")
        # Fetch image from MongoDB
        image_doc = collection.find_one({'_id': ObjectId(image_id)})
        
        if image_doc is None:
            print(f"[ERROR] Image ID {image_id} not found in database.")
            continue

        image_data = image_doc["image_data"]  # Binary image data
        image_array = np.frombuffer(image_data, dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # Resizing images to constant width x height
        h, w = image.shape[:2]
        width = 500
        ratio = width/float(w)
        height = int(h*ratio)
        image = cv2.resize(image, (width, height))

        if image is None:
            print(f"[ERROR] Failed to decode image ID {image_id}.")
            continue

        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

        # Detect faces in the image
        boxes = face_recognition.face_locations(rgb, model=detection_method)
        valid_boxes = []

        # Filter faces based on size
        for (top, right, bottom, left) in boxes:
            face_width = right - left
            face_height = bottom - top

            # Print face dimensions for debugging
            # print(f"[DEBUG] Face dimensions (width x height): {face_width} x {face_height}")

            if face_width >= min_face_size and face_height >= min_face_size:
                valid_boxes.append((top, right, bottom, left))
        
        # Encode the valid faces
        encodings = face_recognition.face_encodings(rgb, valid_boxes)

        d = [{"imageId": image_id, "loc": box, "encoding": enc, "session_id": image_doc.get('session_id')}
             for (box, enc) in zip(valid_boxes, encodings)]
        data.extend(d)

    return data
