from typing import List

"""
    Add collections here
"""

__all__ = (
    "users",
    "admin_management"
)


users="users"
admin_management="admin_management"


def __dir__() -> List[str]:
    return sorted(list(__all__))
