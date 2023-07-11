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
    OPTION_PARAM = {
        'CURRENCY_PAIR': CURRENCY_PAIR,
        'MATURITY': MATURITY,
        'STRIKE': STRIKE,
        'NOTIONAL': NOTIONAL,
        'EXOTIC_TYPE': EXOTIC_TYPE,
        'EXERCISE': EXERCISE,
        'TYPE': TYPE,
        'UPPER_BARRIER': UPPER_BARRIER,
        'LOWER_BARRIER': LOWER_BARRIER,
        'WINDOW_START_DATE': WINDOW_START_DATE,
        'WINDOW_END_DATE': WINDOW_END_DATE,
        'SPOT': SPOT,
        'VOLATILITY': VOLATILITY
    }

    # Create a list to store errors
    errors = []

        # CURRECY_PAIR
    try:
        # Process currency pair
        # If length is 6, assume format is 'USDEUR'
        if len(OPTION_PARAM['CURRENCY_PAIR']) == 6:
            # If the first 3 characters are in the list of currencies, and the last 3 characters are in the list of currencies
            if CURRENCY_PAIR[0:3].upper() in ['USD', 'EUR', 'GBP', 'AUD', 'NZD', 'CAD', 'CHF', 'JPY'] and CURRENCY_PAIR[3:6].upper() in ['USD', 'EUR', 'GBP', 'AUD', 'NZD', 'CAD', 'CHF', 'JPY']:
                # Create new common fields
                OPTION_PARAM['FOREIGN_CURRENCY'] = OPTION_PARAM['CURRENCY_PAIR'][0:3]
                OPTION_PARAM['DOMESTIC_CURRENCY'] = OPTION_PARAM['CURRENCY_PAIR'][3:6]
                # Set the risk free rate for FOREIGN & DOMESTIC currencies
                if OPTION_PARAM['FOREIGN_CURRENCY'] == 'USD':
                    usdrate = 0.05 # can fetch from database or API here.
                    UsdRateGlobal = ql.SimpleQuote(usdrate)
                    OPTION_PARAM['FOREIGN_CURRENCY_RF_RATE'] = ql.QuoteHandle(UsdRateGlobal)
                elif OPTION_PARAM['FOREIGN_CURRENCY'] == 'EUR':
                    eurrate = 0.01
                    EurRateGlobal = ql.SimpleQuote(eurrate)
                    OPTION_PARAM['FOREIGN_CURRENCY_RF_RATE'] = ql.QuoteHandle(EurRateGlobal)
                elif OPTION_PARAM['FOREIGN_CURRENCY'] == 'GBP':
                    gbprate = 0.02
                    GbpRateGlobal = ql.SimpleQuote(gbprate)
                    OPTION_PARAM['FOREIGN_CURRENCY_RF_RATE'] = ql.QuoteHandle(GbpRateGlobal)

                if OPTION_PARAM['DOMESTIC_CURRENCY'] == 'USD':
                    usdrate = 0.05
                    UsdRateGlobal = ql.SimpleQuote(usdrate)
                    OPTION_PARAM['DOMESTIC_CURRENCY_RF_RATE'] = ql.QuoteHandle(UsdRateGlobal)
                elif OPTION_PARAM['DOMESTIC_CURRENCY'] == 'EUR':
                    eurrate = 0.01
                    EurRateGlobal = ql.SimpleQuote(eurrate)
                    OPTION_PARAM['DOMESTIC_CURRENCY_RF_RATE'] = ql.QuoteHandle(EurRateGlobal)
                elif OPTION_PARAM['DOMESTIC_CURRENCY'] == 'GBP':
                    gbprate = 0.02
                    GbpRateGlobal = ql.SimpleQuote(gbprate)
                    OPTION_PARAM['DOMESTIC_CURRENCY_RF_RATE'] = ql.QuoteHandle(GbpRateGlobal)


            else:
                errors.append("CURRENCY_PAIR not supported. Supported currencies: [USD, EUR, GBP, AUD, NZD, CAD, CHF, JPY")
        else:
            errors.append("Invalid CURRENCY_PAIR. Ex: USDEUR")
    except:
        errors.append("Runtime error in CURRENCY_PAIR.")
        return errors

    # MATURITY
    try:
        # Process maturity
        # Check if maturity date is valid
        if len(OPTION_PARAM['MATURITY']) == 9:
            print("Maturity specified in 10Sep2023 format.")
            try:    
                # Convert maturity date to datetime object
                maturity_date = datetime.strptime(OPTION_PARAM['MATURITY'], "%d%b%Y").date()
                if maturity_date > date.today():
                    try:
                        # Convert maturity date to QuantLib Date object
                        OPTION_PARAM['EXPIRY_DATE'] = ql.Date(maturity_date.day, maturity_date.month, maturity_date.year)
                        OPTION_PARAM['DELIVERY_DATE'] = OPTION_PARAM['EXPIRY_DATE'] + 2
                        print(f"Expiry date: {OPTION_PARAM['EXPIRY_DATE']}.")
                        print(f"Delivery date: {OPTION_PARAM['DELIVERY_DATE']}.")

                        # Set calculation date to today's date
                        OPTION_PARAM['EVALUATION_DATE'] = ql.Date(date.today().day, date.today().month, date.today().year)
                        OPTION_PARAM['SETTLEMENT_DATE'] = OPTION_PARAM['EVALUATION_DATE'] + 2
                        NumberOfDaysBetween = OPTION_PARAM['EXPIRY_DATE'] - OPTION_PARAM['EVALUATION_DATE']
                        print(f"Evaluation date: {OPTION_PARAM['EVALUATION_DATE']}.")
                        print(f"Settlement date: {OPTION_PARAM['SETTLEMENT_DATE']}.")
                        print(f"Number of days between expiry and evaluation date: {NumberOfDaysBetween}.")
                        
                        # Set evaluation date
                        ql.Settings.instance().evaluationDate = OPTION_PARAM['EVALUATION_DATE']

                    except RuntimeError:
                        errors.append("Runtime error with MATURITY. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")
                        print(f"Runtime error with MATURITY. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")
                    
                # Check if maturity date is before today's date
                elif maturity_date < date.today():
                    print("MATURITY is before today's date.")
                    errors.append("MATURITY is before today's date.")
            except ValueError:
                errors.append("1 Invalid MATURITY format. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")
        elif len(OPTION_PARAM['MATURITY']) == 2 or len(OPTION_PARAM['MATURITY']) == 3:
            print("Maturity specified as '1m' or '3Y'")
            try:
                if str(OPTION_PARAM['MATURITY'][-1]).upper() in ['D', 'W', 'M', 'Y']:
                    # Maturity specified as '1m' or '3M'
                    # Extract the number
                    period = int(OPTION_PARAM['MATURITY'][0:1])
                    #Extract the time unit
                    time_unit = str(OPTION_PARAM['MATURITY'][-1]).upper()
                    if time_unit == 'D':
                        period = ql.Period(period, ql.Days)
                    elif time_unit == 'W':
                        period = ql.Period(period, ql.Weeks)
                    elif time_unit == 'M':
                        period = ql.Period(period, ql.Months)
                    elif time_unit == 'Y':
                        period = ql.Period(period, ql.Years)
                    # print("period: ", period)

                    # Set calculation date to today's date
                    OPTION_PARAM['EVALUATION_DATE'] = ql.Date(date.today().day, date.today().month, date.today().year)
                    OPTION_PARAM['SETTLEMENT_DATE'] = OPTION_PARAM['EVALUATION_DATE'] + 2
                    print(f"Evaluation Date: {OPTION_PARAM['EVALUATION_DATE']}")
                    print(f"Settlement Date: {OPTION_PARAM['SETTLEMENT_DATE']}")

                    # Set evaluation date
                    ql.Settings.instance().evaluationDate = OPTION_PARAM['EVALUATION_DATE']

                    # Convert expiry date to QuantLib Date object
                    expiry_date = OPTION_PARAM['EVALUATION_DATE'] + period
                    OPTION_PARAM['EXPIRY_DATE'] = ql.Date(expiry_date.dayOfMonth(), expiry_date.month(), expiry_date.year())
                    OPTION_PARAM['DELIVERY_DATE'] = OPTION_PARAM['EXPIRY_DATE'] + 2
                    NumberOfDaysBetween = OPTION_PARAM['EXPIRY_DATE'] - OPTION_PARAM['EVALUATION_DATE']
                    print(f"Expiry date: {OPTION_PARAM['EXPIRY_DATE']}.")
                    print(f"Delivery date: {OPTION_PARAM['DELIVERY_DATE']}.")
                    print(f"Number of days between expiry and evaluation date: {NumberOfDaysBetween}.")
                else:
                    errors.append("2 Invalid MATURITY format. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")
            except KeyError:
                errors.append("3 Invalid MATURITY format. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")
        else:
            errors.append("4 Invalid MATURITY format. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")
    except RuntimeError:
        errors.append("Runtime error with MATURITY. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")
        print("Runtime error with MATURITY. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")
        return errors
    
    # STRIKE
    try:
        # Process strike
        if OPTION_PARAM['STRIKE'] == '':
            errors.append("STRIKE is empty")
        else:
            try:
                if isinstance(float(OPTION_PARAM['STRIKE']), float) and float(OPTION_PARAM['STRIKE']) <= 0:
                    errors.append("STRIKE must be > 0.")
                else:
                    OPTION_PARAM['STRIKE'] = float(OPTION_PARAM['STRIKE'])
            except ValueError:
                errors.append("Invalid STRIKE. Must be a float.")
        print(f"Strike: {OPTION_PARAM['STRIKE']}")    
    except RuntimeError:
        errors.append("Runtime error with STRIKE. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")
        print("Runtime error with STRIKE. Ex: 29Sep2023, 1m, 3M, 1y, 1w, 1d.")
        return errors
    
    # NOTIONAL
    try:
        # Process notional
        if OPTION_PARAM['NOTIONAL'] == '':
            errors.append("NOTIONAL is empty.")
        else:
            try:
                if isinstance(float(OPTION_PARAM['NOTIONAL']), float):
                    if float(OPTION_PARAM['NOTIONAL']) > 0:
                        NotionalGlobal = ql.SimpleQuote(float(OPTION_PARAM['NOTIONAL']))
                        OPTION_PARAM['NOTIONAL_HANDLE'] = ql.QuoteHandle(NotionalGlobal)
                    elif float(OPTION_PARAM['NOTIONAL']) <= 0:
                        errors.append("NOTIONAL must be > 0.")
            except ValueError:
                errors.append("NOTIONAL is not a valid float")

        print(f"Notional: {OPTION_PARAM['NOTIONAL']}")
    except RuntimeError:
        errors.append("Runtime Error with NOTIONAL. Ex: 100.")
        print("Runtime Error with NOTIONAL. Ex: 100.")
        return errors
    
    # SPOT
    try:
        # Process spot    
        if OPTION_PARAM['SPOT'] == '':
            errors.append("SPOT is empty.")
        else:
            try:
                if isinstance(float(OPTION_PARAM['SPOT']), float):
                    if float(OPTION_PARAM['SPOT']) > 0:
                        SpotGlobal = ql.SimpleQuote(float(OPTION_PARAM['SPOT']))
                        OPTION_PARAM['SPOT_HANDLE'] = ql.QuoteHandle(SpotGlobal)
                    elif float(OPTION_PARAM['SPOT']) <= 0:
                        errors.append("SPOT must be > 0.")
            except ValueError:   
                errors.append("SPOT is not a valid float")
                
        print(f"Spot: {OPTION_PARAM['SPOT']}")   
    except RuntimeError:
        errors.append("Runtime Error with SPOT. Ex: 100.")
        print("Runtime Error with SPOT. Ex: 100.")
        return errors
    
    # VOLATILITY
    try:
        # Process volatility
        if OPTION_PARAM['VOLATILITY'] == '':
            errors.append("VOLATILITY is empty.")
        else:
            try:
                if isinstance(float(OPTION_PARAM['VOLATILITY']), float):
                    if float(OPTION_PARAM['VOLATILITY']) > 0:
                        VolatilityGlobal = ql.SimpleQuote(float(OPTION_PARAM['VOLATILITY']))
                        OPTION_PARAM['VOLATILITY_HANDLE'] = ql.QuoteHandle(VolatilityGlobal)
                    elif float(OPTION_PARAM['VOLATILITY']) <= 0:
                        errors.append("VOLATILITY must be > 0.")
            except ValueError:
                errors.append("VOLATILITY is not a valid float")

        print(f"Volatility: {OPTION_PARAM['VOLATILITY']}")
    except RuntimeError:
        errors.append("Runtime Error with VOLATILITY. Ex: 0.2.")
        print("Runtime Error with VOLATILITY. Ex: 0.2.")
        return errors
    
    # EXERCISE
    try:
        ## Process exercise type
        if OPTION_PARAM['EXERCISE'].upper() == 'E':
            OPTION_PARAM['EXERCISE_Q'] = ql.EuropeanExercise(OPTION_PARAM['EXPIRY_DATE'])
            print("EuropeanExercise")
        elif OPTION_PARAM['EXERCISE'].upper() == 'A':
            OPTION_PARAM['EXERCISE_Q'] = ql.AmericanExercise(OPTION_PARAM['EVALUATION_DATE'], OPTION_PARAM['EXPIRY_DATE'])
            print("AmericanExercise")
        else:
            errors.append("Invalid EXERCISE. Ex: E, A.")
            print("Invalid EXERCISE. Ex: E, A.")
    except RuntimeError:
        errors.append("Runtime Error with EXERCISE. Ex: E, A.")
        print("Runtime Error with EXERCISE. Ex: E, A.")
        return errors
    
    # OPTION_TYPE
    try:
        # Process option type
        if str(OPTION_PARAM['TYPE']).upper() == 'CALL':
            OPTION_PARAM['TYPE'] = ql.Option.Call
            print("Call")
            # Set evaluation date
            ql.Settings.instance().evaluationDate = OPTION_PARAM['EVALUATION_DATE']
        elif str(OPTION_PARAM['TYPE']).upper() == 'PUT':
            OPTION_PARAM['TYPE'] = ql.Option.Put
            print("Put")
            # Set evaluation date
            ql.Settings.instance().evaluationDate = OPTION_PARAM['EVALUATION_DATE']
        else:
            errors.append("Invalid TYPE. Ex: CALL, PUT.")
            print("Invalid TYPE. Ex: CALL, PUT.")
    except RuntimeError:
        errors.append("Runtime Error with TYPE. Ex: CALL, PUT.")
        print("Runtime Error with TYPE. Ex: CALL, PUT.")
        return errors
    
    # EXOTIC_TYPE
    try:
        # Barrier options
        if OPTION_PARAM['EXOTIC_TYPE'].upper() in ['KO_BARRIER', 'KI_BARRIER']:
            print("Barrier options")
            if OPTION_PARAM['TYPE'] == ql.Option.Call:

                if OPTION_PARAM['EXOTIC_TYPE'].upper() == 'KO_BARRIER':
                    OPTION_PARAM['BARRIER_TYPE'] = ql.Barrier.UpOut
                    print("Knock Out")
                elif OPTION_PARAM['EXOTIC_TYPE'].upper() == 'KI_BARRIER':
                    OPTION_PARAM['BARRIER_TYPE'] = ql.Barrier.UpIn
                    print("Knock In")

                if OPTION_PARAM['UPPER_BARRIER'] == '':
                    errors.append("UPPER_BARRIER is empty")
                else:
                    try:              
                        if isinstance(float(OPTION_PARAM['UPPER_BARRIER']), float) and float(OPTION_PARAM['UPPER_BARRIER']) > float(OPTION_PARAM['SPOT']):
                            # Convert to float
                            OPTION_PARAM['UPPER_BARRIER'] = float(OPTION_PARAM['UPPER_BARRIER'])
                        elif isinstance(float(OPTION_PARAM['UPPER_BARRIER']), float) and float(OPTION_PARAM['UPPER_BARRIER']) <= float(OPTION_PARAM['SPOT']):
                            errors.append("UPPER_BARRIER must be > SPOT.")
                    except ValueError:
                        errors.append("Invalid UPPER_BARRIER. Must be a float.")
                print(f"UPPER_BARRIER: {OPTION_PARAM['UPPER_BARRIER']}")   
            
            elif OPTION_PARAM['TYPE'] == ql.Option.Put:

                if OPTION_PARAM['EXOTIC_TYPE'].upper() == 'KO_BARRIER':
                    OPTION_PARAM['BARRIER_TYPE'] = ql.Barrier.DownOut
                    print("Knock Out")
                elif OPTION_PARAM['EXOTIC_TYPE'].upper() == 'KI_BARRIER':
                    OPTION_PARAM['BARRIER_TYPE'] = ql.Barrier.DownIn
                    print("Knock In")

                if OPTION_PARAM['LOWER_BARRIER'] == '':
                    errors.append("LOWER_BARRIER is empty")
                else:
                    try:              
                        if isinstance(float(OPTION_PARAM['LOWER_BARRIER']), float) and float(OPTION_PARAM['LOWER_BARRIER']) < float(OPTION_PARAM['SPOT']):
                            # Convert to float
                            OPTION_PARAM['LOWER_BARRIER'] = float(OPTION_PARAM['LOWER_BARRIER'])
                        elif isinstance(float(OPTION_PARAM['LOWER_BARRIER']), float) and float(OPTION_PARAM['LOWER_BARRIER']) >= float(OPTION_PARAM['SPOT']):
                            errors.append("LOWER_BARRIER must be < SPOT.")
                    except ValueError:
                        errors.append("Invalid LOWER_BARRIER. Must be a float.")
                print(f"LOWER_BARRIER: {OPTION_PARAM['LOWER_BARRIER']}")   
            
        # Double barrier options
        elif OPTION_PARAM['EXOTIC_TYPE'].upper() in ['KO_DB_BARRIER', 'KI_DB_BARRIER', 'KIKO', 'KOKI']:
            if OPTION_PARAM['EXOTIC_TYPE'].upper() == 'KO_DB_BARRIER':
                OPTION_PARAM['BARRIER_TYPE'] = ql.DoubleBarrier.KnockOut
            elif OPTION_PARAM['EXOTIC_TYPE'].upper() == 'KI_DB_BARRIER':
                OPTION_PARAM['BARRIER_TYPE'] = ql.DoubleBarrier.KnockIn
            elif OPTION_PARAM['EXOTIC_TYPE'].upper() == 'KIKO':
                OPTION_PARAM['BARRIER_TYPE'] = ql.DoubleBarrier.KIKO
            elif OPTION_PARAM['EXOTIC_TYPE'].upper() == 'KOKI':
                OPTION_PARAM['BARRIER_TYPE'] = ql.DoubleBarrier.KOKI
            
            if OPTION_PARAM['TYPE'] == ql.Option.Call:
                if OPTION_PARAM['UPPER_BARRIER'] == '':
                    errors.append("UPPER_BARRIER is empty")
                else:
                    try:              
                        if isinstance(float(OPTION_PARAM['UPPER_BARRIER']), float) and float(OPTION_PARAM['UPPER_BARRIER']) > float(OPTION_PARAM['SPOT']):
                            # Convert to float
                            OPTION_PARAM['UPPER_BARRIER'] = float(OPTION_PARAM['UPPER_BARRIER'])
                        elif isinstance(float(OPTION_PARAM['UPPER_BARRIER']), float) and float(OPTION_PARAM['UPPER_BARRIER']) <= float(OPTION_PARAM['SPOT']):
                            errors.append("UPPER_BARRIER must be > SPOT.")
                    except ValueError:
                        errors.append("Invalid UPPER_BARRIER. Must be a float.")
                print(f"UPPER_BARRIER: {OPTION_PARAM['UPPER_BARRIER']}")  
                
                if OPTION_PARAM['LOWER_BARRIER'] == '':
                    errors.append("LOWER_BARRIER is empty")
                else:
                    try:              
                        if isinstance(float(OPTION_PARAM['LOWER_BARRIER']), float) and float(OPTION_PARAM['LOWER_BARRIER']) > float(OPTION_PARAM['SPOT']):
                            # Convert to float
                            OPTION_PARAM['LOWER_BARRIER'] = float(OPTION_PARAM['LOWER_BARRIER'])
                        elif isinstance(float(OPTION_PARAM['LOWER_BARRIER']), float) and float(OPTION_PARAM['LOWER_BARRIER']) <= float(OPTION_PARAM['SPOT']):
                            errors.append("LOWER_BARRIER must be > SPOT.")
                    except ValueError:
                        errors.append("Invalid LOWER_BARRIER. Must be a float.")
                print(f"LOWER_BARRIER: {OPTION_PARAM['LOWER_BARRIER']}")  
                print('DoubleBarrier options')
            elif OPTION_PARAM['TYPE'] == ql.Option.Put:
                if OPTION_PARAM['UPPER_BARRIER'] == '':
                    errors.append("UPPER_BARRIER is empty")
                else:
                    try:              
                        if isinstance(float(OPTION_PARAM['UPPER_BARRIER']), float) and float(OPTION_PARAM['UPPER_BARRIER']) < float(OPTION_PARAM['SPOT']):
                            # Convert to float
                            OPTION_PARAM['UPPER_BARRIER'] = float(OPTION_PARAM['UPPER_BARRIER'])
                        elif isinstance(float(OPTION_PARAM['UPPER_BARRIER']), float) and float(OPTION_PARAM['UPPER_BARRIER']) >= float(OPTION_PARAM['SPOT']):
                            errors.append("UPPER_BARRIER must be < SPOT.")
                    except ValueError:
                        errors.append("Invalid UPPER_BARRIER. Must be a float.")
                print(f"UPPER_BARRIER: {OPTION_PARAM['UPPER_BARRIER']}")  
                
                if OPTION_PARAM['LOWER_BARRIER'] == '':
                    errors.append("LOWER_BARRIER is empty")
                else:
                    try:              
                        if isinstance(float(OPTION_PARAM['LOWER_BARRIER']), float) and float(OPTION_PARAM['LOWER_BARRIER']) < float(OPTION_PARAM['SPOT']):
                            # Convert to float
                            OPTION_PARAM['LOWER_BARRIER'] = float(OPTION_PARAM['LOWER_BARRIER'])
                        elif isinstance(float(OPTION_PARAM['LOWER_BARRIER']), float) and float(OPTION_PARAM['LOWER_BARRIER']) >= float(OPTION_PARAM['SPOT']):
                            errors.append("LOWER_BARRIER must be < SPOT.")
                    except ValueError:
                        errors.append("Invalid LOWER_BARRIER. Must be a float.")
                print(f"LOWER_BARRIER: {OPTION_PARAM['LOWER_BARRIER']}")  
                print('DoubleBarrier options')

        # Asian options
        # elif OPTION_PARAM['EXOTIC_TYPE'].upper() in ['ASIAN']:
    except RuntimeError:
        errors.append("RuntimeError in EXOTIC_TYPE selection.")
        print("RuntimeError in EXOTIC_TYPE selection.")
        return errors
    except TypeError:
        errors.append("TypeError in EXOTIC_TYPE selection.")
        print("TypeError in EXOTIC_TYPE selection.")
        return errors
        
    # Construct payoff & option
    try:
        # Create rebate
        OPTION_PARAM['REBATE'] = 0.0

        if OPTION_PARAM['EXOTIC_TYPE'].upper() == 'VANILLA':
            OPTION_PARAM['PAYOFF'] = ql.PlainVanillaPayoff(OPTION_PARAM['TYPE'], OPTION_PARAM['STRIKE'])
            OPTION_PARAM['OPTION'] = ql.VanillaOption(OPTION_PARAM['PAYOFF'], OPTION_PARAM['EXERCISE_Q'])
            print("VanillaOption")
        elif OPTION_PARAM['EXOTIC_TYPE'].upper() in ['KI_BARRIER']:
            OPTION_PARAM['PAYOFF'] = ql.PlainVanillaPayoff(OPTION_PARAM['TYPE'], OPTION_PARAM['STRIKE'])
            OPTION_PARAM['OPTION'] = ql.BarrierOption(OPTION_PARAM['BARRIER_TYPE'], OPTION_PARAM['UPPER_BARRIER'], OPTION_PARAM['REBATE'], OPTION_PARAM['PAYOFF'], OPTION_PARAM['EXERCISE_Q'])
            print("Knock in BarrierOption")
        elif OPTION_PARAM['EXOTIC_TYPE'].upper() in ['KO_BARRIER']:
            OPTION_PARAM['PAYOFF'] = ql.PlainVanillaPayoff(OPTION_PARAM['TYPE'], OPTION_PARAM['STRIKE'])
            OPTION_PARAM['OPTION'] = ql.BarrierOption(OPTION_PARAM['BARRIER_TYPE'], OPTION_PARAM['LOWER_BARRIER'], OPTION_PARAM['REBATE'], OPTION_PARAM['PAYOFF'], OPTION_PARAM['EXERCISE_Q'])
            print("Knock out BarrierOption")
        elif OPTION_PARAM['EXOTIC_TYPE'].upper() in ['KO_DB_BARRIER', 'KI_DB_BARRIER', 'KIKO', 'KOKI']:
            OPTION_PARAM['PAYOFF'] = ql.PlainVanillaPayoff(OPTION_PARAM['TYPE'], OPTION_PARAM['STRIKE'])
            OPTION_PARAM['OPTION'] = ql.DoubleBarrierOption(OPTION_PARAM['BARRIER_TYPE'], OPTION_PARAM['LOWER_BARRIER'], OPTION_PARAM['UPPER_BARRIER'], OPTION_PARAM['REBATE'], OPTION_PARAM['PAYOFF'], OPTION_PARAM['EXERCISE_Q'])
            print("DoubleBarrierOption")
        else:
            errors.append("Invalid EXOTIC_TYPE. Supported types: VANILLA, KO_BARRIER, KI_BARRIER, KO_DB_BARRIER, KI_DB_BARRIER, KIKO, KOKI.")
            print('Invalid EXOTIC_TYPE. Supported types: VANILLA, KO_BARRIER, KI_BARRIER, KO_DB_BARRIER, KI_DB_BARRIER, KIKO, KOKI.')
    except RuntimeError:
        errors.append("Runtime Error with constructing payoff & option.")
        print("Runtime Error with constructing payoff & option.")
        return errors
    
    #Settings such as calendar, evaluationdate; daycount
    try:           
        calendar = ql.UnitedStates(ql.UnitedStates.GovernmentBond)
        ql.Settings.instance().evaluationDate = OPTION_PARAM['EVALUATION_DATE']
        DayCountRate = ql.Actual360()
        DayCountVolatility = ql.ActualActual(ql.ActualActual.ISDA)
    except RuntimeError:
        errors.append("RuntimeError in calendar settings.")
        print("RuntimeError in calendar settings.")
        return errors
    
    # Construct process
    try:
        # TODAY = ql.Date().todaysDate()
        DOMESTIC_RF_RATE = ql.YieldTermStructureHandle(ql.FlatForward(0, calendar, OPTION_PARAM['DOMESTIC_CURRENCY_RF_RATE'], DayCountRate))
        FOREIGN_RF_RATE = ql.YieldTermStructureHandle(ql.FlatForward(0, calendar, OPTION_PARAM['FOREIGN_CURRENCY_RF_RATE'], DayCountRate))
        VOLATILITY_TS = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(0, calendar, OPTION_PARAM['VOLATILITY_HANDLE'], DayCountVolatility))

        # Processes
        # BS Process
        PROCESS = ql.BlackScholesMertonProcess(OPTION_PARAM['SPOT_HANDLE'], FOREIGN_RF_RATE, DOMESTIC_RF_RATE, VOLATILITY_TS)
        # GK Process
        # PROCESS = ql.GarmanKohlagenProcess(OPTION_PARAM['SPOT_HANDLE'], FOREIGN_RF_RATE, DOMESTIC_RF_RATE, VOLATILITY_TS)
        # Vanna Volga Process ?    
    except:
        errors.append("RuntimeError in constructing process.")
        print("RuntimeError in constructing process.")
        return errors
    
    # Construct engine
    try:
        if OPTION_PARAM['EXOTIC_TYPE'].upper() == 'VANILLA': # and OPTION_PARAM['EXERCISE'] == 'E':
            OPTION_PARAM['ENGINE'] = ql.AnalyticEuropeanEngine(PROCESS)
            print("AnalyticEuropeanEngine")
        # elif OPTION_PARAM['EXOTIC_TYPE'].upper() == 'VANILLA' and OPTION_PARAM['EXERCISE'] == 'A':
        #     OPTION_PARAM['ENGINE'] = ql.AnalyticDigitalAmericanEngine(PROCESS)
        #     print("AnalyticDigitalAmericanEngine")
        elif OPTION_PARAM['EXOTIC_TYPE'].upper() in ['KO_BARRIER', 'KI_BARRIER']:
            OPTION_PARAM['ENGINE'] = ql.AnalyticBarrierEngine(PROCESS)
            print("AnalyticBarrierEngine")
        elif OPTION_PARAM['EXOTIC_TYPE'].upper() in ['KO_DB_BARRIER', 'KI_DB_BARRIER', 'KIKO', 'KOKI']:
            OPTION_PARAM['ENGINE'] = ql.AnalyticDoubleBarrierEngine(PROCESS)
            print("AnalyticDoubleBarrierEngine")
    except RuntimeError:
        errors.append("RuntimeError in constructing engine.")
        print("RuntimeError in constructing engine.")
        return errors
    
    # CALCULATED_FIELDS
    try:
        # Set the pricing engine
        OPTION_PARAM['OPTION'].setPricingEngine(OPTION_PARAM['ENGINE'])

        # Create a new dictionary to store the calculated fields
        CALCULATED_FIELDS = {}
        CALCULATED_FIELDS['PREMIUM'] = 0
        CALCULATED_FIELDS['DELTA'] = 0.0
        CALCULATED_FIELDS['GAMMA'] = 0.0
        CALCULATED_FIELDS['VEGA'] = 0.0

        # Calculate the fields
        if str(OPTION_PARAM['EXOTIC_TYPE']).upper() == 'VANILLA':
            ql.Settings.instance().evaluationDate = OPTION_PARAM['EVALUATION_DATE']
            CALCULATED_FIELDS['OPTION_NPV'] = OPTION_PARAM['OPTION'].NPV()
            CALCULATED_FIELDS['PREMIUM'] = OPTION_PARAM['OPTION'].NPV()*OPTION_PARAM['NOTIONAL']/float(OPTION_PARAM['SPOT'])
            CALCULATED_FIELDS['DELTA'] = OPTION_PARAM['OPTION'].delta()*OPTION_PARAM['NOTIONAL']
            CALCULATED_FIELDS['GAMMA'] = OPTION_PARAM['OPTION'].gamma()*OPTION_PARAM['NOTIONAL']*float(OPTION_PARAM['SPOT'])/100
            CALCULATED_FIELDS['VEGA'] = OPTION_PARAM['OPTION'].vega()*OPTION_PARAM['NOTIONAL']*(1/100)/float(OPTION_PARAM['SPOT'])
            # CALCULATED_FIELDS['THETA'] = OPTION_PARAM['OPTION'].theta()*1000000*(1/365)/OPTION_PARAM['SPOT']
        
        # elif str(OPTION_PARAM['EXOTIC_TYPE']).upper() in ['KO_BARRIER', 'KI_BARRIER', 'KO_DB_BARRIER', 'KI_DB_BARRIER', 'KIKO', 'KOKI']:

        # Print the option type
        print(f"\nEXOTIC_TYPE: {EXOTIC_TYPE}")
        # Print the processed fields
        print("CALCULATED_FIELDS:")
        print(CALCULATED_FIELDS)

        # Call the function that performs calculations using the processed fields
        # OPTION_PRICE = calculate_option_price(processed_fields)
        # print(f"\nOPTION_PRICE: {CALCULATED_FIELDS['OPTION_PRICE']}")
    except RuntimeError:
        errors.append("RuntimeError in calculating option price & greeks.")
        print("RuntimeError in calculating option price & greeks.")
        return errors
    
    # Return calculated fields
    return CALCULATED_FIELDS


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
                response = await task # if condition to check if response contains runtime error. where should the if conditon be?
                response.raise_for_status() # HTTP error propagation
                # Catch runtime errors
            
                # Retrieve the option price from the response
                calculated_values = response.json()

                # Store the option price along with the index
                option_values.append((i, calculated_values))
                print(f"{i}-Payload below:")
                print(option_values)
        except Exception as e:
            # Handle any exceptions and log the error
            print(f"Error occurred: {e}")

        finally:
            # Ensure all tasks are completed before exiting
            await asyncio.gather(*[task for _, task in tasks if not task.done()])

    # print("Payload below 1:")
    # print(option_values)
    # Sort the option prices based on the original order
    option_values.sort(key=lambda x: x[0])

    updated_data = []
    for index, value in option_values:
        if isinstance(value, list):
            error_dict = {"RuntimeError": value[0]}
            updated_data.append((index, error_dict))
        else:
            updated_data.append((index, value))

    print("Payload below:")
    print(updated_data)
    # # Extract the option prices without the index
    # option_prices = [price for _, price in option_values]

    # Return the list of option prices as the final response
    return updated_data

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80)