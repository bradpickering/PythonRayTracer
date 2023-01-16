class Ray:
    def __init__(self, origin, direction, transformed_ray=None, depth=0, reflected=False, on_near=False):
        self.origin = origin
        self.direction = direction
        self.transformed_ray = transformed_ray
        self.depth = depth
        self.reflected = reflected
        self.on_near = on_near

    def get_origin(self):
        return self.origin

    def get_direction(self):
        return self.direction

    def set_transformed_ray(self, transformed_ray):
        self.transformed_ray = transformed_ray

    def increase_depth(self):
        self.depth += 1
    
    def set_reflected(self):
        self.reflected = True

    def set_on_near(self):
        self.on_near = True

    def get_hit_point(self, t):
        return [self.origin[0] + t*self.direction[0], self.origin[1] + t*self.direction[1], self.origin[2] + t*self.direction[2]]
