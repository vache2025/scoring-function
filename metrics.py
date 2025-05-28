import math
from enum import Enum
from typing import Dict, Optional, List, Any

# --- Constants ---
MIN_SCORE_VALUE = 1.0  # The minimum score any metric can receive.


# --- Enums for Score Types ---
class ScoreType(Enum):
    OPTIMAL_RANGE = "optimal_range"  # Score 100 within optimal range, scales to min_score_value outside defined bad thresholds.
    LOWER_IS_BETTER = "lower_is_better"  # Score 100 up to optimal_upper_bound, scales to min_score_value at/above poor_threshold.
    HIGHER_IS_BETTER = "higher_is_better"  # Score 100 at/above optimal_lower_bound, scales from min_score_value at 0.
    INJURY_RISK = "injury_risk"  # Score 100 below warning_threshold, scales to min_score_value at/above critical_threshold.


class MetricInfo:
    """
    Defines the properties, scoring logic type, and hardcoded parameters for a single biomechanical metric.
    """

    def __init__(self, name: str, unit: str, score_type: ScoreType, description: str, default_params: Dict[str, float]):
        self.name = name
        self.unit = unit
        self.score_type = score_type
        self.description = description
        self.default_params = default_params

    def calculate_score(self, value: float) -> float:
        """
        Calculates the score (MIN_SCORE_VALUE-100) for the given metric value using its hardcoded parameters.
        No score will ever literally be 0; it will be floored at MIN_SCORE_VALUE.
        """
        score = 0.0
        params = self.default_params # Use the hardcoded parameters for this metric

        if self.score_type == ScoreType.OPTIMAL_RANGE:
            optimal_min = params.get('optimal_min')
            optimal_max = params.get('optimal_max')
            bad_low_threshold = params.get('bad_low_threshold')
            bad_high_threshold = params.get('bad_high_threshold')

            # Basic validation
            if any(p is None for p in [optimal_min, optimal_max]):
                raise ValueError(f"Missing mandatory parameters for OPTIMAL_RANGE. Requires optimal_min, optimal_max.")
            if not (optimal_min <= optimal_max):
                raise ValueError(f"Invalid optimal range: optimal_min ({optimal_min}) cannot be greater than optimal_max ({optimal_max}).")

            # Determine actual falloff thresholds, using defaults if not explicitly provided
            final_bad_low_threshold = bad_low_threshold if bad_low_threshold is not None else (0.0 if optimal_min > 0 else optimal_min - (optimal_max - optimal_min))
            final_bad_high_threshold = bad_high_threshold if bad_high_threshold is not None else (100.0 if self.unit == '%' else (optimal_max * 2.0 if optimal_max > 0 else optimal_max + (optimal_max - optimal_min)))

            # Further validation for the effective thresholds
            if not (final_bad_low_threshold < optimal_min):
                 raise ValueError(f"Calculated bad_low_threshold ({final_bad_low_threshold}) is not less than optimal_min ({optimal_min}). Check parameters or defaults.")
            if not (optimal_max < final_bad_high_threshold):
                 raise ValueError(f"Calculated bad_high_threshold ({final_bad_high_threshold}) is not greater than optimal_max ({optimal_max}). Check parameters or defaults.")


            if optimal_min <= value <= optimal_max:
                score = 100.0
            elif value < optimal_min:
                if value <= final_bad_low_threshold:
                    score = MIN_SCORE_VALUE
                else:
                    # Linear scale from MIN_SCORE_VALUE at final_bad_low_threshold to 100 at optimal_min
                    score = MIN_SCORE_VALUE + ((value - final_bad_low_threshold) / (optimal_min - final_bad_low_threshold)) * (100.0 - MIN_SCORE_VALUE)
                    score = max(MIN_SCORE_VALUE, score) # Ensure it doesn't go below MIN_SCORE_VALUE
            elif value > optimal_max:
                if value >= final_bad_high_threshold:
                    score = MIN_SCORE_VALUE
                else:
                    # Linear scale from 100 at optimal_max to MIN_SCORE_VALUE at final_bad_high_threshold
                    score = 100.0 - ((value - optimal_max) / (final_bad_high_threshold - optimal_max)) * (100.0 - MIN_SCORE_VALUE)
                    score = max(MIN_SCORE_VALUE, score) # Ensure it doesn't go below MIN_SCORE_VALUE

        elif self.score_type == ScoreType.LOWER_IS_BETTER:
            optimal_upper_bound = params.get('optimal_upper_bound')
            poor_threshold = params.get('poor_threshold')

            if any(p is None for p in [optimal_upper_bound, poor_threshold]):
                raise ValueError(f"Missing parameters for LOWER_IS_BETTER. Requires optimal_upper_bound, poor_threshold.")
            if not (0 <= optimal_upper_bound < poor_threshold): # Added constraint for logical bounds
                 raise ValueError(f"Invalid parameters for LOWER_IS_BETTER. optimal_upper_bound ({optimal_upper_bound}) must be non-negative and strictly less than poor_threshold ({poor_threshold}).")

            if value <= optimal_upper_bound:
                score = 100.0
            elif value >= poor_threshold:
                score = MIN_SCORE_VALUE
            else:
                # Linearly scale from 100 at optimal_upper_bound to MIN_SCORE_VALUE at poor_threshold
                score = 100.0 - ((value - optimal_upper_bound) / (poor_threshold - optimal_upper_bound)) * (100.0 - MIN_SCORE_VALUE)
                score = max(MIN_SCORE_VALUE, score) # Cap at MIN_SCORE_VALUE

        elif self.score_type == ScoreType.HIGHER_IS_BETTER:
            optimal_lower_bound = params.get('optimal_lower_bound') # Renamed from target_value for consistency

            if optimal_lower_bound is None or optimal_lower_bound <= 0:
                raise ValueError(f"Missing or invalid optimal_lower_bound for HIGHER_IS_BETTER. Requires optimal_lower_bound > 0.")

            if value >= optimal_lower_bound:
                score = 100.0
            else:
                if value <= 0:
                    score = MIN_SCORE_VALUE
                else:
                    score = (value / optimal_lower_bound) * 100.0
                    score = max(MIN_SCORE_VALUE, score) # Cap at MIN_SCORE_VALUE

        elif self.score_type == ScoreType.INJURY_RISK:
            warning_threshold = params.get('warning_threshold')
            critical_threshold = params.get('critical_threshold')
            if any(p is None for p in [warning_threshold, critical_threshold]):
                raise ValueError(f"Missing parameters for INJURY_RISK. Requires warning_threshold, critical_threshold.")

            # For INJURY_RISK, it's assumed that 'higher value means higher risk'.
            # So, warning_threshold < critical_threshold for linear scaling.
            if warning_threshold >= critical_threshold: # Sanity check for thresholds
                score = 100.0 if value <= warning_threshold else MIN_SCORE_VALUE
            else:
                if value <= warning_threshold:
                    score = 100.0
                elif value >= critical_threshold:
                    score = MIN_SCORE_VALUE
                else:
                    # Linear drop from 100 at warning to MIN_SCORE_VALUE at critical
                    score = 100.0 - (value - warning_threshold) / (critical_threshold - warning_threshold) * (
                                100.0 - MIN_SCORE_VALUE)
                    score = max(MIN_SCORE_VALUE, score) # Ensure it doesn't go below MIN_SCORE_VALUE

        return round(score, 1)


