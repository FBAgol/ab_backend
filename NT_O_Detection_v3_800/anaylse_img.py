import os
import cv2
from io import BytesIO
import matplotlib.pyplot as plt
from ultralytics import YOLO

# Setze das Home-Verzeichnis und den Pfad zum Dataset
HOME = os.getcwd()

def analyse_imgs(img):
    # Modell laden
    model_path = '/home/fgolzari/Dokumente/myProjekts/Abschlussprojekt/backend/NT_O_Detection_v3_800/NT_O3/NT_O_Detection3/runs/detect/train/weights/best.pt'
    model = YOLO(model_path)

    # Bild lesen
    image_path = img
    image = cv2.imread(image_path)

    # Inferenz durchführen
    results = model(image, conf=0.3)

    # Überprüfe die Rückgabewerte
    boxes = results[0].boxes.xyxy
    scores = results[0].boxes.conf
    classes = results[0].boxes.cls
    class_names = model.model.names  # Zugriff auf die Klassennamen

    # Liste zur Speicherung der erkannten Klassen mit Position und Größe
    detected_objects = []

    # Boxen und Texte zeichnen
    colors = [[0, 255, 0], [255, 0, 0], [0, 0, 255]]
    for box, score, cls in zip(boxes, scores, classes):
        x1, y1, x2, y2 = map(int, box)
        width, height = x2 - x1, y2 - y1
        color = colors[int(cls) % len(colors)]
        label = f'{class_names[int(cls)]}: {score:.2f}' if cls < len(class_names) else f'Klasse {cls}: {score:.2f}'
        cv2.rectangle(image, (x1, y1), (x2, y2), color, 2)
        cv2.putText(image, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        # Informationen zur erkannten Klasse hinzufügen
        detected_objects.append({
            'class_name': class_names[int(cls)] if cls < len(class_names) else f'Klasse {cls}',
            'x': x1,
            'y': y1,
            'width': width,
            'height': height
        })

    # Bild anzeigen
    """
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.axis('off')
    plt.show()
    """


    # Bild speichern
    """
     output_dir = os.path.join(HOME, 'output-testimg')  # Zielordner
    os.makedirs(output_dir, exist_ok=True)  # Erstelle den Ordner, falls er nicht existiert

    output_image_path = os.path.join(output_dir, 'erkanntes_Trasse_4069993.jpg')
    cv2.imwrite(output_image_path, image)  # Bild speichern
    print(f'Bild gespeichert unter: {output_image_path}')
    
    """





    # Erkannten Klasseninformationen ausgeben
    """
     print("Gefundene Objekte mit Position und Größe:")
    for obj in detected_objects:
        print(
            f"Klasse: {obj['class_name']}, x: {obj['x']}, y: {obj['y']}, Breite: {obj['width']}, Höhe: {obj['height']}")
    """


    # Optional: Visualisierung von Trainingsbildern

    """
        def visualize_training_images(train_images_path):
        train_image_files = os.listdir(train_images_path)

        # Zeige ein paar Bilder an
        for img_file in train_image_files[:5]:  # die ersten 5 Bilder
            img_path = os.path.join(train_images_path, img_file)
            img = cv2.imread(img_path)
            plt.imshow(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
            plt.axis('off')
            plt.title(img_file)
            plt.show()
    """

    # Bild in einen BytesIO-Puffer schreiben
    _, buffer = cv2.imencode('.jpg', image)
    image_bytes = BytesIO(buffer)

    return image_bytes, detected_objects


