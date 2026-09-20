BACKGROUND_IMAGE_URL = "https://images.stockcake.com/public/7/0/e/70e60fd6-ceb2-48ae-b552-95a5d23ac0e4_large/purple-moon-glows-stockcake.jpg"

BACKGROUND_CSS = f"""
<style>
.stApp {{
    background-image: linear-gradient(rgba(8, 4, 20, 0.28), rgba(8, 4, 20, 0.28)),
        url("{BACKGROUND_IMAGE_URL}");
    background-size: cover;
    background-position: center;
    background-attachment: fixed;
}}

.stApp > header {{
    background-color: transparent;
}}

.main .block-container {{
    background-color: rgba(15, 8, 30, 0.55);
    backdrop-filter: blur(8px);
    -webkit-backdrop-filter: blur(8px);
    border-radius: 18px;
    padding: 2rem 2.5rem;
    margin-top: 1rem;
}}

[data-testid="stSidebar"] {{
    background-color: rgba(18, 18, 18, 0.75);
    backdrop-filter: blur(6px);
}}

.stButton > button {{
    background-color: rgba(124, 77, 255, 0.85);
    color: white;
    border: none;
}}

.stButton > button:hover {{
    background-color: rgba(124, 77, 255, 1);
}}
</style>
"""