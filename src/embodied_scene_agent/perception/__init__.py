"""Teacher-state and benchmark adapters feeding scene memory."""

from embodied_scene_agent.perception.base import BaseTeacherStateAdapter
from embodied_scene_agent.perception.calvin_field_mapper import (
    extract_robot_state_from_live_obs,
    extract_scene_objects_from_live_obs,
    map_calvin_obs_and_info_to_teacher_bundle,
    map_live_calvin_to_teacher_bundle,
    map_robot_info_to_teacher_robot,
)
from embodied_scene_agent.perception.calvin_teacher import CalvinTeacherStateAdapter
from embodied_scene_agent.perception.mock import MockTeacherStateAdapter

__all__ = [
    "BaseTeacherStateAdapter",
    "CalvinTeacherStateAdapter",
    "MockTeacherStateAdapter",
    "map_robot_info_to_teacher_robot",
    "map_calvin_obs_and_info_to_teacher_bundle",
    "map_live_calvin_to_teacher_bundle",
    "extract_robot_state_from_live_obs",
    "extract_scene_objects_from_live_obs",
]
