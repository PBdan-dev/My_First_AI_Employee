import json
import os
from langchain_community.llms import Ollama
from langchain.schema import HumanMessage, SystemMessage, AIMessage

class IAEmploye:
    def __init__(self, model_name="gemma4"):
        # Initialisation du modèle (Gemma 4 tournant sur ta 3090)
        self.llm = Ollama(model=model_name)
        self.memory_file = "long_term_memory.json"
        self.history_file = "chat_history.json"
        
        # Chargement des données
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
        """Sauvegarde la mémoire sur le disque."""
        with open(self.memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.long_term_memory, f, indent=4)
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(self.chat_history, f, indent=4)

    def update_long_term_memory(self, user_input, ai_response):
        """
        Analyse si l'utilisateur a donné une info personnelle importante.
        Ici, on simule une extraction simple.
        """
        # Si l'utilisateur mentionne son nom
        if "m'appelle" in user_input.lower() or "mon nom est" in user_input.lower():
            # Extraction basique (on pourrait utiliser l'IA pour extraire proprement)
            name = user_input.split()[-1]
            self.long_term_memory["user_name"] = name
            self.save_data()

    def generate_response(self, user_text):
        # 1. Préparer le contexte système (La fiche de poste)
        user_name = self.long_term_memory.get("user_name", "Patron")
        
        system_prompt = f"""
        Tu es un employé virtuel proactif. Ton patron est {user_name}.
        Tu dois être poli, efficace et te souvenir des détails qu'il te donne.
        Infos connues sur le patron : {json.dumps(self.long_term_memory)}
        """

        # 2. Construire l'historique pour la mémoire à court terme
        messages = [SystemMessage(content=system_prompt)]
        
        # On ajoute les 5 derniers échanges pour ne pas saturer la VRAM
        for msg in self.chat_history[-10:]:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            else:
                messages.append(AIMessage(content=msg['content']))
        
        # Ajouter le message actuel
        messages.append(HumanMessage(content=user_text))

        # 3. Envoyer à Gemma 4
        full_prompt = "\n".join([m.content for m in messages])
        response = self.llm.invoke(full_prompt)

        # 4. Mémoriser
        self.chat_history.append({"role": "user", "content": user_text})
        self.chat_history.append({"role": "assistant", "content": response})
        self.update_long_term_memory(user_text, response)
        self.save_data()

        return response

# --- TEST DE L'EMPLOYÉ ---
if __name__ == "__main__":
    employe = IAEmploye()
    
    print("--- Employé IA prêt (Gemma 4 sur 3090) ---")
    while True:
        user_input = input("Vous : ")
        if user_input.lower() in ["exit", "quitter"]:
            break
            
        reponse = employe.generate_response(user_input)
        print(f"\nEmployé : {reponse}\n")