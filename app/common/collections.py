from typing import List

"""
    Add collections here
"""

__all__ = (
    "users",
    "admin_management",
    "state_universities",
    "llm"
)


users="users"
admin_management="admin_management"
state_universities="state_universities"
llm="llm"


def __dir__() -> List[str]:
    return sorted(list(__all__))
