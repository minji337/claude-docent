import anthropic
from pprint import pprint
from typing import List, Optional, Literal
from pydantic import BaseModel, Field
from pprint import pprint

class Applicant(BaseModel):
    name: str = Field(description="이름")                        
    gender: Literal["M", "F"] = Field(description="지원자의 성별") 
    age: Optional[int] = Field(None, description="나이")             
    major: str = Field(description="전공(학과)") 

class Applicants(BaseModel):
    applicants: List[Applicant] = Field(description="지원자 객체들의 배열")

pprint(Applicants.model_json_schema())