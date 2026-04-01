# Test Cases

## FR-1: Accept voice and text messages as input

### TC-FR-001-01
- **Test Case ID:** TC-FR-001-01
- **Requirement ID:** FR-1
- **Title:** Bot accepts voice message and creates a run
- **Type:** Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** Telegram webhook is configured, bot is running
- **Test Data:** Valid Telegram voice message update JSON
- **Steps:**
  1. Send a POST request to `/telegram/webhook` with a voice message update
  2. Verify the response indicates acceptance
  3. Verify a run is created with input_modality=voice
- **Expected Result:**
  - Response `{"accepted": true, "run_id": "<uuid>"}`
  - Run exists in storage with status `received`
  - Raw voice file reference saved
- **Automation Status:** Automated
- **Automation ID:** AT-FR-001-INT-01

### TC-FR-001-02
- **Test Case ID:** TC-FR-001-02
- **Requirement ID:** FR-1
- **Title:** Bot accepts text message and creates a run
- **Type:** Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** Telegram webhook is configured, bot is running
- **Test Data:** Valid Telegram text message update JSON `{"message": {"text": "Make a report on EV market"}}`
- **Steps:**
  1. Send a POST request to `/telegram/webhook` with a text message update
  2. Verify the response indicates acceptance
  3. Verify a run is created with input_modality=text
- **Expected Result:**
  - Response `{"accepted": true, "run_id": "<uuid>"}`
  - Run exists with status `received` and raw_input populated
- **Automation Status:** Automated
- **Automation ID:** AT-FR-001-INT-02

### TC-FR-001-03
- **Test Case ID:** TC-FR-001-03
- **Requirement ID:** FR-1
- **Title:** Bot rejects unsupported message types gracefully
- **Type:** Functional
- **Level:** Integration
- **Priority:** Medium
- **Preconditions:** Bot is running
- **Test Data:** Telegram update with sticker message
- **Steps:**
  1. Send a POST to `/telegram/webhook` with sticker update
  2. Verify the bot responds with a user-friendly error
- **Expected Result:**
  - No run created
  - Bot sends message to user explaining supported input types
- **Automation Status:** Automated
- **Automation ID:** AT-FR-001-INT-03

---

## FR-2: STT and transcript storage

### TC-FR-002-01
- **Test Case ID:** TC-FR-002-01
- **Requirement ID:** FR-2
- **Title:** Voice message is transcribed and transcript saved
- **Type:** Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** STT service is available, run exists with voice input
- **Test Data:** Voice file simulating "Make a report on the EV market in Saudi Arabia"
- **Steps:**
  1. Trigger STT pipeline for the run
  2. Verify transcript is produced
  3. Verify transcript is saved to run state
  4. Verify run status transitions to `transcribed`
- **Expected Result:**
  - Transcript text contains the spoken content
  - RunState.transcript is populated
  - RunState.execution_status == `transcribed`
- **Automation Status:** Automated
- **Automation ID:** AT-FR-002-INT-01

### TC-FR-002-02
- **Test Case ID:** TC-FR-002-02
- **Requirement ID:** FR-2
- **Title:** Empty voice file returns error without crashing run
- **Type:** Functional
- **Level:** Unit
- **Priority:** Medium
- **Preconditions:** None
- **Test Data:** Empty audio bytes
- **Steps:**
  1. Pass empty audio data to STT pipeline
  2. Verify fallback behavior
- **Expected Result:**
  - No crash/exception
  - Transcript set to empty or fallback message
  - Run status transitions to a state where user can confirm
- **Automation Status:** Automated
- **Automation ID:** AT-FR-002-UNIT-01

---

## FR-3: Goal normalization

### TC-FR-003-01
- **Test Case ID:** TC-FR-003-01
- **Requirement ID:** FR-3
- **Title:** Clear transcript produces complete normalized goal
- **Type:** Functional
- **Level:** Unit
- **Priority:** High
- **Preconditions:** None
- **Test Data:** Transcript: "Make a report on the EV market in Saudi Arabia and save it to Google Docs"
- **Steps:**
  1. Pass transcript to goal normalization function
  2. Verify output structure
