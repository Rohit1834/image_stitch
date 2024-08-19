import streamlit as st
import cv2
import stitch
import utils
import timeit
import os
import io
import cv2
import numpy as np  # Add this import statement
import features

st.title("Image Stitching")

uploaded_files = st.file_uploader(
    "Upload your images (left to right)",
    accept_multiple_files=True,
    type=["jpg", "jpeg", "png"],
)

resize_option = st.checkbox("Resize images (reduce resolution)")

if uploaded_files:
    # Create a temporary directory to store the uploaded images
    temp_dir = "uploads"
    os.makedirs(temp_dir, exist_ok=True)

    # Save uploaded files to the temporary directory
    image_paths = []
    for i, uploaded_file in enumerate(uploaded_files):
        file_path = os.path.join(temp_dir, f"image_{i}.jpg")
        with open(file_path, "wb") as f:
            f.write(uploaded_file.getvalue())
        image_paths.append(file_path)

    # Run image stitching
    try:
        print("Processing....")
        start = timeit.default_timer()
        list_images = utils.loadImages(temp_dir, resize_option)
        panorama = stitch.multiStitching(list_images)
        stop = timeit.default_timer()
        print("Complete!")
        print("Execution time: ", stop - start)

        # Ensure pixel values are within the valid range (0-255)
        panorama = np.clip(panorama, 0, 255).astype(np.uint8) 

        # Display or download options
        display_panorama = st.checkbox("Display Stitched Panorama")
        download_panorama = st.checkbox("Download Stitched Panorama")

        if display_panorama:
            st.image(panorama, caption="Stitched Panorama", width=None)

        if download_panorama:
            # Convert the image to bytes for download
            buf = io.BytesIO()
            cv2.imwrite(buf, panorama)
            buf.seek(0)
            st.download_button(
                label="Download Stitched Panorama",
                data=buf,
                file_name="panorama.jpg",
                mime="image/jpeg",
            )

        # Clean up the temporary directory (only if stitching was successful and empty)
        if not os.listdir(temp_dir):
            os.rmdir(temp_dir)
    except Exception as e:
        st.error(f"Error during stitching: {e}")

    # Clean up the temporary directory (even if an error occurred)
    try:
        os.rmdir(temp_dir)  # Try to remove the directory even if it's not empty
    except OSError:
        pass  # Ignore the error if the directory is not empty

# Add some information about the app
st.write(
    "This app stitches multiple images together to create a panoramic image. "
    "The images must be uploaded in left-to-right order."
)