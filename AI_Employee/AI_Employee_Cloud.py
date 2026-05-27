import json
import os
# On remplace Ollama par GoogleGenerativeAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

class IAEmploye:
    def __init__(self, api_key="AIzaSyAi62U27loBkZ3Kl7aUzhZ2A4xdfP88x3M"):
        # Initialisation de Gemini 1.5 Pro ou Flash
        # 'gemini-1.5-flash' est ultra rapide et souvent gratuit/très peu cher
        # 'gemini-1.5-pro' est le plus intelligent pour les tâches complexes
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-3.1-flash-lite", 
            google_api_key=api_key,
            temperature=0.7
        )
        
        self.memory_file = "long_term_memory.json"
        self.history_file = "chat_history.json"
        self.long_term_memory = self._load_json(self.memory_file)
        self.chat_history = self._load_history()

    def _load_json(self, file_path):
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _load_history(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_data(self):
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.long_term_memory, f, indent=4)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.chat_history, f, indent=4)

    def generate_response(self, user_text):
        user_name = self.long_term_memory.get("user_name", "Pierre-Baptiste")
        
        # Le prompt système (Fiche de poste)
        system_prompt = SystemMessage(content=f"""
        Tu es un employé virtuel nommé 'Max'. Ton patron est {user_name}.
        Tu dois être proactif. Si tu as fini une tâche, propose ton aide.
        Voici ce que tu sais sur ton patron : {json.dumps(self.long_term_memory)}
        """)

        # Construction des messages (Format Chat)
        messages = [system_prompt]
        for msg in self.chat_history[-10:]:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))
        
        messages.append(HumanMessage(content=user_text))

        # Appel API (Beaucoup plus rapide que le local)
        result = self.llm.invoke(messages)
        response = result.content

        # Sauvegarde
        self.chat_history.append({"role": "user", "content": user_text})
        self.chat_history.append({"role": "assistant", "content": response})
        
        # Extraction de nom simple (on pourra l'améliorer plus tard)
        if "m'appelle" in user_text.lower():
            self.long_term_memory["user_name"] = user_text.split()[-1]
            
        self.save_data()
        return response

# --- LANCEMENT ---
if __name__ == "__main__":
    # Remplace par ta vraie clef
    CLEF = "AIzaSyAi62U27lA4xdfP88x3M" 
    employe = IAEmploye(api_key=CLEF)
    
    print("--- Employé Gemini prêt (Mode Cloud) ---")
    while True:
        prompt = input("Vous : ")
        if prompt.lower() in ["exit", "quitter"]: break
        print(f"\nEmployé : {employe.generate_response(prompt)}\n")