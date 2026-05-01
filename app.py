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
    background-image: url('https://weppy.figma.site/_assets/v11/9d3ca6313b6785619d82cf9ed822392d059852f1.png?w=1800&q=80');
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
        rgba(8,18,38,0.55) 0%,
        rgba(10,25,50,0.30) 55%,
        rgba(5,15,30,0.50) 100%);
    pointer-events: none;
    z-index: 0;
}

.block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

section.main > div { padding: 0 !important; }
.element-container { margin: 0 !important; }

/* Hide Streamlit chrome */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* ── Hero left title ── */
.hero-wrap {
    position: fixed;
    bottom: 120px;
    left: 72px;
    z-index: 2;
}

.hero-title {
    font-size: clamp(3rem, 5vw, 4.5rem);
    font-weight: 700;
    color: #ffffff;
    letter-spacing: -0.035em;
    line-height: 1.05;
    margin-bottom: 16px;
    text-shadow: 0 4px 40px rgba(0,0,0,0.25);
}

.hero-sub {
    font-size: 0.97rem;
    font-weight: 300;
    color: rgba(255,255,255,0.58);
    letter-spacing: 0.01em;
    line-height: 1.55;
}

/* ── Controls top-right ── */
.controls-wrap {
    position: fixed;
    top: 56px;
    right: 64px;
    z-index: 10;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 18px;
}

/* Glass button style */
.glass-btn-row {
    display: flex;
    gap: 12px;
    align-items: center;
}

/* Quality pills */
.quality-row {
    display: flex;
    align-items: center;
    gap: 22px;
}
.quality-label {
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 0.14em;
    color: rgba(255,255,255,0.45);
    text-transform: uppercase;
}
.quality-options {
    display: flex;
    gap: 18px;
}
.q-opt {
    font-size: 0.88rem;
    font-weight: 400;
    color: rgba(255,255,255,0.38);
    cursor: pointer;
    letter-spacing: 0.01em;
    transition: color 0.15s;
}
.q-opt.active {
    font-weight: 700;
    color: #ffffff;
}

/* ── Result panel (appears after conversion) ── */
.result-panel {
    position: fixed;
    top: 50%;
    right: 64px;
    transform: translateY(-50%);
    z-index: 8;
    display: flex;
    flex-direction: column;
    align-items: flex-end;
    gap: 12px;
}

.result-metric {
    background: rgba(255,255,255,0.10);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 14px;
    padding: 14px 22px;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    text-align: right;
}
.rm-label {
    font-size: 0.68rem;
    font-weight: 600;
    letter-spacing: 0.1em;
    text-transform: uppercase;
    color: rgba(255,255,255,0.38);
    margin-bottom: 4px;
}
.rm-val {
    font-size: 1.35rem;
    font-weight: 600;
    color: #fff;
    letter-spacing: -0.02em;
}
.rm-delta {
    font-size: 0.75rem;
    color: rgba(255,255,255,0.55);
    margin-top: 2px;
}

/* ── Bottom bar ── */
.bottom-bar {
    position: fixed;
    bottom: 0; left: 0; right: 0;
    border-top: 1px solid rgba(255,255,255,0.1);
    padding: 18px 72px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    z-index: 20;
    background: rgba(0,0,0,0.12);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
}
.footer-txt {
    font-size: 0.8rem;
    color: rgba(255,255,255,0.3);
    font-weight: 300;
}

/* ── Streamlit widget overrides ── */

/* File uploader — pill glass */
[data-testid="stFileUploaderDropzone"] {
    background: rgba(255,255,255,0.12) !important;
    border: 1.5px solid rgba(255,255,255,0.28) !important;
    border-radius: 50px !important;
    padding: 10px 26px !important;
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
    font-size: 0.88rem !important;
    font-weight: 500 !important;
}
[data-testid="stFileUploaderDropzoneInstructions"] svg { display: none !important; }
[data-testid="stFileUploaderDropzone"] button {
    background: rgba(255,255,255,0.15) !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
    border-radius: 50px !important;
    color: #fff !important;
    font-size: 0.78rem !important;
    padding: 5px 14px !important;
}
[data-testid="stFileUploaderFileName"] {
    color: rgba(255,255,255,0.9) !important;
    font-weight: 500 !important;
    font-size: 0.82rem !important;
}

