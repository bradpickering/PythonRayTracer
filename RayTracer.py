from utils.sphere import *
from utils.ray import *
from utils.light import *
import numpy as np
import sys

def normalize(vec):
    return (np.array(vec)/np.linalg.norm(vec)).tolist()


def multiply_matrices(vec1, vec2):
    return np.matmul(np.array(vec1), np.array(vec2)).tolist()


pixels = []
spheres = []
lights = []
inputs = {}
def main():
    parse_inputs()

    nCols = inputs["res"][0]
    nRows = inputs["res"][1]
    near = inputs["near"]
    left = inputs["left"]
    right = inputs["right"]
    bottom = inputs["bottom"]
    top = inputs["top"]

    W = (right - left) / 2.0
    H = (top - bottom) / 2.0

    eye = [0, 0, 0]
    f2 = open(inputs["output_file"], "w")
    f2.write("P3 " + str(nRows) + " " + str(nCols) + " 255\n")

    for i in range(0, nCols):
        # store each row of ppm values in pixel_row
        # append to it after each iteration of the rows
        pixel_row = []
        for j in range(0, nRows):
            # calculate the pixel coordinates of the row and column
            uc = -W +(W*(2*j)/nCols)
            vr = -H +(H*(2*i)/nRows)

            # set and normalize the ray direction to the pixel coordinates
            ray_dir = [uc, vr, -near]
            ray_dir = normalize(ray_dir)
            # origin is always 0 before reflecting
            ray = Ray(eye, ray_dir)

            # get the colour back from the raytrace value, this colour accounts for ambient, specular, diffuse and reflected colour
            colour = raytrace(ray)
            # transform to int and scale and clamp to 255 to conform to ppm P3 file standard
            pixel_colour = f"{min(255,int(colour[0]*255))} {min(255,int(colour[1]*255))} {min(255,int(colour[2]*255))}  "
            pixel_row.append(pixel_colour)

        # after each iteration through an entire row append the row to a 2D array of pixels
        pixels.append(pixel_row)

    
    # this loop handles writing to the output ppm
    # have to loop through the pixels backwards because ppm P3 expects the bottom left corner to be pixel (0,0)
    # when writing to the pixels we are assuming the top left pixel is (0,0)
    for i in pixels[::-1]:
        for j in i:
            f2.write(j)
        f2.write("\n")  


def raytrace(ray):
    # only do 3 recursion levels
    if ray.depth > 2:
        return [0, 0, 0]

    ray, th, sphere = find_intersection(ray)

    # if we hit a sphere with our ray, calculate the pixels colour
    if sphere is not None:
        colour = illumination(ray, th, sphere)
        return colour
    
    # if we did not hit a sphere and our ray is reflected return black
    elif ray.reflected:
        return [0, 0, 0]
    
    # else return the given background colour
    return inputs["back"]    


def find_intersection(ray):
    min_th = None
    intersected_sphere = None
    for sphere in spheres:
        # transform the input ray to intersect with the canonical sphere by multiplying the ray origin and direction by the sphere inverse transform

        ray_origin = np.array(ray.origin)
        ray_direction = np.array(ray.direction)

        ray_origin = np.append(ray_origin, 1)
        ray_direction = np.append(ray_direction, 0)

        ray_origin_transformed = multiply_matrices(sphere.inverse_transform, ray_origin)[:-1]
        ray_direction_transformed = multiply_matrices(sphere.inverse_transform, ray_direction)[:-1]

        ray_origin = ray_origin[:-1]
        ray_direction = ray_direction[:-1]
    
        ray_transform = Ray(ray_origin_transformed, ray_direction_transformed)
        
        # if the input ray was reflected, set the transformed ray to also be reflected, as reflected rays are handelled differently when finding hit times
        if ray.reflected:
            ray_transform.set_reflected()

        th = sphere.calculate_intersection(ray_transform)
        # find the closest intersected sphere
        if th is not None and min_th is None or (th is not None and th < min_th):
            ray.set_transformed_ray(ray_transform)
            min_th = th 
            intersected_sphere = sphere

    return ray, min_th, intersected_sphere  


