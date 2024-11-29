import streamlit as st
import google.generativeai as genai
from PIL import Image
from fpdf import FPDF
import io

# Configure the API key securely from Streamlit's secrets
genai.configure(api_key=st.secrets["GOOGLE_API_KEY"])

# Function to generate section HTML dynamically
def generate_section_html(section_name, page_content, key):
    if key in page_content:
        content = page_content[key].text
        section_html = f"""
        <div style="margin-top: 30px;">
            <h2 style="color:{brand_secondary_color};">{section_name}</h2>
            <p>{content}</p>
        </div>
        """
        return section_html
    else:
        return ""

# Function to save HTML content to an in-memory file (using BytesIO)
def save_html_to_bytes(content):
    # Create a BytesIO buffer and write the content
    buffer = io.BytesIO()
    buffer.write(content.encode("utf-8"))
    buffer.seek(0)
    return buffer

# Function to create PDF from HTML content (simple approach using FPDF)
def generate_pdf_from_html(content):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, content)
    
    # Save to an in-memory buffer
    pdf_output = io.BytesIO()
    pdf.output(pdf_output)
    pdf_output.seek(0)
    return pdf_output

# Streamlit App UI
st.title("Ever AI: Dynamic Landing Page Generator with Advanced Features")
st.write("Create custom, AI-driven landing pages with multiple sections, interactive features, and branding options.")

# Input fields for user data to customize the landing page
landing_page_title = st.text_input("Enter your landing page title:", "My Awesome Product")
landing_page_description = st.text_area("Enter a brief description of your product or service:", "Our product is the best solution for developers.")
layout_choice = st.selectbox("Select a landing page layout:", ["Product Page", "Service Page", "Portfolio", "Campaign"])
color_scheme = st.selectbox("Select a color scheme:", ["Light", "Dark", "Custom"])

# Custom branding: Upload logo and select brand colors
logo_upload = st.file_uploader("Upload your brand logo (optional):", type=["png", "jpg", "jpeg"])
brand_primary_color = st.color_picker("Choose your primary brand color", "#1a73e8")
brand_secondary_color = st.color_picker("Choose your secondary brand color", "#ff7043")

# Multiple sections for dynamic landing page
sections = st.multiselect(
    "Select the sections for your landing page",
    ["About Us", "Features", "Pricing", "Testimonials", "Call to Action"],
    default=["About Us", "Features"]
)

# AI Content Generation Prompts
about_us_prompt = st.text_input("What should the 'About Us' section say?", "We are a tech company making the world a better place.")
features_prompt = st.text_input("Enter your product features:", "Fast, Secure, Scalable")
pricing_prompt = st.text_input("Describe your pricing model:", "Affordable subscription-based pricing.")
testimonials_prompt = st.text_input("Provide some customer testimonials:", "This product has changed the way I work!")
cta_prompt = st.text_input("Call to Action:", "Sign up for free and start using our product!")

# Button to generate the landing page and provide export options
if st.button("Generate Landing Page"):
    try:
        # Generate AI content for the sections selected
        content_response = genai.GenerativeModel('gemini-1.5-flash')

        page_content = {}

        if "About Us" in sections:
            page_content["About Us"] = content_response.generate_content(f"Write an about us section based on: {about_us_prompt}")
        if "Features" in sections:
            page_content["Features"] = content_response.generate_content(f"Generate a list of features for a product with these characteristics: {features_prompt}")
        if "Pricing" in sections:
            page_content["Pricing"] = content_response.generate_content(f"Describe the pricing structure based on: {pricing_prompt}")
        if "Testimonials" in sections:
            page_content["Testimonials"] = content_response.generate_content(f"Generate customer testimonials based on: {testimonials_prompt}")
        if "Call to Action" in sections:
            page_content["Call to Action"] = content_response.generate_content(f"Write a compelling call to action: {cta_prompt}")

        # Generate dynamic HTML and CSS for the landing page
        if color_scheme == "Light":
            background_color = "#FFFFFF"
            text_color = "#000000"
        elif color_scheme == "Dark":
            background_color = "#333333"
            text_color = "#FFFFFF"
        else:
            background_color = "#F0F0F0"
            text_color = "#000000"

        # Base HTML structure
        landing_page_html = f"""
        <html>
        <head>
            <title>{landing_page_title}</title>
            <style>
                body {{
                    background-color:{background_color};
                    color:{text_color};
                    font-family: Arial, sans-serif;
                    padding: 30px;
                }}
                h1 {{
                    color:{brand_primary_color};
                }}
                h2 {{
                    color:{brand_secondary_color};
                }}
                .section {{
                    margin-top: 30px;
                }}
            </style>
        </head>
        <body>
            <h1>{landing_page_title}</h1>
            <p>{landing_page_description}</p>
            {generate_section_html("About Us", page_content, "About Us")}
            {generate_section_html("Features", page_content, "Features")}
            {generate_section_html("Pricing", page_content, "Pricing")}
            {generate_section_html("Testimonials", page_content, "Testimonials")}
            {generate_section_html("Call to Action", page_content, "Call to Action")}
        </body>
        </html>
        """

        # Optionally add the logo to the page
        if logo_upload is not None:
            logo_img = Image.open(logo_upload)

        # Save the generated HTML and PDF
        if st.button("Download Landing Page as HTML"):
            # Save the HTML content to a BytesIO buffer and provide download option
            html_buffer = save_html_to_bytes(landing_page_html)
            st.download_button(
                label="Download HTML",
                data=html_buffer,
                file_name="landing_page.html",
                mime="text/html"
            )
        
        if st.button("Download Landing Page as PDF"):
            # Generate the PDF content from HTML
            pdf_buffer = generate_pdf_from_html(landing_page_html)
            st.download_button(
                label="Download PDF",
                data=pdf_buffer,
                file_name="landing_page.pdf",
                mime="application/pdf"
            )
    
    except Exception as e:
        st.error(f"Error: {e}")
