from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi import Request
from pydantic import BaseModel

import time
import logging
import httpx
from typing import List

import uvicorn
import QuantLib as ql

app = FastAPI()

# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exception: HTTPException):
    # Log the exception details
    logging.error(f"Exception occurred: {exception}")

    # Return "msg" instead of {"detail": "msg"} for nicer frontend formatting
    return PlainTextResponse(str(exception.detail), status_code=exception.status_code)

# # Unprotected health check
# @app.get("/health")
# async def health(request: Request):
#     client_ip = request.client.host
#     print(f"Request received from IP address: {client_ip}")
#     return {"status": "ok"}


@app.post("/example")
async def example(request: Request):
    return {"message": "Empty POST request received"}


class MessagePayload(BaseModel):
    message: str

@app.put("/example_put")
async def example_put(request: Request, payload: MessagePayload, exception: HTTPException):
    print("PUT request received:")
    print(payload.dict())
    return JSONResponse(content={"status": "ok"}, status_code=200)


# Define the request model
class OptionPriceRequest(BaseModel):
    
    CURRENCY_PAIR: str
    MATURITY: str
    STRIKE: float
    NOTIONAL: float
    EXOTIC_TYPE: str
    TYPE: str
    UPPER_BARRIER: float
    LOWER_BARRIER: float
    WINDOW_START_DATE: str
    WINDOW_END_DATE: str
    SPOT: float
    VOLATILITY: float

# Endpoint to calculate vanilla option price
@app.post('/webpricer')
async def calculate_option_price(request: OptionPriceRequest):
    # Extract the input parameters from the request
    CURRENCY_PAIR = request.CURRENCY_PAIR
    MATURITY = request.MATURITY
    STRIKE = request.STRIKE
    NOTIONAL = request.NOTIONAL
    EXOTIC_TYPE = request.EXOTIC_TYPE
    TYPE = request.TYPE
    UPPER_BARRIER = request.UPPER_BARRIER
    LOWER_BARRIER = request.LOWER_BARRIER
    WINDOW_START_DATE = request.WINDOW_START_DATE
    WINDOW_END_DATE = request.WINDOW_END_DATE
    SPOT = request.SPOT
    VOLATILITY = request.VOLATILITY

    # Print the extracted input parameters
    print("Extracted input parameters:")
    print(f"CURRENCY_PAIR: {CURRENCY_PAIR}")
    print(f"MATURITY: {MATURITY}")
    print(f"STRIKE: {STRIKE}")
    print(f"NOTIONAL: {NOTIONAL}")
    print(f"EXOTIC_TYPE: {EXOTIC_TYPE}")
    print(f"TYPE: {TYPE}")
    print(f"UPPER_BARRIER: {UPPER_BARRIER}")
    print(f"LOWER_BARRIER: {LOWER_BARRIER}")
    print(f"WINDOW_START_DATE: {WINDOW_START_DATE}")
    print(f"WINDOW_END_DATE: {WINDOW_END_DATE}")
    print(f"SPOT: {SPOT}")
    print(f"VOLATILITY: {VOLATILITY}")

    option_price = 4500

  # Return the calculated option price
    return {"option_price": option_price}


class OPRequest(BaseModel):
    CURRENCY_PAIR: str
    MATURITY: str
    STRIKE: float
    NOTIONAL: float
    EXOTIC_TYPE: str
    TYPE: str
    UPPER_BARRIER: float
    LOWER_BARRIER: float
    WINDOW_START_DATE: str
    WINDOW_END_DATE: str
    SPOT: float
    VOLATILITY: float

@app.post('/bulkwebpricer')
async def calculate_option_prices_bulk(requests: List[OPRequest]):
    num_rows = len(requests)
    option_prices = []  # List to store the calculated option prices

    async with httpx.AsyncClient() as client:
        # Iterate through each JSON package
        for i, request in enumerate(requests):
            print("Sending request for row: ", i")
            # Make a request to the specific route /webpricer
            response = await client.post('http://localhost:80/webpricer', json=request.dict())
            response.raise_for_status()  # Optional: Raise an exception for non-2xx responses

            # Retrieve the option price from the response
            data = await response.json()
            option_price = data["option_price"]

            # Append the option price to the list
            option_prices.append(option_price)

            # Print the statement for the last option
            if i == num_rows - 1:
                print("All rows received")

    # Return the list of option prices as the final response
    return {"option_prices": option_prices}






    # # Extract the individual characters for the dates
    # maturity_day = int(maturity_date_str[3:5])
    # maturity_month = int(maturity_date_str[0:2])
    # maturity_year = int(maturity_date_str[6:])

    # calculation_day = int(calculation_date_str[3:5])
    # calculation_month = int(calculation_date_str[0:2])
    # calculation_year = int(calculation_date_str[6:])

    # # Convert date integers to QuantLib Dates
    # maturity_date = ql.Date(maturity_day, maturity_month, maturity_year)
    # calculation_date = ql.Date(calculation_day, calculation_month, calculation_year)

    # # Determine option type
    # if TYPE.lower() == 'call':
    #     option_type = ql.Option.Call
    # elif TYPE.lower() == 'put':
    #     option_type = ql.Option.Put

    # # Set evaluation date
    # ql.Settings.instance().evaluationDate = calculation_date

    # # Convert day count and calendar strings to QuantLib objects
    # # day_count = ql.Actual365Fixed()
    # if day_count_str.lower() == 'actual365fixed':
    #     day_count = ql.Actual365Fixed()
    # elif day_count_str.lower() == 'actual360':
    #     day_count = ql.Actual360()
    # elif day_count_str.lower() == 'actualactual':
    #     day_count = ql.ActualActual()
    # # Add more conditions for other day count conventions if needed

    # calendar = ql.NullCalendar()
    # if calendar_str.lower() == 'usgovbond':
    #     calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)

    # # Construct the European option
    # payoff = ql.PlainVanillaPayoff(option_type, strike_price)
    # exercise = ql.EuropeanExercise(maturity_date)
    # european_option = ql.VanillaOption(payoff, exercise)
    
    # # Construct the Black-Scholes-Merton process
    # print(f"Constructing BSM process... {calendar_str}")
    # spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
    # flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(0, calendar, risk_free_rate, day_count))
    # dividend_yield = ql.YieldTermStructureHandle(ql.FlatForward(0, calendar, dividend_rate, day_count))
    # flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(0, calendar, volatility, day_count))
    # bsm_process = ql.BlackScholesMertonProcess(spot_handle, dividend_yield, flat_ts, flat_vol_ts)

    # # Set pricing engine and calculate option price
    # european_option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
    # option_price = european_option.NPV()

    # # Return the calculated option price
    # return {"option_price": option_price}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80)