# PythonRayTracer
[Backwards RayTracer](https://cs.stanford.edu/people/eroberts/courses/soco/projects/1997-98/ray-tracing/types.html#Backward%20Ray%20Tracing) written in Python. Outputs results in a ppm file.

## Example output
![exampleTest](https://user-images.githubusercontent.com/64803010/212615328-7ec9e4d8-e798-4093-a8f2-6202fe69c55f.png)

## Input file format
### example given in [exampleTest.txt](https://github.com/bradpickering/PythonRayTracer/blob/main/exampleTest.txt)

NEAR \<n>

LEFT \<l>

RIGHT \<r>

BOTTOM \<b>

TOP \<t>

RES \<x> \<y>

SPHERE \<name> \<pos x> \<pos y> \<pos z> \<scl x> \<scl y> \<scl z> \<r> \<g> \<b> \<Ka> \<Kd> \<Ks> \<Kr> \<n>

… // additional sphere specifications

LIGHT \<name> \<pos x> \<pos y> \<pos z> \<Ir> \<Ig> \<Ib>

… // additional light specifications

BACK \<r> \<g > \<b>

AMBIENT \<Ir> \<Ig> \<Ib>

OUTPUT \<name>
  
## How to run
````
python3 RayTracer.py <inputfile.txt>
````
 
