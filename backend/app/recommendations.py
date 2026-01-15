def lifestyle_recommendations(brand):
    rec = []
    try:
        ts = float(brand.total_salts or 0)
        ca = float(brand.calcium or 0)
        mg = float(brand.magnesium or 0)
        so4 = float(brand.sulfates or 0)
    except Exception:
        ts = ca = mg = so4 = 0.0

    if ts < 200:
        rec.append("Low-mineral — good for low-sodium diets and everyday hydration.")
    if mg > 20:
        rec.append("Magnesium-rich — may support muscle recovery after exercise.")
    if ca > 60:
        rec.append("High calcium — supportive of bone health; good for older adults/teens.")
    if so4 > 100:
        rec.append("High sulfates — pronounced mineral taste; consume moderately.")
    if not rec:
        rec.append("Balanced profile — suitable for daily consumption.")

    return rec

def water_personality(brand):
    try:
        ts = float(brand.total_salts or 0)
        mg = float(brand.magnesium or 0)
        ca = float(brand.calcium or 0)
    except Exception:
        ts = mg = ca = 0.0

    if ts > 500:
        return "Bold & Mineral: assertive mineral notes, robust mouthfeel."
    if ts < 180:
        return "Light & Crisp: clean, refreshing and easy to drink."
    if mg > 25:
        return "Sporty & Refreshing: slightly 'energetic' mineral kick."
    if ca > 80:
        return "Smooth & Comforting: creamy mouthfeel, bone-friendly."
    return "Balanced & Friendly: versatile for meals and daily use."
