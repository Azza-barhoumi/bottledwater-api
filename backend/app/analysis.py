from .models import Brand
import pandas as pd
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering

def run_pca_clustering(n_clusters=7, features=None):
    if features is None:
        features = ["total_salts", "calcium", "magnesium", "bicarbonates", "sulfates"]
    
    # Fetch brands from database
    brands = Brand.query.order_by(Brand.id).all()
    data = []
    for b in brands:
        row = {'brand': b.name}
        for f in features:
            val = getattr(b, f, 0.0)
            row[f] = float(val) if val is not None else 0.0
        data.append(row)
    
    if not data:
        return {"error": "no brands in database"}
    
    # Create DataFrame
    df = pd.DataFrame(data)
    X = df[features].values
    
    # Standardize features
    scaler = StandardScaler()
    Xs = scaler.fit_transform(X)
    
    # Run PCA (2 components max)
    n_components = min(2, Xs.shape[1])
    pca = PCA(n_components=n_components)
    comps = pca.fit_transform(Xs)
    
    # Run clustering
    n_clusters = min(n_clusters, len(df))
    cl = AgglomerativeClustering(n_clusters=n_clusters)
    labels = cl.fit_predict(comps)
    
    # Prepare assignments
    assignments = []
    for i, name in enumerate(df['brand']):
        assignments.append({
            'brand': name,
            'cluster': int(labels[i]),
            'values': {f: float(df.iloc[i][f]) for f in features},
            'pc1': float(comps[i, 0]) if comps.shape[1] >= 1 else 0.0,
            'pc2': float(comps[i, 1]) if comps.shape[1] >= 2 else 0.0
        })
    
    return {
        'n_brands': len(df),
        'n_clusters': n_clusters,
        'features': features,
        'assignments': assignments,
        'pca_explained_variance_ratio': pca.explained_variance_ratio_.tolist()
    }
