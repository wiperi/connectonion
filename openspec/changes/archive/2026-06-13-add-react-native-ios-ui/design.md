## Context

oo-chat currently proves the hosted-agent chat experience on the web. The important reusable layer is not the Next.js UI itself; it is the connectonion-ts hosted-agent protocol client. Today that protocol client is reachable through `RemoteAgent`, while human-friendly session restore, React lifecycle, and persistence live in `useAgentForHuman` plus a Zustand/localStorage store. The web app then derives pending ask_user, approval, onboarding, plan review, and ULW state from the SDK UI list.

React Native is the selected path for the first iOS UI because it can reuse TypeScript protocol logic and keeps an Android path open later. It still needs native platform adapters because browser localStorage, browser key storage, Node fallback modules, and React DOM assumptions do not hold on iOS.

The hosted-agent protocol remains the source of truth. The iOS client must continue to use CONNECT, INPUT, SESSION_STATUS, PONG, ASK_USER_RESPONSE, APPROVAL_RESPONSE, PLAN_REVIEW_RESPONSE, ULW_RESPONSE, ONBOARD_SUBMIT, and mode_change messages with Ed25519 signed payloads where required.

## Goals / Non-Goals

**Goals:**

- Extract the durable human-agent session behavior from React/Zustand into a connectonion-ts core that can run in web and React Native environments.
- Preserve oo-chat behavior while giving React Native a non-React-DOM API to create sessions, subscribe to snapshots, send commands, reconnect, persist session data, and manage identity.
- Build an iOS React Native chat UI that renders the same ChatItem conversation model and supports the same human interaction gates as oo-chat.
- Store private identity material in an iOS secure storage adapter and keep conversation/session data in a separate mobile persistence adapter.
- Add adapter-level and session-core tests so protocol behavior can be verified without a device.

**Non-Goals:**

- A native Swift SDK or SwiftUI app.
- A backend-for-frontend proxy that owns user signing keys.
- A hosted-agent WebSocket protocol redesign.
- Android app polish, although adapter boundaries should not block Android later.
- Full visual parity with oo-chat component internals; behavioral parity matters more than sharing React DOM components.

## Decisions

### Decision 1: Split connectonion-ts into core, adapters, and UI bindings

The shared architecture will be:

```text
Application UI
  Web oo-chat / React Native iOS screens
        |
UI binding
  useAgentForHuman / RN hook or view model
        |
Session core
  AgentSession, reducer, event mapper, command API
        |
Platform adapters
  AgentTransport, SessionRepository, KeyManager, AppLifecycle, AttachmentStore
        |
Concrete platform
  Browser localStorage/WebSocket/tweetnacl
  React Native AsyncStorage-or-SQLite/WebSocket/Keychain/Ed25519
```

Rationale: this preserves the working TypeScript protocol path while making React and Zustand implementation details replaceable. The existing `RemoteAgent` behavior should be moved or wrapped into the session core in small steps rather than rewritten in one pass.

Alternatives considered:

- WebView wrapper: fastest, but it does not create a real mobile SDK boundary.
- Swift native SDK: strongest iOS fit, but duplicates protocol logic too early.
- Server-side proxy: simplifies the app, but changes identity ownership and adds a trust-sensitive service.

### Decision 2: UI observes immutable snapshots and sends commands

The core will expose a session object with a snapshot subscription API and command methods. UI code receives immutable `AgentSessionSnapshot` values that include status, connection state, session id, ChatItem list, mode, ULW counters, pending human gates, current error, and timestamps. UI code sends commands such as input, respondToAskUser, respondToApproval, respondToPlanReview, respondToUlwTurnsReached, submitOnboard, setMode, reconnect, checkSessionStatus, and reset.

Rationale: this matches the existing direction where UI should render state and not mutate protocol internals. Streaming is represented as repeated snapshot emissions where one ChatItem is updated incrementally.

Alternative considered:

- Expose raw WebSocket events to each UI. This is flexible, but it leaks protocol churn into web and iOS rendering code.

### Decision 3: Keep protocol mapping in one shared reducer pipeline

Incoming WebSocket frames will flow through:

```text
raw frame -> ServerEvent -> EventMapper -> AgentDomainEvent[] -> AgentSessionReducer -> AgentSessionSnapshot
```

The reducer is pure. Transport, persistence, timers, and signing stay outside reducer logic. Interactive events such as ask_user, approval_needed, plan_review, onboard_required, ULW pause, OUTPUT, and ERROR emit snapshots immediately. High-frequency assistant or progress deltas can be batched in the session core before emission.

