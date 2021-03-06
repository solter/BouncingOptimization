# BouncingOptimization
Program to shoot bouncing projectiles at a target.

This package solves the following problem:
Given a piecewise planar surface (defined by mesh of x,y,z points),
a tosser on the surface (at an x,y point), and a reciever (at an x,y point),
along with the number of bounces to take (N), find the angle the tosser must
launch the ball to hit the reciever.

This will be done via an optimization routine.

## Landscapes
Landscapes should use the following JSON format:
```
{
"verts":[],
"tri":[]
 }
```
Where each vertex has specifies [x,y,z], and
each triangle specifies [v1, v2, v3] where each vn is an index
to the vertices (0-indexed).
No two vertices should share a x and y, otherwise bad things happen.
