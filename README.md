🦸‍♂️ Daredevil — Real-Time AI Accessibility Assistant for the Blind

Daredevil is a Proof of Concept (PoC) accessibility tool that provides real-time audio feedback for visually impaired users using a live camera feed.
It leverages Generative AI, WebSockets, and text-to-speech (TTS) technologies to describe surroundings, detect obstacles, and guide safe navigation — all in real time.

🚀 Features

🎥 Live Scene Understanding — Analyzes the camera feed in real time using OpenAI Vision models.

🗣️ Instant Audio Feedback — Converts AI-generated descriptions into natural speech using Edge TTS.

🌐 Real-Time Streaming — Uses WebSockets for low-latency communication between the camera client and AI backend.

🧭 Navigation-Oriented Descriptions — Focused feedback on:

Immediate obstacles or hazards

Open pathways and directions

Relative distance to objects

People and their positions

Doorways, stairs, or elevation changes

♿ Accessibility-First Design — Built to enhance independent mobility for blind and low-vision users.

🧠 How It Works

Camera Feed → Backend via WebSocket:
The live camera stream is sent frame-by-frame to the backend through WebSockets.

AI Scene Analysis:
The backend uses OpenAI’s multimodal models (e.g., gpt-4o-mini or gpt-4o) to interpret the scene and generate concise, safety-critical navigation instructions.

Audio Generation:
The textual feedback is converted to speech using Edge TTS for fast and natural voice output.

User Feedback Loop:
The generated speech is streamed back to the user for real-time situational awareness.
