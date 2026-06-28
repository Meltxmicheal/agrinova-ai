"""AgriNova AI — Full Boot Verification Script"""
import sys, os
sys.path.insert(0, os.path.dirname(__file__))

from app import create_app
app = create_app()

print("=== AgriNova AI Boot Check ===")
print(f"Blueprints ({len(app.blueprints)}): {list(app.blueprints.keys())}")

routes = []
skip_methods = {"OPTIONS", "HEAD"}
for rule in app.url_map.iter_rules():
    if rule.endpoint != "static":
        methods = rule.methods - skip_methods
        routes.append(f"  {','.join(sorted(methods)):8s} {rule.rule}")

routes.sort()
print(f"\nTotal Routes: {len(routes)}")
for r in routes:
    print(r)
print("\n=== Boot Successful ===")
