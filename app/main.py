from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse
from fastapi import Request
from xlwings import XlwingsError
import uvicorn

app = FastAPI()

# Error handling
@app.exception_handler(XlwingsError)
async def xlwings_exception_handler(request: Request, exception: XlwingsError):
    return PlainTextResponse(
        str(exception), status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )

@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exception: HTTPException):
    # Return "msg" instead of {"detail": "msg"} for nicer frontend formatting
    return PlainTextResponse(str(exception.detail), status_code=exception.status_code)

# Routers
# app.include_router(myspreadsheet.router)

# Unprotected healthcheck
@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get('/')
def test_endpoint(request: Request):
    client_ip = request.client.host
    print(f"Received request from IP address: {client_ip}")
    return "Test Endpoint"

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=8000)

# # This function calcukates the price of a vanilla option using quantlib library, its inputs are
# @app.get('/vanillaoptionprice')
# async def vanilla_option_price(request: Request):

