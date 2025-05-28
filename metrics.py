import math
from enum import Enum
from typing import Dict, Optional, List, Any

# --- Constants ---
MIN_SCORE_VALUE = 1.0  # The minimum score any metric can receive.


# --- Enums for Score Types ---
class ScoreType(Enum):
    OPTIMAL_RANGE = "optimal_range"  # Score 100 within range, scales to min_score_value outside
    LOWER_IS_BETTER = "lower_is_better"  # Score 100 at 0, scales to min_score_value as value increases
    HIGHER_IS_BETTER = "higher_is_better"  # Score 100 at/above target, scales from min_score_value at 0
    INJURY_RISK = "injury_risk"  # Score 100 below warning, scales to min_score_value at/above critical


# --- Metric Information Data Class (Now truly parameter-free) ---
class MetricInfo:
    """
    Defines the properties and scoring logic type for a single biomechanical metric.
    No default parameters are stored here; all thresholds are provided by the user.
    """

    def __init__(self, name: str, unit: str, score_type: ScoreType, description: str):
        self.name = name
        self.unit = unit
        self.score_type = score_type
        self.description = description

    def calculate_score(self, value: float, params: Dict[str, float]) -> float:
        """
        Calculates the score (0-100) for the given metric value using user-provided parameters.
        No score will ever literally be 0; it will be floored at MIN_SCORE_VALUE.
        """
        score = 0.0

        if self.score_type == ScoreType.OPTIMAL_RANGE:
            min_opt = params.get('min_optimal')
            max_opt = params.get('max_optimal')

            if any(p is None for p in [min_opt, max_opt]):
                raise ValueError(f"Missing parameters for OPTIMAL_RANGE. Requires min_optimal, max_optimal.")

            if min_opt <= value <= max_opt:
                score = 100.0
            else:
                if value < min_opt:
                    # Scales linearly from MIN_SCORE_VALUE at 0 to 100 at min_opt
                    if min_opt <= 0:  # If min_opt is 0 or negative, any value below it gets MIN_SCORE_VALUE
                        score = MIN_SCORE_VALUE
                    else:
                        score = MIN_SCORE_VALUE + (value / min_opt) * (100.0 - MIN_SCORE_VALUE)
                        score = max(MIN_SCORE_VALUE, score)  # Ensure it doesn't go below MIN_SCORE_VALUE
                elif value > max_opt:
                    # Scales linearly from 100 at max_opt to MIN_SCORE_VALUE at 2*max_opt (simple falloff)
                    if max_opt <= 0:  # If max_opt is 0 or negative, any value above it gets MIN_SCORE_VALUE
                        score = MIN_SCORE_VALUE
                    else:
                        upper_bound_for_min_score = max_opt * 2.0  # Simple scaling for "very bad" high values
                        if upper_bound_for_min_score <= max_opt:  # Safety check for negative/zero max_opt
                            score = MIN_SCORE_VALUE
                        else:
                            score = 100.0 - ((value - max_opt) / (upper_bound_for_min_score - max_opt)) * (
                                        100.0 - MIN_SCORE_VALUE)
                            score = max(MIN_SCORE_VALUE, score)  # Ensure it doesn't go below MIN_SCORE_VALUE

        elif self.score_type == ScoreType.LOWER_IS_BETTER:
            max_value_for_min_score = params.get('max_value_for_min_score')
            if max_value_for_min_score is None or max_value_for_min_score <= 0:
                raise ValueError(
                    f"Missing or invalid max_value_for_min_score for LOWER_IS_BETTER. Requires max_value_for_min_score > 0.")

            # Score 100 at 0, scales down to MIN_SCORE_VALUE at max_value_for_min_score
            score = max(MIN_SCORE_VALUE, 100.0 - (value / max_value_for_min_score) * (100.0 - MIN_SCORE_VALUE))

        elif self.score_type == ScoreType.HIGHER_IS_BETTER:
            target_value = params.get('target_value')
            if target_value is None or target_value <= 0:
                raise ValueError(f"Missing or invalid target_value for HIGHER_IS_BETTER. Requires target_value > 0.")

            if value >= target_value:
                score = 100.0
            else:
                # Scale from MIN_SCORE_VALUE (at value 0) up to 100 (at target_value)
                if value <= 0:  # If value is non-positive, it gets the floor score
                    score = MIN_SCORE_VALUE
                else:
                    score = max(MIN_SCORE_VALUE, (value / target_value) * 100.0)

        elif self.score_type == ScoreType.INJURY_RISK:
            warning_threshold = params.get('warning_threshold')
            critical_threshold = params.get('critical_threshold')
            if any(p is None for p in [warning_threshold, critical_threshold]):
                raise ValueError(f"Missing parameters for INJURY_RISK. Requires warning_threshold, critical_threshold.")

            if warning_threshold >= critical_threshold:  # Sanity check for thresholds
                score = 100.0 if value <= warning_threshold else MIN_SCORE_VALUE
            else:
                if value <= warning_threshold:
                    score = 100.0
                elif value >= critical_threshold:
                    score = MIN_SCORE_VALUE
                else:
                    # Linear drop from 100 at warning to MIN_SCORE_VALUE at critical
                    score = max(MIN_SCORE_VALUE,
                                100.0 - (value - warning_threshold) / (critical_threshold - warning_threshold) * (
                                            100.0 - MIN_SCORE_VALUE))

        return round(score, 1)


