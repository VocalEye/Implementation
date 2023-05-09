SECTORS = [
    [None, "J", None, "K", None, "I", None, "L", None],
    [None, "F", None, "G", None, "E", None, "H", None],
    [None, "B", None, "C", None, "A", None, "D", None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, " ", None, None, None],
    [None, "V", None, "W", None, "U", "Z", "X", "Y"],
    [None, "R", None, "S", None, "Q", None, "T", None],
    [None, "N", None, "O", None, "M", None, "P", None],
]

class MessageWritter:
    buffer = []
    message = ""
    sensibility = 10
    counter = 0
    memory = -1

    def __init__(self, sensibility):
        self.sensibility = sensibility

    def resolveSelection(self, previous, present):
        return SECTORS[previous][present]

    def resolveMessage(self):
        if(len(self.buffer) >= 2):
            first = self.buffer.pop(0)
            second = self.buffer.pop(0)
            response = self.resolveSelection(first, second)
            if response != None:
                self.message = self.message + response

    def fetchCharacter(self, prediction):
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
    
    def getMessage(self):
        return self.message
    
    def processPrediction(self, prediction):
        if(self.memory != 4 and self.memory != prediction and self.counter > self.sensibility):
            self.buffer.append(self.memory)

        self.resolveMessage()
        
        if(self.memory == prediction): self.counter += 1
        else:
            self.counter = 0
            self.memory = prediction