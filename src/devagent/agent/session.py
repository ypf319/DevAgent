import os
import json
from ..exceptions import DevAgentBaseError

class SessionManager:
    def __init__(self, save_dir: str="./data/sessions"):

        self.save_dir = save_dir
        os.makedirs(save_dir, exist_ok=True)


    def _get_session_file(self, session_id: str) -> str:
        return os.path.join(self.save_dir, f"{session_id}.json")

    def save_session(self, session_id: str, messages:list[dict]):
        session_file = self._get_session_file(session_id)

        try:
            save_messages = [m for m in messages if m.get("role") != "system"]
            with open(session_file, "w", encoding="utf-8") as f:
                json.dump(save_messages, f, ensure_ascii=False, indent=2)
        except Exception as e:
            raise DevAgentBaseError(f"保存会话失败：{str(e)}") from e

    def load_session(self, session_id: str, system_prompt: str) -> list[dict[str,str]]:
        session_file = self._get_session_file(session_id)

        if os.path.exists(session_file):
            try:
                with open(session_file, "r", encoding="utf-8") as f:
                    messages = json.load(f)
                return messages
            except Exception as e:
                raise DevAgentBaseError(f"加载会话失败：{str(e)}") from e

        return [{"role": "system", "content": system_prompt}]

    def list_sessions(self):
        if not os.path.exists(self.save_dir):
            return []
        files = os.listdir(self.save_dir)
        return [file.replace("json","") for file in files if file.endswith(".json")]

session_manager = SessionManager()
