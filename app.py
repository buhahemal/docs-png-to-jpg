import streamlit as st
import zipfile
import tempfile
import re
from pathlib import Path
from PIL import Image

st.set_page_config(
    page_title="DOCX Converter",
    page_icon="🖼️",
    layout="centered"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* ── Reset ── */
*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

html, body, [class*="css"], .stApp {
    font-family: 'Inter', sans-serif;
}

/* ── Full-bleed background ── */
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
    background: linear-gradient(
        180deg,
        rgba(5, 10, 25, 0.72) 0%,
        rgba(8, 18, 42, 0.55) 40%,
        rgba(5, 12, 30, 0.68) 100%
    );
    pointer-events: none;
    z-index: 0;
}

/* ── Streamlit layout reset ── */
.block-container {
    padding: 0 !important;
    max-width: 100% !important;
    position: relative;
    z-index: 1;
}

section.main > div {
    padding: 0 !important;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }
[data-testid="stDecoration"] { display: none !important; }

/* ── Page wrapper ── */
.page-wrap {
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    padding: 52px 24px 100px;
    position: relative;
    z-index: 1;
}

/* ── Header block ── */
.header-block {
    text-align: center;
    margin-bottom: 48px;
    width: 100%;
}

.app-name {
    font-size: clamp(2.6rem, 6vw, 4.8rem);
    font-weight: 800;
    color: #ffffff;
    letter-spacing: -0.04em;
    line-height: 1.0;
    margin-bottom: 14px;
    text-shadow: 0 2px 40px rgba(0,0,0,0.4);
}

.app-tagline {
    font-size: clamp(0.85rem, 2vw, 1rem);
    font-weight: 300;
    color: rgba(255,255,255,0.52);
    letter-spacing: 0.02em;
    line-height: 1.5;
}

/* ── Center card ── */
.center-card {
    width: 100%;
    max-width: 560px;
    display: flex;
    flex-direction: column;
    gap: 20px;
}

/* ── Quality selector ── */
.quality-row {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 10px;
    flex-wrap: wrap;
}

.quality-label-txt {
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: rgba(255,255,255,0.38);
    text-transform: uppercase;
    margin-right: 4px;
}

.quality-pill {
    font-size: 0.82rem;
    font-weight: 400;
    color: rgba(255,255,255,0.38);
    padding: 0 2px;
}

.quality-pill.active {
    font-weight: 700;
    color: #ffffff;
}

/* ── Glass card ── */
.glass-card {
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.16);
    border-radius: 20px;
    backdrop-filter: blur(24px);
    -webkit-backdrop-filter: blur(24px);
    padding: 28px 28px 24px;
}

/* ── Result cards row ── */
.result-row {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
    gap: 12px;
    width: 100%;
    max-width: 560px;
}

.rcard {
    background: rgba(255,255,255,0.09);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 14px;
    padding: 14px 16px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    text-align: center;
}

.rlabel {
    font-size: 0.62rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.35);
    margin-bottom: 6px;
}

.rval {
    font-size: 1.3rem;
    font-weight: 700;
    color: #fff;
    letter-spacing: -0.02em;
}

.rdelta {
    font-size: 0.7rem;
    color: rgba(255,255,255,0.48);
    margin-top: 3px;
}

/* ── Bottom bar ── */
.bottom-bar {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    border-top: 1px solid rgba(255,255,255,0.08);
    padding: 14px 40px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 20;
    background: rgba(0,0,0,0.15);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}

.footer-txt {
    font-size: 0.74rem;
    color: rgba(255,255,255,0.25);
    font-weight: 300;
}

/* ── Streamlit widget overrides ── */

/* File uploader */
[data-testid="stFileUploader"] {
    width: 100% !important;
}

[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.06) !important;
    border: 1.5px dashed rgba(255,255,255,0.22) !important;
    border-radius: 14px !important;
    padding: 24px !important;
    backdrop-filter: blur(10px) !important;
    -webkit-backdrop-filter: blur(10px) !important;
    transition: all 0.2s !important;
    width: 100% !important;
}

[data-testid="stFileUploaderDropzone"]:hover {
    background: rgba(255,255,255,0.12) !important;
    border-color: rgba(255,255,255,0.4) !important;
}

[data-testid="stFileUploaderDropzone"] p,
[data-testid="stFileUploaderDropzone"] span {
    color: rgba(255,255,255,0.75) !important;
    font-size: 0.88rem !important;
    font-weight: 400 !important;
}

