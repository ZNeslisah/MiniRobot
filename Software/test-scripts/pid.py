
class PID:

    def __init__(self, gains,  timeFunction) -> None:
        self.Kp, self.Ki, self.Kd = gains
        self.timeFunction = timeFunction


    @staticmethod
    def __limit(value, valueMax, valueMin):
        if valueMax and value > valueMax:
            return valueMax
        if valueMin and value < valueMin:
            return valueMin
        return value
    
    