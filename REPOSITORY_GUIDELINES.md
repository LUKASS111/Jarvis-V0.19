# Jarvis – Repository Guidelines, Automation, Logging, Archiving & Core Backend Logic

**Version:** v1.0.0  
**Last Updated:** 2025-01-08  
**Author:** Copilot AI Agent  
**Purpose:** Comprehensive workflow and documentation standards for Jarvis AI Assistant repository

---

## 📋 Table of Contents

1. [Workflow Structure](#1-workflow-structure)
2. [Changelog, Decision Logging, and Micro-version Logging](#2-changelog-decision-logging-and-micro-version-logging)
3. [Structured Archiving and Logical File Division](#3-structured-archiving-and-logical-file-division)
4. [Automation & CI/CD Integration](#4-automation--cicd-integration)
5. [Core Backend Logic Documentation](#5-core-backend-logic-documentation)
6. [Quality Gates & Validation](#6-quality-gates--validation)

---

## 1. Workflow Structure

### 🔄 Single PR Workflow
- **All development work occurs within one continuous Pull Request**
- Each significant change must be committed with meaningful commit messages
- Every commit should be reflected in the changelog section of relevant `.md` files
- **Micro-versioning**: Each commit represents a micro-version increment

### 🚫 Documentation Protection Policy
- **NEVER delete any documentation, plan, changelog, or archive file**
- After work cycle completion or plan updates, move files to `docs/archive/` with full history preserved
- All historical context must remain accessible for future reference

### 📝 Commit Standards
- Use conventional commit format: `type(scope): description`
- Types: `feat`, `fix`, `docs`, `refactor`, `test`, `chore`
- Each commit must include reference to updated documentation

---

## 2. Changelog, Decision Logging, and Micro-version Logging

### 📊 Changelog Format (Required in ALL .md files)

Every `.md` file must contain this section:

```markdown
## Changelog / Revision Log

| Date       | Version | Change Type        | Author     | Commit Link | Description               |
|------------|---------|--------------------|------------|-------------|---------------------------|
| 2025-01-08 | v1.0.1  | Feature addition   | copilot    | [pending]   | Added smart GUI features |
| 2025-01-08 | v1.0.0  | Initial creation   | copilot    | [pending]   | Created repository guidelines |
```

### 🎯 Decision Log Requirements

**All major decisions** must be explicitly logged in a "Decision Log" section:

```markdown
## Decision Log

### [Date] - [Decision Title]
- **Author**: [Name]
- **Context**: [Why this decision was needed]
- **Decision**: [What was decided]
- **Alternatives Considered**: [Other options evaluated]
- **Consequences**: [Expected impact and risks]
- **Commit**: [Link to implementation commit]
```

### 🔍 Traceability Requirements
- Every code change must reference corresponding documentation update
- Every architecture decision must include rationale and alternatives
- All bug fixes must include root cause analysis and prevention strategy

---

## 3. Structured Archiving and Logical File Division

### 📁 Repository Structure

```
Jarvis-V0.19/
├── docs/
│   ├── archive/           # Historical documentation
│   │   ├── past/         # Completed/obsolete versions
│   │   ├── decisions/    # Archived decision logs
│   │   └── versions/     # Version-specific documentation
│   ├── current/          # Active working documentation
│   └── future/           # Planning and roadmap documents
├── [root .md files]      # Active documentation only
```

### 🗂️ Documentation Categories

**PAST (History)**: `docs/archive/past/`
- All previous versions, legacy logic, and historical decisions
- Complete audit trail of repository evolution
- Examples: `PAST_HISTORY.md`, `LEGACY_ARCHITECTURE.md`

**CURRENT (Active)**: Root directory + `docs/current/`
- Current version documentation, active plans, working guides
- Examples: `README.md`, `ARCHITECTURE.md`, `CURRENT_STATUS.md`

**FUTURE (Planning)**: `docs/future/`
- Roadmaps, planned features, future architecture
- Examples: `FUTURE_ROADMAP.md`, `PLANNED_FEATURES.md`

### 📦 Archive Process
1. Before major updates, copy current documentation to `docs/archive/past/`
2. Add timestamp and version to archived filename
3. Update archive index with change summary
4. Maintain full commit history links

---

## 4. Automation & CI/CD Integration

### 🤖 GitHub Actions Integration
- Automated documentation validation on each commit
- Changelog completeness verification
- Link validation for all commit references
- Archive integrity checks

### 🔧 Copilot Workspace Features
- Automated changelog generation from commit messages
- Documentation synchronization across files
- Decision log template generation
- Archive management assistance

---

## 5. Core Backend Logic Documentation

### 🧠 Backend Documentation Requirements
- Every backend module must have corresponding documentation
- API changes must be documented with before/after examples
- Integration patterns must be explained with sequence diagrams
- Error handling strategies must be documented with examples

### 📡 Signal Flow Documentation
- All backend signals must be documented in `BACKEND_SIGNALS.md`
- GUI and CLI signal flow must be identical and documented
- Integration points must have clear interface specifications

---

## 6. Quality Gates & Validation

### ✅ Documentation Quality Gates
- [ ] All .md files have changelog sections
- [ ] All commits are referenced in relevant changelogs
- [ ] All major decisions are logged with full context
- [ ] All links are valid and accessible
- [ ] Archive structure is maintained
- [ ] Version consistency across all files

### 🧪 Automated Validation
- Pre-commit hooks validate changelog format
- CI/CD pipeline checks documentation completeness
- Link validation ensures all commit references are accessible
- Archive integrity verification

---

## Implementation Checklist

- [ ] Add changelog sections to all existing .md files
- [ ] Create decision log sections where needed
- [ ] Establish archive directory structure
- [ ] Implement automated validation scripts
- [ ] Update all documentation with proper versioning
- [ ] Create archive index with current documentation state

---

## Changelog / Revision Log

| Date       | Version | Change Type      | Author  | Commit Link | Description                    |
|------------|---------|------------------|---------|-------------|--------------------------------|
| 2025-01-08 | v1.0.0  | Initial creation | copilot | [pending]   | Created comprehensive repository guidelines system |

## Decision Log

### 2025-01-08 - Comprehensive Repository Guidelines Implementation
- **Author**: Copilot AI Agent
- **Context**: User requested systematic workflow, documentation, and archiving standards for professional repository management
- **Decision**: Implement comprehensive guidelines covering workflow, changelog, archiving, automation, and quality gates
- **Alternatives Considered**: 
  - Minimal documentation approach (rejected - insufficient traceability)
  - Tool-specific solutions (rejected - vendor lock-in)
  - Manual-only processes (rejected - error-prone)
- **Consequences**: 
  - Enhanced traceability and accountability
  - Improved collaboration and maintenance
  - Systematic knowledge preservation
  - Increased initial overhead offset by long-term benefits
- **Commit**: [To be added after implementation]