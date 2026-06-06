import logging
from fastapi import APIRouter, HTTPException
from app_example.models.framework import Framework

logger = logging.getLogger(__name__)

router = APIRouter()

FRAMEWORKS = {
    "rise": Framework(id="rise", name="RISE", description="Role, Input, Steps, Expectation"),
    "coast": Framework(id="coast", name="COAST", description="Context, Objective, Actions, Scenario, Task"),
    "ape": Framework(id="ape", name="APE", description="Action, Purpose, Expectation"),
    "tag": Framework(id="tag", name="TAG", description="Task, Action, Goal"),
    "care": Framework(id="care", name="CARE", description="Context, Action, Result, Example"),
    "rtf": Framework(id="rtf", name="RTF", description="Role, Task, Format"),
}

@router.get("/frameworks", response_model=list[dict])
def list_frameworks():
    logger.info("Listing all frameworks")
    return [{"id": f.id, "name": f.name} for f in FRAMEWORKS.values()]

@router.get("/frameworks/{id}", response_model=Framework)
def get_framework(id: str):
    framework = FRAMEWORKS.get(id)
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    return framework
