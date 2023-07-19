
import cv2
import mediapipe as mp
import numpy as np
from src.utils.camera import getCapturer
from src.utils.modelResponse import fetchCharacter, getPredictedClass
from src.writing.writing import MessageWritter

mp_face_mesh = mp.solutions.face_mesh

LEFT_EYE = [362,382,381,380,374,390,249,263,466,388,387,386,385,384,398]
RIGHT_EYE = [33,7,163,144,145,153,154,155,133,173,157,158,159,160,161,246]
LEFT_IRIS = [474,475,476,477]
RIGHT_IRIS = [469,470,471,472]
MARGIN = 30

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

def processRealInput(input, model):
    capturer = getCapturer(input)
    activeTracking = False
    messageWritter = MessageWritter(10, True)
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
                rightArray = model.predict(processed_images[0], verbose = 0)
                leftArray = model.predict(processed_images[1], verbose = 0)
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
                    imageHeight, imageWeight = full_image.shape[:2]
                    messageWritter.processPrediction(prediction)
                    print(messageWritter.getStatistics(), "message:", messageWritter.getMessage())
                    full_image = cv2.putText(full_image, messageWritter.getStatistics(), (50, imageHeight - 200), cv2.FONT_HERSHEY_SIMPLEX, 
                        1.2, (500, 0, 0), 2, cv2.LINE_AA)
                    full_image = cv2.putText(full_image, "Mensaje", (50, imageHeight - 150), cv2.FONT_HERSHEY_SIMPLEX, 
                        1.2, (255, 255, 255), 2, cv2.LINE_AA)
                    full_image = cv2.putText(full_image, "\"" + messageWritter.getMessage() + "\"", (50, imageHeight - 80), cv2.FONT_HERSHEY_SIMPLEX, 
                        2.5, (0, 0, 0), 2, cv2.LINE_AA)

            cv2.imshow('MediaPipe Face Mesh', full_image)

            key = cv2.waitKey(1) 
            if key == ord('q'):
                break
            if key == ord('s'):
                if activeTracking == False:
                    activeTracking = True
                    messageWritter = MessageWritter(10, True)
                else:
                    activeTracking = False
                    messageWritter = None
        capturer.release()