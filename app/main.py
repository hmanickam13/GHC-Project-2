from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse, JSONResponse
from fastapi import Request
from pydantic import BaseModel

import asyncio
import time
from datetime import date, datetime, timedelta
import logging
import httpx
from typing import List
from typing import Optional

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

# Unprotected health check
@app.get("/health")
async def health(request: Request):
    client_ip = request.client.host
    print(f"Get request received from IP address: {client_ip}")
    return {"status": "active"}


@app.post("/example")
async def example(request: Request):
    return {"message": "Empty POST request received by server"}


class MessagePayload(BaseModel):
    message: str

@app.put("/example")
async def example_put(request: Request, payload: MessagePayload):
    print(payload.dict())
    return {"status": "ok"}


# Define the request model
class OptionPriceRequest(BaseModel):
    
    # We take every input parameter as a string because some fields may be empty and a float does not accept empty values
    CURRENCY_PAIR: str
    MATURITY: str
    STRIKE: str
    NOTIONAL: str
    EXOTIC_TYPE: str
    EXERCISE: str
    TYPE: str
    UPPER_BARRIER: str
    LOWER_BARRIER: str
    WINDOW_START_DATE: str
    WINDOW_END_DATE: str
    SPOT: str
    VOLATILITY: str

# Endpoint to calculate vanilla option price
@app.post('/webpricer')
async def preprocess_option_json(request: Request, payload: OptionPriceRequest):
    # Extract the input parameters from the request
    CURRENCY_PAIR = payload.CURRENCY_PAIR
    MATURITY = payload.MATURITY
    STRIKE = payload.STRIKE
    NOTIONAL = payload.NOTIONAL
    EXOTIC_TYPE = payload.EXOTIC_TYPE
    EXERCISE = payload.EXERCISE
    TYPE = payload.TYPE
    UPPER_BARRIER = payload.UPPER_BARRIER
    LOWER_BARRIER = payload.LOWER_BARRIER
    WINDOW_START_DATE = payload.WINDOW_START_DATE
    WINDOW_END_DATE = payload.WINDOW_END_DATE
    SPOT = payload.SPOT
    VOLATILITY = payload.VOLATILITY

    # Print the extracted input parameters
    print("Incoming input parameters:")
    print(f"CURRENCY_PAIR: {CURRENCY_PAIR}")
    print(f"MATURITY: {MATURITY}")
    print(f"STRIKE: {STRIKE}")
    print(f"NOTIONAL: {NOTIONAL}")
    print(f"EXOTIC_TYPE: {EXOTIC_TYPE}")
    print(f"EXERCISE: {EXERCISE}")
    print(f"TYPE: {TYPE}")
    print(f"UPPER_BARRIER: {UPPER_BARRIER}")
    print(f"LOWER_BARRIER: {LOWER_BARRIER}")
    print(f"WINDOW_START_DATE: {WINDOW_START_DATE}")
    print(f"WINDOW_END_DATE: {WINDOW_END_DATE}")
    print(f"SPOT: {SPOT}")
    print(f"VOLATILITY: {VOLATILITY}")

    # Preprocess the fields
    COMMON_FIELDS = {
        'CURRENCY_PAIR': CURRENCY_PAIR,
        'MATURITY': MATURITY,
        'STRIKE': STRIKE,
        'NOTIONAL': NOTIONAL,
        'EXOTIC_TYPE': EXOTIC_TYPE,
        'EXERCISE': EXERCISE,
        'TYPE': TYPE,
        'SPOT': SPOT,
        'VOLATILITY': VOLATILITY
    }

    # Create a list to store errors
    errors = []

    # Process currency pair
    # If length is 6, assume format is 'USDEUR'
    if len(COMMON_FIELDS['CURRENCY_PAIR']) == 6:
        # If the first 3 characters are in the list of currencies, and the last 3 characters are in the list of currencies
        if CURRENCY_PAIR[0:3].upper() in ['USD', 'EUR', 'GBP', 'AUD', 'NZD', 'CAD', 'CHF', 'JPY'] and CURRENCY_PAIR[3:6].upper() in ['USD', 'EUR', 'GBP', 'AUD', 'NZD', 'CAD', 'CHF', 'JPY']:
            # Create new common fields
            COMMON_FIELDS['FOREIGN_CURRENCY'] = COMMON_FIELDS['CURRENCY_PAIR'][0:3]
            COMMON_FIELDS['DOMESTIC_CURRENCY'] = COMMON_FIELDS['CURRENCY_PAIR'][3:6]
        else:
            errors.append("CURRENCY_PAIR not supported. Supported currencies: [USD, EUR, GBP, AUD, NZD, CAD, CHF, JPY")
    else:
        errors.append("Invalid CURRENCY_PAIR. Ex: USDEUR")
    
    # Check if maturity date is valid
    if len(COMMON_FIELDS['MATURITY']) == 10:
        try:
            # Convert maturity date to datetime object
            maturity_date = datetime.datetime.strptime(COMMON_FIELDS['MATURITY'], '%Y-%m-%d')

            # Check if maturity date is before today's date
            if maturity_date.date() < datetime.date.today():
                errors.append("MATURITY is before today's date")
            else:
                # Convert maturity date to QuantLib Date object
                maturity_day = int(COMMON_FIELDS['MATURITY'][8:10])
                maturity_month = int(COMMON_FIELDS['MATURITY'][5:7])
                maturity_year = int(COMMON_FIELDS['MATURITY'][0:4])
                maturity_date = ql.Date(maturity_day, maturity_month, maturity_year)
                COMMON_FIELDS['MATURITY_DATE'] = maturity_date
        except ValueError:
            errors.append("Invalid MATURITY format. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")
    elif len(COMMON_FIELDS['MATURITY']) == 2 or len(COMMON_FIELDS['MATURITY']) == 3:
        try:
            if str(COMMON_FIELDS['MATURITY'][-1]).upper() in ['D', 'W', 'M', 'Y']:
                # Maturity specified as '1m' or '3M'
                maturity_type = MATURITY[-1].lower()  # Get the last character (M, W, D, Y)
                maturity_unit = {'m': ql.Period.Months, 'w': ql.Period.Weeks, 'd': ql.Period.Days, 'y': ql.Period.Years}
                maturity_value = int(MATURITY[:-1])  # Extract the numeric part
                maturity_date = ql.Date(date.today()) + ql.Period(maturity_value, maturity_unit[maturity_type])
                COMMON_FIELDS['MATURITY_DATE'] = maturity_date
            else:
                errors.append("Invalid MATURITY format. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")
        except KeyError:
            errors.append("Invalid MATURITY format. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")
    else:
        errors.append("Invalid MATURITY format. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")

    # Process strike
    if COMMON_FIELDS['STRIKE'] == '':
        errors.append("STRIKE is empty")
    else:
        try:
            COMMON_FIELDS['STRIKE'] = float(COMMON_FIELDS['STRIKE'])
        except ValueError:
            errors.append("Invalid STRIKE. Must be a float.")
        if COMMON_FIELDS['STRIKE'] <= 0:
            errors.append("STRIKE must be > 0.")

    # Process notional
    if COMMON_FIELDS['NOTIONAL'] == '':
        errors.append("NOTIONAL is empty")
    else:
        try:
            COMMON_FIELDS['NOTIONAL'] = float(COMMON_FIELDS['NOTIONAL'])
        except ValueError:
            errors.append("Invalid NOTIONAL. Must be a float.")
        if COMMON_FIELDS['NOTIONAL'] <= 0:
            errors.append("NOTIONAL must be > 0.")

    # Process spot    
    if COMMON_FIELDS['SPOT'] == '':
        errors.append("SPOT is empty.")
    else:
        try:
            COMMON_FIELDS['SPOT'] = float(COMMON_FIELDS['SPOT'])    
        except ValueError:
            errors.append("SPOT is not a valid float")
        if COMMON_FIELDS['SPOT'] <=0:
            errors.append("SPOT is not > 0.")
            
    # Process volatility
    if COMMON_FIELDS['VOLATILITY'] == '':
        print("VOLATILITY is empty.")
    else:
        try:
            COMMON_FIELDS['VOLATILITY'] = float(COMMON_FIELDS['VOLATILITY'])
        except ValueError:
            errors.append("VOLATILITY is not a valid float.")
        if VOLATILITY <=0:
            errors.append("VOLATILITY is not > 0.")

    # Process exercise type
    if COMMON_FIELDS['EXERCISE'].upper() in ['E']:
        COMMON_FIELDS['EXERCISE'] = ql.EuropeanExercise()
    elif COMMON_FIELDS['EXERCISE'].upper() in ['A']:
        COMMON_FIELDS['EXERCISE'] = ql.AmericanExercise(ql.Date().todaysDate(), COMMON_FIELDS['MATURITY'])
    else:
        errors.append("Invalid EXERCISE. Ex: E, A.")

    # Process option type
    if COMMON_FIELDS['TYPE'].upper() == 'CALL':
        COMMON_FIELDS['TYPE'] = ql.Option.Call 
    elif COMMON_FIELDS['TYPE'].upper() == 'PUT':
        COMMON_FIELDS['TYPE'] = ql.Option.Put
    else:
        errors.append("Invalid TYPE. Ex: CALL, PUT.")

    # Barrier options
    if COMMON_FIELDS['EXOTIC_TYPE'].upper() in ['KO_BARRIER', 'KI_BARRIER']:
        COMMON_FIELDS['UPPER_BARRIER'] = UPPER_BARRIER
        try:
            COMMON_FIELDS['UPPER_BARRIER'] = float(COMMON_FIELDS['UPPER_BARRIER'])
        except ValueError:
            errors.append("Invalid UPPER_BARRIER. Must be a float.")
        
        if COMMON_FIELDS['EXOTIC_TYPE'].upper() == 'KO_BARRIER':
            COMMON_FIELDS['BARRIER_TYPE'] = ql.Barrier.UpOut
        elif COMMON_FIELDS['EXOTIC_TYPE'].upper() == 'KI_BARRIER':
            COMMON_FIELDS['BARRIER_TYPE'] = ql.Barrier.UpIn
    
    # Double barrier options
    elif COMMON_FIELDS['EXOTIC_TYPE'].upper() in ['KO_DB_BARRIER', 'KI_DB_BARRIER', 'KIKO', 'KOKI']:
        COMMON_FIELDS['UPPER_BARRIER'] = UPPER_BARRIER
        COMMON_FIELDS['LOWER_BARRIER'] = LOWER_BARRIER
        try:
            COMMON_FIELDS['UPPER_BARRIER'] = float(COMMON_FIELDS['UPPER_BARRIER'])
        except ValueError:
            errors.append("Invalid UPPER_BARRIER. Must be a float.")
        try:
            COMMON_FIELDS['LOWER_BARRIER'] = float(COMMON_FIELDS['LOWER_BARRIER'])
        except ValueError:
            errors.append("Invalid LOWER_BARRIER. Must be a float.")

        if COMMON_FIELDS['EXOTIC_TYPE'].upper() == 'KO_DB_BARRIER':
            COMMON_FIELDS['BARRIER_TYPE'] = ql.DoubleBarrier.KnockOut
        elif COMMON_FIELDS['EXOTIC_TYPE'].upper() == 'KI_DB_BARRIER':
            COMMON_FIELDS['BARRIER_TYPE'] = ql.DoubleBarrier.KnockIn
        elif COMMON_FIELDS['EXOTIC_TYPE'].upper() == 'KIKO':
            COMMON_FIELDS['BARRIER_TYPE'] = ql.DoubleBarrier.KIKO
        elif COMMON_FIELDS['EXOTIC_TYPE'].upper() == 'KOKI':
            COMMON_FIELDS['BARRIER_TYPE'] = ql.DoubleBarrier.KOKI

    # Asian options
    # elif COMMON_FIELDS['EXOTIC_TYPE'].upper() in ['ASIAN']:

    # Create rebate
    COMMON_FIELDS['REBATE'] = 0.0

    # Construct payoff & option
    if COMMON_FIELDS['EXOTIC_TYPE'].upper() == 'VANILLA':
        COMMON_FIELDS['PAYOFF'] = ql.PlainVanillaPayoff(COMMON_FIELDS['TYPE'], COMMON_FIELDS['STRIKE'])
        COMMON_FIELDS['OPTION'] = ql.VanillaOption(COMMON_FIELDS['PAYOFF'], COMMON_FIELDS['EXERCISE'])
    elif COMMON_FIELDS['EXOTIC_TYPE'].upper() in ['KO_BARRIER', 'KI_BARRIER']:
        COMMON_FIELDS['PAYOFF'] = ql.PlainVanillaPayoff(COMMON_FIELDS['TYPE'], COMMON_FIELDS['STRIKE'])
        COMMON_FIELDS['OPTION'] = ql.BarrierOption(COMMON_FIELDS['BARRIER_TYPE'], COMMON_FIELDS['UPPER_BARRIER'], COMMON_FIELDS['REBATE'], COMMON_FIELDS['PAYOFF'], COMMON_FIELDS['EXERCISE'])
    elif COMMON_FIELDS['EXOTIC_TYPE'].upper() in ['KO_DB_BARRIER', 'KI_DB_BARRIER', 'KIKO', 'KOKI']:
        COMMON_FIELDS['PAYOFF'] = ql.PlainVanillaPayoff(COMMON_FIELDS['TYPE'], COMMON_FIELDS['STRIKE'])
        COMMON_FIELDS['OPTION'] = ql.DoubleBarrierOption(COMMON_FIELDS['BARRIER_TYPE'], COMMON_FIELDS['LOWER_BARRIER'], COMMON_FIELDS['UPPER_BARRIER'], COMMON_FIELDS['REBATE'], COMMON_FIELDS['PAYOFF'], COMMON_FIELDS['EXERCISE'])
    else:
        errors.append("Invalid EXOTIC_TYPE. Supported types: VANILLA, KO_BARRIER, KI_BARRIER, KO_DB_BARRIER, KI_DB_BARRIER, KIKO, KOKI.")

    
    # Construct process
    TODAY = ql.Date().todaysDate()
    DOMESTIC_RF = ql.YieldTermStructureHandle(ql.FlatForward(TODAY, 0.05, ql.Actual365Fixed()))
    FOREIGN_RF = ql.YieldTermStructureHandle(ql.FlatForward(TODAY, 0.01, ql.Actual365Fixed()))
    VOLATILITY_TS = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(TODAY, ql.NullCalendar(), 0.1, ql.Actual365Fixed()))
    SPOT_HANDLE = ql.QuoteHandle(ql.SimpleQuote(COMMON_FIELDS['SPOT']))
    PROCESS = ql.BlackScholesMertonProcess(SPOT_HANDLE, FOREIGN_RF, DOMESTIC_RF, VOLATILITY_TS)
    
    # Construct engine
    if COMMON_FIELDS['EXOTIC_TYPE'].upper() == 'VANILLA':
        COMMON_FIELDS['ENGINE'] = ql.AnalyticEuropeanEngine(PROCESS)
    elif COMMON_FIELDS['EXOTIC_TYPE'].upper() in ['KO_BARRIER', 'KI_BARRIER']:
        COMMON_FIELDS['ENGINE'] = ql.AnalyticBarrierEngine(PROCESS)
    elif COMMON_FIELDS['EXOTIC_TYPE'].upper() in ['KO_DB_BARRIER', 'KI_DB_BARRIER', 'KIKO', 'KOKI']:
        COMMON_FIELDS['ENGINE'] = ql.AnalyticDoubleBarrierEngine(PROCESS)
    
    # Calculate option price
    COMMON_FIELDS['OPTION'].setPricingEngine(COMMON_FIELDS['ENGINE'])
    
    # Create a new dictionary to store the calculated fields
    CALCULATED_FIELDS = {}
    
    CALCULATED_FIELDS['OPTION_PRICE'] = COMMON_FIELDS['OPTION'].NPV()
    CALCULATED_FIELDS['DELTA'] = COMMON_FIELDS['OPTION'].delta()
    CALCULATED_FIELDS['GAMMA'] = COMMON_FIELDS['OPTION'].gamma()
    CALCULATED_FIELDS['VEGA'] = COMMON_FIELDS['OPTION'].vega()
    # CALCULATED_FIELDS['THETA'] = COMMON_FIELDS['OPTION'].theta()

    # Print the option type
    print(f"\nEXOTIC_TYPE: {EXOTIC_TYPE}")
    # Print the processed fields
    print("CALCULATED_FIELDS:")
    print(CALCULATED_FIELDS)

    # Call the function that performs calculations using the processed fields
    # OPTION_PRICE = calculate_option_price(processed_fields)
    print(f"\nOPTION_PRICE: {CALCULATED_FIELDS['OPTION_PRICE']}")

    # Return common fields
    return {CALCULATED_FIELDS}


