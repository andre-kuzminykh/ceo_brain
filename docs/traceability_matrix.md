# Traceability Matrix

| Requirement ID | Requirement Summary | Test Case ID | Test Level | Automation ID | Status |
|---|---|---|---|---|---|
| FR-1 | Accept voice/text input | TC-FR-001-01 | Integration | AT-FR-001-INT-01 | Implemented |
| FR-1 | Accept voice/text input | TC-FR-001-02 | Integration | AT-FR-001-INT-02 | Implemented |
| FR-1 | Accept voice/text input | TC-FR-001-03 | Integration | AT-FR-001-INT-03 | Implemented |
| FR-2 | STT and transcript storage | TC-FR-002-01 | Integration | AT-FR-002-INT-01 | Implemented |
| FR-2 | STT and transcript storage | TC-FR-002-02 | Unit | AT-FR-002-UNIT-01 | Implemented |
| FR-3 | Goal normalization | TC-FR-003-01 | Unit | AT-FR-003-UNIT-01 | Implemented |
| FR-3 | Goal normalization | TC-FR-003-02 | Unit | AT-FR-003-UNIT-02 | Implemented |
| FR-3 | Goal normalization | TC-FR-003-03 | Unit | AT-FR-003-UNIT-03 | Implemented |
| FR-4 | Missing info → waiting_for_user | TC-FR-004-01 | Unit | AT-FR-004-UNIT-01 | Implemented |
| FR-4 | Missing info → waiting_for_user | TC-FR-004-02 | Integration | AT-FR-004-INT-01 | Implemented |
| FR-5 | Clarification as user_input step | TC-FR-005-01 | Unit | AT-FR-005-UNIT-01 | Implemented |
| FR-6 | Atomic action decomposition | TC-FR-006-01 | Unit | AT-FR-006-UNIT-01 | Implemented |
| FR-6 | Atomic action decomposition | TC-FR-006-02 | Unit | AT-FR-006-UNIT-02 | Implemented |
| FR-7 | Tool selection by capability | TC-FR-007-01 | Unit | AT-FR-007-UNIT-01 | Implemented |
| FR-7 | Tool selection by capability | TC-FR-007-02 | Unit | AT-FR-007-UNIT-02 | Implemented |
| FR-8 | Delivery only after critic pass | TC-FR-008-01 | Integration | AT-FR-008-INT-01 | Implemented |
| FR-8 | Delivery only after critic pass | TC-FR-008-02 | Integration | AT-FR-008-INT-02 | Implemented |
| FR-9 | Human interrupt as graph node | TC-FR-009-01 | Integration | AT-FR-009-INT-01 | Implemented |
| FR-9 | Human interrupt as graph node | TC-FR-009-02 | Integration | AT-FR-009-INT-02 | Implemented |
| FR-10 | User response validation/mapping | TC-FR-010-01 | Unit | AT-FR-010-UNIT-01 | Implemented |
| FR-10 | User response validation/mapping | TC-FR-010-02 | Unit | AT-FR-010-UNIT-02 | Implemented |
| FR-10 | User response validation/mapping | TC-FR-010-03 | Unit | AT-FR-010-UNIT-03 | Implemented |
| FR-11 | 3 repair attempts per failure | TC-FR-011-01 | Integration | AT-FR-011-INT-01 | Implemented |
| FR-11 | 3 repair attempts per failure | TC-FR-011-02 | Integration | AT-FR-011-INT-02 | Implemented |
| FR-12 | Post-repair validation cycle | TC-FR-012-01 | Integration | AT-FR-012-INT-01 | Implemented |
| NFR-1 | First response ≤ 5s | TC-NFR-001-01 | Performance | AT-NFR-001-PERF-01 | Implemented |
| NFR-2 | Idempotent persistence | TC-NFR-002-01 | Integration | AT-NFR-002-INT-01 | Implemented |
| NFR-3 | STT error fallback | TC-NFR-003-01 | Integration | AT-NFR-003-INT-01 | Implemented |
| NFR-4 | Choice + text clarification | TC-NFR-004-01 | Unit | AT-NFR-004-UNIT-01 | Implemented |
| NFR-5 | Resume in same thread_id | TC-NFR-005-01 | Integration | AT-NFR-005-INT-01 | Implemented |
| NFR-6 | Side effects only via tools | TC-NFR-006-01 | Unit | AT-NFR-006-UNIT-01 | Implemented |
| NFR-7 | Step tracing | TC-NFR-007-01 | Integration | AT-NFR-007-INT-01 | Implemented |
| NFR-8 | Interrupt survives restart | TC-NFR-008-01 | Integration | AT-NFR-008-INT-01 | Implemented |
| NFR-9 | Reply latency ≤ 3s | TC-NFR-009-01 | Performance | AT-NFR-009-PERF-01 | Implemented |
| NFR-10 | Sandboxed subprocess | TC-NFR-010-01 | Integration | AT-NFR-010-INT-01 | Implemented |
| NFR-11 | Deterministic repair log | TC-NFR-011-01 | Unit | AT-NFR-011-UNIT-01 | Implemented |
| FR-1,2,3,6,7,8 | Full voice→report→delivery pipeline | TC-E2E-001 | E2E | AT-E2E-001 | Implemented |
| FR-4,5,9,10 | Ambiguous request → clarification → resume | TC-E2E-002 | E2E | AT-E2E-002 | Implemented |
| FR-11,12 | Workflow authoring with auto-repair | TC-E2E-003 | E2E | AT-E2E-003 | Implemented |
