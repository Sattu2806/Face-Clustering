from flask import Flask, render_template, request, redirect, url_for, send_file, jsonify, session
from io import BytesIO
import datetime
import bson
from bson import ObjectId
from config import init_mongo
import uuid
from dotenv import load_dotenv
import os

app = Flask(__name__)

# Configuration
app.config['MONGO_URI'] = os.getenv('MONGO_URI') 
mongo = init_mongo(app)  # Initialize mongo here

app.secret_key = 'lokesh.1015'

# Utility functions
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

def create_zip_from_database(cluster_label):
    """Create a zip file for a given cluster from the database."""
    session_id = session['session_id']
    clusters_collection = mongo.db.clusters
    cluster = clusters_collection.find_one({'cluster_label': cluster_label, 'session_id': session_id})
    
    if cluster:
        zip_data = cluster['zip_data']
        return BytesIO(zip_data)
    return None

# Routes
@app.route('/')
def root():
    return redirect(url_for('index'))

@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/home', methods=['GET', 'POST'])
def home():
    if 'session_id' not in session:
        session['session_id'] = str(uuid.uuid4())  # Create a new session_id if not present
    
    if request.method == 'POST':
        if 'upload' in request.form:
            if 'files[]' not in request.files:
                return redirect(request.url)
            files = request.files.getlist('files[]')
            for file in files:
                if file and allowed_file(file.filename):
                    filename = file.filename
                    content_type = file.content_type
                    image_data = file.read()
                    mongo.db.uploads.insert_one({
                        'filename': filename,
                        'content_type': content_type,
                        'upload_date': datetime.datetime.utcnow(),
                        'image_data': image_data,
                        'session_id': session['session_id']  # Associate the image with the session
                    })
            return redirect(url_for('home'))
        elif 'proceed' in request.form:
            return redirect(url_for('process_and_redirect'))
    return render_template('home.html')

@app.route('/process_and_redirect', methods=['POST'])
def process_and_redirect():
    if 'session_id' not in session:
        return "Session ID not found", 400

    uploads_collection = mongo.db.uploads
    images = list(uploads_collection.find({'session_id': session['session_id']}))

    image_ids = [str(image['_id']) for image in images]  # Convert ObjectId to string for processing

    print(f"[INFO] Image IDs: {image_ids}")

    from pipeline.main import run_clustering_pipeline
    run_clustering_pipeline(image_ids)  # Pass session_id to the clustering pipeline
    return jsonify({'redirect': url_for('results')})

@app.route('/results')
def results():
    if 'session_id' not in session:
        return "Session ID not found", 400

    session_id = session['session_id']
    clusters_collection = mongo.db.clusters
    
    # Fetch clusters only for the current session
    cluster_data = list(clusters_collection.find({'session_id': session_id}))

    face_data = []
    for cluster in cluster_data:
        images = cluster.get('images', [])
        image_docs = []
        for img_id in images:
            img_doc = mongo.db.uploads.find_one({'_id': ObjectId(img_id)})
            if img_doc:
                image_docs.append({
                    'id': str(img_doc['_id']),
                    'filename': img_doc['filename'],
                    'content_type': img_doc['content_type']
                })
        face_data.append({
            'label': cluster['cluster_label'],
            'images': image_docs
        })

    return render_template('results.html', faces=face_data)

@app.route('/image/<image_id>')
def get_image(image_id):
    uploads_collection = mongo.db.uploads
    try:
        image_id = bson.ObjectId(image_id)  # Convert to ObjectId for MongoDB query
        image_doc = uploads_collection.find_one({'_id': image_id})
        
        if image_doc:
            return send_file(
                BytesIO(image_doc['image_data']),
                mimetype=image_doc['content_type'],
                as_attachment=False,
                download_name=image_doc['filename']
            )
    except Exception as e:
        print(f"Error retrieving image: {e}")
    return "Image not found", 404

@app.route('/download/<cluster_label>')
def download(cluster_label):
    zip_buffer = create_zip_from_database(cluster_label)
    if zip_buffer:
        return send_file(zip_buffer, as_attachment=True, download_name=f"{cluster_label}.zip", mimetype='application/zip')
    return "No such cluster found", 404

@app.route('/get_images/<cluster_label>')
def get_images(cluster_label):
    clusters_collection = mongo.db.clusters
    session_id = session['session_id']
    cluster = clusters_collection.find_one({'cluster_label': cluster_label, 'session_id': session_id})
    
    if cluster:
        image_ids = cluster.get('images', [])
        uploads_collection = mongo.db.uploads
        images = [{'id': str(img_id), 'filename': uploads_collection.find_one({'_id': ObjectId(img_id)})['filename']} for img_id in image_ids]
        return jsonify({'images': images})
    return jsonify({'images': []})

@app.route('/clear_database', methods=['POST'])
def clear_database():
    session_id = session.pop('session_id', None)
    if session_id:
        mongo.db.uploads.delete_many({'session_id': session_id})
        mongo.db.clusters.delete_many({'session_id': session_id})
    return redirect(url_for('index'))

# if __name__ == '__main__':
#     app.run(debug=True)