# --- Database of All Metrics (now without default parameters) ---
ALL_METRICS: Dict[str, MetricInfo] = {}


# Helper function to add a metric to the global dictionary
def add_metric(metric_def: MetricInfo):
    ALL_METRICS[metric_def.name] = metric_def


# --- POPULATING METRICS (from pitch.md tables, now purely definitional) ---

# 1. WINDUP PHASE
add_metric(MetricInfo("Knee Lift Height", "°", ScoreType.OPTIMAL_RANGE,
                      "Hip flexion angle of lead knee at peak lift. Higher is generally better for load."))
add_metric(MetricInfo("Balance Duration", "s", ScoreType.OPTIMAL_RANGE,
                      "Time spent at peak knee lift. Optimal is generally shorter for elite, suggesting quick rhythm."))
add_metric(MetricInfo("Trunk Rotation (Windup)", "°", ScoreType.OPTIMAL_RANGE,
                      "Initial rotation away from home plate during windup. Allows for counter-rotation."))
add_metric(MetricInfo("Weight Distribution (Windup)", "% Back", ScoreType.OPTIMAL_RANGE,
                      "Percentage of weight on back leg at maximum knee lift. Critical for momentum generation."))
add_metric(MetricInfo("Balance Stability Index", "cm deviation", ScoreType.LOWER_IS_BETTER,
                      "Quantifies COM maintenance during leg lift (lower deviation is better)."))
add_metric(MetricInfo("Posture Alignment (Windup)", "° variation", ScoreType.LOWER_IS_BETTER,
                      "Spine angle consistency during windup (lower variation is better)."))
add_metric(MetricInfo("Tempo Consistency (Windup)", "s", ScoreType.LOWER_IS_BETTER,
                      "Variation in timing between pitches during windup. Indicates rhythm consistency."))
add_metric(MetricInfo("Head Stability (Windup)", "cm displacement", ScoreType.LOWER_IS_BETTER,
                      "Movement of head during leg lift (lower displacement is better)."))
add_metric(MetricInfo("Lead Leg Path Efficiency", "cm lateral deviation", ScoreType.LOWER_IS_BETTER,
                      "Directness of knee lift trajectory (lower deviation is better)."))

# 2. STRIDE PHASE
add_metric(MetricInfo("Stride Length", "% Height", ScoreType.OPTIMAL_RANGE,
                      "Distance as percentage of pitcher's height. Affects effective velocity and force."))
add_metric(MetricInfo("Stride Direction", "° Closed", ScoreType.OPTIMAL_RANGE,
                      "Angle of stride foot relative to center line (0-5° closed is optimal). Aids hip-shoulder separation."))
add_metric(MetricInfo("Knee Flexion at Peak (Stride)", "°", ScoreType.OPTIMAL_RANGE,
                      "Flexion angle of lead knee during stride. Affects absorption and bracing."))
add_metric(MetricInfo("Hip-Shoulder Separation (Stride FC)", "°", ScoreType.OPTIMAL_RANGE,
                      "Rotational difference between hips and shoulders at foot contact. Key for elastic energy."))
add_metric(MetricInfo("Pelvic Tilt", "° anterior tilt", ScoreType.OPTIMAL_RANGE,
                      "Anterior/posterior pelvic positioning (Elite optimal)."))
add_metric(MetricInfo("Center of Mass Trajectory", "cm vertical displacement", ScoreType.LOWER_IS_BETTER,
                      "Path of COM during stride (lower displacement is better)."))
