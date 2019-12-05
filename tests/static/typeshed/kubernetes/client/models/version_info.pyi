# Stubs for kubernetes.client.models.version_info (Python 2)
#
# NOTE: This dynamically typed stub was automatically generated by stubgen.

from typing import Any, Optional

class VersionInfo:
    swagger_types: Any = ...
    attribute_map: Any = ...
    discriminator: Any = ...
    build_date: Any = ...
    compiler: Any = ...
    git_commit: Any = ...
    git_tree_state: Any = ...
    git_version: Any = ...
    go_version: Any = ...
    major: Any = ...
    minor: Any = ...
    platform: Any = ...
    def __init__(self, build_date: Optional[Any] = ..., compiler: Optional[Any] = ..., git_commit: Optional[Any] = ..., git_tree_state: Optional[Any] = ..., git_version: Optional[Any] = ..., go_version: Optional[Any] = ..., major: Optional[Any] = ..., minor: Optional[Any] = ..., platform: Optional[Any] = ...) -> None: ...
    @property
    def build_date(self): ...
    @build_date.setter
    def build_date(self, build_date: Any) -> None: ...
    @property
    def compiler(self): ...
    @compiler.setter
    def compiler(self, compiler: Any) -> None: ...
    @property
    def git_commit(self): ...
    @git_commit.setter
    def git_commit(self, git_commit: Any) -> None: ...
    @property
    def git_tree_state(self): ...
    @git_tree_state.setter
    def git_tree_state(self, git_tree_state: Any) -> None: ...
    @property
    def git_version(self): ...
    @git_version.setter
    def git_version(self, git_version: Any) -> None: ...
    @property
    def go_version(self): ...
    @go_version.setter
    def go_version(self, go_version: Any) -> None: ...
    @property
    def major(self): ...
    @major.setter
    def major(self, major: Any) -> None: ...
    @property
    def minor(self): ...
    @minor.setter
    def minor(self, minor: Any) -> None: ...
    @property
    def platform(self): ...
    @platform.setter
    def platform(self, platform: Any) -> None: ...
    def to_dict(self): ...
    def to_str(self): ...
    def __eq__(self, other: Any): ...
    def __ne__(self, other: Any): ...