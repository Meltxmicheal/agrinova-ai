from app.dashboard.repository import DashboardRepository


class DashboardService:
    """
    Dashboard Service
    Formats and processes dashboard telemetry.
    """

    @staticmethod
    def get_dashboard_data(user_id: str):
        try:
            raw = DashboardRepository.get_stats_by_user(user_id)

            # Format recent predictions
            predictions_list = []
            for pred in raw["recent_predictions"]:
                predictions_list.append({
                    "id": str(pred.id),
                    "prediction_type": pred.prediction_type,
                    "inputs": pred.inputs,
                    "outputs": pred.outputs,
                    "confidence": pred.confidence,
                    "created_at": (
                        pred.created_at.isoformat()
                        if pred.created_at
                        else None
                    )
                })

            # Format recent weather logs
            weather_list = []
            for w in raw["recent_weather"]:
                weather_list.append({
                    "id": str(w.id),
                    "farm_id": str(w.farm_id),
                    "temperature": w.temperature,
                    "humidity": w.humidity,
                    "wind_speed": w.wind_speed,
                    "rain_probability": w.rain_probability,
                    "weather_description": w.weather_description,
                    "polled_at": (
                        w.polled_at.isoformat()
                        if w.polled_at
                        else None
                    )
                })

            # Generate Smart Insights
            insights = []
            
            # Simple rules for insights
            if raw["farms_count"] == 0:
                insights.append({
                    "icon": "bi-geo-alt",
                    "color": "text-primary",
                    "text": "Register your first farm to unlock hyper-local weather alerts and AI-driven crop recommendations."
                })
            else:
                if weather_list:
                    latest_weather = weather_list[0]
                    if latest_weather["rain_probability"] > 60:
                        insights.append({
                            "icon": "bi-cloud-rain",
                            "color": "text-info",
                            "text": f"High probability of rain ({latest_weather['rain_probability']}%) detected for one of your farms. Consider delaying fertilizer application."
                        })
                    elif latest_weather["temperature"] > 35:
                        insights.append({
                            "icon": "bi-thermometer-sun",
                            "color": "text-danger",
                            "text": f"High temperatures ({latest_weather['temperature']}°C) detected. Ensure adequate irrigation for heat-sensitive crops."
                        })
                
                if predictions_list:
                    recent_pred = predictions_list[0]
                    pred_type = recent_pred["prediction_type"].replace("_", " ")
                    insights.append({
                        "icon": "bi-clock-history",
                        "color": "text-success",
                        "text": f"Your latest {pred_type} prediction is ready. Review the detailed report for actionable steps."
                    })
                
                if len(insights) < 2:
                    insights.append({
                        "icon": "bi-lightbulb",
                        "color": "text-warning",
                        "text": "Update your farm's seasonal data to get the most accurate market price forecasts."
                    })

            return {
                "success": True,
                "stats": {
                    "farms_count": raw["farms_count"],
                    "total_size_hectares": raw["total_size"],
                    "predictions_count": raw["predictions_count"],
                    "breakdown": raw["breakdown"]
                },
                "recent_predictions": predictions_list,
                "recent_weather": weather_list,
                "insights": insights
            }, 200

        except Exception as e:
            return {
                "success": False,
                "message": "Failed to compile dashboard statistics.",
                "error": str(e)
            }, 500
