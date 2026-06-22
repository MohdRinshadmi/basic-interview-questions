"""
Generates a beautifully designed interview prep PDF
for Mohammed Rinshad M I — 50 beginner React Native + Full-Stack Q&A.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.colors import HexColor, white, black
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle,
    KeepTogether, Flowable
)
from reportlab.pdfgen import canvas

OUT_PATH = "/Users/ioss/Documents/StudyProjects/interview/basic/Rinshad_RN_FullStack_Interview_Prep.pdf"

# ---------- Color palette (modern, clean) ----------
PRIMARY      = HexColor("#1E3A8A")   # deep indigo
ACCENT       = HexColor("#0EA5E9")   # sky blue
SUCCESS      = HexColor("#16A34A")   # green
WARN         = HexColor("#D97706")   # amber
PURPLE       = HexColor("#7C3AED")   # purple
ROSE         = HexColor("#E11D48")   # rose
GRAY_DARK    = HexColor("#1F2937")
GRAY         = HexColor("#475569")
GRAY_LIGHT   = HexColor("#E2E8F0")
BG_SOFT      = HexColor("#F8FAFC")
CARD_BG      = HexColor("#F1F5F9")

# ---------- Sections ----------
SECTIONS = [
    {
        "title": "Section 1 — Experience at Infinite Open Source Solution LLP",
        "color": PRIMARY,
        "icon": "1",
        "blurb": "Questions drawn from your Full Stack Developer role: TypeScript component library, AI features, JS→TS migration, release pipeline, native modules, billing.",
    },
    {
        "title": "Section 2 — Project: AI Life Assistant Super App",
        "color": PURPLE,
        "icon": "2",
        "blurb": "Voice-first AI assistant — streaming LLM chat, Whisper, TTS, tool calling, native audio module.",
    },
    {
        "title": "Section 3 — Project: Cloud-Native IoT Analytics Dashboard",
        "color": ACCENT,
        "icon": "3",
        "blurb": "Live device telemetry over WebSockets, virtualized charts, offline sync, push alerts, Sentry tracing.",
    },
    {
        "title": "Section 4 — Project: AI-Powered Real-Time Collaboration Platform",
        "color": ROSE,
        "icon": "4",
        "blurb": "CRDT collaboration with Yjs, WebRTC voice notes, inline streaming AI on document selections.",
    },
    {
        "title": "Section 5 — Languages, Frontend & State Management",
        "color": SUCCESS,
        "icon": "5",
        "blurb": "TypeScript, Expo / EAS, Redux Toolkit, Zustand, React Query, Reanimated, Gesture Handler.",
    },
    {
        "title": "Section 6 — Native, Push & Real-Time",
        "color": WARN,
        "icon": "6",
        "blurb": "Native modules, FCM / APNs, background tasks, biometric auth, WebSockets vs polling.",
    },
    {
        "title": "Section 7 — AI / LLM on Mobile & Backend",
        "color": HexColor("#0891B2"),
        "icon": "7",
        "blurb": "Claude API, Vercel AI SDK, REST vs WebSockets, JWT, SQLite vs MongoDB vs Redis.",
    },
    {
        "title": "Section 8 — Debugging, Teamwork & Communication",
        "color": HexColor("#9333EA"),
        "icon": "8",
        "blurb": "Real-world debugging stories, production crashes, stakeholder communication, learning AI tools.",
    },
    # ================ VOLUME 2: AI / NATIVE / MOBILE DEEP DIVE ================
    {
        "title": "Section 9 — AI Streaming, Chat & Cost Optimization",
        "color": HexColor("#DC2626"),
        "icon": "9",
        "blurb": "Server-Sent Events, cancel handling, prompt caching, context window management, partial JSON, cost estimation, latency budgets.",
    },
    {
        "title": "Section 10 — Whisper, Voice AI & Audio Pipeline",
        "color": HexColor("#059669"),
        "icon": "10",
        "blurb": "Audio formats, sample rates, VAD libraries, AVAudioSession, echo cancellation, TTS choice, end-to-end voice latency.",
    },
    {
        "title": "Section 11 — Tool Calling, Agents & Safety",
        "color": HexColor("#B45309"),
        "icon": "11",
        "blurb": "Tool schemas, validation, multi-step agent loops, dangerous-tool guardrails, prompting techniques.",
    },
    {
        "title": "Section 12 — Native Modules: Bridge, JSI & TurboModules",
        "color": HexColor("#1E40AF"),
        "icon": "12",
        "blurb": "Old bridge vs new architecture, JSI, TurboModules, Fabric, Kotlin/Swift bridging, ViewManagers, autolinking, debugging native crashes, memory & threads.",
    },
    {
        "title": "Section 13 — Mobile Platform Integration",
        "color": HexColor("#BE185D"),
        "icon": "13",
        "blurb": "FCM setup, APNs, deep links, runtime permissions, in-app purchases, app lifecycle, secure storage, safe area, splash screens.",
    },
    {
        "title": "Section 14 — Real-time AI on Mobile & On-Device AI",
        "color": HexColor("#4338CA"),
        "icon": "14",
        "blurb": "WebSocket reconnect, background-stream handling, battery, Core ML / TFLite / ONNX, on-device vs cloud trade-offs.",
    },
]

# ---------- Q&A data ----------
# Each entry: (section_index, question, why, answer, tip)
QA = [
    # ===== SECTION 1: EXPERIENCE (10) =====
    (0,
     "Can you walk me through your current role at Infinite Open Source Solution LLP?",
     "Interviewers want a clear, structured summary of your day-to-day work and the breadth of your responsibilities.",
     "Sure! I joined <b>Infinite Open Source Solution LLP</b> in November 2023 as a <b>Full Stack Developer</b>. My main focus is building <b>React Native</b> apps with a <b>TypeScript + Node.js</b> backend, and I’ve shipped <b>20+ web and mobile apps</b> across e-commerce, IoT, and AI domains. On a typical day I’m writing TypeScript on both client and server, integrating <b>REST</b> and <b>WebSocket</b> APIs, building <b>native modules in Kotlin</b> when a feature isn’t available in JS, and pushing builds through <b>EAS</b> to the App Store and Play Store. I also own the AI-related work — streaming Claude and OpenAI responses, Whisper voice input — and the billing layer with Stripe and PayPal.",
     "Always end the answer with what you <b>own end-to-end</b> — interviewers love candidates who can say 'this is mine, I ship it.'"),

    (0,
     "How did you cut feature delivery time by 30%? Can you give an example?",
     "Tests whether you can quantify impact and explain the reasoning behind a productivity improvement.",
     "Yes — the biggest lever was building a <b>shared TypeScript component library</b>. Earlier, every project was re-implementing the same UI primitives — buttons, modals, form inputs, list rows — slightly differently. I extracted them into a single package with consistent props and theming, so a new screen that used to take a day now takes a few hours. I also added <b>Storybook</b> for visual previews and strict <b>TypeScript types</b> so misuse fails at compile time. After we rolled it out across three projects, feature lead-time dropped roughly <b>30%</b>, mostly because designers and engineers stopped re-debating basic UI patterns.",
     "When you give a number like '30%', be ready for a follow-up: <b>how did you measure it?</b> Have a one-line answer ready, like 'we tracked Jira lead-time before and after rollout.'"),

    (0,
     "What does a 'cross-platform TypeScript component library' actually contain, and why is it useful?",
     "Checks your understanding of code reuse, design systems, and the value of shared abstractions.",
     "It’s basically a <b>shared npm package</b> with primitives that work on both <b>React</b> and <b>React Native</b>. So you have <b>Button</b>, <b>Input</b>, <b>Modal</b>, <b>Card</b>, plus higher-level patterns like <b>FormRow</b> and <b>EmptyState</b>. The trick is the components expose the same <b>TypeScript props</b> everywhere, but internally they render <b>div / input</b> on web and <b>View / TextInput</b> on native. The value is consistency — one bug fix updates every app — and speed, because engineers stop re-styling the same elements per project. It also makes <b>design hand-off</b> much cleaner since designers can reference one library.",
     "Mention <b>versioning strategy</b> if asked deeper — say you use semantic versioning so consuming apps can upgrade safely."),

    (0,
     "What AI-powered mobile features have you actually shipped to production?",
     "Confirms your AI claims are real and tests how well you can talk through implementation details.",
     "I’ve shipped <b>streaming Claude and OpenAI chat</b> directly inside React Native apps — where each token appears as it arrives, instead of waiting for the whole response. I’ve integrated <b>Whisper</b> for <b>voice-to-text</b>, so the user can speak and we transcribe in real time. And I’ve built <b>conversational AI flows</b> with <b>tool calling</b>, where the LLM can trigger native actions like 'set a reminder' or 'open settings.' All of it runs inside our React Native shell, talking to the model APIs over <b>HTTPS / WebSockets</b>, with a small Node.js proxy to keep API keys off the device.",
     "Always mention the <b>API key proxy</b> — interviewers will check if you understand never to ship secrets in the mobile bundle."),

    (0,
     "Why did you migrate a live codebase from JavaScript to TypeScript? What problem were you trying to solve?",
     "Probes your reasoning, not just your tooling — checks if you understand the why behind a big refactor.",
     "We were hitting the same <b>runtime errors</b> over and over — undefined props, wrong shape from the API, typos in keys. They’d only show up in production because JavaScript doesn’t catch them at build time. So I proposed moving to <b>TypeScript</b> to catch that whole class of bugs at <b>compile time</b>. We did it <b>incrementally</b> — renaming files .ts/.tsx one by one and starting with <b>strict: false</b>, then tightening the config as we converted modules. Within a few months, the recurring 'cannot read property of undefined' bugs basically disappeared, and onboarding new devs got faster because types act as inline documentation.",
     "Frame TypeScript as a <b>safety net + documentation</b>, not as 'extra work.' That mindset is what senior interviewers want to hear."),

    (0,
     "How did you handle the JS-to-TypeScript migration without breaking the live app?",
     "Checks for safe-rollout instincts — important for any production change.",
     "Carefully and gradually. First I added a TypeScript config with <b>allowJs: true</b> so .js and .ts files could coexist. Then I converted <b>leaf files first</b> — utility functions and small components — because they had the fewest dependents. Each PR was small and code-reviewed. We kept the <b>existing tests</b> green and ran the app on a dev device daily to catch regressions. For API responses I created shared <b>type definitions</b> aligned with the backend. Anything risky went behind a <b>feature flag</b>. The whole thing took a few months, but we never had to do a 'big bang' release — production stayed stable the whole time.",
     "Use the phrase <b>'incremental migration'</b> — interviewers immediately associate it with safe, mature engineering practice."),

    (0,
     "You mentioned 'owning the release pipeline.' What does that include?",
     "Verifies whether you actually shipped apps or just wrote code others released.",
     "It means I handle the app end-to-end from build to live store. On <b>iOS</b> that’s managing the <b>Apple Developer account</b>, generating <b>signing certificates</b> and <b>provisioning profiles</b>, archiving with <b>Xcode</b>, and uploading via <b>EAS Submit</b> or Transporter. On <b>Android</b> it’s the <b>keystore</b>, the <b>signed AAB</b>, and uploads through the Play Console. I also write the release notes, set up <b>staged rollouts</b> — usually 10% then 50% then 100% — and watch <b>Sentry</b> for crash spikes. If something breaks, I can roll back. I’ve done this independently for <b>5+ apps</b>.",
     "Mention <b>staged rollout</b> specifically — it’s one of those small details that shows you’ve actually published apps."),

    (0,
     "What native modules have you built in Kotlin, and why was a native module needed?",
     "Tests your understanding of when JS isn't enough and how the bridge works.",
     "Three main ones. First, <b>background geolocation</b> — the JS-only libraries couldn’t keep tracking after the app was killed, so I wrote a Kotlin service that uses <b>FusedLocationProviderClient</b> and a foreground notification. Second, <b>push notifications</b> with <b>FCM</b> — to handle data-only messages and deep-link routing into specific screens. Third, <b>biometric auth</b> using Android’s <b>BiometricPrompt</b> for fingerprint and face unlock. In each case the JS side calls a method exposed through React Native’s <b>native module bridge</b>, and the native code does the platform-specific work and returns a promise.",
     "Be ready to draw the <b>JS ↔ bridge ↔ native</b> flow on a whiteboard — interviewers love when you visualize it."),

    (0,
     "How did you process Stripe and PayPal subscriptions with zero reconciliation failures?",
     "Checks if you understand payment flows, webhooks, and idempotency — common pitfalls for juniors.",
     "Three things made it work. First, every payment event came in through a <b>webhook</b>, and I always verified the <b>signature</b> using the Stripe and PayPal SDKs — so spoofed requests were rejected. Second, every charge had an <b>idempotency key</b> tied to the order ID, so if the webhook fired twice we didn’t double-charge or double-credit. Third, I built a <b>reconciliation job</b> that runs nightly and compares our DB records to Stripe’s API — if anything’s off, it alerts. With those three layers, we’ve had <b>zero mismatches</b> in production.",
     "Use the magic word <b>'idempotent'</b> — every backend interviewer is listening for it in payment questions."),

    (0,
     "What is webhook verification, and why is it important?",
     "Beginner-friendly security question — checks fundamentals of trusting external events.",
     "A <b>webhook</b> is just an HTTP request that an external service like Stripe sends to my server when something happens — say a payment succeeds. The problem is, anyone on the internet can hit that URL and pretend to be Stripe. <b>Webhook verification</b> means checking a <b>cryptographic signature</b> in the request header, computed with a <b>secret key</b> only Stripe and I share. If the signature doesn’t match, I reject the request. Without this, an attacker could fake a 'payment succeeded' event and trigger us to ship a free product.",
     "Always tie security questions back to a concrete attack — interviewers want to see you think like an attacker."),

    # ===== SECTION 2: AI LIFE ASSISTANT (7) =====
    (1,
     "Walk me through your AI Life Assistant Super App at a high level.",
     "Tests storytelling — can you explain a complex product in plain language?",
     "Absolutely. It’s a <b>voice-first AI assistant</b> built in React Native. The user can tap a mic button and speak — we capture audio with a <b>custom native module</b>, transcribe it with <b>Whisper</b>, send it to <b>Claude or OpenAI</b> as a streaming chat, and then read the answer back using <b>TTS</b>. The assistant can also call <b>tools</b> like 'create a reminder' or 'fetch my calendar', and the message UI animates at <b>60fps</b> using <b>Reanimated</b>. We also support <b>offline-first SQLite</b> so the user’s history persists, and we use <b>FCM/APNs</b> push so the agent can proactively nudge the user — like 'you said to remind you about the gym, here’s your reminder.'",
     "Start a project answer with <b>what the product does for the user</b>, not the tech stack. Tech comes second."),

    (1,
     "What is streaming LLM chat, and why is it better than waiting for a full response?",
     "Beginner-friendly AI concept that affects perceived performance.",
     "Streaming LLM chat means the model sends back <b>tokens one at a time</b> instead of returning the whole answer at once. So instead of staring at a spinner for 8 seconds, the user starts seeing words appear within half a second — just like how ChatGPT renders. Technically, we keep an open connection — usually <b>Server-Sent Events</b> or a WebSocket — and append each token to the message bubble as it arrives. The total time is similar, but the <b>perceived latency</b> is dramatically lower, and users feel the app is fast and alive.",
     "Use the phrase <b>'perceived latency'</b> — it shows you think about UX, not just network performance."),

    (1,
     "How does Whisper transcription work in your app?",
     "Tests practical AI integration knowledge.",
     "<b>Whisper</b> is OpenAI’s speech-to-text model. In the app, when the user taps the mic, our <b>native audio module</b> records a short audio clip — usually in WAV or M4A — and we send it to the Whisper API as a multipart upload. Whisper returns the transcribed text in a few hundred milliseconds, and we either show it as user input in the chat or feed it directly to the LLM as the next message. For longer recordings we <b>chunk the audio</b> so the user sees partial transcripts coming back, which keeps it feeling responsive.",
     "Mention <b>chunking</b> for long audio — interviewers love when you anticipate the 'what about a 10-minute recording' edge case."),

    (1,
     "What is TTS playback and how did you implement it?",
     "Checks knowledge of audio output APIs and user experience.",
     "<b>TTS</b> stands for <b>text-to-speech</b> — it turns the LLM’s text answer into spoken audio. I used a cloud TTS service (OpenAI TTS or ElevenLabs depending on the project) which returns an MP3 stream. On the React Native side, I pipe that audio into a player — <b>react-native-track-player</b> on top — and start playback as soon as the first chunk arrives. So the user hears the answer almost immediately. I also handle <b>interruption</b> — if the user starts speaking again, I stop playback and switch back to recording, which makes it feel like a real conversation.",
     "Bring up <b>barge-in</b> — letting the user interrupt the AI mid-sentence. It’s a small but advanced UX detail."),

    (1,
     "What is 'tool calling' in the context of AI assistants?",
     "Tests whether you understand modern LLM architecture, not just chat.",
     "Tool calling — sometimes called <b>function calling</b> — is where the LLM doesn’t just reply with text but instead returns a <b>structured request</b> to run a function. For example, I tell Claude 'you have a tool called createReminder(title, time)', and when the user says 'remind me to call mom at 5', the model returns a JSON like <b>{ tool: 'createReminder', args: { title: 'call mom', time: '17:00' } }</b>. My app sees that, runs the actual native code to create the reminder, and sends the result back to the model so it can confirm to the user. It’s how AI assistants <b>take real actions</b> instead of just chatting.",
     "Always close with 'and the result goes back to the model' — many candidates forget the loop and lose points."),

    (1,
     "Why did you build a custom native audio module instead of using an existing library?",
     "Checks judgment about build vs buy.",
     "I tried libraries first — <b>expo-av</b> and <b>react-native-audio-recorder-player</b> — but they had two issues for our use case. First, <b>latency</b>: I needed sub-100ms mic capture for VAD to feel snappy, and the JS bridge added too much overhead. Second, I needed <b>Voice Activity Detection</b> on raw audio frames, which the libraries didn’t expose. So I wrote a thin native module in <b>Swift</b> and <b>Kotlin</b> using <b>AVAudioEngine</b> on iOS and <b>AudioRecord</b> on Android, did the VAD natively, and only sent the resulting transcripts up to JS. It was about <b>2x faster</b> and used less battery.",
     "Always justify a custom native module with a <b>concrete limitation</b> of the library — never 'just because.'"),

    (1,
     "What is VAD — Voice Activity Detection — and how is it useful?",
     "Beginner-friendly question on a buzzword you used.",
     "<b>VAD</b> is a small algorithm that listens to incoming audio and tells you 'someone is speaking now' versus 'silence.' It’s useful because we don’t want to send <b>silence</b> or background noise to Whisper — that wastes API calls and money, and adds latency. With VAD, we automatically start recording when the user begins talking and stop a moment after they finish. So the user doesn’t even need to press a button — they just talk and the assistant responds. It’s what makes voice AI feel natural.",
     "End with the UX win — <b>'no button needed'</b> — because the interviewer remembers the user impact more than the algorithm."),

    # ===== SECTION 3: IoT DASHBOARD (7) =====
    (2,
     "Tell me about your Cloud-Native IoT Analytics Dashboard project.",
     "Lets you frame a real project naturally.",
     "It’s a <b>mobile companion app</b> for a cloud IoT platform. Field engineers use it to monitor live device telemetry — temperature, voltage, signal strength — coming in from thousands of sensors. The data <b>streams over WebSockets</b> in real time into <b>virtualized charts</b>, so even on a low-end Android phone the UI stays smooth. They can <b>acknowledge alerts</b>, and if it’s critical, the system <b>pages the on-call engineer</b> via push notification. When the phone goes offline — like in a basement or rural site — we <b>cache to SQLite</b> and sync back when the network returns. We also use <b>Sentry</b> for crash tracing.",
     "Always mention <b>'low-end device'</b> — interviewers want to know you think about real-world hardware, not just iPhones."),

    (2,
     "Why did you use WebSockets for streaming device telemetry instead of REST polling?",
     "Tests understanding of real-time communication trade-offs.",
     "Polling REST endpoints every second works in theory but it’s wasteful and slow. The phone has to keep opening new HTTPS connections, the server fires up handlers for empty responses, and the user still sees a 1-second lag. <b>WebSockets</b> open <b>one persistent connection</b>, and the server pushes data as it arrives. For IoT, where readings come every couple hundred milliseconds, that’s a much better fit — lower battery use, lower latency, and the server can also push <b>alerts</b> without us asking.",
     "Always mention <b>battery life</b> when comparing WebSockets vs polling — it’s the answer most candidates miss."),

    (2,
     "What are virtualized charts and why did you need them?",
     "Beginner-friendly performance question.",
     "A virtualized chart only <b>renders the data points that are currently visible</b> on the screen, not the whole dataset. So if a device sends 10,000 readings over a day, we don’t draw 10,000 dots — we draw the few hundred visible at the current zoom level. As the user scrolls or zooms, we swap them in and out. Without virtualization, the chart would freeze the UI thread on low-end devices and burn battery. I used <b>react-native-skia</b> and <b>victory-native</b> patterns depending on the chart type.",
     "Mention <b>'UI thread blocking'</b> — it’s the technical term that makes the answer sound senior."),

    (2,
     "How does offline sync with SQLite plus backoff retries actually work?",
     "Tests real-world offline strategy.",
     "When the device is online, every action — like acknowledging an alert — goes straight to the API. But I also write it to a local <b>SQLite</b> table called <b>pending_actions</b>. If the API call fails or the device is offline, the action stays in that table. A background task tries to flush the queue periodically with <b>exponential backoff</b> — first after 2 seconds, then 4, then 8, up to a max. When the network returns, it drains the queue in order. The user’s actions never get lost, even if they spent two hours in a basement.",
     "Always say <b>'queue draining in order'</b> — losing event order is a classic bug interviewers probe for."),

    (2,
     "What’s the difference between FCM and APNs?",
     "Beginner-friendly push notification fundamentals.",
     "Both are <b>push notification services</b>, just for different platforms. <b>FCM — Firebase Cloud Messaging</b> — is Google’s service for Android. <b>APNs — Apple Push Notification service</b> — is Apple’s for iOS. From the server side, you send a payload — title, body, data — to either Google’s or Apple’s servers, and they deliver it to the device. The device <b>token</b> identifies which phone to deliver to, and it’s unique per app install. I usually wrap both behind a single Node.js service so the app team only thinks about 'send notification', not which platform.",
     "Mention the <b>device token</b> explicitly — interviewers want to know you’ve actually wired one up."),

    (2,
     "What is Sentry, and how did it help you reach MTTR under 1 hour?",
     "Checks knowledge of production observability.",
     "<b>Sentry</b> is a service that captures <b>crashes and errors</b> from your app in real time — with the full stack trace, the device model, OS version, and even the user actions that led up to it. So when a crash happens in production, I get a Slack alert within seconds, click into the error, and I already have everything I need to reproduce it. Combined with <b>source maps</b>, I can see the exact line in TypeScript — not minified JS. That’s how we kept <b>MTTR — mean time to recover — under one hour</b>. Without Sentry, we’d be guessing from app store reviews.",
     "MTTR stands for <b>Mean Time To Recover</b> — always say the expansion in your answer in case the interviewer doesn’t know it."),

    (2,
     "What does 'on-call paging' mean for a mobile app?",
     "Beginner-friendly clarification on a domain term.",
     "On-call paging is when the system <b>wakes someone up</b> because a critical issue needs immediate attention. In our IoT dashboard, if a device fires a critical alert — say a sensor reading goes dangerously high — we send a <b>high-priority push notification</b> to the on-call engineer’s phone. On iOS we use <b>critical alerts</b> which bypass silent mode, and on Android we send it as a <b>high-priority FCM message</b> that wakes the device. If they don’t acknowledge within a few minutes, the system pages the next person in the rotation. It’s basically PagerDuty inside our app.",
     "Mention <b>'bypass silent mode'</b> for critical alerts — it shows you understand iOS notification entitlements at a deeper level."),

    # ===== SECTION 4: REAL-TIME COLLAB (7) =====
    (3,
     "Can you explain your Real-Time Collaboration Platform project?",
     "Lets you frame a complex project in your own words.",
     "Sure! It’s a React Native app where multiple users edit the same document together — like Google Docs on mobile. Each user sees the others’ cursors and selections live, with <b>presence avatars</b> and <b>typing indicators</b>. The magic underneath is <b>Yjs</b>, which is a <b>CRDT</b> library that lets edits merge automatically without conflicts — even when users are offline and reconnect later. We also added <b>WebRTC voice notes</b> so they can drop a short voice message, and <b>inline AI</b> where you can highlight a paragraph and ask OpenAI to summarize it, with the response streaming in at 60fps using Reanimated.",
     "When describing collab products, always say <b>'like Google Docs / Figma / Notion'</b> — it instantly anchors the interviewer."),

    (3,
     "What is a CRDT and why did you choose Yjs?",
     "Beginner-friendly version of an advanced concept.",
     "<b>CRDT</b> stands for <b>Conflict-Free Replicated Data Type</b>. The idea is that two users can edit the same document <b>at the same time</b>, even offline, and when they sync, the changes merge automatically — no 'conflict, choose one' popup. It works because every edit carries a unique ID and a logical timestamp, so the algorithm can deterministically order them. <b>Yjs</b> is one of the best implementations — small bundle, mobile-friendly, has React bindings, and works over <b>WebSockets</b> or <b>WebRTC</b>. We chose it because it’s production-proven — Linear and JupyterLab use it — and it just works out of the box.",
     "Use the magic phrase <b>'conflict-free merge'</b> — that’s the value proposition and what the interviewer wants to hear."),

    (3,
     "How do live presence and typing indicators work in a collaborative app?",
     "Beginner-friendly real-time UX question.",
     "Presence is basically <b>heartbeat messages</b>. Each user sends a small WebSocket message every few seconds saying 'I’m here, my cursor is at position X.' The server broadcasts that to other users, who render the avatar and cursor in real time. If a user goes silent for 30 seconds, we mark them as away. Typing indicators are the same idea — on a <b>debounced</b> keystroke, send 'I’m typing'; after 2 seconds of silence, send 'I stopped.' It’s lightweight, and the <b>debounce</b> stops us from spamming the server every keypress.",
     "Mention <b>debounce</b> — it’s the small detail that prevents you from looking like you’d DDoS your own server."),

    (3,
     "What is WebRTC, and how did you use it for voice notes?",
     "Tests understanding of peer-to-peer media.",
     "<b>WebRTC</b> is a browser and mobile API for sending <b>audio, video, and data peer-to-peer</b>, with very low latency. For voice notes I didn’t actually need real-time calling — I just used WebRTC’s <b>audio capture</b> on the device to record, encoded it as Opus, and uploaded it to S3 with a shareable link. But the same API also lets us do <b>live voice calls</b> later by setting up a peer connection through a signaling server. The big win of WebRTC is the audio codec and echo cancellation are battle-tested by Google and built right in.",
     "If asked about scaling WebRTC calls to many users, mention <b>SFU — Selective Forwarding Unit</b> — that shows you’ve thought past 1-on-1 calls."),

    (3,
     "What is 'inline AI' and how did you implement it on document selections?",
     "Beginner-friendly question on a feature you built.",
     "Inline AI is when the user <b>highlights text</b> inside the document and a small toolbar pops up — 'summarize', 'rewrite', 'translate.' When they tap one, we send the selected text plus the action prompt to <b>OpenAI</b> as a streaming request, and the response writes itself into the document <b>token by token</b>. So the user sees the AI typing right where they were working. The trick is using <b>Reanimated</b> to keep the cursor and surrounding text stable during the insert — otherwise it feels jumpy.",
     "Mention <b>'no modal popup, no context switch'</b> — that’s the UX value of inline AI vs a separate chat window."),

    (3,
     "How do streaming OpenAI completions feel different to users compared to regular API calls?",
     "Tests UX intuition.",
     "A regular API call shows a spinner for 5 to 10 seconds and then dumps the whole answer at once — it feels slow and lifeless. A <b>streaming completion</b> starts showing words within 200 to 500 milliseconds — the user sees the AI 'thinking out loud.' Even if total time is the same, the <b>perceived speed</b> is dramatically better. It also gives the user a chance to read along, stop the request early if they see it going off track, and feel more engaged. From an engineering side, it means we have to handle <b>partial responses</b> and the <b>cancel button</b> properly.",
     "Always mention the <b>cancel button</b> — interviewers love when you bring up user agency, not just rendering speed."),

    (3,
     "How did you achieve 60fps animations with Reanimated?",
     "Tests mobile performance knowledge.",
     "<b>Reanimated</b> runs animations on the <b>UI thread</b> using its own native worklet runtime, instead of on the JS thread. That’s the key — the regular React Native Animated API can stutter when the JS thread is busy parsing API responses, but Reanimated bypasses that entirely. So even while we’re streaming tokens from OpenAI and re-rendering the document, the animation stays smooth at <b>60fps</b>. I also avoided animating layout properties — sticking to <b>transform</b> and <b>opacity</b> — and used <b>useSharedValue</b> and <b>useAnimatedStyle</b> properly.",
     "Mention <b>'transform and opacity only'</b> — it’s the universal rule for smooth animations on any platform."),

    # ===== SECTION 5: LANGUAGES, FRONTEND, STATE (5) =====
    (4,
     "What’s the difference between JavaScript and TypeScript, and when would you prefer one over the other?",
     "Beginner-level fundamental, asked in almost every TS interview.",
     "<b>JavaScript</b> is the original language — it’s flexible and runs anywhere, but it has no <b>type checking</b>, so bugs like passing a string where a number was expected only show up at runtime. <b>TypeScript</b> is a superset that adds <b>static types</b> on top, and a compiler that catches those mistakes <b>before</b> the code runs. For a <b>quick prototype or script</b>, plain JavaScript is fine — less ceremony. For anything <b>shipped to production or worked on by a team</b>, I always go TypeScript — the types act as inline documentation, refactoring becomes safe, and the editor autocomplete is much better.",
     "Always link TypeScript to <b>team scale</b> — the bigger the team, the bigger the win."),

    (4,
     "When would you use Redux Toolkit vs Zustand vs React Query?",
     "Tests practical state management judgment.",
     "Each solves a different problem. <b>React Query</b> is for <b>server state</b> — API data, caching, refetching, loading states — that’s 70% of what most apps need, so I start there. <b>Zustand</b> is for <b>simple client state</b> — a small global store with no boilerplate, perfect for UI state like a sidebar toggle or theme. <b>Redux Toolkit</b> I reach for when the app has <b>complex client state</b> with lots of interactions — multi-step wizards, offline queues, undo/redo — where I want the structure of actions, reducers, and middleware. Often I use React Query and Zustand together and skip Redux entirely.",
     "Phrase it as <b>'server state vs client state'</b> — that distinction shows mature thinking."),

    (4,
     "What is Expo and EAS, and why are they useful?",
     "Beginner-friendly tooling question.",
     "<b>Expo</b> is a framework on top of React Native that gives you a smoother developer experience — pre-built native modules, easy access to camera, location, push, and so on, without writing native code. <b>EAS — Expo Application Services</b> — is their cloud build and deployment service. Instead of fighting with Xcode and Android Studio locally, you run <b>eas build</b> and it builds the iOS and Android binaries in the cloud. <b>eas submit</b> then uploads to the App Store and Play Store. For solo developers or small teams, it saves an enormous amount of time.",
     "Mention <b>'no local Xcode required'</b> — that’s the magic moment for anyone who’s ever fought with code signing."),

    (4,
     "What is React Query and what problem does it solve?",
     "Beginner-friendly question about a common library.",
     "<b>React Query</b> — now called <b>TanStack Query</b> — manages <b>server data</b> in your React components. Before it, every developer wrote their own useEffect + useState + loading + error + retry logic for every API call. React Query gives you <b>useQuery</b> and <b>useMutation</b> hooks that handle caching, automatic refetching, stale-while-revalidate, retries on failure, and request deduplication — all out of the box. So instead of 30 lines of boilerplate per API call, you write three. And because it caches by query key, two components asking for the same data don’t fire two requests.",
     "Mention <b>'stale-while-revalidate'</b> — it’s the buzzword that signals you understand caching deeply."),

    (4,
     "What is Gesture Handler and why is it preferred over PanResponder?",
     "Tests mobile gesture knowledge.",
     "<b>react-native-gesture-handler</b> is a library that runs gesture recognition <b>natively</b> on iOS and Android, instead of in the JS thread. The old built-in <b>PanResponder</b> ran in JavaScript, so if the JS thread was busy, your swipe would feel sticky or drop. Gesture Handler doesn’t have that problem — gestures are smooth even under load. It also composes nicely with <b>Reanimated</b>, so you can do things like a swipe-to-dismiss with the position driven by gesture and the spring back driven by Reanimated, all on the UI thread. Smooth 60fps interactions.",
     "Bundle <b>Gesture Handler + Reanimated</b> in your answer — they’re the standard combo and interviewers expect both names."),

    # ===== SECTION 6: NATIVE, PUSH, REAL-TIME (5) =====
    (5,
     "What is a native module in React Native, and when do you need to build one?",
     "Beginner-friendly question about bridging native code.",
     "A <b>native module</b> is platform-specific code — <b>Swift</b> or <b>Objective-C</b> on iOS, <b>Kotlin</b> or <b>Java</b> on Android — that you expose to JavaScript through the React Native bridge. You need one when JavaScript can’t do something the platform requires: <b>background tasks that survive app kill</b>, <b>biometric prompts</b>, <b>Bluetooth</b>, <b>low-latency audio</b>, or any vendor SDK that only ships in native form. I usually try a community library first; if it doesn’t exist or has limitations, I write a thin wrapper that exposes only the methods I need.",
     "Always mention <b>'community library first'</b> — interviewers want to see judgment, not 'I write native code for everything.'"),

    (5,
     "How do push notifications work end-to-end with FCM and APNs?",
     "Tests understanding of the full push flow.",
     "There are four pieces. First, the <b>device registers</b> with FCM or APNs at app launch and gets back a <b>device token</b>. Second, the app sends that token to <b>my backend</b> and saves it against the user. Third, when something happens — like an alert — my backend POSTs a notification payload to FCM or APNs with that token. Fourth, FCM or APNs delivers it to the device, the OS shows the banner, and tapping it deep-links the user into the right screen. If the app is killed, the OS still shows the banner. If it’s in the foreground, my JS code handles it instead.",
     "Always end with <b>'deep link to the right screen'</b> — many candidates forget the in-app routing piece."),

    (5,
     "What are background tasks in mobile apps, and what limitations should you know about?",
     "Practical question on a tricky area.",
     "Background tasks let your app keep doing work after the user leaves it — syncing data, tracking location, finishing an upload. The catch is both OSes are very strict to save battery. On <b>iOS</b>, you only get a <b>few seconds to a few minutes</b> via Background Tasks framework, and the system decides when to wake you. On <b>Android</b> it’s more flexible with <b>WorkManager</b> and <b>foreground services</b>, but you must show a persistent notification or get killed. So the rule is: <b>do the minimum work</b>, persist state to disk, and assume you can be killed at any moment.",
     "Use the phrase <b>'assume you can be killed'</b> — it shows you’ve been burned by it before, which is a sign of experience."),

    (5,
     "How do you implement biometric authentication in React Native?",
     "Beginner-friendly platform feature question.",
     "I use a library like <b>react-native-biometrics</b> or <b>expo-local-authentication</b>. The flow is simple: check whether the device supports biometrics, then call <b>authenticate</b> with a prompt message. On iOS, the OS shows the <b>Face ID or Touch ID</b> system sheet; on Android, it shows the <b>BiometricPrompt</b>. The library returns success or failure. The important detail is I never store the actual biometric — that stays in the <b>Secure Enclave</b> on iOS or the <b>TEE</b> on Android — the OS just tells me yes or no. I usually pair it with a <b>fallback to PIN</b>.",
     "Mention <b>'Secure Enclave'</b> — it’s the magic word that proves you understand the security model."),

    (5,
     "What’s the difference between WebSockets and HTTP polling, and when would you use each?",
     "Real-time fundamentals.",
     "<b>HTTP polling</b> is when the client repeatedly asks the server 'anything new?' every few seconds. It’s simple, works over normal HTTP, but it’s wasteful when nothing has changed, and there’s always a delay equal to the poll interval. <b>WebSockets</b> open a <b>persistent two-way connection</b> — the server pushes data as it happens, with no overhead per message. I use WebSockets for <b>chat, live cursors, IoT telemetry, notifications</b> — anything that needs <b>sub-second freshness</b>. I use polling only when updates are rare and infrastructure for WebSockets is too heavy.",
     "Mention <b>'persistent two-way connection'</b> — that single phrase tells the interviewer you understand the model."),

    # ===== SECTION 7: AI/LLM & BACKEND (5) =====
    (6,
     "What is the Claude API, and how do you call it from a mobile app safely?",
     "Tests AI integration and security awareness.",
     "The <b>Claude API</b> is Anthropic’s REST API for talking to the Claude language model. You send a chat history with a system prompt and a list of messages, and it returns the model’s reply — either as one response or as a <b>streaming SSE</b> connection. From a mobile app, I never call it directly — that would expose my API key to anyone who decompiles the app. Instead, I put a <b>Node.js proxy</b> in the middle: the mobile app authenticates with my backend, the backend holds the Anthropic key and forwards the request to Claude. That way the key stays secret and I can add <b>rate limiting</b> and <b>logging</b>.",
     "The phrase <b>'never put API keys in the mobile bundle'</b> is the #1 security gotcha — always mention it."),

    (6,
     "What is the Vercel AI SDK and how does it help with streaming?",
     "Beginner-friendly question on a popular library.",
     "The <b>Vercel AI SDK</b> is a small library that wraps the messy parts of calling LLMs — Claude, OpenAI, Gemini — behind one consistent interface. It handles <b>streaming</b> over Server-Sent Events out of the box, manages the message format, supports <b>tool calling</b>, and on the React side gives you a <b>useChat</b> hook that auto-renders streaming responses into the UI. Without it, you write a lot of boilerplate around fetch, SSE parsing, and partial JSON. With it, you’re shipping a streaming chat UI in about ten lines. I’ve used it both in Next.js backends and in React Native via a custom hook.",
     "Mention the <b>useChat</b> hook by name — it’s the signature feature interviewers look for."),

    (6,
     "What’s the difference between REST APIs and WebSockets, and when do you use each?",
     "Beginner-friendly backend communication question.",
     "<b>REST</b> is a request-response model — client asks, server replies, connection closes. Great for <b>CRUD</b>: fetch a user, create a post, delete an item. It’s simple, cacheable, and works everywhere. <b>WebSockets</b> are <b>bidirectional and persistent</b> — both sides can send messages whenever, with no per-message overhead. Great for <b>real-time</b>: chat, presence, live dashboards, streaming. In practice I use REST for most operations and <b>add WebSockets for the few real-time features</b>, so I’m not paying the complexity tax everywhere.",
     "Always say <b>'REST for CRUD, WebSockets for real-time'</b> — it’s the one-liner interviewers want to hear."),

    (6,
     "What is JWT and how do you use it for authentication?",
     "Beginner-friendly auth fundamentals.",
     "<b>JWT</b> stands for <b>JSON Web Token</b>. It’s a small, signed string that contains the user’s identity — like <b>{ userId: 123, role: 'admin' }</b> — plus an expiry. When the user logs in, my backend signs a JWT with a secret key and sends it back. The client stores it (in <b>Keychain</b> on iOS or <b>Keystore</b> on Android — not AsyncStorage), and includes it in the <b>Authorization: Bearer</b> header on every API request. My backend verifies the signature, and if valid, trusts the user ID inside. The big win is the backend doesn’t need to look up the session in a database on every request.",
     "Mention <b>Keychain / Keystore</b> instead of AsyncStorage — it’s the security detail interviewers reward."),

    (6,
     "When would you use SQLite vs MongoDB vs Redis?",
     "Beginner-friendly data store question.",
     "Different jobs. <b>SQLite</b> is a tiny, file-based SQL database — I use it <b>on the device</b> for offline caches and local storage. <b>MongoDB</b> is a document database on the server — great when the data shape is flexible or nested, like user profiles, chat messages, or event logs. <b>Redis</b> is an <b>in-memory store</b> — blazing fast, used for <b>caching, session storage, rate limiting, and pub/sub</b>. A typical stack: MongoDB as the source of truth, Redis in front for hot reads and pub/sub, and SQLite on the mobile client for offline.",
     "Always close with <b>'they’re complementary, not competing'</b> — that nuance shows real production experience."),

    # ===== SECTION 8: DEBUGGING, TEAMWORK (4) =====
    (7,
     "Walk me through how you’d debug an API call that’s failing in a React Native app.",
     "Tests systematic debugging instincts.",
     "I always go layer by layer. First, I check the <b>network</b> — is the device online, can it reach the server at all? I use <b>Flipper</b> or <b>Reactotron</b> to watch the actual HTTP request and response. Second, I check the <b>request shape</b> — headers, body, auth token — to make sure I’m sending what the backend expects. Third, I look at the <b>backend logs</b> to see if the request even arrived and what the server saw. Fourth, if the response is correct but the UI is wrong, the bug is in my <b>state or rendering</b>. The mistake juniors make is jumping into code first; I always confirm the request and response first.",
     "Use the phrase <b>'layer by layer'</b> — it signals a calm, systematic engineer."),

    (7,
     "Tell me about a time you handled a production crash. What was your process?",
     "Behavioral question that tests calm under pressure.",
     "Yes — once we shipped a release that crashed on Android 9 devices on startup. <b>Sentry</b> alerted me within minutes with the stack trace, and I saw it was a null pointer in a native library that didn’t support that OS. First thing: I <b>rolled back</b> the Play Store release to the previous version, so new users got the working build. Second: I reproduced the crash locally on an Android 9 emulator. Third: I added a <b>version check</b> guard and shipped a hotfix within a few hours. Final step: I added a regression test and a Sentry alert for that specific error so we’d catch it earlier next time.",
     "The four steps — <b>rollback → reproduce → fix → prevent</b> — make any incident answer sound senior."),

    (7,
     "How do you communicate a technical decision to a non-technical stakeholder?",
     "Soft-skill question — critical even at junior levels.",
     "I lead with the <b>impact on them</b>, not the technology. So instead of saying 'I want to migrate to TypeScript,' I’d say 'we’re hitting recurring production bugs that hurt our users, and there’s a one-time investment we can make that will reduce those by maybe 70% over the next quarter.' Then if they want detail, I go deeper. I also use <b>analogies</b> — for caching I’ll say 'it’s like keeping a snack on your desk so you don’t walk to the kitchen every time.' And I always quantify trade-offs: this costs us two weeks now, saves us a week every month after.",
     "Always lead with <b>user impact and numbers</b>, not technology — that’s how engineers earn trust with PMs and execs."),

    (7,
     "How do you stay up to date with new AI tools and React Native changes?",
     "Behavioral — shows curiosity and learning habits.",
     "Honestly, I treat learning as part of the job. I follow the <b>React Native release notes</b> and the <b>Expo blog</b>, because both ecosystems move fast. For AI, I read the <b>Anthropic and OpenAI changelogs</b> directly — that’s where features like streaming and tool calling are announced. I also use the tools — <b>Claude Code</b>, <b>Cursor</b>, <b>Copilot</b> — every day, and I’ve noticed they each have strengths. Beyond that, I rebuild a small side project every quarter using whatever’s new, because I learn fastest by building, not just reading. I also share what I learn with my team in short demos.",
     "Mention you <b>share with the team</b> — interviewers love candidates who teach, not just hoard knowledge."),

    # ============================================================
    # VOLUME 2 — AI / NATIVE / MOBILE INTEGRATION DEEP DIVE
    # ============================================================

    # ===== SECTION 9: AI STREAMING, CHAT & COST (10) =====
    (8,
     "How does Server-Sent Events (SSE) actually work, and why is it preferred for LLM streaming?",
     "Tests your understanding of the protocol behind modern AI streaming APIs.",
     "<b>SSE</b> is a one-way streaming protocol that runs over plain <b>HTTP</b>. The client opens a normal GET or POST, and the server keeps the connection open and pushes messages as text — each one formatted as <b>data: {json}</b> followed by a blank line. The browser or native fetch parses it line by line. It’s preferred for LLM streaming because it works through every <b>HTTP proxy and load balancer</b> in the wild, supports <b>auto-reconnect</b> with EventSource, and is much simpler than WebSockets for a server-push use case. Both <b>Anthropic</b> and <b>OpenAI</b> use it for their streaming chat endpoints.",
     "Mention that SSE is <b>one-way only</b> — that’s why we fire a fresh request per message instead of using a long-lived bidirectional channel."),

    (8,
     "How do you handle a streaming AI connection that drops mid-response?",
     "Real-world reliability question — mobile networks fail constantly.",
     "First, detect the failure — the stream’s <b>error</b> or <b>close</b> event fires, or no chunks arrive for a timeout window like 10 seconds. Then I keep the <b>tokens we already received</b> and surface them in the bubble with a small <b>retry</b> button. If the user taps retry, I resend the conversation history with the <b>partial assistant message</b> appended and a prompt to continue from where it left off. I never silently drop the message. On flaky cellular, I also do a single auto-retry with backoff before showing the manual retry.",
     "Always say <b>'never silently drop'</b> — losing a chat message is one of the worst UX bugs in AI apps."),

    (8,
     "How would you implement a 'Stop' button while a Claude or OpenAI response is streaming?",
     "Tests fetch and async cancellation knowledge.",
     "I create an <b>AbortController</b> when I start the request and pass its <b>signal</b> into fetch. When the user taps stop, I call <b>controller.abort()</b> — the fetch rejects, the stream closes, and the server stops generating shortly after. I keep whatever tokens already arrived in the chat bubble and swap the 'Stop' button for a 'Regenerate' button. One honest detail: you still get billed for tokens that arrived before the abort, but both Anthropic and OpenAI <b>stop generation server-side</b> on disconnect, so you don’t pay for the full unwritten response.",
     "Mention the <b>billing implication</b> — interviewers notice when candidates think about cost, not just code."),

    (8,
     "What is prompt caching and how does it save you money on the Claude API?",
     "Tests knowledge of a major cost-optimization feature.",
     "<b>Prompt caching</b> lets you mark parts of a prompt — usually the <b>system prompt</b>, <b>RAG documents</b>, or <b>tool definitions</b> — to be cached server-side. On the next request with the same cached prefix, Anthropic charges roughly <b>10% of normal input cost</b> for those tokens and serves them with <b>much lower first-token latency</b>. You enable it by adding <b>cache_control: { type: 'ephemeral' }</b> on the relevant content blocks. It’s a huge win for chat apps with long static system prompts — I’ve seen <b>80%+ cost reduction</b> in production with no UX change.",
     "If asked when not to use it, mention that caching has a <b>small write overhead</b> — it only pays off if the same prefix is reused within minutes."),

    (8,
     "How do you manage the context window when a chat conversation gets very long?",
     "Practical AI engineering question many juniors miss.",
     "Every model has a token limit — Claude is around 200k — and you can’t just keep appending forever, both for the limit and the cost per turn. I track <b>token count</b> as I go using the Anthropic SDK or tiktoken. When I’m around 70% of the window, I start <b>summarizing older turns</b>: I ask the model to compress everything before message N into a short summary, then replace those messages with the summary. The user keeps the feel of long memory while the actual context stays small. For simpler apps I use a <b>sliding window</b> — system prompt plus the last 20 turns.",
     "Use the phrase <b>'rolling summary'</b> or <b>'sliding window'</b> — naming the pattern signals seniority."),

    (8,
     "How do you parse partial JSON when an LLM streams a tool call back to you?",
     "Tests deep streaming knowledge.",
     "Tool calls stream <b>character by character</b>, so for most of the stream you have invalid JSON like <b>{\"city\": \"new yor</b>. Two strategies. The simple one: wait until the streaming event signals <b>tool_use complete</b> (Anthropic fires a <b>content_block_stop</b>), then parse the assembled string with normal JSON.parse. The live one: use a library like <b>partial-json</b> or <b>jsonrepair</b> that handles incomplete JSON — useful when you want to show 'AI is calling getWeather for…' in real time. I default to the complete-then-parse approach unless I need progressive UI.",
     "Mention both approaches — 'wait and parse' vs 'partial parse' — interviewers like trade-off reasoning."),

    (8,
     "What’s the difference between system, user, and assistant messages in a chat API?",
     "Beginner-friendly fundamentals.",
     "Every modern chat API uses three roles. The <b>system message</b> sets the model’s behavior — 'you are a helpful coding assistant' — and the model is trained to weight it strongly. The <b>user message</b> is what the human typed. The <b>assistant message</b> is what the model previously said, included in history so it remembers the conversation. Order matters: typically system first, then alternating user and assistant. One important security rule: <b>never put untrusted user input into the system message</b> — that’s how <b>prompt injection</b> attacks work. The user’s text always goes in the user role.",
     "The <b>prompt injection</b> point at the end always lands — interviewers love when you connect features to security."),

    (8,
     "How do you render markdown smoothly while text is still streaming in?",
     "Tests practical UI performance under streaming.",
     "Two challenges. First, <b>re-render performance</b>: if you re-parse the full markdown on every token, you redraw 50 times per second. I throttle the render to about <b>60ms</b> — visually identical but much cheaper. Second, <b>incomplete syntax</b>: mid-stream you’ll have unclosed bold like <b>**hello wor</b>, which renders ugly. Some libraries handle this gracefully; if not, I run a tiny <b>auto-close pass</b> that closes any open formatting before render. Libraries: <b>react-native-markdown-display</b> on RN, <b>react-markdown</b> on web.",
     "Mention <b>throttling re-renders</b> — it’s the small performance detail that proves you’ve actually built a streaming UI."),

    (8,
     "How would you estimate the cost of an AI chat feature before shipping it?",
     "Tests product and engineering judgment.",
     "I build a small calculator. For each <b>session</b>, estimate average <b>input tokens</b> (system prompt + history) and average <b>output tokens</b> (the reply). Multiply each by the per-million-token price for the chosen model. Then estimate <b>sessions per user per day</b> and <b>active users</b>. So: cost per session × sessions per user × users = daily cost. I always factor in a <b>cache hit ratio</b> if using prompt caching, plus a buffer for <b>retries and tool round-trips</b>. Before launch, I run a small beta to validate the assumptions — real-world token counts are usually higher than estimates.",
     "Always end with <b>'validate with a beta'</b> — it shows you trust real data over spreadsheets."),

    (8,
     "What’s a typical latency budget for a 'feels real-time' AI chat on mobile?",
     "Tests UX intuition around perceived performance.",
     "The number that matters most is <b>TTFT — time to first token</b>. Under <b>500ms</b> feels instant; under <b>1 second</b> is acceptable; over <b>2 seconds</b> feels broken. After the first token, as long as tokens flow at <b>20+ per second</b>, users feel it’s smooth. To hit that budget I keep the system prompt short, enable <b>prompt caching</b>, pick a model in a <b>nearby region</b>, and stream from token one. Spinners that last more than 800ms are where users start tapping the back button.",
     "The phrase <b>'spinners over 800ms lose users'</b> is memorable — interviewers often quote it back."),

    # ===== SECTION 10: WHISPER / VOICE / AUDIO (8) =====
    (9,
     "What audio format should you send to Whisper, and why does it matter?",
     "Beginner-friendly question on a detail that affects latency and cost.",
     "Whisper accepts <b>mp3, m4a, wav, webm, mp4, mpeg, mpga</b>. The trick is choosing one based on your constraint. On cellular, I use <b>m4a (AAC)</b> because the upload is small — a 10-second clip might be 30KB instead of 300KB for WAV. On Wi-Fi or when latency matters most, I use <b>16kHz mono WAV</b> because Whisper internally resamples to that anyway, so no server-side transcoding step. Bad choice: high-sample-rate stereo WAV — it’s 10x bigger than needed and Whisper just downsamples it.",
     "Always mention <b>'Whisper resamples to 16kHz mono internally'</b> — it’s the one detail that justifies your format choice."),

    (9,
     "What sample rate and channel count does Whisper actually want?",
     "Tests detail-level voice AI knowledge.",
     "Whisper internally works at <b>16kHz mono</b>. So if you can encode in 16kHz mono on the device, you skip a transcoding step server-side and trim a few hundred milliseconds. Higher sample rates like 44.1kHz or 48kHz still work — Whisper just downsamples — but you waste bandwidth and a tiny bit of latency. Stereo gets mixed to mono. Voice doesn’t benefit from stereo for transcription, so I always record mono.",
     "Mention <b>'mono saves 50% bandwidth'</b> — it’s the kind of micro-optimization interviewers love."),

    (9,
     "How do you keep Whisper transcription latency low for short utterances?",
     "Tests practical voice AI tuning.",
     "Four levers. First, <b>compress the audio</b> — m4a uploads way faster than WAV. Second, <b>trim silence with VAD</b> before sending, so Whisper isn’t transcribing empty space. Third, <b>chunk long audio</b> — send 5-second windows and stitch transcripts, instead of one big request at the end. Fourth, <b>region selection</b> — use a Whisper endpoint geographically close to the user. With those, I usually hit <b>300–600ms</b> for short phrases. If you need sub-200ms, look at <b>Deepgram</b> or <b>AssemblyAI realtime</b> over WebSocket — those give you partial transcripts live.",
     "Name a <b>specific alternative</b> like Deepgram — it shows you’ve evaluated trade-offs, not just used the default."),

    (9,
     "What’s the difference between Silero VAD and WebRTC VAD?",
     "Beginner-friendly question on tools you mentioned.",
     "<b>WebRTC VAD</b> is the classic — small, written in C, runs everywhere, very fast. But it’s based on signal-processing heuristics, so it produces <b>false positives in noisy environments</b> — wind, traffic, fan hum can all trigger 'speech detected.' <b>Silero VAD</b> is a small neural network — slightly heavier, but dramatically more accurate, especially in real-world noise. For mobile voice AI I default to Silero because false positives mean sending silence to Whisper, which costs money and adds latency. Both run on-device, so no privacy concerns.",
     "Always mention <b>'runs on-device'</b> when comparing VAD — privacy and cost both matter for voice features."),

    (9,
     "What is AVAudioSession on iOS and why does it matter for voice apps?",
     "Tests iOS-specific audio knowledge.",
     "<b>AVAudioSession</b> is iOS’s system-wide audio configuration. It defines how your app’s audio interacts with the rest of the device — does it mix with music, does it activate the speaker, can it record while playing, does it work over Bluetooth. The big decision is the <b>category</b>: <b>playAndRecord</b> for voice apps, <b>playback</b> for video. Then the <b>mode</b>: <b>voiceChat</b> for VOIP-style apps unlocks <b>built-in echo cancellation</b> and routes through the earpiece by default. Wrong category and your app records but can’t play, or vice versa.",
     "Mention <b>'voiceChat unlocks echo cancellation'</b> — that’s the specific detail that proves you’ve shipped a voice app."),

    (9,
     "How do you handle echo cancellation when TTS and mic are both active?",
     "Tests deep voice AI knowledge.",
     "Without echo cancellation, the mic picks up the TTS audio coming out of the speaker and re-sends it to Whisper, creating a <b>feedback loop</b> where the AI hears its own voice. The fix on <b>iOS</b> is using AVAudioSession in <b>mode voiceChat</b> or <b>videoChat</b> — both turn on the built-in AEC. On <b>Android</b>, wrap your AudioRecord with the <b>AcousticEchoCanceler</b> API if the device supports it. WebRTC libraries also bundle their own AEC if you need cross-platform. With AEC on, the user can talk over the AI naturally — no feedback.",
     "End with <b>'user can talk over the AI'</b> — that’s the user-visible benefit and the reason it matters."),

    (9,
     "How do you pick the right TTS voice — what trade-offs matter?",
     "Tests product judgment around AI features.",
     "Three axes: <b>quality, latency, cost</b>. <b>ElevenLabs</b> is the gold standard — voices sound human, supports cloning — but slowest and most expensive. <b>OpenAI TTS</b> is excellent quality, faster, much cheaper, good enough for most chat assistants. <b>System TTS</b> — iOS AVSpeechSynthesizer, Android TextToSpeech — is <b>free, instant, runs offline</b>, but sounds robotic. For an AI assistant where character matters I’d use ElevenLabs or OpenAI; for utility apps reading short messages, system TTS is fine. Always <b>stream audio in chunks</b> so playback starts before the full file is generated.",
     "Mention <b>'system TTS is offline'</b> — it’s the killer feature interviewers forget exists."),

    (9,
     "What’s a typical end-to-end latency budget for a voice AI turn?",
     "Tests holistic understanding of a voice pipeline.",
     "Breaking it down: <b>mic stop to VAD-detected end</b> is 100–300ms; <b>audio upload + Whisper</b> is 300–800ms; <b>LLM time-to-first-token</b> is 300–700ms; <b>TTS first audio chunk</b> is 200–500ms. Sum it up and a great voice AI app feels real-time at <b>1–2 seconds end-to-end</b>. Under 1 second is exceptional. Over 3 seconds, users disengage. Every component matters — shaving 200ms off Whisper by switching to <b>streaming transcription</b> often gives the biggest perceived improvement.",
     "Mention <b>'streaming transcription saves the most'</b> — it’s the lever with the biggest user-visible win."),

    # ===== SECTION 11: TOOL CALLING / AGENTS / SAFETY (5) =====
    (10,
     "How do you define a tool schema for Claude or OpenAI tool calling?",
     "Tests practical agent implementation.",
     "A tool definition is a small <b>JSON Schema</b> with three things: a <b>name</b>, a clear <b>description</b>, and a <b>parameters</b> object describing inputs. Example: name <b>getWeather</b>, description <b>'Get current weather for a city. Returns temperature in Celsius and condition.'</b>, parameters <b>{ city: { type: 'string', description: 'City name in English' } }</b>. The descriptions matter more than people realize — the model uses them to <b>decide which tool to call</b>, so vague descriptions lead to wrong tool selection. Keep the tool count small — under 20 — because too many confuses the model.",
     "The phrase <b>'descriptions matter more than people realize'</b> is something interviewers nod to — most candidates skip it."),

    (10,
     "What happens if the LLM picks the wrong tool or calls it with invalid arguments?",
     "Tests error-handling instincts for agents.",
     "Three failure modes I plan for. <b>Invalid arguments</b> — I validate every tool input with <b>zod</b> server-side; if it fails, I return the validation error as the tool result and the model usually retries with corrected args. <b>Wrong tool entirely</b> — I just run it and return the result; if it’s nonsensical, the model self-corrects on the next turn. <b>Tool execution error</b> — I return the actual error message in the tool_result, not a generic 'failed.' I also <b>log every tool call</b> with inputs and outputs so I can see which prompts cause misbehavior and improve the descriptions.",
     "Mention <b>'log every tool call'</b> — observability for agents is what separates production from demo."),

    (10,
     "How do you build a multi-step agent loop without it running forever?",
     "Tests safety and resource awareness.",
     "An agent loop is: model picks tool → execute → return result → model picks next → repeat. Two safety guards are essential. <b>Max iterations</b> — I cap at 10 or 15 turns; if not done by then, something’s wrong. <b>Max wall time</b> — say 30 or 60 seconds total; anything longer is probably a loop. I also <b>stream intermediate steps to the UI</b> so the user sees 'searching files…', 'reading X…', 'thinking…' — they can hit cancel any time. And I log the full transcript so I can debug runaway loops after the fact.",
     "Mention <b>'stream steps to the UI'</b> — agent UX is mostly about making the wait feel intentional."),

    (10,
     "How would you handle a dangerous tool — like 'delete account' — safely in an AI agent?",
     "Tests safety design.",
     "Never let an AI execute destructive actions silently. The pattern I use: classify tools as <b>read</b>, <b>write</b>, or <b>destructive</b>. Read tools auto-run. Write tools may auto-run or require confirmation depending on impact. <b>Destructive tools always require explicit user confirmation</b> — when the model calls them, I pause the loop, show a confirmation UI with the exact action and arguments, and only proceed on user tap. I also support a <b>dry-run mode</b> where the tool returns 'this is what would happen' without doing it. And I always <b>audit log</b> destructive tool calls with user, time, args.",
     "Use the phrase <b>'explicit confirmation for destructive'</b> — it’s the universal AI safety mantra."),

    (10,
     "What’s the difference between zero-shot, few-shot, and ReAct prompting?",
     "Tests prompting vocabulary.",
     "<b>Zero-shot</b> is just asking the model directly with no examples — 'classify this review as positive or negative.' Works well for modern models on common tasks. <b>Few-shot</b> means including <b>2–5 example input/output pairs</b> in the prompt to teach the format — useful when output needs strict structure. <b>ReAct</b> stands for Reasoning + Acting — the model alternates between <b>thinking out loud</b> and <b>taking actions</b> (tool calls), which improves accuracy on multi-step tasks. Modern Claude and GPT do most things well zero-shot; I reach for few-shot mainly for strict formatting and ReAct for complex agents.",
     "Mention you <b>default to zero-shot and add complexity only when needed</b> — it shows pragmatism over cargo-culting."),

    # ===== SECTION 12: NATIVE MODULES DEEP DIVE (12) =====
    (11,
     "What is the React Native bridge, and why is it being replaced?",
     "Tests fundamental architecture knowledge.",
     "The old <b>bridge</b> is the communication layer between the <b>JS thread</b> and the <b>native UI thread</b>. Every call between them goes through a <b>JSON-serialized, asynchronous, batched queue</b>. It worked but had real downsides: serialization overhead for high-frequency calls (animations, gestures, lots of native module calls), and everything was asynchronous — you couldn’t call a native function and get a value back synchronously. The new architecture replaces this with <b>JSI (JavaScript Interface)</b>, which lets JS and native talk directly in memory.",
     "Always frame it as <b>'old async-batched bridge vs new direct JSI'</b> — that contrast is the one-liner interviewers want."),

    (11,
     "What is JSI and how is it different from the old bridge?",
     "Tests new architecture knowledge.",
     "<b>JSI</b> stands for <b>JavaScript Interface</b>. It’s a C++ layer that lets the JS engine — <b>Hermes</b> or JavaScriptCore — call host (native) functions directly, and vice versa, <b>without JSON serialization</b>. So instead of every native module call going through a queue and being serialized, you can register a C++ function as a JS property and call it like a normal JS function. This unlocks <b>synchronous calls</b>, much lower overhead, and is the foundation for <b>TurboModules</b>, <b>Fabric</b>, and modern <b>Reanimated</b>. You don’t usually write raw JSI code — you use TurboModules or libraries that wrap it.",
     "Mention <b>Hermes</b> by name — it’s the modern JS engine and the standard pairing with JSI."),

    (11,
     "What are TurboModules and what problems do they solve?",
     "Tests new architecture knowledge in depth.",
     "<b>TurboModules</b> are the new architecture’s replacement for native modules, built on top of JSI. They solve three problems. <b>Lazy loading</b> — modules initialize only when first used, so app startup is faster. <b>Type safety via codegen</b> — you describe your module’s interface in a TypeScript-ish spec, and codegen generates both the JS bindings and the native interface, so types are guaranteed to match. <b>Synchronous methods</b> — you can call a native method and get the value back immediately, no Promise needed. Migrating an existing native module to TurboModule is mostly mechanical.",
     "Mention <b>'codegen guarantees JS-native types match'</b> — this is the killer feature that prevents a whole class of bugs."),

    (11,
     "What is Fabric in the React Native new architecture?",
     "Tests rendering architecture knowledge.",
     "<b>Fabric</b> is the new rendering system. It replaces the old <b>Shadow Tree</b> with a JSI-based one that lives in C++, shared between threads. Two big wins. <b>Synchronous layout</b> — components can measure themselves immediately without a bridge round-trip, which fixes a class of jank. <b>Concurrent React features</b> — Suspense, transitions, and the priority scheduler work properly because React can schedule work without fighting the bridge. Combined with TurboModules and JSI, this is what people mean by 'the new architecture' that rolled out around 2023.",
     "Mention <b>'concurrent React features work properly'</b> — it ties Fabric to features web devs already know."),

    (11,
     "How do you expose a Kotlin function to JavaScript as a Promise?",
     "Tests practical native module implementation.",
     "In a class extending <b>ReactContextBaseJavaModule</b>, I write a function annotated with <b>@ReactMethod</b> that takes a <b>Promise</b> parameter at the end. Inside, I do the work and call <b>promise.resolve(value)</b> on success or <b>promise.reject(code, message)</b> on failure. If the work is async, I launch a <b>coroutine</b> with a CoroutineScope and resolve from inside. Example: <b>@ReactMethod fun fetchData(promise: Promise) { scope.launch { try { val r = api.fetch(); promise.resolve(r) } catch (e: Exception) { promise.reject('FETCH_ERR', e) } } }</b>. On the JS side this becomes a regular async function returning a Promise.",
     "Be ready to write this on a whiteboard — interviewers often ask for the actual code, not just the concept."),

    (11,
     "How do you bridge Swift async/await to a JavaScript Promise?",
     "Tests iOS native module knowledge.",
     "An iOS native module method takes <b>RCTPromiseResolveBlock</b> and <b>RCTPromiseRejectBlock</b> as its last two arguments. Inside, I wrap the async call in a <b>Task { ... }</b> block and call resolve or reject when done. Example: <b>@objc func fetchData(_ resolve: @escaping RCTPromiseResolveBlock, rejecter reject: @escaping RCTPromiseRejectBlock) { Task { do { let r = try await api.fetch(); resolve(r) } catch { reject('FETCH_ERR', error.localizedDescription, error) } } }</b>. In the new architecture with TurboModules, you can declare async methods more directly via codegen.",
     "Mention <b>'always call resolve OR reject, never both, never neither'</b> — that’s the gotcha that causes hung Promises."),

    (11,
     "How do you emit events from native code back to JavaScript?",
     "Tests bidirectional communication.",
     "I use <b>DeviceEventEmitter</b> or <b>NativeEventEmitter</b>. On the native side I call something like <b>reactContext.getJSModule(RCTDeviceEventEmitter::class.java).emit('audioChunk', data)</b> on Android, or <b>sendEvent(withName: 'audioChunk', body: data)</b> on iOS. On the JS side, I subscribe with <b>new NativeEventEmitter(MyModule).addListener('audioChunk', handler)</b>. This is how I stream <b>audio frames, location updates, BLE scans</b> — anything that produces a stream of values rather than a single result. Important: always <b>remove the listener</b> in cleanup or you leak memory.",
     "Always mention <b>'remove the listener on cleanup'</b> — forgetting it is the #1 native module memory leak."),

    (11,
     "What is a ViewManager and when would you need one?",
     "Tests native UI component knowledge.",
     "A <b>ViewManager</b> exposes a native UI component to React Native — not just a function but an actual on-screen view. You subclass <b>SimpleViewManager</b> on Android or <b>RCTViewManager</b> on iOS, return the native view, and map <b>JSX props</b> to native properties using annotations like <b>@ReactProp</b>. You need one when wrapping a third-party native widget — a custom <b>map view</b>, a <b>video player</b>, a <b>camera preview</b>, or any vendor SDK that ships a UIView. Examples: <b>react-native-maps</b> and <b>react-native-vision-camera</b> are both ViewManagers under the hood.",
     "Name <b>react-native-maps</b> or <b>vision-camera</b> — interviewers instantly recognize them."),

    (11,
     "What is autolinking in React Native and what does it do for you?",
     "Beginner-friendly question on tooling.",
     "<b>Autolinking</b> is the system that automatically wires up native dependencies after you <b>npm install</b> a React Native library. Before autolinking — pre 0.60 — you had to manually edit <b>Podfile</b> on iOS and <b>settings.gradle</b> on Android, run <b>react-native link</b>, and pray. Now, when you install a library, React Native scans <b>node_modules</b> for <b>react-native.config.js</b> or known patterns and adds the native code to the build automatically. You just do <b>cd ios &amp;&amp; pod install</b> on iOS and rebuild. It saves hours of setup and is the reason RN went from painful to pleasant for adding libraries.",
     "Mention <b>'pod install still needed on iOS'</b> — it’s the one manual step people forget."),

    (11,
     "How would you debug a native module that’s crashing on Android?",
     "Tests practical debugging skills.",
     "Step one: <b>adb logcat | grep -E 'AndroidRuntime|FATAL'</b> — the crash trace shows up there immediately with exception and stack. If it’s a Kotlin/Java exception, the line number points right at the bug. For native (C++) crashes with no symbols, I <b>symbolicate</b> using the build’s mapping file. For deeper debugging I attach the <b>Android Studio debugger</b> to the running app, set breakpoints in the native module, and step through. In production, <b>Sentry</b> or <b>Crashlytics</b> capture the same trace with source maps. The mistake juniors make is reading only the JS error — most native crashes don’t show up in the JS console.",
     "Mention <b>'most native crashes don’t show in the JS console'</b> — it’s the most common reason juniors get stuck."),

    (11,
     "How do you avoid memory leaks in a native module?",
     "Tests real-world native development care.",
     "Three usual suspects. <b>Event listeners</b> — every NativeEventEmitter listener on the JS side and every native callback registration must be paired with a cleanup, otherwise they hold references forever. <b>Holding ReactContext or Activity references</b> in long-lived objects — they become invalid when the activity recreates and prevent garbage collection. <b>Bitmaps and large native buffers</b> on Android need explicit recycling or try-with-resources. I profile with <b>Android Studio Profiler</b> or <b>Xcode Instruments</b> — they highlight leaks visually. A leak of 200KB per session adds up fast across a million users.",
     "Mention <b>'200KB per session adds up fast'</b> — concrete numbers make abstract leak talk land."),

    (11,
     "How do you keep a native module thread-safe?",
     "Tests concurrency awareness.",
     "First, know which thread you’re on. <b>@ReactMethod</b> on Android runs on a <b>native modules thread pool</b> — not the UI thread. So if I need to touch the UI, I wrap it in <b>UiThreadUtil.runOnUiThread { ... }</b>. On iOS, similar — use <b>DispatchQueue.main.async</b>. For shared mutable state, I use <b>synchronized</b> blocks or a <b>Mutex</b> in Kotlin, and <b>DispatchQueue</b> or <b>NSLock</b> on Swift. And the Promise rule: <b>resolve or reject exactly once</b>, from any thread. Calling it twice or never causes hung Promises that are a nightmare to debug.",
     "Mention <b>'resolve exactly once'</b> — it’s the specific concurrency bug that hits everyone eventually."),

    # ===== SECTION 13: MOBILE PLATFORM INTEGRATION (10) =====
    (12,
     "How do you set up FCM end-to-end for a React Native app?",
     "Tests practical push setup knowledge.",
     "Roughly six steps. <b>Create a Firebase project</b>. Add the Android app, download <b>google-services.json</b>, drop into <b>android/app/</b>. Add the iOS app, download <b>GoogleService-Info.plist</b>, drag into Xcode, and upload your <b>APNs auth key (p8)</b> to Firebase. Install <b>@react-native-firebase/app</b> and <b>@react-native-firebase/messaging</b>. In code: request notification permission, get the <b>FCM token</b> with messaging().getToken(), send it to my backend. Set up handlers for <b>foreground</b>, <b>background</b>, and <b>killed</b> states — they’re different APIs. Test with a curl to Firebase’s send endpoint before integrating fully.",
     "Mention testing with a <b>curl call to Firebase</b> before backend work — it isolates whether the issue is mobile or server."),

    (12,
     "What’s the difference between APNs certificates and auth keys, and which should you use?",
     "Tests iOS push knowledge.",
     "Both let your server send push notifications to iOS devices. <b>Certificates</b> (the older approach) expire <b>every year</b>, are tied to a single app, and are different for dev and prod — so you rotate them annually and manage multiple files. <b>Auth keys (p8 files)</b> <b>never expire</b>, work for <b>all apps under your team</b>, and handle both dev and prod. <b>Always use auth keys</b> in modern projects — less maintenance, fewer outages from expired certs. I’ve seen production push fail at 2am because someone forgot to renew a cert.",
     "The <b>'2am production outage'</b> story is the kind of war-story detail interviewers remember."),

    (12,
     "What’s the difference between URL schemes, Universal Links, and App Links?",
     "Tests deep linking knowledge.",
     "All three let an external trigger open your app to a specific screen. <b>URL schemes</b> like <b>myapp://order/123</b> are simple but <b>unverified</b> — any app can register the same scheme and hijack it. <b>Universal Links (iOS)</b> are real <b>https URLs</b> verified via an <b>apple-app-site-association</b> file hosted on your domain. <b>App Links (Android)</b> are the equivalent with <b>assetlinks.json</b>. The big win of Universal/App Links: they open your app if installed, otherwise fall back to your website seamlessly. I always go with Universal/App Links in production.",
     "Mention <b>'fall back to website if not installed'</b> — it’s the killer UX feature URL schemes can’t match."),

    (12,
     "How do you request and check runtime permissions on iOS and Android?",
     "Beginner-friendly platform basics.",
     "On <b>iOS</b>, you declare every permission in <b>Info.plist</b> with a <b>usage string</b> explaining why — without that string, the app crashes when requesting. The OS shows the popup the first time you ask. On <b>Android</b>, declare in <b>AndroidManifest.xml</b>; for 'dangerous' permissions (camera, location, mic, contacts), you also request at runtime. I use <b>react-native-permissions</b> for a unified API. Always <b>check before requesting</b> — if it’s already granted, skip the popup. And handle the <b>'denied permanently'</b> case by linking to system settings.",
     "Mention <b>'linking to settings on permanent denial'</b> — it’s the UX path most apps miss."),

    (12,
     "How do In-App Purchases work and what’s the difference between StoreKit and Play Billing?",
     "Tests monetization fundamentals.",
     "Apps selling digital goods <b>must</b> use Apple’s <b>StoreKit</b> on iOS and Google’s <b>Play Billing</b> on Android — both take a 15–30% cut. Each supports <b>consumables</b> (coins), <b>non-consumables</b> (unlock a feature), and <b>subscriptions</b>. I use <b>react-native-iap</b> to bridge both behind one API. Critical: always <b>validate the receipt server-side</b> against Apple/Google’s servers — client-only validation can be faked, leading to free unlocked content. You <b>cannot use Stripe or PayPal</b> for digital goods — only for physical goods, real-world services, or B2B.",
     "Always mention <b>'server-side receipt validation'</b> — this is the IAP-specific security must."),

    (12,
     "How do you handle the app foreground / background transitions?",
     "Tests lifecycle awareness.",
     "React Native exposes <b>AppState</b> with three states: <b>active</b>, <b>background</b>, <b>inactive</b> (a brief transitional state on iOS). I subscribe with <b>AppState.addEventListener('change', handler)</b>. On <b>background</b>, I <b>save state to disk</b>, close streaming connections to save battery, pause timers. On <b>active</b>, I reconnect, refresh stale data, check for missed notifications. On iOS the app <b>can be killed any time</b> in background, so I never assume state persists in memory. I also use this hook to track <b>session length</b> for analytics.",
     "Mention <b>'iOS can kill the app any time'</b> — it’s the assumption juniors get wrong most often."),

    (12,
     "How do you store a JWT or refresh token securely on a mobile device?",
     "Tests security awareness.",
     "Never put it in <b>AsyncStorage</b> — that’s plain text on Android and easy to read on a rooted device. Use the platform’s secure store: <b>Keychain on iOS</b> and <b>EncryptedSharedPreferences</b> or the <b>Keystore</b> on Android. The library I use is <b>react-native-keychain</b>, which abstracts both. For extra paranoia I store the <b>refresh token</b> in the secure store and keep the short-lived <b>access token</b> only in memory — that way even a process dump doesn’t expose long-term credentials. Also, set the keychain accessibility to <b>after-first-unlock</b> so it’s not accessible until the user unlocks the device.",
     "Mention <b>'after-first-unlock'</b> — that’s the keychain detail that signals real security awareness."),

    (12,
     "What is SafeAreaView and why do you need it?",
     "Beginner-friendly UI question.",
     "Modern phones have <b>non-rectangular display areas</b> — the iPhone notch, the home indicator at the bottom, status bars, Android cutouts. If you render content edge-to-edge without thinking, your buttons sit under the notch and your text gets clipped. <b>SafeAreaView</b> wraps content so it stays inside the visible, untouchable area. The current best library is <b>react-native-safe-area-context</b>, which provides hooks like <b>useSafeAreaInsets()</b> giving you exact pixel insets for each side. The old built-in SafeAreaView is iOS-only and deprecated.",
     "Mention <b>'old SafeAreaView is iOS-only'</b> — many candidates don’t realize they should use the modern library."),

    (12,
     "How do you handle the iPhone notch, Dynamic Island, and Android cutouts?",
     "Tests detail-level UI awareness.",
     "Same toolkit: <b>react-native-safe-area-context</b> works on iOS and Android — it gives the inset values for each edge. The <b>Dynamic Island</b> sits inside the iOS top safe area, so SafeAreaView protects you automatically — but I avoid putting critical UI in the top 60pt anyway because system overlays (recording, calls) can cover it. For Android cutouts, declare <b>layoutInDisplayCutoutMode</b> in styles.xml and let SafeAreaView handle the rest. Always <b>test on real devices</b> with and without notches — emulators sometimes lie.",
     "Mention <b>'always test on real notch devices'</b> — many candidates only check the simulator and miss visual bugs."),

    (12,
     "How do you set up a custom splash screen and app icon for both platforms?",
     "Beginner-friendly question on shipping basics.",
     "For <b>icons</b>, I use a generator like <b>@bam.tech/react-native-make</b> or Expo’s image-utils — feed one 1024×1024 PNG, it spits out every size each platform needs. On <b>iOS</b>, the icons go in the Asset Catalog; on <b>Android</b>, into <b>res/mipmap-*</b> folders. For <b>splash screens</b> I use <b>react-native-bootsplash</b> (or expo-splash-screen if Expo). It generates the native assets, configures iOS <b>LaunchScreen.storyboard</b> and Android <b>splash theme + drawable</b>, and hides the splash from JS when the app is ready. Critical: don’t show a long fake splash to hide a slow startup — fix the startup instead.",
     "Mention <b>'fix slow startup, don’t hide it'</b> — it’s the perspective that separates engineers from icon-pushers."),

    # ===== SECTION 14: REAL-TIME AI ON MOBILE / ON-DEVICE (5) =====
    (13,
     "How do you reconnect a WebSocket streaming AI session after a network drop?",
     "Tests resilience design.",
     "Three pieces. First, <b>detect the drop</b> — both onClose and onError fire, plus a heartbeat ping to detect dead connections that haven’t closed. Second, <b>reconnect with exponential backoff</b> — wait 1s, 2s, 4s, up to a cap of 30s, with a bit of <b>jitter</b> to avoid thundering herd. Third, <b>resume meaningfully</b> — the server holds a session ID, and on reconnect the client sends 'resume from message N' so the AI continues instead of restarting. During reconnect, show a <b>discreet 'reconnecting…' banner</b>, not a blocking modal — users hate modals.",
     "Mention <b>'jitter to avoid thundering herd'</b> — it’s the small detail that shows distributed-systems awareness."),

    (13,
     "What happens to a streaming AI request when the user backgrounds the app?",
     "Tests deep lifecycle knowledge.",
     "On <b>iOS</b>, the app typically gets about <b>30 seconds</b> before being suspended; long network requests usually fail mid-stream. On <b>Android</b> it varies but is similar without a foreground service. Strategy: when the app backgrounds, I <b>complete the request on the server</b> (so the AI finishes its reply) and store the result. When the app foregrounds, I <b>fetch the completed message</b> and render it. Alternative: send a <b>silent push notification</b> when the response is ready, so the user knows to come back. Never assume a streaming connection survives backgrounding.",
     "End with <b>'never assume the stream survives backgrounding'</b> — it’s the rule that prevents nasty production bugs."),

    (13,
     "What are the battery implications of long-running AI sessions on mobile?",
     "Tests resource awareness.",
     "Three big drains in a voice AI app: <b>persistent WebSocket</b>, <b>continuous mic recording</b>, and <b>screen on</b>. Mitigations: use <b>VAD</b> to record only when there’s speech, use a <b>low-power codec</b> like Opus, <b>close the WS</b> when idle and reopen on next interaction, batch network calls to wake the radio less often, and let the screen dim if the user isn’t interacting. I profile battery with <b>Android Battery Historian</b> and <b>Xcode Energy Impact</b> — both show which subsystem is eating power. A poorly tuned voice AI app can drain a phone in 2 hours; a well-tuned one lasts 6–8.",
     "Mention the <b>2-hour vs 8-hour</b> contrast — concrete numbers make the case memorable."),

    (13,
     "What is on-device AI, and which frameworks would you use — Core ML, TFLite, or ONNX?",
     "Tests modern AI deployment knowledge.",
     "<b>On-device AI</b> means running the model directly on the phone, with no cloud call. Three main frameworks. <b>Core ML</b> on iOS — Apple’s native framework, ships <b>.mlmodel</b> files, accelerated by the Neural Engine. <b>TFLite</b> — Google’s, cross-platform, optimized for mobile, supports <b>GPU and NNAPI</b> acceleration on Android. <b>ONNX Runtime</b> — cross-platform, supports models converted from PyTorch, TensorFlow, and many others. In React Native I’d use <b>react-native-fast-tflite</b> for vision tasks, or <b>react-native-vision-camera</b> for real-time camera + ML.",
     "Name <b>react-native-fast-tflite</b> by name — it’s the modern RN-friendly choice and interviewers notice when you know specific libraries."),

    (13,
     "When should you pick on-device AI vs cloud AI?",
     "Tests product-engineering judgment.",
     "On-device wins when you need <b>privacy</b> (data never leaves the phone), <b>offline capability</b>, <b>no per-request cost</b>, or <b>ultra-low latency</b>. Cloud wins when you need <b>large, state-of-the-art models</b> (LLMs are too big for phones), <b>centralized updates</b>, or <b>compute-heavy</b> tasks. Most production apps end up <b>hybrid</b>: on-device for small classifiers, wake words, image filters, vision tasks; cloud for large LLMs and anything that needs broader knowledge. A useful rule: if the model is over <b>2GB</b> compressed, it probably belongs in the cloud — most phones can’t load it without killing other apps.",
     "Mention <b>'hybrid is the default'</b> — pure on-device or pure cloud is rare in production."),
]


# ============================================================
#                      PDF BUILDING
# ============================================================

styles = getSampleStyleSheet()

class CoverBackground(Flowable):
    """A decorative full-page colored band for the cover."""
    def __init__(self, width, height):
        Flowable.__init__(self)
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        c.setFillColor(PRIMARY)
        c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        c.setFillColor(ACCENT)
        c.rect(0, self.height * 0.62, self.width, 4 * mm, fill=1, stroke=0)
        c.setFillColor(PURPLE)
        c.rect(0, self.height * 0.60, self.width, 1.5 * mm, fill=1, stroke=0)


# ---------- Paragraph styles ----------
style_cover_title = ParagraphStyle(
    "CoverTitle", parent=styles["Title"], fontName="Helvetica-Bold",
    fontSize=32, leading=38, alignment=TA_CENTER, textColor=white, spaceAfter=12)

style_cover_sub = ParagraphStyle(
    "CoverSub", parent=styles["Normal"], fontName="Helvetica",
    fontSize=14, leading=20, alignment=TA_CENTER, textColor=white, spaceAfter=4)

style_cover_meta = ParagraphStyle(
    "CoverMeta", parent=styles["Normal"], fontName="Helvetica-Oblique",
    fontSize=11, leading=16, alignment=TA_CENTER, textColor=HexColor("#E0E7FF"))

style_section_title = ParagraphStyle(
    "SectionTitle", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=20, leading=26, textColor=white, alignment=TA_LEFT, spaceAfter=4)

style_section_blurb = ParagraphStyle(
    "SectionBlurb", parent=styles["Normal"], fontName="Helvetica",
    fontSize=11, leading=15, textColor=GRAY_DARK, alignment=TA_LEFT,
    spaceBefore=10, spaceAfter=10)

style_qnumber = ParagraphStyle(
    "QNumber", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=10, leading=12, textColor=white)

style_question = ParagraphStyle(
    "Question", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=13, leading=17, textColor=GRAY_DARK, spaceBefore=2, spaceAfter=8)

style_label = ParagraphStyle(
    "Label", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=10.5, leading=14, textColor=PRIMARY, spaceBefore=8, spaceAfter=3)

style_body = ParagraphStyle(
    "Body", parent=styles["Normal"], fontName="Helvetica",
    fontSize=10.5, leading=15.5, textColor=GRAY_DARK, alignment=TA_JUSTIFY, spaceAfter=4)

style_tip = ParagraphStyle(
    "Tip", parent=styles["Normal"], fontName="Helvetica-Oblique",
    fontSize=10.5, leading=15, textColor=GRAY_DARK, alignment=TA_LEFT)

style_toc_section = ParagraphStyle(
    "TOCSection", parent=styles["Normal"], fontName="Helvetica-Bold",
    fontSize=12, leading=16, textColor=PRIMARY, spaceBefore=10, spaceAfter=4)

style_toc_item = ParagraphStyle(
    "TOCItem", parent=styles["Normal"], fontName="Helvetica",
    fontSize=10, leading=14, textColor=GRAY_DARK, leftIndent=12, spaceAfter=1)

style_h1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontName="Helvetica-Bold",
    fontSize=24, leading=30, textColor=PRIMARY, spaceAfter=12)


# ---------- Page templates ----------

def on_cover_page(canvas_obj, doc):
    """Draws cover background."""
    canvas_obj.saveState()
    width, height = A4
    canvas_obj.setFillColor(PRIMARY)
    canvas_obj.rect(0, 0, width, height, fill=1, stroke=0)
    # gradient-ish stripes
    canvas_obj.setFillColor(ACCENT)
    canvas_obj.rect(0, height * 0.62, width, 6 * mm, fill=1, stroke=0)
    canvas_obj.setFillColor(PURPLE)
    canvas_obj.rect(0, height * 0.60, width, 2 * mm, fill=1, stroke=0)
    canvas_obj.setFillColor(HexColor("#312E81"))
    canvas_obj.rect(0, 0, width, 30 * mm, fill=1, stroke=0)
    # footer brand line
    canvas_obj.setFillColor(white)
    canvas_obj.setFont("Helvetica-Oblique", 9)
    canvas_obj.drawCentredString(width / 2, 12 * mm,
        "Curated for Mohammed Rinshad M I — React Native + Full-Stack Interview Prep")
    canvas_obj.restoreState()


def on_content_page(canvas_obj, doc):
    """Header / footer for all non-cover pages."""
    canvas_obj.saveState()
    width, height = A4
    # top thin band
    canvas_obj.setFillColor(PRIMARY)
    canvas_obj.rect(0, height - 8 * mm, width, 8 * mm, fill=1, stroke=0)
    canvas_obj.setFillColor(white)
    canvas_obj.setFont("Helvetica-Bold", 8.5)
    canvas_obj.drawString(15 * mm, height - 5.5 * mm,
        "RINSHAD · React Native + Full-Stack Interview Prep")
    canvas_obj.drawRightString(width - 15 * mm, height - 5.5 * mm,
        "100 Q&A · Vol. 1 + Vol. 2")
    # bottom page number
    canvas_obj.setFillColor(GRAY)
    canvas_obj.setFont("Helvetica", 9)
    canvas_obj.drawCentredString(width / 2, 10 * mm, f"Page {doc.page}")
    # bottom thin line
    canvas_obj.setStrokeColor(GRAY_LIGHT)
    canvas_obj.setLineWidth(0.4)
    canvas_obj.line(15 * mm, 14 * mm, width - 15 * mm, 14 * mm)
    canvas_obj.restoreState()


# ---------- Custom flowables ----------

class SectionBanner(Flowable):
    """Colored banner with section title + icon."""
    def __init__(self, title, color, icon, width=170 * mm, height=22 * mm):
        Flowable.__init__(self)
        self.title = title
        self.color = color
        self.icon = icon
        self.width = width
        self.height = height

    def wrap(self, *args):
        return self.width, self.height

    def draw(self):
        c = self.canv
        c.setFillColor(self.color)
        c.roundRect(0, 0, self.width, self.height, 4, fill=1, stroke=0)
        # icon circle
        c.setFillColor(white)
        c.circle(13 * mm, self.height / 2, 6.5 * mm, fill=1, stroke=0)
        c.setFillColor(self.color)
        # shrink font for double-digit section numbers so they fit in the circle
        icon_str = str(self.icon)
        icon_font_size = 14 if len(icon_str) == 1 else 12
        c.setFont("Helvetica-Bold", icon_font_size)
        # vertical offset adjusted with font size so the digit stays centered
        c.drawCentredString(13 * mm, self.height / 2 - icon_font_size / 3.2, icon_str)
        # title text
        c.setFillColor(white)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(26 * mm, self.height / 2 - 4, self.title)


class QuestionBadge(Flowable):
    """A pill with the question number. Auto-sizes for 1, 2, or 3 digit numbers."""
    def __init__(self, number, color, width=170 * mm, height=8 * mm):
        Flowable.__init__(self)
        self.number = number
        self.color = color
        self.width = width
        self.height = height

    def wrap(self, *args):
        return self.width, self.height

    def draw(self):
        c = self.canv
        # auto-size the pill width so "QUESTION #100" fits without clipping
        label = f"QUESTION #{self.number}"
        font_size = 9.5
        c.setFont("Helvetica-Bold", font_size)
        text_width = c.stringWidth(label, "Helvetica-Bold", font_size)
        pad = 4 * mm
        pill_width = max(28 * mm, text_width + 2 * pad)
        # left badge
        c.setFillColor(self.color)
        c.roundRect(0, 0, pill_width, self.height, 2, fill=1, stroke=0)
        c.setFillColor(white)
        c.drawCentredString(pill_width / 2, self.height / 2 - 3, label)
        # thin divider line continuing
        c.setStrokeColor(self.color)
        c.setLineWidth(1.4)
        c.line(pill_width + 2, self.height / 2, self.width, self.height / 2)


# ---------- Build flowables ----------

doc = SimpleDocTemplate(
    OUT_PATH,
    pagesize=A4,
    leftMargin=18 * mm,
    rightMargin=18 * mm,
    topMargin=18 * mm,
    bottomMargin=20 * mm,
    title="Rinshad — React Native + Full-Stack Interview Prep",
    author="Mohammed Rinshad M I",
    subject="50 Beginner Interview Q&A",
)

story = []

# ============== COVER PAGE ==============
story.append(Spacer(1, 60 * mm))
story.append(Paragraph("React Native + Full-Stack", style_cover_title))
story.append(Paragraph("Interview Preparation", style_cover_title))
story.append(Spacer(1, 6 * mm))
story.append(Paragraph("100 Questions &amp; Answers — Beginner Friendly", style_cover_sub))
story.append(Paragraph("Vol. 1: Resume &amp; Projects · Vol. 2: AI / Native / Mobile Deep Dive", style_cover_sub))
story.append(Spacer(1, 30 * mm))
story.append(Paragraph("Prepared for", style_cover_meta))
story.append(Spacer(1, 4))
story.append(Paragraph("<b>Mohammed Rinshad M I</b>", ParagraphStyle(
    "name", parent=style_cover_sub, fontSize=18, textColor=white, spaceAfter=2)))
story.append(Paragraph("AI-Augmented React Native Engineer", style_cover_meta))
story.append(Paragraph("Palakkad, Kerala · 2026", style_cover_meta))
story.append(PageBreak())


# ============== TABLE OF CONTENTS ==============
story.append(Paragraph("Table of Contents", style_h1))
story.append(Spacer(1, 4))

# numbering through QA
q_index_by_section = {i: [] for i in range(len(SECTIONS))}
for q_idx, item in enumerate(QA, start=1):
    sec_idx = item[0]
    q_index_by_section[sec_idx].append((q_idx, item[1]))

for sec_idx, sec in enumerate(SECTIONS):
    story.append(Paragraph(sec["title"], style_toc_section))
    for qn, qtxt in q_index_by_section[sec_idx]:
        # shorten really long questions
        short = qtxt if len(qtxt) <= 95 else qtxt[:92] + "..."
        story.append(Paragraph(f"Q{qn}. {short}", style_toc_item))

story.append(PageBreak())


# ============== INTRO / HOW TO USE ==============
story.append(Paragraph("How to Use This Guide", style_h1))
intro_text = (
    "This guide contains <b>100 beginner-level interview questions</b> in two volumes. "
    "<b>Volume 1 (Q1–Q50)</b> is curated from your resume — your role at <b>Infinite Open Source Solution LLP</b>, "
    "your three flagship projects, and your declared stack. <b>Volume 2 (Q51–Q100)</b> is a focused deep dive into "
    "<b>AI integration, native modules, and mobile platform integration</b> — the areas you work in every day. "
    "Each question follows the same structure: the question, <b>why interviewers ask it</b>, "
    "a <b>strong candidate answer</b> written in natural conversational language, and a <b>pro tip</b> to use in the room."
)
story.append(Paragraph(intro_text, style_body))
story.append(Spacer(1, 8))
story.append(Paragraph(
    "Read aloud, not silently. The goal isn't memorization — it's <b>making the answer feel like yours</b>. "
    "Replace examples with your own where you have stronger stories. Bold phrases in the answers are the keywords "
    "interviewers anchor to — say them clearly.",
    style_body))
story.append(Spacer(1, 12))

# Legend
legend_data = [
    [Paragraph("<b>💬 Interview Question</b>", style_body),
     Paragraph("The exact question you'll likely hear.", style_body)],
    [Paragraph("<b>🎯 Why Interviewers Ask</b>", style_body),
     Paragraph("What the interviewer is really probing for.", style_body)],
    [Paragraph("<b>✅ Strong Candidate Answer</b>", style_body),
     Paragraph("Natural, confident response — speak it like a conversation.", style_body)],
    [Paragraph("<b>⭐ Pro Tip</b>", style_body),
     Paragraph("One practical move that lifts an average answer to a strong one.", style_body)],
]
legend = Table(legend_data, colWidths=[55 * mm, 110 * mm])
legend.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, -1), BG_SOFT),
    ("BOX", (0, 0), (-1, -1), 0.5, GRAY_LIGHT),
    ("INNERGRID", (0, 0), (-1, -1), 0.3, GRAY_LIGHT),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ("TOPPADDING", (0, 0), (-1, -1), 6),
    ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
]))
story.append(legend)
story.append(PageBreak())


# ============== SECTIONS + QUESTIONS ==============
question_counter = 0
for sec_idx, sec in enumerate(SECTIONS):
    # Section banner
    story.append(SectionBanner(sec["title"], sec["color"], sec["icon"]))
    story.append(Spacer(1, 4))
    story.append(Paragraph(sec["blurb"], style_section_blurb))
    story.append(Spacer(1, 4))

    for qa in QA:
        if qa[0] != sec_idx:
            continue
        question_counter += 1
        _, question, why, answer, tip = qa

        block = []
        block.append(QuestionBadge(question_counter, sec["color"]))
        block.append(Spacer(1, 4))
        block.append(Paragraph(f"💬 <b>Q{question_counter}.</b> {question}", style_question))

        block.append(Paragraph("🎯 Why Interviewers Ask This", style_label))
        block.append(Paragraph(why, style_body))

        block.append(Paragraph("✅ Strong Candidate Answer", style_label))
        block.append(Paragraph(answer, style_body))

        block.append(Paragraph("⭐ Pro Tip", style_label))
        block.append(Paragraph(tip, style_tip))

        block.append(Spacer(1, 10))
        # divider
        block.append(Table([[""]], colWidths=[170 * mm], rowHeights=[0.6],
                           style=TableStyle([
                               ("LINEABOVE", (0, 0), (-1, -1), 0.6, GRAY_LIGHT),
                           ])))
        block.append(Spacer(1, 8))

        story.append(KeepTogether(block))

    # page break between sections
    story.append(PageBreak())


# ============== CLOSING PAGE ==============
story.append(Spacer(1, 50 * mm))
story.append(Paragraph("Good luck, Rinshad.", ParagraphStyle(
    "ClosingTitle", parent=style_h1, alignment=TA_CENTER, fontSize=26)))
story.append(Spacer(1, 6))
story.append(Paragraph(
    "<i>Confidence comes from preparation. You've already done the work — "
    "this guide just helps you say it out loud.</i>",
    ParagraphStyle("ClosingBody", parent=style_body,
                   alignment=TA_CENTER, fontSize=12, textColor=GRAY)))
story.append(Spacer(1, 20))
story.append(Paragraph(
    "— Prepared with care, 2026",
    ParagraphStyle("Sig", parent=style_body, alignment=TA_CENTER,
                   fontSize=10, textColor=GRAY)))


# ---------- Build with two page templates ----------
from reportlab.platypus.doctemplate import PageTemplate, BaseDocTemplate
from reportlab.platypus.frames import Frame


class TwoTemplateDoc(BaseDocTemplate):
    def __init__(self, filename, **kw):
        BaseDocTemplate.__init__(self, filename, **kw)
        page_w, page_h = A4
        cover_frame = Frame(0, 0, page_w, page_h, id="cover",
                            leftPadding=18 * mm, rightPadding=18 * mm,
                            topPadding=20 * mm, bottomPadding=20 * mm)
        content_frame = Frame(
            18 * mm, 18 * mm, page_w - 36 * mm, page_h - 36 * mm,
            id="content", leftPadding=0, rightPadding=0,
            topPadding=4, bottomPadding=4)
        self.addPageTemplates([
            PageTemplate(id="Cover", frames=[cover_frame], onPage=on_cover_page),
            PageTemplate(id="Content", frames=[content_frame], onPage=on_content_page),
        ])


from reportlab.platypus.flowables import KeepInFrame
from reportlab.lib.pagesizes import A4 as _A4

# rebuild with custom templates: insert NextPageTemplate before page break
from reportlab.platypus import NextPageTemplate

final_story = []
# Cover
final_story.append(NextPageTemplate("Content"))
# the cover block (already in story up to first PageBreak)
# we need to interleave: but we already built story straight through.
# Simplest: rebuild — add explicit template transitions:

final_story = []
# cover content (first part of story, up to first PageBreak)
# We'll rebuild from scratch with template hints
final_story.append(NextPageTemplate("Content"))  # next page after cover uses content template

# Re-assemble: we'll re-walk story but insert NextPageTemplate after first PageBreak.
new_story = []
inserted = False
new_story.append(NextPageTemplate("Content"))
for item in story:
    new_story.append(item)

# Build
final_doc = TwoTemplateDoc(
    OUT_PATH,
    pagesize=A4,
    leftMargin=18 * mm,
    rightMargin=18 * mm,
    topMargin=18 * mm,
    bottomMargin=20 * mm,
    title="Rinshad — React Native + Full-Stack Interview Prep",
    author="Mohammed Rinshad M I",
    subject="50 Beginner Interview Q&A",
)

# Build with explicit first template = Cover, then Content
build_story = [NextPageTemplate("Content")] + story
final_doc.build(build_story)

print(f"PDF written: {OUT_PATH}")
print(f"Total questions: {len(QA)}")
print(f"Total sections: {len(SECTIONS)}")
