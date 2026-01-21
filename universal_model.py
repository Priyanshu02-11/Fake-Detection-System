from transformers import pipeline
import torch

class UniversalDetector:
    def __init__(self, device_id):
        print(f"Loading Universal AI Detector on {'GPU' if device_id == 0 else 'CPU'}...")
        
        self.pipe = pipeline(
            "image-classification", 
            model="umm-maybe/AI-image-detector", 
            device=device_id
        )

    def predict(self, image):
        results = self.pipe(image)
                
        ai_score = 0.0
        for r in results:
            if r['label'].lower() in ['artificial', 'ai', 'fake', 'cg', 'generated']:
                ai_score = r['score']
                
        return ai_score

def get_universal_detector(device_id):
    return UniversalDetector(device_id)