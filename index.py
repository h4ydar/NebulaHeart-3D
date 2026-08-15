import cv2
import mediapipe as mp
import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import numpy as np
import math
import threading
import time
import os

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ============================================================
# NEBULAHEART 3D
# ============================================================

WIDTH = 1000
HEIGHT = 700

CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

NUM_PARTICLES = 1800

MODEL_PATH = "hand_landmarker.task"


# ============================================================
# DATA BERSAMA
# ============================================================

lock = threading.Lock()

shared_data = {
    "running": True,
    "mode": 1,
    "gesture": "Tidak ada tangan",

    "target_x": 0.0,
    "target_y": 0.0,
    "target_z": -12.0,

    "frame": None,
    "fps": 0.0
}


# ============================================================
# RANDOM
# ============================================================

np.random.seed(42)


# ============================================================
# MODE 1 - KOSMOS
# ============================================================

pos_space = np.zeros(
    (NUM_PARTICLES, 3),
    dtype=np.float32
)

for i in range(NUM_PARTICLES):

    angle = np.random.uniform(
        0,
        math.pi * 2
    )

    radius = np.random.uniform(
        0.5,
        5.0
    )

    height = np.random.uniform(
        -2.5,
        2.5
    )

    pos_space[i] = [
        math.cos(angle) * radius,
        height,
        math.sin(angle) * radius
    ]


# ============================================================
# MODE 2 - SATURNUS
# ============================================================

pos_planet = np.zeros(
    (NUM_PARTICLES, 3),
    dtype=np.float32
)

NUM_SPHERE = 850


# Bola planet

for i in range(NUM_SPHERE):

    phi = np.random.uniform(
        0,
        math.pi * 2
    )

    costheta = np.random.uniform(
        -1,
        1
    )

    theta = math.acos(
        costheta
    )

    radius = np.random.uniform(
        1.15,
        1.45
    )

    pos_planet[i] = [
        radius * math.sin(theta) * math.cos(phi),
        radius * math.sin(theta) * math.sin(phi),
        radius * math.cos(theta)
    ]


# Cincin

for i in range(
    NUM_SPHERE,
    NUM_PARTICLES
):

    angle = np.random.uniform(
        0,
        math.pi * 2
    )

    radius = np.random.uniform(
        1.8,
        4.0
    )

    pos_planet[i] = [
        radius * math.cos(angle),
        np.random.uniform(
            -0.06,
            0.06
        ),
        radius * math.sin(angle)
    ]


# ============================================================
# MODE 3 - I LOVE U
# ============================================================

text_img = np.zeros(
    (260, 1000),
    dtype=np.uint8
)

cv2.putText(
    text_img,
    "I LOVE U",
    (150, 170),
    cv2.FONT_HERSHEY_SIMPLEX,
    4.0,
    255,
    12,
    cv2.LINE_AA
)

y_indices, x_indices = np.where(
    text_img > 0
)

x_text = (
    x_indices - 500
) / 90.0

y_text = -(
    y_indices - 130
) / 90.0

z_text = np.random.uniform(
    -0.12,
    0.12,
    len(x_text)
)

text_points = np.stack(
    [
        x_text,
        y_text,
        z_text
    ],
    axis=-1
)

chosen = np.random.choice(
    len(text_points),
    NUM_PARTICLES
)

pos_text = text_points[
    chosen
].astype(np.float32)


# ============================================================
# MODE 4 - HATI
# ============================================================

pos_heart = np.zeros(
    (NUM_PARTICLES, 3),
    dtype=np.float32
)

for i in range(NUM_PARTICLES):

    t = np.random.uniform(
        -math.pi,
        math.pi
    )

    depth = np.random.uniform(
        -math.pi,
        math.pi
    )

    x = 2.0 * (
        math.sin(t) ** 3
    )

    y = (
        2.0 * math.cos(t)
        - 0.7 * math.cos(2 * t)
        - 0.3 * math.cos(3 * t)
        - 0.1 * math.cos(4 * t)
    )

    z = math.sin(depth) * 0.45

    pos_heart[i] = [
        x * 0.9,
        y * 0.9 + 0.45,
        z
    ]


# ============================================================
# POSISI PARTIKEL
# ============================================================

current_pos = pos_space.copy()


# ============================================================
# DETEKSI JARI
# ============================================================

def get_fingers(hand_landmarks):

    tips = [
        8,
        12,
        16,
        20
    ]

    pips = [
        6,
        10,
        14,
        18
    ]

    result = []

    for tip, pip in zip(
        tips,
        pips
    ):

        result.append(
            hand_landmarks[tip].y
            <
            hand_landmarks[pip].y
        )

    return result


# ============================================================
# DETEKSI GESTURE
# ============================================================

