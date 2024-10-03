import streamlit as st
from PIL import Image
from moviepy.editor import VideoFileClip
import io
import zipfile
import os
import tempfile

# Función para guardar y comprimir la imagen
def save_image(image, output_format):
    img_bytes = io.BytesIO()
    
    # Convertir a RGB si es JPG y guardar la imagen
    if output_format == 'jpg':
        image = image.convert('RGB')  # Convertir a RGB si es JPG
        image.save(img_bytes, format='JPEG', quality=100)  # Preservar máxima calidad para JPG
    else:
        image.save(img_bytes, format=output_format.upper())  # Guardar en PNG sin compresión de calidad
    
    img_bytes.seek(0)
    return img_bytes

# Función para convertir una imagen a formato JPG o PNG
def convert_image_to_format(image, output_format):
    output_format = output_format.lower()  # Asegurar que el formato esté en minúsculas
    
    try:
        output_img = save_image(image, output_format)
        return output_img
    except Exception as e:
        st.error(f"Error durante la conversión de la imagen: {str(e)}")
        return None

# Función para procesar múltiples imágenes desde un archivo ZIP
def process_zip_file(zip_file, output_format):
    output_zip_bytes = io.BytesIO()

    with zipfile.ZipFile(output_zip_bytes, mode='w') as output_zip:
        with zipfile.ZipFile(zip_file) as z:
            for file_name in z.namelist():
                if file_name.lower().endswith(('.tif', '.tiff')):
                    # Abrir cada archivo de imagen dentro del ZIP
                    with z.open(file_name) as file:
                        try:
                            image = Image.open(file)
                            image.load()  # Cargar la imagen para evitar problemas con archivos grandes
                            # Convertir la imagen
                            converted_image = convert_image_to_format(image, output_format)
                            if converted_image:
                                # Guardar la imagen convertida en el nuevo ZIP
                                output_zip.writestr(f"{os.path.splitext(file_name)[0]}_converted.{output_format}", converted_image.getvalue())
                        except Exception as e:
                            st.error(f"Error procesando {file_name}: {str(e)}")
    
    output_zip_bytes.seek(0)
    return output_zip_bytes

# Función para convertir video a formato AVI o MP4
def convert_video_to_format(input_video, output_format):
    try:
        # Crear un archivo temporal para el video de entrada
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wmp') as temp_input:
            temp_input.write(input_video.read())
            temp_input_path = temp_input.name

        # Crear un archivo temporal para el video de salida
        with tempfile.NamedTemporaryFile(delete=False, suffix=f'.{output_format.lower()}') as temp_output:
            output_file_path = temp_output.name

        clip = VideoFileClip(temp_input_path)
        # Preservar la resolución original
        if output_format.lower() == 'mp4':
            # Configurar parámetros para alta calidad
            clip.write_videofile(
                output_file_path,
                codec='libx264',
                audio_codec='aac',
                bitrate='5000k',  # Ajusta según la calidad deseada
                preset='medium',
                threads=4,
                ffmpeg_params=['-crf', '18']  # Valor de crf bajo para mayor calidad
            )
        elif output_format.lower() == 'avi':
            clip.write_videofile(
                output_file_path,
                codec='png',  # AVI con compresión PNG (sin pérdida)
                audio_codec='pcm_s16le',
                threads=4
            )
        else:
            st.error(f"Formato {output_format} no soportado.")
            clip.close()
            os.remove(temp_input_path)
            os.remove(temp_output.name)
            return None
        
        clip.close()
        
        # Leer el archivo de salida
        with open(output_file_path, 'rb') as f:
            converted_video = f.read()
        
        # Limpiar archivos temporales
        os.remove(temp_input_path)
        os.remove(output_file_path)
        
        return io.BytesIO(converted_video)
    
    except Exception as e:
        st.error(f"Error durante la conversión de video: {str(e)}")
        return None