/* Convert / action buttons */
[data-testid="stButton"] > button {
    background: rgba(255,255,255,0.13) !important;
    border: 1.5px solid rgba(255,255,255,0.28) !important;
    border-radius: 50px !important;
    color: #fff !important;
    font-family: 'Inter', sans-serif !important;
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 10px 24px !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
    transition: all 0.18s !important;
    letter-spacing: 0.01em !important;
    white-space: nowrap !important;
    width: auto !important;
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
    font-size: 0.88rem !important;
    font-weight: 500 !important;
    padding: 10px 24px !important;
    backdrop-filter: blur(18px) !important;
    -webkit-backdrop-filter: blur(18px) !important;
    transition: all 0.18s !important;
    width: auto !important;
}
[data-testid="stDownloadButton"] > button:hover {
    background: rgba(255,255,255,0.22) !important;
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

/* Slider (hidden — quality pills used instead) */
[data-testid="stSlider"] { display: none !important; }

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
</style>
""", unsafe_allow_html=True)


# ── Session state ──
if "quality_label" not in st.session_state:
    st.session_state.quality_label = "High"
if "result" not in st.session_state:
    st.session_state.result = None

QUALITY_MAP = {"Low": 60, "Mid": 78, "High": 92, "Max": 100}


# ── Hero left ──
st.markdown("""
<div class="hero-wrap">
    <div class="hero-title">DOCX<br>Converter</div>
    <div class="hero-sub">Convert PNG images inside Word documents<br>to JPG — smaller file, same layout.</div>
</div>
""", unsafe_allow_html=True)


# ── Quality pills HTML (cosmetic) ──
q_html = '<div class="controls-wrap"><div class="quality-row"><span class="quality-label">Quality</span><div class="quality-options">'
for opt in ["Low", "Mid", "High", "Max"]:
    cls = "q-opt active" if opt == st.session_state.quality_label else "q-opt"
    q_html += f'<span class="{cls}">{opt}</span>'
q_html += '</div></div></div>'
st.markdown(q_html, unsafe_allow_html=True)


# ── Controls: top-right column layout ──
_, right_col = st.columns([2, 1])

with right_col:
    st.markdown('<div style="display:flex;flex-direction:column;align-items:flex-end;gap:14px;padding:52px 0 0;">', unsafe_allow_html=True)

    # Quality buttons (real, styled as pills)
    q_cols = st.columns(4)
    for i, label in enumerate(["Low", "Mid", "High", "Max"]):
        with q_cols[i]:
            if st.button(label, key=f"q_{label}"):
                st.session_state.quality_label = label
                st.session_state.result = None
                st.rerun()

    # Hidden slider driven by pill selection
    quality = st.slider("_q", 50, 100, QUALITY_MAP[st.session_state.quality_label],
                        label_visibility="collapsed")

    # Upload
    uploaded = st.file_uploader("", type=["docx"], label_visibility="collapsed")

    st.markdown("</div>", unsafe_allow_html=True)


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
        progress = st.progress(0, text="Converting…")

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


# ── Upload & Convert ──
if uploaded:
    file_bytes = uploaded.read()
    original_size_kb = len(file_bytes) / 1024

    with right_col:
        btn_row = st.columns([1, 1])
        with btn_row[0]:
            if st.button("↑  Upload & Convert"):
                with st.spinner("Converting…"):
                    result_bytes, total_pngs, converted = convert_docx(file_bytes, quality)
                if result_bytes is None:
                    st.warning("No PNG images found.")
                else:
                    new_size_kb = len(result_bytes) / 1024
                    saving = ((original_size_kb - new_size_kb) / original_size_kb) * 100
                    st.session_state.result = {
                        "bytes": result_bytes,
                        "converted": converted,
                        "original_kb": original_size_kb,
                        "new_kb": new_size_kb,
                        "saving": saving,
                        "filename": uploaded.name.replace(".docx", "_converted.docx"),
                    }

    # Show result panel
    if st.session_state.result:
        r = st.session_state.result
        saving_str = f"−{r['saving']:.0f}% smaller" if r['saving'] > 0 else f"+{abs(r['saving']):.0f}% larger"
        st.markdown(f"""
        <div class="result-panel">
            <div class="result-metric">
                <div class="rm-label">Images converted</div>
                <div class="rm-val">{r['converted']}</div>
            </div>
            <div class="result-metric">
                <div class="rm-label">Original size</div>
                <div class="rm-val">{r['original_kb']:.0f} KB</div>
            </div>
            <div class="result-metric">
                <div class="rm-label">New size</div>
                <div class="rm-val">{r['new_kb']:.0f} KB</div>
                <div class="rm-delta">{saving_str}</div>
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
    <span class="footer-txt">Made with ♥ - files are never stored or shared</span>
    <span class="footer-txt">DOCX Converter 2026</span>
</div>
""", unsafe_allow_html=True)
