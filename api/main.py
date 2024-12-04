import os
from fastapi import FastAPI, File, HTTPException, Query, UploadFile
from fastapi.responses import JSONResponse
import motor.motor_asyncio
from dotenv import load_dotenv
from models.paginated_response import PaginatedResponseModel
from utils import custom_jsonable_encoder
from config import PIPELINE, UPLOAD_DIRECTORY 

load_dotenv(dotenv_path="../.env")

app = FastAPI()

app.jsonable_encoder = custom_jsonable_encoder

@app.post("/upload/")
async def uploadFile(file: UploadFile = File(...)):
    """

    Args:
        file (UploadFile, optional): Accepts csv that is below 50mb and saves it to
        ../storage/app/medalists . Defaults to File(...).

    Returns:
        JsonResponse: contains a message with a statuc code
    """
    try:
        file_path = os.path.join(UPLOAD_DIRECTORY, file.filename)
        if file.size > 50000000 or file.content_type != "text/csv":
            return JSONResponse(
                content={"error": "File bigger than 50mb or not csv"}, status_code=400
            )
        
        base, ext = os.path.splitext(file_path)
        counter = 1
        while os.path.exists(file_path):
            file_path = f"{base}_{counter}{ext}"
            counter += 1
            
        with open(file_path, "wb") as f:
            contents = await file.read()
            f.write(contents)

        return JSONResponse(
            content={"message": "File saved"},
            status_code=200,
        )
    except Exception as e:
        return JSONResponse(content={"message": f"Error: {str(e)}"}, status_code=400)

@app.get("/aggregated_stats/event", response_model=PaginatedResponseModel)
async def getAggregatedStats(page: int = Query(1, ge=1)):
    """
    Args:
        page (int, optional): Returns a PaginatedResponseModel. Defaults to Query(1, ge=1).

    Raises:
        HTTPException: Returns the Exception
        
    """
    try:
        page_size = 10
        client = motor.motor_asyncio.AsyncIOMotorClient(os.getenv("MONGO_URL"))
        db = client.examdb
        medalists_collection = db.get_collection("medalists_collection")
        skip = (page - 1) * page_size
        limit = page_size

        agg_cursor = medalists_collection.aggregate(PIPELINE)
        agg = await agg_cursor.to_list(length=limit)
        total_count = await medalists_collection.count_documents({})  
        
        return PaginatedResponseModel(
            data=agg,
            paginate={
                "current_page": page,
                "total_pages": (total_count + page_size - 1) // page_size,
                "next_page": f"/aggregated_stats/event?page={page+1}",
                "previous_page": f"/aggregated_stats/event?page={page-1}",
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
