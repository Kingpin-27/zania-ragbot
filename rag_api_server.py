from fastapi import FastAPI, UploadFile, File, Form
import uvicorn
from datetime import datetime
from rag_agent import query_doc
from typing import Annotated


app = FastAPI()


@app.post("/rag_on_docs")
async def rag_on_docs(post_in_slack: Annotated[bool, Form()], queries: Annotated[str, Form()], file: UploadFile = File(...)):
    file_path = f"./uploads/file-{round(datetime.timestamp(datetime.now()))}.pdf"
    with open(file_path, "wb") as f:
        f.write(await file.read())

    result = query_doc(queries.split(";"), file_path, post_in_slack)
    return {"result": result}


if __name__ == "__main__":
    uvicorn.run(app, port=4444)
