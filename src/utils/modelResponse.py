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
        return "Arriba Izquierda"
    elif prediction == 1:
        return "Arriba"
    elif prediction == 2:
        return "Arriba Derecha"
    elif prediction == 3:
        return "Izquierda"
    elif prediction == 4:
        return "Centro"
    elif prediction == 5:
        return "Derecha"
    elif prediction == 6:
        return "Abajo Izquierda"
    elif prediction == 7:
        return "Abajo"
    elif prediction == 8:
        return "Abajo Derecha"