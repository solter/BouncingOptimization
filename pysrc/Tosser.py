"""
This class defines the tosser,
and thus contains the ball propagation routines.
"""
import numpy as np

import landscape as ls

class Tosser():
    """
    Class containing the tosser object

    Parameters
    ----------
    landscape_file : str
        Path to the landscape file the tosser lives in.
    x : float
        x location of tosser
    y : float
        y location of tosser
    z : float
        z location of tosser. If not provided,
        the tosser is placed on the landscape.
        If the tosser is outside, or below, of the landscape,
        an exception is thrown.
    """

    def __init__(self, landscape_file, x, y, z=None):
        self.x = x
        self.y = y
        self.landscape = ls.landscape.load(landscape_file)

        try:
            z_ls = self.landscape.valueAndNormal(x,y)
        except ls.LandscapeException:
            raise TosserError("Tosser is outside of landscape")

        if z is None:
            self.z = z_ls
        elif z >= z_ls:
            self.z = z
        else:
            raise TosserError("Tosser is below the landscape")

    def throw(self, azim, elev, vel, num_bounce):
        """
        Throws the ball and returns where it lands.

        Parameters
        ----------
        azim : degrees
            azimuth the ball is thrown at.
            Defined as clockwise from the y-axis.
            0 < azim < 360
        elev : degrees
            elevation the ball is thrown at.
            Defind as angle above the x-y plane.
            0 < elev < 90
        vel : m/s
            velocity the ball is thrown at.
            0 < vel
        num_bounce : integer
            number of bounces the ball must take before
            it stops. A bounce is defined as a touching
            of the landscape. So 2 bounces will bounce
            off the landscape once, then stick the 2nd
            time it touches the landscape.
        """
        unit_vel = np.zeros(3)

        unit_vel[0] = np.cos(elev)*np.sin(azim) # x component
        unit_vel[1] = np.cos(elev)*np.cos(azim) # y component
        unit_vel[2] = np.sin(elev) # z component

        # Velocity as a vector
        vel_vec = vel*unit_vel

        # For the number of bounces
        pos = np.array([self.x, self.y, self.z])
        for i in range(num_bounce):
            # Perform a bounce
            pos, vel = self.bounce(pos, vel_vec)
            # Reflect the velocity off the landscape
            _, normal = self.landscape.valueAndNormal(pos[0], pos[1])
            # Projection onto the normal
            vel_norm = np.dot(vel, normal)*normal
            # Projection orthoganal to the normal
            vel_par = vel - vel_norm
            # Final velocity reflects the normal velocity,
            # but maintains the orthogonal projection
            vel_vec = vel_par - vel_norm

        return pos

    def bounce(pos, vel):
        """
        Perform projectile motion until intersecting the landscape.

        Parameters
        ----------
        pos : 3-element array, m
            position to start from
        vel : 3-element array, m/s
            velocity the bounce starts at

        Results
        -------
        pos : 3-element array, m
            final position
        vel : 3-element array, m/s
            velocity at the final position
        """
        # Define equations of motion
        a = np.array([0,0,-10])
        pos_t = lambda t: .5*a*t**2 + vel*t + pos
        vel_t = lambda t: a*t + vel

        ## Find the time that it takes to hit the landscape
        # Initial Time step should corresponds to .5 meter
        # TODO: this should be tied to the landscape gradient...
        dt = .5/np.linalg.norm(vel) 

        t_left = 0
        t_right = 0 + dt
        pos = pos_t(t_right)
        z_ls, _ = self.landscape.valueAndNormal(pos[0], pos[1])

        # Step forward until we get below the landscape
        while pos[2] > z_ls:
            t_left = t_right
            t_right+= dt
            pos = pos_t(t_right)
            z_ls, _ = self.landscape.valueAndNormal(pos[0], pos[1])

        # We have now stepped too far, so use a binary search
        # to find exactly where it intersects the landscape,
        # to within 1 mm
        while t_right - t_left > 1e-3/np.linalg.norm(vel):
            # Calculate the midpoint
            t_mid = .5*(t_right - t_left)
            pos = pos_t(t_mid)
            z_ls, _ = self.landscape.valueAndNormal(pos[0], pos[1])

            # If the midpoint is too far
            if pos[2] < z_ls:
                t_right = t_mid
            # If the midpoint is too close
            elif pos[2] > z_ls:
                t_left = t_mid
            # If the midpoint is the exact solution
            else:
                t_final = t_mid
                break
        else:
            # If the loop terminates because it gets smaller
            # than the tolerance without finding the exact point,
            # make t_final the point just above the surface
            t_final = left

        return pos_t(t_final), vel_t(t_final)

class TosserError(Exception):
    pass

