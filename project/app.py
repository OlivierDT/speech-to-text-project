from fastapi import FastAPI, UploadFile, File, responses
import os
import io
import uvicorn
import shutil
import zipfile
import whisperx

'''
run api locally, from inside directory: $ uvicorn app:app --reload
'''

# Set port to the env variable PORT to make it easy to choose the port on the server
# If the Port env variable is not set, use port 8000
#PORT = os.environ.get("PORT", 8000)
# instantiate fastAPI
app = FastAPI()

# load wisperX model
model = whisperx.load_model("medium.en")

@app.get("/")
def root():
    """HTTP get function to check that the application is alive."""
    return "Live and kicking!"

@app.post("/transcribe")
async def transcribe(file: UploadFile = File(...)):
    """HTTP post function that receives a .zip file as input and returns a .zip file as output."""
    if file.filename.endswith('.zip'):
        try :
            files_to_zip = process_zip_file(file)
        except Exception:
            # Cleanup
            os.remove(file.filename)
            shutil.rmtree("audio_files")
            return {"message": Exception}
    else :
        return {"message": "Uploaded file is not a .zip. Please upload a .zip file."}
    
    # Create a ZIP file in memory
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
        for file in files_to_zip:
            zip_file.write(file)

    # Reset the buffer's file pointer to the beginning
    zip_buffer.seek(0)

    # Return the ZIP file to the client as a stream
    return responses.StreamingResponse(
        zip_buffer.getvalue(),
        media_type='application/octet-stream',
        headers={
            'Content-Disposition': f'attachment; filename={"processed_files.zip"}'
        }
    )
    
    return {}

def process_zip_file(file):
    # Save the uploaded file to disk
    with open(file.filename, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Unzip the file to a directory called audio_files
    with zipfile.ZipFile(file.filename, "r") as zip_ref:
        zip_ref.extractall("audio_files")

    # Process the audio files
    files_to_zip = []
    for path in os.listdir("audio_files"):
        for filename in os.listdir(os.path.join("audio_files", path)):
            if filename.endswith(".mp3") or filename.endswith(".wav"):
                filepath = os.path.join("audio_files", filename)
                files_to_zip.append(to_text(filepath))
            else:
                return {"message": f"The following file has not been processed: {filename}. Please make sure all audio files are in .mp3 or .wav format."}

    # Cleanup
    os.remove(file.filename)
    shutil.rmtree("audio_files")

    return files_to_zip

def to_text(filepath):
    # transcribe file
    result = model.transcribe(filepath)
    
    # write raw text to .txt file
    raw_text_file = os.path.splitext(filepath)[0] + "_text.txt"
    with open(raw_text_file, "w") as text_file:
      text_file.write(result["text"])

    # write segments to .txt file
    segments_text_file = os.path.splitext(filepath)[0] + "_segments.txt"
    with open(segments_text_file,"w") as segments_file:
      segments_file.write(str(result["segments"])) 

    return raw_text_file, segments_text_file


# to run the app locally using uvicorn, otherwise comment this block out
if __name__ == "__main__":
  uvicorn.run(app,host="127.0.0.1", port="8000")

# curl -X POST -F "file=@/home/tania/becode/ucl-sermons-project/Panin sermons projects/church1680-trial.zip" http://localhost:8000/transcribe
