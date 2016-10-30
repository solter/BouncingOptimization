import json
import numpy as np

class landscape():
    """
    Landscape class to hold the ground specification.

    self.x - array of x values
    self.y - array of y values
    self.grid - z value of the landscape, such that
        self.grid[i,j] is at self.x[i] and self.y[j]
    """
    @classmethod 
    def load(cls, fname)
        """
        Generate a new landscape instance via loading
        in a landscape from a JSON file with the following format:
        ```
        {
            "verts":[[x,y,z],
                     [x,y,z],
                     ...],
            "tri":[[v1, v2, v3],
                   [v1, v2, v3]
                   ...]
        }
        ```
        Where x, y, z are floats,
        v1, v2, and v3 are the indices for the triangles.
        Note that this does NOT do 3-D shapes, just a 2-D surface.
        """
        with open(fname, 'r') as f:
            data = json.load(f)
        return cls(data['verts'], data['tri'])

    def __init__(self, verts, tris, grid):
        self.verts = np.array(verts)
        if self.verts.shape[1] != 3:
            raise LandscapeException('All vertices must contain 3 values for x,y,z')

        self.tri2vert = np.array(tris)
        if self.tri2vert.shape[1] != 3:
            raise LandscapeException('All triangles must contain 3 vertex indices')
        self._funcs   = [None]*len(self.tri2vert)
        self._normals = [None]*len(self.tri2vert)

        # Build the reverse list
        self.vert2tri = [[] for i in range(len(self.verts))]
        for tri_idx, val in enumerate(self.tri2vert):
            for vidx in val:
                self.vert2tri[vidx].append(tri_idx)
            

    def valueAndNormal(self, x, y):
        """
        Get the Grid value and normal at (x,y)

        Parameters
        ----------
        x : float
            x location
        y : float
            y location

        Result
        -------
        z : float
            Height at the x,y position
        norm : array-like
            normal to the surface at x,y

        Notes
        ------
        If the point is on an edge or vertex, the normal is the average
        of the surrounding normals.
        """
        # Find the closest point
        pt = np.array([x,y])

        # Calculate the norms of the difference between all the x,y points
        dist = self.verts[:,:2] - pt
        dist = dist**2
        dist = dist.sum(axis=1)

        closest_vidx = np.argmin(dist)

        val = None
        normal = []
        # For all triangles it can be part of
        for tri_idx in self.vert2tri[closest_vidx]:
            if self._inTri(pt, tri_idx):
                f, n = self._getPlane(tri_idx)
                if val is None:
                    val = f(pt)
                elif val != f(pt):
                    # This should never happen
                    raise LandscapeException('Edge of triangles disagree on value')
                normal.append(n)

        if val is None:
            raise LandscapeException("Point outside of grid")

        normal = np.array(normal)
        normal = normal.mean(axis=0)

        return val, normal

    def _inTri(pt, tri_idx):
        """
        Determine if a point is within a triangle

        Paramters
        ---------
        pt : array-like
            (x,y) point
        tri_idx : integer
            index of triangle

        Results
        -------
        boolean
            True if inside the triangle, False if outside
        """
        tri1 = self.verts[self.tri2vert[tri_idx][0]][:2]
        tri2 = self.verts[self.tri2vert[tri_idx][1]][:2]
        tri3 = self.verts[self.tri2vert[tri_idx][2]][:2]

        A = np.stack([tri2 - tri1, tri3 - tri1], axis=1)
        b = pt - tri1
        
        x = np.linalg.solve(A,b)

        if 0 < x[0] < 1 and 0 < x[1] < 1:
            return True
        else:
            return False



    def _getPlane(self, tri_idx):
        """
        Get the gradient and function to evaluate on this plane

        Paramters
        ---------
        tri_idx : integer
            Index of the triangle to use.

        Results
        -------
        func : function
            function which takes x,y and yields a value z
        normal : array-like
            A 3-element vector normal to the plane
        """
        if self._funcs[tri_idx] is None:
            tri1 = self.verts[self.tri2vert[tri_idx][0]]
            tri2 = self.verts[self.tri2vert[tri_idx][1]]
            tri3 = self.verts[self.tri2vert[tri_idx][2]]

            LHS = np.array([[tri1[0], tri2[1], 1],
                            [tri2[0], tri2[1], 1],
                            [tri3[0], tri3[1], 1]])
            RHS = np.array([tri1[2], tri2[2], tri3[2]])
            sol = np.linalg.solve(LHS, RHS)
            normal = np.array([-sol[0], -sol[1], 1])
            normal /= np.linalg.norm(normal)
            self._normals[tri_idx] = normal
            f = lambda x: x[0]*sol[0] + x[1]*sol[1] + sol[2]
            self._funcs[tri_idx] = f

        return self._funcs[tri_idx], self._normals[tri_idx]

class LandscapeException(Exception):
    pass
