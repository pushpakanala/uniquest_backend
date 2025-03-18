from typing import List

"""
    Add collections here
"""

__all__ = (
    "users",
    "admin_management",
    "state_universities",
    "llm",
    "university_details",
    "metrics"
)


users="users"
admin_management="admin_management"
state_universities="state_universities"
llm="llm"
university_details="university_details"
metrics="metrics"


def __dir__() -> List[str]:
    return sorted(list(__all__))