- **Expected Result:**
  - `goal` is populated with the core objective
  - `deliverable` mentions report/document
  - `constraints` may include geography (Saudi Arabia)
  - `ambiguities` is empty or minimal
- **Automation Status:** Automated
- **Automation ID:** AT-FR-003-UNIT-01

### TC-FR-003-02
- **Test Case ID:** TC-FR-003-02
- **Requirement ID:** FR-3
- **Title:** Ambiguous transcript produces ambiguities list
- **Type:** Functional
- **Level:** Unit
- **Priority:** High
- **Preconditions:** None
- **Test Data:** Transcript: "Do something with the data"
- **Steps:**
  1. Pass vague transcript to goal normalization
  2. Verify ambiguities are identified
- **Expected Result:**
  - `goal` is a best-effort interpretation
  - `ambiguities` list is non-empty
  - `deliverable` may be empty or marked as unknown
- **Automation Status:** Automated
- **Automation ID:** AT-FR-003-UNIT-02

### TC-FR-003-03
- **Test Case ID:** TC-FR-003-03
- **Requirement ID:** FR-3
- **Title:** Empty transcript returns empty goal with ambiguity flag
- **Type:** Functional
- **Level:** Unit
- **Priority:** Medium
- **Preconditions:** None
- **Test Data:** Transcript: ""
- **Steps:**
  1. Pass empty string to goal normalization
  2. Verify output
- **Expected Result:**
  - `goal` is empty
  - `ambiguities` contains indication of empty input
- **Automation Status:** Automated
- **Automation ID:** AT-FR-003-UNIT-03

---

## FR-4: Missing info transitions to waiting_for_user

### TC-FR-004-01
- **Test Case ID:** TC-FR-004-01
- **Requirement ID:** FR-4
- **Title:** Missing critical inputs move run to waiting_for_user
- **Type:** Functional
- **Level:** Unit
- **Priority:** High
- **Preconditions:** Planner has detected missing inputs
- **Test Data:** NormalizedGoal with non-empty ambiguities
- **Steps:**
  1. Submit goal with ambiguities to planner
  2. Verify run status transition
- **Expected Result:**
  - Run status set to `waiting_for_user`
  - Run is NOT set to `failed`
  - Clarification questions are generated
- **Automation Status:** Automated
- **Automation ID:** AT-FR-004-UNIT-01

### TC-FR-004-02
- **Test Case ID:** TC-FR-004-02
- **Requirement ID:** FR-4
- **Title:** Missing permissions trigger waiting_for_user
- **Type:** Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** Tool requires scope user hasn't granted
- **Test Data:** Plan requiring Google Docs write without write scope
- **Steps:**
  1. Attempt tool binding with missing scope
  2. Verify interrupt is created
- **Expected Result:**
  - Run moves to `waiting_for_user`
  - Interrupt payload requests the missing permission
- **Automation Status:** Automated
- **Automation ID:** AT-FR-004-INT-01

---

## FR-5: Clarification as user_input step

### TC-FR-005-01
- **Test Case ID:** TC-FR-005-01
- **Requirement ID:** FR-5
- **Title:** Clarification question formatted as user_input action
- **Type:** Functional
- **Level:** Unit
- **Priority:** High
- **Preconditions:** None
- **Test Data:** Missing field: deliverable format
- **Steps:**
  1. Create clarification for missing deliverable format
  2. Verify it produces an AtomicAction with type user_input
- **Expected Result:**
  - Action type is `user_input`
  - InterruptPayload has question, response_type, and choices if applicable
- **Automation Status:** Automated
- **Automation ID:** AT-FR-005-UNIT-01

---

## FR-6: Atomic action decomposition

