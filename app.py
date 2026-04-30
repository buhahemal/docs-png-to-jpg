import streamlit as st
import zipfile
import tempfile
import re
import io
from pathlib import Path
from PIL import Image

st.set_page_config(
    page_title="PNG → JPG Converter",
    page_icon="🖼️",
    layout="centered"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

/* Global reset & font */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}

/* Page background */
.stApp {
    background: #0f0f13;
}

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }

/* Main content area */
.block-container {
    padding: 3rem 2rem 4rem !important;
    max-width: 680px !important;
}

/* ── Hero section ── */
.hero {
    text-align: center;
    padding: 3rem 0 2rem;
    border-bottom: 1px solid rgba(255,255,255,0.06);
    margin-bottom: 2.5rem;
}
.hero-badge {
    display: inline-block;
    background: rgba(99, 102, 241, 0.15);
    color: #a5b4fc;
    font-family: 'DM Mono', monospace;
    font-size: 11px;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 100px;
    border: 1px solid rgba(99, 102, 241, 0.25);
    margin-bottom: 1.25rem;
}
.hero-title {
    font-size: 2.6rem;
    font-weight: 600;
    color: #f1f1f5;
    letter-spacing: -0.03em;
    line-height: 1.15;
    margin: 0 0 0.75rem;
}
.hero-title span {
    color: #818cf8;
}
.hero-subtitle {
    font-size: 1rem;
    color: #7a7a92;
    line-height: 1.6;
    max-width: 440px;
    margin: 0 auto;
}

/* ── Card wrapper ── */
.card {
    background: #16161e;
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 16px;
    padding: 1.75rem 1.75rem;
    margin-bottom: 1.25rem;
}
.card-label {
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: #55556a;
    margin-bottom: 0.6rem;
}

/* ── File uploader ── */
[data-testid="stFileUploader"] {
    border-radius: 12px;
    overflow: hidden;
}
[data-testid="stFileUploader"] section {
    background: #0f0f13 !important;
    border: 1.5px dashed rgba(99, 102, 241, 0.3) !important;
    border-radius: 12px !important;
    padding: 1.5rem !important;
    transition: border-color 0.2s;
}
[data-testid="stFileUploader"] section:hover {
    border-color: rgba(99, 102, 241, 0.6) !important;
}
[data-testid="stFileUploader"] section > div {
    gap: 0.5rem !important;
}
[data-testid="stFileUploader"] p,
[data-testid="stFileUploader"] small,
[data-testid="stFileUploader"] span:not([data-testid="baseButton-primary"] span) {
    color: #7a7a92 !important;
    font-family: 'DM Sans', sans-serif !important;
}
/* hide the duplicated label that appears above the drop zone */
[data-testid="stFileUploader"] > label {
    display: none !important;
}

