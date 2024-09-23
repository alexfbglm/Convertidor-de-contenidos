import streamlit as st
from moviepy.editor import VideoFileClip
import io
import zipfile
import os

# Función para convertir video a formato AVI o MP4
def convert_video_to_format(input_video, output_format):
    clip = VideoFileClip(input_video)
    output_bytes = io.BytesIO()
    
    output_file_name = f"video_convertido.{output_format.lower()}"
    
    # Convertir a MP4 o AVI y guardar en un buffer de memoria
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

# Streamlit App
def main():
    st.title("Convertidor")

    # Panel lateral para seleccionar el tipo de conversión
    conversion_option = st.sidebar.selectbox(
        "Selecciona una opción",
        ("Convertidor de Imágenes", "Convertidor de WMP a AVI/MP4")
    )

    if conversion_option == "Convertidor de Imágenes":
        # Opción de Convertidor de Imágenes (ya implementada)
        st.write("Convertidor de imágenes implementado previamente")
        # Aquí seguiríamos con el código ya implementado previamente para convertir imágenes

    elif conversion_option == "Convertidor de WMP a AVI/MP4":
        output_format = st.selectbox("Selecciona el formato de salida", ['mp4', 'avi'])

        # Preguntar si el usuario quiere convertir uno o varios videos
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

if __name__ == "__main__":
    main()