ALL_METRICS: Dict[str, MetricInfo] = {}


# Helper function to add a metric to the global dictionary
def add_metric(metric_def: MetricInfo):
    ALL_METRICS[metric_def.name] = metric_def


# --- Populating ALL_METRICS with parameters derived from pitch.md (Adult Elite values) ---

# 1. WINDUP PHASE METRICS
add_metric(MetricInfo("Knee Lift Height", "°", ScoreType.OPTIMAL_RANGE,
                      "Hip flexion angle of lead knee at peak lift. Higher is generally better for load.",
                      {'optimal_min': 45.0, 'optimal_max': 90.0})) # No explicit bad_high_threshold
add_metric(MetricInfo("Balance Duration", "s", ScoreType.OPTIMAL_RANGE,
                      "Time spent at peak knee lift. Optimal is generally shorter for elite, suggesting quick rhythm.",
                      {'optimal_min': 0.3, 'optimal_max': 0.9, 'bad_high_threshold': 0.8})) # No explicit bad_low_threshold (assumes 0.0)
add_metric(MetricInfo("Trunk Rotation (Windup)", "°", ScoreType.OPTIMAL_RANGE,
                      "Initial rotation away from home plate during windup. Allows for counter-rotation.",
                      {'optimal_min': 15.0, 'optimal_max': 25.0, 'bad_high_threshold': 30.0})) # No explicit bad_low_threshold (assumes 0.0)