def illumination(ray, th, sphere):
    intersection = ray.get_hit_point(th)

    # intersection point on the canonical sphere, used to calculate the normal
    intersection_tr = ray.transformed_ray.get_hit_point(th)
    
  
    ambient = inputs["ambient"]
    # ambient colour contribution
    colour = [ambient[0]*sphere.Ka*sphere.colour[0], ambient[1]*sphere.Ka*sphere.colour[1], ambient[2]*sphere.Ka*sphere.colour[2]]
    
    # calculate the normal by multiplying the intersection point by the inverse transpose transform matrix
    N = np.array(intersection_tr)
    N = np.append(N, 0)
    N = multiply_matrices(N, sphere.inverse_transform_transpose)
    N = N[:-1]
    N = normalize(N)

    for light in lights:

        # handles sphere on image plane with light behind it
        # only apply ambient light
        if sphere.position[2] == -inputs["near"] and sphere.position[:2] == light.position[:2] and light.position[2] < sphere.position[2]:
            continue

        # unit vector towards light
        L = np.array(light.position) - np.array(intersection).tolist()
        L = normalize(L)

        # shoot a shadow ray, if the shadow ray intersects with a sphere continue without calculating diffuse or specular
        shadow_ray = Ray(intersection, L)
        temp1, temp2, shadow_intersected_sphere = find_intersection(shadow_ray)
        if shadow_intersected_sphere is not None:
            continue

        V = normalize(np.array([0,0,0]) -np.array(intersection))
        R = 2*max(0,np.dot(N,L))*np.array(N) - np.array(L)
        R = normalize(R)

        # add the diffuse and specular colours
        for i in range(3):
            colour[i] += sphere.Kd*light.intensity[i]*max(0,np.dot(N,L))*sphere.colour[i]
            colour[i] += sphere.Ks*light.intensity[i]*(max(0, np.dot(R, V))**(sphere.spec_exp))

    # reflected ray, set origin at intersection point
    rf_origin = intersection
    rf_direction = -2*np.dot(N, ray.direction)*np.array(N) + np.array(ray.direction)
    rf_direction = normalize(rf_direction)
    rf_ray = Ray(rf_origin, rf_direction)
    rf_ray.set_reflected()
    rf_ray.depth = ray.depth
    rf_ray.increase_depth()
    rf_colour = raytrace(rf_ray)
    
    # add the reflected colour to the colour 
    for i in range(3):
        colour[i] += rf_colour[i]*sphere.Kr

    # clamp colour values to a max of 1
    for i in range(3):
        colour[i] = min(1, colour[i])

    return colour


def parse_inputs():
    input_file = sys.argv[1]
    input_file = open(input_file, 'r')
    lines = input_file.readlines()

    # puts spheres and lights into a list of sphere and light objects respectively
    # everything else is put into a dictionary to be used later
    for line in lines:
        # handles malformed input files
        if not line.strip():
            continue

        if line.split()[0] in ['NEAR', 'LEFT', 'RIGHT', 'BOTTOM', 'TOP']:
            inputs[line.split()[0].lower()] = float(line.split()[1])
        
        if line.split()[0] == "RES":
            inputs[line.split()[0].lower()] = [ int(i) for i in line.split()[1::]]

        if line.split()[0] == "SPHERE":
            sphere_params = line.split()
            name = sphere_params[1]
            position = [float(sphere_params[2]), float(sphere_params[3]), float(sphere_params[4])]
            scale = [float(sphere_params[5]), float(sphere_params[6]), float(sphere_params[7])]
            colour = [float(sphere_params[8]), float(sphere_params[9]), float(sphere_params[10])]
            Ka = float(sphere_params[11])
            Kd = float(sphere_params[12])
            Ks = float(sphere_params[13])
            Kr = float(sphere_params[14])
            spec_exponent = float(sphere_params[15])

            spheres.append(Sphere(name, position, scale, colour, Ka, Kd, Ks, Kr, spec_exponent))

        if line.split()[0] == "LIGHT":
            light_params = line.split()
            name = light_params[1]
            position = [float(light_params[2]), float(light_params[3]), float(light_params[4])]
            intensity = [float(light_params[5]), float(light_params[6]), float(light_params[7])]

            lights.append(Light(name, position, intensity))
    
        if line.split()[0] in ["BACK", "AMBIENT"]:
             inputs[line.split()[0].lower()] = [ float(i) for i in line.split()[1::]]

        if line.split()[0] == "OUTPUT":
            inputs["output_file"] = line.split()[1]

    
if __name__ == "__main__":
    main()