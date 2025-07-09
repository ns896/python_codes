# Author: Navneet Singh
# mobil_eye_structures.py
# Data structures for the Mobil Eye CAN Data

from dataclasses import dataclass, field
from typing import Dict, List, Optional
import time 
import can
import cantools 


@dataclass
class Obstacle_Data:
    " Data Structure for the Obstacle Data"
    object_class: int = 0
    longitudinal_distance: float = 0.0
    lateral_distance: float = 0.0
    absolute_long_velocity: float = 0.0
    absolute_lateral_velocity: float = 0.0
    id: int = 0
    motion_status: str = ""
    object_age: int = 0
    last_update: float = 0.0

@dataclass
class Obstacle_Data_List:

    object1: Obstacle_Data = field(default_factory=Obstacle_Data)
    object2: Obstacle_Data = field(default_factory=Obstacle_Data)
    object3: Obstacle_Data = field(default_factory=Obstacle_Data)
    object4: Obstacle_Data = field(default_factory=Obstacle_Data)
    object5: Obstacle_Data = field(default_factory=Obstacle_Data)
    object6: Obstacle_Data = field(default_factory=Obstacle_Data)
    object7: Obstacle_Data = field(default_factory=Obstacle_Data)
    object8: Obstacle_Data = field(default_factory=Obstacle_Data)
    object9: Obstacle_Data = field(default_factory=Obstacle_Data)
    object10: Obstacle_Data = field(default_factory=Obstacle_Data)

@dataclass
class Left_Lane_Data:
    "Data Structure for Lane Data"
    classification: str = ""  # Classification of lane marking
    quality: str = ""  # Quality of lane detection
    LaneMarkPosition_C0_Lh_ME: float = 0.0  # Lane mark position C0 in meters
    LaneMarkModelA_C2_Lh_ME: float = 0.0  # Lane mark heading angle C1 in radians  
    LaneMarkHeadingAngle_C1_Lh_ME: float = 0.0  # Lane mark model coefficient A (C2) in 1/m
    LaneMarkModelDerivA_C3_Lh_ME: float = 0.0  # Lane mark model derivative A (C3) in 1/m2
    last_update: float = 0.0

@dataclass
class Right_Lane_Data:
    "Data Structure for Lane Data"
    classification: str = ""  # Classification of lane marking
    quality: str = ""  # Quality of lane detection
    LaneMarkPosition_C0_Rh_ME: float = 0.0  # Lane mark position C0 in meters
    LaneMarkModelA_C2_Rh_ME: float = 0.0  # Lane mark heading angle C1 in radians  
    LaneMarkHeadingAngle_C1_Rh_ME: float = 0.0  # Lane mark model coefficient A (C2) in 1/m
    LaneMarkModelDerivA_C3_Rh_ME: float = 0.0  # Lane mark model derivative A (C3) in 1/m2
    last_update: float = 0.0

   
