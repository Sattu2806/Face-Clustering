import os
import cv2
import shutil

def save_distinct_faces(data, labels, labelIDs, output_base_path):
    """
    Save one cropped image of each distinct face to the 'DistinctFace' directory.

    Args:
    - data (list of dict): The data containing image paths, face locations, and encodings.
    - labels (np.array): The labels assigned to each face by the clustering algorithm.
    - labelIDs (np.array): The unique label IDs from the clustering algorithm.
    - output_base_path (str): The base directory where distinct face images will be saved.
    """
    # Create the 'DistinctFace' directory if it doesn't exist
    distinct_faces_dir = os.path.join(output_base_path, "DistinctFace")
    if not os.path.exists(distinct_faces_dir):
        os.makedirs(distinct_faces_dir)

    # Dictionary to track if we've already saved a cropped face for each label
    distinct_face_saved = {}

    # Loop over the unique face labels
    for labelID in labelIDs:
        if labelID not in distinct_face_saved:
            # Get one index for the current label
            idx = next(i for i, label in enumerate(labels) if label == labelID)
            imagePath = data[idx]["imagePath"]
            image = cv2.imread(imagePath)
            (top, right, bottom, left) = data[idx]["loc"]
            cropped_face = image[top:bottom, left:right]
            face_path = os.path.join(distinct_faces_dir, f"Face_{labelID}.jpg")
            cv2.imwrite(face_path, cropped_face)
            distinct_face_saved[labelID] = True

def save_clustered_faces(data, labels, labelIDs, output_base_path):
    """
    Save original images to directories corresponding to each face label.

    Args:
    - data (list of dict): The data containing image paths, face locations, and encodings.
    - labels (np.array): The labels assigned to each face by the clustering algorithm.
    - labelIDs (np.array): The unique label IDs from the clustering algorithm.
    - output_base_path (str): The base directory where clustered images will be saved.
    """
    # Ensure the output base directory exists
    if not os.path.exists(output_base_path):
        os.makedirs(output_base_path)

    # Loop over the unique face labels
    for labelID in labelIDs:
        if labelID==-1:
            continue
        else:
            label_dir = os.path.join(output_base_path, f"Face_{labelID}")
            if not os.path.exists(label_dir):
                os.makedirs(label_dir)

            # Get all indices for the current label
            idxs = [i for i, label in enumerate(labels) if label == labelID]

            for i in idxs:
                imagePath = data[i]["imagePath"]
                # Copy the original image to the corresponding face directory
                shutil.copy(imagePath, label_dir)
