from typing import Optional

from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.migration_tracking.migration import Migration
from wildlife_tracker.migration_tracking.migration_path import MigrationPath
from wildlife_tracker.animal_management.animal import Animal

class MigrationPath:

    def __init__(self, path_id: int,
                duration: Optional[int] = None,
                migrations: dict[int, Migration] = {},
                paths: dict[int, MigrationPath] = {}) -> None:
        self.duration = duration
        self.migrations = migrations
        self.paths = paths

    def update_migration_path_details(self, path_id: int, **kwargs) -> None:
        pass

    def get_migration_path_details(self, path_id) -> dict:
        pass