### TC-FR-006-01
- **Test Case ID:** TC-FR-006-01
- **Requirement ID:** FR-6
- **Title:** Research task decomposes into correct atomic actions
- **Type:** Functional
- **Level:** Unit
- **Priority:** High
- **Preconditions:** None
- **Test Data:** Goal: "Research EV market in Saudi Arabia"
- **Steps:**
  1. Submit goal to decomposer
  2. Verify action types
- **Expected Result:**
  - Actions include mix of `llm`, `tool`, and potentially `code` types
  - Each action has description and success_criteria
  - Dependencies between actions are specified
- **Automation Status:** Automated
- **Automation ID:** AT-FR-006-UNIT-01

### TC-FR-006-02
- **Test Case ID:** TC-FR-006-02
- **Requirement ID:** FR-6
- **Title:** Each action type is one of llm/tool/code/user_input
- **Type:** Functional
- **Level:** Unit
- **Priority:** High
- **Preconditions:** None
- **Test Data:** Various decomposed plans
- **Steps:**
  1. Decompose multiple different goals
  2. Verify all action types are valid enum members
- **Expected Result:**
  - Every AtomicAction.action_type is in {llm, tool, code, user_input}
  - No unknown action types exist
- **Automation Status:** Automated
- **Automation ID:** AT-FR-006-UNIT-02

---

## FR-7: Tool selection by capability

### TC-FR-007-01
- **Test Case ID:** TC-FR-007-01
- **Requirement ID:** FR-7
- **Title:** Tool retriever matches correct tools by action requirements
- **Type:** Functional
- **Level:** Unit
- **Priority:** High
- **Preconditions:** Tool registry populated with web_search, google_docs_write, code_exec
- **Test Data:** Actions requiring web search and document writing
- **Steps:**
  1. Submit actions to tool retriever
  2. Verify bindings
- **Expected Result:**
  - web_search tool bound to search actions
  - google_docs_write bound to delivery action
  - All bindings have valid params
- **Automation Status:** Automated
- **Automation ID:** AT-FR-007-UNIT-01

### TC-FR-007-02
- **Test Case ID:** TC-FR-007-02
- **Requirement ID:** FR-7
- **Title:** Missing tool triggers re-plan or fallback
- **Type:** Functional
- **Level:** Unit
- **Priority:** Medium
- **Preconditions:** Action requires a tool not in registry
- **Test Data:** Action requiring `slack_send` when only email tools exist
- **Steps:**
  1. Attempt tool retrieval for unavailable tool
  2. Verify fallback behavior
- **Expected Result:**
  - Binding warnings generated
  - Either fallback tool suggested or action sent back for re-plan
- **Automation Status:** Automated
- **Automation ID:** AT-FR-007-UNIT-02

---

## FR-8: Delivery only after critic pass

### TC-FR-008-01
- **Test Case ID:** TC-FR-008-01
- **Requirement ID:** FR-8
- **Title:** Artifact delivered only after critic verdict is pass
- **Type:** Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** Artifact is generated, critic is available
- **Test Data:** Generated report artifact
- **Steps:**
  1. Submit artifact to critic
  2. If critic returns `pass`, proceed to delivery
  3. If critic returns `retry`/`repair`, verify delivery is blocked
- **Expected Result:**
  - Delivery only happens after CriticVerdict.PASS
  - No delivery occurs if critic verdict is retry/repair/escalate
- **Automation Status:** Automated
- **Automation ID:** AT-FR-008-INT-01

### TC-FR-008-02
- **Test Case ID:** TC-FR-008-02
- **Requirement ID:** FR-8
- **Title:** Failed critic blocks Google Docs write
- **Type:** Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** Artifact has quality issues
- **Test Data:** Incomplete report missing key sections
- **Steps:**
  1. Generate artifact with known quality issues
  2. Run critic validation
  3. Attempt delivery
- **Expected Result:**
  - Critic returns `retry` or `repair`
  - Google Docs write is NOT invoked
  - System attempts to fix the artifact
