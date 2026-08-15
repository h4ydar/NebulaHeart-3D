<div align="center">

# 🌌 NebulaHeart 3D

### ✋ Gesture-Controlled 3D Particle Experience

**A real-time 3D visual experience controlled by hand gestures using Python, OpenCV, MediaPipe and OpenGL.**

<br>

<img src="nebulaheart-demo.png" alt="NebulaHeart 3D Demo" width="800">

<br><br>

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)
![OpenCV](https://img.shields.io/badge/OpenCV-Computer%20Vision-red?logo=opencv)
![MediaPipe](https://img.shields.io/badge/MediaPipe-Hand%20Tracking-orange)
![OpenGL](https://img.shields.io/badge/OpenGL-3D%20Graphics-lightgrey?logo=opengl)
![Pygame](https://img.shields.io/badge/Pygame-Graphics-green)

</div>

---

## ✨ About

**NebulaHeart 3D** is an interactive Python project that combines **computer vision, hand tracking and 3D particle graphics**.

The project uses your laptop camera to detect hand gestures in real time. Each gesture controls a different particle formation inside a 3D environment.

The goal is to create a simple but visually interesting example of how **AI/computer vision can interact with 3D graphics**.

---

## ✋ Gesture Controls

| Gesture | Effect |
|:---:|---|
| 🖐️ Open Hand | 🌌 Cosmic Particles |
| ☝️ One Finger | 🪐 Saturn 3D |
| ✌️ Peace | 💙 **I LOVE U NAMA KAMU** |
| ✊ Fist | ❤️ Heart |

---

## 🎥 How It Works

```text
        📷 Camera
           │
           ▼
   ┌─────────────────┐
   │    MediaPipe    │
   │  Hand Tracking  │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │ Gesture Detection│
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │   Mode Selector │
   └────────┬────────┘
            │
            ▼
   ┌─────────────────┐
   │  3D Particles   │
   │     OpenGL      │
   └─────────────────┘
