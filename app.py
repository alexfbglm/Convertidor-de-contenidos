import streamlit as st
from PIL import Image
import io

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

# Función para convertir la imagen a formato JPG o PNG
def convert_image_to_format(image, output_format):
    output_format = output_format.lower()  # Asegurar que el formato esté en minúsculas
    
    try:
        output_img = save_image(image, output_format)
        return output_img
    except Exception as e:
        st.error(f"Error durante la compresión de la imagen: {str(e)}")
        return None

# Streamlit App
def main():
    st.title("Convertidor de Imágenes TIFF a JPG/PNG")

    # Permitir al usuario subir un archivo TIFF
    uploaded_file = st.file_uploader("Sube una imagen TIFF para convertir", type=["tif", "tiff"])

    if uploaded_file is not None:
        # Mostrar la imagen original
        image = Image.open(uploaded_file)
        st.image(image, caption='Imagen original', use_column_width=True)
        
        st.write("**Archivo cargado correctamente.**")

        # Seleccionar formato de salida
        output_format = st.selectbox("Selecciona el formato de salida", ['jpg', 'png'])

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

if __name__ == "__main__":
    main()
