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

from mediapipe.tasks import python
from mediapipe.tasks.python import vision


# ============================================================
# KONFIGURASI
# ============================================================

WIDTH = 1000
HEIGHT = 700

NUM_PARTICLES = 1500

MODEL_PATH = "hand_landmarker.task"

lock = threading.Lock()

shared_data = {
    "mode": 1,
    "target_x": 0.0,
    "target_y": 0.0,
    "target_z": -12.0,
    "frame": None,
    "running": True
}


# ============================================================
# MODE 1 - KOSMOS
# ============================================================

pos_space = np.random.uniform(
    -4.0,
    4.0,
    (NUM_PARTICLES, 3)
)


# ============================================================
# MODE 2 - SATURNUS
# ============================================================

pos_planet = np.zeros(
    (NUM_PARTICLES, 3)
)

NUM_SPHERE = 700

for i in range(NUM_SPHERE):

    phi = np.random.uniform(
        0,
        2 * np.pi
    )

    costheta = np.random.uniform(
        -1,
        1
    )

    theta = np.arccos(
        costheta
    )

    r = 1.3

    pos_planet[i, 0] = (
        r
        * np.sin(theta)
        * np.cos(phi)
    )

    pos_planet[i, 1] = (
        r
        * np.sin(theta)
        * np.sin(phi)
    )

    pos_planet[i, 2] = (
        r
        * np.cos(theta)
    )


# Cincin Saturnus

for i in range(
    NUM_SPHERE,
    NUM_PARTICLES
):

    theta = np.random.uniform(
        0,
        2 * np.pi
    )

    r = np.random.uniform(
        1.8,
        3.8
    )

    pos_planet[i, 0] = (
        r * np.cos(theta)
    )

    pos_planet[i, 1] = np.random.uniform(
        -0.05,
        0.05
    )

    pos_planet[i, 2] = (
        r * np.sin(theta)
    )


# ============================================================
# MODE 3 - I LOVE U AYAA
# ============================================================

text_img = np.zeros(
    (250, 900),
    dtype=np.uint8
)

cv2.putText(
    text_img,
    "I LOVE U AYAA",
    (20, 160),
    cv2.FONT_HERSHEY_SIMPLEX,
    3.0,
    255,
    10,
    cv2.LINE_AA
)

y_indices, x_indices = np.where(
    text_img > 0
)

x_text = (
    x_indices - 450
) / 75.0

y_text = -(
    y_indices - 125
) / 75.0

z_text = np.random.uniform(
    -0.1,
    0.1,
    len(x_text)
)

text_points = np.stack(
    (
        x_text,
        y_text,
        z_text
    ),
    axis=-1
)

chosen_indices = np.random.choice(
    len(text_points),
    NUM_PARTICLES
)

pos_text = text_points[
    chosen_indices
]


# ============================================================
# MODE 4 - HATI
# ============================================================

pos_heart = np.zeros(
    (NUM_PARTICLES, 3)
)

for i in range(
    NUM_PARTICLES
):

    t = np.random.uniform(
        -np.pi,
        np.pi
    )

    p = np.random.uniform(
        -np.pi,
        np.pi
    )

    x = 2.0 * (
        np.sin(t) ** 3
    )

    y = (
        2.0 * np.cos(t)
        - 0.7 * np.cos(2 * t)
        - 0.3 * np.cos(3 * t)
        - 0.1 * np.cos(4 * t)
    )

    z = np.sin(p) * 0.4

    pos_heart[i, 0] = (
        x * 0.85
    )

    pos_heart[i, 1] = (
        y * 0.85
    ) + 0.5

    pos_heart[i, 2] = z


# ============================================================
# POSISI PARTIKEL
# ============================================================

current_pos = np.copy(
    pos_space
)

target_pos = np.copy(
    pos_space
)


# ============================================================
# DETEKSI GESTUR
# ============================================================

def hitung_mode_gestur(
    hand_landmarks
):

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

    jari_berdiri = []

    for tip, pip in zip(
        tips,
        pips
    ):

        jari_berdiri.append(
            hand_landmarks[tip].y
            <
            hand_landmarks[pip].y
        )


    # --------------------------------------------------------
    # KEPAL -> HATI
    # --------------------------------------------------------

    if sum(jari_berdiri) == 0:

        return 4


    # --------------------------------------------------------
    # TELUNJUK -> SATURNUS
    # --------------------------------------------------------

    if (
        jari_berdiri[0]
        and not any(
            jari_berdiri[1:]
        )
    ):

        return 2


    # --------------------------------------------------------
    # PEACE -> I LOVE U AYAA
    # --------------------------------------------------------

    if (
        jari_berdiri[0]
        and jari_berdiri[1]
        and not jari_berdiri[2]
        and not jari_berdiri[3]
    ):

        return 3


    # --------------------------------------------------------
    # DEFAULT -> KOSMOS
    # --------------------------------------------------------

    return 1


