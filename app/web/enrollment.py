"""Guided poses for facial enrollment.

These are presentation copy only. The browser captures local thumbnails so the
participant can see progress, but no frame, descriptor, or measurement leaves
the page until the enrollment endpoint exists.
"""

from __future__ import annotations

TARGET_SAMPLES = 9

ENROLLMENT_POSES = (
    {
        "id": "frontal_1",
        "label": "Frontal",
        "instruction": "Look straight at the camera with a neutral expression.",
    },
    {
        "id": "slight_left",
        "label": "Slight left",
        "instruction": "Turn your head gently to your left.",
    },
    {
        "id": "slight_right",
        "label": "Slight right",
        "instruction": "Turn your head gently to your right.",
    },
    {
        "id": "angle_left",
        "label": "Left angle",
        "instruction": "Turn a little further to your left.",
    },
    {
        "id": "angle_right",
        "label": "Right angle",
        "instruction": "Turn a little further to your right.",
    },
    {
        "id": "slight_up",
        "label": "Chin up",
        "instruction": "Tilt your chin slightly upwards.",
    },
    {
        "id": "slight_down",
        "label": "Chin down",
        "instruction": "Tilt your chin slightly downwards.",
    },
    {
        "id": "expression",
        "label": "Expression",
        "instruction": "Smile naturally.",
    },
    {
        "id": "frontal_2",
        "label": "Frontal again",
        "instruction": "Face the camera straight on one last time.",
    },
)