add_metric(MetricInfo("Weight Distribution (Windup)", "% Back", ScoreType.OPTIMAL_RANGE,
                      "Percentage of weight on back leg at maximum knee lift. Critical for momentum generation.",
                      {'optimal_min': 75.0, 'optimal_max': 85.0, 'bad_low_threshold': 80.0, 'bad_high_threshold': 100.0})) # '<80%' is common error, but optimal is 75-85%. Adjusted bad_low_threshold to be below optimal_min. For % assumed 100.0 for high bad.
# From the table common errors, it's '<80%' while optimal is '75-85%'. This implies that 80% is still good.
# Let's adjust based on the narrative for a more strict "bad" range if 75-85 is optimal:
# If 75-85 is optimal, then values like 70 or 90 might be bad.
# Re-interpreting for Weight Distribution based on the table's "Common Errors" for 80%:
# "<80% premature weight shift" implies anything below 80% is where issues start.
# So if optimal is 75-85, and <80 is error, then 75-79.9 is optimal but getting close to error.
# If "optimal" is strictly 75-85, then 74 is already outside. Let's make bad_low_threshold 70.0.
# The table explicitly says 85-95 for Elite in SIGHTFX. So use that.
add_metric(MetricInfo("Weight Distribution", "% Back", ScoreType.OPTIMAL_RANGE,
                      "Percentage of weight on back leg at maximum knee lift. Critical for momentum generation.",
                      {'optimal_min': 85.0, 'optimal_max': 95.0, 'bad_low_threshold': 80.0, 'bad_high_threshold': 100.0}))


# Based on SIGHTFX tables for Adult Elite:
add_metric(MetricInfo("Balance Stability Index", "cm deviation", ScoreType.LOWER_IS_BETTER,
                      "Quantifies COM maintenance during leg lift (lower deviation is better). Optimal <2cm, poor >5cm.",
                      {'optimal_upper_bound': 2.0, 'poor_threshold': 5.0}))
add_metric(MetricInfo("Posture Alignment (Windup)", "° variation", ScoreType.LOWER_IS_BETTER,
                      "Spine angle consistency during windup (lower variation is better). Optimal <3°, poor >8°.",
                      {'optimal_upper_bound': 3.0, 'poor_threshold': 8.0}))
add_metric(MetricInfo("Tempo Consistency (Windup)", "s", ScoreType.LOWER_IS_BETTER,
                      "Variation in timing between pitches during windup. Indicates rhythm consistency. Optimal <0.05s, poor >0.2s.",
                      {'optimal_upper_bound': 0.05, 'poor_threshold': 0.2}))
add_metric(MetricInfo("Head Stability (Windup)", "cm displacement", ScoreType.LOWER_IS_BETTER,
                      "Movement of head during leg lift (lower displacement is better). Optimal <2cm, poor >4cm.",
                      {'optimal_upper_bound': 2.0, 'poor_threshold': 4.0}))
add_metric(MetricInfo("Lead Leg Path Efficiency", "cm lateral deviation", ScoreType.LOWER_IS_BETTER,
                      "Directness of knee lift trajectory (lower deviation is better). Optimal <5cm, poor >10cm.",
                      {'optimal_upper_bound': 5.0, 'poor_threshold': 10.0}))

# 2. STRIDE PHASE METRICS
add_metric(MetricInfo("Stride Length", "% Height", ScoreType.OPTIMAL_RANGE,
                      "Distance as percentage of pitcher's height. Affects effective velocity and force.",
                      {'optimal_min': 80.0, 'optimal_max': 90.0, 'bad_low_threshold': 70.0, 'bad_high_threshold': 95.0}))