# ============================================================
# GARIS TANGAN
# ============================================================

HAND_CONNECTIONS = [

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


# ============================================================
# GAMBAR LANDMARK TANGAN
# ============================================================

def gambar_tangan(
    frame,
    hand_landmarks
):

    tinggi, lebar, _ = frame.shape

    points = []

    for landmark in hand_landmarks:

        x = int(
            landmark.x * lebar
        )

        y = int(
            landmark.y * tinggi
        )

        points.append(
            (x, y)
        )

        cv2.circle(
            frame,
            (x, y),
            4,
            (0, 255, 0),
            -1
        )


    for start, end in HAND_CONNECTIONS:

        cv2.line(
            frame,
            points[start],
            points[end],
            (255, 0, 0),
            2
        )


# ============================================================
# THREAD KAMERA
# ============================================================

def camera_thread_func():

    cap = cv2.VideoCapture(0)

    if not cap.isOpened():

        print(
            "ERROR: Kamera tidak dapat dibuka."
        )

        shared_data["running"] = False

        return


    cap.set(
        cv2.CAP_PROP_FRAME_WIDTH,
        480
    )

    cap.set(
        cv2.CAP_PROP_FRAME_HEIGHT,
        360
    )


    # ========================================================
    # MEDIAPIPE HAND LANDMARKER
    # ========================================================

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

    detector = (
        vision.HandLandmarker
        .create_from_options(options)
    )


    # ========================================================
    # LOOP KAMERA
    # ========================================================

    while shared_data["running"]:

        ret, frame = cap.read()

        if not ret:

            time.sleep(0.01)

            continue


        # Mirror kamera

        frame = cv2.flip(
            frame,
            1
        )


        # BGR -> RGB

        rgb_frame = cv2.cvtColor(
            frame,
            cv2.COLOR_BGR2RGB
        )


        # MediaPipe Image

        mp_image = mp.Image(
            image_format=mp.ImageFormat.SRGB,
            data=rgb_frame
        )


        # Deteksi tangan

        detection_result = detector.detect(
            mp_image
        )


        local_mode = 1

        local_x = 0.0
        local_y = 0.0
        local_z = -12.0


        # ====================================================
        # JIKA TANGAN TERDETEKSI
        # ====================================================

        if detection_result.hand_landmarks:

            for hand_landmarks in (
                detection_result.hand_landmarks
            ):

                # Gambar tangan

                gambar_tangan(
                    frame,
                    hand_landmarks
                )


                # Deteksi gesture

                local_mode = (
                    hitung_mode_gestur(
                        hand_landmarks
                    )
                )


                # Posisi wrist

                wrist = (
                    hand_landmarks[0]
                )


                local_x = (
                    wrist.x - 0.5
                ) * 10.0


                local_y = -(
                    wrist.y - 0.5
                ) * 7.0


                # Jarak tangan

                pinky_mcp = (
                    hand_landmarks[17]
                )


                distance = math.sqrt(

                    (
                        wrist.x
                        -
                        pinky_mcp.x
                    ) ** 2

                    +

                    (
                        wrist.y
                        -
                        pinky_mcp.y
                    ) ** 2

                )


                local_z = (
                    -10.0
                    -
                    (
                        1.0
                        /
                        (distance + 0.01)
                    )
                    * 0.2
                )


        # ====================================================
        # SIMPAN DATA
        # ====================================================

        with lock:

            shared_data["mode"] = (
                local_mode
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

            shared_data["frame"] = (
                frame
            )


    detector.close()

    cap.release()


# ============================================================
# MULAI THREAD KAMERA
# ============================================================

camera_thread = threading.Thread(
    target=camera_thread_func,
    daemon=True
)

camera_thread.start()

time.sleep(1.0)


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
    "NebulaHeart 3D - Gesture Controller"
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
    50.0
)

glMatrixMode(
    GL_MODELVIEW
)

glEnable(
    GL_DEPTH_TEST
)


# ============================================================
# VARIABEL RENDER
# ============================================================

clock = pygame.time.Clock()

rotation_angle = 0.0

hand_x = 0.0
hand_y = 0.0
hand_z = -12.0


# ============================================================
# LOOP UTAMA
# ============================================================

while shared_data["running"]:

    pygame.event.pump()


    for event in pygame.event.get():

        if (
            event.type == pygame.QUIT
            or (
                event.type == KEYDOWN
                and event.key == K_ESCAPE
            )
        ):

            shared_data["running"] = False


    # ========================================================
    # AMBIL DATA DARI KAMERA
    # ========================================================

    with lock:

        current_mode = (
            shared_data["mode"]
        )

        target_hand_x = (
            shared_data["target_x"]
        )

        target_hand_y = (
            shared_data["target_y"]
        )

        target_hand_z = (
            shared_data["target_z"]
        )

        frame = (
            shared_data["frame"]
        )


    # ========================================================
    # TAMPILKAN KAMERA
    # ========================================================

    if frame is not None:

        mode_labels = {

            1:
            "KOSMOS - Telapak Terbuka",

            2:
            "SATURNUS 3D - Satu Jari",

            3:
            "I LOVE U AYAA - Peace",

            4:
            "HATI / LOVE - Kepal"
        }


        cv2.putText(

            frame,

            "MODE: "
            +
            mode_labels[
                current_mode
            ],

            (10, 30),

            cv2.FONT_HERSHEY_SIMPLEX,

            0.5,

            (0, 255, 0),

            2
        )


        # Window kamera

        cv2.imshow(
            "Hand Sensor Monitor",
            frame
        )


        # Tekan Q untuk keluar

        if (
            cv2.waitKey(1) & 0xFF
        ) == ord("q"):

            shared_data["running"] = False


    # ========================================================
    # BERSIHKAN LAYAR OPENGL
    # ========================================================

    glClearColor(
        0.0,
        0.0,
        0.0,
        1.0
    )

    glClear(
        GL_COLOR_BUFFER_BIT
        |
        GL_DEPTH_BUFFER_BIT
    )

    glLoadIdentity()


    # ========================================================
    # GERAKAN OBJEK MENGIKUTI TANGAN
    # ========================================================

    hand_x += (
        target_hand_x
        -
        hand_x
    ) * 0.25


    hand_y += (
        target_hand_y
        -
        hand_y
    ) * 0.25


    hand_z += (
        target_hand_z
        -
        hand_z
    ) * 0.25


    # ========================================================
    # PILIH TARGET BENTUK
    # ========================================================

    if current_mode == 1:

        target_pos = pos_space

        rotation_angle += 0.5


    elif current_mode == 2:

        target_pos = pos_planet

        rotation_angle += 2.0


    elif current_mode == 3:

        target_pos = pos_text

        rotation_angle = 0.0


    elif current_mode == 4:

        target_pos = pos_heart

        rotation_angle += 1.5


    # ========================================================
    # TRANSISI PARTIKEL
    # ========================================================

    current_pos += (
        target_pos
        -
        current_pos
    ) * 0.15


    # ========================================================
    # POSISI BENTUK
    # ========================================================

    if current_mode in [
        2,
        3,
        4
    ]:

        glTranslatef(
            hand_x,
            hand_y,
            hand_z
        )


        if current_mode == 2:

            glRotatef(
                25,
                1.0,
                0.0,
                0.5
            )


    else:

        glTranslatef(
            0.0,
            0.0,
            -12.0
        )


    # Rotasi

    glRotatef(
        rotation_angle,
        0.0,
        1.0,
        0.0
    )


    # ========================================================
    # PARTIKEL
    # ========================================================

    glEnable(
        GL_BLEND
    )

    glBlendFunc(
        GL_SRC_ALPHA,
        GL_ONE_MINUS_SRC_ALPHA
    )

    glPointSize(
        4.5
    )


    glBegin(
        GL_POINTS
    )


    for i in range(
        NUM_PARTICLES
    ):


        # ----------------------------------------------------
        # I LOVE U AYAA
        # ----------------------------------------------------

        if current_mode == 3:

            glColor4f(
                0.0,
                0.8,
                1.0,
                0.9
            )


        # ----------------------------------------------------
        # HATI
        # ----------------------------------------------------

        elif current_mode == 4:

            glColor4f(
                1.0,
                0.1,
                0.4,
                0.95
            )


        # ----------------------------------------------------
        # CINCIN SATURNUS
        # ----------------------------------------------------

        elif (
            current_mode == 2
            and i >= NUM_SPHERE
        ):

            glColor4f(
                1.0,
                0.7,
                0.3,
                0.6
            )


        # ----------------------------------------------------
        # BADAN SATURNUS
        # ----------------------------------------------------

        elif (
            current_mode == 2
            and i < NUM_SPHERE
        ):

            glColor4f(
                1.0,
                0.5,
                0.0,
                0.85
            )


        # ----------------------------------------------------
        # KOSMOS
        # ----------------------------------------------------

        else:

            glColor4f(
                0.1,
                0.5,
                1.0,
                0.8
            )


        glVertex3f(

            current_pos[i, 0],

            current_pos[i, 1],

            current_pos[i, 2]
        )


    glEnd()


    # ========================================================
    # UPDATE DISPLAY
    # ========================================================

    pygame.display.flip()

    clock.tick(60)


# ============================================================
# CLEAN UP
# ============================================================

shared_data["running"] = False

cv2.destroyAllWindows()

pygame.quit()