- **Automation Status:** Automated
- **Automation ID:** AT-FR-008-INT-02

---

## FR-9: Human interrupt as first-class graph node

### TC-FR-009-01
- **Test Case ID:** TC-FR-009-01
- **Requirement ID:** FR-9
- **Title:** Interrupt node pauses execution and sends Telegram message
- **Type:** Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** Graph is executing, reaches user_input node
- **Test Data:** Interrupt requesting user approval
- **Steps:**
  1. Execute graph until interrupt node
  2. Verify execution pauses
  3. Verify Telegram message sent to user
- **Expected Result:**
  - Graph execution is suspended
  - RunState.execution_status == `interrupted`
  - Telegram message delivered with question and options
- **Automation Status:** Automated
- **Automation ID:** AT-FR-009-INT-01

### TC-FR-009-02
- **Test Case ID:** TC-FR-009-02
- **Requirement ID:** FR-9
- **Title:** Resume after user reply continues execution
- **Type:** Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** Graph is interrupted, awaiting user reply
- **Test Data:** User reply "Approved"
- **Steps:**
  1. Simulate user reply to interrupt
  2. Verify graph resumes
  3. Verify state is updated with user response
- **Expected Result:**
  - Graph execution resumes from interrupt point
  - RunState.execution_status == `executing`
  - User response incorporated into state
- **Automation Status:** Automated
- **Automation ID:** AT-FR-009-INT-02

---

## FR-10: User response validation and mapping

### TC-FR-010-01
- **Test Case ID:** TC-FR-010-01
- **Requirement ID:** FR-10
- **Title:** Valid choice response maps to state update
- **Type:** Functional
- **Level:** Unit
- **Priority:** High
- **Preconditions:** Interrupt with choices ["PDF", "Google Docs", "Email"]
- **Test Data:** User selects "Google Docs"
- **Steps:**
  1. Validate user response against interrupt payload
  2. Map response to state field
- **Expected Result:**
  - Validation passes
  - State field updated with "Google Docs"
- **Automation Status:** Automated
- **Automation ID:** AT-FR-010-UNIT-01

### TC-FR-010-02
- **Test Case ID:** TC-FR-010-02
- **Requirement ID:** FR-10
- **Title:** Invalid choice response rejected with re-prompt
- **Type:** Functional
- **Level:** Unit
- **Priority:** Medium
- **Preconditions:** Interrupt with choices ["PDF", "Google Docs", "Email"]
- **Test Data:** User types "Slack" (not in choices)
- **Steps:**
  1. Validate user response against choices
  2. Verify rejection
- **Expected Result:**
  - Validation fails
  - System re-prompts user with valid choices
- **Automation Status:** Automated
- **Automation ID:** AT-FR-010-UNIT-02

### TC-FR-010-03
- **Test Case ID:** TC-FR-010-03
- **Requirement ID:** FR-10
- **Title:** Free text response accepted for text-type interrupts
- **Type:** Functional
- **Level:** Unit
- **Priority:** High
- **Preconditions:** Interrupt with response_type="text"
- **Test Data:** User types "Focus on consumer segment only"
- **Steps:**
  1. Validate free text response
  2. Map to state
- **Expected Result:**
  - Validation passes (any non-empty text)
  - State updated with the text value
- **Automation Status:** Automated
- **Automation ID:** AT-FR-010-UNIT-03

---

## FR-11: Minimum 3 repair attempts per failure class

### TC-FR-011-01
- **Test Case ID:** TC-FR-011-01
- **Requirement ID:** FR-11
- **Title:** System retries repair up to 3 times before escalating
- **Type:** Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** Generated code has a persistent compile error
- **Test Data:** Python code with syntax error that repair can fix
- **Steps:**
  1. Submit code with compile error to validator
  2. Observe repair attempts
  3. Verify attempt count
- **Expected Result:**
  - At least 3 repair attempts made
  - Each attempt is logged with attempt_number, error_class, fix_strategy
  - If all fail, status escalates to `escalated`
