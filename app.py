import streamlit as st
import zipfile
import tempfile
import re
import io
from pathlib import Path
from PIL import Image

st.set_page_config(
    page_title="PNG to JPG in DOCX",
    page_icon="🖼️",
    layout="centered"
)

st.title("🖼️ PNG → JPG inside DOCX")
st.markdown("Upload your Word document and get it back with all PNG images converted to JPG — smaller file, same layout.")

st.divider()

uploaded = st.file_uploader("📄 Upload your .docx file", type=["docx"])
quality = st.slider("JPG Quality", min_value=50, max_value=100, value=92, help="92 is best balance of quality and size")

def convert_docx(file_bytes, quality):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        extract_dir = tmpdir / "extracted"
        input_path = tmpdir / "input.docx"
        output_path = tmpdir / "output.docx"

        input_path.write_bytes(file_bytes)

        with zipfile.ZipFile(input_path, 'r') as z:
            z.extractall(extract_dir)

        media_dir = extract_dir / "word" / "media"
        rels_path = extract_dir / "word" / "_rels" / "document.xml.rels"
        content_types_path = extract_dir / "[Content_Types].xml"

        if not media_dir.exists():
            return None, 0, 0

        png_files = list(media_dir.glob("*.png")) + list(media_dir.glob("*.PNG"))

        if not png_files:
            return None, 0, 0

        rename_map = {}
        converted_count = 0

        progress = st.progress(0, text="Converting images...")

        for i, png_path in enumerate(png_files):
            jpg_name = png_path.stem + ".jpg"
            jpg_path = media_dir / jpg_name

            try:
                with Image.open(png_path) as img:
                    if img.mode in ("RGBA", "P", "LA"):
                        background = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        background.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                        img = background
                    elif img.mode != "RGB":
                        img = img.convert("RGB")

                    img.save(jpg_path, "JPEG", quality=quality, optimize=True)

                rename_map[png_path.name] = jpg_name
                png_path.unlink()
                converted_count += 1

            except Exception as e:
                st.warning(f"Could not convert {png_path.name}: {e}")

            progress.progress((i + 1) / len(png_files), text=f"Converting {i+1} of {len(png_files)}...")

        progress.empty()

        # Update relationships file
        if rels_path.exists() and rename_map:
            rels_content = rels_path.read_text(encoding="utf-8")
            for old_name, new_name in rename_map.items():
                rels_content = rels_content.replace(
                    f'Target="media/{old_name}"',
                    f'Target="media/{new_name}"'
                )
            rels_path.write_text(rels_content, encoding="utf-8")

        # Update content types
        if content_types_path.exists():
            ct_content = content_types_path.read_text(encoding="utf-8")
            if 'Extension="jpeg"' not in ct_content and 'Extension="jpg"' not in ct_content:
                ct_content = ct_content.replace(
                    '</Types>',
                    '  <Default Extension="jpeg" ContentType="image/jpeg"/>\n</Types>'
                )
            for old_name, new_name in rename_map.items():
                ct_content = ct_content.replace(old_name, new_name)
            remaining_pngs = list(media_dir.glob("*.png")) + list(media_dir.glob("*.PNG"))
            if not remaining_pngs and 'Extension="png"' in ct_content:
                ct_content = re.sub(r'\s*<Default Extension="[Pp][Nn][Gg]"[^/]*/>', '', ct_content)
            content_types_path.write_text(ct_content, encoding="utf-8")

        # Update document.xml
        doc_xml_path = extract_dir / "word" / "document.xml"
        if doc_xml_path.exists() and rename_map:
            doc_content = doc_xml_path.read_text(encoding="utf-8")
            for old_name, new_name in rename_map.items():
                doc_content = doc_content.replace(old_name, new_name)
            doc_xml_path.write_text(doc_content, encoding="utf-8")

        # Repack
        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for file in extract_dir.rglob("*"):
                if file.is_file():
                    arcname = file.relative_to(extract_dir)
                    zout.write(file, arcname)

        return output_path.read_bytes(), len(png_files), converted_count


if uploaded:
    file_bytes = uploaded.read()
    original_size_kb = len(file_bytes) / 1024

    st.info(f"📎 **{uploaded.name}** — {original_size_kb:.0f} KB uploaded")

    if st.button("⚡ Convert Now", type="primary", use_container_width=True):
        with st.spinner("Processing your document..."):
            result_bytes, total_pngs, converted = convert_docx(file_bytes, quality)

        if result_bytes is None:
            st.warning("⚠️ No PNG images found in this document.")
        else:
            new_size_kb = len(result_bytes) / 1024
            saving = ((original_size_kb - new_size_kb) / original_size_kb) * 100

            st.success(f"✅ Done! Converted **{converted}** PNG image(s) to JPG")

            col1, col2, col3 = st.columns(3)
            col1.metric("Images Converted", converted)
            col2.metric("Original Size", f"{original_size_kb:.0f} KB")
            col3.metric("New Size", f"{new_size_kb:.0f} KB", delta=f"{saving:.0f}% smaller" if saving > 0 else f"{abs(saving):.0f}% larger")

            output_filename = uploaded.name.replace(".docx", "_converted.docx")
            st.download_button(
                label="⬇️ Download Converted DOCX",
                data=result_bytes,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
                type="primary"
            )

st.divider()
st.caption("All processing happens on the server. Files are never stored.")
