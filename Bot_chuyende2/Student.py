class Student:
    def speak(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def name(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def address(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def telegram_id(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def ip(self):
        raise NotImplementedError("Subclass must implement abstract method")

    def stock(self, code):
        raise NotImplementedError("Subclass must implement abstract method")

