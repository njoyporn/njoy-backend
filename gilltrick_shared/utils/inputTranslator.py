from backend_shared.logger import colors

class InputTranslator:
    def __init__(self):
        pass
    
    class ColorTranslator:
        def __init__(self):
            self.colors = colors.Colors()

        def is_green(self, input):
            input = str(input).lower()
            if    (input == "green"
                or input == "ok"
                or input == "grün"
                or input == "positive"):
                return True
            return False 
        
        def is_red(self, input):
            input = str(input).lower()
            if    (input == "red"
                or input == "bad"
                or input == "false"
                or input == "negative"
                or input == "failure"
                or input == "error"
                or input == "fatal"):
                return True
            return False 
        
        def is_orange(self, input):
            input = str(input).lower()
            if    (input == "orange"
                or input == "warning"):
                return True
            return False 
        
        def is_blue(self, input):
            input = str(input).lower()
            if    (input == "blue"
                or input == "info"
                or input == "blau"):
                return True
            return False 
        
        def is_end(self, input):
            input = str(input).lower()
            if    (input == "end"
                or input == "endc"
                or input == "reset"
                or input == "resett"):
                return True
            return False 

        def translate(self, input):
            if self.is_end(input): return self.colors.ENDC
            if self.is_green(input): return self.colors.OKGREEN
            if self.is_red(input): return self.colors.FAIL
            if self.is_orange(input): return self.colors.WARNING
            if self.is_blue(input): return self.colors.OKBLUE
            else: return self.colors.WHITE