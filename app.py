import streamlit as st
import zipfile
import tempfile
import re
from pathlib import Path
from PIL import Image

st.set_page_config(
    page_title="DOCX Converter",
    page_icon="🖼️",
    layout="wide"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
}

.stApp {
    background-image: url('https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1800&q=80');
    background-size: cover;
    background-position: center center;
    background-attachment: fixed;
    min-height: 100vh;
}

.stApp::before {
    content: '';
    position: fixed;
    inset: 0;
    background: linear-gradient(135deg,
        rgba(8,18,38,0.58) 0%,
        rgba(10,25,50,0.32) 55%,
        rgba(5,15,30,0.52) 100%);
    pointer-events: none;
    z-index: 0;
}

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

section.main > div { padding: 0 !important; }
.element-container { margin: 0 !important; }
div[data-testid="stVerticalBlock"] > div { padding-top: 0 !important; padding-bottom: 0 !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* ── Hero left ── */
.hero-wrap {
    position: fixed;
    bottom: 110px;
    left: 72px;
    z-index: 2;
}
.hero-title {
    font-size: clamp(3rem, 5vw, 4.5rem);
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.035em;
    line-height: 1.06;
    margin-bottom: 14px;
    text-shadow: 0 4px 40px rgba(0,0,0,0.28);
}
.hero-sub {
    font-size: 0.95rem;
    font-weight: 300;
    color: rgba(255,255,255,0.55);
    line-height: 1.55;
}

/* ── Quality label display (cosmetic) ── */
.quality-bar {
    display: flex;
    align-items: center;
    gap: 22px;
}
.qlabel {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: rgba(255,255,255,0.38);
    text-transform: uppercase;
}
.qopts { display: flex; gap: 18px; }
.qopt {
    font-size: 0.85rem;
    font-weight: 400;
    color: rgba(255,255,255,0.35);
    cursor: pointer;
}
.qopt.active { font-weight: 700; color: #ffffff; }

/* ── Result cards ── */
.result-panel {
    position: fixed;
    top: 50%;
    right: 64px;
    transform: translateY(-50%);
    z-index: 8;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 10px;
}
.rcard {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 14px;
    padding: 13px 20px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    text-align: right;
    min-width: 150px;
}
.rlabel {
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.38);
    margin-bottom: 4px;
}
.rval {
    font-size: 1.25rem;
    font-weight: 600;
    color: #fff;
    letter-spacing: -0.02em;
}
.rdelta { font-size: 0.72rem; color: rgba(255,255,255,0.52); margin-top: 2px; }

/* ── Bottom bar ── */
.bottom-bar {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    border-top: 1px solid rgba(255,255,255,0.1);
    padding: 16px 72px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 20;
    background: rgba(0,0,0,0.12);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}
.footer-txt { font-size: 0.78rem; color: rgba(255,255,255,0.28); font-weight: 300; }

/* ── Streamlit widget overrides ── */

/* File uploader */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.12) !important;
    border: 1.5px solid rgba(255,255,255,0.28) !important;
    border-radius: 50px !important;
    padding: 10px 24px !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
    min-height: unset !important;
    transition: all 0.2s !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    background: rgba(255,255,255,0.18) !important;
    border-color: rgba(255,255,255,0.45) !important;
}
[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span {
    color: rgba(255,255,255,0.88) !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] svg { display: none !important; }
[data-testid="stFileUploaderDropzone"] button {
    background: rgba(255,255,255,0.14) !important;
    border: 1px solid rgba(255,255,255,0.28) !important;
    border-radius: 50px !important;
    color: #fff !important;
    font-size: 0.76rem !important;
    padding: 4px 14px !important;
}
[data-testid="stFileUploaderFileName"] {
    color: rgba(255,255,255,0.88) !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
}

/* Label for file uploader (hidden visually but accessible) */
[data-testid="stFileUploader"] label {
    position: absolute !important;
    width: 1px !important;
    height: 1px !important;
    overflow: hidden !important;
    clip: rect(0,0,0,0) !important;
    white-space: nowrap !important;
}

/* Buttons — glass pill */
[data-testid="stButton"] > button {
    background: rgba(255,255,255,0.13) !important;
    border: 1.5px solid rgba(255,255,255,0.28) !important;
    border-radius: 50px !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    padding: 10px 22px !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
    transition: all 0.18s !important;
    white-space: nowrap !important;
    width: auto !important;
    min-width: unset !important;
}
[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.22) !important;
    border-color: rgba(255,255,255,0.5) !important;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.13) !important;
    border: 1.5px solid rgba(255,255,255,0.28) !important;
    border-radius: 50px !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    padding: 10px 22px !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
    transition: all 0.18s !important;
    width: auto !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(255,255,255,0.22) !important;
}

