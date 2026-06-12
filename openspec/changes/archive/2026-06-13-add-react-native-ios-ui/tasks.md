## 1. Baseline and Test Fixtures

- [ ] 1.1 Capture current connectonion-ts hosted-agent behavior with focused tests around CONNECT, INPUT, PING/PONG, OUTPUT, ERROR, ask_user, approval_needed, plan_review, onboard_required, ulw_turns_reached, and mode_change handling.
- [ ] 1.2 Add deterministic canonical JSON and Ed25519 signing fixtures that can be reused by Node, browser-compatible, and React Native-compatible key adapters.
- [ ] 1.3 Add import-boundary tests that verify the new session-core entrypoint does not import React, Zustand, browser localStorage, React DOM, or Node-only WebSocket modules.
- [ ] 1.4 Document the current public hook fields and command semantics from `useAgentForHuman` so web compatibility can be checked after migration.

## 2. Shared Session Core

- [ ] 2.1 Add connectonion-ts session-core types for `AgentSessionSnapshot`, `AgentSessionCommand`, `AgentTransport`, `SessionRepository`, `KeyManager`, `AppLifecycle`, `AttachmentStore`, and unsubscribe-capable snapshot listeners.
- [ ] 2.2 Move hosted-agent server event parsing and ChatItem mapping into a shared mapper that accepts protocol events and produces domain events.
- [ ] 2.3 Implement a pure reducer that converts prior snapshots plus domain events into new immutable snapshots.
- [ ] 2.4 Implement `AgentSession` orchestration for hydrate, subscribe, input, reconnect, checkSessionStatus, setMode, gate responses, onboard submit, reset, dispose, and persistence saves.
- [ ] 2.5 Preserve current relay endpoint resolution and direct endpoint fallback behavior behind the transport/session composition layer.
- [ ] 2.6 Add mocked-transport tests for session lifecycle, snapshot emission, unsubscribe behavior, input completion, error completion, server-newer merge, and reconnect.

## 3. Web Adapter and oo-chat Compatibility

- [ ] 3.1 Implement browser transport, browser key manager, browser session repository, browser lifecycle, and browser attachment adapters for the shared core.
- [ ] 3.2 Rebuild `useAgentForHuman` on top of the shared session core while preserving its current return shape and command names.
- [ ] 3.3 Update oo-chat's SDK integration to use the migrated hook without changing chat behavior.
- [ ] 3.4 Move pure pending-state extraction, UI dedupe, title, redaction, and attachment helpers into shared code only where they have no DOM or Next.js dependency.
- [ ] 3.5 Run connectonion-ts tests and oo-chat build or lint checks to confirm web behavior did not regress.

## 4. React Native Platform Adapters

- [ ] 4.1 Add a React Native-safe connectonion-ts entrypoint that exports the session core and RN adapter factory without pulling web-only or Node-only modules.
- [x] 4.2 Implement React Native WebSocket transport using the platform WebSocket implementation.
- [ ] 4.3 Implement iOS secure key storage adapter for Ed25519 identity creation, loading, and signing, keeping private keys out of ordinary session persistence.
- [ ] 4.4 Implement React Native session repository using AsyncStorage or SQLite behind the `SessionRepository` interface.
- [ ] 4.5 Implement React Native app lifecycle adapter for foreground, background, and reconnect triggers.
- [ ] 4.6 Implement React Native attachment adapter for images and files with persistence-safe metadata and payload normalization.
- [ ] 4.7 Add adapter tests or mocks that verify RN composition can create a session and satisfy the shared core requirements.

## 5. React Native iOS App

- [x] 5.1 Create the React Native iOS app/package or example workspace in the agreed repository location.
- [x] 5.2 Add app shell navigation for agent selection, conversation list, active chat, and settings or identity display.
- [x] 5.3 Implement conversation create, select, delete, title, persistence, and restore behavior.
- [x] 5.4 Implement the chat message list for user, agent, thinking, tool_call, intent, eval, compact, tool_blocked, files_received, onboard_success, and error-visible states.
- [x] 5.5 Implement chat input with text send, disabled/working state, elapsed-time or progress affordance, and duplicate-send protection.
- [x] 5.6 Implement image and file attachment selection, preview, normalization, and send integration.
- [x] 5.7 Implement approval mode controls for safe, plan, accept_edits, and ulw with configurable turn budget.

## 6. Human Gate UI

- [x] 6.1 Implement ask_user UI with text input, options, multi-select, optional fields, and ASK_USER_RESPONSE dispatch.
- [x] 6.2 Implement approval_needed UI with tool name, arguments, description, batch remaining data, approve once, approve session, and reject actions.
- [x] 6.3 Implement onboard_required UI for invite-code and payment methods with signed ONBOARD_SUBMIT dispatch.
- [x] 6.4 Implement plan_review UI with plan content rendering and PLAN_REVIEW_RESPONSE dispatch.
- [x] 6.5 Implement ulw_turns_reached UI with turns used, max turns, continue action, and mode-switch action.

## 7. Mobile Lifecycle and Verification

- [x] 7.1 Persist the latest snapshot before backgrounding and reconnect or check session status on foreground.
- [x] 7.2 Verify first launch creates an identity, subsequent launches reuse the same address, and private keys are not written to session or conversation storage.
- [x] 7.3 Add simulator or integration smoke test for sending a prompt to a hosted agent and receiving an agent response.
- [ ] 7.4 Add simulator or mocked integration coverage for approvals, ask_user, onboarding, plan review, ULW pause, disconnect, reconnect, and app restart restore.
- [ ] 7.5 Run connectonion-ts tests, oo-chat compatibility checks, React Native type checks, and iOS simulator smoke checks.
- [ ] 7.6 Update developer documentation with the new session-core API, adapter responsibilities, RN setup commands, and known iOS lifecycle limits.