add_metric(MetricInfo("Stride Direction", "° Closed", ScoreType.OPTIMAL_RANGE,
                      "Angle of stride foot relative to center line (0-5° closed is optimal). Aids hip-shoulder separation.",
                      {'optimal_min': 0.0, 'optimal_max': 5.0, 'bad_low_threshold': -10.0, 'bad_high_threshold': 10.0})) # -10 for >10° open, 10 for >10° closed
add_metric(MetricInfo("Knee Flexion at Peak (Stride)", "°", ScoreType.OPTIMAL_RANGE,
                      "Flexion angle of lead knee during stride. Affects absorption and bracing.",
                      {'optimal_min': 35.0, 'optimal_max': 45.0, 'bad_low_threshold': 25.0, 'bad_high_threshold': 60.0}))
add_metric(MetricInfo("Hip-Shoulder Separation (Stride FC)", "°", ScoreType.OPTIMAL_RANGE,
                      "Rotational difference between hips and shoulders at foot contact. Key for elastic energy.",
                      {'optimal_min': 40.0, 'optimal_max': 50.0, 'bad_low_threshold': 30.0, 'bad_high_threshold': 60.0})) # No upper common error, assumed 60 for consistency
add_metric(MetricInfo("Pelvic Tilt", "° anterior tilt", ScoreType.OPTIMAL_RANGE,
                      "Anterior/posterior pelvic positioning (Elite optimal).",
                      {'optimal_min': 5.0, 'optimal_max': 15.0, 'bad_low_threshold': 0.0, 'bad_high_threshold': 20.0})) # Assuming 0 for minimal and 20 for excessive
add_metric(MetricInfo("Center of Mass Trajectory", "cm vertical displacement", ScoreType.LOWER_IS_BETTER,
                      "Path of COM during stride (lower displacement is better). Optimal <3cm, poor >6cm.",
                      {'optimal_upper_bound': 3.0, 'poor_threshold': 6.0}))
add_metric(MetricInfo("Front Foot Landing Pattern", "° Closed", ScoreType.OPTIMAL_RANGE,
                      "Foot position and angle at contact (10-20° closed is optimal).",
                      {'optimal_min': 10.0, 'optimal_max': 20.0, 'bad_low_threshold': 0.0, 'bad_high_threshold': 30.0})) # Assumed 0 and 30
add_metric(MetricInfo("Timing Efficiency (Stride)", "s", ScoreType.OPTIMAL_RANGE,
                      "Duration from leg lift to foot contact (Adult Elite optimal).",
                      {'optimal_min': 0.5, 'optimal_max': 0.7, 'bad_high_threshold': 0.9})) # No explicit bad_low_threshold (assumes 0.0)

# 3. ARM COCKING PHASE METRICS
add_metric(MetricInfo("Shoulder External Rotation", "°", ScoreType.OPTIMAL_RANGE,
                      "Shoulder rotation at maximum external rotation (MER).",
                      {'optimal_min': 165.0, 'optimal_max': 185.0, 'bad_low_threshold': 150.0, 'bad_high_threshold': 195.0}))
add_metric(MetricInfo("Shoulder Abduction (FC)", "°", ScoreType.OPTIMAL_RANGE, "Shoulder abduction angle at foot contact.",
                      {'optimal_min': 85.0, 'optimal_max': 100.0, 'bad_low_threshold': 75.0, 'bad_high_threshold': 110.0})) # Assumed thresholds
add_metric(MetricInfo("Elbow Flexion (FC)", "°", ScoreType.OPTIMAL_RANGE, "Elbow flexion angle at foot contact.",
                      {'optimal_min': 65.0, 'optimal_max': 95.0, 'bad_low_threshold': 50.0, 'bad_high_threshold': 100.0})) # Assumed thresholds
add_metric(MetricInfo("Hip-Shoulder Separation (Cock)", "°", ScoreType.OPTIMAL_RANGE,
                      "Peak rotational difference between hips and shoulders.",
                      {'optimal_min': 45.0, 'optimal_max': 65.0, 'bad_low_threshold': 30.0, 'bad_high_threshold': 75.0})) # No explicit upper error, assumed 75
add_metric(MetricInfo("Pelvis Rotation Velocity", "°/s", ScoreType.OPTIMAL_RANGE, "Angular speed of pelvis rotation.",
                      {'optimal_min': 700.0, 'optimal_max': 850.0, 'bad_low_threshold': 500.0, 'bad_high_threshold': 1000.0})) # Assumed thresholds based on range