Rationale: one mapper/reducer path keeps hosted-agent protocol compatibility consistent across web and iOS.

Alternative considered:

- Let `RemoteAgent` keep mutating `_chatItems` directly and have RN mirror it. This works short term but keeps mutable protocol state tied to implementation details that are hard to persist and test.

### Decision 4: Platform adapters own persistence, key storage, and lifecycle

The core depends on interfaces:

- `AgentTransport`: WebSocket open/send/close plus connection events.
- `SessionRepository`: load/save/delete/list session snapshots and durable conversation metadata.
- `KeyManager`: load/create/sign identity; private keys never enter ordinary conversation storage.
- `AppLifecycle`: foreground/background/network state events.
- `AttachmentStore`: normalize file/image attachments into protocol payloads and persistence-safe metadata.

Browser adapters can continue using localStorage and tweetnacl. React Native iOS adapters must use secure storage for private key material and a separate persistence layer for sessions. The first implementation may use AsyncStorage if the data volume stays small; SQLite is preferred if conversation lists, files, or larger UI histories need durable indexing.

Rationale: iOS secure identity and app lifecycle are not browser concepts, so they must be injected.

Alternative considered:

- Add conditionals inside `address-browser.ts` and the Zustand store. That would spread platform checks through the SDK and make future native clients harder.

### Decision 5: React Native UI reuses data contracts, not web DOM components

The iOS app will render `ChatItem` variants and pending gate models that match oo-chat behavior, but it will use React Native components rather than reusing Next.js/Tailwind DOM components. Shared pure helpers such as event mapping, pending-state extraction, redaction, attachment normalization, title generation, and dedupe logic can move to shared packages when they have no DOM dependency.

Rationale: the chat semantics should be shared; the rendering primitives are platform-specific.

Alternative considered:

- Share web components with a compatibility layer. That adds styling and DOM friction before protocol reuse is stable.

### Decision 6: Preserve web compatibility during migration

The migration should first add the shared core behind existing APIs, then adapt `useAgentForHuman` and oo-chat to call the new core. After web parity tests pass, add React Native adapters and the iOS app. Existing public exports should continue to work unless a future proposal explicitly marks a breaking change.

Rationale: oo-chat is the current proof point and should not regress while the mobile work is built.

## Risks / Trade-offs

- React Native bundler rejects Node/browser assumptions in connectonion-ts -> Keep Node fallback imports behind adapter boundaries and provide RN-safe entrypoints.
- Ed25519 signatures diverge between platforms -> Add cross-platform canonical JSON signing vectors shared by browser, Node, and RN tests.
- Session persistence grows beyond AsyncStorage limits -> Keep persistence behind `SessionRepository` and allow SQLite replacement without core changes.
- Background WebSocket behavior is limited by iOS -> Treat backgrounding as disconnect-and-resume, persist snapshots before background, and reconnect on foreground.
- Duplicated UI logic between oo-chat and RN -> Move only pure derivation helpers into shared code, leaving presentation components platform-specific.
- Migration destabilizes oo-chat -> Port web onto the core behind the existing hook API and run existing oo-chat/connectonion-ts tests before mobile work.

## Migration Plan

1. Add session-core interfaces and tests around current hosted-agent event handling.
2. Wrap or refactor `RemoteAgent` into the core while keeping current connectonion-ts exports intact.
3. Move React/Zustand persistence and hydration into a web adapter that feeds the shared core.
4. Update oo-chat to keep using the existing hook-level API backed by the core.
5. Add React Native adapters for WebSocket, secure keys, session persistence, attachments, and app lifecycle.
6. Build the RN iOS app screens and wire them to the shared session API.
7. Validate against mocked transport tests, connectonion-ts tests, oo-chat build/tests, and an iOS simulator smoke test.

Rollback strategy: keep the existing `RemoteAgent` and `useAgentForHuman` behavior available until web parity and RN smoke tests pass. If the core migration fails, revert the hook adapter to the current implementation and keep RN work behind the new entrypoint.

## Open Questions

- Should the first RN persistence adapter use AsyncStorage for speed or SQLite for larger conversation histories?
- Which React Native secure key package should be standardized for iOS Keychain access?
- Should the RN app live inside this repository, inside `connectonion-ts`, or as a separate app workspace?
- Which attachment size limits should the mobile client enforce before sending images or files through the hosted-agent protocol?