class Process_Mobil_Eye_CAN_Data:
    " Class to process the Mobil Eye CAN Data"
    def __init__(self, database):
        self.obstacle_data_list = Obstacle_Data_List()
        self.left_lane_data = Left_Lane_Data()
        self.right_lane_data = Right_Lane_Data()
        self.can_data_base = database

    def parse_mobil_eye_can_data(self, msg, obstacle_data_list):
        " Process the Mobil Eye CAN Data"

        match msg.arbitration_id:
            case 568:
                # Decode the message using cantools database
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    # print("--------------------------------")
                    # print(decoded)
                    # print("--------------------------------")
                    # Update object1 data from the decoded dictionary
                    self.obstacle_data_list.object1.object_class = decoded['Object_Class_1_A']
                    self.obstacle_data_list.object1.longitudinal_distance = decoded['Longitudinal_Distance_1_A'] 
                    self.obstacle_data_list.object1.lateral_distance = decoded['Lateral_Distance_1_A']
                    self.obstacle_data_list.object1.absolute_long_velocity = decoded['Absolute_Long_Velocity_1_A']
                    self.obstacle_data_list.object1.absolute_lateral_velocity = decoded['Absolute_Lateral_Velocity_1_A']
                    self.obstacle_data_list.object1.id = decoded['ID_1_A']
                    self.obstacle_data_list.object1.last_update = time.time()

                except Exception as e:
                    print(f"Error decoding message: {e}")
                
            case 569:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    motion_status = decoded['Motion_Status_1_B']
                    
                    self.obstacle_data_list.object1.motion_status = motion_status
                    self.obstacle_data_list.object1.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding motion status message: {e}")
            
            case 570:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    object_age = decoded['Object_Age_1_C']
                    self.obstacle_data_list.object1.object_age = object_age
                    self.obstacle_data_list.object1.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding object age message: {e}")

            case 571:
                # Decode the message using cantools database
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    # Update object1 data from the decoded dictionary
                    self.obstacle_data_list.object2.object_class = decoded['Object_Class_2_A']
                    self.obstacle_data_list.object2.longitudinal_distance = decoded['Longitudinal_Distance_2_A'] 
                    self.obstacle_data_list.object2.lateral_distance = decoded['Lateral_Distance_2_A']
                    self.obstacle_data_list.object2.absolute_long_velocity = decoded['Absolute_Long_Velocity_2_A']
                    self.obstacle_data_list.object2.absolute_lateral_velocity = decoded['Absolute_Lateral_Velocity_2_A']
                    self.obstacle_data_list.object2.id = decoded['ID_2_A']
                    self.obstacle_data_list.object2.last_update = time.time()

                except Exception as e:
                    print(f"Error decoding message: {e}")
                
            case 572:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    motion_status = decoded['Motion_Status_2_B']
                    
                    self.obstacle_data_list.object2.motion_status = motion_status
                    self.obstacle_data_list.object2.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding motion status message: {e}")
            
            case 573:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    object_age = decoded['Object_Age_2_C']
                    self.obstacle_data_list.object2.object_age = object_age
                    self.obstacle_data_list.object2.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding object age message: {e}")

            case 574:
                # Decode the message using cantools database
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    # Update object1 data from the decoded dictionary
                    self.obstacle_data_list.object3.object_class = decoded['Object_Class_3_A']
                    self.obstacle_data_list.object3.longitudinal_distance = decoded['Longitudinal_Distance_3_A'] 
                    self.obstacle_data_list.object3.lateral_distance = decoded['Lateral_Distance_3_A']
                    self.obstacle_data_list.object3.absolute_long_velocity = decoded['Absolute_Long_Velocity_3_A']
                    self.obstacle_data_list.object3.absolute_lateral_velocity = decoded['Absolute_Lateral_Velocity_3_A']
                    self.obstacle_data_list.object3.id = decoded['ID_3_A']
                    self.obstacle_data_list.object3.last_update = time.time()

                except Exception as e:
                    print(f"Error decoding message: {e}")
                
            case 575:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    motion_status = decoded['Motion_Status_3_B']
                    
                    self.obstacle_data_list.object3.motion_status = motion_status
                    self.obstacle_data_list.object3.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding motion status message: {e}")
            
            case 576:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    object_age = decoded['Object_Age_3_C']
                    self.obstacle_data_list.object3.object_age = object_age
                    self.obstacle_data_list.object3.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding object age message: {e}")

            case 577:
                # Decode the message using cantools database
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    # Update object1 data from the decoded dictionary
                    self.obstacle_data_list.object4.object_class = decoded['Object_Class_4_A']
                    self.obstacle_data_list.object4.longitudinal_distance = decoded['Longitudinal_Distance_4_A'] 
                    self.obstacle_data_list.object4.lateral_distance = decoded['Lateral_Distance_4_A']
                    self.obstacle_data_list.object4.absolute_long_velocity = decoded['Absolute_Long_Velocity_4_A']
                    self.obstacle_data_list.object4.absolute_lateral_velocity = decoded['Absolute_Lateral_Velocity_4_A']
                    self.obstacle_data_list.object4.id = decoded['ID_4_A']
                    self.obstacle_data_list.object4.last_update = time.time()

                except Exception as e:
                    print(f"Error decoding message: {e}")
                
            case 578:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    motion_status = decoded['Motion_Status_4_B']
                    
                    self.obstacle_data_list.object4.motion_status = motion_status
                    self.obstacle_data_list.object4.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding motion status message: {e}")
            
            case 579:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    object_age = decoded['Object_Age_4_C']
                    self.obstacle_data_list.object4.object_age = object_age
                    self.obstacle_data_list.object4.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding object age message: {e}")

            case 580:
                # Decode the message using cantools database
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    # Update object1 data from the decoded dictionary
                    self.obstacle_data_list.object5.object_class = decoded['Object_Class_5_A']
                    self.obstacle_data_list.object5.longitudinal_distance = decoded['Longitudinal_Distance_5_A'] 
                    self.obstacle_data_list.object5.lateral_distance = decoded['Lateral_Distance_5_A']
                    self.obstacle_data_list.object5.absolute_long_velocity = decoded['Absolute_Long_Velocity_5_A']
                    self.obstacle_data_list.object5.absolute_lateral_velocity = decoded['Absolute_Lateral_Velocity_5_A']
                    self.obstacle_data_list.object5.id = decoded['ID_5_A']
                    self.obstacle_data_list.object5.last_update = time.time()

                except Exception as e:
                    print(f"Error decoding message: {e}")
                
            case 581:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    motion_status = decoded['Motion_Status_5_B']
                    
                    self.obstacle_data_list.object5.motion_status = motion_status
                    self.obstacle_data_list.object5.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding motion status message: {e}")
            
            case 582:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    object_age = decoded['Object_Age_5_C']
                    self.obstacle_data_list.object5.object_age = object_age
                    self.obstacle_data_list.object5.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding object age message: {e}")

            case 583:
                # Decode the message using cantools database
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    # Update object1 data from the decoded dictionary
                    self.obstacle_data_list.object6.object_class = decoded['Object_Class_6_A']
                    self.obstacle_data_list.object6.longitudinal_distance = decoded['Longitudinal_Distance_6_A'] 
                    self.obstacle_data_list.object6.lateral_distance = decoded['Lateral_Distance_6_A']
                    self.obstacle_data_list.object6.absolute_long_velocity = decoded['Absolute_Long_Velocity_6_A']
                    self.obstacle_data_list.object6.absolute_lateral_velocity = decoded['Absolute_Lateral_Velocity_6_A']
                    self.obstacle_data_list.object6.id = decoded['ID_6_A']
                    self.obstacle_data_list.object6.last_update = time.time()

                except Exception as e:
                    print(f"Error decoding message: {e}")
                
            case 584:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    motion_status = decoded['Motion_Status_6_B']
                    
                    self.obstacle_data_list.object6.motion_status = motion_status
                    self.obstacle_data_list.object6.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding motion status message: {e}")
            
            case 585:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    object_age = decoded['Object_Age_6_C']
                    self.obstacle_data_list.object6.object_age = object_age
                    self.obstacle_data_list.object6.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding object age message: {e}")

            case 586:
                # Decode the message using cantools database
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    # Update object1 data from the decoded dictionary
                    self.obstacle_data_list.object7.object_class = decoded['Object_Class_7_A']
                    self.obstacle_data_list.object7.longitudinal_distance = decoded['Longitudinal_Distance_7_A'] 
                    self.obstacle_data_list.object7.lateral_distance = decoded['Lateral_Distance_7_A']
                    self.obstacle_data_list.object7.absolute_long_velocity = decoded['Absolute_Long_Velocity_7_A']
                    self.obstacle_data_list.object7.absolute_lateral_velocity = decoded['Absolute_Lateral_Velocity_7_A']
                    self.obstacle_data_list.object7.id = decoded['ID_7_A']
                    self.obstacle_data_list.object7.last_update = time.time()

                except Exception as e:
                    print(f"Error decoding message: {e}")
                
            case 587:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    motion_status = decoded['Motion_Status_7_B']
                    
                    self.obstacle_data_list.object7.motion_status = motion_status
                    self.obstacle_data_list.object7.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding motion status message: {e}")
            
            case 588:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    object_age = decoded['Object_Age_7_C']
                    self.obstacle_data_list.object7.object_age = object_age
                    self.obstacle_data_list.object7.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding object age message: {e}")

            case 589:
                # Decode the message using cantools database
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    # Update object1 data from the decoded dictionary
                    self.obstacle_data_list.object8.object_class = decoded['Object_Class_8_A']
                    self.obstacle_data_list.object8.longitudinal_distance = decoded['Longitudinal_Distance_8_A'] 
                    self.obstacle_data_list.object8.lateral_distance = decoded['Lateral_Distance_8_A']
                    self.obstacle_data_list.object8.absolute_long_velocity = decoded['Absolute_Long_Velocity_8_A']
                    self.obstacle_data_list.object8.absolute_lateral_velocity = decoded['Absolute_Lateral_Velocity_8_A']
                    self.obstacle_data_list.object8.id = decoded['ID_8_A']
                    self.obstacle_data_list.object8.last_update = time.time()

                except Exception as e:
                    print(f"Error decoding message: {e}")
                
            case 590:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    motion_status = decoded['Motion_Status_8_B']
                    
                    self.obstacle_data_list.object8.motion_status = motion_status
                    self.obstacle_data_list.object8.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding motion status message: {e}")
            
            case 591:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    object_age = decoded['Object_Age_8_C']
                    self.obstacle_data_list.object8.object_age = object_age
                    self.obstacle_data_list.object8.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding object age message: {e}")

            case 592:
                # Decode the message using cantools database
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    # Update object1 data from the decoded dictionary
                    self.obstacle_data_list.object9.object_class = decoded['Object_Class_9_A']
                    self.obstacle_data_list.object9.longitudinal_distance = decoded['Longitudinal_Distance_9_A'] 
                    self.obstacle_data_list.object9.lateral_distance = decoded['Lateral_Distance_9_A']
                    self.obstacle_data_list.object9.absolute_long_velocity = decoded['Absolute_Long_Velocity_9_A']
                    self.obstacle_data_list.object9.absolute_lateral_velocity = decoded['Absolute_Lateral_Velocity_9_A']
                    self.obstacle_data_list.object9.id = decoded['ID_9_A']
                    self.obstacle_data_list.object9.last_update = time.time()

                except Exception as e:
                    print(f"Error decoding message: {e}")
                
            case 593:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    motion_status = decoded['Motion_Status_9_B']
                    
                    self.obstacle_data_list.object9.motion_status = motion_status
                    self.obstacle_data_list.object9.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding motion status message: {e}")
            
            case 594:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    object_age = decoded['Object_Age_9_C']
                    self.obstacle_data_list.object9.object_age = object_age
                    self.obstacle_data_list.object9.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding object age message: {e}")

            case 595:
                # Decode the message using cantools database
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    # Update object1 data from the decoded dictionary
                    self.obstacle_data_list.object10.object_class = decoded['Object_Class_10_A']
                    self.obstacle_data_list.object10.longitudinal_distance = decoded['Longitudinal_Distance_10_A'] 
                    self.obstacle_data_list.object10.lateral_distance = decoded['Lateral_Distance_10_A']
                    self.obstacle_data_list.object10.absolute_long_velocity = decoded['Absolute_Long_Velocity_10_A']
                    self.obstacle_data_list.object10.absolute_lateral_velocity = decoded['Absolute_Lateral_Velocity_10_A']
                    self.obstacle_data_list.object10.id = decoded['ID_10_A']
                    self.obstacle_data_list.object10.last_update = time.time()

                except Exception as e:
                    print(f"Error decoding message: {e}")
                
            case 596:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    motion_status = decoded['Motion_Status_10_B']
                    
                    self.obstacle_data_list.object10.motion_status = motion_status
                    self.obstacle_data_list.object10.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding motion status message: {e}")
            
            case 597:
                try:
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    object_age = decoded['Object_Age_10_C']
                    self.obstacle_data_list.object10.object_age = object_age
                    self.obstacle_data_list.object10.last_update = time.time()
                    
                except Exception as e:
                    print(f"Error decoding object age message: {e}")
            
            case 614:
                try:
                    # Decode the message using cantools database
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    self.left_lane_data.classification = decoded['Classification_Lh_ME']
                    self.left_lane_data.quality = decoded['Quality_Lh_ME']
                    self.left_lane_data.LaneMarkPosition_C0_Lh_ME = decoded['LaneMarkPosition_C0_Lh_ME']
                    self.left_lane_data.LaneMarkModelA_C2_Lh_ME = decoded['LaneMarkModelA_C2_Lh_ME']
                    # Update timestamp immediately when first part of left lane data arrives
                    self.left_lane_data.last_update = time.time()
                except Exception as e:
                    print(f"Error decoding message: {e}")

            case 615:
                try:
                    # Decode the message using cantools database
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    self.left_lane_data.LaneMarkHeadingAngle_C1_Lh_ME = decoded['LaneMarkHeadingAngle_C1_Lh_ME']
                    self.left_lane_data.LaneMarkModelDerivA_C3_Lh_ME = decoded['LaneMarkModelDerivA_C3_Lh_ME']
                    # Update timestamp when second part of left lane data arrives
                    self.left_lane_data.last_update = time.time()
                except Exception as e:
                    print(f"Error decoding message: {e}")

            case 616:
                try:
                    # Decode the message using cantools database
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    self.right_lane_data.classification = decoded['Classification_Rh_ME']
                    self.right_lane_data.quality = decoded['Quality_Rh_ME']
                    self.right_lane_data.LaneMarkPosition_C0_Rh_ME = decoded['LaneMarkPosition_C0_Rh_ME']
                    self.right_lane_data.LaneMarkModelA_C2_Rh_ME = decoded['LaneMarkModelA_C2_Rh_ME']
                    # Update timestamp immediately when first part of right lane data arrives
                    self.right_lane_data.last_update = time.time()
                except Exception as e:
                    print(f"Error decoding message: {e}")

            case 617:
                try:
                    # Decode the message using cantools database
                    decoded = self.can_data_base.decode_message(msg.arbitration_id, msg.data)
                    self.right_lane_data.LaneMarkHeadingAngle_C1_Rh_ME = decoded['LaneMarkHeadingAngle_C1_Rh_ME']
                    self.right_lane_data.LaneMarkModelDerivA_C3_Rh_ME = decoded['LaneMarkModelDerivA_C3_Rh_ME']
                    # Update timestamp when second part of right lane data arrives
                    self.right_lane_data.last_update = time.time()
                except Exception as e:
                    print(f"Error decoding message: {e}")

            case _:
                pass
                # print("Unknown message ID")