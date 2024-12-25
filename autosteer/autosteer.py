import time
import math
from typing import Tuple
from pprint import pprint
from cereal import messaging, car
from openpilot.selfdrive.controls.lib.vehicle_model import VehicleModel

from .sensors import read_sensors
from openpilot.common.numpy_fast import clip

MAX_WIRE_DISTANCE = 3.0
MAX_LAT_ACCEL = 2.5

def Autosteer(sm: messaging.SubMaster, VM: VehicleModel):
  def __init__(self, sm: messaging.SubMaster, VM: VehicleModel):
    self.sm = sm
    self.VM = VM

    self.is_active = False
    self.steeringAngleDeg = 0.0
    self.curvature = 0.0
    self.steer = 0.0
    self.acceleration = 0.0

  def get_acceleration(self, max_acceleration: float) -> float:
      return min(self.acceleration, max_acceleration)

  def get_steering(self) -> Tuple[float, float, float]:
    return self.curvature, self.steer, self.steeringAngleDeg

  def calculate_steering(self, wire_distance: float, sm: messaging.SubMaster, VM: VehicleModel) -> Tuple[float, float, float]:
    """
    Calculate the steering curvature based on the wire distance.

    Args:
      wire_distance: The distance to the wire in meters.
      sm: The SubMaster object.
      VM: The VehicleModel object.

    Returns:
      steeringAngleDeg: The steering angle in degrees.
      curvature: The steering curvature.
      steer: The steering input.
    """

    max_curvature = MAX_LAT_ACCEL / max(sm['carState'].vEgo ** 2, 5)
    max_angle = math.degrees(VM.get_steer_from_curvature(max_curvature, sm['carState'].vEgo, sm['liveParameters'].roll))

    normalized_wire_distance = wire_distance / MAX_WIRE_DISTANCE

    steer = clip(normalized_wire_distance, -1, 1)
    steeringAngleDeg, curvature = steer * max_angle, steer * -max_curvature

    return steeringAngleDeg, curvature, steer

  def calculate_acceleration(self, metadata):
    # TODO: Implement acceleration calculation
    return 0.0

  def main(self):
    """
    Main loop for the Autosteer class.
    """
    while True:
      for active, wire_distance, metadata in read_sensors():
        if active:
          # If autosteer is active, use autosteer data to control the car
          self.is_active = True

        if wire_distance:
          self.steeringAngleDeg, self.curvature, self.steer = self.calculate_steering(wire_distance, sm, VM)

        if metadata:
          self.acceleration = self.calculate_acceleration(metadata)

      else:
        # If autosteer is not active, use the other methods to control the car
        self.is_active = False

      time.sleep(0.01)
