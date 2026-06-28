from app.models.farm import Farm
from app.farm.repository import FarmRepository


class FarmService:
    """
    Farm Service
    Handles business logic related to farms.
    """

    @staticmethod
    def create_farm(data, user_id):
        """
        Create a new farm.
        """

        try:
            from app.services.soil_service import SoilService
            
            # Deduce Soil Type
            soil_data = SoilService.get_soil_by_location(
                lat=data.get("latitude"),
                lon=data.get("longitude"),
                district=data.get("district")
            )
            derived_soil_type = soil_data.get("soil_type", "Unknown")

            farm = Farm(
                user_id=user_id,
                farm_name=data["farm_name"],
                country=data.get("country"),
                state=data.get("state"),
                district=data.get("district"),
                taluk=data.get("taluk"),
                village=data["village"],
                soil_type=derived_soil_type,
                farm_size=data["farm_size"],
                latitude=data.get("latitude"),
                longitude=data.get("longitude")
            )

            FarmRepository.create_farm(farm)

            return {
                "success": True,
                "message": "Farm created successfully.",
                "farm": {
                    "id": str(farm.id),
                    "farm_name": farm.farm_name,
                    "state": farm.state,
                    "district": farm.district,
                    "village": farm.village,
                    "soil_type": farm.soil_type,
                    "farm_size": farm.farm_size,
                    "latitude": farm.latitude,
                    "longitude": farm.longitude,
                    "created_at": (
                        farm.created_at.isoformat()
                        if farm.created_at
                        else None
                    )
                }
            }, 201

        except Exception as e:

            FarmRepository.rollback()

            return {
                "success": False,
                "message": "Failed to create farm.",
                "error": str(e)
            }, 500

    @staticmethod
    def get_all_farms(user_id):
        """
        Get all farms for the logged-in user.
        """

        try:

            farms = FarmRepository.get_farms_by_user(user_id)

            farm_list = []

            for farm in farms:
                farm_list.append({
                    "id": str(farm.id),
                    "farm_name": farm.farm_name,
                    "state": farm.state,
                    "district": farm.district,
                    "village": farm.village,
                    "soil_type": farm.soil_type,
                    "farm_size": farm.farm_size,
                    "latitude": farm.latitude,
                    "longitude": farm.longitude,
                    "created_at": (
                        farm.created_at.isoformat()
                        if farm.created_at
                        else None
                    )
                })

            return {
                "success": True,
                "count": len(farm_list),
                "farms": farm_list
            }, 200

        except Exception as e:

            return {
                "success": False,
                "message": "Failed to fetch farms.",
                "error": str(e)
            }, 500

    @staticmethod
    def get_farm_by_id(farm_id, user_id):
        """
        Fetch a single farm's details.
        """
        try:
            farm = FarmRepository.get_farm_by_id(farm_id)
            if not farm:
                return {
                    "success": False,
                    "message": "Farm not found."
                }, 404

            if str(farm.user_id) != str(user_id):
                return {
                    "success": False,
                    "message": "Unauthorized access to this farm."
                }, 403

            return {
                "success": True,
                "farm": {
                    "id": str(farm.id),
                    "farm_name": farm.farm_name,
                    "state": farm.state,
                    "district": farm.district,
                    "village": farm.village,
                    "soil_type": farm.soil_type,
                    "farm_size": farm.farm_size,
                    "latitude": farm.latitude,
                    "longitude": farm.longitude,
                    "created_at": (
                        farm.created_at.isoformat()
                        if farm.created_at
                        else None
                    )
                }
            }, 200

        except Exception as e:
            return {
                "success": False,
                "message": "Failed to fetch farm details.",
                "error": str(e)
            }, 500

    @staticmethod
    def update_farm(farm_id, data, user_id):
        """
        Update farm properties.
        """
        try:
            farm = FarmRepository.get_farm_by_id(farm_id)
            if not farm:
                return {
                    "success": False,
                    "message": "Farm not found."
                }, 404

            if str(farm.user_id) != str(user_id):
                return {
                    "success": False,
                    "message": "Unauthorized access to this farm."
                }, 403

            # Update only provided attributes
            if "farm_name" in data:
                farm.farm_name = data["farm_name"]
            if "state" in data:
                farm.state = data["state"]
            if "district" in data:
                farm.district = data["district"]
            if "village" in data:
                farm.village = data["village"]
            if "soil_type" in data:
                farm.soil_type = data["soil_type"]
            if "farm_size" in data:
                farm.farm_size = data["farm_size"]
            if "latitude" in data:
                farm.latitude = data["latitude"]
            if "longitude" in data:
                farm.longitude = data["longitude"]

            FarmRepository.update_farm()

            return {
                "success": True,
                "message": "Farm updated successfully.",
                "farm": {
                    "id": str(farm.id),
                    "farm_name": farm.farm_name,
                    "state": farm.state,
                    "district": farm.district,
                    "village": farm.village,
                    "soil_type": farm.soil_type,
                    "farm_size": farm.farm_size,
                    "latitude": farm.latitude,
                    "longitude": farm.longitude,
                    "created_at": (
                        farm.created_at.isoformat()
                        if farm.created_at
                        else None
                    )
                }
            }, 200

        except Exception as e:
            FarmRepository.rollback()
            return {
                "success": False,
                "message": "Failed to update farm.",
                "error": str(e)
            }, 500

    @staticmethod
    def delete_farm(farm_id, user_id):
        """
        Delete a farm.
        """
        try:
            farm = FarmRepository.get_farm_by_id(farm_id)
            if not farm:
                return {
                    "success": False,
                    "message": "Farm not found."
                }, 404

            if str(farm.user_id) != str(user_id):
                return {
                    "success": False,
                    "message": "Unauthorized access to this farm."
                }, 403

            FarmRepository.delete_farm(farm)

            return {
                "success": True,
                "message": "Farm deleted successfully."
            }, 200

        except Exception as e:
            FarmRepository.rollback()
            return {
                "success": False,
                "message": "Failed to delete farm.",
                "error": str(e)
            }, 500