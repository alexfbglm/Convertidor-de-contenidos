import streamlit as st
from PIL import Image
import io
import zipfile
import os

# Función para guardar y comprimir la imagen
def save_image(image, output_format):
    img_bytes = io.BytesIO()
    
    # Convertir a RGB si es JPG y guardar la imagen
    if output_format == 'jpg':
        image = image.convert('RGB')  # Convertir a RGB si es JPG
        image.save(img_bytes, format='JPEG', quality=85)  # Guardar con calidad fija para JPG
    else:
        image.save(img_bytes, format=output_format.upper())  # Guardar en PNG sin compresión de calidad
    
    return img_bytes

# Función para convertir una imagen a formato JPG o PNG
def convert_image_to_format(image, output_format):
    output_format = output_format.lower()  # Asegurar que el formato esté en minúsculas
    
    try:
        output_img = save_image(image, output_format)
        return output_img
    except Exception as e:
        st.error(f"Error durante la compresión de la imagen: {str(e)}")
        return None

# Función para procesar múltiples imágenes desde un archivo ZIP
def process_zip_file(zip_file, output_format):
    # Crear un nuevo archivo ZIP para las imágenes convertidas
    output_zip_bytes = io.BytesIO()

    with zipfile.ZipFile(output_zip_bytes, mode='w') as output_zip:
        with zipfile.ZipFile(zip_file) as z:
            for file_name in z.namelist():
                if file_name.lower().endswith(('.tif', '.tiff')):
                    # Abrir cada archivo de imagen dentro del ZIP
                    with z.open(file_name) as file:
                        image = Image.open(file)
                        # Convertir la imagen
                        converted_image = convert_image_to_format(image, output_format)
                        if converted_image:
                            # Guardar la imagen convertida en el nuevo ZIP
                            output_zip.writestr(f"{os.path.splitext(file_name)[0]}_converted.{output_format}", converted_image.getvalue())
    
    return output_zip_bytes

# Streamlit App
def main():
    st.title("Convertidor de Imágenes TIFF a JPG/PNG")

    # Preguntar si el usuario quiere convertir una o varias imágenes
    conversion_type = st.radio("¿Qué quieres convertir?", ('Una imagen', 'Varias imágenes (archivo ZIP)'))

    output_format = st.selectbox("Selecciona el formato de salida", ['jpg', 'png'])

    if conversion_type == 'Una imagen':
        # Permitir al usuario subir una imagen TIFF
        uploaded_file = st.file_uploader("Sube una imagen TIFF para convertir", type=["tif", "tiff"])

        if uploaded_file is not None:
            # Mostrar la imagen original
            image = Image.open(uploaded_file)
            st.image(image, caption='Imagen original', use_column_width=True)
            
            st.write("**Archivo cargado correctamente.**")

            # Mostrar botón de conversión solo después de subir la imagen
            if st.button("Convertir"):
                st.write("**Convirtiendo la imagen...**")
                
                # Convertir la imagen
                output_image = convert_image_to_format(image, output_format)
                if output_image is not None:
                    st.success("**Conversión completada!**")
                    
                    # Descargar el archivo convertido
                    st.download_button(
                        label="Descargar imagen convertida",
                        data=output_image.getvalue(),
                        file_name=f"imagen_convertida.{output_format}",
                        mime=f"image/{'jpeg' if output_format == 'jpg' else 'png'}"
                    )

    elif conversion_type == 'Varias imágenes (archivo ZIP)':
        # Permitir al usuario subir un archivo ZIP
        uploaded_zip = st.file_uploader("Sube un archivo ZIP con imágenes TIFF para convertir", type=["zip"])

        if uploaded_zip is not None:
            st.write("**Archivo ZIP cargado correctamente.**")

            # Mostrar botón de conversión solo después de subir el ZIP
            if st.button("Convertir todas las imágenes"):
                st.write("**Convirtiendo las imágenes...**")

                # Procesar las imágenes dentro del ZIP
                output_zip = process_zip_file(uploaded_zip, output_format)
                if output_zip:
                    st.success("**Todas las imágenes han sido convertidas!**")

                    # Descargar el archivo ZIP convertido
                    st.download_button(
                        label="Descargar archivo ZIP con imágenes convertidas",
                        data=output_zip.getvalue(),
                        file_name=f"imagenes_convertidas_{output_format}.zip",
                        mime="application/zip"
                    )

if __name__ == "__main__":
    main()