- **Automation Status:** Automated
- **Automation ID:** AT-FR-011-INT-01

### TC-FR-011-02
- **Test Case ID:** TC-FR-011-02
- **Requirement ID:** FR-11
- **Title:** Successful repair on 2nd attempt stops retry loop
- **Type:** Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** Generated code has a fixable error
- **Test Data:** Code with import error fixable by adding import
- **Steps:**
  1. Submit code to validator
  2. First repair attempt partially fixes
  3. Second repair fully fixes
  4. Verify loop stops
- **Expected Result:**
  - Exactly 2 repair attempts logged
  - Final validation passes
  - Run continues execution
- **Automation Status:** Automated
- **Automation ID:** AT-FR-011-INT-02

---

## FR-12: Post-repair validation cycle

### TC-FR-012-01
- **Test Case ID:** TC-FR-012-01
- **Requirement ID:** FR-12
- **Title:** After each patch: compile + import + smoke test runs
- **Type:** Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** Repair patch has been applied
- **Test Data:** Patched Python files
- **Steps:**
  1. Apply repair patch
  2. Run compile check
  3. Run import check
  4. Run smoke test
  5. Verify all three stages execute
- **Expected Result:**
  - All three validation stages execute in order
  - Results logged in validator report
  - Pass/fail determined by all three stages
- **Automation Status:** Automated
- **Automation ID:** AT-FR-012-INT-01

---

## NFR-1: First response ≤ 5 seconds

### TC-NFR-001-01
- **Test Case ID:** TC-NFR-001-01
- **Requirement ID:** NFR-1
- **Title:** First acknowledgment sent within 5 seconds of voice message
- **Type:** Non-Functional
- **Level:** Performance
- **Priority:** High
- **Preconditions:** System is running under normal load
- **Test Data:** 50 voice message requests
- **Steps:**
  1. Send voice message
  2. Measure time until first Telegram response
  3. Repeat 50 times
- **Expected Result:**
  - p95 of first response time ≤ 5 seconds
- **Automation Status:** Automated
- **Automation ID:** AT-NFR-001-PERF-01

---

## NFR-2: Idempotent persistence

### TC-NFR-002-01
- **Test Case ID:** TC-NFR-002-01
- **Requirement ID:** NFR-2
- **Title:** Duplicate webhook update does not create duplicate run
- **Type:** Non-Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** A run already exists for a given update_id
- **Test Data:** Same Telegram update JSON sent twice
- **Steps:**
  1. Send webhook update
  2. Send identical webhook update again
  3. Count runs
- **Expected Result:**
  - Only one run exists
  - Second request returns same run_id
- **Automation Status:** Automated
- **Automation ID:** AT-NFR-002-INT-01

---

## NFR-3: STT error fallback

### TC-NFR-003-01
- **Test Case ID:** TC-NFR-003-01
- **Requirement ID:** NFR-3
- **Title:** STT failure does not crash run; offers manual confirmation
- **Type:** Non-Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** STT service returns error
- **Test Data:** Valid voice file, but STT service unavailable
- **Steps:**
  1. Send voice message with mocked STT failure
  2. Verify run state
  3. Verify user receives fallback message
- **Expected Result:**
  - Run is NOT in `failed` state
  - User receives message asking to type their request manually
  - Run transitions to `waiting_for_user`
- **Automation Status:** Automated
- **Automation ID:** AT-NFR-003-INT-01

---

## NFR-4: Choice + text clarification

### TC-NFR-004-01
- **Test Case ID:** TC-NFR-004-01
- **Requirement ID:** NFR-4
- **Title:** Clarification supports both choice buttons and free text
- **Type:** Non-Functional
- **Level:** Unit
- **Priority:** Medium
- **Preconditions:** None
- **Test Data:** InterruptPayload with choices and response_type
- **Steps:**
  1. Create interrupt with choices ["Option A", "Option B"] and response_type="choice"
  2. Verify choice selection works
  3. Create interrupt with response_type="text"
  4. Verify free text input works