/* Slider */
[data-testid="stSlider"] label {
    color: rgba(255,255,255,0.45) !important;
    font-size: 0.72rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}
[data-testid="stSlider"] [data-testid="stTickBar"] { display: none !important; }
div[data-baseweb="slider"] div[role="slider"] {
    background-color: #ffffff !important;
    border-color: #ffffff !important;
}

/* Progress */
[data-testid="stProgressBar"] > div {
    background: rgba(255,255,255,0.18) !important;
    border-radius: 100px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: rgba(255,255,255,0.7) !important;
    border-radius: 100px !important;
}

/* Alerts */
[data-testid="stAlert"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.15) !important;
    border-radius: 14px !important;
    color: rgba(255,255,255,0.8) !important;
    backdrop-filter: blur(16px) !important;
}

/* Spinner */
.stSpinner > div {
    border-color: rgba(255,255,255,0.65) rgba(255,255,255,0.12) rgba(255,255,255,0.12) !important;
}

/* Columns spacing */
[data-testid="stColumns"] { gap: 10px !important; }
</style>
""", unsafe_allow_html=True)


# ── Quality config ──
# High = 95, Medium = 70–94, Low = < 70
QUALITY_OPTIONS = {
    "High":   95,
    "Medium": 82,
    "Low":    60,
}

if "quality_label" not in st.session_state:
    st.session_state.quality_label = "High"
if "result" not in st.session_state:
    st.session_state.result = None
if "file_bytes" not in st.session_state:
    st.session_state.file_bytes = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None


def quality_label_from_value(v):
    """Derive label from numeric slider value."""
    if v >= 95:
        return "High"
    elif v >= 70:
        return "Medium"
    else:
        return "Low"


# ── Hero ──
st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">DOCX<br>Converter</div>
    <div class="hero-sub">Convert PNG images inside Word documents<br>to JPG — smaller file, same layout.</div>
</div>
""", unsafe_allow_html=True)


# ── Quality pills HTML (cosmetic display) ──
q_html = '<div style="position:fixed;top:52px;right:64px;z-index:10;display:flex;flex-direction:column;align-items:flex-end;gap:16px;"><div class="quality-bar"><span class="qlabel">Quality</span><div class="qopts">'
for opt in ["High", "Medium", "Low"]:
    cls = "qopt active" if opt == st.session_state.quality_label else "qopt"
    q_html += f'<span class="{cls}">{opt}</span>'
q_html += '</div></div></div>'
st.markdown(q_html, unsafe_allow_html=True)


# ── Right-side controls column ──
_, right_col = st.columns([2, 1])

with right_col:
    st.markdown('<div style="display:flex;flex-direction:column;align-items:flex-end;gap:14px;padding:48px 0 0;">', unsafe_allow_html=True)

    # Quality preset buttons
    q_cols = st.columns(3)
    for i, label in enumerate(["High", "Medium", "Low"]):
        with q_cols[i]:
            if st.button(label, key=f"q_{label}"):
                st.session_state.quality_label = label
                st.session_state.result = None
                st.rerun()

    # Slider — synced to quality label, but also manually adjustable
    # Shows current label's value as default; label updates if user drags
    current_default = QUALITY_OPTIONS[st.session_state.quality_label]

    quality = st.slider(
        "JPG Quality",
        min_value=50,
        max_value=95,
        value=current_default,
        step=1,
        help="High ≥ 95  |  Medium 70–94  |  Low < 70"
    )

    # Sync label from slider value
    derived_label = quality_label_from_value(quality)
    if derived_label != st.session_state.quality_label:
        st.session_state.quality_label = derived_label

    # Quality value annotation
    st.markdown(
        f'<div style="text-align:right;font-size:0.72rem;color:rgba(255,255,255,0.35);margin-top:-6px;">'
        f'value: <strong style="color:rgba(255,255,255,0.6);">{quality}</strong></div>',
        unsafe_allow_html=True
    )

    # File uploader — label provided for accessibility, hidden via CSS
    uploaded = st.file_uploader(
        "Upload DOCX file",
        type=["docx"],
        label_visibility="hidden"
    )

    if uploaded:
        st.session_state.file_bytes = uploaded.read()
        st.session_state.file_name = uploaded.name
        st.markdown(
            f'<div style="text-align:right;font-size:0.76rem;color:rgba(255,255,255,0.42);margin-top:2px;">'
            f'{uploaded.name} · {len(st.session_state.file_bytes)/1024:.0f} KB</div>',
            unsafe_allow_html=True
        )

    st.markdown("</div>", unsafe_allow_html=True)


