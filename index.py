import cv2
import numpy as np
import pyautogui
import tkinter as tk

# Coordonnées de la zone de détection
DETECTION_REGION = [1175, 665, 1423, 788]  # (x1, y1, x2, y2)

# Plages de couleurs pour la barre de progression en HSV (émeraude)
EMERALD_LOWER = np.array([35, 60, 60])  # Ajustez pour la couleur émeraude
EMERALD_UPPER = np.array([85, 255, 255])

PIXEL_VALUE_INCREMENT_NEGATIVE = 87.58008658008658
PIXEL_VALUE_INCREMENT_POSITIVE = 87.58064516129032
VALUE_MIN = -10000

# Détection active ou non
detection_active = True


def capture_detection_region():
    """Capture uniquement la zone de détection."""
    x1, y1, x2, y2 = DETECTION_REGION
    width, height = x2 - x1, y2 - y1
    screenshot = pyautogui.screenshot(region=(x1, y1, width, height))
    return cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)


def calculate_progress(image):
    """Calcule la valeur numérique de la longueur de la barre de progression."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, EMERALD_LOWER, EMERALD_UPPER)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        largest_contour = max(contours, key=cv2.contourArea)
        x, _, w, _ = cv2.boundingRect(largest_contour)
        length_in_pixels = w

        # Utilise une valeur de pixel différente selon la longueur détectée
        if length_in_pixels <= 124:
            progress_value = VALUE_MIN + (length_in_pixels * PIXEL_VALUE_INCREMENT_NEGATIVE)
        else:
            progress_value = VALUE_MIN + (124 * PIXEL_VALUE_INCREMENT_NEGATIVE) + \
                             ((length_in_pixels - 124) * PIXEL_VALUE_INCREMENT_POSITIVE)

        return round(progress_value)
    else:
        return VALUE_MIN


def update_detection():
    """Met à jour la détection en continu et affiche les résultats."""
    if detection_active:
        screen_image = capture_detection_region()
        progress_value = calculate_progress(screen_image)

        # Mise à jour du texte et de la couleur
        result_label.config(
            text=f"Valeur de la sérénité : {progress_value}",
            fg="red" if progress_value < 0 else "green"
        )

    # Reprogrammer la prochaine vérification
    root.after(200, update_detection)


def toggle_always_on_top():
    """Active ou désactive le mode toujours au premier plan."""
    current_state = root.attributes("-topmost")
    root.attributes("-topmost", not current_state)
    toggle_top_button.config(
        text="Désactiver Toujours au Premier Plan" if not current_state else "Activer Toujours au Premier Plan"
    )


def toggle_detection():
    """Active ou désactive la détection."""
    global detection_active
    detection_active = not detection_active
    toggle_detection_button.config(
        text="Démarrer la détection" if not detection_active else "Arrêter la détection"
    )


# Interface Tkinter
root = tk.Tk()
root.title("Détection de Barre de Sérénité")
root.geometry("500x150")
root.resizable(False, False)

# Résultat
result_label = tk.Label(root, text="Valeur de la sérénité : -10000", font=("Helvetica", 14), fg="red")
result_label.pack(pady=10)

# Bouton pour activer la détection
toggle_detection_button = tk.Button(root, text="Actionner la détection", command=toggle_detection)
toggle_detection_button.pack(pady=5)

# Bouton pour activer/désactiver "toujours au premier plan"
toggle_top_button = tk.Button(root, text="Activer Toujours au Premier Plan", command=toggle_always_on_top)
toggle_top_button.pack(pady=5)

# Démarrage de la détection
root.after(100, update_detection)

# Lancer l'application
root.mainloop()
