import re

with open('app.py', 'r', encoding='utf8') as f:
    content = f.read()

# Update sidebar
content = content.replace(
    'show_ab_test_lines = st.sidebar.checkbox("Show A/B Test Events on Charts", value=True)',
    'show_build_lines = st.sidebar.checkbox("Show Build Events on Charts", value=True)\nshow_ab_test_lines = st.sidebar.checkbox("Show A/B Test Events on Charts", value=True)'
)

# Update all function calls
content = re.sub(
    r'add_changelog_vlines\(([^,]+),\s*changelog_df,\s*start_date,\s*end_date,\s*show_ab_test_lines\)',
    r'add_changelog_vlines(\1, changelog_df, start_date, end_date, show_ab_test=show_ab_test_lines, show_build=show_build_lines)',
    content
)

with open('app.py', 'w', encoding='utf8') as f:
    f.write(content)

print("Updated successfully")
