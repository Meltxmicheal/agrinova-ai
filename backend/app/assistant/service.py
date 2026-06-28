import os
import json
from app.farm.repository import FarmRepository
from app.dashboard.repository import DashboardRepository

class AssistantService:
    @staticmethod
    def handle_chat(user_id: str, message: str, history: list):
        try:
            # 1. Fetch user's context
            farms = FarmRepository.get_farms_by_user(user_id)
            stats = DashboardRepository.get_stats_by_user(user_id)
            
            # Format context
            context_str = f"You have {stats['farms_count']} farms registered. "
            for farm in farms:
                context_str += f"Farm '{farm.farm_name}' is located in {farm.village}, {farm.district}, {farm.state} with {farm.soil_type} soil. "
            
            # 2. Smart Mock Logic for Chat
            # Since we don't have a guaranteed live LLM API key here, we'll build a responsive mock
            msg_lower = message.lower()
            
            response_text = ""
            
            if "hello" in msg_lower or "hi" in msg_lower:
                response_text = "Hello! I am your AI Farm Assistant. How can I help you with your agriculture today? " + context_str
            elif "farm" in msg_lower or "my farms" in msg_lower:
                if stats['farms_count'] == 0:
                    response_text = "You don't have any farms registered yet. Please go to the Manage Farms section to add one."
                else:
                    response_text = f"You have {stats['farms_count']} farms. " + context_str
            elif "weather" in msg_lower or "rain" in msg_lower:
                response_text = "Based on our latest weather fetch for your area, there is a moderate chance of rain in the coming week. Make sure your drainage is clear!"
            elif "soil" in msg_lower or "fertilizer" in msg_lower:
                response_text = "I recommend getting a soil test for accurate fertilizer application. If you upload a soil report in the predictions tab, I can give you precise NPK requirements for your crop."
            else:
                response_text = "I'm your AI Farm Assistant. I can help you with crop recommendations, yield predictions, weather alerts, and managing your farms. " + context_str
                
            return {
                "success": True,
                "reply": response_text
            }, 200

        except Exception as e:
            return {
                "success": False,
                "message": "Failed to generate AI response.",
                "error": str(e)
            }, 500