/* ── Slider ── */
[data-testid="stSlider"] > div > div > div {
    background: #818cf8 !important;
}
[data-testid="stSlider"] label {
    color: #a1a1b8 !important;
    font-size: 0.85rem !important;
}
[data-testid="stSlider"] [data-testid="stMarkdownContainer"] p {
    color: #818cf8 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* ── Primary button ── */
[data-testid="baseButton-primary"] {
    background: linear-gradient(135deg, #6366f1 0%, #818cf8 100%) !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.95rem !important;
    letter-spacing: 0.01em !important;
    color: #fff !important;
    padding: 0.6rem 1.5rem !important;
    box-shadow: 0 4px 20px rgba(99, 102, 241, 0.3) !important;
    transition: all 0.2s !important;
}
[data-testid="baseButton-primary"]:hover {
    box-shadow: 0 6px 28px rgba(99, 102, 241, 0.45) !important;
    transform: translateY(-1px);
}

/* ── Secondary button (download) ── */
[data-testid="baseButton-secondary"] {
    background: rgba(99, 102, 241, 0.1) !important;
    border: 1px solid rgba(99, 102, 241, 0.35) !important;
    border-radius: 10px !important;
    font-family: 'DM Sans', sans-serif !important;
    font-weight: 500 !important;
    color: #a5b4fc !important;
    transition: all 0.2s !important;
}
[data-testid="baseButton-secondary"]:hover {
    background: rgba(99, 102, 241, 0.18) !important;
    border-color: rgba(99, 102, 241, 0.55) !important;
}

/* ── Metric cards ── */
[data-testid="stMetric"] {
    background: #0f0f13;
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 12px;
    padding: 1rem 1.1rem !important;
}
[data-testid="stMetricLabel"] p {
    color: #55556a !important;
    font-size: 11px !important;
    font-weight: 600 !important;
    text-transform: uppercase !important;
    letter-spacing: 0.08em !important;
}
[data-testid="stMetricValue"] {
    color: #f1f1f5 !important;
    font-size: 1.5rem !important;
    font-weight: 500 !important;
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stMetricDelta"] svg { display: none !important; }
[data-testid="stMetricDelta"] span {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
}

/* ── Info / Warning / Success ── */
[data-testid="stAlert"] {
    border-radius: 10px !important;
    border-left-width: 3px !important;
    font-size: 0.88rem !important;
}

/* ── Progress bar ── */
[data-testid="stProgressBar"] > div > div {
    background: linear-gradient(90deg, #6366f1, #a5b4fc) !important;
}

/* ── Footer note ── */
.footer-note {
    text-align: center;
    color: #3a3a50;
    font-size: 0.75rem;
    margin-top: 2.5rem;
    letter-spacing: 0.02em;
}

/* ── Info pill ── */
.info-pill {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 8px;
    padding: 8px 14px;
    font-size: 0.85rem;
    color: #7a7a92;
    margin-bottom: 1rem;
    width: 100%;
}
.info-pill strong {
    color: #c4c4d8;
}

/* ── Divider ── */
hr {
    border-color: rgba(255,255,255,0.05) !important;
    margin: 1.5rem 0 !important;
}

/* ── Columns gap ── */
[data-testid="column"] {
    padding: 0 6px !important;
}
</style>
""", unsafe_allow_html=True)

# ── Hero ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero">
    <div class="hero-badge">DOCX Image Optimizer</div>
    <h1 class="hero-title">PNG → <span>JPG</span> inside DOCX</h1>
    <p class="hero-subtitle">
        Drop your Word document and we'll swap every PNG for a leaner JPG —
        same layout, smaller file, instant download.
    </p>
</div>
""", unsafe_allow_html=True)

# ── Upload card ──────────────────────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-label">📄 Your document</div>', unsafe_allow_html=True)
uploaded = st.file_uploader(
    label="Upload your .docx file",
    type=["docx"],
    label_visibility="hidden"
)
st.markdown('</div>', unsafe_allow_html=True)

# ── Quality card ─────────────────────────────────────────────────────────────
st.markdown('<div class="card"><div class="card-label">🎚 JPG Quality</div>', unsafe_allow_html=True)
quality = st.slider(
    "Quality",
    min_value=50,
    max_value=100,
    value=92,
    help="92 gives the best balance of quality and file size.",
    label_visibility="collapsed"
)
col_l, col_r = st.columns(2)
col_l.caption("50 — Smaller file, lower quality")
col_r.markdown(f"<p style='text-align:right;color:#818cf8;font-family:DM Mono,monospace;font-size:0.8rem;'>Selected: {quality}</p>", unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# ── Core conversion function ─────────────────────────────────────────────────
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
        progress = st.progress(0, text="Converting images…")

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
            progress.progress((i + 1) / len(png_files), text=f"Converting {i+1} of {len(png_files)}…")

        progress.empty()

        if rels_path.exists() and rename_map:
            rels_content = rels_path.read_text(encoding="utf-8")
            for old_name, new_name in rename_map.items():
                rels_content = rels_content.replace(f'Target="media/{old_name}"', f'Target="media/{new_name}"')
            rels_path.write_text(rels_content, encoding="utf-8")

        if content_types_path.exists():
            ct_content = content_types_path.read_text(encoding="utf-8")
            if 'Extension="jpeg"' not in ct_content and 'Extension="jpg"' not in ct_content:
                ct_content = ct_content.replace('</Types>', '  <Default Extension="jpeg" ContentType="image/jpeg"/>\n</Types>')
            for old_name, new_name in rename_map.items():
                ct_content = ct_content.replace(old_name, new_name)
            remaining_pngs = list(media_dir.glob("*.png")) + list(media_dir.glob("*.PNG"))
            if not remaining_pngs and 'Extension="png"' in ct_content:
                ct_content = re.sub(r'\s*<Default Extension="[Pp][Nn][Gg]"[^/]*/>', '', ct_content)
            content_types_path.write_text(ct_content, encoding="utf-8")

        doc_xml_path = extract_dir / "word" / "document.xml"
        if doc_xml_path.exists() and rename_map:
            doc_content = doc_xml_path.read_text(encoding="utf-8")
            for old_name, new_name in rename_map.items():
                doc_content = doc_content.replace(old_name, new_name)
            doc_xml_path.write_text(doc_content, encoding="utf-8")

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for file in extract_dir.rglob("*"):
                if file.is_file():
                    zout.write(file, file.relative_to(extract_dir))

        return output_path.read_bytes(), len(png_files), converted_count


# ── Actions ──────────────────────────────────────────────────────────────────
if uploaded:
    file_bytes = uploaded.read()
    original_size_kb = len(file_bytes) / 1024

    st.markdown(f"""
    <div class="info-pill">
        <span>📎</span>
        <strong>{uploaded.name}</strong>
        &nbsp;·&nbsp; {original_size_kb:.0f} KB
    </div>
    """, unsafe_allow_html=True)

    if st.button("⚡  Convert Now", type="primary", use_container_width=True):
        with st.spinner("Working on it…"):
            result_bytes, total_pngs, converted = convert_docx(file_bytes, quality)

        if result_bytes is None:
            st.warning("No PNG images were found inside this document.")
        else:
            new_size_kb = len(result_bytes) / 1024
            saving = ((original_size_kb - new_size_kb) / original_size_kb) * 100
            delta_label = f"↓ {saving:.0f}% smaller" if saving > 0 else f"↑ {abs(saving):.0f}% larger"

            st.success(f"Done! Converted **{converted}** PNG image(s) to JPG.")

            c1, c2, c3 = st.columns(3)
            c1.metric("Converted", str(converted))
            c2.metric("Before", f"{original_size_kb:.0f} KB")
            c3.metric("After", f"{new_size_kb:.0f} KB", delta=delta_label)

            st.markdown("<br>", unsafe_allow_html=True)

            output_filename = uploaded.name.replace(".docx", "_converted.docx")
            st.download_button(
                label="⬇  Download Converted DOCX",
                data=result_bytes,
                file_name=output_filename,
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                use_container_width=True,
            )

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-note">
    All processing is done on the server in a temporary directory.<br>
    Your files are never stored or logged.
</div>
""", unsafe_allow_html=True)
