import numpy as np

class Sphere:
    def __init__(self, name, position, scale, colour, Ka, Kd, Ks, Kr, spec_exp):
        self.name = name
        self.position = position
        self.scale = scale
        self.colour = colour
        self.Ka = Ka
        self.Kd = Kd
        self.Ks = Ks
        self.Kr = Kr
        self.spec_exp = spec_exp
        self.inverse_transform = np.linalg.inv([
            [self.scale[0], 0, 0, position[0]],
            [0, self.scale[1], 0, position[1]],
            [0, 0, self.scale[2], position[2]],
            [0, 0, 0, 1]
        ]).tolist()

        self.inverse_transform_transpose = np.linalg.inv([
            [self.scale[0], 0, 0, position[0]],
            [0, self.scale[1], 0, position[1]],
            [0, 0, self.scale[2], position[2]],
            [0, 0, 0, 1]
        ]).T.tolist()

    def calculate_normal(self, intersection):
        return [intersection[0]-self.position[0], intersection[1]-self.position[1], intersection[2]-self.position[2]]

    def calculate_intersection(self, ray):
        # canonical sphere intersection equation
        a = np.dot(ray.direction, ray.direction)
        b = np.dot(ray.origin, ray.direction)
        c = np.dot(ray.origin, ray.origin) - 1.0
        
        discrim = b**2 - (a*c)

        if discrim >= 0:
            th1 = -b/a - np.sqrt(discrim)/a
            th = -b/a + np.sqrt(discrim)/a

            # get minimum hit time
            # check if th1 > 1 to handle spheres on img plane
            if not ray.reflected and th1 < th and th1 > 1:
                th = th1
            
            # if the ray is reflected check if hit time > 0.001 to avoid intersections with its own surface due to float errors
            if ray.reflected:
                if th1 < th:
                    th = th1
                if th > 0.001:
                    return th

            # if the ray is not reflected check if th > 1 to avoid drawing objects between the camera and near plane
            elif th > 1:
                return th

        return None