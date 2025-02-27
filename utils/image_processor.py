import io
from PIL import Image
import streamlit as st

def process_upload_image(uploaded_file, keep_original=False, max_file_size=50*1024*1024):
    """
    Process uploaded image with comprehensive error handling
    If keep_original is True, maintains original size and quality
    """
    try:
        # Initial validation
        if uploaded_file is None:
            return None, "Nessun file caricato"

        file_size = len(uploaded_file.getvalue())
        if file_size > max_file_size:
            return None, f"File troppo grande ({file_size/1024/1024:.1f}MB). Massimo consentito: 50MB"

        # Read image
        image_data = uploaded_file.read()
        image = Image.open(io.BytesIO(image_data))

        # Convert to RGBA if needed
        if image.mode not in ('RGBA', 'RGB'):
            image = image.convert('RGBA')

        if keep_original:
            # Keep original size and quality
            output = io.BytesIO()
            image.save(output, 
                      format='PNG',
                      quality=100)  # Maximum quality

            processed_size = len(output.getvalue())
            st.info(f"""
            Informazioni immagine:
            - Dimensioni: {image.size}
            - Dimensione file: {file_size/1024:.1f}KB
            """)

            return output.getvalue(), None

        else:
            # For non-branding images, maintain existing behavior
            target_size = (128, 128)
            aspect = image.width / image.height

            if aspect > 1:
                new_size = (target_size[0], int(target_size[1] / aspect))
            else:
                new_size = (int(target_size[0] * aspect), target_size[1])

            image = image.resize(new_size, Image.Resampling.LANCZOS)
            final_image = Image.new('RGBA', target_size, (255, 255, 255, 0))
            paste_pos = ((target_size[0] - new_size[0]) // 2,
                        (target_size[1] - new_size[1]) // 2)
            final_image.paste(image, paste_pos)

            output = io.BytesIO()
            final_image.save(output, format='PNG')
            return output.getvalue(), None

    except Exception as e:
        error_msg = f"Errore nel processare l'immagine: {str(e)}"
        st.error(error_msg)
        return None, error_msg