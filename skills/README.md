# Agent Skills - Project Chimera

## Overview
Skills are discrete capability packages that Chimera agents can invoke to perform specific tasks. Each skill has a well-defined Input/Output contract.

## Skill Categories
1. **Research Skills**: Gather and analyze data
2. **Content Skills**: Create and process content
3. **Distribution Skills**: Publish and manage content

## Implemented Skills

### 1. skill_fetch_trends
**Location**: `skills/skill_fetch_trends/`

### 2. skill_generate_script
**Location**: `skills/skill_generate_script/`

### 3. skill_generate_video
**Location**: `skills/skill_generate_video/`

### 4. skill_publish_content
**Location**: `skills/skill_publish_content/`

## Skill Development Guidelines
1. Each skill must have a `README.md` defining its contract
2. Skills should be stateless where possible
3. All dependencies must be documented
4. Error handling is mandatory

## Integration
Skills are invoked by agents through the skill registry. See `src/core/skill_registry.py` for implementation details.