add_metric(MetricInfo("Trunk Rotation Velocity", "°/s", ScoreType.OPTIMAL_RANGE, "Angular speed of trunk rotation.",
                      {'optimal_min': 1100.0, 'optimal_max': 1300.0, 'bad_low_threshold': 850.0, 'bad_high_threshold': 1500.0})) # Assumed thresholds based on range
add_metric(MetricInfo("Arm Slot Consistency (Cock)", "°", ScoreType.LOWER_IS_BETTER,
                      "Variation in arm position at MER between pitches (lower is better). Optimal <3°, poor >8°.",
                      {'optimal_upper_bound': 3.0, 'poor_threshold': 8.0}))
add_metric(MetricInfo("Elbow Height (MER)", "cm relative to shoulder", ScoreType.OPTIMAL_RANGE,
                      "Position of elbow relative to shoulder at MER (-5cm to +5cm is optimal).",
                      {'optimal_min': -5.0, 'optimal_max': 5.0, 'bad_low_threshold': -10.0, 'bad_high_threshold': 10.0})) # Assumed thresholds
add_metric(MetricInfo("Trunk Forward Tilt (MER)", "°", ScoreType.OPTIMAL_RANGE, "Forward lean from vertical at MER.",
                      {'optimal_min': 20.0, 'optimal_max': 30.0, 'bad_low_threshold': 15.0, 'bad_high_threshold': 40.0})) # Assumed thresholds
add_metric(MetricInfo("Trunk Lateral Tilt (MER)", "°", ScoreType.OPTIMAL_RANGE, "Side bend toward non-throwing side at MER.",
                      {'optimal_min': 15.0, 'optimal_max': 25.0, 'bad_low_threshold': 10.0, 'bad_high_threshold': 35.0})) # Assumed thresholds
add_metric(MetricInfo("Kinetic Chain Sequencing (Timing)", "s", ScoreType.OPTIMAL_RANGE,
                      "Timing delay between peak segment velocities (e.g., pelvis-trunk, trunk-arm).",
                      {'optimal_min': 0.015, 'optimal_max': 0.025, 'bad_low_threshold': 0.01, 'bad_high_threshold': 0.035})) # Based on table
add_metric(MetricInfo("Lead Leg Bracing", "° knee extension variation", ScoreType.LOWER_IS_BETTER,
                      "Stability of lead leg during cocking (lower variation is better). Optimal <3°, poor >8°.",
                      {'optimal_upper_bound': 3.0, 'poor_threshold': 8.0}))


# 4. ACCELERATION & RELEASE PHASE METRICS
add_metric(MetricInfo("Shoulder Internal Rotation Velocity", "°/s", ScoreType.OPTIMAL_RANGE,
                      "Angular speed of shoulder internal rotation during acceleration. Optimal 7000-8500°/s.",
                      {'optimal_min': 7000.0, 'optimal_max': 8500.0, 'bad_low_threshold': 6000.0, 'bad_high_threshold': 9500.0})) # Using values from previous table and inferred high end
add_metric(MetricInfo("Elbow Extension Velocity", "°/s", ScoreType.OPTIMAL_RANGE,
                      "Speed of elbow straightening during acceleration. Optimal 2200-2700°/s.",
                      {'optimal_min': 2200.0, 'optimal_max': 2700.0, 'bad_low_threshold': 1800.0, 'bad_high_threshold': 3000.0})) # Using values from previous table and inferred high end

add_metric(MetricInfo("Trunk Forward Tilt (Release)", "°", ScoreType.OPTIMAL_RANGE,
                      "Forward lean from vertical at ball release.",
                      {'optimal_min': 38.0, 'optimal_max': 48.0, 'bad_low_threshold': 30.0, 'bad_high_threshold': 55.0})) # Based on Adult Elite, inferred common errors
add_metric(MetricInfo("Trunk Lateral Tilt (Release)", "°", ScoreType.OPTIMAL_RANGE,
                      "Side bend angle toward non-throwing side at ball release.",
                      {'optimal_min': 15.0, 'optimal_max': 25.0, 'bad_low_threshold': 10.0, 'bad_high_threshold': 30.0})) # Based on Adult Elite, inferred common errors
