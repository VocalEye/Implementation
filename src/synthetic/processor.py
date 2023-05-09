import cv2
import numpy as np
import os
from ..utils.camera import getCapturer
from ..utils.modelResponse import getPredictedClass, fetchCharacter
from ..writing.writing import MessageWritter

def CustomParser(image):
    center = image.shape
    x = center[1]/2 - center[0]/2
    y = center[0]/2 - center[0]/2

    crop_img = image[int(y):int(y+center[0]), int(x):int(x+center[0])]
    gray = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

    resized = cv2.resize(gray, (75,75))
    resized = resized[np.newaxis,:,:]

    return resized/255

def processSyntheticInput(input, model):
    capturer = getCapturer(input)
    messageWritter = MessageWritter(10)
    while capturer.isOpened():
        success, full_image = capturer.read()
        if not success:
            print("Ignoring empty camera frame.")
            break

        test = CustomParser(full_image)
        
        prediction = getPredictedClass(model.predict(test, verbose = 0))[0]
        messageWritter.processPrediction(prediction)

        imageHeight, imageWeight = full_image.shape[:2]

        full_image = cv2.putText(full_image, "Prediccion: " + fetchCharacter(prediction), (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 
                   1.2, (0, 0, 0), 2, cv2.LINE_AA)
        
        full_image = cv2.putText(full_image, "Mensaje", (50, imageHeight - 150), cv2.FONT_HERSHEY_SIMPLEX, 
                    1.2, (0, 0, 0), 2, cv2.LINE_AA)
        full_image = cv2.putText(full_image, "\"" + messageWritter.getMessage() + "\"", (50, imageHeight - 80), cv2.FONT_HERSHEY_SIMPLEX, 
                    1.2, (0, 0, 0), 2, cv2.LINE_AA)

        cv2.imshow('Prueba de simulacion', full_image)

        key = cv2.waitKey(1) 
        if key == ord('q'):
            break
        if key == ord('s'):
            os.system("pause")
    capturer.release()