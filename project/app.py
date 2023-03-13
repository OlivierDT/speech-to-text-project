from fastapi import FastAPI, UploadFile, File
#from pydantic import BaseModel
#import os
import uvicorn

'''
run api locally, from inside directory: $ uvicorn app:app --reload
'''

# Set port to the env variable PORT to make it easy to choose the port on the server
# If the Port env variable is not set, use port 8000
#PORT = os.environ.get("PORT", 8000)
app = FastAPI()

@app.get("/")
def root():
    """HTTP get function to check that the application is alive."""
    return "Live and kicking!"

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """HTTP post function that receives a .zip file as input and returns a .zip file as output."""
    if file.filename.endswith('.zip'):
        contents = await file.read()
        process_zip_file(contents)
    return {"filename": file.filename}

# to run the app locally using uvicorn, otherwise comment this block out
if __name__ == "__main__":
  uvicorn.run(app,host="127.0.0.1", port="8000")