import streamlit as st
from PIL import Image
from moviepy.editor import VideoFileClip
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

# Función para convertir video a formato AVI o MP4
def convert_video_to_format(input_video, output_format):
    clip = VideoFileClip(input_video)
    output_file_name = f"video_convertido.{output_format.lower()}"
    
    # Convertir a MP4 o AVI y guardar en un archivo temporal
    if output_format.lower() == 'mp4':
        clip.write_videofile(output_file_name, codec='libx264')
    elif output_format.lower() == 'avi':
        clip.write_videofile(output_file_name, codec='png')  # AVI con compresión PNG
    else:
        st.error(f"Formato {output_format} no soportado.")
    
    clip.close()
    st.success(f"Video convertido y guardado como: {output_file_name}")
    return output_file_name

# Función para procesar múltiples videos desde un archivo ZIP
def process_zip_videos(zip_file, output_format):
    output_zip_bytes = io.BytesIO()

    with zipfile.ZipFile(output_zip_bytes, mode='w') as output_zip:
        with zipfile.ZipFile(zip_file) as z:
            for file_name in z.namelist():
                if file_name.lower().endswith(('.wmp')):
                    with z.open(file_name) as file:
                        video_path = file_name
                        # Convertir el video
                        converted_video = convert_video_to_format(video_path, output_format)
                        if converted_video:
                            output_zip.writestr(f"{os.path.splitext(file_name)[0]}_converted.{output_format}", converted_video)
    
    return output_zip_bytes

# Cargar Font Awesome para los iconos
st.markdown("""
    <link href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0-beta3/css/all.min.css" rel="stylesheet">
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
    .menu-item {
        padding: 15px;
        font-weight: bold;
        border-radius: 8px;
        text-align: left;
        cursor: pointer;
        display: block;
        color: #223848;
        background-color: #f0f2f6;
        text-decoration: none;
        font-size: 16px;
    }
    .menu-item:hover {
        background-color: #009dac;
        color: white;
    }
    .menu-item.selected {
        background-color: #009dac;
        color: white;
        box-shadow: 0px 0px 10px rgba(0,0,0,0.1);
    }
    </style>
    """, unsafe_allow_html=True)

# Función para mostrar el menú con el estado de sesión
def menu_item(label, icon, page):
    active_page = st.session_state.get("page", "Home")
    active_class = "selected" if page == active_page else ""
    if st.sidebar.button(f"{label}", key=page):
        st.session_state.page = page
    return f'<a class="menu-item {active_class}" href="#" onclick="window.location.href=\'#{page}\'"><i class="fa {icon}" style="margin-right:10px;"></i>{label}</a>'

# Función para convertir una imagen TIFF a JPG o PNG
def convert_image_to_format(image, output_format):
    with io.BytesIO() as output_bytes:
        image = image.convert("RGB")  # Convertir a RGB
        image.save(output_bytes, format=output_format.upper())
        return io.BytesIO(output_bytes.getvalue())  # Devolver los bytes de la imagen

# Función para convertir videos
def convert_video_to_format(uploaded_file, output_format):
    try:
        with io.BytesIO(uploaded_file.read()) as input_bytes:
            with open('temp_video.wmp', 'wb') as f:
                f.write(input_bytes.getvalue())
            clip = VideoFileClip('temp_video.wmp')
            output_file = f'temp_video_converted.{output_format}'
            clip.write_videofile(output_file, codec='libx264' if output_format == 'mp4' else 'png')
            with open(output_file, 'rb') as f:
                video_bytes = f.read()
            return io.BytesIO(video_bytes)
    except Exception as e:
        st.error(f"Error al convertir el video: {e}")
        return None

# Página principal
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

# Página para la conversión de imágenes
def show_image_converter():
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
            image = Image.open(uploaded_file)
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

    elif conversion_type == 'Varias imágenes (archivo ZIP)':
        uploaded_zip = st.file_uploader("Sube un archivo ZIP con imágenes TIFF para convertir", type=["zip"])

        if uploaded_zip is not None:
            st.write("**Archivo ZIP cargado correctamente.**")

            if st.button("Convertir todas las imágenes"):
                st.write("**Convirtiendo las imágenes...**")
                # Aquí puedes añadir el proceso para manejar un archivo ZIP
                # output_zip = process_zip_file(uploaded_zip, output_format)
                st.success("**Todas las imágenes han sido convertidas!**")
                # Agregar botón para descargar ZIP resultante

# Página para la conversión de videos
def show_video_converter():
    st.title("Convertidor de WMP a AVI/MP4")
    st.write("""
    ### Convertir Archivos de Video WMP
    Este convertidor te permite transformar archivos de video en formato **WMP** a **AVI** o **MP4**. Puedes seleccionar si quieres convertir un solo video o varios videos subiendo un archivo ZIP.
    """)
    output_format = st.selectbox("Selecciona el formato de salida", ['mp4', 'avi'])

    conversion_type = st.radio("¿Qué quieres convertir?", ('Un solo video', 'Varios videos (archivo ZIP)'))

    if conversion_type == 'Un solo video':
        uploaded_file = st.file_uploader("Sube un archivo WMP para convertir", type=["wmp"])

        if uploaded_file is not None:
            st.write("**Archivo WMP cargado correctamente.**")

            if st.button("Convertir"):
                st.write("**Convirtiendo el archivo WMP...**")
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
                st.write("**Convirtiendo los videos...**")
                # Aquí puedes añadir el proceso para manejar un archivo ZIP de videos

# Página de contacto
def show_contact():
    st.title("Contacto")
    st.write("""
    Si tienes dudas, contacta con alejandro.fernandez-bravo@leroymerlin.es
    """)

# Función para mostrar la página seleccionada
def show_page():
    if st.session_state.get("page") == "Convertidor de Imágenes":
        show_image_converter()
    elif st.session_state.get("page") == "Convertidor de WMP a AVI/MP4":
        show_video_converter()
    elif st.session_state.get("page") == "Contacto":
        show_contact()
    else:
        show_home()

# Página principal de la app
def main():
    if "page" not in st.session_state:
        st.session_state["page"] = "Home"
    
    # Menú lateral
    st.sidebar.markdown(menu_item("Home", "fa-home", "Home"), unsafe_allow_html=True)
    st.sidebar.markdown(menu_item("Convertidor de Imágenes", "fa-image", "Convertidor de Imágenes"), unsafe_allow_html=True)
    st.sidebar.markdown(menu_item("Convertidor de WMP a AVI/MP4", "fa-video", "Convertidor de WMP a AVI/MP4"), unsafe_allow_html=True)
    st.sidebar.markdown(menu_item("Contacto", "fa-envelope", "Contacto"), unsafe_allow_html=True)

    # Mostrar la página actual
    show_page()

if __name__ == "__main__":
    main()