# Función para procesar múltiples videos desde un archivo ZIP
def process_zip_videos(zip_file, output_format):
    output_zip_bytes = io.BytesIO()

    with zipfile.ZipFile(output_zip_bytes, mode='w') as output_zip:
        with zipfile.ZipFile(zip_file) as z:
            for file_name in z.namelist():
                if file_name.lower().endswith(('.wmp', '.wmv', '.wm')):  # Ampliar formatos si es necesario
                    with z.open(file_name) as file:
                        try:
                            converted_video = convert_video_to_format(file, output_format)
                            if converted_video:
                                # Guardar el video convertido en el nuevo ZIP
                                output_zip.writestr(f"{os.path.splitext(file_name)[0]}_converted.{output_format}", converted_video.getvalue())
                        except Exception as e:
                            st.error(f"Error procesando {file_name}: {str(e)}")
    
    output_zip_bytes.seek(0)
    return output_zip_bytes

# Estilos personalizados para la app, el selectbox y el menú lateral con íconos
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stButton>button {
        background-color: #009dac;
        color: white;
        border-radius: 8px;
    }
    .stButton>button:hover {
        background-color: #007b8b;
    }
    .css-1aumxhk {  /* Sidebar title style */
        color: #223848;
    }
    h1 {
        color: #009dac;
    }
    h2 {
        color: #223848;
    }

    /* Estilo para el sidebar */
    .css-1d391kg {  
        background-color: #ffffff !important;
        border-radius: 15px;
        padding: 10px;
    }
    .css-qbe2hs {  
        background-color: #ff6b6b !important;
        color: white;
        border-radius: 10px;
    }
    .css-1d3k3q9 a {
        color: #223848 !important;
        text-decoration: none;
    }
    .css-1d3k3q9 a:hover {
        color: #009dac !important;
    }

    /* Estilos para el selectbox (caja de selección) */
    .stSelectbox>div>div {
        background-color: white;  /* Fondo blanco */
        color: #223848;  /* Color del texto */
        border-radius: 5px;
        border: 1px solid #ff6b6b;
    }
    .stSelectbox>div>div:hover {
        background-color: #009dac;  /* Cambia al color corporativo */
        color: white;  /* Texto en blanco al seleccionar */
    }
    </style>
    """, unsafe_allow_html=True)

# Página de inicio con explicación
def show_home():
    st.title("Bienvenido al Convertidor de Imágenes y Videos")
    st.write("""
    ### ¿Qué puedes hacer con esta herramienta?
    Esta aplicación te permite realizar las siguientes conversiones:
    - Convertir **imágenes TIFF** a **JPG** o **PNG**.
    - Convertir archivos de video **WMP** a **AVI** o **MP4**.
    
    ### ¿Cómo funciona?
    1. Selecciona el tipo de conversión que deseas realizar.
    2. Sube el archivo que quieras convertir, o varios archivos en un ZIP.
    3. Descarga el archivo convertido cuando el proceso haya terminado.
    
    ¡Es simple y rápido!
    """)

# Página de contacto
def show_contact():
    st.title("Contacto")
    st.write("""
    ¿Tienes alguna otra duda adicional?
    
    Contacta con alejandro.fernandez-bravo@leroymerlin.es
    """)

# Función principal de la app
def main():
    st.sidebar.title("📋 Main Menu")
    # Menú lateral con opciones y emoticonos
    option = st.sidebar.radio(
        "",
        ("🏠 Home", "🖼️ Convertidor de Imágenes", "🎥 Convertidor de WMP a AVI/MP4", "📧 Contacto")
    )

    if option == "🏠 Home":
        show_home()

    elif option == "🖼️ Convertidor de Imágenes":
        st.title("Convertidor de Imágenes")
        st.write("""
        ### Convertir Imágenes TIFF
        Este convertidor permite transformar imágenes en formato **TIFF** a los formatos **JPG** o **PNG**. Puedes seleccionar si quieres convertir una sola imagen o varias imágenes subiendo un archivo ZIP.
        """)
        output_format = st.selectbox("Selecciona el formato de salida", ['jpg', 'png'])

        # Preguntar si el usuario quiere convertir una o varias imágenes
        conversion_type = st.radio("¿Qué quieres convertir?", ('Una imagen', 'Varias imágenes (archivo ZIP)'))

        if conversion_type == 'Una imagen':
            uploaded_file = st.file_uploader("Sube una imagen TIFF para convertir", type=["tif", "tiff"])

            if uploaded_file is not None:
                try:
                    image = Image.open(uploaded_file)
                    image.load()  # Cargar la imagen para asegurar que está completamente cargada
                    st.image(image, caption='Imagen original', use_column_width=True)
                    st.write("**Archivo cargado correctamente.**")

                    if st.button("Convertir"):
                        st.write("**Convirtiendo la imagen...**")
                        output_image = convert_image_to_format(image, output_format)
                        if output_image is not None:
                            st.success("**Conversión completada!**")
                            st.download_button(
                                label="Descargar imagen convertida",
                                data=output_image.getvalue(),
                                file_name=f"imagen_convertida.{output_format}",
                                mime=f"image/{'jpeg' if output_format == 'jpg' else 'png'}"
                            )
                except Exception as e:
                    st.error(f"Error al cargar la imagen: {str(e)}")

        elif conversion_type == 'Varias imágenes (archivo ZIP)':
            uploaded_zip = st.file_uploader("Sube un archivo ZIP con imágenes TIFF para convertir", type=["zip"])

            if uploaded_zip is not None:
                st.write("**Archivo ZIP cargado correctamente.**")

                if st.button("Convertir todas las imágenes"):
                    with st.spinner("Convirtiendo las imágenes..."):
                        output_zip = process_zip_file(uploaded_zip, output_format)
                        if output_zip:
                            st.success("**Todas las imágenes han sido convertidas!**")
                            st.download_button(
                                label="Descargar archivo ZIP con imágenes convertidas",
                                data=output_zip.getvalue(),
                                file_name=f"imagenes_convertidas_{output_format}.zip",
                                mime="application/zip"
                            )

    elif option == "🎥 Convertidor de WMP a AVI/MP4":
        st.title("Convertidor de WMP a AVI/MP4")
        st.write("""
        ### Convertir Archivos de Video WMP
        Este convertidor te permite transformar archivos de video en formato **WMP** a **AVI** o **MP4**. Puedes seleccionar si quieres convertir un solo video o varios videos subiendo un archivo ZIP.
        """)
        output_format = st.selectbox("Selecciona el formato de salida", ['mp4', 'avi'])

        # Preguntar si el usuario quiere convertir uno o varios videos
        conversion_type = st.radio("¿Qué quieres convertir?", ('Un solo video', 'Varios videos (archivo ZIP)'))

        if conversion_type == 'Un solo video':
            uploaded_file = st.file_uploader("Sube un archivo WMP para convertir", type=["wmp", "wmv", "wm"])

            if uploaded_file is not None:
                st.write("**Archivo WMP cargado correctamente.**")

                if st.button("Convertir"):
                    with st.spinner("Convirtiendo el archivo WMP..."):
                        output_video = convert_video_to_format(uploaded_file, output_format)
                        if output_video:
                            st.success("**Conversión completada!**")
                            st.download_button(
                                label="Descargar video convertido",
                                data=output_video.getvalue(),
                                file_name=f"video_convertido.{output_format}",
                                mime=f"video/{output_format}"
                            )

        elif conversion_type == 'Varios videos (archivo ZIP)':
            uploaded_zip = st.file_uploader("Sube un archivo ZIP con videos WMP para convertir", type=["zip"])

            if uploaded_zip is not None:
                st.write("**Archivo ZIP cargado correctamente.**")

                if st.button("Convertir todos los videos"):
                    with st.spinner("Convirtiendo los videos..."):
                        # Procesar los videos dentro del ZIP
                        output_zip = process_zip_videos(uploaded_zip, output_format)
                        if output_zip:
                            st.success("**Todos los videos han sido convertidos!**")
                            st.download_button(
                                label="Descargar archivo ZIP con videos convertidos",
                                data=output_zip.getvalue(),
                                file_name=f"videos_convertidos_{output_format}.zip",
                                mime="application/zip"
                            )

    elif option == "📧 Contacto":
        show_contact()

if __name__ == "__main__":
    main()
