"""
app/services/emergency_handler.py
───────────────────────────────────
Emergency Handler.

Responsibilities
────────────────
1. Load and serve the emergency resources JSON file.
2. Provide a safe, pre-configured emergency response without any LLM involvement.
3. Never generate or invent phone numbers – only serve what is in the config file.
4. Flag unverified contacts clearly so administrators can review them before deployment.

IMPORTANT: The resources loaded here must be reviewed and verified by a university
administrator before this system is used in a live environment.
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from app.config import EMERGENCY_RESOURCES_FILE, UNIVERSITY_ID, CLINICAL_DISCLAIMER
from app.schemas.triage_schema import EmergencyContact, EmergencyResponse, OnlineResource

logger = logging.getLogger(__name__)


class EmergencyHandler:
    """
    Loads emergency resource configuration and constructs safe emergency responses.

    All data comes from emergency_resources.json.
    No LLM is invoked at any point in this handler.
    """

    def __init__(self, resources_path: Path | None = None) -> None:
        self._path = resources_path or EMERGENCY_RESOURCES_FILE
        self._data: dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        """Load emergency resources from the JSON configuration file."""
        if not self._path.exists():
            logger.error(
                "Emergency resources file not found at '%s'. "
                "Emergency responses will be incomplete.",
                self._path,
            )
            self._data = {}
            return
        try:
            with open(self._path, "r", encoding="utf-8") as fh:
                self._data = json.load(fh)
            logger.info("Emergency resources loaded from '%s'.", self._path)
        except Exception as exc:
            logger.error("Failed to load emergency resources: %s", exc)
            self._data = {}

    def get_emergency_response(
        self, university_id: str | None = None
    ) -> EmergencyResponse:
        """
        Build and return the emergency response for the given university.

        Falls back to 'default' if the requested university_id is not found.
        Only returns contacts and resources defined in the config file.
        """
        uid = university_id or UNIVERSITY_ID
        universities: dict = self._data.get("universities", {})

        # Fallback chain: requested → default → empty
        uni_data = universities.get(uid) or universities.get("default") or {}
        global_config: dict = self._data.get("global", {})

        if not uni_data:
            logger.warning(
                "No emergency resource config found for university_id='%s' or 'default'.",
                uid,
            )

        # Build verified contact list
        raw_contacts: list[dict] = uni_data.get("emergency_contacts", [])
        contacts: list[EmergencyContact] = []
        for raw in raw_contacts:
            try:
                contacts.append(EmergencyContact(**raw))
            except Exception as exc:
                logger.error("Skipping malformed emergency contact entry: %s | error: %s", raw, exc)

        # Build online resource list
        raw_resources: list[dict] = uni_data.get("online_resources", [])
        online: list[OnlineResource] = []
        for raw in raw_resources:
            try:
                online.append(OnlineResource(**raw))
            except Exception as exc:
                logger.error("Skipping malformed online resource entry: %s | error: %s", raw, exc)

        return EmergencyResponse(
            university_name=uni_data.get("name", "Your University"),
            global_disclaimer=global_config.get("disclaimer", CLINICAL_DISCLAIMER),
            crisis_message=global_config.get(
                "crisis_message",
                "You are not alone. Please reach out to one of the contacts below.",
            ),
            emergency_contacts=contacts,
            online_resources=online,
        )

    def get_critical_contacts_only(
        self, university_id: str | None = None
    ) -> list[EmergencyContact]:
        """
        Return only the contacts marked as EMERGENCY or CRISIS_LINE type.
        Used to populate the resources array in a CRITICAL triage response.
        """
        full = self.get_emergency_response(university_id)
        priority_types = {"EMERGENCY", "CRISIS_LINE", "CRISIS_TEXT"}
        return [c for c in full.emergency_contacts if c.type in priority_types]

