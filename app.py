import streamlit as st
from src.models import CopyRequest, Platform, Tone
from src.generator import CopyGenerator
import asyncio

st.title("🚀 Automated Copywriting Engine")

col1, col2 = st.columns(2)

with col1:
    product_name = st.text_input("Product Name")
    platform = st.selectbox("Platform", [p.value for p in Platform])
    tone = st.selectbox("Tone", [t.value for t in Tone])

with col2:
    description = st.text_area("Product Description", height=100)
    audience = st.text_input("Target Audience")
    cta = st.text_input("Call to Action")

if st.button("Generate Copy"):
    if product_name and description:
        request = CopyRequest(
            product_name=product_name,
            product_description=description,
            platform=Platform(platform),
            tone=Tone(tone),
            target_audience=audience,
            call_to_action=cta,
        )
        
        with st.spinner("Generating..."):
            generator = CopyGenerator()
            response = asyncio.run(generator.generate_async(request))
            
        st.success("✅ Copy Generated!")
        st.text_area("Generated Copy", response.copy_text, height=200)
        
        if response.hashtags:
            st.write("**Hashtags:**", ", ".join(response.hashtags))