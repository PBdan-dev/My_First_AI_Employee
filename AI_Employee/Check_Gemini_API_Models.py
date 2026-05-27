import google.generativeai as genai

# Remplace par ta clef
API_KEY = ""

genai.configure(api_key=API_KEY)

print("--- Liste des modèles accessibles via ta clef ---")
try:
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            print(f"Nom : {m.name}  |  Titre : {m.display_name}")
except Exception as e:
    print(f"Erreur : {e}")

