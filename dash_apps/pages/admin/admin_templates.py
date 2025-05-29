import os

def load_template(template_name):
    TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'templates', 'admin')
    template_path = os.path.join(TEMPLATE_DIR, template_name)
    with open(template_path, 'r', encoding='utf-8') as file:
        return file.read()

USER_FORM_TEMPLATE = load_template('user_form.html')
USER_TABLE_TEMPLATE = load_template('user_table.html')
ADMIN_JS = load_template('admin.js')
ADMIN_LAYOUT = load_template('admin_layout.html')
