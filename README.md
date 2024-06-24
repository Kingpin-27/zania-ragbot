# Zania RagBot

## Project Demo Video

[![Watch the video](https://raw.githubusercontent.com/Kingpin-27/zania-ragbot/main/assets/demo-result.png)](https://raw.githubusercontent.com/Kingpin-27/zania-ragbot/main/assets/Project%20Demo.mp4)

## Install Requirements

Run `pip install requirements.txt`

## Project Structure

```
├───assets
├───uploads                 <---- directory for all RAG file uploads
├───constants.py
├───rag_agent.py            <---- core logic for implementation of RAG technique
├───rag_api_server.py       <---- FastAPI server to interact with the RAG gent

```

## Start the application

Run `python .\rag_api_server.py` to start the RAG server

## Explanation

The RAG Server consists of :
  - Parse the uploaded PDFs from the `uploads\` folder.
  - Clean the Embedding table in KDB.AI Vector Database and initialize the table
  - Configure a MarkdownElementNodeParser and recursive retrieval RAG technique to hierarchically index and query over tables and text in the uploaded document
  - Get the RAG QueryEngine configured with Post processing Rerank embedding model (Cohere) which is used to RAG over complex documents that can answer questions over both tabular and unstructured data
  - A FastAPI server to trigger the file upload process and to query the RAG Server

## Demo Request

Format:
```
{
    "file",                 <---- file to upload to RAG Agent
    "queries",              <---- semicolon separated queries to ask the agent
    "post_in_slack"         <---- boolean value to upload to slack channel
}

```

Example
```JSON
{
    "file": "./handbook.pdf",
    "queries": "What is the name of the company?;Who is the CEO of the company?;What is their vacation policy?;What is the termination policy?;What is the tech stack used by company?",
    "post_in_slack": "true"
}

```


## Demo Response
```JSON
{
   "result":[
      {
         "query":"What is the name of the company?",
         "answer":"Zania, Inc."
      },
      {
         "query":"Who is the CEO of the company?",
         "answer":"Shruti Gupta"
      },
      {
         "query":"What is their vacation policy?",
         "answer":"Zania, Inc. provides employees with paid vacation. All full-time regular employees are eligible to receive vacation time immediately upon hire/upon completion of the introductory period/after completing a certain number of days of employment. Vacation time is calculated according to the work anniversary year/the calendar year/the fiscal year, which begins on a specific date and ends on another specific date. Employees may be granted a lump sum of vacation time at the beginning of each year or accrue vacation time based on their length of service. Unused vacation time may be carried over to the following year or may be forfeited upon separation of employment."
      },
      {
         "query":"What is the termination policy?",
         "answer":"The termination policy at Zania, Inc. is based on an \"at-will\" employment basis, meaning that employment can be terminated at any time, with or without notice and with or without cause. The company reserves the right to interpret, modify, or supplement the provisions of the handbook at any time. If a written contract between the employee and the company is inconsistent with the handbook, the written contract is controlling."
      },
      {
         "query":"What is the tech stack used by company?",
         "answer":"Data Not Available"
      }
   ]
}
```

## Screenshots
Result Screen
![Screenshot-1](https://raw.githubusercontent.com/Kingpin-27/zania-ragbot/main/assets/demo-result.png)

