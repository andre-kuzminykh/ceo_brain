# Test Strategy

## 1. Document Information

| Field | Value |
|---|---|
| Project Name | Voice-first Telegram LangGraph Agent Builder & Executor |
| Document Version | 1.0 |
| Specification Version | 1.0 |
| Author | QA Team |
| Date | 2026-04-01 |

## 2. Purpose

This document defines the overall testing approach for the Voice-first Telegram LangGraph Agent system. It explains what will be tested, which test levels will be used, how requirements will be covered, what will be automated, and which quality gates must be satisfied before release.

## 3. Scope

### 3.1 In Scope

- Telegram Gateway: voice/text message intake, webhook handling, message routing, reply delivery
- Speech & Input Normalization: STT pipeline, transcript storage, goal normalization (goal, constraints, deliverable, ambiguities)
- Planner & Decomposer: intent classification, execution mode selection, DAG plan construction, atomic action decomposition (llm/tool/code/user_input)
- Tool Registry & Capability Retrieval: tool matching, binding, permission checking, fallback handling
- Workflow Compiler: spec.yaml generation (Prompt 1), code generation (Prompt 2), packaging
- Execution Runtime: graph compilation, node execution, state persistence, interrupt/resume, progress streaming
- Critic & Auto-Repair: per-step validation, build validation, repair loop, escalation
- Artifact & Delivery: Google Docs write, Telegram delivery, fallback delivery
- Human-in-the-loop: interrupt creation, Telegram delivery, user reply resume, choice/text support
- State management: RunState lifecycle, status transitions, idempotent persistence

### 3.2 Out of Scope

- Telegram Bot API server-side behavior (third-party)
- LLM provider internal behavior (OpenAI/Anthropic API correctness)
- Google Docs API server-side behavior
- Browser/mobile UI rendering of Telegram client
- Infrastructure provisioning (Kubernetes, cloud setup)
- Load testing beyond staging environment capacity
- Third-party STT provider accuracy benchmarking

## 4. System Overview

The system is a voice-first Telegram bot backed by a LangGraph-based orchestrator. Users send voice or text messages in Telegram. The system transcribes speech, understands the user's goal, builds an executable plan decomposed into atomic actions (llm/tool/code/user_input), retrieves and binds appropriate tools, compiles a LangGraph workflow, executes it with per-step critic validation, auto-repairs errors, and delivers results back to the user via Telegram and/or external systems like Google Docs.

## 5. Requirements Overview

### Functional Requirements (FR)

| ID | Summary |
|---|---|
| FR-1 | Accept voice and text messages as input |
| FR-2 | Transcribe speech and save transcript to run state |
| FR-3 | Normalize user goal into structured format (goal, deliverable, constraints, ambiguities) |
| FR-4 | Missing critical info transitions run to waiting_for_user, not failed |
| FR-5 | User clarification formatted as atomic user_input step |
| FR-6 | Planner decomposes tasks to atomic actions (llm/tool/code/user_input) |
| FR-7 | System selects tools by capabilities and schema contract before execution |
| FR-8 | Delivery to external system only after critic-check passes |
| FR-9 | Human interrupt is a first-class node in the graph |
| FR-10 | User response validated and mapped to typed state update |
| FR-11 | Minimum 3 automatic repair attempts per failure class |
| FR-12 | After each repair patch: compile + import + smoke test |

### Non-Functional Requirements (NFR)

| ID | Summary |
|---|---|
| NFR-1 | Time to first response ≤ 5 seconds |
| NFR-2 | Transcript and run state idempotently persisted |
| NFR-3 | STT errors don't break run; fallback to manual transcript confirmation |
| NFR-4 | Clarification supports choices and free text |
| NFR-5 | After user reply, execution resumes in the same thread_id |
| NFR-6 | All side effects only through tool-nodes |
| NFR-7 | Each executed step traced: input, output, critic verdict, retries |
| NFR-8 | Human interrupt survives service restart |
| NFR-9 | Telegram reply latency after user response ≤ 3 seconds |
| NFR-10 | Generated code runs in sandboxed subprocess |
| NFR-11 | Repair loop deterministically logged and reproducible |

## 6. Test Objectives

