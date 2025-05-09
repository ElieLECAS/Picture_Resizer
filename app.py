import streamlit as st
from PIL import Image
import io
import zipfile

# Taille cible fixée à 0.9 Mo
TARGET_SIZE_MB = 0.9
TARGET_SIZE_BYTES = TARGET_SIZE_MB * 1024 * 1024

def compress_until_target_size(img):
    quality = 95  # On démarre avec une meilleure qualité
    min_quality = 40  # Qualité minimale à atteindre
    step = 5
    
    # Convertir en RGB si l'image est en RGBA
    if img.mode == 'RGBA':
        img = img.convert('RGB')
    
    # Premier essai avec qualité maximale
    buffer = io.BytesIO()
    img.save(buffer, format="JPEG", quality=quality, optimize=True)
    
    # Si l'image est déjà plus petite que la taille cible, on la retourne telle quelle
    if buffer.tell() <= TARGET_SIZE_BYTES:
        return buffer
    
    # Sinon, on réduit progressivement la qualité
    while quality > min_quality:
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=quality, optimize=True)
        if buffer.tell() <= TARGET_SIZE_BYTES:
            break
        quality -= step
    
    return buffer

st.title("📸 Redimensionneur d'images")

uploaded_files = st.file_uploader("Chargez des images (JPEG/PNG)", type=["jpg", "jpeg", "png"], accept_multiple_files=True)

if uploaded_files:
    with st.spinner("Traitement des images en cours..."):
        resized_images = []
        download_buttons = []
        
        for uploaded_file in uploaded_files:
            image = Image.open(uploaded_file)
            
            # Compression de l'image
            resized_buffer = compress_until_target_size(image)
            resized_size_kb = resized_buffer.tell() / 1024
            
            resized_images.append((uploaded_file.name, resized_buffer))
            
            # Création d'un bouton de téléchargement pour l'image
            download_button = st.download_button(
                label=f"📥 Télécharger {uploaded_file.name} ({resized_size_kb:.0f} Ko)",
                data=resized_buffer.getvalue(),
                file_name=f"redim_{uploaded_file.name}",
                mime="image/jpeg"
            )
            download_buttons.append(download_button)
    
    # Option pour télécharger toutes les images dans un ZIP
    if len(resized_images) > 1:
        st.write("---")
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w") as zip_file:
            for name, buffer in resized_images:
                buffer.seek(0)
                zip_file.writestr(f"redim_{name}", buffer.read())
        
        st.download_button(
            label="📥 Télécharger toutes les images redimensionnées (ZIP)",
            data=zip_buffer.getvalue(),
            file_name="images_redimensionnees.zip",
            mime="application/zip"
        )