add_metric(MetricInfo("Pitch Velocity", "mph", ScoreType.HIGHER_IS_BETTER, "Speed of the ball at release.",
                      {'optimal_lower_bound': 90.0})) # Based on Adult Elite 90-100+
add_metric(MetricInfo("Spin Rate", "rpm", ScoreType.HIGHER_IS_BETTER,
                      "Ball rotation at release (generally higher is better for fastballs).",
                      {'optimal_lower_bound': 2100.0})) # Based on Adult Elite 2100-2500+
add_metric(MetricInfo("Extension", "ft", ScoreType.HIGHER_IS_BETTER, "Distance from rubber at release.",
                      {'optimal_lower_bound': 6.3})) # Based on Adult Elite 6.3-7.0+
add_metric(MetricInfo("Release Height", "% of Height", ScoreType.OPTIMAL_RANGE,
                      "Height of release point as percentage of pitcher's height.",
                      {'optimal_min': 81.0, 'optimal_max': 86.0, 'bad_low_threshold': 75.0, 'bad_high_threshold': 88.0})) # Based on Adult Elite & common errors
add_metric(MetricInfo("Release Point Consistency", "cm", ScoreType.LOWER_IS_BETTER,
                      "Variation in release position between pitches (lower is better). Optimal <2cm, poor >5cm.",
                      {'optimal_upper_bound': 2.0, 'poor_threshold': 5.0}))
add_metric(MetricInfo("Arm Slot at Release", "° SD", ScoreType.OPTIMAL_RANGE,
                      "Standard deviation of arm slot at release between pitches. Optimal 1-2° SD, poor >4°.",
                      {'optimal_min': 1.0, 'optimal_max': 2.0, 'bad_low_threshold': 0.0, 'bad_high_threshold': 4.0})) # Bad low assumed 0
add_metric(MetricInfo("Stride Length to Release Distance", "% of height", ScoreType.OPTIMAL_RANGE,
                      "Distance from stride foot to release point as % of pitcher's height.",
                      {'optimal_min': 85.0, 'optimal_max': 95.0, 'bad_low_threshold': 80.0, 'bad_high_threshold': 100.0})) # Based on Adult Elite, assumed high bad at 100%
add_metric(MetricInfo("Trunk Stabilization", "° change post-FCP", ScoreType.LOWER_IS_BETTER,
                      "Trunk acceleration deceleration post-Foot Contact (lower change is better). Optimal <5°, poor >10°.",
                      {'optimal_upper_bound': 5.0, 'poor_threshold': 10.0}))
add_metric(MetricInfo("Hand Position at Release", "° variation", ScoreType.OPTIMAL_RANGE,
                      "Orientation of hand and fingers at release (lower variation is better). Optimal 1-2° variation, poor >5°.",
                      {'optimal_min': 1.0, 'optimal_max': 2.0, 'bad_low_threshold': 0.0, 'bad_high_threshold': 5.0})) # Bad low assumed 0


# 5. FOLLOW-THROUGH PHASE METRICS
add_metric(MetricInfo("Balance Recovery Time", "s", ScoreType.OPTIMAL_RANGE,
                      "Time to stable fielding-ready position after release.",
                      {'optimal_min': 0.3, 'optimal_max': 0.5, 'bad_high_threshold': 0.8})) # Based on Adult Elite & common errors
add_metric(MetricInfo("Deceleration Path Efficiency", "° arc", ScoreType.OPTIMAL_RANGE,
                      "Path of arm during deceleration (gradual 60-80° arc is optimal).",
                      {'optimal_min': 60.0, 'optimal_max': 80.0, 'bad_low_threshold': 45.0, 'bad_high_threshold': 90.0})) # Based on description, assumed high bad.
add_metric(MetricInfo("Controlled Eccentricity", "% slowdown", ScoreType.OPTIMAL_RANGE,
                      "Rate of arm deceleration (25-35% gradual slowdown is optimal).",
                      {'optimal_min': 25.0, 'optimal_max': 35.0, 'bad_low_threshold': 15.0, 'bad_high_threshold': 50.0})) # Assumed thresholds
