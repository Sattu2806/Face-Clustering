import pipeline.data_preperation
import pipeline.face_clustering
import pipeline.pca_analysis
# import pipeline.plotting
from flask_pymongo import PyMongo
from io import BytesIO
import zipfile
import datetime
from bson import ObjectId
from app import mongo  # Import mongo from app
import io

def run_clustering_pipeline(image_ids):
    detection_method = "hog"
    min_face_size = 20

    # print("[INFO] Loading and encoding images...")
    data = pipeline.data_preperation.load_and_encode_images(image_ids, detection_method, min_face_size)

    encodings = [d["encoding"] for d in data]
    # print(f"[DEBUG] Encodings length: {len(encodings)}")  # Debugging line

    if len(encodings) == 0:
        print("[ERROR] No encodings found. Exiting pipeline.")
        return  # Exit if no encodings are found

    # print("[INFO] Calculating explained variance...")
    n_components_values, explained_variances = pipeline.pca_analysis.calculate_explained_variance(encodings)

    optimal_components = pipeline.pca_analysis.determine_optimal_components(explained_variances, threshold=0.86)
    # print(f"[INFO] Optimal number of components for PCA: {optimal_components}")

    # print("[INFO] Applying PCA reduction...")
    reduced_data = pipeline.pca_analysis.apply_pca(encodings, n_components=optimal_components)

    labels, labelIDs = pipeline.face_clustering.cluster_faces(reduced_data)

    clusters_collection = mongo.db.clusters

    for label in labelIDs:
        # print(f"[INFO] Saving cluster for label: {label}")
        cluster_images = []
        zip_buffer = io.BytesIO()

        # Filter encodings by label
        label_encodings = [d for (d, l) in zip(data, labels) if l == label]

        if len(label_encodings) == 0:
            continue

        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for entry in label_encodings:
                image_doc = mongo.db.uploads.find_one({'_id': ObjectId(entry['imageId'])})
                if image_doc:
                    image_data = image_doc['image_data']
                    image_filename = image_doc['filename']
                    cluster_images.append(image_doc['_id'])

                    zip_file.writestr(image_filename, image_data)

        # Save zip file to database
        clusters_collection.insert_one({
            'cluster_label': f'cluster_{int(label)+1}',
            'images': cluster_images,
            'zip_data': zip_buffer.getvalue(),
            'session_id': label_encodings[0].get('session_id', None)  # Default to None if session_id is missing
        })

    # print("[INFO] Clustering pipeline complete.")
