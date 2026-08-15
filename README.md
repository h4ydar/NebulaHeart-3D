# 🌌 NebulaHeart 3D

**NebulaHeart 3D** adalah project visual 3D berbasis Python yang menggunakan **hand tracking** untuk mengendalikan bentuk partikel secara real-time.

Gerakan tangan di depan kamera akan mengubah bentuk partikel 3D. ✨

## ✋ Gesture Controls

| Gesture | Efek |
|---|---|
| 🖐️ Telapak terbuka | 🌌 Kosmos |
| ☝️ Satu jari | 🪐 Saturnus 3D |
| ✌️ Peace | 💙 I LOVE U AYAA |
| ✊ Kepal | ❤️ Hati |

## 🛠️ Dibuat dengan

- Python
- OpenCV
- MediaPipe
- NumPy
- Pygame
- PyOpenGL              

## 🎥 Cara Kerja

Kamera laptop mendeteksi posisi tangan menggunakan MediaPipe Hand Landmarker.

Gesture yang terdeteksi kemudian digunakan untuk memilih bentuk partikel 3D yang ditampilkan menggunakan OpenGL.

## 🚀 Menjalankan Project

Pastikan Python dan library yang diperlukan sudah terpasang.

```bash
pip install opencv-python mediapipe numpy pygame PyOpenGL PyOpenGL_accelerate
