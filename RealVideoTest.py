import cv2
import mediapipe as mp
import numpy as np
import os
from playsound import playsound
from keras.models import load_model

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

SENSIBILITY = 10
MODEL = load_model('./resources/models/resNet.h5')
SOUND_INPUT = './resources/sounds/'
mp_face_mesh = mp.solutions.face_mesh

LEFT_EYE = [362,382,381,380,374,390,249,263,466,388,387,386,385,384,398]
RIGHT_EYE = [33,7,163,144,145,153,154,155,133,173,157,158,159,160,161,246]
LEFT_IRIS = [474,475,476,477]
RIGHT_IRIS = [469,470,471,472]
MARGIN = 30

SECTORS = [
    [None, "J", None, "K", None, "I", None, "L", None],
    [None, "F", None, "G", None, "E", None, "H", None],
    [None, "B", None, "C", None, "A", None, "D", None],
    [None, None, None, " ", None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, "V", None, "W", None, "U", "Z", "X", "Y"],
    [None, "R", None, "S", None, "Q", None, "T", None],
    [None, "N", None, "O", None, "M", None, "P", None],
]

BUFFER = []

def getPredictedClass(predictions):
    y_pred_class = []

    for prediction in predictions:
        search = np.where(prediction == np.amax(prediction))[0]
        if not search.size:
            return None
        y_pred_class.append(search[0])
    
    return y_pred_class

def getCapturer():
    capture = False
    while(not capture):
        capture = cv2.VideoCapture(1)
        if not capture.isOpened():
            print("Cannot open camera")
            exit()

        ret, frame = capture.read()
        if not ret or np.sum(frame) == 0:
            print("Can't receive frame (stream end?). Retrying...")
            capture.release()

            capture = cv2.VideoCapture(0)
            capture.release()
            capture = False
    return capture

def processImage(faceMesh, image):
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = faceMesh.process(image)
    
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    imageHeight, imageWeight = image.shape[:2]
    if results.multi_face_landmarks:
        mesh_points = np.array([ np.multiply([p.x, p.y], [imageWeight, imageHeight]).astype(int) for p in results.multi_face_landmarks[0].landmark])

        firstPoint, secondPoint = findMarginOfEye(mesh_points[RIGHT_EYE])
        image = cropImageAround(image, firstPoint, secondPoint)
    
    return image

def cropImageAround(image, firstPoint, secondPoint):
    return image[firstPoint[1]:secondPoint[1], firstPoint[0]:secondPoint[0]]

def findMarginOfEye(innerMargin):
    innerMarginX = list(map(lambda margin: margin[0], innerMargin))
    innerMarginY = list(map(lambda margin: margin[1], innerMargin))

    innerMarginX.sort()
    innerMarginY.sort()

    firstPoint = (innerMarginX[0] - MARGIN, innerMarginY[0] - MARGIN)
    secondPoint = (innerMarginX[len(innerMarginX)-1] + MARGIN, innerMarginY[len(innerMarginY)-1] + MARGIN)
    horizontal = (secondPoint[0] - firstPoint[0])
    vertical = (secondPoint[1] - firstPoint[1])
    difference = int((horizontal-vertical)/2)

    return (firstPoint[0], firstPoint[1] - difference), (secondPoint[0], secondPoint[1] + difference)

def processImage(image, innerMargin):
    firstPoint, secondPoint = findMarginOfEye(innerMargin)
    image = cropImageAround(image, firstPoint, secondPoint)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, (75,75))
    resized = resized[np.newaxis,:,:]
    return resized/255

def customParseFromRealPhoto(image, mesh):
    image.flags.writeable = False
    image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = mesh.process(image)
    
    image.flags.writeable = True
    image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    imageHeight, imageWeight = image.shape[:2]
    
    if results.multi_face_landmarks:
        mesh_points = np.array([ np.multiply([p.x, p.y], [imageWeight, imageHeight]).astype(int) for p in results.multi_face_landmarks[0].landmark])
        rightEye = processImage(image, mesh_points[RIGHT_EYE])
        leftEye = processImage(image, mesh_points[LEFT_EYE])

        return [rightEye, leftEye]
    return None