def hitung_mode_gestur(
    hand_landmarks
):

    fingers = get_fingers(
        hand_landmarks
    )

    # Kepal = Hati

    if sum(fingers) == 0:

        return 4, "Kepal"


    # Telunjuk = Saturnus

    if (
        fingers[0]
        and not any(
            fingers[1:]
        )
    ):

        return 2, "Telunjuk"


    # Peace = I LOVE U

    if (
        fingers[0]
        and fingers[1]
        and not fingers[2]
        and not fingers[3]
    ):

        return 3, "Peace"


    # Telapak = Kosmos

    if all(fingers):

        return 1, "Telapak"


    return 1, "Gerakan lain"


# ============================================================
# GAMBAR TANGAN
# ============================================================

CONNECTIONS = [

    (0, 1),
    (1, 2),
    (2, 3),
    (3, 4),

    (0, 5),
    (5, 6),
    (6, 7),
    (7, 8),

    (5, 9),
    (9, 10),
    (10, 11),
    (11, 12),

    (9, 13),
    (13, 14),
    (14, 15),
    (15, 16),

    (13, 17),
    (17, 18),
    (18, 19),
    (19, 20),

    (0, 17)
]


def draw_hand(
    frame,
    landmarks
):

    height, width, _ = frame.shape

    points = []

    for landmark in landmarks:

        x = int(
            landmark.x * width
        )

        y = int(
            landmark.y * height
        )

        points.append(
            (x, y)
        )

        cv2.circle(
            frame,
            (x, y),
            4,
            (0, 255, 120),
            -1
        )

    for start, end in CONNECTIONS:

        cv2.line(
            frame,
            points[start],
            points[end],
            (255, 120, 0),
            2
        )


# ============================================================
# THREAD KAMERA
# ============================================================

