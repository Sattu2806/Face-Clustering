from sklearn.decomposition import PCA
import numpy as np

def calculate_explained_variance(encodings):
    n_components_values = list(range(1, min(len(encodings[0]), len(encodings)) + 1))
    explained_variances = []

    for n_component in n_components_values:
        pca = PCA(n_components=n_component)
        pca.fit(encodings)
        explained_variances.append(np.sum(pca.explained_variance_ratio_))
    
    return n_components_values, explained_variances

def determine_optimal_components(explained_variances, threshold=0.86):
    for i, variance in enumerate(explained_variances):
        if variance >= threshold:
            return i + 1  # Since components start at 1, not 0
    return len(explained_variances)  # Return the max if the threshold is not reached

def apply_pca(encodings, n_components):
    # Initialize PCA with the optimal number of components
    pca = PCA(n_components=n_components)
    # Fit and transform the encodings
    reduced_data = pca.fit_transform(encodings)
    
    return reduced_data
