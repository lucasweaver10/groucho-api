import asyncio
import os
from dataclasses import dataclass
from typing import Any
from pydantic import BaseModel

import logfire
from devtools import debug
from httpx import AsyncClient

from pydantic_ai import Agent, ModelRetry, RunContext

class ContentBlock(BaseModel):    
    content_block: str

@dataclass
class Deps:    
    system_prompt: str

content_writer_agent = Agent(
    'openai:gpt-4o-mini',        
    deps_type=Deps,
    retries=2,
    result_type=ContentBlock
)

@content_writer_agent.system_prompt
def add_system_prompt(ctx: RunContext[str]) -> str:  
    return f"{ctx.deps.system_prompt}"