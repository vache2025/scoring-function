import math

class SightFXMetricsCalculator:
    def __init__(self):
        # Age groups and skill levels for adaptive metrics
        self.age_groups = {
            1: "Youth (8-12)",
            2: "Young Adult (13-25)", 
            3: "Adult (26-39)",
            4: "Middle Age (40-55)",
            5: "Masters (56+)"
        }
        
        self.skill_levels = {
            1: "Beginner",
            2: "Intermediate", 
            3: "Elite"
        }
        
        # ORIGINAL FIXED METRICS (Elite Adult Standards)
        self.fixed_metrics = {
            # WINDUP PHASE METRICS
            "Balance Stability Index": {
                "description": "Quantifies COM maintenance during leg lift",
                "unit": "cm deviation",
                "optimal_range": (0, 2),
                "elite_threshold": 2,
                "warning_threshold": 5,
                "lower_is_better": True,
                "phase": "Windup"
            }
        }
        
        # Add new metric categories
        self.fixed_metrics.update({
            # PITCH TYPE-SPECIFIC METRICS
            "Four-Seam Fastball Spin Efficiency": {
                "description": "Spin efficiency for four-seam fastball",
                "unit": "percentage",
                "optimal_range": (90, 100),
                "elite_threshold": 100,
                "warning_threshold": 80,
                "lower_is_better": False,
                "phase": "Pitch Specific"
            },
            "Four-Seam Fastball Ball Axis": {
                "description": "Ball axis orientation",
                "unit": "clock position deviation from 12:00-1:00",
                "optimal_range": (0, 1),  # Perfect alignment
                "elite_threshold": 1,
                "warning_threshold": 2,
                "lower_is_better": True,
                "phase": "Pitch Specific"
            },
            "Two-Seam Fastball Horizontal Movement": {
                "description": "Horizontal movement for two-seam fastball",
                "unit": "inches",
                "optimal_range": (6, 14),
                "elite_threshold": 14,
                "warning_threshold": 4,
                "lower_is_better": False,
                "phase": "Pitch Specific"
            },
            "Changeup Velocity Differential": {
                "description": "Speed difference from fastball",
                "unit": "mph slower than FB",
                "optimal_range": (8, 12),
                "elite_threshold": 12,
                "warning_threshold": 6,
                "lower_is_better": False,
                "phase": "Pitch Specific"
            },
            "Curveball Spin Rate": {
                "description": "Spin rate for curveball",
                "unit": "rpm",
                "optimal_range": (2600, 3000),
                "elite_threshold": 3000,
                "warning_threshold": 2300,
                "lower_is_better": False,
                "phase": "Pitch Specific"
            },
            "Slider Gyroscopic Component": {
                "description": "Gyroscopic spin component for slider",
                "unit": "percentage",
                "optimal_range": (10, 30),
                "elite_threshold": 30,
                "warning_threshold": 5,
                "lower_is_better": False,
                "phase": "Pitch Specific"
            },
            
            # KINETIC CHAIN EFFICIENCY METRICS
            "Ground Force Utilization": {
                "description": "Transfer of ground reaction force",
                "unit": "times body weight vertical GRF",
                "optimal_range": (1.2, 1.5),
                "elite_threshold": 1.5,
                "warning_threshold": 1.0,
                "lower_is_better": False,
                "phase": "Kinetic Chain"
            },
            "Pelvic-Trunk Timing": {
                "description": "Delay between peak pelvic and trunk rotation",
                "unit": "seconds",
                "optimal_range": (0.015, 0.025),
                "elite_threshold": 0.025,
                "warning_threshold": 0.035,
                "lower_is_better": False,
                "phase": "Kinetic Chain"
            },
            "Trunk-Arm Timing": {
                "description": "Delay between peak trunk rotation and shoulder rotation",
                "unit": "seconds",
                "optimal_range": (0.015, 0.025),
                "elite_threshold": 0.025,
                "warning_threshold": 0.035,
                "lower_is_better": False,
                "phase": "Kinetic Chain"
            },
            "Energy Transfer Efficiency": {
                "description": "Percentage of energy transferred up kinetic chain",
                "unit": "percentage",
                "optimal_range": (80, 90),
                "elite_threshold": 90,
                "warning_threshold": 70,
                "lower_is_better": False,
                "phase": "Kinetic Chain"
            },
            "Joint Torque Distribution": {
                "description": "Balanced loading across joints",
                "unit": "percentage variation between adjacent segments",
                "optimal_range": (0, 25),
                "elite_threshold": 25,
                "warning_threshold": 40,
                "lower_is_better": True,
                "phase": "Kinetic Chain"
            },
            "Movement Plane Consistency": {
                "description": "Minimization of out-of-plane motion",
                "unit": "degrees deviation from optimal path",
                "optimal_range": (0, 5),
                "elite_threshold": 5,
                "warning_threshold": 10,
                "lower_is_better": True,
                "phase": "Kinetic Chain"
            },
            "Lead Knee Elevation": {
                "description": "Maximum height of lead knee relative to hip",
                "unit": "degrees",
                "optimal_range": (60, 90),
                "elite_threshold": 90,
                "warning_threshold": 50,
                "lower_is_better": False,
                "phase": "Windup"
            },
            "Posture Alignment": {
                "description": "Spine angle consistency during windup",
                "unit": "degree variation",
                "optimal_range": (0, 3),
                "elite_threshold": 3,
                "warning_threshold": 8,
                "lower_is_better": True,
                "phase": "Windup"
            },
            "Tempo Consistency": {
                "description": "Variation in timing between pitches",
                "unit": "seconds",
                "optimal_range": (0, 0.05),
                "elite_threshold": 0.05,
                "warning_threshold": 0.2,
                "lower_is_better": True,
                "phase": "Windup"
            },
            "Weight Distribution": {
                "description": "Percentage on back leg at maximum knee lift",
                "unit": "percentage",
                "optimal_range": (85, 95),
                "elite_threshold": 95,
                "warning_threshold": 80,
                "lower_is_better": False,
                "phase": "Windup"
            },
            "Torso Rotation Angle": {
                "description": "Initial rotation away from target",
                "unit": "degrees",
                "optimal_range": (15, 25),
                "elite_threshold": 25,
                "warning_threshold": 30,
                "lower_is_better": False,
                "phase": "Windup"
            },
            "Head Stability": {
                "description": "Movement of head during leg lift",
                "unit": "cm displacement",
                "optimal_range": (0, 2),
                "elite_threshold": 2,
                "warning_threshold": 4,
                "lower_is_better": True,
                "phase": "Windup"
            },
            "Lead Leg Path Efficiency": {
                "description": "Directness of knee lift trajectory",
                "unit": "cm lateral deviation",
                "optimal_range": (0, 5),
                "elite_threshold": 5,
                "warning_threshold": 10,
                "lower_is_better": True,
                "phase": "Windup"
            },
            
            # STRIDE/FOOT PLANT METRICS
            "Stride Length": {
                "description": "Distance as percentage of pitcher's height",
                "unit": "percentage of height",
                "optimal_range": (80, 90),
                "elite_threshold": 90,
                "warning_threshold": 70,
                "lower_is_better": False,
                "phase": "Stride"
            },
            "Stride Direction": {
                "description": "Angle relative to center line",
                "unit": "degrees closed",
                "optimal_range": (0, 5),
                "elite_threshold": 5,
                "warning_threshold": 10,
                "lower_is_better": True,
                "phase": "Stride"
            },
            "Hip-Shoulder Separation": {
                "description": "Rotational difference at foot contact",
                "unit": "degrees",
                "optimal_range": (40, 50),
                "elite_threshold": 50,
                "warning_threshold": 30,
                "lower_is_better": False,
                "phase": "Stride"
            },
            "Pelvic Tilt": {
                "description": "Anterior/posterior pelvic positioning",
                "unit": "degrees anterior tilt",
                "optimal_range": (5, 15),
                "elite_threshold": 15,
                "warning_threshold": 20,
                "lower_is_better": False,
                "phase": "Stride"
            },
            "Center of Mass Trajectory": {
                "description": "Path of COM during stride",
                "unit": "cm vertical displacement",
                "optimal_range": (0, 3),
                "elite_threshold": 3,
                "warning_threshold": 6,
                "lower_is_better": True,
                "phase": "Stride"
            },
            "Front Foot Landing Pattern": {
                "description": "Foot position and angle at contact",
                "unit": "degrees closed",
                "optimal_range": (10, 20),
                "elite_threshold": 20,
                "warning_threshold": 30,
                "lower_is_better": False,
                "phase": "Stride"
            },
            "Timing Efficiency": {
                "description": "Duration from leg lift to foot contact",
                "unit": "seconds",
                "optimal_range": (0.5, 0.7),
                "elite_threshold": 0.7,
                "warning_threshold": 0.9,
                "lower_is_better": False,
                "phase": "Stride"
            },
            "Lead Knee Position": {
                "description": "Flexion angle at foot contact",
                "unit": "degrees",
                "optimal_range": (35, 45),
                "elite_threshold": 45,
                "warning_threshold": 25,
                "lower_is_better": False,
                "phase": "Stride"
            },
            
            # ARM COCKING PHASE METRICS
            "Maximum External Rotation": {
                "description": "Shoulder rotation at MER",
                "unit": "degrees",
                "optimal_range": (165, 185),
                "elite_threshold": 185,
                "warning_threshold": 150,
                "lower_is_better": False,
                "phase": "Arm Cocking"
            },
            "Arm Slot Consistency": {
                "description": "Variation in arm position at MER",
                "unit": "degrees between pitches",
                "optimal_range": (0, 3),
                "elite_threshold": 3,
                "warning_threshold": 8,
                "lower_is_better": True,
                "phase": "Arm Cocking"
            },
            "Elbow Height": {
                "description": "Position relative to shoulder at MER",
                "unit": "cm above shoulder",
                "optimal_range": (0, 5),
                "elite_threshold": 5,
                "warning_threshold": -10,  # Below shoulder is bad
                "lower_is_better": False,
                "phase": "Arm Cocking"
            },
            "Trunk Forward Tilt": {
                "description": "Forward lean from vertical at MER",
                "unit": "degrees",
                "optimal_range": (20, 30),
                "elite_threshold": 30,
                "warning_threshold": 15,
                "lower_is_better": False,
                "phase": "Arm Cocking"
            },
            "Trunk Lateral Tilt": {
                "description": "Side bend toward non-throwing side",
                "unit": "degrees",
                "optimal_range": (15, 25),
                "elite_threshold": 25,
                "warning_threshold": 10,
                "lower_is_better": False,
                "phase": "Arm Cocking"
            },
            "Kinetic Chain Sequencing": {
                "description": "Timing between peak segment velocities",
                "unit": "seconds between segments",
                "optimal_range": (0.015, 0.025),
                "elite_threshold": 0.025,
                "warning_threshold": 0.035,
                "lower_is_better": False,
                "phase": "Arm Cocking"
            },
            "Lead Leg Bracing": {
                "description": "Stability of lead leg during cocking",
                "unit": "degrees knee extension variation",
                "optimal_range": (0, 3),
                "elite_threshold": 3,
                "warning_threshold": 8,
                "lower_is_better": True,
                "phase": "Arm Cocking"
            },
            "Glove Arm Action": {
                "description": "Position and movement of non-dominant arm",
                "unit": "degrees from optimal position",
                "optimal_range": (0, 5),  # Within 5° of ideal tucked position
                "elite_threshold": 5,
                "warning_threshold": 15,  # Flying open
                "lower_is_better": True,
                "phase": "Arm Cocking"
            },
            
            # ACCELERATION & RELEASE METRICS
            "Shoulder Internal Rotation Velocity": {
                "description": "Angular speed during acceleration",
                "unit": "degrees/second",
                "optimal_range": (7000, 8500),
                "elite_threshold": 8500,
                "warning_threshold": 6000,
                "lower_is_better": False,
                "phase": "Acceleration & Release"
            },
            "Elbow Extension Velocity": {
                "description": "Speed of elbow straightening",
                "unit": "degrees/second",
                "optimal_range": (2200, 2700),
                "elite_threshold": 2700,
                "warning_threshold": 1800,
                "lower_is_better": False,
                "phase": "Acceleration & Release"
            },
            "Release Point Consistency": {
                "description": "Variation in release position",
                "unit": "cm between pitches",
                "optimal_range": (0, 2),
                "elite_threshold": 2,
                "warning_threshold": 5,
                "lower_is_better": True,
                "phase": "Acceleration & Release"
            },
            "Arm Slot at Release": {
                "description": "Vertical angle of arm at release",
                "unit": "degrees SD between pitches",
                "optimal_range": (1, 2),
                "elite_threshold": 2,
                "warning_threshold": 4,
                "lower_is_better": True,
                "phase": "Acceleration & Release"
            },
            "Stride Length to Release Distance": {
                "description": "Distance from stride foot to release point",
                "unit": "percentage of height",
                "optimal_range": (85, 95),
                "elite_threshold": 95,
                "warning_threshold": 80,
                "lower_is_better": False,
                "phase": "Acceleration & Release"
            },
            "Trunk Stabilization": {
                "description": "Trunk acceleration deceleration",
                "unit": "degrees trunk position change post-FCP",
                "optimal_range": (0, 5),
                "elite_threshold": 5,
                "warning_threshold": 10,
                "lower_is_better": True,
                "phase": "Acceleration & Release"
            },
            "Hand Position at Release": {
                "description": "Orientation of hand and fingers",
                "unit": "degrees variation between pitches",
                "optimal_range": (1, 2),
                "elite_threshold": 2,
                "warning_threshold": 5,
                "lower_is_better": True,
                "phase": "Acceleration & Release"
            },
            "Release Point Height": {
                "description": "Height as percentage of pitcher's height",
                "unit": "percentage of height",
                "optimal_range": (78, 85),
                "elite_threshold": 85,
                "warning_threshold": 75,
                "lower_is_better": False,
                "phase": "Acceleration & Release"
            },
            
            # FOLLOW-THROUGH METRICS
            "Deceleration Path Efficiency": {
                "description": "Path of arm during deceleration",
                "unit": "degrees arc",
                "optimal_range": (60, 80),
                "elite_threshold": 80,
                "warning_threshold": 45,
                "lower_is_better": False,
                "phase": "Follow-through"
            },
            "Controlled Eccentricity": {
                "description": "Rate of arm deceleration",
                "unit": "percentage gradual slowdown",
                "optimal_range": (25, 35),
                "elite_threshold": 35,
                "warning_threshold": 50,
                "lower_is_better": False,
                "phase": "Follow-through"
            },
            "Balance Retention": {
                "description": "COM control during follow-through",
                "unit": "cm lateral displacement",
                "optimal_range": (0, 5),
                "elite_threshold": 5,
                "warning_threshold": 10,
                "lower_is_better": True,
                "phase": "Follow-through"
            },
            "Recovery Position Time": {
                "description": "Time to fielding-ready position",
                "unit": "seconds",
                "optimal_range": (0.3, 0.5),
                "elite_threshold": 0.5,
                "warning_threshold": 0.8,
                "lower_is_better": False,
                "phase": "Follow-through"
            },
            "Front Knee Control": {
                "description": "Stability of front leg during follow-through",
                "unit": "degrees controlled flexion",
                "optimal_range": (10, 20),
                "elite_threshold": 20,
                "warning_threshold": 30,
                "lower_is_better": False,
                "phase": "Follow-through"
            },
            "Rotational Completion": {
                "description": "Degree of body rotation completion",
                "unit": "degrees toward target",
                "optimal_range": (80, 100),
                "elite_threshold": 100,
                "warning_threshold": 70,
                "lower_is_better": False,
                "phase": "Follow-through"
            },
            "Head Position Tracking": {
                "description": "Head movement during follow-through",
                "unit": "cm vertical drop",
                "optimal_range": (0, 4),
                "elite_threshold": 4,
                "warning_threshold": 8,
                "lower_is_better": True,
                "phase": "Follow-through"
            },
            "Energy Dissipation Rate": {
                "description": "Gradual reduction in system energy",
                "unit": "percentage per 0.1s",
                "optimal_range": (30, 40),
                "elite_threshold": 40,
                "warning_threshold": 60,
                "lower_is_better": False,
                "phase": "Follow-through"
            },
            
            # INJURY RISK METRICS  
            "Shoulder Maximum External Rotation Risk": {
                "description": "Degree of external rotation (Risk Assessment)",
                "unit": "degrees",
                "optimal_range": (165, 185),
                "elite_threshold": 185,
                "warning_threshold": 195,
                "critical_threshold": 195,
                "lower_is_better": True,  # Fixed: Lower risk is better
                "phase": "Injury Risk",
                "risk_metric": True
            },
            "Elbow Valgus Torque": {
                "description": "Medial stress during cocking",
                "unit": "Nm",
                "optimal_range": (0, 40),
                "elite_threshold": 40,
                "warning_threshold": 55,
                "critical_threshold": 55,
                "lower_is_better": True,
                "phase": "Injury Risk",
                "risk_metric": True
            },
            "Lead Knee Extension Rate": {
                "description": "Rate of knee straightening",
                "unit": "degrees/second",
                "optimal_range": (0, 250),
                "elite_threshold": 250,
                "warning_threshold": 350,
                "critical_threshold": 350,
                "lower_is_better": True,
                "phase": "Injury Risk",
                "risk_metric": True
            },
            "Shoulder Horizontal Abduction": {
                "description": "Extreme layback position",
                "unit": "degrees at foot contact",
                "optimal_range": (0, 15),
                "elite_threshold": 15,
                "warning_threshold": 25,
                "critical_threshold": 25,
                "lower_is_better": True,
                "phase": "Injury Risk",
                "risk_metric": True
            },
            "Trunk Lateral Tilt Timing": {
                "description": "Early side-bending",
                "unit": "degrees before foot contact",
                "optimal_range": (0, 15),
                "elite_threshold": 15,
                "warning_threshold": 25,
                "critical_threshold": 25,
                "lower_is_better": True,
                "phase": "Injury Risk",
                "risk_metric": True
            },
            "Inverted W Position": {
                "description": "Elbow above shoulder with scapular loading",
                "unit": "severity score (0-10)",
                "optimal_range": (0, 2),  # Minimal presence
                "elite_threshold": 2,
                "warning_threshold": 5,  # Mild presence
                "critical_threshold": 8,  # Pronounced presence
                "lower_is_better": True,
                "phase": "Injury Risk",
                "risk_metric": True
            },
            "Deceleration Control": {
                "description": "Rate of arm slowdown post-release",
                "unit": "percentage per 0.1s",
                "optimal_range": (30, 60),  # Gradual is good
                "elite_threshold": 60,
                "warning_threshold": 80,
                "critical_threshold": 80,
                "lower_is_better": True,
                "phase": "Injury Risk",
                "risk_metric": True
            },
            "Premature Trunk Rotation": {
                "description": "Early upper body rotation",
                "unit": "percentage before foot contact",
                "optimal_range": (0, 30),
                "elite_threshold": 30,
                "warning_threshold": 50,
                "critical_threshold": 50,
                "lower_is_better": True,
                "phase": "Injury Risk",
                "risk_metric": True
            }
        })
        
        # AGE/SKILL-DEPENDENT METRICS
        self.adaptive_metrics = {
            # WINDUP PHASE METRICS
            "Knee Lift Height": {
                "description": "Hip flexion angle during leg lift", 
                "unit": "degrees",
                "phase": "Windup",
                "ranges": {
                    ("Youth (8-12)", "Beginner"): (45, 60),
                    ("Youth (8-12)", "Intermediate"): (50, 65),
                    ("Youth (8-12)", "Elite"): (55, 70),
                    ("Young Adult (13-25)", "Beginner"): (50, 65),
                    ("Young Adult (13-25)", "Intermediate"): (60, 75),
                    ("Young Adult (13-25)", "Elite"): (70, 90),
                    ("Adult (26-39)", "Beginner"): (55, 70),
                    ("Adult (26-39)", "Intermediate"): (65, 80),
                    ("Adult (26-39)", "Elite"): (75, 90),
                    ("Middle Age (40-55)", "Beginner"): (50, 65),
                    ("Middle Age (40-55)", "Intermediate"): (60, 75),
                    ("Middle Age (40-55)", "Elite"): (65, 80),
                    ("Masters (56+)", "Beginner"): (45, 60),
                    ("Masters (56+)", "Intermediate"): (50, 65),
                    ("Masters (56+)", "Elite"): (55, 70)
                }
            },
            "Balance Duration": {
                "description": "Time spent at peak knee lift",
                "unit": "seconds",
                "phase": "Windup",
                "ranges": {
                    ("Youth (8-12)", "Beginner"): (0.6, 0.8),
                    ("Youth (8-12)", "Intermediate"): (0.5, 0.7),
                    ("Youth (8-12)", "Elite"): (0.4, 0.6),
                    ("Young Adult (13-25)", "Beginner"): (0.5, 0.7),
                    ("Young Adult (13-25)", "Intermediate"): (0.4, 0.6),
                    ("Young Adult (13-25)", "Elite"): (0.3, 0.5),
                    ("Adult (26-39)", "Beginner"): (0.5, 0.7),
                    ("Adult (26-39)", "Intermediate"): (0.4, 0.6),
                    ("Adult (26-39)", "Elite"): (0.3, 0.5),
                    ("Middle Age (40-55)", "Beginner"): (0.6, 0.8),
                    ("Middle Age (40-55)", "Intermediate"): (0.5, 0.7),
                    ("Middle Age (40-55)", "Elite"): (0.4, 0.6),
                    ("Masters (56+)", "Beginner"): (0.7, 0.9),
                    ("Masters (56+)", "Intermediate"): (0.6, 0.8),
                    ("Masters (56+)", "Elite"): (0.5, 0.7)
                }
            },
            "Trunk Rotation": {
                "description": "Initial rotation away from home plate",
                "unit": "degrees",
                "phase": "Windup",
                "ranges": {
                    ("Youth (8-12)", "Beginner"): (0, 5),
                    ("Youth (8-12)", "Intermediate"): (0, 10),
                    ("Youth (8-12)", "Elite"): (5, 15),
                    ("Young Adult (13-25)", "Beginner"): (0, 10),
                    ("Young Adult (13-25)", "Intermediate"): (5, 15),
                    ("Young Adult (13-25)", "Elite"): (10, 20),
                    ("Adult (26-39)", "Beginner"): (5, 15),
                    ("Adult (26-39)", "Intermediate"): (10, 20),
                    ("Adult (26-39)", "Elite"): (15, 25),
                    ("Middle Age (40-55)", "Beginner"): (0, 10),
                    ("Middle Age (40-55)", "Intermediate"): (5, 15),
                    ("Middle Age (40-55)", "Elite"): (10, 20),
                    ("Masters (56+)", "Beginner"): (0, 5),
                    ("Masters (56+)", "Intermediate"): (0, 10),
                    ("Masters (56+)", "Elite"): (5, 15)
                }
            },
            "Weight Distribution Windup": {
                "description": "Percentage on back leg during windup",
                "unit": "percentage",
                "phase": "Windup",
                "ranges": {
                    ("Youth (8-12)", "Beginner"): (85, 95),
                    ("Youth (8-12)", "Intermediate"): (85, 90),
                    ("Youth (8-12)", "Elite"): (80, 90),
                    ("Young Adult (13-25)", "Beginner"): (85, 90),
                    ("Young Adult (13-25)", "Intermediate"): (80, 90),
                    ("Young Adult (13-25)", "Elite"): (80, 85),
                    ("Adult (26-39)", "Beginner"): (80, 90),
                    ("Adult (26-39)", "Intermediate"): (80, 85),
                    ("Adult (26-39)", "Elite"): (75, 85),
                    ("Middle Age (40-55)", "Beginner"): (85, 90),
                    ("Middle Age (40-55)", "Intermediate"): (80, 90),
                    ("Middle Age (40-55)", "Elite"): (80, 85),
                    ("Masters (56+)", "Beginner"): (85, 95),
                    ("Masters (56+)", "Intermediate"): (85, 90),
                    ("Masters (56+)", "Elite"): (80, 90)
                }
            },
            
            # STRIDE PHASE METRICS
            "Stride Length Adaptive": {
                "description": "Distance as percentage of pitcher's height",
                "unit": "percentage of height",
                "phase": "Stride",
                "ranges": {
                    ("Youth (8-12)", "Beginner"): (60, 65),
                    ("Youth (8-12)", "Intermediate"): (65, 70),
                    ("Youth (8-12)", "Elite"): (68, 73),
                    ("Young Adult (13-25)", "Beginner"): (65, 70),
                    ("Young Adult (13-25)", "Intermediate"): (70, 80),
                    ("Young Adult (13-25)", "Elite"): (78, 88),
                    ("Adult (26-39)", "Beginner"): (70, 75),
                    ("Adult (26-39)", "Intermediate"): (75, 85),
                    ("Adult (26-39)", "Elite"): (80, 90),
                    ("Middle Age (40-55)", "Beginner"): (65, 75),
                    ("Middle Age (40-55)", "Intermediate"): (70, 80),
                    ("Middle Age (40-55)", "Elite"): (75, 85),
                    ("Masters (56+)", "Beginner"): (60, 70),
                    ("Masters (56+)", "Intermediate"): (65, 75),
                    ("Masters (56+)", "Elite"): (70, 80)
                }
            },
            "Stride Direction Adaptive": {
                "description": "Angle toward or away from centerline",
                "unit": "degrees closed",
                "phase": "Stride",
                "ranges": {
                    ("Youth (8-12)", "Beginner"): (5, 10),
                    ("Youth (8-12)", "Intermediate"): (3, 8),
                    ("Youth (8-12)", "Elite"): (2, 7),
                    ("Young Adult (13-25)", "Beginner"): (3, 8),
                    ("Young Adult (13-25)", "Intermediate"): (2, 7),
                    ("Young Adult (13-25)", "Elite"): (0, 5),
                    ("Adult (26-39)", "Beginner"): (3, 8),
                    ("Adult (26-39)", "Intermediate"): (2, 7),
                    ("Adult (26-39)", "Elite"): (0, 5),
                    ("Middle Age (40-55)", "Beginner"): (3, 8),
                    ("Middle Age (40-55)", "Intermediate"): (2, 7),
                    ("Middle Age (40-55)", "Elite"): (0, 5),
                    ("Masters (56+)", "Beginner"): (5, 10),
                    ("Masters (56+)", "Intermediate"): (3, 8),
                    ("Masters (56+)", "Elite"): (2, 7)
                }
            },
            "Knee Flexion at Peak": {
                "description": "Degree of lead knee bend during stride",
                "unit": "degrees",
                "phase": "Stride", 
                "ranges": {
                    ("Youth (8-12)", "Beginner"): (45, 55),
                    ("Youth (8-12)", "Intermediate"): (42, 52),
                    ("Youth (8-12)", "Elite"): (40, 50),
                    ("Young Adult (13-25)", "Beginner"): (43, 53),
                    ("Young Adult (13-25)", "Intermediate"): (40, 50),
                    ("Young Adult (13-25)", "Elite"): (37, 47),
                    ("Adult (26-39)", "Beginner"): (42, 52),
                    ("Adult (26-39)", "Intermediate"): (38, 48),
                    ("Adult (26-39)", "Elite"): (35, 45),
                    ("Middle Age (40-55)", "Beginner"): (43, 53),
                    ("Middle Age (40-55)", "Intermediate"): (40, 50),
                    ("Middle Age (40-55)", "Elite"): (38, 48),
                    ("Masters (56+)", "Beginner"): (45, 55),
                    ("Masters (56+)", "Intermediate"): (43, 53),
                    ("Masters (56+)", "Elite"): (40, 50)
                }
            },
            "Hip-Shoulder Separation at Foot Contact": {
                "description": "Rotational difference at foot contact",
                "unit": "degrees",
                "phase": "Stride",
                "ranges": {
                    ("Youth (8-12)", "Beginner"): (15, 20),
                    ("Youth (8-12)", "Intermediate"): (18, 23),
                    ("Youth (8-12)", "Elite"): (20, 25),
                    ("Young Adult (13-25)", "Beginner"): (20, 25),
                    ("Young Adult (13-25)", "Intermediate"): (25, 30),
                    ("Young Adult (13-25)", "Elite"): (30, 40),
                    ("Adult (26-39)", "Beginner"): (25, 30),
                    ("Adult (26-39)", "Intermediate"): (30, 40),
                    ("Adult (26-39)", "Elite"): (40, 50),
                    ("Middle Age (40-55)", "Beginner"): (20, 25),
                    ("Middle Age (40-55)", "Intermediate"): (25, 35),
                    ("Middle Age (40-55)", "Elite"): (30, 40),
                    ("Masters (56+)", "Beginner"): (15, 20),
                    ("Masters (56+)", "Intermediate"): (20, 30),
                    ("Masters (56+)", "Elite"): (25, 35)
                }
            },
            
            # ARM COCKING PHASE METRICS
            "Shoulder External Rotation Adaptive": {
                "description": "Maximum angle of shoulder external rotation",
                "unit": "degrees",
                "phase": "Arm Cocking",
                "ranges": {
                    ("Youth (8-12)", "Beginner"): (145, 155),
                    ("Youth (8-12)", "Intermediate"): (150, 160),
                    ("Youth (8-12)", "Elite"): (155, 165),
                    ("Young Adult (13-25)", "Beginner"): (150, 160),
                    ("Young Adult (13-25)", "Intermediate"): (160, 170),
                    ("Young Adult (13-25)", "Elite"): (165, 180),
                    ("Adult (26-39)", "Beginner"): (155, 165),
                    ("Adult (26-39)", "Intermediate"): (165, 175),
                    ("Adult (26-39)", "Elite"): (170, 185),
                    ("Middle Age (40-55)", "Beginner"): (150, 160),
                    ("Middle Age (40-55)", "Intermediate"): (160, 170),
                    ("Middle Age (40-55)", "Elite"): (165, 175),
                    ("Masters (56+)", "Beginner"): (145, 155),
                    ("Masters (56+)", "Intermediate"): (150, 160),
                    ("Masters (56+)", "Elite"): (155, 165)
                }
            },
            "Ball Velocity": {
                "description": "Speed at release",
                "unit": "mph",
                "phase": "Performance",
                "ranges": {
                    ("Youth (8-12)", "Beginner"): (35, 45),
                    ("Youth (8-12)", "Intermediate"): (45, 55),
                    ("Youth (8-12)", "Elite"): (55, 65),
                    ("Young Adult (13-25)", "Beginner"): (50, 65),
                    ("Young Adult (13-25)", "Intermediate"): (65, 80),
                    ("Young Adult (13-25)", "Elite"): (80, 95),
                    ("Adult (26-39)", "Beginner"): (60, 75),
                    ("Adult (26-39)", "Intermediate"): (75, 90),
                    ("Adult (26-39)", "Elite"): (90, 100),
                    ("Middle Age (40-55)", "Beginner"): (55, 70),
                    ("Middle Age (40-55)", "Intermediate"): (70, 85),
                    ("Middle Age (40-55)", "Elite"): (85, 95),
                    ("Masters (56+)", "Beginner"): (50, 60),
                    ("Masters (56+)", "Intermediate"): (60, 75),
                    ("Masters (56+)", "Elite"): (75, 85)
                }
            },
            "Spin Rate": {
                "description": "Ball rotation",
                "unit": "rpm",
                "phase": "Performance",
                "ranges": {
                    ("Youth (8-12)", "Beginner"): (1000, 1400),
                    ("Youth (8-12)", "Intermediate"): (1200, 1600),
                    ("Youth (8-12)", "Elite"): (1400, 1800),
                    ("Young Adult (13-25)", "Beginner"): (1300, 1700),
                    ("Young Adult (13-25)", "Intermediate"): (1600, 2000),
                    ("Young Adult (13-25)", "Elite"): (1900, 2400),
                    ("Adult (26-39)", "Beginner"): (1500, 1900),
                    ("Adult (26-39)", "Intermediate"): (1800, 2200),
                    ("Adult (26-39)", "Elite"): (2100, 2500),
                    ("Middle Age (40-55)", "Beginner"): (1400, 1800),
                    ("Middle Age (40-55)", "Intermediate"): (1700, 2100),
                    ("Middle Age (40-55)", "Elite"): (2000, 2400),
                    ("Masters (56+)", "Beginner"): (1300, 1700),
                    ("Masters (56+)", "Intermediate"): (1600, 2000),
                    ("Masters (56+)", "Elite"): (1800, 2200)
                }
            }
        }
    
    def select_metric_type(self):
        """Let user choose between fixed and adaptive metrics"""
        print("\n" + "="*80)
        print("🥎 SIGHTFX BASEBALL PITCHING METRICS CALCULATOR")
        print("="*80)
        print("\nChoose your analysis type:")
        print("\n1. 📊 STANDARD METRICS")
        print("   - Fixed elite adult standards")
        print("   - Comprehensive biomechanical analysis")
        print("   - 54+ professional-level metrics")
        print("   - Injury risk assessments")
        print("   - Pitch-specific analysis")
        print("   - Kinetic chain efficiency")
        
        print("\n2. 🎯 ADAPTIVE METRICS")
        print("   - Age and skill-level specific ranges")
        print("   - Personalized development targets")
        print("   - Appropriate expectations by profile")
        print("   - 15+ core developmental metrics")
        
        while True:
            try:
                choice = int(input("\nSelect analysis type (1 or 2): "))
                if choice in [1, 2]:
                    return choice
                else:
                    print("❌ Please select 1 or 2")
            except ValueError:
                print("❌ Please enter a valid number")
    
    def get_user_profile(self):
        """Get user's age group and skill level for adaptive metrics"""
        print("\n" + "="*60)
        print("PITCHER PROFILE SETUP")
        print("="*60)
        
        print("\nSelect your age group:")
        for key, value in self.age_groups.items():
            print(f"{key}. {value}")
        
        while True:
            try:
                age_choice = int(input("\nEnter age group (1-5): "))
                if age_choice in self.age_groups:
                    selected_age = self.age_groups[age_choice]
                    break
                else:
                    print("❌ Please select a valid age group (1-5)")
            except ValueError:
                print("❌ Please enter a valid number")
        
        print(f"\nSelect your skill level:")
        for key, value in self.skill_levels.items():
            print(f"{key}. {value}")
        
        while True:
            try:
                skill_choice = int(input("\nEnter skill level (1-3): "))
                if skill_choice in self.skill_levels:
                    selected_skill = self.skill_levels[skill_choice]
                    break
                else:
                    print("❌ Please select a valid skill level (1-3)")
            except ValueError:
                print("❌ Please enter a valid number")
        
        return selected_age, selected_skill
    
    def display_fixed_metrics_menu(self):
        """Display fixed metrics organized by phase"""
        print(f"\n" + "="*80)
        print("STANDARD METRICS - ELITE ADULT STANDARDS")
        print("="*80)
        
        # Group metrics by phase
        phases = {}
        for metric_name, metric_data in self.fixed_metrics.items():
            phase = metric_data["phase"]
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(metric_name)
        
        metric_count = 1
        metric_map = {}
        
        for phase, metrics in phases.items():
            print(f"\n{phase.upper()} METRICS:")
            print("-" * (len(phase) + 9))
            for metric in metrics:
                metric_info = self.fixed_metrics[metric]
                range_min, range_max = metric_info["optimal_range"]
                unit = metric_info["unit"]
                print(f"{metric_count:2d}. {metric}")
                print(f"    Optimal: {range_min}-{range_max} {unit}")
                metric_map[metric_count] = metric
                metric_count += 1
        
        print(f"\n{metric_count}. Change Analysis Type")
        print(f"{metric_count + 1}. Exit Program")
        return metric_map, metric_count
    
    def display_adaptive_metrics_menu(self, age_group, skill_level):
        """Display adaptive metrics organized by phase"""
        print(f"\n" + "="*80)
        print(f"ADAPTIVE METRICS - {age_group} {skill_level}")
        print("="*80)
        
        # Group metrics by phase
        phases = {}
        for metric_name, metric_data in self.adaptive_metrics.items():
            phase = metric_data["phase"]
            if phase not in phases:
                phases[phase] = []
            phases[phase].append(metric_name)
        
        metric_count = 1
        metric_map = {}
        
        for phase, metrics in phases.items():
            print(f"\n{phase.upper()} METRICS:")
            print("-" * (len(phase) + 9))
            for metric in metrics:
                # Show the optimal range for this user's profile
                key = (age_group, skill_level)
                if key in self.adaptive_metrics[metric]["ranges"]:
                    range_min, range_max = self.adaptive_metrics[metric]["ranges"][key]
                    unit = self.adaptive_metrics[metric]["unit"]
                    print(f"{metric_count:2d}. {metric}")
                    print(f"    Optimal: {range_min}-{range_max} {unit}")
                    metric_map[metric_count] = metric
                    metric_count += 1
        
        print(f"\n{metric_count}. Change Profile")
        print(f"{metric_count + 1}. Change Analysis Type")
        print(f"{metric_count + 2}. Exit Program")
        return metric_map, metric_count
    
    def calculate_fixed_score(self, metric_name, value):
        """Calculate score for fixed metrics with special handling for injury risk"""
        metric = self.fixed_metrics[metric_name]
        optimal_min, optimal_max = metric["optimal_range"]
        elite_threshold = metric["elite_threshold"]
        warning_threshold = metric["warning_threshold"]
        lower_is_better = metric["lower_is_better"]
        is_risk_metric = metric.get("risk_metric", False)
        
        # Special handling for injury risk metrics
        if is_risk_metric:
            critical_threshold = metric.get("critical_threshold", warning_threshold)
            
            # For injury risk: lower values = better scores
            if value <= optimal_max:
                return 100  # Safe range
            elif value <= elite_threshold:
                # Slight risk - score 75-99
                progress = (value - optimal_max) / (elite_threshold - optimal_max)
                return max(75, 100 - (progress * 25))
            elif value <= warning_threshold:
                # Moderate risk - score 25-74
                progress = (value - elite_threshold) / (warning_threshold - elite_threshold)
                return max(25, 75 - (progress * 50))
            else:
                # Critical risk - score 0-24
                excess = min(value - warning_threshold, warning_threshold)
                return max(0, 25 - (excess / warning_threshold) * 25)
        
        # Original logic for non-risk metrics
        # Perfect score (100) for values in optimal range
        if optimal_min <= value <= optimal_max:
            return 100
        
        # Calculate score based on distance from optimal range
        if lower_is_better:
            if value <= optimal_max:
                return 100
            elif value <= elite_threshold:
                # Linear decrease from 100 to 85
                return max(85, 100 - ((value - optimal_max) / (elite_threshold - optimal_max)) * 15)
            elif value <= warning_threshold:
                # Linear decrease from 85 to 50
                return max(50, 85 - ((value - elite_threshold) / (warning_threshold - elite_threshold)) * 35)
            else:
                # Below 50 for values beyond warning threshold
                excess = value - warning_threshold
                return max(0, 50 - (excess / warning_threshold) * 50)
        else:
            if value >= optimal_min:
                return 100
            elif value >= warning_threshold:
                # Linear decrease from 100 to 50 based on distance from optimal
                if value < optimal_min:
                    distance_from_optimal = optimal_min - value
                    max_distance = optimal_min - warning_threshold
                    score = 100 - (distance_from_optimal / max_distance) * 50
                    return max(50, score)
                return 100
            else:
                # Below 50 for values below warning threshold
                deficit = warning_threshold - value
                return max(0, 50 - (deficit / warning_threshold) * 50)
    
    def calculate_adaptive_score(self, metric_name, value, age_group, skill_level):
        """Calculate score for adaptive metrics"""
        metric = self.adaptive_metrics[metric_name]
        key = (age_group, skill_level)
        
        if key not in metric["ranges"]:
            return 0, "Profile not supported for this metric"
        
        optimal_min, optimal_max = metric["ranges"][key]
        
        # Perfect score (100) for values in optimal range
        if optimal_min <= value <= optimal_max:
            return 100, "Perfect - within optimal range"
        
        # Calculate distance from optimal range
        if value < optimal_min:
            distance = optimal_min - value
            range_size = optimal_max - optimal_min
            # Score decreases based on how far below optimal
            score = max(0, 100 - (distance / range_size) * 100)
        else:  # value > optimal_max
            distance = value - optimal_max
            range_size = optimal_max - optimal_min
            # Score decreases based on how far above optimal
            score = max(0, 100 - (distance / range_size) * 100)
        
        return score, self.get_score_interpretation(score)[0]
    
    def get_score_interpretation(self, score, is_risk_metric=False):
        """Get interpretation and emoji for score"""
        if is_risk_metric:
            # For injury risk metrics, interpretation is different
            if score >= 90:
                return "SAFE", "🟢"
            elif score >= 75:
                return "LOW RISK", "🟡"
            elif score >= 25:
                return "MODERATE RISK", "🟠"
            else:
                return "HIGH RISK", "🔴"
        else:
            # Normal performance metrics
            if score >= 90:
                return "ELITE", "🟢"
            elif score >= 75:
                return "GOOD", "🟡"
            elif score >= 50:
                return "NEEDS IMPROVEMENT", "🟠"
            else:
                return "CRITICAL ISSUE", "🔴"
    
    def run_fixed_metrics(self):
        """Run fixed metrics analysis"""
        while True:
            metric_map, last_metric_num = self.display_fixed_metrics_menu()
            
            try:
                choice = int(input(f"\nSelect an option (1-{last_metric_num + 1}): "))
                
                if choice == last_metric_num + 1:  # Exit
                    return "exit"
                elif choice == last_metric_num:  # Change analysis type
                    return "change_type"
                
                if choice not in metric_map:
                    print("❌ Invalid selection. Please try again.")
                    continue
                
                selected_metric = metric_map[choice]
                metric_info = self.fixed_metrics[selected_metric]
                optimal_min, optimal_max = metric_info["optimal_range"]
                
                print(f"\n" + "="*70)
                print(f"SELECTED METRIC: {selected_metric}")
                print("="*70)
                print(f"Phase: {metric_info['phase']}")
                print(f"Description: {metric_info['description']}")
                print(f"Unit: {metric_info['unit']}")
                print(f"Optimal Range: {optimal_min}-{optimal_max} {metric_info['unit']}")
                print(f"Elite Threshold: {'≤' if metric_info['lower_is_better'] else '≥'}{metric_info['elite_threshold']} {metric_info['unit']}")
                
                # Get user input
                while True:
                    try:
                        user_value = float(input(f"\nEnter your measured value ({metric_info['unit']}): "))
                        break
                    except ValueError:
                        print("❌ Please enter a valid number.")
                
                # Calculate score
                score = self.calculate_fixed_score(selected_metric, user_value)
                is_risk_metric = metric_info.get("risk_metric", False)
                interpretation, emoji = self.get_score_interpretation(score, is_risk_metric)
                
                # Display results
                print(f"\n" + "="*70)
                print("RESULTS")
                print("="*70)
                print(f"Measured Value: {user_value} {metric_info['unit']}")
                print(f"Score: {score:.1f}/100")
                print(f"Rating: {interpretation} {emoji}")
                
                # Provide specific feedback based on metric type
                if is_risk_metric:
                    # Special feedback for injury risk metrics
                    if score >= 90:
                        print("✅ Safe! Your value is within the low-risk range.")
                    elif score >= 75:
                        print("⚠️  Low risk, but monitor this metric closely.")
                        print(f"🎯 Optimal: Stay within {optimal_min}-{optimal_max} {metric_info['unit']}")
                    elif score >= 25:
                        print("🚨 MODERATE INJURY RISK - Immediate attention needed!")
                        print(f"🎯 Priority: Reduce to below {metric_info['elite_threshold']} {metric_info['unit']}")
                    else:
                        print("🚨🚨 HIGH INJURY RISK - CRITICAL! Seek professional evaluation!")
                        print(f"🎯 URGENT: Must reduce to below {metric_info['warning_threshold']} {metric_info['unit']}")
                else:
                    # Original feedback for performance metrics
                    if score == 100:
                        print("✅ Excellent! Your value is within the elite optimal range.")
                    elif score >= 85:
                        print("👍 Good performance, close to elite level.")
                    elif score >= 50:
                        if metric_info['lower_is_better']:
                            print(f"⚠️  Consider working to reduce this value. Target: ≤{optimal_max} {metric_info['unit']}")
                        else:
                            print(f"⚠️  Consider working to increase this value. Target: ≥{optimal_min} {metric_info['unit']}")
                    else:
                        print("🚨 This metric indicates a significant area for improvement.")
                        if metric_info['lower_is_better']:
                            print(f"🎯 Priority: Reduce to ≤{metric_info['elite_threshold']} {metric_info['unit']}")
                        else:
                            print(f"🎯 Priority: Increase to ≥{metric_info['warning_threshold']} {metric_info['unit']}")
                
                input("\nPress Enter to continue...")
                
            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\nExiting program...")
                return "exit"
    
    def run_adaptive_metrics(self):
        """Run adaptive metrics analysis"""
        # Get user profile
        age_group, skill_level = self.get_user_profile()
        
        while True:
            metric_map, last_metric_num = self.display_adaptive_metrics_menu(age_group, skill_level)
            
            try:
                choice = int(input(f"\nSelect an option (1-{last_metric_num + 2}): "))
                
                if choice == last_metric_num + 2:  # Exit
                    return "exit"
                elif choice == last_metric_num + 1:  # Change analysis type
                    return "change_type"
                elif choice == last_metric_num:  # Change profile
                    age_group, skill_level = self.get_user_profile()
                    continue
                
                if choice not in metric_map:
                    print("❌ Invalid selection. Please try again.")
                    continue
                
                selected_metric = metric_map[choice]
                metric_info = self.adaptive_metrics[selected_metric]
                key = (age_group, skill_level)
                
                if key not in metric_info["ranges"]:
                    print("❌ This metric is not available for your age/skill profile.")
                    continue
                
                optimal_min, optimal_max = metric_info["ranges"][key]
                
                print(f"\n" + "="*70)
                print(f"SELECTED METRIC: {selected_metric}")
                print("="*70)
                print(f"Phase: {metric_info['phase']}")
                print(f"Description: {metric_info['description']}")
                print(f"Unit: {metric_info['unit']}")
                print(f"Your Profile: {age_group} - {skill_level}")
                print(f"Optimal Range: {optimal_min}-{optimal_max} {metric_info['unit']}")
                
                # Get user input
                while True:
                    try:
                        user_value = float(input(f"\nEnter your measured value ({metric_info['unit']}): "))
                        break
                    except ValueError:
                        print("❌ Please enter a valid number.")
                
                # Calculate score
                score, interpretation = self.calculate_adaptive_score(selected_metric, user_value, age_group, skill_level)
                _, emoji = self.get_score_interpretation(score)
                
                # Display results
                print(f"\n" + "="*70)
                print("RESULTS")
                print("="*70)
                print(f"Measured Value: {user_value} {metric_info['unit']}")
                print(f"Score: {score:.1f}/100")
                print(f"Rating: {interpretation} {emoji}")
                
                # Provide specific feedback
                if score == 100:
                    print("✅ Excellent! Your value is within the optimal range for your profile.")
                elif score >= 75:
                    print("👍 Good performance for your age and skill level.")
                    if user_value < optimal_min:
                        print(f"💡 To reach elite level, work to increase to at least {optimal_min} {metric_info['unit']}")
                    else:
                        print(f"💡 To reach elite level, work to decrease to no more than {optimal_max} {metric_info['unit']}")
                elif score >= 50:
                    print("⚠️  This metric shows room for improvement.")
                    if user_value < optimal_min:
                        print(f"🎯 Target: Increase to {optimal_min}-{optimal_max} {metric_info['unit']}")
                    else:
                        print(f"🎯 Target: Reduce to {optimal_min}-{optimal_max} {metric_info['unit']}")
                else:
                    print("🚨 This metric indicates a significant area needing attention.")
                    print(f"🎯 Priority: Work toward {optimal_min}-{optimal_max} {metric_info['unit']}")
                
                # Show comparison to other skill levels
                print(f"\n📊 COMPARISON ACROSS SKILL LEVELS:")
                for level in ["Beginner", "Intermediate", "Elite"]:
                    comp_key = (age_group, level)
                    if comp_key in metric_info["ranges"]:
                        comp_min, comp_max = metric_info["ranges"][comp_key]
                        marker = "👈 YOU" if level == skill_level else ""
                        print(f"   {level}: {comp_min}-{comp_max} {metric_info['unit']} {marker}")
                
                input("\nPress Enter to continue...")
                
            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\nExiting program...")
                return "exit"
    
    def run_calculator(self):
        """Main program loop"""
        print("🥎 Welcome to SightFX Baseball Pitching Metrics Calculator!")
        print("Choose between standard elite metrics or age/skill-adaptive analysis.")
        
        while True:
            metric_type = self.select_metric_type()
            
            if metric_type == 1:  # Fixed metrics
                result = self.run_fixed_metrics()
            else:  # Adaptive metrics
                result = self.run_adaptive_metrics()
            
            if result == "exit":
                print("\n🙏 Thank you for using SightFX Metrics Calculator!")
                break
            elif result == "change_type":
                continue  # Go back to type selection

# Run the calculator
if __name__ == "__main__":
    calculator = SightFXMetricsCalculator()
    calculator.run_calculator()