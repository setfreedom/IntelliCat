import sys, os
sys.path.insert(0, r'D:\python\project\IntelliCat\smart_catalog\backend')
os.chdir(r'D:\python\project\IntelliCat\smart_catalog\backend')

from app import create_app
app = create_app()
print('Flask app initialized successfully')
for rule in sorted(app.url_map.iter_rules(), key=lambda r: r.rule):
    if rule.rule.startswith('/api'):
        methods = rule.methods - {'OPTIONS', 'HEAD'}
        if methods:
            print(f'  {sorted(methods)} {rule.rule}')
