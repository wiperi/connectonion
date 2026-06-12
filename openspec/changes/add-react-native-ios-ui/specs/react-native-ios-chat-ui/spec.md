## ADDED Requirements

### Requirement: React Native iOS chat app shell
The system SHALL provide a React Native iOS chat UI that can create, select, persist, and delete hosted-agent conversations.

#### Scenario: Starts a new conversation
- **WHEN** the user selects an agent and starts a new chat
- **THEN** the app SHALL create a stable session id, persist conversation metadata, and render an empty input-ready chat view

#### Scenario: Selects existing conversation
- **WHEN** the user opens a persisted conversation
- **THEN** the app SHALL restore the latest persisted snapshot and attempt reconnect according to session status

#### Scenario: Deletes conversation
- **WHEN** the user deletes a conversation
- **THEN** the app SHALL remove persisted conversation metadata and session state for that conversation

### Requirement: Hosted-agent messaging
The React Native iOS UI SHALL send prompts to hosted agents through the connectonion-ts shared session API and render ChatItem snapshots from that API.

#### Scenario: Sends prompt
- **WHEN** the user submits text input
- **THEN** the app SHALL call the session input command, render the user ChatItem, and show working state until completion, waiting state, or error

#### Scenario: Receives agent response
- **WHEN** the session snapshot includes an agent ChatItem
- **THEN** the app SHALL render the agent message in chronological order without requiring a page refresh

#### Scenario: Handles disconnect
- **WHEN** the session connection state becomes disconnected during a request
- **THEN** the app SHALL surface the error or reconnect state and preserve the last durable snapshot

### Requirement: Human interaction gates
The React Native iOS UI SHALL support the same human interaction gate types used by oo-chat.

#### Scenario: ask_user prompt
- **WHEN** the snapshot contains a pending ask_user item
- **THEN** the app SHALL render the question, options, multi-select state, and optional fields, then send ASK_USER_RESPONSE when the user answers

#### Scenario: approval prompt
- **WHEN** the snapshot contains approval_needed
- **THEN** the app SHALL render tool name, arguments, description, batch remaining data when present, and approve or reject actions that send APPROVAL_RESPONSE

#### Scenario: onboarding prompt
- **WHEN** the snapshot contains onboard_required
- **THEN** the app SHALL render supported onboarding methods and send ONBOARD_SUBMIT with a signed invite code or payment payload

#### Scenario: plan review prompt
- **WHEN** the snapshot contains plan_review
- **THEN** the app SHALL render the plan content and send PLAN_REVIEW_RESPONSE with the user's review message

#### Scenario: ULW turns reached prompt
- **WHEN** the snapshot contains ulw_turns_reached
- **THEN** the app SHALL render turns used, max turns, continue action, and mode-switch action that send ULW_RESPONSE

### Requirement: Approval mode controls
The React Native iOS UI SHALL expose the agent approval modes supported by the session core.

#### Scenario: Changes approval mode
- **WHEN** the user selects safe, plan, accept_edits, or ulw mode
- **THEN** the app SHALL call the session setMode command and render the updated mode from the next snapshot

#### Scenario: Configures ULW turns
- **WHEN** the user selects ULW mode with a turn budget
- **THEN** the app SHALL pass the turn budget to the session and render turns used and turns remaining when available

### Requirement: iOS identity and secure storage
The React Native iOS UI SHALL use a secure identity adapter for ConnectOnion signing keys.

#### Scenario: First launch identity
- **WHEN** no local identity exists on first launch
- **THEN** the app SHALL create an Ed25519 identity and store private key material in an iOS secure storage adapter

#### Scenario: Subsequent launch identity
- **WHEN** a local identity exists on subsequent launch
- **THEN** the app SHALL load the same address without regenerating keys

#### Scenario: Ordinary persistence excludes private keys
- **WHEN** conversation or session data is saved
- **THEN** the app MUST NOT store private key material in AsyncStorage, SQLite conversation tables, logs, or exported session data

### Requirement: iOS session persistence
The React Native iOS UI SHALL persist conversation metadata and durable session snapshots across app restarts.

#### Scenario: App restarts
- **WHEN** the app is terminated and relaunched
- **THEN** persisted conversations SHALL still appear with titles, agent addresses, session ids, and last known chat snapshots

#### Scenario: Large inline media is persisted safely
- **WHEN** snapshots include image or file data that exceeds mobile persistence limits
- **THEN** the app SHALL persist metadata or storage references instead of blindly writing oversized inline payloads into the conversation store

### Requirement: iOS lifecycle and reconnect
The React Native iOS UI SHALL handle foreground, background, and reconnect behavior using mobile lifecycle events.

#### Scenario: App enters background
- **WHEN** iOS moves the app to background
- **THEN** the app SHALL save the latest snapshot and avoid assuming the WebSocket remains alive

#### Scenario: App returns foreground
- **WHEN** iOS returns the app to foreground with an active or previously running conversation
- **THEN** the app SHALL check session status or reconnect and update UI state from server events or persisted data

#### Scenario: Network recovers
- **WHEN** network connectivity recovers after a disconnected state
- **THEN** the app SHALL allow reconnect without losing the current prompt history

### Requirement: Attachment input
The React Native iOS UI SHALL support sending text prompts with optional images and files through the session API.

#### Scenario: Sends image attachment
- **WHEN** the user attaches an image to a prompt
- **THEN** the app SHALL normalize the image into the attachment format accepted by the session core and render it with the user message

#### Scenario: Sends file attachment
- **WHEN** the user attaches a file to a prompt
- **THEN** the app SHALL include file name, type, size, and data reference or payload in the session command according to adapter policy

### Requirement: Mobile UI states
The React Native iOS UI SHALL render connected, working, waiting, reconnecting, disconnected, idle, and error states in the chat surface.

#### Scenario: Waiting for human response
- **WHEN** the session status is waiting because of a human interaction gate
- **THEN** the input area SHALL make the required user action clear and avoid sending unrelated gate responses

#### Scenario: Request in progress
- **WHEN** the session status is working
- **THEN** the app SHALL show elapsed time or progress affordance and prevent duplicate sends for the same prompt

#### Scenario: Error is visible
- **WHEN** the session snapshot contains an error
- **THEN** the app SHALL render a recoverable error state with retry or reconnect affordance when applicable

### Requirement: Web behavior parity guard
The React Native iOS work SHALL NOT regress oo-chat's existing hosted-agent behavior.

#### Scenario: Existing web chat continues
- **WHEN** oo-chat uses the migrated connectonion-ts hook API
- **THEN** sending messages, restoring sessions, approvals, ask_user, onboarding, plan review, ULW mode, and reconnect SHALL continue to work as before

#### Scenario: Shared helper changes are platform-neutral
- **WHEN** a helper is shared between oo-chat and the React Native app
- **THEN** it MUST NOT import DOM-only, Next.js-only, or React Native-only modules
