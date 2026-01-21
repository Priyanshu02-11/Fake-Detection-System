import os
import cv2
import torch
from flask import Flask, render_template, request, redirect
from PIL import Image
from universal_model import get_universal_detector

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['MAX_CONTENT_LENGTH'] = 64 * 1024 * 1024

device_id = 0 if torch.cuda.is_available() else -1
detector = get_universal_detector(device_id)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp', 'mp4', 'avi', 'mov'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def process_video(filepath):
    cap = cv2.VideoCapture(filepath)
    scores = []
    frame_count = 0
    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    skip = max(1, total_frames // 10)
    while True:
        ret, frame = cap.read()
        if not ret: break
        
        if frame_count % skip == 0:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame)
            score = detector.predict(pil_img)
            scores.append(score)
            
        frame_count += 1
    
    cap.release()
    return sum(scores) / len(scores) if scores else 0.0

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files: return redirect(request.url)
        file = request.files['file']
        if file.filename == '' or not allowed_file(file.filename): return redirect(request.url)

        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)
            
            try:
                ext = file.filename.rsplit('.', 1)[1].lower()
                
                if ext in {'mp4', 'avi', 'mov'}:
                    ai_prob = process_video(filepath)
                else:
                    img = Image.open(filepath).convert('RGB')
                    ai_prob = detector.predict(img)

                ai_percent = round(ai_prob * 100, 2)
                
                if ai_percent > 30:
                    label = "AI GENERATED"
                    category = "artificial"
                elif ai_percent < 15:
                    label = "REAL / HUMAN"
                    category = "real"
                else:
                    label = "UNCERTAIN"
                    category = "uncertain"

                return render_template('index.html', 
                                       label=label, 
                                       percent=ai_percent, 
                                       category=category,
                                       filename=file.filename)
                                       
            except Exception as e:
                return f"Error: {e}"

    return render_template('index.html', label=None)

if __name__ == '__main__':
    app.run(debug=True)