from sklearn.cluster import DBSCAN
import numpy as np

def cluster_faces(encodings, eps=0.33, min_samples=1):
    clt = DBSCAN(eps=eps, min_samples=min_samples, metric="euclidean", n_jobs=-1)
    clt.fit(encodings)
    
    labelIDs = np.unique(clt.labels_)
    numUniqueFaces = len(np.where(labelIDs > -1)[0])
    # print("[INFO] Number of unique faces: {}".format(numUniqueFaces))
    
    return clt.labels_, labelIDs