- **Expected Result:**
  - Both interaction modes produce valid state updates
- **Automation Status:** Automated
- **Automation ID:** AT-NFR-004-UNIT-01

---

## NFR-5: Resume in same thread_id

### TC-NFR-005-01
- **Test Case ID:** TC-NFR-005-01
- **Requirement ID:** NFR-5
- **Title:** After user reply, execution resumes in same thread
- **Type:** Non-Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** Run is interrupted in thread_id="thread-123"
- **Test Data:** User reply in thread_id="thread-123"
- **Steps:**
  1. Create run with thread_id
  2. Interrupt run
  3. Resume with user reply
  4. Verify thread_id preserved
- **Expected Result:**
  - Same thread_id used throughout
  - State continuity maintained
- **Automation Status:** Automated
- **Automation ID:** AT-NFR-005-INT-01

---

## NFR-6: Side effects only via tools

### TC-NFR-006-01
- **Test Case ID:** TC-NFR-006-01
- **Requirement ID:** NFR-6
- **Title:** LLM and code nodes cannot perform side effects directly
- **Type:** Non-Functional
- **Level:** Unit
- **Priority:** High
- **Preconditions:** None
- **Test Data:** AtomicAction definitions
- **Steps:**
  1. Verify that LLM-type actions only produce text output
  2. Verify that code-type actions only perform transformations
  3. Verify that only tool-type actions can call external services
- **Expected Result:**
  - Side-effect capabilities restricted to tool-type actions
  - LLM/code actions return data only
- **Automation Status:** Automated
- **Automation ID:** AT-NFR-006-UNIT-01

---

## NFR-7: Step tracing

### TC-NFR-007-01
- **Test Case ID:** TC-NFR-007-01
- **Requirement ID:** NFR-7
- **Title:** Each executed step logs input, output, critic verdict, retries
- **Type:** Non-Functional
- **Level:** Integration
- **Priority:** Medium
- **Preconditions:** A multi-step run completes
- **Test Data:** 3-step plan execution
- **Steps:**
  1. Execute a 3-step plan
  2. Inspect critic_log
- **Expected Result:**
  - critic_log has entries for each step
  - Each entry contains verdict and score
- **Automation Status:** Automated
- **Automation ID:** AT-NFR-007-INT-01

---

## NFR-8: Interrupt survives restart

### TC-NFR-008-01
- **Test Case ID:** TC-NFR-008-01
- **Requirement ID:** NFR-8
- **Title:** Interrupted run can resume after service restart
- **Type:** Non-Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** Run is interrupted, state persisted to DB
- **Test Data:** Interrupted RunState with checkpointed state
- **Steps:**
  1. Create and interrupt a run
  2. Simulate service restart (reload state from persistence)
  3. Send user reply
  4. Verify resume works
- **Expected Result:**
  - State loaded correctly from persistence
  - Run resumes with full context
  - No data loss
- **Automation Status:** Automated
- **Automation ID:** AT-NFR-008-INT-01

---

## NFR-9: Reply latency ≤ 3 seconds

### TC-NFR-009-01
- **Test Case ID:** TC-NFR-009-01
- **Requirement ID:** NFR-9
- **Title:** Resume confirmation sent within 3 seconds of user reply
- **Type:** Non-Functional
- **Level:** Performance
- **Priority:** High
- **Preconditions:** Run is interrupted, user sends reply
- **Test Data:** 20 interrupt-resume cycles
- **Steps:**
  1. Interrupt run
  2. Send user reply
  3. Measure time to resume confirmation
  4. Repeat 20 times
- **Expected Result:**
  - p95 of resume confirmation latency ≤ 3 seconds
- **Automation Status:** Automated
- **Automation ID:** AT-NFR-009-PERF-01

---

## NFR-10: Sandboxed subprocess