# ── Conversion logic ──
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
                        bg = Image.new("RGB", img.size, (255, 255, 255))
                        if img.mode == "P":
                            img = img.convert("RGBA")
                        bg.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                        img = bg
                    elif img.mode != "RGB":
                        img = img.convert("RGB")
                    img.save(jpg_path, "JPEG", quality=quality, optimize=True)
                    rename_map[png_path.name] = jpg_name
                    png_path.unlink()
                    converted_count += 1
            except Exception as e:
                st.warning(f"Could not convert {png_path.name}: {e}")
            progress.progress((i + 1) / len(png_files), text=f"Processing {i+1} of {len(png_files)}…")

        progress.empty()

        if rels_path.exists() and rename_map:
            content = rels_path.read_text(encoding="utf-8")
            for old, new in rename_map.items():
                content = content.replace(f'Target="media/{old}"', f'Target="media/{new}"')
            rels_path.write_text(content, encoding="utf-8")

        if content_types_path.exists():
            ct = content_types_path.read_text(encoding="utf-8")
            if 'Extension="jpeg"' not in ct and 'Extension="jpg"' not in ct:
                ct = ct.replace('</Types>', '  <Default Extension="jpeg" ContentType="image/jpeg"/>\n</Types>')
            for old, new in rename_map.items():
                ct = ct.replace(old, new)
            if not (list(media_dir.glob("*.png")) + list(media_dir.glob("*.PNG"))) and 'Extension="png"' in ct:
                ct = re.sub(r'\s*<Default Extension="[Pp][Nn][Gg]"[^/]*/>', '', ct)
            content_types_path.write_text(ct, encoding="utf-8")

        doc_xml = extract_dir / "word" / "document.xml"
        if doc_xml.exists() and rename_map:
            content = doc_xml.read_text(encoding="utf-8")
            for old, new in rename_map.items():
                content = content.replace(old, new)
            doc_xml.write_text(content, encoding="utf-8")

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for f in extract_dir.rglob("*"):
                if f.is_file():
                    zout.write(f, f.relative_to(extract_dir))

        return output_path.read_bytes(), len(png_files), converted_count


# ── Convert button & results ──
if st.session_state.file_bytes:
    original_size_kb = len(st.session_state.file_bytes) / 1024

    with right_col:
        if st.button("↑  Convert now"):
            with st.spinner("Converting…"):
                result_bytes, total_pngs, converted = convert_docx(
                    st.session_state.file_bytes, quality
                )
            if result_bytes is None:
                st.warning("No PNG images found in this document.")
            else:
                new_size_kb = len(result_bytes) / 1024
                saving = ((original_size_kb - new_size_kb) / original_size_kb) * 100
                st.session_state.result = {
                    "bytes": result_bytes,
                    "converted": converted,
                    "original_kb": original_size_kb,
                    "new_kb": new_size_kb,
                    "saving": saving,
                    "quality_label": st.session_state.quality_label,
                    "quality_val": quality,
                    "filename": st.session_state.file_name.replace(".docx", "_converted.docx"),
                }

    # Show floating result cards
    if st.session_state.result:
        r = st.session_state.result
        saving_str = f"−{r['saving']:.0f}% smaller" if r['saving'] > 0 else f"+{abs(r['saving']):.0f}% larger"
        st.markdown(f"""
        <div class="result-panel">
            <div class="rcard">
                <div class="rlabel">Images converted</div>
                <div class="rval">{r['converted']}</div>
            </div>
            <div class="rcard">
                <div class="rlabel">Quality used</div>
                <div class="rval">{r['quality_label']}</div>
                <div class="rdelta">value: {r['quality_val']}</div>
            </div>
            <div class="rcard">
                <div class="rlabel">Original size</div>
                <div class="rval">{r['original_kb']:.0f} KB</div>
            </div>
            <div class="rcard">
                <div class="rlabel">New size</div>
                <div class="rval">{r['new_kb']:.0f} KB</div>
                <div class="rdelta">{saving_str}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        with right_col:
            st.download_button(
                "⬇  Download converted DOCX",
                data=r["bytes"],
                file_name=r["filename"],
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )


# ── Footer ──
st.markdown("""
<div class="bottom-bar">
    <span class="footer-txt">Made with ♥ — files are never stored or shared</span>
    <span class="footer-txt">DOCX Converter 2026</span>
</div>
""", unsafe_allow_html=True)
