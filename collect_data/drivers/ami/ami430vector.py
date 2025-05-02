from time import sleep

import numpy as np

from .ami430 import AMI430


class AMI430Vector:
    def __init__(self, addrs: tuple(str)):
        """
        Connect to AMI430 all 3-axis magnet.
        xadr, yadr, zadr: IP address of the magnet.
        sets the ramp rate units to seconds.
        sets the field units to Tesla.

        be careful with the field magnitude input,
        it should be in the units of mT.

        program takes care of the unit conversion.

        """

        self.amix = AMI430(addrs[0])
        self.amiy = AMI430(addrs[1])
        self.amiz = AMI430(addrs[2])

        self._name = "AMI430xyz"
        self.config = {
            "name": self._name,
            "IP": {
                "X": self.amix,
                "Y": self.amiy,
                "Z": self.amiz,
            },
        }
        self.amix.ramp_rate_units = "seconds"
        self.amiy.ramp_rate_units = "seconds"
        self.amiz.ramp_rate_units = "seconds"

        self.amix.field_units = "tesla"
        self.amiy.field_units = "tesla"
        self.amiz.field_units = "tesla"

    def get_config(self):
        self.config["params"] = {
            "AMIx_config": self.amix.get_config(),
            "AMIy_config": self.amiy.get_config(),
            "AMiz_config": self.amiz.get_config(),
        }
        return self.config

    def magnetic_field(self):
        mag_x = self.amix.magnetic_field
        mag_y = self.amiy.magnetic_field
        mag_z = self.amiz.magnetic_field
        return np.array([mag_x, mag_y, mag_z])

    def ramp_zero(self):
        self.amix.ramp_rate = 0.001
        self.amiy.ramp_rate = 0.001
        self.amiz.ramp_rate = 0.001

        self.amix.zero()
        self.amiy.zero()
        self.amiz.zero()
        ## check if ramping to zero is finished

        state_x = self.amix.state
        state_y = self.amiy.state
        state_z = self.amiz.state

        while state_x == "RAMPING" or state_y == "RAMPING" or state_z == "RAMPING":
            state_x = self.amix.state
            state_y = self.amiy.state
            state_z = self.amiz.state
            sleep(0.5)

        sleep(1.0)

        if state_x != "HOLDING":
            return "setField failed"
        if state_y != "HOLDING":
            return "setField failed"
        if state_z != "HOLDING":
            return "setField failed"

        print("Bfield is zero")

    def ramp_spherical(self, field=0, theta=0, phi=0, ramp_rate=0.5):
        """
        Basic command to use multi-axis magnet.
        fieldMod: Magnitude of B-field
        thetaDeg: angle along x-axis
        phiDeg  : angle along z-axis
        rampRate: ramp rate of magnet [mT/s], Max is 2 [mT/s]
        """
        theta = float(theta * np.pi / 180)  #
        phi = float(phi * np.pi / 180)  #
        self._theta = theta
        self._phi = phi

        r = field * 1e-3  # Convert to Tesla
        Btilt = np.array(
            [
                r * np.sin(theta) * np.cos(phi),
                r * np.sin(theta) * np.sin(phi),
                r * np.cos(theta),
            ]
        )

        Bcurr = self.magnetic_field().astype("float64")
        # print(type(Btilt))
        # print(type(Bcurr.astype('float64')[0]))
        Bdiff = Btilt - Bcurr

        normalized_B = np.abs(Bdiff) / np.sqrt(np.sum(Bdiff**2))
        rampRates = (0.001 * ramp_rate) * normalized_B  # T -> mT

        for i in range(len(rampRates)):
            if rampRates[i] == 0:
                rampRates[i] = 0.000001

        # print("target = ", Btilt)
        # print("ramp rate = ", rampRates)

        ### check for quench
        if not self.amix.can_start_ramp():
            return "cannot start ramping ami x yet"
        if not self.amiy.can_start_ramp():
            return "cannot start ramping ami x yet"
        if not self.amiz.can_start_ramp():
            return "cannot start ramping ami z yet"

        ### Check we aren't violating field limits
        field_lim = self.amix.field_limit
        if np.abs(Btilt[0]) > field_lim:
            return "The x direction field is too high!"

        field_lim = self.amiy.field_limit
        if np.abs(Btilt[1]) > field_lim:
            return "The y direction field is too high!"

        field_lim = self.amiz.field_limit
        if np.abs(Btilt[2]) > field_lim:
            return "The z direction field is too high!"

        ### Then, do the actual ramp
        ### Set the ramp target
        self.amix.target_field = round(Btilt[0], 7)
        self.amiy.target_field = round(Btilt[1], 7)
        self.amiz.target_field = round(Btilt[2], 7)

        ### adjust Ramp rates
        self.amix.ramp_rate = round(rampRates[0], 7)
        self.amiy.ramp_rate = round(rampRates[1], 7)
        self.amiz.ramp_rate = round(rampRates[2], 7)

        ### then start!
        self.amix.ramp()
        self.amiy.ramp()
        self.amiz.ramp()

        ### check if finished
        state_x = self.amix.state
        state_y = self.amiy.state
        state_z = self.amiz.state
        while state_x == "RAMPING" or state_y == "RAMPING" or state_z == "RAMPING":
            state_x = self.amix.state
            state_y = self.amiy.state
            state_z = self.amiz.state
            sleep(0.5)
        sleep(1.0)

        if state_x != "HOLDING":
            return "setField failed."

        if state_y != "HOLDING":
            return "setField failed."

        if state_z != "HOLDING":
            return "setField failed."

        # print('{} done.'.format(fieldMod))
        cur_Bfield = self.magnetic_field()
        cur_r = np.linalg.norm(cur_Bfield)
        # print(cur_r, cur_Bfield)

    def rotateInPlane(
        self,
        fieldMod,
        initThetaDeg,
        initPhiDeg,
        axisThetaDeg,
        axisPhiDeg,
        rotStep=1,
        rotRange=180,
    ):
        """
        It gives us rotation angles of the B-field along any axis.
        https://en.wikipedia.org/wiki/Rodrigues%27_rotation_formula
        """
        init_theta = float(initThetaDeg * np.pi / 180)  #
        init_phi = float(initPhiDeg * np.pi / 180)  #
        r = 0.001 * fieldMod  # T -> mT

        axis_theta = float(axisThetaDeg * np.pi / 180)  #
        axis_phi = float(axisPhiDeg * np.pi / 180)  #

        initVec = np.array(
            [
                r * np.sin(init_theta) * np.cos(init_phi),
                r * np.sin(init_theta) * np.sin(init_phi),
                r * np.cos(init_theta),
            ]
        )
        n = np.array(
            [
                r * np.sin(axis_theta) * np.cos(axis_phi),
                r * np.sin(axis_theta) * np.sin(axis_phi),
                r * np.cos(axis_theta),
            ]
        )
        norm_n = np.linalg.norm(n)
        n = n / norm_n  # unit vector along the axis of rotation

        rotStepInRad = float(rotStep * np.pi / 180)

        RodMatrics = np.array(
            [
                [
                    n[0] * n[0] * (1 - np.cos(rotStepInRad)) + np.cos(rotStepInRad),
                    n[0] * n[1] * (1 - np.cos(rotStepInRad))
                    - n[2] * np.sin(rotStepInRad),
                    n[2] * n[0] * (1 - np.cos(rotStepInRad))
                    + n[1] * np.sin(rotStepInRad),
                ],
                [
                    n[0] * n[1] * (1 - np.cos(rotStepInRad))
                    + n[2] * np.sin(rotStepInRad),
                    n[1] * n[1] * (1 - np.cos(rotStepInRad)) + np.cos(rotStepInRad),
                    n[1] * n[2] * (1 - np.cos(rotStepInRad))
                    - n[0] * np.sin(rotStepInRad),
                ],
                [
                    n[2] * n[0] * (1 - np.cos(rotStepInRad))
                    - n[1] * np.sin(rotStepInRad),
                    n[1] * n[2] * (1 - np.cos(rotStepInRad))
                    + n[0] * np.sin(rotStepInRad),
                    n[2] * n[2] * (1 - np.cos(rotStepInRad)) + np.cos(rotStepInRad),
                ],
            ]
        )  # Rodrigues rotation formula

        rotVec_list = [initVec]
        rotAng_list = [[init_theta * (180 / np.pi), init_phi * (180 / np.pi)]]

        for i in range(1, (int(rotRange / rotStep) + 1)):
            _rotVec = np.dot(RodMatrics, rotVec_list[i - 1])
            rotVec_list.append(_rotVec)

            _x = _rotVec[0]
            _y = _rotVec[1]
            _z = _rotVec[2]

            _theta = np.arccos(_z / np.sqrt(_x**2 + _y**2 + _z**2))
            _phi = np.sign(_y) * np.arccos(_x / np.sqrt(_x**2 + _y**2))
            rotAng_list.append([_theta * (180 / np.pi), _phi * (180 / np.pi)])

        # print(rotVec_list)
        return rotAng_list

    def rotateInGreatCircle(
        self,
        fieldMod,
        initThetaDeg,
        initPhiDeg,
        rotStep=1,
        rotRange=180,
        plusminus=False,
    ):
        """
        It gives us rotation angles of the B-field along a great circle including the initial vector.
        """

        if plusminus:
            plus = self.rotateInPlane(
                fieldMod=fieldMod,
                initThetaDeg=initThetaDeg,
                initPhiDeg=initPhiDeg,
                axisThetaDeg=initThetaDeg + 90,
                axisPhiDeg=initPhiDeg,
                rotStep=rotStep,
                rotRange=rotRange / 2,
            )
            minus = self.rotateInPlane(
                fieldMod=fieldMod,
                initThetaDeg=initThetaDeg,
                initPhiDeg=initPhiDeg,
                axisThetaDeg=initThetaDeg + 90,
                axisPhiDeg=initPhiDeg,
                rotStep=rotStep,
                rotRange=360,
            )[-int(rotRange / 2 / rotStep) - 1 : -1]

            return minus + plus

        return self.rotateInPlane(
            fieldMod=fieldMod,
            initThetaDeg=initThetaDeg,
            initPhiDeg=initPhiDeg,
            axisThetaDeg=initThetaDeg + 90,
            axisPhiDeg=initPhiDeg,
            rotStep=rotStep,
            rotRange=rotRange,
        )


if __name__ == "__main__":
    
    magnet = AMI430Vector((mag_x, mag_y, mag_z))
    magnet.ramp_spherical(field=165.65, theta=0, phi=0, ramp_rate=0.1)