### TC-NFR-010-01
- **Test Case ID:** TC-NFR-010-01
- **Requirement ID:** NFR-10
- **Title:** Generated code cannot access filesystem outside sandbox
- **Type:** Non-Functional
- **Level:** Integration
- **Priority:** High
- **Preconditions:** Sandbox runner is configured
- **Test Data:** Generated code attempting `os.listdir("/")`
- **Steps:**
  1. Execute generated code that tries to access root filesystem
  2. Verify sandbox blocks access
- **Expected Result:**
  - Code execution is blocked or returns error
  - No filesystem access outside designated sandbox directory
- **Automation Status:** Automated
- **Automation ID:** AT-NFR-010-INT-01
- **Notes:** Security-critical test

---

## NFR-11: Deterministic repair log

### TC-NFR-011-01
- **Test Case ID:** TC-NFR-011-01
- **Requirement ID:** NFR-11
- **Title:** Repair log contains all attempts with reproducible details
- **Type:** Non-Functional
- **Level:** Unit
- **Priority:** Medium
- **Preconditions:** Repair loop completed (success or escalation)
- **Test Data:** 3 repair attempts with different fix strategies
- **Steps:**
  1. Run repair loop with known failing code
  2. Inspect repair log
- **Expected Result:**
  - Each attempt has: attempt_number, error_class, fix_strategy, files_changed, validation_passed, traceback
  - Log is ordered and complete
  - Same input produces same log structure
- **Automation Status:** Automated
- **Automation ID:** AT-NFR-011-UNIT-01

---

## E2E Test Cases

### TC-E2E-001
- **Test Case ID:** TC-E2E-001
- **Requirement IDs:** FR-1, FR-2, FR-3, FR-6, FR-7, FR-8, US-2
- **Title:** Voice message → research → Google Docs report → Telegram link
- **Type:** Functional
- **Level:** E2E
- **Priority:** High
- **Preconditions:** All services running, mocked LLM/STT/Google Docs
- **Test Data:** Voice file saying "Make a report on EV market in Saudi Arabia and save to Google Docs"
- **Steps:**
  1. Send voice message to bot
  2. Verify STT transcript
  3. Verify plan is created
  4. Verify tools are bound
  5. Verify execution completes
  6. Verify artifact is created in Google Docs
  7. Verify user receives link
- **Expected Result:**
  - Full pipeline completes
  - Google Docs link sent to user
  - All steps logged
- **Automation Status:** Automated
- **Automation ID:** AT-E2E-001

### TC-E2E-002
- **Test Case ID:** TC-E2E-002
- **Requirement IDs:** FR-4, FR-5, FR-9, FR-10, US-1
- **Title:** Ambiguous request → clarification → resume → completion
- **Type:** Functional
- **Level:** E2E
- **Priority:** High
- **Preconditions:** All services running
- **Test Data:** Text message "Do something with the data"
- **Steps:**
  1. Send ambiguous text message
  2. Verify clarification question sent
  3. Reply with clarification
  4. Verify run resumes
  5. Verify completion
- **Expected Result:**
  - Clarification sent as user_input step
  - User reply resumes execution
  - Final result delivered
- **Automation Status:** Automated
- **Automation ID:** AT-E2E-002

### TC-E2E-003
- **Test Case ID:** TC-E2E-003
- **Requirement IDs:** FR-11, FR-12, US-3
- **Title:** Workflow authoring with compile error → auto-repair → success
- **Type:** Functional
- **Level:** E2E
- **Priority:** High
- **Preconditions:** Workflow compiler available
- **Test Data:** TO-BE process description
- **Steps:**
  1. Submit workflow description
  2. Verify spec.yaml generated
  3. Verify code generated (with intentional error in mock)
  4. Verify compile error detected
  5. Verify repair attempted
  6. Verify successful repair
  7. Verify workflow executes
- **Expected Result:**
  - Spec and code generated
  - Error detected and repaired automatically
  - Workflow executes successfully after repair
- **Automation Status:** Automated
- **Automation ID:** AT-E2E-003
