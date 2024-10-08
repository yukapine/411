from typing import Any, Optional

from wildlife_tracker.habitat_management.habitat import Habitat
from wildlife_tracker.migration_tracking.migration import Migration
from wildlife_tracker.migration_tracking.migration_path import MigrationPath
from wildlife_tracker.animal_management.animal import Animal

class Animal:

    def __init__(self, 
                animal_id: int,
                species: str,
                age: Optional[int] = None,
                health_status: Optional[str] = None) -> None:
        self.animal_id = animal_id
        self.species = species
        self.age = age
        self.health_status = health_status
        
    def update_animal_details(self, animal_id: int, **kwargs: Any) -> None:
        pass

    def get_animal_details(self, animal_id) -> dict[str, Any]:
        pass

