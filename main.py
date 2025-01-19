# main.py
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from bson.objectid import ObjectId
from typing import List
from models import RestaurantFeedback
from config import Config
from fastapi.responses import HTMLResponse, FileResponse
import os
from fastapi.middleware.cors import CORSMiddleware


# Initialize FastAPI app
app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace "*" with the specific origins you want to allow (e.g., ["http://localhost:3000"]).
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)


# Serve the HTML file (index.html) as the frontend
@app.get("/", response_class=HTMLResponse)
async def get_index():
    # Assuming index.html is located directly in the restaurant_feedback directory
    html_file_path = os.path.join(os.getcwd(), "index.html")
    return FileResponse(html_file_path)

@app.get("/favicon.ico")
async def favicon():
    favicon_path = os.path.join(os.getcwd(), "favicon.ico")  # assuming you have a favicon.ico file
    return FileResponse(favicon_path)

# Initialize MongoDB client
client = MongoClient(Config.MONGO_URI)
db = client.get_database()
feedback_collection = db.feedback

# Helper function to convert ObjectId to string
def str_id(feedback):
    feedback['_id'] = str(feedback['_id'])
    return feedback

# 1. Create a new restaurant feedback
@app.post("/feedback/", response_model=RestaurantFeedback)
async def create_feedback(feedback: RestaurantFeedback):
    feedback_dict = feedback.dict()
    result = feedback_collection.insert_one(feedback_dict)
    feedback_dict['_id'] = str(result.inserted_id)  # Add the ObjectId as a string
    return feedback_dict

# 2. Get restaurant feedback by ID
@app.get("/feedback/{feedback_id}", response_model=RestaurantFeedback)
async def get_feedback(feedback_id: str):
    feedback = feedback_collection.find_one({"_id": ObjectId(feedback_id)})
    if feedback:
        return str_id(feedback)
    raise HTTPException(status_code=404, detail="Feedback not found")

# 3. Update restaurant feedback by ID
@app.put("/feedback/{feedback_id}", response_model=RestaurantFeedback)
async def update_feedback(feedback_id: str, feedback: RestaurantFeedback):
    feedback_dict = feedback.dict()
    result = feedback_collection.update_one({"_id": ObjectId(feedback_id)}, {"$set": feedback_dict})

    if result.matched_count:
        updated_feedback = feedback_collection.find_one({"_id": ObjectId(feedback_id)})
        return str_id(updated_feedback)

    raise HTTPException(status_code=404, detail="Feedback not found")

# 4. Delete restaurant feedback by ID
@app.delete("/feedback/{feedback_id}", response_model=dict)
async def delete_feedback(feedback_id: str):
    result = feedback_collection.delete_one({"_id": ObjectId(feedback_id)})
    
    if result.deleted_count:
        return {"message": "Feedback deleted successfully"}
    
    raise HTTPException(status_code=404, detail="Feedback not found")

# 5. Get all feedbacks
@app.get("/feedbacks/", response_model=List[RestaurantFeedback])
async def get_all_feedbacks():
    feedbacks = feedback_collection.find()
    return [str_id(feedback) for feedback in feedbacks]
