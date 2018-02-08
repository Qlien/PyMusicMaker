
class SerializationBase:
    def __init__(self):
        pass

    def get_serialization_data(self):
        raise NotImplementedError

    def set_serialization_data(self):
        raise NotImplementedError