1. Verify that all functional requirements (FR-1 through FR-12) are correctly implemented
2. Validate critical business workflows: voice intake → plan → execute → deliver
3. Ensure human-in-the-loop interrupt/resume works reliably across service restarts
4. Verify the critic validates each step and the repair loop auto-fixes errors within budget
5. Ensure system behavior is stable under expected concurrent load
6. Validate performance constraints (response latency, processing time)
7. Verify security boundaries (sandbox isolation, tool allowlist, secret protection)
8. Provide confidence for safe changes and releases through automated regression

## 7. Test Levels and Test Types

### 7.1 Unit Testing

**Purpose:** Validate isolated business logic, data transformations, validation rules, and state transitions.

**Typical Coverage:**
- State model validation and serialization
- Goal normalization logic
- Plan decomposition rules
- Tool matching/binding logic
- Critic verdict computation
- Repair attempt classification
- Interrupt payload construction
- Action type classification
- Status transition validation

### 7.2 Integration Testing

**Purpose:** Validate interaction between components, services, and external APIs.

**Typical Coverage:**
- Telegram webhook → Gateway → Orchestrator flow
- STT service → Goal normalization pipeline
- Planner → Tool Registry → Binding pipeline
- Workflow Compiler → Validator → Execution Runtime
- Critic → Repair → Revalidation loop
- Execution Runtime → Interrupt → Telegram → Resume
- Artifact Service → Google Docs delivery
- State persistence and recovery across service boundaries

### 7.3 End-to-End Testing

**Purpose:** Validate critical user workflows from voice/text input to artifact delivery.

**Typical Coverage:**
- Voice message → transcription → plan → execution → Telegram delivery
- Text message → plan → tool execution → Google Docs report → link delivery
- Ambiguous request → clarification → user reply → resume → completion
- Failed step → critic detection → repair → successful completion
- Workflow authoring: TO-BE description → spec.yaml → generated code → execution

### 7.4 Non-Functional Testing

**Purpose:** Validate system qualities beyond functional correctness.

**Types:**
- **Performance:** Response latency (NFR-1, NFR-9), processing throughput
- **Reliability:** Service restart resilience (NFR-8), idempotent persistence (NFR-2)
- **Security:** Sandbox isolation (NFR-10), tool allowlist enforcement, secret protection
- **Observability:** Step tracing completeness (NFR-7), repair log reproducibility (NFR-11)

## 8. Requirement-to-Test-Level Mapping

| Req ID | Summary | Unit | Integration | E2E | Performance | Security | Monitoring |
|---|---|---|---|---|---|---|---|
| FR-1 | Accept voice/text input | No | Yes | Yes | No | No | No |
| FR-2 | STT and transcript storage | Yes | Yes | Yes | No | No | No |
| FR-3 | Goal normalization | Yes | Yes | Yes | No | No | No |
| FR-4 | Missing info → waiting_for_user | Yes | Yes | Yes | No | No | No |
| FR-5 | Clarification as user_input step | Yes | Yes | Yes | No | No | No |
| FR-6 | Atomic action decomposition | Yes | Yes | Yes | No | No | No |
| FR-7 | Tool selection by capability | Yes | Yes | Yes | No | No | No |
| FR-8 | Delivery only after critic pass | Yes | Yes | Yes | No | No | No |
| FR-9 | Human interrupt as graph node | Yes | Yes | Yes | No | No | No |
| FR-10 | User response validation/mapping | Yes | Yes | Yes | No | No | No |
| FR-11 | 3 repair attempts per failure | Yes | Yes | Yes | No | No | Yes |
| FR-12 | Post-repair validation cycle | Yes | Yes | Yes | No | No | Yes |
| NFR-1 | First response ≤ 5s | No | No | No | Yes | No | Yes |
| NFR-2 | Idempotent persistence | Yes | Yes | No | No | No | No |
| NFR-3 | STT error fallback | Yes | Yes | Yes | No | No | No |
| NFR-4 | Choice + text clarification | Yes | Yes | Yes | No | No | No |
| NFR-5 | Resume in same thread_id | No | Yes | Yes | No | No | No |
| NFR-6 | Side effects only via tools | Yes | Yes | Yes | No | Yes | No |
| NFR-7 | Step tracing | No | Yes | No | No | No | Yes |
| NFR-8 | Interrupt survives restart | No | Yes | Yes | No | No | No |
| NFR-9 | Reply latency ≤ 3s | No | No | No | Yes | No | Yes |
| NFR-10 | Sandboxed subprocess | No | Yes | No | No | Yes | No |
| NFR-11 | Deterministic repair log | Yes | Yes | No | No | No | Yes |

