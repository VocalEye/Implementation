import numpy as np

def getPredictedClass(predictions):
    y_pred_class = []

    for prediction in predictions:
        search = np.where(prediction == np.amax(prediction))[0]
        if not search.size:
            return None
        y_pred_class.append(search[0])
    
    return y_pred_class

def fetchCharacter(prediction):
    if prediction == 0:
        return "Up left"
    elif prediction == 1:
        return "Up"
    elif prediction == 2:
        return "Up right"
    elif prediction == 3:
        return "Left"
    elif prediction == 4:
        return "Center"
    elif prediction == 5:
        return "Right"
    elif prediction == 6:
        return "Down left"
    elif prediction == 7:
        return "Down"
    elif prediction == 8:
        return "Down right"