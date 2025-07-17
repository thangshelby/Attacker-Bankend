import os
import pickle

def predict(data:list):
    model = None
    # Get the path to the model file relative to this script
    model_path = os.path.join(os.path.dirname(__file__), 'model.pkl')
    
    with open(model_path, 'rb') as f:
        model = pickle.load(f)

    # Make a prediction
    prediction = model.predict([data])
    
    return {"prediction": prediction.tolist()}
    