import json
import os

from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

class IAEmploye:
    def __init__(self):
        # Initialisation du modèle local via Ollama
        # Assure-toi que "gemma4" (ou le nom exact de ton tag) est bien téléchargé sur ton instance Ollama
        self.llm = ChatOllama(
            model="gemma4", 
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
        user_name = self.long_term_memory.get("user_name", "Pierre")
        
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

        # Appel au modèle local
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
    employe = IAEmploye()
    
    print("--- Employé local (Ollama + Gemma) prêt ---")
    while True:
        prompt = input("Vous : ")
        if prompt.lower() in ["exit", "quitter"]: break
        print(f"\nEmployé : {employe.generate_response(prompt)}\n")