[data-testid="stFileUploaderDropzoneInstructions"] svg {
    display: none !important;
}

[data-testid="stFileUploaderDropzone"] button {
    background: rgba(255,255,255,0.14) !important;
    border: 1px solid rgba(255,255,255,0.28) !important;
    border-radius: 50px !important;
    color: #fff !important;
    font-size: 0.78rem !important;
    font-weight: 500 !important;
    padding: 6px 18px !important;
}

[data-testid="stFileUploaderFileName"] {
    color: rgba(255,255,255,0.85) !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
}

/* Hide label for file uploader visually */
[data-testid="stFileUploader"] label {
    position: absolute !important;
    width: 1px !important; height: 1px !important;
    overflow: hidden !important;
    clip: rect(0,0,0,0) !important;
}

/* All buttons → glass pill */
[data-testid="stButton"] > button {
    background: rgba(255,255,255,0.12) !important;
    border: 1.5px solid rgba(255,255,255,0.26) !important;
    border-radius: 50px !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.86rem !important;
    font-weight: 500 !important;
    padding: 10px 22px !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
    transition: all 0.18s ease !important;
    width: auto !important;
    min-width: unset !important;
    white-space: nowrap !important;
}

[data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.22) !important;
    border-color: rgba(255,255,255,0.5) !important;
    transform: translateY(-1px) !important;
}

/* Active/selected quality button */
[data-testid="stButton"] > button[kind="primary"] {
    background: rgba(255,255,255,0.28) !important;
    border-color: rgba(255,255,255,0.6) !important;
    font-weight: 700 !important;
}

/* Convert button — full width, more prominent */
.convert-btn [data-testid="stButton"] > button {
    width: 100% !important;
    padding: 14px 28px !important;
    font-size: 0.94rem !important;
    font-weight: 600 !important;
    background: rgba(255,255,255,0.18) !important;
    border-color: rgba(255,255,255,0.38) !important;
    letter-spacing: 0.02em !important;
}

.convert-btn [data-testid="stButton"] > button:hover {
    background: rgba(255,255,255,0.28) !important;
}

/* Download button */
[data-testid="stDownloadButton"] > button {
    background: rgba(255,255,255,0.18) !important;
    border: 1.5px solid rgba(255,255,255,0.38) !important;
    border-radius: 50px !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.94rem !important;
    font-weight: 600 !important;
    padding: 14px 28px !important;
    backdrop-filter: blur(18px) !important;
    width: 100% !important;
    transition: all 0.18s !important;
    letter-spacing: 0.02em !important;
}

[data-testid="stDownloadButton"] > button:hover {
    background: rgba(255,255,255,0.28) !important;
    transform: translateY(-1px) !important;
}

/* Slider */
[data-testid="stSlider"] {
    width: 100% !important;
}

[data-testid="stSlider"] label {
    color: rgba(255,255,255,0.42) !important;
    font-size: 0.7rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
}

[data-testid="stSlider"] [data-testid="stTickBar"] { display: none !important; }

div[data-baseweb="slider"] div[role="slider"] {
    background-color: #ffffff !important;
    border-color: #ffffff !important;
    width: 18px !important;
    height: 18px !important;
}

/* Progress */
[data-testid="stProgressBar"] > div {
    background: rgba(255,255,255,0.15) !important;
    border-radius: 100px !important;
}
[data-testid="stProgressBar"] > div > div {
    background: rgba(255,255,255,0.65) !important;
    border-radius: 100px !important;
}

/* Alerts */
[data-testid="stAlert"] {
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.14) !important;
    border-radius: 12px !important;
    color: rgba(255,255,255,0.8) !important;
}

/* Spinner */
.stSpinner > div {
    border-color: rgba(255,255,255,0.65) rgba(255,255,255,0.1) rgba(255,255,255,0.1) !important;
}

/* Remove default Streamlit spacing */
.element-container { margin-bottom: 0 !important; }
div[data-testid="stVerticalBlock"] > div[data-testid="stVerticalBlock"] {
    gap: 0 !important;
}

