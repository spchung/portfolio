from app.db.redis import r
from app.api.v2.skincare_gpt.context.context_manager import SkincareGPTContextManager

context_manager = SkincareGPTContextManager()

class ContextService:
    def __init__(self):
        self.context = None

    def reset_context(self, session_id):
        # remove for active session pool
        context_manager.remove_from_pool(session_id)

        temp_session_id = context_manager.generate_session_id()
        new_context = context_manager.get_context(temp_session_id)
        new_context.session_id = session_id

        r.set(session_id, new_context.serialize())
        return {"status": "success"}
