## ADDED Requirements

### Requirement: Platform-neutral session core
The connectonion-ts SDK SHALL provide a human-agent session core that can run without importing React, Zustand, browser localStorage, React DOM, or Node-only WebSocket modules.

#### Scenario: Core imports in non-React environment
- **WHEN** a React Native-compatible entrypoint imports the session core
- **THEN** the import MUST NOT require React, Zustand, browser localStorage, React DOM, or Node-only WebSocket modules

#### Scenario: Web adapter keeps existing hook behavior
- **WHEN** the existing React hook API is used by oo-chat
- **THEN** it SHALL delegate to the shared session behavior while preserving the current hook-level fields and command semantics

### Requirement: Snapshot subscription model
The session core SHALL expose immutable session snapshots through a subscribe/unsubscribe API and SHALL expose command methods for user actions instead of requiring UI code to mutate session internals.

#### Scenario: UI receives current snapshot
- **WHEN** UI code subscribes to a session
- **THEN** the session SHALL deliver the latest snapshot and subsequent snapshots whenever observable state changes

#### Scenario: UI unsubscribes
- **WHEN** UI code calls the unsubscribe function returned by subscribe
- **THEN** the session MUST stop delivering snapshots to that listener

#### Scenario: UI sends a command
- **WHEN** UI code sends an input, approval response, ask_user response, plan review response, ULW response, onboard submission, mode change, reconnect, session-status check, or reset command
- **THEN** the session core SHALL translate the command into the appropriate protocol action without exposing mutable internal state to the UI

### Requirement: Hosted-agent protocol compatibility
The session core SHALL preserve the hosted-agent WebSocket protocol semantics used by the current connectonion-ts `RemoteAgent` client.

#### Scenario: Connects to hosted agent
- **WHEN** a session connects to an agent through the relay or a resolved direct endpoint
- **THEN** it SHALL send a CONNECT message with signed payload data, target address routing when needed, session id when present, and client session data when present

#### Scenario: Sends user input
- **WHEN** the user sends a prompt with optional images or files
- **THEN** the session SHALL send an INPUT message with an input id, prompt, attachment payloads, and relay routing fields when needed

#### Scenario: Responds to human interaction gate
- **WHEN** the user answers ask_user, approval, plan review, ULW pause, or onboarding prompts
- **THEN** the session SHALL send the matching protocol message type expected by hosted agents

#### Scenario: Handles keepalive
- **WHEN** the server sends PING
- **THEN** the session SHALL update connection health and send PONG

### Requirement: Event mapping and reducer pipeline
The session core SHALL convert raw server events into domain events and then into immutable snapshots using a shared event mapper and pure reducer.

#### Scenario: Tool call lifecycle
- **WHEN** the server sends tool_call followed by tool_result for the same tool id
- **THEN** the resulting snapshots SHALL contain one tool_call ChatItem whose status and result update from running to done or error

#### Scenario: LLM lifecycle
- **WHEN** the server sends llm_call followed by llm_result
- **THEN** the resulting snapshots SHALL contain a thinking ChatItem whose status, duration, model, usage, and context fields reflect the latest server data

#### Scenario: Output completion
- **WHEN** the server sends OUTPUT with result and session data
- **THEN** the session SHALL update the snapshot session, append or preserve the final agent ChatItem, mark processing idle, and resolve the active input command

#### Scenario: Error completion
- **WHEN** the server sends ERROR
- **THEN** the session SHALL expose an error snapshot, close or mark the connection disconnected, and reject the active input command

### Requirement: Streaming through snapshots
The session core SHALL represent streaming or incremental assistant output as repeated snapshot updates rather than a separate UI observation model.

#### Scenario: Incremental assistant content
- **WHEN** the server emits repeated assistant or assistant-delta style events for the same response
- **THEN** the session SHALL update the relevant agent ChatItem across successive snapshots

#### Scenario: Noisy events are throttled
- **WHEN** high-frequency incremental events arrive faster than the UI needs to render
- **THEN** the session core MAY batch snapshot emissions while still emitting interactive gates, completion, and errors immediately

### Requirement: Adapter-based persistence and identity
The session core SHALL depend on injected adapters for transport, session persistence, secure identity, lifecycle, and attachment handling.

#### Scenario: Web platform composition
- **WHEN** the web adapter creates a session
- **THEN** it SHALL provide browser-compatible transport, persistence, and signing implementations without changing the session core

#### Scenario: React Native platform composition
- **WHEN** the React Native adapter creates a session
- **THEN** it SHALL provide React Native-compatible transport, secure key storage, session persistence, lifecycle, and attachment implementations without changing the session core

#### Scenario: Private keys are isolated
- **WHEN** session snapshots or conversation metadata are persisted
- **THEN** private key material MUST NOT be written into ordinary session or conversation storage

### Requirement: Session restore and reconnect
The session core SHALL support durable session restore and reconnect semantics equivalent to the current web client.

#### Scenario: Restores persisted session
- **WHEN** a session is created with an existing session id and persisted session data
- **THEN** it SHALL hydrate the snapshot from persisted data before reconnecting

#### Scenario: Reconnects running session
- **WHEN** the server reports an existing session as running during reconnect
- **THEN** the session SHALL resume forwarding server events for that session

#### Scenario: Merges newer server session
- **WHEN** CONNECTED or OUTPUT reports newer server session data and chat items
- **THEN** the session SHALL merge or replace local snapshot data according to the server-newer signal

### Requirement: Core testability
The session core SHALL be testable with mocked adapters and deterministic protocol fixtures.

#### Scenario: Mock transport drives session
- **WHEN** tests provide a mock transport that emits hosted-agent events
- **THEN** tests SHALL verify snapshot changes without opening a real WebSocket

#### Scenario: Signing vectors are stable
- **WHEN** tests sign canonical payload fixtures in Node, browser-compatible, and React Native-compatible adapters
- **THEN** the resulting signatures SHALL verify against the same public key and canonical payload rules