class BulkOptionPriceRequest(BaseModel):

    # List of OptionPriceRequest objects
    payloads: List[OptionPriceRequest]

@app.post('/bulkwebpricer')
async def calculate_option_prices_bulk(payload: BulkOptionPriceRequest):
    payloads = payload.payloads
    num_rows = len(payloads)
    option_values = []  # List to store the calculated option prices

    async with httpx.AsyncClient() as client:
        tasks = []  # List to store the asynchronous tasks

        try:
            # Iterate through each payload item
            for i, payload in enumerate(payloads):
                # Extract the input parameters from the payload
                input_params = {}
                for field, value in payload:
                    input_params[field] = value or ""

                # Make a request to the specific route /webpricer
                task = asyncio.create_task(client.post('http://localhost:80/webpricer', json=input_params))
                tasks.append((i, task))  # Store the task along with the index

            # Wait for all the tasks to complete
            for i, task in tasks:
                response = await task
                response.raise_for_status()  # Optional: Raise an exception for non-2xx responses

                # Retrieve the option price from the response
                option_price = response.json()
                #  = data["option_price"]

                # Store the option price along with the index
                option_values.append((i, option_price))

        except Exception as e:
            # Handle any exceptions and log the error
            print(f"Error occurred: {e}")

        finally:
            # Ensure all tasks are completed before exiting
            await asyncio.gather(*[task for _, task in tasks if not task.done()])

    # Sort the option prices based on the original order
    option_values.sort(key=lambda x: x[0])

    # Extract the option prices without the index
    option_prices = [price for _, price in option_values]


    # Return the list of option prices as the final response
    return {"option_prices": option_prices}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80)