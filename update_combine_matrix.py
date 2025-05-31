import math
import uuid


class SightFXMetricsCalculator:
    def __init__(self):
        # Simulate database tables by populating dictionaries
        self.metrics_db = {}
        self.bands_db = []

        # Populate simulated database with sample data from pitch.md
        self._populate_simulated_db()

        # Age groups and skill levels for user profile input
        self.age_groups_map = {
            1: "Youth (8-12)", 2: "Young Adult (13-25)",
            3: "Adult (26-39)", 4: "Middle Age (40-55)",
            5: "Masters (56+)"
        }
        self.skill_levels_map = {
            1: "Beginner", 2: "Intermediate", 3: "Elite"
        }

    def _add_metric(self, name, unit, score_function, description="", is_risk_metric=False, calculate_function=None):
        metric_id = str(uuid.uuid4())
        self.metrics_db[name] = {
            "id": metric_id,
            "name": name,
            "unit": unit,
            "description": description,
            "is_risk_metric": is_risk_metric,
            "calculate_function": calculate_function,
            "score_function": score_function
        }
        return metric_id

    def _add_band(self, metric_id, name, min_value=None, max_value=None,
                  target_value=None, score_multiplier=1.0, invert_score_display=False,
                  age_group=None, skill_level=None):
        self.bands_db.append({
            "id": str(uuid.uuid4()),
            "metric_id": metric_id,
            "name": name,
            "min_value": float(min_value) if min_value is not None else None,
            "max_value": float(max_value) if max_value is not None else None,
            "target_value": float(target_value) if target_value is not None else None,
            "score_multiplier": float(score_multiplier),
            "invert_score_display": bool(invert_score_display),
            "age_group": age_group,
            "skill_level": skill_level
        })

    def _populate_simulated_db(self):
        # --- Add METRICS with their specific score_function ---
        # Windup Phase Metrics
        m_knee_lift_height_id = self._add_metric("Knee Lift Height", "degrees", "score_adaptive_range_metric",
                                                 "Hip flexion angle during leg lift")
        m_balance_duration_id = self._add_metric("Balance Duration", "seconds", "score_adaptive_range_metric",
                                                 "Time spent at peak knee lift")
        m_trunk_rotation_windup_id = self._add_metric("Trunk Rotation Windup", "degrees", "score_adaptive_range_metric",
                                                      "Initial rotation away from home plate")
        m_weight_distribution_windup_id = self._add_metric("Weight Distribution Windup", "percentage",
                                                           "score_adaptive_range_metric",
                                                           "Percentage on back leg during windup")
        m_balance_stability_index_id = self._add_metric("Balance Stability Index", "cm deviation",
                                                        "score_lower_is_better_metric",
                                                        "Quantifies COM maintenance during leg lift")  # Fixed metric
        m_head_stability_id = self._add_metric("Head Stability", "cm displacement", "score_lower_is_better_metric",
                                               "Movement of head during leg lift")  # Fixed metric
        m_lead_leg_path_efficiency_id = self._add_metric("Lead Leg Path Efficiency", "cm lateral deviation",
                                                         "score_lower_is_better_metric",
                                                         "Directness of knee lift trajectory")  # Fixed metric
        m_posture_alignment_id = self._add_metric("Posture Alignment", "degree variation",
                                                  "score_lower_is_better_metric",
                                                  "Spine angle consistency during windup")
        m_tempo_consistency_id = self._add_metric("Tempo Consistency", "seconds", "score_lower_is_better_metric",
                                                  "Variation in timing between pitches")
        m_torso_rotation_angle_id = self._add_metric("Torso Rotation Angle", "degrees", "score_standard_range_metric",
                                                     "Initial rotation away from target (SightFX)")

        # Stride Phase Metrics
        m_stride_length_id = self._add_metric("Stride Length", "percentage of height", "score_adaptive_range_metric",
                                              "Distance as percentage of pitcher's height")
        m_stride_direction_id = self._add_metric("Stride Direction", "degrees closed", "score_adaptive_range_metric",
                                                 "Angle relative to center line")
        m_knee_flexion_at_peak_id = self._add_metric("Knee Flexion at Peak", "degrees", "score_adaptive_range_metric",
                                                     "Degree of lead knee bend during stride")
        m_hip_shoulder_separation_fc_id = self._add_metric("Hip-Shoulder Separation at Foot Contact", "degrees",
                                                           "score_adaptive_range_metric",
                                                           "Rotational difference at foot contact")
        m_pelvic_tilt_id = self._add_metric("Pelvic Tilt", "degrees anterior tilt", "score_standard_range_metric",
                                            "Anterior/posterior pelvic positioning")  # Example fixed
        m_com_trajectory_id = self._add_metric("Center of Mass Trajectory", "cm vertical displacement",
                                               "score_lower_is_better_metric",
                                               "Path of COM during stride")  # Example fixed
        m_front_foot_landing_pattern_id = self._add_metric("Front Foot Landing Pattern", "degrees closed",
                                                           "score_standard_range_metric",
                                                           "Foot position and angle at contact")  # Example fixed
        m_timing_efficiency_id = self._add_metric("Timing Efficiency", "seconds", "score_standard_range_metric",
                                                  "Duration from leg lift to foot contact")  # Example fixed

        # Arm Cocking Phase Metrics
        m_mer_id = self._add_metric("Maximum External Rotation", "degrees", "score_adaptive_range_metric",
                                    "Shoulder rotation at MER")
        m_shoulder_abduction_fc_id = self._add_metric("Shoulder Abduction at FC", "degrees",
                                                      "score_standard_range_metric",
                                                      "Shoulder Abduction at Foot Contact")  # Adaptive, but optimal range is fixed around 90 for all
        m_elbow_flexion_fc_id = self._add_metric("Elbow Flexion at FC", "degrees", "score_standard_range_metric",
                                                 "Elbow Flexion at Foot Contact")  # Adaptive, but optimal range is fixed around 90 for all
        m_hip_shoulder_separation_peak_id = self._add_metric("Hip-Shoulder Separation Peak", "degrees",
                                                             "score_adaptive_range_metric",
                                                             "Hip-Shoulder Separation at peak")  # Adaptive, but optimal range is fixed around 90 for all
        m_pelvis_rotation_velocity_id = self._add_metric("Pelvis Rotation Velocity", "degrees/s",
                                                         "score_adaptive_range_metric",
                                                         "Angular speed of pelvis rotation")
        m_trunk_rotation_velocity_id = self._add_metric("Trunk Rotation Velocity", "degrees/s",
                                                        "score_adaptive_range_metric",
                                                        "Angular speed of trunk rotation")
        m_time_pelvis_trunk_peak_id = self._add_metric("Time Between Pelvis & Trunk Peak", "percentage of delivery",
                                                       "score_adaptive_range_metric",
                                                       "Timing between peak pelvis and trunk velocities")

        m_arm_slot_consistency_mer_id = self._add_metric("Arm Slot Consistency MER", "degrees between pitches",
                                                         "score_lower_is_better_metric",
                                                         "Variation in arm position at MER (SightFX)")
        m_elbow_height_id = self._add_metric("Elbow Height", "cm above shoulder", "score_standard_range_metric",
                                             "Position relative to shoulder at MER (SightFX)")  # Optimal 0-5cm above, Warning >10cm below
        m_trunk_forward_tilt_mer_id = self._add_metric("Trunk Forward Tilt MER", "degrees",
                                                       "score_standard_range_metric",
                                                       "Forward lean from vertical at MER (SightFX)")
        m_trunk_lateral_tilt_mer_id = self._add_metric("Trunk Lateral Tilt MER", "degrees",
                                                       "score_standard_range_metric",
                                                       "Side bend toward non-throwing side (SightFX)")
        m_kinetic_chain_sequencing_id = self._add_metric("Kinetic Chain Sequencing", "seconds between segments",
                                                         "score_standard_range_metric",
                                                         "Timing between peak segment velocities (SightFX)")
        m_lead_leg_bracing_cocking_id = self._add_metric("Lead Leg Bracing Cocking", "degrees knee extension variation",
                                                         "score_lower_is_better_metric",
                                                         "Stability of lead leg during cocking (SightFX)")
        m_glove_arm_action_id = self._add_metric("Glove Arm Action", "degrees from optimal position",
                                                 "score_lower_is_better_metric",
                                                 "Position and movement of non-dominant arm (SightFX)")

        # Acceleration & Release Metrics
        m_sir_velocity_id = self._add_metric("Shoulder Internal Rotation Velocity", "degrees/second",
                                             "score_higher_is_better_metric", "Angular speed during acceleration")
        m_elbow_extension_velocity_id = self._add_metric("Elbow Extension Velocity", "degrees/second",
                                                         "score_higher_is_better_metric",
                                                         "Speed of elbow straightening")
        m_trunk_forward_tilt_release_id = self._add_metric("Trunk Forward Tilt Release", "degrees",
                                                           "score_adaptive_range_metric",
                                                           "Trunk Forward Tilt at Release")
        m_trunk_lateral_tilt_release_id = self._add_metric("Trunk Lateral Tilt Release", "degrees",
                                                           "score_adaptive_range_metric",
                                                           "Trunk Lateral Tilt at Release")

        m_pitch_velocity_id = self._add_metric("Pitch Velocity", "mph", "score_higher_is_better_metric",
                                               "Speed at release")
        m_spin_rate_perf_id = self._add_metric("Spin Rate Performance", "rpm", "score_higher_is_better_metric",
                                               "Ball rotation")
        m_extension_performance_id = self._add_metric("Extension Performance", "ft", "score_adaptive_range_metric",
                                                      "Distance from rubber at release")
        m_release_height_perf_id = self._add_metric("Release Height Performance", "percentage of height",
                                                    "score_adaptive_range_metric",
                                                    "Height as percentage of pitcher's height")

        m_release_point_consistency_id = self._add_metric("Release Point Consistency", "cm between pitches",
                                                          "score_lower_is_better_metric",
                                                          "Variation in release position (SightFX)")
        m_arm_slot_at_release_id = self._add_metric("Arm Slot at Release", "degrees SD between pitches",
                                                    "score_lower_is_better_metric",
                                                    "Vertical angle of arm at release (SightFX)")
        m_stride_length_to_release_id = self._add_metric("Stride Length to Release Distance", "percentage of height",
                                                         "score_standard_range_metric",
                                                         "Distance from stride foot to release point (SightFX)")
        m_trunk_stabilization_id = self._add_metric("Trunk Stabilization", "degrees trunk position change post-FCP",
                                                    "score_lower_is_better_metric",
                                                    "Trunk acceleration deceleration (SightFX)")
        m_hand_position_at_release_id = self._add_metric("Hand Position at Release",
                                                         "degrees variation between pitches",
                                                         "score_lower_is_better_metric",
                                                         "Orientation of hand and fingers (SightFX)")

        # Follow-through Phase Metrics
        m_follow_through_length_id = self._add_metric("Follow-Through Length", "Completeness",
                                                      "score_adaptive_range_metric",
                                                      "Completeness of arm deceleration (Qualitative)")
        m_balance_recovery_ft_id = self._add_metric("Balance Recovery FT", "seconds", "score_adaptive_range_metric",
                                                    "Time to stable position after release")
        m_front_leg_at_finish_id = self._add_metric("Front Leg at Finish", "Quality", "score_adaptive_range_metric",
                                                    "Stability and control of front leg at finish (Qualitative)")
        m_fielding_position_id = self._add_metric("Fielding Position", "Quality", "score_adaptive_range_metric",
                                                  "Quality of defensive ready stance (Qualitative)")

        m_deceleration_path_efficiency_id = self._add_metric("Deceleration Path Efficiency", "degrees arc",
                                                             "score_standard_range_metric",
                                                             "Path of arm during deceleration (SightFX)")
        m_controlled_eccentricity_id = self._add_metric("Controlled Eccentricity", "percentage gradual slowdown",
                                                        "score_standard_range_metric",
                                                        "Rate of arm deceleration (SightFX)")
        m_balance_retention_id = self._add_metric("Balance Retention", "cm lateral displacement",
                                                  "score_lower_is_better_metric",
                                                  "COM control during follow-through (SightFX)")
        m_recovery_position_time_id = self._add_metric("Recovery Position Time", "seconds",
                                                       "score_lower_is_better_metric",
                                                       "Time to fielding-ready position (SightFX)")
        m_front_knee_control_id = self._add_metric("Front Knee Control", "degrees controlled flexion",
                                                   "score_standard_range_metric",
                                                   "Stability of front leg during follow-through (SightFX)")
        m_rotational_completion_id = self._add_metric("Rotational Completion", "degrees toward target",
                                                      "score_standard_range_metric",
                                                      "Degree of body rotation completion (SightFX)")
        m_head_position_tracking_id = self._add_metric("Head Position Tracking", "cm vertical drop",
                                                       "score_lower_is_better_metric",
                                                       "Head movement during follow-through (SightFX)")
        m_energy_dissipation_rate_id = self._add_metric("Energy Dissipation Rate", "percentage per 0.1s",
                                                        "score_standard_range_metric",
                                                        "Gradual reduction in system energy (SightFX)")

        # Pitch Type-Specific Metrics (SightFX)
        m_fb_spin_efficiency_id = self._add_metric("Four-Seam Fastball Spin Efficiency", "percentage",
                                                   "score_standard_range_metric",
                                                   "Spin efficiency for four-seam fastball")
        m_fb_ball_axis_id = self._add_metric("Four-Seam Fastball Ball Axis", "clock position deviation",
                                             "score_target_based_metric",
                                             "Ball axis orientation for 4-seam fastball (12:00-1:00 optimal)")  # Deviation from 12:30
        m_two_seam_horizontal_movement_id = self._add_metric("Two-Seam Fastball Horizontal Movement", "inches",
                                                             "score_standard_range_metric",
                                                             "Horizontal movement for two-seam fastball")
        m_changeup_velocity_diff_id = self._add_metric("Changeup Velocity Differential", "mph slower than FB",
                                                       "score_standard_range_metric", "Speed difference from fastball")
        m_curveball_spin_rate_id = self._add_metric("Curveball Spin Rate", "rpm", "score_higher_is_better_metric",
                                                    "Spin rate for curveball")
        m_curveball_spin_axis_id = self._add_metric("Curveball Spin Axis", "clock position deviation",
                                                    "score_target_based_metric",
                                                    "Spin axis orientation for curveball (6:00-7:00 optimal)")
        m_slider_gyro_component_id = self._add_metric("Slider Gyroscopic Component", "percentage",
                                                      "score_standard_range_metric",
                                                      "Gyroscopic spin component for slider")
        m_slider_break_ratio_id = self._add_metric("Slider Horizontal:Vertical Break Ratio", "ratio",
                                                   "score_standard_range_metric",
                                                   "Horizontal to Vertical break ratio for slider")
        m_slider_release_spin_direction_id = self._add_metric("Slider Release Spin Direction", "clock position",
                                                              "score_target_based_metric",
                                                              "Release spin direction for slider (9:00-10:30 optimal)")

        # Kinetic Chain Efficiency Metrics (SightFX)
        m_grf_utilization_id = self._add_metric("Ground Force Utilization", "times body weight vertical GRF",
                                                "score_standard_range_metric", "Transfer of ground reaction force")
        m_pelvis_trunk_timing_id = self._add_metric("Pelvis-Trunk Timing", "seconds", "score_standard_range_metric",
                                                    "Delay between peak pelvic and trunk rotation")
        m_trunk_arm_timing_id = self._add_metric("Trunk-Arm Timing", "seconds", "score_standard_range_metric",
                                                 "Delay between peak trunk rotation and shoulder rotation")
        m_energy_transfer_efficiency_id = self._add_metric("Energy Transfer Efficiency", "percentage",
                                                           "score_standard_range_metric",
                                                           "Percentage of energy transferred up kinetic chain")
        m_joint_torque_distribution_id = self._add_metric("Joint Torque Distribution", "percentage variation",
                                                          "score_lower_is_better_metric",
                                                          "Balanced loading across joints")
        m_movement_plane_consistency_id = self._add_metric("Movement Plane Consistency", "degrees deviation",
                                                           "score_lower_is_better_metric",
                                                           "Minimization of out-of-plane motion")

        # Injury Risk Metrics (SightFX)
        m_shoulder_mer_risk_id = self._add_metric("Shoulder Maximum External Rotation Risk", "degrees",
                                                  "score_risk_metric", "Degree of external rotation (Risk Assessment)",
                                                  is_risk_metric=True)
        m_elbow_valgus_torque_id = self._add_metric("Elbow Valgus Torque", "Nm", "score_risk_metric",
                                                    "Medial stress during cocking", is_risk_metric=True)
        m_lead_knee_extension_rate_id = self._add_metric("Lead Knee Extension Rate", "degrees/second",
                                                         "score_risk_metric", "Rate of knee straightening",
                                                         is_risk_metric=True)
        m_shoulder_horizontal_abduction_id = self._add_metric("Shoulder Horizontal Abduction",
                                                              "degrees at foot contact", "score_risk_metric",
                                                              "Extreme layback position", is_risk_metric=True)
        m_trunk_lateral_tilt_timing_risk_id = self._add_metric("Trunk Lateral Tilt Timing Risk",
                                                               "degrees before foot contact", "score_risk_metric",
                                                               "Early side-bending", is_risk_metric=True)
        m_inverted_w_position_id = self._add_metric("Inverted W Position", "severity score (0-10)", "score_risk_metric",
                                                    "Elbow above shoulder with scapular loading", is_risk_metric=True)
        m_deceleration_control_risk_id = self._add_metric("Deceleration Control Risk", "percentage per 0.1s",
                                                          "score_risk_metric", "Rate of arm slowdown post-release",
                                                          is_risk_metric=True)
        m_premature_trunk_rotation_id = self._add_metric("Premature Trunk Rotation", "percentage before foot contact",
                                                         "score_risk_metric", "Early upper body rotation",
                                                         is_risk_metric=True)

        # --- Add BANDS --- (Populated based on pitch.md data)
        # Helper to simplify adding bands for different skill levels
        def add_adaptive_bands(metric_id, ranges, suboptimal_low_mult=0.7, suboptimal_high_mult=0.7,
                               critical_low_mult=0.4, critical_high_mult=0.4):
            for age_skill, (min_opt, max_opt) in ranges.items():
                age_group, skill_level = age_skill
                # Optimal band
                self._add_band(metric_id, f"{age_group} {skill_level} Optimal", min_opt, max_opt, score_multiplier=1.0,
                               age_group=age_group, skill_level=skill_level)

                # Suboptimal Low band (below optimal range)
                # Max value for low band is just below the optimal min
                if min_opt is not None and min_opt > 0:
                    self._add_band(metric_id, f"{age_group} {skill_level} Suboptimal Low", min_value=0,
                                   max_value=min_opt - 0.1, score_multiplier=suboptimal_low_mult, age_group=age_group,
                                   skill_level=skill_level)
                    # For critical low, make it a smaller range at the very bottom
                    self._add_band(metric_id, f"{age_group} {skill_level} Critical Low", min_value=0,
                                   max_value=max(0, min_opt * 0.5 - 0.1), score_multiplier=critical_low_mult,
                                   age_group=age_group, skill_level=skill_level)

                # Suboptimal High band (above optimal range)
                # Min value for high band is just above the optimal max
                if max_opt is not None:
                    self._add_band(metric_id, f"{age_group} {skill_level} Suboptimal High", min_value=max_opt + 0.1,
                                   score_multiplier=suboptimal_high_mult, age_group=age_group, skill_level=skill_level)
                    # For critical high, make it a larger range at the very top
                    self._add_band(metric_id, f"{age_group} {skill_level} Critical High", min_value=max_opt * 1.5 + 0.1,
                                   score_multiplier=critical_high_mult, age_group=age_group, skill_level=skill_level)

        # --- WINDUP PHASE ---
        add_adaptive_bands(m_knee_lift_height_id, {
            ("Youth (8-12)", "Beginner"): (45, 60), ("Youth (8-12)", "Intermediate"): (50, 65),
            ("Youth (8-12)", "Elite"): (55, 70),
            ("Young Adult (13-25)", "Beginner"): (50, 65), ("Young Adult (13-25)", "Intermediate"): (60, 75),
            ("Young Adult (13-25)", "Elite"): (70, 90),
            ("Adult (26-39)", "Beginner"): (55, 70), ("Adult (26-39)", "Intermediate"): (65, 80),
            ("Adult (26-39)", "Elite"): (75, 90),
            ("Middle Age (40-55)", "Beginner"): (50, 65), ("Middle Age (40-55)", "Intermediate"): (60, 75),
            ("Middle Age (40-55)", "Elite"): (65, 80),
            ("Masters (56+)", "Beginner"): (45, 60), ("Masters (56+)", "Intermediate"): (50, 65),
            ("Masters (56+)", "Elite"): (55, 70)
        })
        add_adaptive_bands(m_balance_duration_id, {
            ("Youth (8-12)", "Beginner"): (0.6, 0.8), ("Youth (8-12)", "Intermediate"): (0.5, 0.7),
            ("Youth (8-12)", "Elite"): (0.4, 0.6),
            ("Young Adult (13-25)", "Beginner"): (0.5, 0.7), ("Young Adult (13-25)", "Intermediate"): (0.4, 0.6),
            ("Young Adult (13-25)", "Elite"): (0.3, 0.5),
            ("Adult (26-39)", "Beginner"): (0.5, 0.7), ("Adult (26-39)", "Intermediate"): (0.4, 0.6),
            ("Adult (26-39)", "Elite"): (0.3, 0.5),
            ("Middle Age (40-55)", "Beginner"): (0.6, 0.8), ("Middle Age (40-55)", "Intermediate"): (0.5, 0.7),
            ("Middle Age (40-55)", "Elite"): (0.4, 0.6),
            ("Masters (56+)", "Beginner"): (0.7, 0.9), ("Masters (56+)", "Intermediate"): (0.6, 0.8),
            ("Masters (56+)", "Elite"): (0.5, 0.7)
        })
        add_adaptive_bands(m_trunk_rotation_windup_id, {  # Initial rotation away from home plate
            ("Youth (8-12)", "Beginner"): (0, 5), ("Youth (8-12)", "Intermediate"): (0, 10),
            ("Youth (8-12)", "Elite"): (5, 15),
            ("Young Adult (13-25)", "Beginner"): (0, 10), ("Young Adult (13-25)", "Intermediate"): (5, 15),
            ("Young Adult (13-25)", "Elite"): (10, 20),
            ("Adult (26-39)", "Beginner"): (5, 15), ("Adult (26-39)", "Intermediate"): (10, 20),
            ("Adult (26-39)", "Elite"): (15, 25),
            ("Middle Age (40-55)", "Beginner"): (0, 10), ("Middle Age (40-55)", "Intermediate"): (5, 15),
            ("Middle Age (40-55)", "Elite"): (10, 20),
            ("Masters (56+)", "Beginner"): (0, 5), ("Masters (56+)", "Intermediate"): (0, 10),
            ("Masters (56+)", "Elite"): (5, 15)
        })
        add_adaptive_bands(m_weight_distribution_windup_id, {
            ("Youth (8-12)", "Beginner"): (85, 95), ("Youth (8-12)", "Intermediate"): (85, 90),
            ("Youth (8-12)", "Elite"): (80, 90),
            ("Young Adult (13-25)", "Beginner"): (85, 90), ("Young Adult (13-25)", "Intermediate"): (80, 90),
            ("Young Adult (13-25)", "Elite"): (80, 85),
            ("Adult (26-39)", "Beginner"): (80, 90), ("Adult (26-39)", "Intermediate"): (80, 85),
            ("Adult (26-39)", "Elite"): (75, 85),
            ("Middle Age (40-55)", "Beginner"): (85, 90), ("Middle Age (40-55)", "Intermediate"): (80, 90),
            ("Middle Age (40-55)", "Elite"): (80, 85),
            ("Masters (56+)", "Beginner"): (85, 95), ("Masters (56+)", "Intermediate"): (85, 90),
            ("Masters (56+)", "Elite"): (80, 90)
        })
        self._add_band(m_balance_stability_index_id, "Elite Stability", 0, 2, score_multiplier=1.0)
        self._add_band(m_balance_stability_index_id, "Good Stability", 2.1, 5, score_multiplier=0.8)
        self._add_band(m_balance_stability_index_id, "Needs Improvement", 5.1, 100, score_multiplier=0.5)
        self._add_band(m_posture_alignment_id, "Elite Alignment", 0, 3, score_multiplier=1.0)
        self._add_band(m_posture_alignment_id, "Good Alignment", 3.1, 8, score_multiplier=0.8)
        self._add_band(m_posture_alignment_id, "Needs Improvement", 8.1, 100, score_multiplier=0.5)
        self._add_band(m_tempo_consistency_id, "Elite Tempo", 0, 0.05, score_multiplier=1.0)
        self._add_band(m_tempo_consistency_id, "Good Tempo", 0.051, 0.2, score_multiplier=0.8)
        self._add_band(m_tempo_consistency_id, "Needs Improvement", 0.21, 5, score_multiplier=0.5)
        self._add_band(m_torso_rotation_angle_id, "Optimal Rotation", 15, 25, score_multiplier=1.0)
        self._add_band(m_torso_rotation_angle_id, "Insufficient Rotation", 0, 14.9, score_multiplier=0.7)
        self._add_band(m_torso_rotation_angle_id, "Over-rotation", 25.1, 100,
                       score_multiplier=0.7)  # Assume 100 is max sensible
        self._add_band(m_head_stability_id, "Elite Stability", 0, 2, score_multiplier=1.0)
        self._add_band(m_head_stability_id, "Good Stability", 2.1, 4, score_multiplier=0.8)
        self._add_band(m_head_stability_id, "Needs Improvement", 4.1, 100, score_multiplier=0.5)
        self._add_band(m_lead_leg_path_efficiency_id, "Elite Path", 0, 5, score_multiplier=1.0)
        self._add_band(m_lead_leg_path_efficiency_id, "Good Path", 5.1, 10, score_multiplier=0.8)
        self._add_band(m_lead_leg_path_efficiency_id, "Inefficient Path", 10.1, 100, score_multiplier=0.5)

        # --- STRIDE PHASE ---
        add_adaptive_bands(m_stride_length_id, {
            ("Youth (8-12)", "Beginner"): (60, 65), ("Youth (8-12)", "Intermediate"): (65, 70),
            ("Youth (8-12)", "Elite"): (68, 73),
            ("Young Adult (13-25)", "Beginner"): (65, 70), ("Young Adult (13-25)", "Intermediate"): (70, 80),
            ("Young Adult (13-25)", "Elite"): (78, 88),
            ("Adult (26-39)", "Beginner"): (70, 75), ("Adult (26-39)", "Intermediate"): (75, 85),
            ("Adult (26-39)", "Elite"): (80, 90),
            ("Middle Age (40-55)", "Beginner"): (65, 75), ("Middle Age (40-55)", "Intermediate"): (70, 80),
            ("Middle Age (40-55)", "Elite"): (75, 85),
            ("Masters (56+)", "Beginner"): (60, 70), ("Masters (56+)", "Intermediate"): (65, 75),
            ("Masters (56+)", "Elite"): (70, 80)
        })
        add_adaptive_bands(m_stride_direction_id, {
            ("Youth (8-12)", "Beginner"): (5, 10), ("Youth (8-12)", "Intermediate"): (3, 8),
            ("Youth (8-12)", "Elite"): (2, 7),
            ("Young Adult (13-25)", "Beginner"): (3, 8), ("Young Adult (13-25)", "Intermediate"): (2, 7),
            ("Young Adult (13-25)", "Elite"): (0, 5),
            ("Adult (26-39)", "Beginner"): (3, 8), ("Adult (26-39)", "Intermediate"): (2, 7),
            ("Adult (26-39)", "Elite"): (0, 5),
            ("Middle Age (40-55)", "Beginner"): (3, 8), ("Middle Age (40-55)", "Intermediate"): (2, 7),
            ("Middle Age (40-55)", "Elite"): (0, 5),
            ("Masters (56+)", "Beginner"): (5, 10), ("Masters (56+)", "Intermediate"): (3, 8),
            ("Masters (56+)", "Elite"): (2, 7)
        })
        add_adaptive_bands(m_knee_flexion_at_peak_id, {
            ("Youth (8-12)", "Beginner"): (45, 55), ("Youth (8-12)", "Intermediate"): (42, 52),
            ("Youth (8-12)", "Elite"): (40, 50),
            ("Young Adult (13-25)", "Beginner"): (43, 53), ("Young Adult (13-25)", "Intermediate"): (40, 50),
            ("Young Adult (13-25)", "Elite"): (37, 47),
            ("Adult (26-39)", "Beginner"): (42, 52), ("Adult (26-39)", "Intermediate"): (38, 48),
            ("Adult (26-39)", "Elite"): (35, 45),
            ("Middle Age (40-55)", "Beginner"): (43, 53), ("Middle Age (40-55)", "Intermediate"): (40, 50),
            ("Middle Age (40-55)", "Elite"): (38, 48),
            ("Masters (56+)", "Beginner"): (45, 55), ("Masters (56+)", "Intermediate"): (43, 53),
            ("Masters (56+)", "Elite"): (40, 50)
        })
        add_adaptive_bands(m_hip_shoulder_separation_fc_id, {
            ("Youth (8-12)", "Beginner"): (15, 20), ("Youth (8-12)", "Intermediate"): (18, 23),
            ("Youth (8-12)", "Elite"): (20, 25),
            ("Young Adult (13-25)", "Beginner"): (20, 25), ("Young Adult (13-25)", "Intermediate"): (25, 30),
            ("Young Adult (13-25)", "Elite"): (30, 40),
            ("Adult (26-39)", "Beginner"): (25, 30), ("Adult (26-39)", "Intermediate"): (30, 40),
            ("Adult (26-39)", "Elite"): (40, 50),
            ("Middle Age (40-55)", "Beginner"): (20, 25), ("Middle Age (40-55)", "Intermediate"): (25, 35),
            ("Middle Age (40-55)", "Elite"): (30, 40),
            ("Masters (56+)", "Beginner"): (15, 20), ("Masters (56+)", "Intermediate"): (20, 30),
            ("Masters (56+)", "Elite"): (25, 35)
        })
        self._add_band(m_pelvic_tilt_id, "Optimal Tilt", 5, 15, score_multiplier=1.0)
        self._add_band(m_pelvic_tilt_id, "Excessive Tilt", 15.1, 100, score_multiplier=0.5)
        self._add_band(m_pelvic_tilt_id, "Insufficient Tilt", 0, 4.9, score_multiplier=0.5)
        self._add_band(m_com_trajectory_id, "Elite Trajectory", 0, 3, score_multiplier=1.0)
        self._add_band(m_com_trajectory_id, "Good Trajectory", 3.1, 6, score_multiplier=0.8)
        self._add_band(m_com_trajectory_id, "Inefficient Trajectory", 6.1, 100, score_multiplier=0.5)
        self._add_band(m_front_foot_landing_pattern_id, "Optimal Landing", 10, 20, score_multiplier=1.0)
        self._add_band(m_front_foot_landing_pattern_id, "Suboptimal Landing (Open/Closed)", 0, 9.9,
                       score_multiplier=0.7)  # Too open
        self._add_band(m_front_foot_landing_pattern_id, "Suboptimal Landing (Open/Closed)", 20.1, 100,
                       score_multiplier=0.7)  # Too closed
        self._add_band(m_timing_efficiency_id, "Optimal Timing", 0.5, 0.7, score_multiplier=1.0)
        self._add_band(m_timing_efficiency_id, "Too Fast", 0, 0.49, score_multiplier=0.6)
        self._add_band(m_timing_efficiency_id, "Too Slow", 0.71, 5, score_multiplier=0.6)

        # --- ARM COCKING PHASE ---
        add_adaptive_bands(m_mer_id, {
            ("Youth (8-12)", "Beginner"): (145, 155), ("Youth (8-12)", "Intermediate"): (150, 160),
            ("Youth (8-12)", "Elite"): (155, 165),
            ("Young Adult (13-25)", "Beginner"): (150, 160), ("Young Adult (13-25)", "Intermediate"): (160, 170),
            ("Young Adult (13-25)", "Elite"): (165, 180),
            ("Adult (26-39)", "Beginner"): (155, 165), ("Adult (26-39)", "Intermediate"): (165, 175),
            ("Adult (26-39)", "Elite"): (170, 185),
            ("Middle Age (40-55)", "Beginner"): (150, 160), ("Middle Age (40-55)", "Intermediate"): (160, 170),
            ("Middle Age (40-55)", "Elite"): (165, 175),
            ("Masters (56+)", "Beginner"): (145, 155), ("Masters (56+)", "Intermediate"): (150, 160),
            ("Masters (56+)", "Elite"): (155, 165)
        })
        # Shoulder Abduction at FC: ~90° for optimal arm path (fixed)
        self._add_band(m_shoulder_abduction_fc_id, "Optimal Abduction", 85, 100,
                       score_multiplier=1.0)  # From text: ~90°
        self._add_band(m_shoulder_abduction_fc_id, "Suboptimal Abduction (Low)", 0, 84.9, score_multiplier=0.6)
        self._add_band(m_shoulder_abduction_fc_id, "Suboptimal Abduction (High)", 100.1, 180, score_multiplier=0.6)
        # Elbow Flexion at FC: ~90° for balance of mechanical advantage (fixed)
        self._add_band(m_elbow_flexion_fc_id, "Optimal Flexion", 65, 95,
                       score_multiplier=1.0)  # Range 65-95 based on tables
        self._add_band(m_elbow_flexion_fc_id, "Suboptimal Flexion (Low)", 0, 64.9, score_multiplier=0.6)
        self._add_band(m_elbow_flexion_fc_id, "Suboptimal Flexion (High)", 95.1, 180, score_multiplier=0.6)

        # Hip-Shoulder Separation at peak: 40-65° (text description, ranges from tables often lower at FC)
        add_adaptive_bands(m_hip_shoulder_separation_peak_id, {
            ("Youth (8-12)", "Beginner"): (15, 25), ("Youth (8-12)", "Intermediate"): (20, 30),
            ("Youth (8-12)", "Elite"): (25, 35),  # Adjusted to text 40-65 in adult elite range
            ("Young Adult (13-25)", "Beginner"): (25, 35), ("Young Adult (13-25)", "Intermediate"): (30, 45),
            ("Young Adult (13-25)", "Elite"): (40, 60),
            ("Adult (26-39)", "Beginner"): (30, 40), ("Adult (26-39)", "Intermediate"): (35, 50),
            ("Adult (26-39)", "Elite"): (45, 65),
            ("Middle Age (40-55)", "Beginner"): (25, 35), ("Middle Age (40-55)", "Intermediate"): (30, 45),
            ("Middle Age (40-55)", "Elite"): (40, 55),
            ("Masters (56+)", "Beginner"): (20, 30), ("Masters (56+)", "Intermediate"): (25, 40),
            ("Masters (56+)", "Elite"): (35, 50)
        })
        add_adaptive_bands(m_pelvis_rotation_velocity_id, {
            ("Youth (8-12)", "Beginner"): (350, 450), ("Youth (8-12)", "Intermediate"): (400, 500),
            ("Youth (8-12)", "Elite"): (450, 550),
            ("Young Adult (13-25)", "Beginner"): (450, 550), ("Young Adult (13-25)", "Intermediate"): (550, 650),
            ("Young Adult (13-25)", "Elite"): (650, 800),
            ("Adult (26-39)", "Beginner"): (500, 600), ("Adult (26-39)", "Intermediate"): (600, 700),
            ("Adult (26-39)", "Elite"): (700, 850),
            ("Middle Age (40-55)", "Beginner"): (450, 550), ("Middle Age (40-55)", "Intermediate"): (550, 650),
            ("Middle Age (40-55)", "Elite"): (650, 750),
            ("Masters (56+)", "Beginner"): (400, 500), ("Masters (56+)", "Intermediate"): (500, 600),
            ("Masters (56+)", "Elite"): (600, 700)
        }, suboptimal_low_mult=0.6, suboptimal_high_mult=0.6)  # Add suboptimals for velocity metrics.
        add_adaptive_bands(m_trunk_rotation_velocity_id, {
            ("Youth (8-12)", "Beginner"): (600, 750), ("Youth (8-12)", "Intermediate"): (700, 850),
            ("Youth (8-12)", "Elite"): (800, 950),
            ("Young Adult (13-25)", "Beginner"): (750, 900), ("Young Adult (13-25)", "Intermediate"): (900, 1100),
            ("Young Adult (13-25)", "Elite"): (1050, 1250),
            ("Adult (26-39)", "Beginner"): (850, 1000), ("Adult (26-39)", "Intermediate"): (1000, 1200),
            ("Adult (26-39)", "Elite"): (1100, 1300),
            ("Middle Age (40-55)", "Beginner"): (800, 950), ("Middle Age (40-55)", "Intermediate"): (900, 1100),
            ("Middle Age (40-55)", "Elite"): (1000, 1200),
            ("Masters (56+)", "Beginner"): (700, 850), ("Masters (56+)", "Intermediate"): (800, 950),
            ("Masters (56+)", "Elite"): (900, 1100)
        }, suboptimal_low_mult=0.6, suboptimal_high_mult=0.6)
        add_adaptive_bands(m_time_pelvis_trunk_peak_id, {  # This is for optimal timing delay
            ("Youth (8-12)", "Beginner"): (3, 5), ("Youth (8-12)", "Intermediate"): (3, 5),
            ("Youth (8-12)", "Elite"): (3, 5),
            ("Young Adult (13-25)", "Beginner"): (3, 5), ("Young Adult (13-25)", "Intermediate"): (2, 4),
            ("Young Adult (13-25)", "Elite"): (2, 4),
            ("Adult (26-39)", "Beginner"): (3, 5), ("Adult (26-39)", "Intermediate"): (2, 4),
            ("Adult (26-39)", "Elite"): (2, 4),
            ("Middle Age (40-55)", "Beginner"): (3, 5), ("Middle Age (40-55)", "Intermediate"): (2, 4),
            ("Middle Age (40-55)", "Elite"): (2, 4),
            ("Masters (56+)", "Beginner"): (4, 6), ("Masters (56+)", "Intermediate"): (3, 5),
            ("Masters (56+)", "Elite"): (3, 5)
        })
        self._add_band(m_arm_slot_consistency_mer_id, "Elite Consistency", 0, 3, score_multiplier=1.0)
        self._add_band(m_arm_slot_consistency_mer_id, "Good Consistency", 3.1, 8, score_multiplier=0.8)
        self._add_band(m_arm_slot_consistency_mer_id, "Inconsistent Slot", 8.1, 100, score_multiplier=0.5)
        self._add_band(m_elbow_height_id, "Optimal Height", 0, 5, score_multiplier=1.0)  # 0-5cm above shoulder
        self._add_band(m_elbow_height_id, "Slightly Low", -10, -0.1, score_multiplier=0.7)  # 0 to -10cm below
        self._add_band(m_elbow_height_id, "Too Low", -10.1, -100, score_multiplier=0.3)
        self._add_band(m_elbow_height_id, "Too High", 5.1, 100, score_multiplier=0.7)
        self._add_band(m_trunk_forward_tilt_mer_id, "Optimal Forward Tilt", 20, 30, score_multiplier=1.0)
        self._add_band(m_trunk_forward_tilt_mer_id, "Too Upright", 0, 19.9, score_multiplier=0.6)
        self._add_band(m_trunk_forward_tilt_mer_id, "Excessive Tilt", 30.1, 100, score_multiplier=0.6)
        self._add_band(m_trunk_lateral_tilt_mer_id, "Optimal Lateral Tilt", 15, 25, score_multiplier=1.0)
        self._add_band(m_trunk_lateral_tilt_mer_id, "Insufficient Tilt", 0, 14.9, score_multiplier=0.6)
        self._add_band(m_trunk_lateral_tilt_mer_id, "Excessive Tilt", 25.1, 100, score_multiplier=0.6)
        self._add_band(m_kinetic_chain_sequencing_id, "Optimal Timing", 0.015, 0.025, score_multiplier=1.0)
        self._add_band(m_kinetic_chain_sequencing_id, "Slightly Off Timing", 0.005, 0.014,
                       score_multiplier=0.7)  # Too fast
        self._add_band(m_kinetic_chain_sequencing_id, "Slightly Off Timing", 0.0251, 0.035,
                       score_multiplier=0.7)  # Too slow
        self._add_band(m_kinetic_chain_sequencing_id, "Disconnected Chain", 0.0351, 1.0, score_multiplier=0.3)
        self._add_band(m_lead_leg_bracing_cocking_id, "Elite Bracing", 0, 3, score_multiplier=1.0)
        self._add_band(m_lead_leg_bracing_cocking_id, "Good Bracing", 3.1, 8, score_multiplier=0.8)
        self._add_band(m_lead_leg_bracing_cocking_id, "Poor Bracing", 8.1, 100, score_multiplier=0.5)
        self._add_band(m_glove_arm_action_id, "Optimal Action", 0, 5,
                       score_multiplier=1.0)  # deviation from ideal tucked 90deg
        self._add_band(m_glove_arm_action_id, "Suboptimal Action", 5.1, 15, score_multiplier=0.7)
        self._add_band(m_glove_arm_action_id, "Flying Open", 15.1, 100, score_multiplier=0.4)

        # --- ACCELERATION & RELEASE PHASE ---
        add_adaptive_bands(m_sir_velocity_id, {
            ("Youth (8-12)", "Beginner"): (3500, 4500), ("Youth (8-12)", "Intermediate"): (4000, 5000),
            ("Youth (8-12)", "Elite"): (4500, 5500),
            ("Young Adult (13-25)", "Beginner"): (4500, 5500), ("Young Adult (13-25)", "Intermediate"): (5500, 6500),
            ("Young Adult (13-25)", "Elite"): (6500, 7500),
            ("Adult (26-39)", "Beginner"): (5000, 6000), ("Adult (26-39)", "Intermediate"): (6000, 7000),
            ("Adult (26-39)", "Elite"): (7000, 8000),  # Elite range from text
            ("Middle Age (40-55)", "Beginner"): (4500, 5500), ("Middle Age (40-55)", "Intermediate"): (5500, 6500),
            ("Middle Age (40-55)", "Elite"): (6500, 7500),
            ("Masters (56+)", "Beginner"): (4000, 5000), ("Masters (56+)", "Intermediate"): (5000, 6000),
            ("Masters (56+)", "Elite"): (5500, 6500)
        }, suboptimal_low_mult=0.6, suboptimal_high_mult=0.6)
        add_adaptive_bands(m_elbow_extension_velocity_id, {
            ("Youth (8-12)", "Beginner"): (1500, 1800), ("Youth (8-12)", "Intermediate"): (1600, 1900),
            ("Youth (8-12)", "Elite"): (1700, 2000),
            ("Young Adult (13-25)", "Beginner"): (1700, 2000), ("Young Adult (13-25)", "Intermediate"): (1900, 2200),
            ("Young Adult (13-25)", "Elite"): (2100, 2500),
            ("Adult (26-39)", "Beginner"): (1800, 2100), ("Adult (26-39)", "Intermediate"): (2000, 2300),
            ("Adult (26-39)", "Elite"): (2200, 2600),  # Elite range from text
            ("Middle Age (40-55)", "Beginner"): (1700, 2000), ("Middle Age (40-55)", "Intermediate"): (1900, 2200),
            ("Middle Age (40-55)", "Elite"): (2100, 2400),
            ("Masters (56+)", "Beginner"): (1600, 1900), ("Masters (56+)", "Intermediate"): (1800, 2100),
            ("Masters (56+)", "Elite"): (1900, 2300)
        }, suboptimal_low_mult=0.6, suboptimal_high_mult=0.6)
        add_adaptive_bands(m_trunk_forward_tilt_release_id, {
            ("Youth (8-12)", "Beginner"): (25, 30), ("Youth (8-12)", "Intermediate"): (28, 33),
            ("Youth (8-12)", "Elite"): (30, 35),
            ("Young Adult (13-25)", "Beginner"): (28, 33), ("Young Adult (13-25)", "Intermediate"): (30, 40),
            ("Young Adult (13-25)", "Elite"): (35, 45),
            ("Adult (26-39)", "Beginner"): (30, 35), ("Adult (26-39)", "Intermediate"): (33, 43),
            ("Adult (26-39)", "Elite"): (38, 48),  # Elite range from text
            ("Middle Age (40-55)", "Beginner"): (28, 38), ("Middle Age (40-55)", "Intermediate"): (30, 40),
            ("Middle Age (40-55)", "Elite"): (35, 45),
            ("Masters (56+)", "Beginner"): (25, 35), ("Masters (56+)", "Intermediate"): (28, 38),
            ("Masters (56+)", "Elite"): (30, 40)
        })
        add_adaptive_bands(m_trunk_lateral_tilt_release_id, {
            ("Youth (8-12)", "Beginner"): (5, 10), ("Youth (8-12)", "Intermediate"): (8, 13),
            ("Youth (8-12)", "Elite"): (10, 15),
            ("Young Adult (13-25)", "Beginner"): (8, 13), ("Young Adult (13-25)", "Intermediate"): (10, 20),
            ("Young Adult (13-25)", "Elite"): (15, 25),
            ("Adult (26-39)", "Beginner"): (10, 15), ("Adult (26-39)", "Intermediate"): (12, 22),
            ("Adult (26-39)", "Elite"): (15, 25),  # Elite range from text
            ("Middle Age (40-55)", "Beginner"): (8, 13), ("Middle Age (40-55)", "Intermediate"): (10, 20),
            ("Middle Age (40-55)", "Elite"): (12, 22),
            ("Masters (56+)", "Beginner"): (5, 10), ("Masters (56+)", "Intermediate"): (8, 13),
            ("Masters (56+)", "Elite"): (10, 20)
        })
        add_adaptive_bands(m_pitch_velocity_id, {
            ("Youth (8-12)", "Beginner"): (35, 45), ("Youth (8-12)", "Intermediate"): (45, 55),
            ("Youth (8-12)", "Elite"): (55, 65),
            ("Young Adult (13-25)", "Beginner"): (50, 65), ("Young Adult (13-25)", "Intermediate"): (65, 80),
            ("Young Adult (13-25)", "Elite"): (80, 95),
            ("Adult (26-39)", "Beginner"): (60, 75), ("Adult (26-39)", "Intermediate"): (75, 90),
            ("Adult (26-39)", "Elite"): (90, 100),  # Elite range from text
            ("Middle Age (40-55)", "Beginner"): (55, 70), ("Middle Age (40-55)", "Intermediate"): (70, 85),
            ("Middle Age (40-55)", "Elite"): (85, 95),
            ("Masters (56+)", "Beginner"): (50, 60), ("Masters (56+)", "Intermediate"): (60, 75),
            ("Masters (56+)", "Elite"): (75, 85)
        }, suboptimal_low_mult=0.6, suboptimal_high_mult=0.6)
        add_adaptive_bands(m_spin_rate_perf_id, {
            ("Youth (8-12)", "Beginner"): (1000, 1400), ("Youth (8-12)", "Intermediate"): (1200, 1600),
            ("Youth (8-12)", "Elite"): (1400, 1800),
            ("Young Adult (13-25)", "Beginner"): (1300, 1700), ("Young Adult (13-25)", "Intermediate"): (1600, 2000),
            ("Young Adult (13-25)", "Elite"): (1900, 2400),
            ("Adult (26-39)", "Beginner"): (1500, 1900), ("Adult (26-39)", "Intermediate"): (1800, 2200),
            ("Adult (26-39)", "Elite"): (2100, 2500),  # Elite range from text
            ("Middle Age (40-55)", "Beginner"): (1400, 1800), ("Middle Age (40-55)", "Intermediate"): (1700, 2100),
            ("Middle Age (40-55)", "Elite"): (2000, 2400),
            ("Masters (56+)", "Beginner"): (1300, 1700), ("Masters (56+)", "Intermediate"): (1600, 2000),
            ("Masters (56+)", "Elite"): (1800, 2200)
        }, suboptimal_low_mult=0.6, suboptimal_high_mult=0.6)
        add_adaptive_bands(m_extension_performance_id, {
            ("Youth (8-12)", "Beginner"): (4.5, 5.0), ("Youth (8-12)", "Intermediate"): (5.0, 5.5),
            ("Youth (8-12)", "Elite"): (5.3, 5.8),
            ("Young Adult (13-25)", "Beginner"): (5.0, 5.5), ("Young Adult (13-25)", "Intermediate"): (5.5, 6.2),
            ("Young Adult (13-25)", "Elite"): (6.0, 6.8),
            ("Adult (26-39)", "Beginner"): (5.3, 5.8), ("Adult (26-39)", "Intermediate"): (5.8, 6.5),
            ("Adult (26-39)", "Elite"): (6.3, 7.0),  # Elite range from text
            ("Middle Age (40-55)", "Beginner"): (5.0, 5.5), ("Middle Age (40-55)", "Intermediate"): (5.5, 6.2),
            ("Middle Age (40-55)", "Elite"): (6.0, 6.7),
            ("Masters (56+)", "Beginner"): (4.8, 5.3), ("Masters (56+)", "Intermediate"): (5.3, 5.8),
            ("Masters (56+)", "Elite"): (5.8, 6.3)
        })
        add_adaptive_bands(m_release_height_perf_id, {
            ("Youth (8-12)", "Beginner"): (77, 82), ("Youth (8-12)", "Intermediate"): (78, 83),
            ("Youth (8-12)", "Elite"): (79, 84),
            ("Young Adult (13-25)", "Beginner"): (78, 83), ("Young Adult (13-25)", "Intermediate"): (79, 84),
            ("Young Adult (13-25)", "Elite"): (80, 85),
            ("Adult (26-39)", "Beginner"): (79, 84), ("Adult (26-39)", "Intermediate"): (80, 85),
            ("Adult (26-39)", "Elite"): (81, 86),  # Elite range from text
            ("Middle Age (40-55)", "Beginner"): (78, 83), ("Middle Age (40-55)", "Intermediate"): (79, 84),
            ("Middle Age (40-55)", "Elite"): (80, 85),
            ("Masters (56+)", "Beginner"): (77, 82), ("Masters (56+)", "Intermediate"): (78, 83),
            ("Masters (56+)", "Elite"): (79, 84)
        })
        self._add_band(m_release_point_consistency_id, "Elite Consistency", 0, 2, score_multiplier=1.0)
        self._add_band(m_release_point_consistency_id, "Good Consistency", 2.1, 5, score_multiplier=0.8)
        self._add_band(m_release_point_consistency_id, "Inconsistent Release", 5.1, 100, score_multiplier=0.5)
        self._add_band(m_arm_slot_at_release_id, "Elite Consistency", 1, 2, score_multiplier=1.0)  # SD
        self._add_band(m_arm_slot_at_release_id, "Good Consistency", 2.1, 4, score_multiplier=0.8)
        self._add_band(m_arm_slot_at_release_id, "Inconsistent Slot", 4.1, 100, score_multiplier=0.5)
        self._add_band(m_stride_length_to_release_id, "Optimal Extension", 85, 95, score_multiplier=1.0)  # % Height
        self._add_band(m_stride_length_to_release_id, "Insufficient Extension", 0, 84.9, score_multiplier=0.6)
        self._add_band(m_stride_length_to_release_id, "Excessive Extension", 95.1, 150, score_multiplier=0.6)
        self._add_band(m_trunk_stabilization_id, "Elite Stabilization", 0, 5, score_multiplier=1.0)  # degrees change
        self._add_band(m_trunk_stabilization_id, "Good Stabilization", 5.1, 10, score_multiplier=0.8)
        self._add_band(m_trunk_stabilization_id, "Poor Stabilization", 10.1, 100, score_multiplier=0.5)
        self._add_band(m_hand_position_at_release_id, "Optimal Position", 1, 2,
                       score_multiplier=1.0)  # degrees variation
        self._add_band(m_hand_position_at_release_id, "Good Position", 2.1, 5, score_multiplier=0.8)
        self._add_band(m_hand_position_at_release_id, "Poor Position", 5.1, 100, score_multiplier=0.5)

        # --- FOLLOW-THROUGH PHASE ---
        # Note: Qualitative aspects need custom score_function or simplified bands
        add_adaptive_bands(m_follow_through_length_id,
                           {  # Ranges here are dummy for "Limited", "Moderate", "Full", "Complete"
                               ("Youth (8-12)", "Beginner"): (0, 0.25), ("Youth (8-12)", "Intermediate"): (0.26, 0.5),
                               ("Youth (8-12)", "Elite"): (0.51, 0.75),
                               ("Young Adult (13-25)", "Beginner"): (0.26, 0.5),
                               ("Young Adult (13-25)", "Intermediate"): (0.51, 0.75),
                               ("Young Adult (13-25)", "Elite"): (0.76, 1.0),
                               ("Adult (26-39)", "Beginner"): (0.51, 0.75),
                               ("Adult (26-39)", "Intermediate"): (0.76, 1.0), ("Adult (26-39)", "Elite"): (0.9, 1.0),
                               # Assuming 0.9-1.0 is "complete"
                               ("Middle Age (40-55)", "Beginner"): (0.51, 0.75),
                               ("Middle Age (40-55)", "Intermediate"): (0.76, 1.0),
                               ("Middle Age (40-55)", "Elite"): (0.9, 1.0),
                               ("Masters (56+)", "Beginner"): (0, 0.25), ("Masters (56+)", "Intermediate"): (0.26, 0.5),
                               ("Masters (56+)", "Elite"): (0.51, 0.75)
                           })
        add_adaptive_bands(m_balance_recovery_ft_id, {
            ("Youth (8-12)", "Beginner"): (0.8, 1.0), ("Youth (8-12)", "Intermediate"): (0.7, 0.9),
            ("Youth (8-12)", "Elite"): (0.6, 0.8),
            ("Young Adult (13-25)", "Beginner"): (0.7, 0.9), ("Young Adult (13-25)", "Intermediate"): (0.5, 0.7),
            ("Young Adult (13-25)", "Elite"): (0.4, 0.6),
            ("Adult (26-39)", "Beginner"): (0.6, 0.8), ("Adult (26-39)", "Intermediate"): (0.4, 0.6),
            ("Adult (26-39)", "Elite"): (0.3, 0.5),
            ("Middle Age (40-55)", "Beginner"): (0.7, 0.9), ("Middle Age (40-55)", "Intermediate"): (0.5, 0.7),
            ("Middle Age (40-55)", "Elite"): (0.4, 0.6),
            ("Masters (56+)", "Beginner"): (0.8, 1.0), ("Masters (56+)", "Intermediate"): (0.7, 0.9),
            ("Masters (56+)", "Elite"): (0.5, 0.7)
        })
        # For qualitative "Front Leg at Finish" and "Fielding Position", use dummy numeric ranges
        add_adaptive_bands(m_front_leg_at_finish_id, {  # Dummy numeric range for categories
            ("Youth (8-12)", "Beginner"): (0, 0.25), ("Youth (8-12)", "Intermediate"): (0.26, 0.5),
            ("Youth (8-12)", "Elite"): (0.51, 0.75),
            ("Young Adult (13-25)", "Beginner"): (0.26, 0.5), ("Young Adult (13-25)", "Intermediate"): (0.51, 0.75),
            ("Young Adult (13-25)", "Elite"): (0.76, 1.0),
            ("Adult (26-39)", "Beginner"): (0.51, 0.75), ("Adult (26-39)", "Intermediate"): (0.76, 1.0),
            ("Adult (26-39)", "Elite"): (0.9, 1.0),
            ("Middle Age (40-55)", "Beginner"): (0.51, 0.75), ("Middle Age (40-55)", "Intermediate"): (0.76, 1.0),
            ("Middle Age (40-55)", "Elite"): (0.9, 1.0),
            ("Masters (56+)", "Beginner"): (0, 0.25), ("Masters (56+)", "Intermediate"): (0.26, 0.5),
            ("Masters (56+)", "Elite"): (0.51, 0.75)
        })
        add_adaptive_bands(m_fielding_position_id, {  # Dummy numeric range for categories
            ("Youth (8-12)", "Beginner"): (0, 0.25), ("Youth (8-12)", "Intermediate"): (0.26, 0.5),
            ("Youth (8-12)", "Elite"): (0.51, 0.75),
            ("Young Adult (13-25)", "Beginner"): (0.26, 0.5), ("Young Adult (13-25)", "Intermediate"): (0.51, 0.75),
            ("Young Adult (13-25)", "Elite"): (0.76, 1.0),
            ("Adult (26-39)", "Beginner"): (0.51, 0.75), ("Adult (26-39)", "Intermediate"): (0.76, 1.0),
            ("Adult (26-39)", "Elite"): (0.9, 1.0),
            ("Middle Age (40-55)", "Beginner"): (0.51, 0.75), ("Middle Age (40-55)", "Intermediate"): (0.76, 1.0),
            ("Middle Age (40-55)", "Elite"): (0.9, 1.0),
            ("Masters (56+)", "Beginner"): (0, 0.25), ("Masters (56+)", "Intermediate"): (0.26, 0.5),
            ("Masters (56+)", "Elite"): (0.51, 0.75)
        })
        self._add_band(m_deceleration_path_efficiency_id, "Optimal Path", 60, 80, score_multiplier=1.0)
        self._add_band(m_deceleration_path_efficiency_id, "Abrupt Stopping", 0, 44.9, score_multiplier=0.4)
        self._add_band(m_deceleration_path_efficiency_id, "Good Path", 45, 59.9,
                       score_multiplier=0.8)  # Between abrupt and optimal
        self._add_band(m_deceleration_path_efficiency_id, "Excessive Arc", 80.1, 180, score_multiplier=0.6)
        self._add_band(m_controlled_eccentricity_id, "Optimal Slowdown", 25, 35, score_multiplier=1.0)
        self._add_band(m_controlled_eccentricity_id, "Too Fast", 35.1, 50, score_multiplier=0.7)
        self._add_band(m_controlled_eccentricity_id, "Abrupt Deceleration", 50.1, 100, score_multiplier=0.4)
        self._add_band(m_controlled_eccentricity_id, "Too Slow", 0, 24.9, score_multiplier=0.6)
        self._add_band(m_balance_retention_id, "Elite Balance", 0, 5, score_multiplier=1.0)
        self._add_band(m_balance_retention_id, "Good Balance", 5.1, 10, score_multiplier=0.8)
        self._add_band(m_balance_retention_id, "Poor Balance", 10.1, 100, score_multiplier=0.5)
        self._add_band(m_recovery_position_time_id, "Optimal Recovery", 0.3, 0.5, score_multiplier=1.0)
        self._add_band(m_recovery_position_time_id, "Slow Recovery", 0.51, 0.8, score_multiplier=0.7)
        self._add_band(m_recovery_position_time_id, "Very Slow Recovery", 0.81, 5, score_multiplier=0.4)
        self._add_band(m_recovery_position_time_id, "Too Fast Recovery", 0, 0.29,
                       score_multiplier=0.6)  # If it's too fast and unstable
        self._add_band(m_front_knee_control_id, "Optimal Control", 10, 20, score_multiplier=1.0)
        self._add_band(m_front_knee_control_id, "Slight Collapse/Extension", 0, 9.9, score_multiplier=0.7)
        self._add_band(m_front_knee_control_id, "Slight Collapse/Extension", 20.1, 30, score_multiplier=0.7)
        self._add_band(m_front_knee_control_id, "Poor Control (Collapse/Hyperextension)", 30.1, 100,
                       score_multiplier=0.4)
        self._add_band(m_rotational_completion_id, "Optimal Completion", 80, 100, score_multiplier=1.0)
        self._add_band(m_rotational_completion_id, "Incomplete Rotation", 0, 69.9, score_multiplier=0.4)
        self._add_band(m_rotational_completion_id, "Good Completion", 70, 79.9,
                       score_multiplier=0.7)  # Between incomplete and optimal
        self._add_band(m_head_position_tracking_id, "Elite Tracking", 0, 4, score_multiplier=1.0)
        self._add_band(m_head_position_tracking_id, "Good Tracking", 4.1, 8, score_multiplier=0.8)
        self._add_band(m_head_position_tracking_id, "Poor Tracking", 8.1, 100, score_multiplier=0.5)
        self._add_band(m_energy_dissipation_rate_id, "Optimal Dissipation", 30, 40, score_multiplier=1.0)
        self._add_band(m_energy_dissipation_rate_id, "Too Fast", 40.1, 60, score_multiplier=0.7)
        self._add_band(m_energy_dissipation_rate_id, "Abrupt Dissipation", 60.1, 100, score_multiplier=0.4)
        self._add_band(m_energy_dissipation_rate_id, "Too Slow", 0, 29.9,
                       score_multiplier=0.6)  # If energy is not dissipated enough

        # --- PITCH TYPE-SPECIFIC METRICS ---
        self._add_band(m_fb_spin_efficiency_id, "Optimal Spin Efficiency", 90, 100, score_multiplier=1.0)
        self._add_band(m_fb_spin_efficiency_id, "Good Spin Efficiency", 80, 89.9, score_multiplier=0.8)
        self._add_band(m_fb_spin_efficiency_id, "Poor Spin Efficiency", 0, 79.9, score_multiplier=0.5)
        # For Ball Axis, 12:00-1:00 is optimal. Let's represent this as deviation from 0.5 (center of 12-1)
        # Assuming 0=12:00, 1=1:00, 0.5 is ideal.
        self._add_band(m_fb_ball_axis_id, "Optimal Axis", 0.25, 0.75, target_value=0.5, score_multiplier=1.0)
        self._add_band(m_fb_ball_axis_id, "Acceptable Axis", 0, 0.24, target_value=0.5, score_multiplier=0.7)
        self._add_band(m_fb_ball_axis_id, "Acceptable Axis", 0.76, 1.0, target_value=0.5, score_multiplier=0.7)
        self._add_band(m_fb_ball_axis_id, "Poor Axis", 1.01, 10, target_value=0.5,
                       score_multiplier=0.3)  # Max deviation 10 for safety
        self._add_band(m_two_seam_horizontal_movement_id, "Optimal Movement", 6, 14, score_multiplier=1.0)
        self._add_band(m_two_seam_horizontal_movement_id, "Insufficient Movement", 0, 5.9, score_multiplier=0.6)
        self._add_band(m_two_seam_horizontal_movement_id, "Excessive Movement", 14.1, 50,
                       score_multiplier=0.6)  # Max 50 for safety
        self._add_band(m_changeup_velocity_diff_id, "Optimal Differential", 8, 12, score_multiplier=1.0)
        self._add_band(m_changeup_velocity_diff_id, "Insufficient Differential", 0, 7.9, score_multiplier=0.6)
        self._add_band(m_changeup_velocity_diff_id, "Excessive Differential", 12.1, 30,
                       score_multiplier=0.6)  # Max 30 for safety
        self._add_band(m_curveball_spin_rate_id, "Optimal Spin Rate", 2600, 3000, score_multiplier=1.0)
        self._add_band(m_curveball_spin_rate_id, "High Spin Rate", 3000.1, 4000, score_multiplier=0.9)
        self._add_band(m_curveball_spin_rate_id, "Low Spin Rate", 0, 2599.9, score_multiplier=0.6)
        # For Curveball Spin Axis, 6:00-7:00 is optimal. Let's use deviation from 6:30 (0.5 for a 0-1 hour range)
        self._add_band(m_curveball_spin_axis_id, "Optimal Axis", 0.25, 0.75, target_value=0.5,
                       score_multiplier=1.0)  # Dummy 0-1 for 6-7 o'clock range
        self._add_band(m_curveball_spin_axis_id, "Acceptable Axis", 0, 0.24, target_value=0.5, score_multiplier=0.7)
        self._add_band(m_curveball_spin_axis_id, "Acceptable Axis", 0.76, 1.0, target_value=0.5, score_multiplier=0.7)
        self._add_band(m_curveball_spin_axis_id, "Poor Axis", 1.01, 10, target_value=0.5,
                       score_multiplier=0.3)  # Max deviation 10 for safety
        self._add_band(m_slider_gyro_component_id, "Optimal Gyro Component", 10, 30, score_multiplier=1.0)
        self._add_band(m_slider_gyro_component_id, "Low Gyro Component", 0, 9.9, score_multiplier=0.6)
        self._add_band(m_slider_gyro_component_id, "High Gyro Component", 30.1, 100, score_multiplier=0.6)
        self._add_band(m_slider_break_ratio_id, "Optimal Break Ratio", 1.2, 1.8, score_multiplier=1.0)
        self._add_band(m_slider_break_ratio_id, "Suboptimal Break Ratio", 0, 1.19, score_multiplier=0.6)
        self._add_band(m_slider_break_ratio_id, "Suboptimal Break Ratio", 1.81, 10, score_multiplier=0.6)
        # For Slider Release Spin Direction, 9:00-10:30 is optimal. Using deviation for a 0-1.5 hour range
        self._add_band(m_slider_release_spin_direction_id, "Optimal Direction", 0.25, 1.25, target_value=0.75,
                       score_multiplier=1.0)  # Dummy 0-1.5 for 9-10:30 o'clock range
        self._add_band(m_slider_release_spin_direction_id, "Acceptable Direction", 0, 0.24, target_value=0.75,
                       score_multiplier=0.7)
        self._add_band(m_slider_release_spin_direction_id, "Acceptable Direction", 1.26, 2.0, target_value=0.75,
                       score_multiplier=0.7)
        self._add_band(m_slider_release_spin_direction_id, "Poor Direction", 2.01, 10, target_value=0.75,
                       score_multiplier=0.3)  # Max deviation 10 for safety

        # --- KINETIC CHAIN EFFICIENCY METRICS ---
        self._add_band(m_grf_utilization_id, "Optimal Utilization", 1.2, 1.5, score_multiplier=1.0)
        self._add_band(m_grf_utilization_id, "Insufficient Force", 0, 1.19, score_multiplier=0.5)
        self._add_band(m_pelvis_trunk_timing_id, "Optimal Timing", 0.015, 0.025, score_multiplier=1.0)
        self._add_band(m_pelvis_trunk_timing_id, "Premature Timing", 0, 0.0149, score_multiplier=0.6)
        self._add_band(m_pelvis_trunk_timing_id, "Delayed Timing", 0.0251, 0.035, score_multiplier=0.6)
        self._add_band(m_pelvis_trunk_timing_id, "Disconnected", 0.0351, 1, score_multiplier=0.3)
        self._add_band(m_trunk_arm_timing_id, "Optimal Timing", 0.015, 0.025, score_multiplier=1.0)
        self._add_band(m_trunk_arm_timing_id, "Premature Timing", 0, 0.0149, score_multiplier=0.6)
        self._add_band(m_trunk_arm_timing_id, "Delayed Timing", 0.0251, 0.035, score_multiplier=0.6)
        self._add_band(m_trunk_arm_timing_id, "Disconnected", 0.0351, 1, score_multiplier=0.3)
        self._add_band(m_energy_transfer_efficiency_id, "Elite Efficiency", 80, 90, score_multiplier=1.0)
        self._add_band(m_energy_transfer_efficiency_id, "Good Efficiency", 70, 79.9, score_multiplier=0.8)
        self._add_band(m_energy_transfer_efficiency_id, "Energy Leakage", 0, 69.9, score_multiplier=0.5)
        self._add_band(m_joint_torque_distribution_id, "Balanced Loading", 0, 25, score_multiplier=1.0)
        self._add_band(m_joint_torque_distribution_id, "Suboptimal Loading", 25.1, 40, score_multiplier=0.7)
        self._add_band(m_joint_torque_distribution_id, "Overloading Joints", 40.1, 100, score_multiplier=0.4)
        self._add_band(m_movement_plane_consistency_id, "Elite Consistency", 0, 5, score_multiplier=1.0)
        self._add_band(m_movement_plane_consistency_id, "Good Consistency", 5.1, 10, score_multiplier=0.8)
        self._add_band(m_movement_plane_consistency_id, "Wasted Motion", 10.1, 100, score_multiplier=0.5)

        # --- INJURY RISK METRICS ---
        self._add_band(m_shoulder_mer_risk_id, "Safe Zone", 0, 185, score_multiplier=1.0)
        self._add_band(m_shoulder_mer_risk_id, "Warning Zone", 185.1, 195, score_multiplier=0.7,
                       invert_score_display=True)
        self._add_band(m_shoulder_mer_risk_id, "Critical Zone", 195.1, 360,
                       score_multiplier=0.1)  # Max possible is 360 for degrees
        self._add_band(m_elbow_valgus_torque_id, "Safe Zone", 0, 40, score_multiplier=1.0)
        self._add_band(m_elbow_valgus_torque_id, "Warning Zone", 40.1, 55, score_multiplier=0.7,
                       invert_score_display=True)
        self._add_band(m_elbow_valgus_torque_id, "Critical Zone", 55.1, 100,
                       score_multiplier=0.1)  # Max Nm is typically around 100 for pitcher
        self._add_band(m_lead_knee_extension_rate_id, "Safe Zone", 0, 250, score_multiplier=1.0)
        self._add_band(m_lead_knee_extension_rate_id, "Warning Zone", 250.1, 350, score_multiplier=0.7,
                       invert_score_display=True)
        self._add_band(m_lead_knee_extension_rate_id, "Critical Zone", 350.1, 500,
                       score_multiplier=0.1)  # Max rate 500 for safety
        self._add_band(m_shoulder_horizontal_abduction_id, "Safe Zone", 0, 15, score_multiplier=1.0)
        self._add_band(m_shoulder_horizontal_abduction_id, "Warning Zone", 15.1, 25, score_multiplier=0.7,
                       invert_score_display=True)
        self._add_band(m_shoulder_horizontal_abduction_id, "Critical Zone", 25.1, 90,
                       score_multiplier=0.1)  # Max abduction is 90
        self._add_band(m_trunk_lateral_tilt_timing_risk_id, "Safe Zone", 0, 15, score_multiplier=1.0)
        self._add_band(m_trunk_lateral_tilt_timing_risk_id, "Warning Zone", 15.1, 25, score_multiplier=0.7,
                       invert_score_display=True)
        self._add_band(m_trunk_lateral_tilt_timing_risk_id, "Critical Zone", 25.1, 90,
                       score_multiplier=0.1)  # Max tilt 90
        self._add_band(m_inverted_w_position_id, "Safe Zone", 0, 2, score_multiplier=1.0)
        self._add_band(m_inverted_w_position_id, "Warning Zone", 2.1, 5, score_multiplier=0.7,
                       invert_score_display=True)
        self._add_band(m_inverted_w_position_id, "Critical Zone", 5.1, 10, score_multiplier=0.1)
        self._add_band(m_deceleration_control_risk_id, "Safe Zone", 0, 60,
                       score_multiplier=1.0)  # Lower is better, but optimal range is 30-40. So 0-60 is range of goodness.
        self._add_band(m_deceleration_control_risk_id, "Warning Zone", 60.1, 80, score_multiplier=0.7,
                       invert_score_display=True)
        self._add_band(m_deceleration_control_risk_id, "Critical Zone", 80.1, 100, score_multiplier=0.1)
        self._add_band(m_premature_trunk_rotation_id, "Safe Zone", 0, 30, score_multiplier=1.0)
        self._add_band(m_premature_trunk_rotation_id, "Warning Zone", 30.1, 50, score_multiplier=0.7,
                       invert_score_display=True)
        self._add_band(m_premature_trunk_rotation_id, "Critical Zone", 50.1, 100, score_multiplier=0.1)

    def _get_metric_data(self, metric_name):
        """Retrieves metric details and its associated bands from the simulated DB."""
        metric = self.metrics_db.get(metric_name)
        if not metric:
            return None

        metric_id = metric["id"]
        bands = [b for b in self.bands_db if b["metric_id"] == metric_id]

        # Add bands to metric data for easy access by scoring functions
        metric["bands"] = bands
        return metric

    def _pick_appropriate_band(self, value, bands_for_metric, age_group=None, skill_level=None):
        """
        Helper to select the most appropriate band from a list of bands.
        Filters by age/skill and then finds the range match.
        """
        eligible_bands = []
        for band in bands_for_metric:
            band_age = band.get("age_group")
            band_skill = band.get("skill_level")

            # If the band has age/skill specified, it must match the pitcher's profile
            if band_age is not None and band_skill is not None:
                if band_age == age_group and band_skill == skill_level:
                    eligible_bands.append(band)
            # If the band doesn't have age/skill, it's a general/fixed band and should be considered
            # This logic means fixed bands apply if no specific adaptive band is available or matches.
            elif band_age is None and band_skill is None:
                eligible_bands.append(band)

        # Priority for band matching: exact target, then ranges.
        # This order is important if bands could overlap.
        for band in eligible_bands:
            min_val = band.get("min_value")
            max_val = band.get("max_value")
            target_val = band.get("target_value")

            # 1. Check for target value match (if target is defined for this band)
            if target_val is not None:
                # If band specifies a range around the target
                if min_val is not None and max_val is not None:
                    if min_val <= value <= max_val:
                        return band
                # If band is solely defined by a target (e.g., exact match needed)
                elif abs(value - target_val) < 1e-6:  # Use epsilon for float comparison
                    return band

            # 2. Check for range-based match (min_value, max_value)
            if min_val is not None and max_val is not None:
                if min_val <= value <= max_val:
                    return band
            # 3. Check for min-only band (value >= min_value)
            elif min_val is not None and max_val is None:
                if value >= min_val:
                    return band
            # 4. Check for max-only band (value <= max_value)
            elif max_val is not None and min_val is None:
                if value <= max_val:
                    return band

        return None  # No band matched

    # --- Specific Scoring Functions (referenced by metric.score_function) ---

    def _get_base_score_for_optimal_bands(self, value, selected_band):
        """
        Helper to determine if the band is an 'optimal' type and should return 100 base score.
        """
        if selected_band.get("invert_score_display", False):  # Inverted bands are not 'Optimal' in this sense
            return None  # Not an optimal band for this rule.

        optimal_keywords = ["Optimal", "Elite", "Safe Zone"]
        for keyword in optimal_keywords:
            if keyword in selected_band['name']:
                # If the value is strictly within the band's min/max (or matches min/max if they are boundaries)
                if (selected_band['min_value'] is not None and selected_band['max_value'] is not None and selected_band[
                    'min_value'] <= value <= selected_band['max_value']) or \
                        (selected_band['min_value'] is not None and selected_band['max_value'] is None and value >=
                         selected_band['min_value']) or \
                        (selected_band['max_value'] is not None and selected_band['min_value'] is None and value <=
                         selected_band['max_value']):
                    return 100.0
        return None  # Not an optimal band, or value is outside its precise range for this rule.

    def score_standard_range_metric(self, value, metric_data, age_group, skill_level):
        """
        Scores metrics that have discrete ranges, where values within a matched band's range get 100% base score.
        """
        selected_band = self._pick_appropriate_band(value, metric_data["bands"], age_group, skill_level)
        if selected_band is None: return 0.0, "Value out of defined bands"

        base_score = self._get_base_score_for_optimal_bands(value, selected_band)
        if base_score is not None:
            return self._apply_final_score_modifiers(base_score, selected_band)

        # For other bands (not "Optimal/Elite/Safe Zone" but still in this scoring function)
        # Assume a flat 100 if the value is within the matched band's defined range,
        # as the score_multiplier will penalize appropriately.
        base_score = 100.0  # If the band was picked, the value is in its defined range

        return self._apply_final_score_modifiers(base_score, selected_band)

    def score_adaptive_range_metric(self, value, metric_data, age_group, skill_level):
        """
        Scores metrics with adaptive ranges (different optimal ranges for different age/skill levels).
        Assumes bands like "Optimal", "Suboptimal Low", "Suboptimal High", "Critical Low/High" are defined.
        """
        selected_band = self._pick_appropriate_band(value, metric_data["bands"], age_group, skill_level)
        if selected_band is None: return 0.0, "Value out of defined bands"

        base_score = self._get_base_score_for_optimal_bands(value, selected_band)
        if base_score is not None:
            return self._apply_final_score_modifiers(base_score, selected_band)

        # For other bands (Suboptimal, Critical) where a gradient is expected
        min_val = selected_band.get("min_value")
        max_val = selected_band.get("max_value")

        if min_val is None and max_val is None:
            base_score = 0.0  # Should not happen with well-defined bands
        elif min_val is not None and max_val is not None:
            if (max_val - min_val) == 0:  # Handle single point range
                base_score = 100.0 if value == min_val else 0.0
            # For "Suboptimal Low" or "Critical Low" bands, scale towards max_val (upper boundary is "better")
            elif "Suboptimal Low" in selected_band['name'] or "Critical Low" in selected_band['name']:
                base_score = 100.0 * (value - min_val) / (max_val - min_val)
            # For "Suboptimal High" or "Critical High" bands, scale towards min_val (lower boundary is "better")
            elif "Suboptimal High" in selected_band['name'] or "Critical High" in selected_band['name']:
                base_score = 100.0 * (max_val - value) / (max_val - min_val)
            else:  # Default for other non-optimal ranges (if matched, they should be flat 100 base score usually)
                base_score = 100.0
        elif min_val is not None and value >= min_val:  # Min-only band (should be rare for gradient bands)
            base_score = 100.0
        elif max_val is not None and value <= max_val:  # Max-only band (should be rare for gradient bands)
            base_score = 100.0
        else:
            base_score = 0.0  # Fallback

        return self._apply_final_score_modifiers(base_score, selected_band)

    def score_higher_is_better_metric(self, value, metric_data, age_group, skill_level):
        """
        Scores metrics where higher values are always better, linearly scaling within bands.
        """
        selected_band = self._pick_appropriate_band(value, metric_data["bands"], age_group, skill_level)
        if selected_band is None: return 0.0, "Value out of defined bands"

        base_score = self._get_base_score_for_optimal_bands(value, selected_band)
        if base_score is not None:
            return self._apply_final_score_modifiers(base_score, selected_band)

        # For other bands (not "Optimal/Elite/Safe Zone") where a gradient is expected
        min_val = selected_band.get("min_value")
        max_val = selected_band.get("max_value")

        # Use the band's min/max as the scaling range. If None, use reasonable defaults.
        effective_min = min_val if min_val is not None else 0.0
        effective_max = max_val if max_val is not None else value * 2  # Or a very large constant if no upper bound

        if effective_max == effective_min:  # Avoid division by zero
            base_score = 100.0 if value >= effective_max else 0.0
        elif value >= effective_max:
            base_score = 100.0
        elif value <= effective_min:
            base_score = 0.0
        else:  # Value is strictly between effective_min and effective_max
            base_score = 100.0 * (value - effective_min) / (effective_max - effective_min)

        return self._apply_final_score_modifiers(base_score, selected_band)

    def score_lower_is_better_metric(self, value, metric_data, age_group, skill_level):
        """
        Scores metrics where lower values are always better, linearly scaling within bands.
        """
        selected_band = self._pick_appropriate_band(value, metric_data["bands"], age_group, skill_level)
        if selected_band is None: return 0.0, "Value out of defined bands"

        base_score = self._get_base_score_for_optimal_bands(value, selected_band)
        if base_score is not None:
            return self._apply_final_score_modifiers(base_score, selected_band)

        # For other bands (not "Optimal/Elite/Safe Zone") where a gradient is expected
        min_val = selected_band.get("min_value")
        max_val = selected_band.get("max_value")

        # Use the band's min/max as the scaling range. If None, use reasonable defaults.
        effective_min = min_val if min_val is not None else value * 0.5  # Or a very small constant
        effective_max = max_val if max_val is not None else value * 2  # Or a very large constant

        if effective_max == effective_min:  # Avoid division by zero
            base_score = 100.0 if value <= effective_min else 0.0
        elif value <= effective_min:  # Value is at or below the "best" end of the band's range
            base_score = 100.0
        elif value >= effective_max:  # Value is at or above the "worst" end of the band's range
            base_score = 0.0
        else:  # Value is strictly between effective_min and effective_max
            base_score = 100.0 * (effective_max - value) / (effective_max - effective_min)

        return self._apply_final_score_modifiers(base_score, selected_band)

    def score_target_based_metric(self, value, metric_data, age_group, skill_level):
        """
        Scores metrics with a specific target value (e.g., consistency metrics),
        using a Gaussian curve where the score is highest at the target.
        """
        selected_band = self._pick_appropriate_band(value, metric_data["bands"], age_group, skill_level)
        if selected_band is None: return 0.0, "Value out of defined bands"

        base_score = self._get_base_score_for_optimal_bands(value, selected_band)
        if base_score is not None:
            return self._apply_final_score_modifiers(base_score, selected_band)

        # For other bands (not "Optimal/Elite/Safe Zone") where a Gaussian gradient is expected
        target_val = selected_band.get("target_value")
        if target_val is None: return 0.0, "Target value not defined for band."

        std_dev = 0.5  # Default std_dev. Can be tuned per metric/band.
        if selected_band.get("min_value") is not None and selected_band.get("max_value") is not None:
            band_range = selected_band["max_value"] - selected_band["min_value"]
            if band_range > 0:
                std_dev = band_range / 4  # Assuming the band range covers +/- 2 standard deviations from target
            else:  # Single point range
                std_dev = 0.1  # Very small std_dev for very tight target

        if std_dev == 0:  # Avoid division by zero
            base_score = 100.0 if abs(value - target_val) < 1e-6 else 0.0  # Exact match for 100
        else:
            base_score = 100.0 * math.exp(-0.5 * ((value - target_val) / std_dev) ** 2)

        return self._apply_final_score_modifiers(base_score, selected_band)

    def score_risk_metric(self, value, metric_data, age_group, skill_level):
        """
        Scores injury risk metrics with specific 'Safe', 'Warning', 'Critical' zones.
        Applies inversion for 'Warning Zone' as per Anne's request.
        """
        selected_band = self._pick_appropriate_band(value, metric_data["bands"], age_group, skill_level)
        if selected_band is None: return 0.0, "Value out of defined risk zones"

        base_score = self._get_base_score_for_optimal_bands(value, selected_band)
        if base_score is not None:  # If it's a "Safe Zone" band
            return self._apply_final_score_modifiers(base_score, selected_band)

        # For "Warning" and "Critical" zones, where a gradient is expected.
        # Lower values (closer to min_val) in these bands are "better" (less risky).
        min_val = selected_band.get("min_value")
        max_val = selected_band.get("max_value")

        effective_min = min_val if min_val is not None else value
        effective_max = max_val if max_val is not None else value

        if effective_min == effective_max:
            base_score = 100.0 if value <= effective_min else 0.0
        elif value <= effective_min:  # Value is at or below the "safer" end of this risk band
            base_score = 100.0
        elif value >= effective_max:  # Value is at or above the "riskier" end of this risk band
            base_score = 0.0
        else:  # Value is strictly between min_val and max_val of this risk band
            base_score = 100.0 * (effective_max - value) / (effective_max - effective_min)

        return self._apply_final_score_modifiers(base_score, selected_band)

    # --- Helper to apply common final modifiers ---
    def _apply_final_score_modifiers(self, base_score, band):
        """Applies score_multiplier and conditional inversion."""
        final_score = base_score * band.get("score_multiplier", 1.0)

        if band.get("invert_score_display", False):
            final_score = 100.0 - final_score

        return max(0.0, min(100.0, final_score)), band["name"]  # Return final score and band name

    # --- Main Calculation Orchestrator ---
    def calculate_metric_score(self, metric_name, value, age_group=None, skill_level=None):
        """
        Main function to calculate the final score for a given metric using its defined score_function.
        """
        metric_data = self._get_metric_data(metric_name)
        if not metric_data:
            return 0.0, "Metric not found.", "N/A", {}  # Score, Interpretation, Band Name, Metric Info

        score_function_name = metric_data.get("score_function")
        if not score_function_name or not hasattr(self, score_function_name):
            return 0.0, f"Scoring function '{score_function_name}' not found for metric.", "N/A", metric_data

        # Dynamically call the scoring function defined for this metric
        scoring_method = getattr(self, score_function_name)

        # All specific scoring methods return (final_score, band_name)
        final_score, band_name = scoring_method(value, metric_data, age_group, skill_level)

        interpretation = self.get_score_interpretation(final_score, metric_data['is_risk_metric'])

        return final_score, interpretation, band_name, metric_data

    # --- Helper to interpret score (was missing) ---
    def get_score_interpretation(self, score, is_risk_metric=False):
        """Get interpretation and emoji for score."""
        if is_risk_metric:
            if score >= 90:
                return "SAFE 🟢"
            elif score >= 75:
                return "LOW RISK 🟡"
            elif score >= 25:
                return "MODERATE RISK 🟠"
            else:
                return "HIGH RISK 🔴"
        else:
            if score >= 90:
                return "ELITE 🟢"
            elif score >= 75:
                return "GOOD 🟡"
            elif score >= 50:
                return "NEEDS IMPROVEMENT 🟠"
            else:
                return "CRITICAL ISSUE 🔴"

    # --- User Interface Functions (remain largely the same) ---
    def display_metrics_menu(self):
        """Displays available metrics to the user."""
        print(f"\n" + "=" * 70)
        print("AVAILABLE METRICS")
        print("=" * 70)
        sorted_metrics = sorted(self.metrics_db.values(), key=lambda x: x['name'])
        metric_map = {}
        for i, metric in enumerate(sorted_metrics):
            print(f"{i + 1:2d}. {metric['name']} ({metric['unit']})")
            metric_map[i + 1] = metric['name']
        print(f"\n{len(sorted_metrics) + 1}. Exit")
        return metric_map, len(sorted_metrics) + 1

    def get_user_profile(self):
        """Gets user's age group and skill level for adaptive metrics."""
        print(f"\n" + "=" * 60)
        print("PITCHER PROFILE SETUP")
        print("=" * 60)

        print("\nSelect your age group:")
        for key, value in self.age_groups_map.items():
            print(f"{key}. {value}")

        selected_age = None
        while selected_age is None:
            try:
                age_choice = int(input("\nEnter age group (1-5): "))
                if age_choice in self.age_groups_map:
                    selected_age = self.age_groups_map[age_choice]
                else:
                    print("❌ Please select a valid age group (1-5)")
            except ValueError:
                print("❌ Please enter a valid number")

        print(f"\nSelect your skill level:")
        for key, value in self.skill_levels_map.items():
            print(f"{key}. {value}")

        selected_skill = None
        while selected_skill is None:
            try:
                skill_choice = int(input("\nEnter skill level (1-3): "))
                if skill_choice in self.skill_levels_map:
                    selected_skill = self.skill_levels_map[skill_choice]
                else:
                    print("❌ Please select a valid skill level (1-3)")
            except ValueError:
                print("❌ Please enter a valid number")

        return selected_age, selected_skill

    def run_calculator(self):
        """Main program loop."""
        print("🥎 Welcome to SightFX Baseball Pitching Metrics Calculator!")
        print("This tool simulates scoring based on a database-driven band system.")

        # Get pitcher profile once at the start
        age_group, skill_level = self.get_user_profile()

        while True:
            metric_map, exit_choice_num = self.display_metrics_menu()

            try:
                choice = int(input(f"\nSelect a metric to score (1-{exit_choice_num}): "))

                if choice == exit_choice_num:
                    print("\n🙏 Thank you for using SightFX Metrics Calculator!")
                    break

                if choice not in metric_map:
                    print("❌ Invalid selection. Please try again.")
                    continue

                selected_metric_name = metric_map[choice]
                metric_info = self._get_metric_data(selected_metric_name)

                print(f"\n" + "=" * 70)
                print(f"SCORING: {selected_metric_name}")
                print("=" * 70)
                print(f"Description: {metric_info['description']}")
                print(f"Unit: {metric_info['unit']}")
                print(f"Your Profile: {age_group} - {skill_level}")

                # Show relevant bands for the selected profile and metric
                print("\nApplicable Bands for Your Profile:")
                found_bands = False
                for band in metric_info['bands']:
                    is_adaptive_band = (band.get('age_group') is not None or band.get('skill_level') is not None)
                    is_profile_match = (band.get('age_group') == age_group and band.get('skill_level') == skill_level)

                    # Display logic: Show bands that are general, OR specific to the user's profile
                    if (not is_adaptive_band) or (is_adaptive_band and is_profile_match):
                        found_bands = True
                        range_str = ""
                        if band['min_value'] is not None and band['max_value'] is not None:
                            range_str += f"{band['min_value']}-{band['max_value']}{metric_info['unit']} "
                        elif band['min_value'] is not None:
                            range_str += f">={band['min_value']}{metric_info['unit']} "
                        elif band['max_value'] is not None:
                            range_str += f"<={band['max_value']}{metric_info['unit']} "

                        if band['target_value'] is not None:
                            range_str += f"Target: {band['target_value']}{metric_info['unit']} "

                        print(
                            f"  - {band['name']}: {range_str.strip()} (Multiplier: {band['score_multiplier']:.1f}, Invert: {band['invert_score_display']})")
                if not found_bands:
                    print("  No specific bands defined for this metric or your profile.")
                    print("  (Scoring will attempt to find a general band.)")

                # Get user input
                while True:
                    try:
                        user_value = float(input(f"\nEnter the measured value ({metric_info['unit']}): "))
                        break
                    except ValueError:
                        print("❌ Please enter a valid number.")

                # Calculate score
                final_score, interpretation, band_name, _ = self.calculate_metric_score(selected_metric_name,
                                                                                        user_value, age_group,
                                                                                        skill_level)

                # Display results
                print(f"\n" + "=" * 70)
                print("RESULTS")
                print("=" * 70)
                print(f"Measured Value: {user_value} {metric_info['unit']}")
                print(f"Band Matched: {band_name}")
                print(f"Final Score: {final_score:.1f}/100")
                print(f"Rating: {interpretation}")

                input("\nPress Enter to continue...")

            except ValueError:
                print("❌ Please enter a valid number.")
            except KeyboardInterrupt:
                print("\n\nExiting program...")
                break
# Run the calculator
if __name__ == "__main__":
    calculator = SightFXMetricsCalculator()
    calculator.run_calculator()