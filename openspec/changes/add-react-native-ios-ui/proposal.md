## Why

ConnectOnion already has a working web UI in oo-chat, but the reusable human-agent client logic is still coupled to browser assumptions such as React hooks, Zustand persistence, localStorage keys, and browser-focused identity storage. A React Native iOS client should reuse the existing connectonion-ts protocol surface while replacing platform-specific storage, secure key handling, lifecycle, and UI bindings.

## What Changes

- Introduce a platform-neutral human-agent session core inside connectonion-ts that owns protocol state, session snapshots, commands, event mapping, reconnect, mode changes, and human-interaction gates without depending on React or Zustand.
- Add platform adapter seams for WebSocket transport, session persistence, secure identity/key storage, file/image attachment handling, and app lifecycle events.
- Keep the existing web oo-chat behavior working by adapting the current React/Zustand implementation onto the shared core.
- Add a React Native iOS chat client that talks to hosted agents through connectonion-ts, renders the same ChatItem-driven conversation model as oo-chat, and supports approvals, ask_user, onboarding, plan review, ULW mode, reconnect, and persisted conversations.
- Add tests that prove the shared core behaves consistently across web-like and React Native-like adapters.

## Capabilities

### New Capabilities
- `cross-platform-agent-session-core`: Defines the reusable connectonion-ts session core, snapshot model, command surface, adapter boundaries, and parity requirements for hosted-agent communication.
- `react-native-ios-chat-ui`: Defines the React Native iOS chat experience, persistence, secure identity behavior, attachment support, reconnect semantics, and human-gate UI requirements.

### Modified Capabilities

None.

## Impact

- Affected code: `connectonion-ts/src/connect/`, `connectonion-ts/src/react/`, `connectonion-ts/src/address-browser.ts`, `connectonion-ts/tests/`, and the oo-chat SDK integration layer under `oo-chat/components/chat/`.
- New code area: a React Native iOS app/package or example, plus React Native platform adapters for connectonion-ts.
- APIs: connectonion-ts should expose a non-React human-agent session API in addition to the existing React hook API.
- Dependencies: likely React Native, iOS secure storage/Keychain adapter, React Native AsyncStorage or SQLite persistence, and any polyfills required for WebSocket, random UUIDs, text encoding, and Ed25519 signing.
- Systems: hosted-agent WebSocket protocol, relay endpoint resolution, direct endpoint fallback, session storage/merge behavior, OpenOnion identity signing, and oo-chat web compatibility.
