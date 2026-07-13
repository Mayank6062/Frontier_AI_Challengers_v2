from app.models.terraform_blueprint import normalize_for_terraform
from app.renderers.enterprise_terraform_renderer import render_terraform
import traceback

try:
    bp = normalize_for_terraform({}, {}, {}, {}, {}, {})
    out = render_terraform(bp)
    print(out[:2000])
except Exception as e:
    print('EXCEPTION:', e)
    traceback.print_exc()