add_metric(MetricInfo("Balance Retention (Follow-Through)", "cm lateral displacement", ScoreType.LOWER_IS_BETTER,
                      "COM control during follow-through (lower displacement is better). Optimal <5cm, poor >10cm.",
                      {'optimal_upper_bound': 5.0, 'poor_threshold': 10.0}))
add_metric(MetricInfo("Front Knee Control", "° controlled flexion", ScoreType.OPTIMAL_RANGE,
                      "Stability of front leg during follow-through (10-20° controlled flexion is optimal).",
                      {'optimal_min': 10.0, 'optimal_max': 20.0, 'bad_low_threshold': 0.0, 'bad_high_threshold': 30.0})) # Assumed 0 for hyperextension, 30 for collapse
add_metric(MetricInfo("Rotational Completion", "° toward target", ScoreType.OPTIMAL_RANGE,
                      "Degree of body rotation completion toward target.",
                      {'optimal_min': 80.0, 'optimal_max': 100.0, 'bad_low_threshold': 70.0, 'bad_high_threshold': 110.0})) # Assumed thresholds
add_metric(MetricInfo("Head Position Tracking (Follow-Through)", "cm vertical drop", ScoreType.LOWER_IS_BETTER,
                      "Head movement during follow-through (lower vertical drop is better). Optimal <4cm, poor >8cm.",
                      {'optimal_upper_bound': 4.0, 'poor_threshold': 8.0}))
add_metric(MetricInfo("Energy Dissipation Rate", "% per 0.1s", ScoreType.OPTIMAL_RANGE,
                      "Gradual reduction in system energy (30-40% per 0.1s is optimal).",
                      {'optimal_min': 30.0, 'optimal_max': 40.0, 'bad_low_threshold': 10.0, 'bad_high_threshold': 60.0})) # Assumed thresholds

# 6. KINETIC CHAIN EFFICIENCY METRICS
add_metric(MetricInfo("Ground Force Utilization", "x Body Weight", ScoreType.OPTIMAL_RANGE,
                      "Transfer of ground reaction force (1.2-1.5x body weight is optimal).",
                      {'optimal_min': 1.2, 'optimal_max': 1.5, 'bad_low_threshold': 1.0, 'bad_high_threshold': 2.0})) # Assumed high bad
add_metric(MetricInfo("Energy Transfer Efficiency", "%", ScoreType.OPTIMAL_RANGE,
                      "Percentage of energy transferred up kinetic chain.",
                      {'optimal_min': 80.0, 'optimal_max': 90.0, 'bad_low_threshold': 70.0, 'bad_high_threshold': 100.0})) # Assumed high bad is 100
add_metric(MetricInfo("Joint Torque Distribution", "% variation", ScoreType.LOWER_IS_BETTER,
                      "Balanced loading across joints (lower variation is better). Optimal <25%, poor >40%.",
                      {'optimal_upper_bound': 25.0, 'poor_threshold': 40.0}))
add_metric(MetricInfo("Movement Plane Consistency", "° deviation", ScoreType.LOWER_IS_BETTER,
                      "Minimization of out-of-plane motion (lower deviation is better). Optimal <5°, poor >10°.",
                      {'optimal_upper_bound': 5.0, 'poor_threshold': 10.0}))


# 7. INJURY RISK METRICS (Higher values indicate higher risk, lower score)
add_metric(MetricInfo("Shoulder Maximum External Rotation (Risk)", "°", ScoreType.INJURY_RISK,
                      "Excessive shoulder external rotation increases labral tear risk.",
                      {'warning_threshold': 185.0, 'critical_threshold': 195.0}))
add_metric(MetricInfo("Elbow Valgus Torque", "Nm", ScoreType.INJURY_RISK,
                      "High medial elbow stress increases UCL injury risk.",
                      {'warning_threshold': 40.0, 'critical_threshold': 55.0}))
add_metric(MetricInfo("Lead Knee Extension Rate", "°/s", ScoreType.INJURY_RISK,
                      "Rapid knee extension creates landing stress (higher is riskier).",
                      {'warning_threshold': 250.0, 'critical_threshold': 350.0}))
add_metric(MetricInfo("Shoulder Horizontal Abduction", "° at FC", ScoreType.INJURY_RISK,
                      "Extreme layback position stresses posterior capsule (higher is riskier).",
                      {'warning_threshold': 15.0, 'critical_threshold': 25.0}))
