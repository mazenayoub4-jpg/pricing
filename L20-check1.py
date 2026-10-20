# ════════════════════════════════════════════════════════════
#   فحص العملي الأول — خدمة لا دفتر
#
#   ١. شغّلوا الخدمة بنافذة:   uvicorn pricing_api:app --reload
#   ٢. وبنافذة تانية:          python L20-check1.py
# ════════════════════════════════════════════════════════════
import sys, os, re

BASE = "http://127.0.0.1:8000"
SRC  = "pricing_api.py"

print("\n" + "═" * 62)
print("  فحص العملي الأول — من سيرفر لخدمة")
print("═" * 62)

try:
    import httpx
except ImportError:
    print("\n  ✗ مكتبة httpx مش مثبّتة.   pip install httpx\n"); sys.exit()

try:
    httpx.get(BASE + "/health", timeout=5)
except Exception:
    print(f"\n  ✗ ما قدرت أوصل الخدمة على {BASE}")
    print("\n    شغّلوها بنافذة تانية، بنفس مجلّد الملف:")
    print("        uvicorn pricing_api:app --reload")
    print("\n    وخلّوها شغّالة، وبعدين شغّلوا الفحص.\n")
    sys.exit()


def جيب(مسار, **params):
    try:
        return httpx.get(BASE + مسار, params=params or None, timeout=15)
    except Exception as e:
        return e


def جسم(r):
    if not isinstance(r, httpx.Response):
        return {}
    try:
        return r.json()
    except Exception:
        return {}


h    = جيب("/health")
a100 = جيب("/quote", code="A-100")
a200 = جيب("/quote", code="A-200")
z999 = جيب("/quote", code="Z-999")
ناقص = جيب("/quote")
docs = جيب("/openapi.json")

j100 = جسم(a100)
نص100 = " ".join(str(v) for v in j100.values())

مصدر = open(SRC, encoding="utf-8").read() if os.path.exists(SRC) else ""

# هل للمسار docstring؟
وصف = ""
o = جسم(docs)
try:
    # description = الـ docstring  ·  summary = اسم الدالة تلقائياً
    وصف = o["paths"]["/quote"]["get"].get("description", "")
except Exception:
    وصف = ""

بنود = [
    ("الخدمة شغّالة · /health بيردّ 200",
     isinstance(h, httpx.Response) and h.status_code == 200),

    ("مسار /quote موجود",
     isinstance(a100, httpx.Response) and a100.status_code != 404),

    ("A-100 بيرجّع 200",
     isinstance(a100, httpx.Response) and a100.status_code == 200),

    ("A-100 فيه سعر العرض 95",
     "95" in نص100),

    ("A-100 بيذكر المصدر promo",
     "promo" in نص100),

    ("A-200 بيرجّع 80 من الكتالوج",
     "80" in " ".join(str(v) for v in جسم(a200).values())),

    ("كود مش موجود بيرجّع ردّاً مفهوماً · بلا انهيار",
     isinstance(z999, httpx.Response) and z999.status_code < 500),

    ("بلا code بيرجّع 422 — مش 500",
     isinstance(ناقص, httpx.Response) and ناقص.status_code == 422),

    ("المسار إله docstring بيطلع بـ /docs",
     len(وصف.strip()) >= 5),
]

ناجح = sum(1 for _, ok in بنود if ok)
print()
for نص, ok in بنود:
    print(f"  {'✓' if ok else '✗'} {نص}")
print(f"\n  ── {ناجح} / 9 ──")

print("\n" + "─" * 62)
print("  وهاي ردود خدمتكم · حرفياً")
print("─" * 62)
for اسم, r in [("A-100", a100), ("A-200", a200), ("Z-999", z999),
               ("بلا code", ناقص)]:
    if isinstance(r, httpx.Response):
        print(f"\n  {اسم:10} → {r.status_code}")
        print(f"     {r.text[:150]}")
    else:
        print(f"\n  {اسم:10} → <ما وصل ردّ>")

print(f"\n  وصف /quote بـ /docs : {وصف.strip() or '(فاضي)'}")
print("\n  وافتحوا بالمتصفّح:  http://127.0.0.1:8000/docs")
print()
