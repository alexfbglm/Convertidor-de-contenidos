import streamlit as st
from PIL import Image
import io

# Función para comprimir la imagen si excede los 30 MB
def compress_image(image, output_format, max_size_mb=30):
    quality = 95
    img_bytes = io.BytesIO()
    
    # Guardar la imagen y verificar el tamaño
    image.save(img_bytes, format=output_format.upper(), quality=quality)
    while img_bytes.tell() > max_size_mb * 1024 * 1024 and quality > 10:
        quality -= 5
        img_bytes = io.BytesIO()  # Reiniciar el buffer
        image.save(img_bytes, format=output_format.upper(), quality=quality)
    
    return img_bytes

# Función para convertir la imagen a formato JPG o PNG
def convert_image_to_format(image, output_format):
    if output_format.lower() == 'jpg':
        image = image.convert('RGB')  # Convertir a RGB si es JPG

    output_img = compress_image(image, output_format)
    return output_img

# Streamlit App
def main():
    st.title("Convertidor de Imágenes TIFF a JPG/PNG")

    # Permitir al usuario subir un archivo TIFF
    uploaded_file = st.file_uploader("Sube una imagen TIFF para convertir", type=["tif", "tiff"])

    if uploaded_file is not None:
        # Mostrar la imagen original
        image = Image.open(uploaded_file)
        st.image(image, caption='Imagen original', use_column_width=True)

        # Seleccionar formato de salida
        output_format = st.selectbox("Selecciona el formato de salida", ['jpg', 'png'])

        if st.button("Convertir"):
            # Convertir la imagen
            output_image = convert_image_to_format(image, output_format)

            # Descargar el archivo convertido
            st.download_button(
                label="Descargar imagen convertida",
                data=output_image.getvalue(),
                file_name=f"imagen_convertida.{output_format}",
                mime=f"image/{'jpeg' if output_format == 'jpg' else 'png'}"
            )

if __name__ == "__main__":
    main()
