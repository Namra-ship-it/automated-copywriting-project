import streamlit as st
from src.models import CopyRequest, Platform, Tone
from src.generator import CopyGenerator
import asyncio
import base64
import os

# ==========================================
# 1. AUTO-LOAD IMAGES
# ==========================================
def load_image(image_name):
    """Safely finds and loads images from the current folder or subfolders."""
    if os.path.exists(image_name):
        with open(image_name, "rb") as f:
            return base64.b64encode(f.read()).decode()
    
    for root, dirs, files in os.walk("."):
        if image_name in files:
            with open(os.path.join(root, image_name), "rb") as f:
                return base64.b64encode(f.read()).decode()
    return None

# Load images
bg_image = load_image("background.jfif")
img2 = load_image("image2.jfif")
img3 = load_image("image3.jfif")
img4 = load_image("image4.jfif")

# ==========================================
# 2. GLOBAL STYLING (STRIP WHITE CANVAS)
# ==========================================
if bg_image:
    bg_css = f'background-image: url("data:image/jpeg;base64,{bg_image}");'
else:
    bg_css = "background-color: #f4f6f9;"

st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&family=Space+Grotesk:wght@500;700&display=swap');

    /* 1. REMOVE STREAMLIT'S WHITE CANVAS COMPLETELY */
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stHeader"], [data-testid="stMainBlockContainer"], .main {{
        background: transparent !important;
    }}

    /* 2. APPLY YOUR BACKGROUND IMAGE TO THE ACTUAL ROOT */
    .stApp {{
        {bg_css}
        background-size: cover !important;
        background-position: top left !important;
        background-repeat: no-repeat !important;
        color: #4a2b3a; 
        font-family: 'Inter', sans-serif;
    }}
    
    /* 3. PLACE A VERY LIGHT, SEMI-TRANSPARENT WHITE GLASS BOX BEHIND THE FORM ONLY
       SO YOUR BACKGROUND IS STILL VISIBLE, BUT TEXT IS READABLE */
    .block-container {{
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 900px; 
        background: rgba(255, 255, 255, 0.35) !important;
        border-radius: 20px;
        backdrop-filter: blur(5px);
        border: 1px solid rgba(255, 255, 255, 0.5);
        margin-top: 2rem;
    }}

    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* Title: Make it dark red so it pops on top of your red/white image */
    h1 {{
        font-family: 'Space Grotesk', sans-serif;
        background: -webkit-linear-gradient(45deg, #a80000, #d32f2f);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-size: 2.5rem;
        text-align: center;
        margin-bottom: 10px;
        text-shadow: 2px 2px 10px rgba(255, 255, 255, 0.8);
    }}

    p {{
        color: #550000 !important;
        font-weight: 700;
        text-shadow: 1px 1px 5px rgba(255, 255, 255, 0.9);
    }}

    /* Inputs: Solid white */
    .stTextInput > div > div > input, 
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div > div {{
        background-color: #ffffff !important;
        color: #4a2b3a !important;
        border: 2px solid #d32f2f !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }}
    
    .stTextInput > div > div > input:focus, 
    .stTextArea > div > div > textarea:focus {{
        border: 2px solid #d32f2f !important;
        box-shadow: 0 0 10px rgba(211, 47, 47, 0.5) !important;
    }}

    .stSelectbox div[data-baseweb="select"] > div {{
        background-color: #ffffff !important;
        color: #4a2b3a !important;
        border: 2px solid #d32f2f !important;
    }}

    /* Labels for Inputs: Dark text, no glow needed due to glass box */
    .stTextInput label, .stTextArea label, .stSelectbox label {{
        color: #333333 !important;
        font-weight: 800;
    }}

    /* Button */
    .stButton > button {{
        background: linear-gradient(90deg, #d32f2f 0%, #ff7043 100%);
        color: white;
        font-weight: bold;
        border: none;
        border-radius: 10px;
        padding: 10px 24px;
        width: 100%;
        transition: 0.3s ease;
        box-shadow: 0 4px 15px rgba(211, 47, 47, 0.5);
    }}
    .stButton > button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(211, 47, 47, 0.7);
        color: white;
    }}

    .stSuccess {{
        background-color: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #d32f2f;
        color: #d32f2f !important;
    }}

    .stTextArea textarea {{
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid #d32f2f;
        color: #4a2b3a;
    }}

    /* Images */
    .stImage img {{
        border-radius: 15px;
        border: 3px solid #d32f2f;
        box-shadow: 0 4px 20px rgba(0,0,0,0.3);
        margin-bottom: 20px;
        max-height: 450px !important; 
        object-fit: cover;
        margin-left: auto;
        margin-right: auto;
        display: block;
        background-color: white; 
    }}

    hr {{
        border-color: rgba(0,0,0,0.2) !important;
    }}
</style>
""", unsafe_allow_html=True)

# ==========================================
# 3. HEADER & IMAGES
# ==========================================
st.markdown("<h1>🚀 Automated Copywriting Engine</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; margin-bottom: 30px;'>Futuristic AI Copy Generation Dashboard</p>", unsafe_allow_html=True)

col_img1, col_img2, col_img3 = st.columns(3)
with col_img1:
    if img2:
        st.image(f"data:image/jpeg;base64,{img2}", caption="AI Ecosystem", width='stretch')
    else:
        st.warning("⚠️ Missing image2.jfif")
with col_img2:
    if img3:
        st.image(f"data:image/jpeg;base64,{img3}", caption="AI Integration", width='stretch')
    else:
        st.warning("⚠️ Missing image3.jfif")
with col_img3:
    if img4:
        st.image(f"data:image/jpeg;base64,{img4}", caption="Global Marketing", width='stretch')
    else:
        st.warning("⚠️ Missing image4.jfif")

st.markdown("---")

# ==========================================
# 4. MAIN APPLICATION LOGIC
# ==========================================
with st.container():
    col1, col2 = st.columns(2)

    with col1:
        product_name = st.text_input("Product Name", placeholder="e.g., Quantum Smartwatch")
        platform = st.selectbox("Platform", [p.value for p in Platform])
        tone = st.selectbox("Tone", [t.value for t in Tone])

    with col2:
        description = st.text_area("Product Description", height=100, placeholder="Describe your product's unique features...")
        audience = st.text_input("Target Audience", placeholder="e.g., Tech-savvy millennials")
        cta = st.text_input("Call to Action", placeholder="e.g., Buy Now")

    st.write("")

    if st.button("⚡ Generate Copy"):
        if product_name and description:
            request = CopyRequest(
                product_name=product_name,
                product_description=description,
                platform=Platform(platform),
                tone=Tone(tone),
                target_audience=audience,
                call_to_action=cta,
            )
            
            with st.spinner("🤖 AI is processing your request..."):
                generator = CopyGenerator()
                response = asyncio.run(generator.generate_async(request))
                
            st.success("✅ Copy Generated Successfully!")
            st.markdown("### ✍️ Your Generated Copy")
            st.text_area("Generated Copy", response.copy_text, height=250, key="output")
            
            if response.hashtags:
                st.markdown("### 🏷️ Suggested Hashtags")
                tags_html = " ".join([f"<span style='background-color: rgba(255, 255, 255, 0.9); color: #d32f2f; padding: 5px 10px; border-radius: 15px; margin-right: 5px; font-weight: bold; border: 1px solid #d32f2f;'>{tag}</span>" for tag in response.hashtags])
                st.markdown(tags_html, unsafe_allow_html=True)
                
        else:
            st.warning("⚠️ Please provide at least a Product Name and Description to generate copy.")