/* Responsive tweaks */
@media (max-width: 600px) {
    .page-wrap { padding: 36px 16px 90px; }
    .glass-card { padding: 20px 16px 18px; }
    .app-name { margin-bottom: 10px; }
    .bottom-bar { padding: 12px 20px; }
    .result-row { grid-template-columns: repeat(2, 1fr); }
}
</style>
""", unsafe_allow_html=True)

# ── Session state ──
if "quality_label" not in st.session_state:
    st.session_state.quality_label = "High"
if "result" not in st.session_state:
    st.session_state.result = None
if "file_bytes" not in st.session_state:
    st.session_state.file_bytes = None
if "file_name" not in st.session_state:
    st.session_state.file_name = None

QUALITY_OPTIONS = {"High": 95, "Medium": 82, "Low": 60}


def quality_label_from_value(v):
    if v >= 95:
        return "High"
    elif v >= 70:
        return "Medium"
    else:
        return "Low"


# ════════════════════════════════════════
#  PAGE OPEN
# ════════════════════════════════════════
st.markdown('<div class="page-wrap">', unsafe_allow_html=True)

# ── HEADER — top center ──
st.markdown("""
<div class="header-block">
    <div class="app-name">DOCX Converter</div>
    <div class="app-tagline">Convert PNG images inside Word documents to JPG<br>— smaller file, same layout.</div>