add_metric(MetricInfo("Front Foot Landing Pattern", "° Closed", ScoreType.OPTIMAL_RANGE,
                      "Foot position and angle at contact (10-20° closed is optimal)."))
add_metric(MetricInfo("Timing Efficiency (Stride)", "s", ScoreType.OPTIMAL_RANGE,
                      "Duration from leg lift to foot contact (Adult Elite optimal)."))

# 3. ARM COCKING PHASE
add_metric(MetricInfo("Shoulder External Rotation", "°", ScoreType.OPTIMAL_RANGE,
                      "Shoulder rotation at maximum external rotation (MER)."))
add_metric(
    MetricInfo("Shoulder Abduction (FC)", "°", ScoreType.OPTIMAL_RANGE, "Shoulder abduction angle at foot contact."))
add_metric(MetricInfo("Elbow Flexion (FC)", "°", ScoreType.OPTIMAL_RANGE, "Elbow flexion angle at foot contact."))
add_metric(MetricInfo("Hip-Shoulder Separation (Cock)", "°", ScoreType.OPTIMAL_RANGE,
                      "Peak rotational difference between hips and shoulders."))
add_metric(MetricInfo("Pelvis Rotation Velocity", "°/s", ScoreType.OPTIMAL_RANGE, "Angular speed of pelvis rotation."))
add_metric(MetricInfo("Trunk Rotation Velocity", "°/s", ScoreType.OPTIMAL_RANGE, "Angular speed of trunk rotation."))
add_metric(MetricInfo("Arm Slot Consistency (Cock)", "°", ScoreType.LOWER_IS_BETTER,
                      "Variation in arm position at MER between pitches (lower is better)."))
add_metric(MetricInfo("Elbow Height (MER)", "cm relative to shoulder", ScoreType.OPTIMAL_RANGE,
                      "Position of elbow relative to shoulder at MER (-5cm to +5cm is optimal)."))
add_metric(MetricInfo("Trunk Forward Tilt (MER)", "°", ScoreType.OPTIMAL_RANGE, "Forward lean from vertical at MER."))
add_metric(
    MetricInfo("Trunk Lateral Tilt (MER)", "°", ScoreType.OPTIMAL_RANGE, "Side bend toward non-throwing side at MER."))
add_metric(MetricInfo("Kinetic Chain Sequencing (Timing)", "s", ScoreType.OPTIMAL_RANGE,
                      "Timing delay between peak segment velocities (e.g., pelvis-trunk, trunk-arm)."))
add_metric(MetricInfo("Lead Leg Bracing", "° knee extension variation", ScoreType.LOWER_IS_BETTER,
                      "Stability of lead leg during cocking (lower variation is better)."))

# 4. ACCELERATION & RELEASE PHASE
add_metric(MetricInfo("Shoulder Internal Rotation Velocity", "°/s", ScoreType.HIGHER_IS_BETTER,
                      "Angular speed of shoulder internal rotation during acceleration."))
add_metric(MetricInfo("Elbow Extension Velocity", "°/s", ScoreType.HIGHER_IS_BETTER,
                      "Speed of elbow straightening during acceleration."))
add_metric(MetricInfo("Trunk Forward Tilt (Release)", "°", ScoreType.OPTIMAL_RANGE,
                      "Forward lean from vertical at ball release."))
add_metric(MetricInfo("Trunk Lateral Tilt (Release)", "°", ScoreType.OPTIMAL_RANGE,
                      "Side bend angle toward non-throwing side at ball release."))
add_metric(MetricInfo("Pitch Velocity", "mph", ScoreType.HIGHER_IS_BETTER, "Speed of the ball at release."))
add_metric(MetricInfo("Spin Rate", "rpm", ScoreType.HIGHER_IS_BETTER,
                      "Ball rotation at release (generally higher is better for fastballs)."))
add_metric(MetricInfo("Extension", "ft", ScoreType.HIGHER_IS_BETTER, "Distance from rubber at release."))
add_metric(MetricInfo("Release Height", "% of Height", ScoreType.OPTIMAL_RANGE,
                      "Height of release point as percentage of pitcher's height."))
add_metric(MetricInfo("Release Point Consistency", "cm", ScoreType.LOWER_IS_BETTER,
                      "Variation in release position between pitches (lower is better)."))
add_metric(MetricInfo("Arm Slot at Release", "° SD", ScoreType.LOWER_IS_BETTER,
                      "Standard deviation of arm slot at release between pitches (lower is better)."))
