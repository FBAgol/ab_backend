import os
import json
from io import BytesIO
import zipfile
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse

from NT_O_Detection_v3_800.anaylse_img import analyse_imgs as analyse


app = FastAPI()


@app.post("/upload-folder/")
async def upload_images(file: UploadFile = File(...)):
    temp_file_path = f"/tmp/{file.filename}"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(await file.read())

    results = []
    zip_buffer = BytesIO()

    # Prüfen, ob es sich um eine ZIP-Datei handelt
    if zipfile.is_zipfile(temp_file_path):
        with zipfile.ZipFile(temp_file_path, 'r') as zip_ref:
            extract_path = "/tmp/extracted_images"
            os.makedirs(extract_path, exist_ok=True)
            zip_ref.extractall(extract_path)

        for root, _, files in os.walk(extract_path):
            # root --> pfad zu der Image im Rechner
            for img_file in files:
                img_path = os.path.join(root, img_file)
                if img_file.lower().endswith(('.png', '.jpg', '.jpeg')):
                    image_stream, detected_objects = analyse(img_path)

                    # Bild in ZIP speichern
                    with zipfile.ZipFile(
                        zip_buffer, "a", zipfile.ZIP_DEFLATED
                    ) as zip_archive:
                        zip_archive.writestr(img_file, image_stream.getvalue())

                    # Metadaten sammeln
                    results.append({
                        "filename": img_file,
                        "detected_objects": detected_objects
                    })

    # Füge JSON-Metadaten in das ZIP hinzu
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED) as zip_archive:
        zip_archive.writestr("metadata.json", json.dumps(results))

    # ZIP-Puffer zurücksetzen mit einer JSON-file dadrin
    zip_buffer.seek(0)

    return StreamingResponse(
        zip_buffer,
        media_type="application/zip",
        headers={
            "Content-Disposition": (
                "attachment; filename=processed_images_with_metadata.zip"
            )
        }
    )