def resolveSelection(previous, present):
    return SECTORS[previous][present]

def resolveMessage(message):
    if(len(BUFFER) >= 2):
        first = BUFFER.pop(0)
        second = BUFFER.pop(0)
        response = resolveSelection(first, second)
        if response != None:
            return message + response
    return message

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

if __name__ == '__main__':
    capturer = getCapturer()
    memory = -1
    counter = 0
    message = ""
    activeTracking = False
    with mp_face_mesh.FaceMesh(
        max_num_faces=1,
        refine_landmarks=True,
        min_detection_confidence = 0.5,
        min_tracking_confidence = 0.5) as face_mesh:
        while capturer.isOpened():
            success, full_image = capturer.read()
            if not success:
                print("Ignoring empty camera frame.")
                break

            processed_images = customParseFromRealPhoto(full_image, face_mesh)
            if processed_images is not None:
                rightArray = MODEL.predict(processed_images[0], verbose = 0)
                leftArray = MODEL.predict(processed_images[1], verbose = 0)
                averageArray = [(x + y)/2 for x, y in zip(rightArray, leftArray)]
                
                rightPrediction = getPredictedClass(rightArray)[0]
                leftPrediction = getPredictedClass(leftArray)[0]
                prediction = getPredictedClass(averageArray)[0]

                full_image = cv2.putText(full_image, "Prediccion derecho: " + fetchCharacter(rightPrediction), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 
                        2, (500, 0, 0), 2, cv2.LINE_AA)
                
                full_image = cv2.putText(full_image, "Prediccion izquierdo: " + fetchCharacter(leftPrediction), (100, 150), cv2.FONT_HERSHEY_SIMPLEX, 
                        2, (500, 0, 0), 2, cv2.LINE_AA)
                
                full_image = cv2.putText(full_image, "Prediccion promedio: " + fetchCharacter(prediction), (100, 200), cv2.FONT_HERSHEY_SIMPLEX, 
                        2, (500, 0, 0), 2, cv2.LINE_AA)
                
                if activeTracking:
                    if(memory != 4 and memory != prediction and counter > SENSIBILITY):
                        playsound(SOUND_INPUT + 'start.mp3', block = False)
                        BUFFER.append(memory)

                    imageHeight, imageWeight = full_image.shape[:2]
                    message = resolveMessage(message)
                    
                    bufferMessage = "Buffer: " + str(BUFFER) + "    memory: " + str(memory) + "    prediction: " + str(prediction) + "    counter: " + str(counter)
                    full_image = cv2.putText(full_image, bufferMessage, (50, imageHeight - 200), cv2.FONT_HERSHEY_SIMPLEX, 
                        1.2, (500, 0, 0), 2, cv2.LINE_AA)

                    
                    if(memory == prediction): 
                        counter += 1
                        if counter > 10 and memory != 4:
                            playsound(SOUND_INPUT + 'stop.mp3', block = False)
                    else: 
                        counter = 0
                        memory = prediction
                        
                    
                    full_image = cv2.putText(full_image, "Mensaje", (50, imageHeight - 150), cv2.FONT_HERSHEY_SIMPLEX, 
                        1.2, (255, 255, 255), 2, cv2.LINE_AA)
                    full_image = cv2.putText(full_image, "\"" + message + "\"", (50, imageHeight - 80), cv2.FONT_HERSHEY_SIMPLEX, 
                        2.5, (255, 255, 255), 2, cv2.LINE_AA)

            cv2.imshow('MediaPipe Face Mesh', full_image)

            key = cv2.waitKey(1) 
            if key == ord('q'):
                break
            if key == ord('s'):
                if activeTracking == False:
                    activeTracking = True
                else:
                    activeTracking = False
                    print(message)
                    memory = -1
                    counter = 0
                    message = ""
        capturer.release()