import re

with open('app.py', 'r', encoding='utf8') as f:
    content = f.read()

config_code = """
# Enable drawing tools for all Plotly charts
PLOTLY_CONFIG = {
    'modeBarButtonsToAdd': ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape'],
    'displayModeBar': True
}
"""

if 'PLOTLY_CONFIG =' not in content:
    # Find st.set_page_config
    if 'st.set_page_config' in content:
        content = content.replace('st.set_page_config(page_title="Game Analytics", layout="wide")',
                                  'st.set_page_config(page_title="Game Analytics", layout="wide")\n' + config_code)
    else:
        # Just prepend it after imports
        content = content.replace('import streamlit as st', 'import streamlit as st\n' + config_code)

# Ensure all st.plotly_chart use config=PLOTLY_CONFIG
# We first remove it if it already exists to avoid duplication, then add it.
content = re.sub(r',\s*config=PLOTLY_CONFIG', '', content)
content = re.sub(r'st\.plotly_chart\(([^,]+),\s*use_container_width=True\)', r'st.plotly_chart(\1, use_container_width=True, config=PLOTLY_CONFIG)', content)

with open('app.py', 'w', encoding='utf8') as f:
    f.write(content)
print('Updated app.py with PLOTLY_CONFIG')
