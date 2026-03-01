from pydantic import BaseModel, Field
from typing import List, Optional, Literal

RelationType = Literal["association", "aggregation", "inheritance"]

class UMLClass(BaseModel):
    name: str
    attributes: List[str] = Field(default_factory=list)
    methods: List[str] = Field(default_factory=list)
    confidence: float = 0.0

class UMLRelation(BaseModel):
    source: str
    target: str
    type: RelationType
    label: Optional[str] = None
    confidence: float = 0.0

class UMLModel(BaseModel):
    classes: List[UMLClass] = Field(default_factory=list)
    relations: List[UMLRelation] = Field(default_factory=list)