## 9. Test Priorities

| Priority | Meaning |
|---|---|
| High | Critical for business value, safety, or core workflow. Blocks release. |
| Medium | Important but not release-blocking. Should be fixed before GA. |
| Low | Useful but not critical. Can be deferred. |

**Priority assignment rules:**
- **High:** Core pipeline (intake → plan → execute → deliver), human interrupt/resume, critic/repair loop, state persistence
- **Medium:** Edge cases in normalization, tool fallback, delivery retry, STT fallback
- **Low:** Observability completeness, performance optimization beyond thresholds, UI polish

## 10. Test Environment

| Environment | Purpose |
|---|---|
| Local developer | Unit tests, fast integration tests with mocks |
| CI pipeline | All unit + integration tests, smoke E2E with mocked externals |
| Staging | Full E2E with real Telegram test bot, performance tests |
| Production | Monitoring, alerting, canary checks |

**Dependencies:**
- PostgreSQL (test instance or in-memory SQLite for unit)
- Redis (test instance or fakeredis for unit)
- Mocked Telegram Bot API (httpx/respx)
- Mocked STT provider
- Mocked LLM provider
- Mocked Google Docs API
- Sandbox subprocess runner (restricted)

## 11. Test Data Strategy

| Category | Examples |
|---|---|
| Valid inputs | Well-formed voice files, clear text commands, complete goals |
| Invalid inputs | Empty voice files, corrupted audio, empty text, non-UTF8 |
| Boundary values | Max message length, minimum audio duration, max plan steps |
| Ambiguous inputs | Vague goals, missing deliverable, conflicting constraints |
| Error scenarios | STT failure, LLM timeout, tool not found, Google Docs write failure |
| Security inputs | Injection attempts in text, malformed file_ids, oversized payloads |
| Performance datasets | 50-100 concurrent voice messages, batch tool executions |

## 12. Automation Strategy

**Automated first:**
1. Unit tests for all state models, normalization, decomposition, critic logic
2. Integration tests for core pipeline: intake → plan → execute → deliver
3. Integration tests for interrupt/resume flow
4. Integration tests for critic → repair → revalidation loop
5. Performance smoke checks for latency thresholds

**Manual testing:**
- Exploratory testing of Telegram bot UX
- Visual review of generated artifacts
- Edge case discovery for novel voice inputs
- Usability review of clarification prompts

## 13. Entry and Exit Criteria

### 13.1 Entry Criteria

- Requirements specification is available and reviewed
- Test environment is provisioned and accessible
- Build is deployable (passes linting and compilation)
- Required mock services are operational
- Test data is prepared

### 13.2 Exit Criteria

- All High-priority test cases executed and passed
- All Medium-priority test cases executed, no critical defects open
- No open Critical or High severity defects
- All automated tests pass in CI
- Performance thresholds met in staging
- Security review completed, no blockers

## 14. Quality Gates

| Gate | Criteria |
|---|---|
| PR Merge | All unit tests pass, no new critical issues |
| Staging Deploy | All integration tests pass, E2E smoke passes |
| Production Release | All E2E scenarios pass, performance thresholds met, no critical security findings, repair loop validated |

## 15. Risks and Limitations

| Risk | Mitigation |
|---|---|
| External API mocking may not cover all edge cases | Supplement with staging tests against real APIs |
| LLM output non-determinism affects test reproducibility | Use seeded/mocked LLM responses for deterministic tests |
| Generated code sandbox may behave differently across environments | Test sandbox in CI with same runtime as production |
| Telegram API rate limits may affect E2E tests | Use dedicated test bot with higher limits |
| Performance tests limited to staging | Monitor production metrics post-deploy |
| Human-in-the-loop tests require simulated user interaction | Automate Telegram reply simulation in E2E |

## 16. Deliverables

1. This test strategy document
2. Test cases document with all test cases
3. Traceability matrix (requirements → test cases)
4. Automated test implementations (unit, integration, E2E, performance)
5. CI pipeline configuration for test execution
6. Test fixtures and factories
