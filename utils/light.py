class Light:
    def __init__(self, name, position, intensity):
        self.name = name
        self.position = position
        self.intensity =  intensity

    def calculate_light_direction(self, intersection):
        return [self.position[0] - intersection[0], self.position[1] - intersection[1], self.position[2] - intersection[2]]
    