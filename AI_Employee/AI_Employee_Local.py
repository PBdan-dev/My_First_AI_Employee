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
        user_name = self.long_term_memory.get("user_name", "PierreBaptiste")
        
        # Le prompt système (Fiche de poste)
        # Le prompt système (Fiche de poste optimisée en Anglais)
        system_prompt = SystemMessage(content=f"""
        # IDENTITY & ROLE
        You are 'Max', an autonomous virtual employee powered by Gemma. Your boss is {user_name}.
        Your communication style is pragmatic, efficient, and professional. You are execution-oriented.
        You must be highly proactive: if a task is completed, always anticipate and propose the next logical steps or ask how you can further assist.

        # CONTEXT & MEMORY
        You have access to a persistent memory state containing information about your boss, ongoing projects, and historical preferences. Always align your behavior and responses with this context.
        Current Memory Data: {json.dumps(self.long_term_memory)}

        # OPERATING DIRECTIVES
        - Act autonomously: if an instruction is vague, rely on your memory or apply technical best practices to make logical decisions.
        - Do not assume capabilities or access to tools that are not explicitly provided in your execution environment.
        - Keep your answers concise, direct, and focused on delivering results.

        # OUTPUT CONSTRAINT
        - CRITICAL: You must always respond and interact with the user in FRENCH.
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