add_metric(MetricInfo("Stride Length to Release Distance", "% of height", ScoreType.OPTIMAL_RANGE,
                      "Distance from stride foot to release point as % of pitcher's height."))
add_metric(MetricInfo("Trunk Stabilization", "° change post-FCP", ScoreType.LOWER_IS_BETTER,
                      "Trunk acceleration deceleration post-Foot Contact (lower change is better)."))
add_metric(MetricInfo("Hand Position at Release", "° variation", ScoreType.LOWER_IS_BETTER,
                      "Orientation of hand and fingers at release (lower variation is better)."))

# 5. FOLLOW-THROUGH PHASE
add_metric(MetricInfo("Balance Recovery Time", "s", ScoreType.OPTIMAL_RANGE,
                      "Time to stable fielding-ready position after release."))
add_metric(MetricInfo("Deceleration Path Efficiency", "° arc", ScoreType.OPTIMAL_RANGE,
                      "Path of arm during deceleration (gradual 60-80° arc is optimal)."))
add_metric(MetricInfo("Controlled Eccentricity", "% slowdown", ScoreType.OPTIMAL_RANGE,
                      "Rate of arm deceleration (25-35% gradual slowdown is optimal)."))
add_metric(MetricInfo("Balance Retention (Follow-Through)", "cm lateral displacement", ScoreType.LOWER_IS_BETTER,
                      "COM control during follow-through (lower displacement is better)."))
add_metric(MetricInfo("Front Knee Control", "° controlled flexion", ScoreType.OPTIMAL_RANGE,
                      "Stability of front leg during follow-through (10-20° controlled flexion is optimal)."))
add_metric(MetricInfo("Rotational Completion", "° toward target", ScoreType.OPTIMAL_RANGE,
                      "Degree of body rotation completion toward target."))
add_metric(MetricInfo("Head Position Tracking (Follow-Through)", "cm vertical drop", ScoreType.LOWER_IS_BETTER,
                      "Head movement during follow-through (lower vertical drop is better)."))
add_metric(MetricInfo("Energy Dissipation Rate", "% per 0.1s", ScoreType.OPTIMAL_RANGE,
                      "Gradual reduction in system energy (30-40% per 0.1s is optimal)."))

# 6. KINETIC CHAIN EFFICIENCY METRICS
add_metric(MetricInfo("Ground Force Utilization", "x Body Weight", ScoreType.OPTIMAL_RANGE,
                      "Transfer of ground reaction force (1.2-1.5x body weight is optimal)."))
add_metric(MetricInfo("Energy Transfer Efficiency", "%", ScoreType.OPTIMAL_RANGE,
                      "Percentage of energy transferred up kinetic chain."))
add_metric(MetricInfo("Joint Torque Distribution", "% variation", ScoreType.LOWER_IS_BETTER,
                      "Balanced loading across joints (lower variation is better)."))
add_metric(MetricInfo("Movement Plane Consistency", "° deviation", ScoreType.LOWER_IS_BETTER,
                      "Minimization of out-of-plane motion (lower deviation is better)."))

# 7. INJURY RISK METRICS (Higher values indicate higher risk, lower score)
add_metric(MetricInfo("Shoulder Maximum External Rotation (Risk)", "°", ScoreType.INJURY_RISK,
                      "Excessive shoulder external rotation increases labral tear risk."))
add_metric(MetricInfo("Elbow Valgus Torque", "Nm", ScoreType.INJURY_RISK,
                      "High medial elbow stress increases UCL injury risk."))
add_metric(MetricInfo("Lead Knee Extension Rate", "°/s", ScoreType.INJURY_RISK,
                      "Rapid knee extension creates landing stress (higher is riskier)."))
add_metric(MetricInfo("Shoulder Horizontal Abduction", "° at FC", ScoreType.INJURY_RISK,
                      "Extreme layback position stresses posterior capsule (higher is riskier)."))
add_metric(MetricInfo("Trunk Lateral Tilt Timing (Risk)", "° before FC", ScoreType.INJURY_RISK,
                      "Early side-bending increases spine stress (higher is riskier)."))
add_metric(MetricInfo("Deceleration Control (Risk)", "% per 0.1s", ScoreType.INJURY_RISK,
                      "Abrupt arm deceleration stresses posterior shoulder (higher is riskier)."))