add_metric(MetricInfo("Trunk Lateral Tilt Timing (Risk)", "° before FC", ScoreType.INJURY_RISK,
                      "Early side-bending increases spine stress (higher is riskier).",
                      {'warning_threshold': 15.0, 'critical_threshold': 25.0}))
add_metric(MetricInfo("Deceleration Control (Risk)", "% per 0.1s", ScoreType.INJURY_RISK,
                      "Abrupt arm deceleration stresses posterior shoulder (higher is riskier).",
                      {'warning_threshold': 60.0, 'critical_threshold': 80.0}))
add_metric(MetricInfo("Premature Trunk Rotation", "% before FC", ScoreType.INJURY_RISK,
                      "Early trunk rotation reduces kinetic chain efficiency and can increase risk (higher is riskier).",
                      {'warning_threshold': 30.0, 'critical_threshold': 50.0}))


# --- Main Scoring Function ---
def get_metric_score_runtime_params(metric_name: str, value: float) -> Optional[
    Dict[str, Any]]:
    """
    Calculates the score for a given metric based on its observed value and its hardcoded parameters.
    """
    metric_info = ALL_METRICS.get(metric_name)
    if metric_info is None:
        print(f"Error: Metric '{metric_name}' not found in database.")
        return None

    try:
        score = metric_info.calculate_score(value) # No runtime params here

        # Prepare output dictionary
        result = {
            "metric_name": metric_info.name,
            "unit": metric_info.unit,
            "value": value,
            "score": score,
            "description": metric_info.description,
            "score_type": metric_info.score_type.value,
            "used_parameters": metric_info.default_params  # Include the hardcoded parameters used
        }
        return result

    except ValueError as e:
        print(f"Error calculating score for '{metric_name}': {e}")
        return None


# --- Interactive Tool ---
def interactive_scoring_tool():
    print("Welcome to the Pitching Biomechanics Scoring Tool.")
    print("Parameters for each metric are hardcoded based on 'pitch.md' (Adult Elite values).")
    print("Type 'list' to see all available metrics and their types, or 'exit' to quit.")

    # Cache sorted metric names for numerical selection
    sorted_metric_names = sorted(ALL_METRICS.keys())

    while True:
        print("\nAvailable Metrics:")
        for i, name in enumerate(sorted_metric_names, 1):
            print(f"  {i}. {name}")

        user_input_choice = input("\nEnter metric number (or 'list', 'exit'): ").strip()
        if user_input_choice.lower() == 'exit':
            print("Exiting tool. Goodbye!")
            break
        elif user_input_choice.lower() == 'list':
            print("\nMetrics and their scoring types:")
            for i, name in enumerate(sorted_metric_names, 1):
                metric_def = ALL_METRICS[name]
                print(f"  {i}. {name} ({metric_def.score_type.value}) - {metric_def.description}")
            continue  # Loop back to ask for a number

        try:
            metric_number = int(user_input_choice)
            if not (1 <= metric_number <= len(sorted_metric_names)):
                raise ValueError
            metric_name = sorted_metric_names[metric_number - 1]
            metric_info = ALL_METRICS[metric_name]
        except ValueError:
            print("Invalid input. Please enter a valid number from the list, 'list', or 'exit'.")
            continue
        except IndexError:
            print("Invalid number. Please select a number within the range.")
            continue

        try:
            value_str = input(f"Enter observed value for '{metric_info.name}' ({metric_info.unit}): ").strip()
            value = float(value_str)
        except ValueError:
            print("Invalid value. Please enter a numerical value.")
            continue

        # Parameters are now hardcoded, no need to ask for them
        result = get_metric_score_runtime_params(metric_name, value)
        if result:
            print(f"\n--- Scoring Result for {result['metric_name']} ---")
            print(f"Observed Value: {result['value']} {result['unit']}")
            print(f"Score ({MIN_SCORE_VALUE}-100): {result['score']:.1f}")
            print(f"Description: {result['description']}")
            print(f"Parameters Used for Calculation: {result['used_parameters']}")
            print("---------------------------------------")


if __name__ == "__main__":
    interactive_scoring_tool()