def camera_thread_func():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print()
        print("================================")
        print("ERROR: KAMERA TIDAK TERBUKA")
        print("================================")
        print()

        shared_data["running"] = False

        return


    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        CAMERA_WIDTH
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        CAMERA_HEIGHT
    )


    # --------------------------------------------------------
    # CEK MODEL
    # --------------------------------------------------------

    if not os.path.exists(
        MODEL_PATH
    ):

        print()
        print(
            "ERROR: hand_landmarker.task tidak ditemukan!"
        )
        print(
            "Pastikan file berada satu folder dengan index.py."
        )
        print()

        cap.release()

        shared_data["running"] = False

        return


    # --------------------------------------------------------
    # MEDIAPIPE
    # --------------------------------------------------------

    base_options = python.BaseOptions(
        model_asset_path=MODEL_PATH
    )

    options = vision.HandLandmarkerOptions(
        base_options=base_options,
        num_hands=1,
        min_hand_detection_confidence=0.5,
        min_hand_presence_confidence=0.5,
        min_tracking_confidence=0.5
    )

    detector = vision.HandLandmarker.create_from_options(
        options
    )


    # --------------------------------------------------------
    # FPS
    # --------------------------------------------------------

    previous_time = time.time()

    frames = 0

    fps = 0.0


    # --------------------------------------------------------
    # LOOP KAMERA
    # --------------------------------------------------------

    while shared_data["running"]:

        ret, frame = cap.read()

        if not ret:

            time.sleep(
                0.01
            )

            continue


        # Mirror kamera

        frame = cv2.flip(
            frame,
            1
        )


        # RGB

        rgb = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb
        )


        # Deteksi tangan

        result = detector.detect(
            mp_image
        )


        local_mode = 1

        local_gesture = (
            "Tidak ada tangan"
        )

        local_x = 0.0
        local_y = 0.0
        local_z = -12.0


        # ----------------------------------------------------
        # TANGAN TERDETEKSI
        # ----------------------------------------------------

        if result.hand_landmarks:

            landmarks = (
                result.hand_landmarks[0]
            )

            draw_hand(
                frame,
                landmarks
            )


            local_mode, local_gesture = (
                hitung_mode_gestur(
                    landmarks
                )
            )


            # Posisi tangan

            wrist = landmarks[0]

            local_x = (
                wrist.x - 0.5
            ) * 10.0

            local_y = -(
                wrist.y - 0.5
            ) * 7.0


            # Jarak tangan

            middle = landmarks[9]

            distance = math.sqrt(

                (
                    wrist.x
                    -
                    middle.x
                ) ** 2

                +

                (
                    wrist.y
                    -
                    middle.y
                ) ** 2
            )


            local_z = (
                -11.0
                -
                distance * 4.0
            )


        # ----------------------------------------------------
        # FPS
        # ----------------------------------------------------

        frames += 1

        now = time.time()

        elapsed = (
            now
            -
            previous_time
        )

        if elapsed >= 1.0:

            fps = (
                frames
                /
                elapsed
            )

            frames = 0

            previous_time = now


        # ----------------------------------------------------
        # TEKS PADA KAMERA
        # ----------------------------------------------------

        cv2.rectangle(
            frame,
            (0, 0),
            (CAMERA_WIDTH, 95),
            (0, 0, 0),
            -1
        )


        cv2.putText(
            frame,
            "NEBULAHEART 3D",
            (15, 28),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.75,
            (255, 255, 255),
            2
        )


        cv2.putText(
            frame,
            f"GESTUR : {local_gesture}",
            (15, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.55,
            (0, 255, 180),
            2
        )


        cv2.putText(
            frame,
            f"FPS : {fps:.1f}",
            (15, 80),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.5,
            (180, 220, 255),
            2
        )


        # ----------------------------------------------------
        # SIMPAN DATA
        # ----------------------------------------------------

        with lock:

            shared_data["mode"] = (
                local_mode
            )

            shared_data["gesture"] = (
                local_gesture
            )

            shared_data["target_x"] = (
                local_x
            )

            shared_data["target_y"] = (
                local_y
            )

            shared_data["target_z"] = (
                local_z
            )

            shared_data["fps"] = (
                fps
            )

            shared_data["frame"] = (
                frame.copy()
            )


    detector.close()

    cap.release()


# ============================================================
# MULAI KAMERA
# ============================================================

camera_thread = threading.Thread(
    target=camera_thread_func,
    daemon=True
)

camera_thread.start()


# Tunggu kamera sebentar

time.sleep(
    1.0
)


# ============================================================
# PYGAME
# ============================================================

pygame.init()

pygame.display.set_mode(
    (
        WIDTH,
        HEIGHT
    ),
    DOUBLEBUF | OPENGL
)

pygame.display.set_caption(
    "NebulaHeart 3D"
)


# ============================================================
# OPENGL
# ============================================================

glMatrixMode(
    GL_PROJECTION
)

glLoadIdentity()

gluPerspective(
    45,
    WIDTH / HEIGHT,
    0.1,
    60.0
)

glMatrixMode(
    GL_MODELVIEW
)

glEnable(
    GL_DEPTH_TEST
)

glEnable(
    GL_BLEND
)

glBlendFunc(
    GL_SRC_ALPHA,
    GL_ONE_MINUS_SRC_ALPHA
)


# ============================================================
# VARIABEL
# ============================================================

clock = pygame.time.Clock()

rotation = 0.0

hand_x = 0.0
hand_y = 0.0
hand_z = -12.0

current_mode = 1

manual_mode = False

start_time = time.time()


# ============================================================
# LOOP UTAMA
# ============================================================

while shared_data["running"]:

    # --------------------------------------------------------
    # EVENT
    # --------------------------------------------------------

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            shared_data["running"] = False


        if event.type == KEYDOWN:

            if event.key == K_ESCAPE:

                shared_data["running"] = False


            elif event.key == K_1:

                current_mode = 1

                manual_mode = True


            elif event.key == K_2:

                current_mode = 2

                manual_mode = True


            elif event.key == K_3:

                current_mode = 3

                manual_mode = True


            elif event.key == K_4:

                current_mode = 4

                manual_mode = True


            elif event.key == K_g:

                manual_mode = False


    # --------------------------------------------------------
    # AMBIL DATA
    # --------------------------------------------------------

    with lock:

        detected_mode = (
            shared_data["mode"]
        )

        target_x = (
            shared_data["target_x"]
        )

        target_y = (
            shared_data["target_y"]
        )

        target_z = (
            shared_data["target_z"]
        )

        frame = (
            shared_data["frame"]
        )


    # --------------------------------------------------------
    # TAMPILKAN KAMERA
    # --------------------------------------------------------

    if frame is not None:

        cv2.imshow(
            "NebulaHeart - Kamera",
            frame
        )

        key = cv2.waitKey(
            1
        ) & 0xFF

        if key == ord("q"):

            shared_data["running"] = False


    # --------------------------------------------------------
    # MODE
    # --------------------------------------------------------

    if not manual_mode:

        current_mode = (
            detected_mode
        )


    # --------------------------------------------------------
    # GERAKAN TANGAN
    # --------------------------------------------------------

    hand_x += (
        target_x
        -
        hand_x
    ) * 0.12


    hand_y += (
        target_y
        -
        hand_y
    ) * 0.12


    hand_z += (
        target_z
        -
        hand_z
    ) * 0.12


    # --------------------------------------------------------
    # WAKTU
    # --------------------------------------------------------

    elapsed = (
        time.time()
        -
        start_time
    )


    # --------------------------------------------------------
    # TARGET BENTUK
    # --------------------------------------------------------

    if current_mode == 1:

        target_pos = pos_space

        rotation += 0.25


    elif current_mode == 2:

        target_pos = pos_planet

        rotation += 0.8


    elif current_mode == 3:

        target_pos = pos_text

        rotation = 0.0


    else:

        target_pos = pos_heart

        rotation += 0.35


    # --------------------------------------------------------
    # TRANSISI
    # --------------------------------------------------------

    current_pos += (
        target_pos
        -
        current_pos
    ) * 0.08


    # Salin agar bentuk asli tidak berubah

    render_pos = (
        current_pos.copy()
    )


    # ========================================================
    # ANIMASI HATI
    # ========================================================

    if current_mode == 4:

        beat = (
            1.0
            +
            0.08
            *
            math.sin(
                elapsed * 5.0
            )
        )

        render_pos *= beat


    # ========================================================
    # ANIMASI KOSMOS
    # ========================================================

    if current_mode == 1:

        orbit = (
            elapsed * 0.25
        )

        cos_a = math.cos(
            orbit
        )

        sin_a = math.sin(
            orbit
        )

        x = render_pos[:, 0].copy()

        z = render_pos[:, 2].copy()

        render_pos[:, 0] = (
            x * cos_a
            -
            z * sin_a
        )

        render_pos[:, 2] = (
            x * sin_a
            +
            z * cos_a
        )


    # ========================================================
    # OPENGL CLEAR
    # ========================================================

    glClearColor(
        0.005,
        0.005,
        0.02,
        1.0
    )

    glClear(
        GL_COLOR_BUFFER_BIT
        |
        GL_DEPTH_BUFFER_BIT
    )

    glLoadIdentity()


    # ========================================================
    # POSISI
    # ========================================================

    if current_mode in (
        2,
        3,
        4
    ):

        glTranslatef(
            hand_x,
            hand_y,
            hand_z
        )

    else:

        glTranslatef(
            0.0,
            0.0,
            -12.0
        )


    # ========================================================
    # ROTASI
    # ========================================================

    if current_mode == 2:

        glRotatef(
            25,
            1.0,
            0.0,
            0.5
        )


    if current_mode == 4:

        glRotatef(
            math.sin(
                elapsed * 0.7
            ) * 4.0,
            0.0,
            1.0,
            0.0
        )


    glRotatef(
        rotation,
        0.0,
        1.0,
        0.0
    )


    # ========================================================
    # UKURAN PARTIKEL
    # ========================================================

    if current_mode == 3:

        glPointSize(
            4.8
        )

    elif current_mode == 4:

        glPointSize(
            5.2
        )

    else:

        glPointSize(
            4.0
        )


    # ========================================================
    # PARTIKEL
    # ========================================================

    glBegin(
        GL_POINTS
    )


    for i in range(
        NUM_PARTICLES
    ):

        pulse = (
            0.75
            +
            0.25
            *
            math.sin(
                elapsed * 3.0
                +
                i * 0.03
            )
        )


        # ----------------------------------------------------
        # KOSMOS
        # ----------------------------------------------------

        if current_mode == 1:

            glColor4f(
                0.10 * pulse,
                0.50 * pulse,
                1.00,
                0.85
            )


        # ----------------------------------------------------
        # SATURNUS
        # ----------------------------------------------------

        elif current_mode == 2:

            if i < NUM_SPHERE:

                glColor4f(
                    1.0,
                    0.55 * pulse,
                    0.08,
                    0.90
                )

            else:

                glColor4f(
                    1.0,
                    0.80 * pulse,
                    0.30,
                    0.70
                )


        # ----------------------------------------------------
        # I LOVE U
        # ----------------------------------------------------

        elif current_mode == 3:

            glColor4f(
                0.15,
                0.80 * pulse,
                1.0,
                0.95
            )


        # ----------------------------------------------------
        # HATI
        # ----------------------------------------------------

        else:

            heart_pulse = (
                0.75
                +
                0.25
                *
                math.sin(
                    elapsed * 5.0
                )
            )

            glColor4f(
                1.0,
                0.08 * heart_pulse,
                0.35 * heart_pulse,
                0.95
            )


        glVertex3f(
            render_pos[i, 0],
            render_pos[i, 1],
            render_pos[i, 2]
        )


    glEnd()


    # ========================================================
    # UPDATE
    # ========================================================

    pygame.display.flip()

    clock.tick(
        60
    )


# ============================================================
# SELESAI
# ============================================================

shared_data["running"] = False

time.sleep(
    0.2
)

cv2.destroyAllWindows()

pygame.quit()

print(
    "NebulaHeart 3D selesai."
)