add_metric(MetricInfo("Premature Trunk Rotation", "% before FC", ScoreType.INJURY_RISK,
                      "Early trunk rotation reduces kinetic chain efficiency and can increase risk (higher is riskier)."))


# --- Main Scoring Function ---
def get_metric_score_runtime_params(metric_name: str, value: float, params: Dict[str, float]) -> Optional[
    Dict[str, Any]]:
    """
    Calculates the score for a given metric based on its observed value and user-provided parameters.
    """
    metric_info = ALL_METRICS.get(metric_name)
    if metric_info is None:
        print(f"Error: Metric '{metric_name}' not found in database.")
        return None

    try:
        score = metric_info.calculate_score(value, params)

        # Prepare output dictionary
        result = {
            "metric_name": metric_info.name,
            "unit": metric_info.unit,
            "value": value,
            "score": score,
            "description": metric_info.description,
            "score_type": metric_info.score_type.value,
            "used_parameters": params  # Include the parameters used for this calculation
        }
        return result

    except ValueError as e:
        print(f"Error calculating score for '{metric_name}': {e}")
        return None


# --- Interactive Tool ---
def interactive_scoring_tool():
    """Provides an interactive command-line tool for scoring metrics."""
    print("Welcome to the Baseball Pitching Biomechanics Scorer (Simplified Version)!")
    print("This tool calculates a 1-100 score for individual pitching metrics (no score will be 0).")
    print("You will provide all optimal ranges/thresholds for scoring.")
    print("Type 'list' to see all available metrics, or 'exit' to quit.")

    # Cache sorted metric names for numerical selection
    sorted_metric_names = sorted(ALL_METRICS.keys())

    while True:
        print("\nAvailable Metrics:")
        for i, name in enumerate(sorted_metric_names, 1):
            print(f"  {i}. {name}")

        user_input_choice = input("\nEnter metric number (or 'list' to show metric types, 'exit' to quit): ").strip()

        if user_input_choice.lower() == 'exit':
            print("Exiting tool. Goodbye!")
            break
        elif user_input_choice.lower() == 'list':
            # This 'list' logic will now show all info, then re-prompt for a number.
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

        # --- Prompt for runtime parameters based on ScoreType ---
        runtime_params = {}
        print(f"\n--- Enter Scoring Parameters for {metric_info.name} ({metric_info.score_type.value}) ---")
        if metric_info.score_type == ScoreType.OPTIMAL_RANGE:
            try:
                runtime_params['min_optimal'] = float(input(f"  Enter Min Optimal ({metric_info.unit}): "))
                runtime_params['max_optimal'] = float(input(f"  Enter Max Optimal ({metric_info.unit}): "))
            except ValueError:
                print("Invalid input for parameters. Please enter numerical values.")
                continue
        elif metric_info.score_type == ScoreType.LOWER_IS_BETTER:
            try:
                runtime_params['max_value_for_min_score'] = float(input(
                    f"  Enter Max Value for Min Score (value at/above which score is {MIN_SCORE_VALUE}) ({metric_info.unit}): "))
            except ValueError:
                print("Invalid input for parameters. Please enter numerical values.")
                continue
        elif metric_info.score_type == ScoreType.HIGHER_IS_BETTER:
            try:
                runtime_params['target_value'] = float(
                    input(f"  Enter Target Value (value at/above which score is 100) ({metric_info.unit}): "))
            except ValueError:
                print("Invalid input for parameters. Please enter numerical values.")
                continue
        elif metric_info.score_type == ScoreType.INJURY_RISK:
            try:
                runtime_params['warning_threshold'] = float(
                    input(f"  Enter Warning Threshold (value at/below which score is 100) ({metric_info.unit}): "))
                runtime_params['critical_threshold'] = float(input(
                    f"  Enter Critical Threshold (value at/above which score is {MIN_SCORE_VALUE}) ({metric_info.unit}): "))
            except ValueError:
                print("Invalid input for parameters. Please enter numerical values.")
                continue

        result = get_metric_score_runtime_params(metric_name, value, runtime_params)
        if result:
            print(f"\n--- Scoring Result for {result['metric_name']} ---")
            print(f"Observed Value: {result['value']} {result['unit']}")
            print(f"Score ({MIN_SCORE_VALUE}-100): {result['score']:.1f}")
            print(f"Description: {result['description']}")
            print(f"Parameters Used for Calculation: {result['used_parameters']}")
            print("---------------------------------------")


if __name__ == "__main__":
    interactive_scoring_tool()