</div>
""", unsafe_allow_html=True)

# ── CENTER CARD ──
st.markdown('<div class="center-card">', unsafe_allow_html=True)

# ── Glass card wrapper ──
st.markdown('<div class="glass-card">', unsafe_allow_html=True)

# Quality cosmetic display row
q_pills = '<div class="quality-row"><span class="quality-label-txt">Quality</span>'
for opt in ["High", "Medium", "Low"]:
    cls = "quality-pill active" if opt == st.session_state.quality_label else "quality-pill"
    q_pills += f'<span class="{cls}">{opt}</span>'
q_pills += '</div>'
st.markdown(q_pills, unsafe_allow_html=True)

# Quality buttons — centered row
q_col1, q_col2, q_col3 = st.columns(3)
with q_col1:
    if st.button("High", key="q_High", use_container_width=True):
        st.session_state.quality_label = "High"
        st.session_state.result = None
        st.rerun()
with q_col2:
    if st.button("Medium", key="q_Medium", use_container_width=True):
        st.session_state.quality_label = "Medium"
        st.session_state.result = None
        st.rerun()
with q_col3:
    if st.button("Low", key="q_Low", use_container_width=True):
        st.session_state.quality_label = "Low"
        st.session_state.result = None
        st.rerun()

# Slider
quality = st.slider(
    "JPG Quality",
    min_value=50,
    max_value=95,
    value=QUALITY_OPTIONS[st.session_state.quality_label],
    step=1,
    help="High ≥ 95  |  Medium 70–94  |  Low < 70"
)

# Sync label ↔ slider
derived = quality_label_from_value(quality)
if derived != st.session_state.quality_label:
    st.session_state.quality_label = derived

st.markdown(
    f'<div style="text-align:right;font-size:0.7rem;color:rgba(255,255,255,0.3);margin-top:2px;">'
    f'value: <b style="color:rgba(255,255,255,0.55);">{quality}</b></div>',
    unsafe_allow_html=True
)

# File uploader
uploaded = st.file_uploader(
    "Upload DOCX file",
    type=["docx"],
    label_visibility="hidden"
)

if uploaded:
    st.session_state.file_bytes = uploaded.read()
    st.session_state.file_name = uploaded.name
    st.markdown(
        f'<div style="text-align:center;font-size:0.76rem;color:rgba(255,255,255,0.4);margin-top:4px;">'
        f'📄 {uploaded.name} &nbsp;·&nbsp; {len(st.session_state.file_bytes)/1024:.0f} KB</div>',
        unsafe_allow_html=True
    )

st.markdown('</div>', unsafe_allow_html=True)  # close glass-card


# ── Conversion function ──
def convert_docx(file_bytes, quality):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        extract_dir = tmpdir / "extracted"
        input_path  = tmpdir / "input.docx"
        output_path = tmpdir / "output.docx"

        input_path.write_bytes(file_bytes)
        with zipfile.ZipFile(input_path, 'r') as z:
            z.extractall(extract_dir)

        media_dir          = extract_dir / "word" / "media"
        rels_path          = extract_dir / "word" / "_rels" / "document.xml.rels"
        content_types_path = extract_dir / "[Content_Types].xml"

        if not media_dir.exists():
            return None, 0, 0

        png_files = list(media_dir.glob("*.png")) + list(media_dir.glob("*.PNG"))
        if not png_files:
            return None, 0, 0

        rename_map      = {}
        converted_count = 0
        progress        = st.progress(0, text="Converting images…")

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
            progress.progress((i + 1) / len(png_files),
                              text=f"Processing {i+1} of {len(png_files)}…")

        progress.empty()

        if rels_path.exists() and rename_map:
            c = rels_path.read_text(encoding="utf-8")
            for old, new in rename_map.items():
                c = c.replace(f'Target="media/{old}"', f'Target="media/{new}"')
            rels_path.write_text(c, encoding="utf-8")

        if content_types_path.exists():
            ct = content_types_path.read_text(encoding="utf-8")
            if 'Extension="jpeg"' not in ct and 'Extension="jpg"' not in ct:
                ct = ct.replace('</Types>',
                    '  <Default Extension="jpeg" ContentType="image/jpeg"/>\n</Types>')
            for old, new in rename_map.items():
                ct = ct.replace(old, new)
            if not (list(media_dir.glob("*.png")) + list(media_dir.glob("*.PNG"))) \
                    and 'Extension="png"' in ct:
                ct = re.sub(r'\s*<Default Extension="[Pp][Nn][Gg]"[^/]*/>', '', ct)
            content_types_path.write_text(ct, encoding="utf-8")

        doc_xml = extract_dir / "word" / "document.xml"
        if doc_xml.exists() and rename_map:
            c = doc_xml.read_text(encoding="utf-8")
            for old, new in rename_map.items():
                c = c.replace(old, new)
            doc_xml.write_text(c, encoding="utf-8")

        with zipfile.ZipFile(output_path, 'w', zipfile.ZIP_DEFLATED) as zout:
            for f in extract_dir.rglob("*"):
                if f.is_file():
                    zout.write(f, f.relative_to(extract_dir))

        return output_path.read_bytes(), len(png_files), converted_count


# ── Convert button ──
if st.session_state.file_bytes:
    st.markdown('<div class="convert-btn">', unsafe_allow_html=True)
    if st.button("↑  Convert Document", use_container_width=True, key="convert"):
        with st.spinner("Converting…"):
            result_bytes, total_pngs, converted = convert_docx(
                st.session_state.file_bytes, quality
            )
        if result_bytes is None:
            st.warning("No PNG images found in this document.")
        else:
            orig_kb = len(st.session_state.file_bytes) / 1024
            new_kb  = len(result_bytes) / 1024
            saving  = ((orig_kb - new_kb) / orig_kb) * 100
            st.session_state.result = {
                "bytes":         result_bytes,
                "converted":     converted,
                "original_kb":   orig_kb,
                "new_kb":        new_kb,
                "saving":        saving,
                "quality_label": st.session_state.quality_label,
                "quality_val":   quality,
                "filename":      st.session_state.file_name.replace(".docx", "_converted.docx"),
            }
    st.markdown('</div>', unsafe_allow_html=True)

# ── Result cards — centered below ──
if st.session_state.result:
    r = st.session_state.result
    saving_str = f"−{r['saving']:.0f}% smaller" if r['saving'] > 0 else f"+{abs(r['saving']):.0f}% larger"

    st.markdown(f"""
    <div class="result-row">
        <div class="rcard">
            <div class="rlabel">Converted</div>
            <div class="rval">{r['converted']}</div>
            <div class="rdelta">images</div>
        </div>
        <div class="rcard">
            <div class="rlabel">Quality</div>
            <div class="rval">{r['quality_label']}</div>
            <div class="rdelta">value {r['quality_val']}</div>
        </div>
        <div class="rcard">
            <div class="rlabel">Before</div>
            <div class="rval">{r['original_kb']:.0f}<span style="font-size:0.7rem;font-weight:400;opacity:.6"> KB</span></div>
        </div>
        <div class="rcard">
            <div class="rlabel">After</div>
            <div class="rval">{r['new_kb']:.0f}<span style="font-size:0.7rem;font-weight:400;opacity:.6"> KB</span></div>
            <div class="rdelta">{saving_str}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # Download button — full width centered
    st.download_button(
        "⬇  Download Converted DOCX",
        data=r["bytes"],
        file_name=r["filename"],
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        use_container_width=True,
    )

st.markdown('</div>', unsafe_allow_html=True)  # close center-card
st.markdown('</div>', unsafe_allow_html=True)  # close page-wrap

# ── Footer ──
st.markdown("""
<div class="bottom-bar">
    <span class="footer-txt">Made with ♥ — files are never stored or shared</span>
    <span class="footer-txt">DOCX Converter 2026</span>
</div>
""", unsafe_allow_html=True)
