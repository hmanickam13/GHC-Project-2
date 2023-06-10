from fastapi import FastAPI, status
from fastapi.exceptions import HTTPException
from fastapi.responses import PlainTextResponse
from fastapi import Request
from pydantic import BaseModel
import time

import uvicorn
import quantlib as ql

app = FastAPI()

# Error handling
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exception: HTTPException):
    # Return "msg" instead of {"detail": "msg"} for nicer frontend formatting
    return PlainTextResponse(str(exception.detail), status_code=exception.status_code)

# Define the request model
class OptionPriceRequest(BaseModel):
    interestRate: float
    maturity: float
    strikePrice: float
    stockPrice: float
    volatility: float
    dividend: float

# Endpoint to calculate vanilla option price
@app.post('/vanillaoptionprice')
async def calculate_option_price(request: OptionPriceRequest):
    # Extract the input parameters from the request
    interest_rate = request.interestRate
    maturity = request.maturity
    strike_price = request.strikePrice
    stock_price = request.stockPrice
    volatility = request.volatility
    dividend = request.dividend

    # Print payload variables
    print("Received payload variables:")
    print(f"Interest Rate: {interest_rate}")
    print(f"Maturity: {maturity}")
    print(f"Strike Price: {strike_price}")
    print(f"Stock Price: {stock_price}")
    print(f"Volatility: {volatility}")
    print(f"Dividend: {dividend}")

    # Calculate option price
    print("Calculating option price...")

    # Simulate delay to mimic the calculation process
    time.sleep(2)  # Adjust the delay time as needed
    
    # Code to calculate the price of a European call option using Black-Scholes formula
    option_type = ql.Option.Call  # Assuming it's a call option
    risk_free_rate = ql.SimpleQuote(interest_rate)
    dividend_yield = ql.SimpleQuote(dividend)
    underlying_price = ql.SimpleQuote(stock_price)
    volatility_quote = ql.SimpleQuote(volatility)

    payoff = ql.PlainVanillaPayoff(option_type, strike_price)
    exercise = ql.EuropeanExercise(maturity)

    process = ql.BlackScholesMertonProcess(
        ql.QuoteHandle(underlying_price),
        ql.YieldTermStructureHandle(ql.FlatForward(0, ql.TARGET(), risk_free_rate, ql.Actual365Fixed())),
        ql.YieldTermStructureHandle(ql.FlatForward(0, ql.TARGET(), dividend_yield, ql.Actual365Fixed())),
        ql.BlackVolTermStructureHandle(ql.BlackConstantVol(0, ql.TARGET(), volatility_quote, ql.Actual365Fixed()))
    )

    option = ql.VanillaOption(payoff, exercise)
    option.setPricingEngine(ql.AnalyticEuropeanEngine(process))

    option_price = option.NPV()

    # Print the calculated option price
    print("Option price calculated:", option_price)

    # Simulate delay to mimic sending the price to Google Sheets
    time.sleep(1)  # Adjust the delay time as needed

    # Return the calculated option price
    return {"option_price": option_price}


# Unprotected health check
@app.get("/health")
async def health():
    return {"status": "ok"}

if __name__ == '__main__':
    uvicorn.run(app, host='0.0.0.0', port=80)
