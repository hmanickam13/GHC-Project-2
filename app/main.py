from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse
from fastapi import Request
from pydantic import BaseModel

import time
import logging

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
    print(f"Request received from IP address: {client_ip}")
    return {"status": "ok"}

# Define the request model
class OptionPriceRequest(BaseModel):
    maturityDate: float
    calculationDate: float
    spot: float
    strike: float
    volatility: float
    dividendRate: float
    riskFreeRate: float
    optionType: str
    dayCount: str
    calendar: str

# Endpoint to calculate vanilla option price
@app.post('/vanillaoptionprice')
async def calculate_option_price(request: OptionPriceRequest):
    # Extract the input parameters from the request
    maturity_date_str = request.maturityDate
    calculation_date_str = request.calculationDate
    spot_price = request.spot
    strike_price = request.strike
    volatility = request.volatility
    dividend_rate = request.dividendRate
    risk_free_rate = request.riskFreeRate
    option_type_str = request.optionType
    day_count_str = request.dayCount
    calendar_str = request.calendar

    # Print the extracted input parameters
    print("Extracted input parameters:")
    print(f"Maturity Date: {maturity_date_str}")
    print(f"Calculation Date: {calculation_date_str}")
    print(f"Spot Price: {spot_price}")
    print(f"Strike Price: {strike_price}")
    print(f"Volatility: {volatility}")
    print(f"Dividend Rate: {dividend_rate}")
    print(f"Risk-Free Rate: {risk_free_rate}")
    print(f"Option Type: {option_type_str}")
    print(f"Day Count: {day_count_str}")
    print(f"Calendar: {calendar_str}")

    # Convert date strings to QuantLib Dates
    maturity_date = ql.Date(int(maturity_date_str[3:5]), int(maturity_date_str[0:2]), int(maturity_date_str[6:10]))
    calculation_date = ql.Date(int(calculation_date_str[3:5]), int(calculation_date_str[0:2]), int(calculation_date_str[6:10]))

    # Convert day count and calendar strings to QuantLib objects
    day_count = ql.DayCounter(day_count_str)
    calendar = ql.Calendar(calendar_str)

    # Determine option type
    option_type = ql.Option.Call if option_type_str.lower() == 'call' else ql.Option.Put

    # Set evaluation date
    ql.Settings.instance().evaluationDate = calculation_date

    # Construct the European option
    payoff = ql.PlainVanillaPayoff(option_type, strike_price)
    exercise = ql.EuropeanExercise(maturity_date)
    european_option = ql.VanillaOption(payoff, exercise)
    
    # Construct the Black-Scholes-Merton process
    print(f"Constructing BSM process... {calendar_str}")
    spot_handle = ql.QuoteHandle(ql.SimpleQuote(spot_price))
    flat_ts = ql.YieldTermStructureHandle(ql.FlatForward(0, calendar, risk_free_rate, day_count))
    dividend_yield = ql.YieldTermStructureHandle(ql.FlatForward(0, calendar, dividend_rate, day_count))
    flat_vol_ts = ql.BlackVolTermStructureHandle(ql.BlackConstantVol(0, calendar, volatility, day_count))
    bsm_process = ql.BlackScholesMertonProcess(spot_handle, dividend_yield, flat_ts, flat_vol_ts)

    # Set pricing engine and calculate option price
    european_option.setPricingEngine(ql.AnalyticEuropeanEngine(bsm_process))
    option_price = european_option.NPV()

    # Return the calculated option price
    return {"option_price": option_price}


if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80)