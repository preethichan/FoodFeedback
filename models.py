from pydantic import BaseModel
from typing import List

class FoodItem(BaseModel):
    name: str
    comment: str
    review: int

class RestaurantFeedback(BaseModel):
    restaurant_name: str
    city: str
    food_items: List[FoodItem]
    
