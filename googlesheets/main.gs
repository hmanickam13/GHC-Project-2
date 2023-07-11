var ipAddress ="http://34.27.249.120:80"

function test() {
  var url = ipAddress + "/health";  // The server's URL

  var options = {
    method: "get",
    muteHttpExceptions: true
  };

  var response = UrlFetchApp.fetch(url, options);
  var content = response.getContentText();

  Logger.log(content);
}

function triggerSendRequest() {
  var endTime = new Date().getTime() + 2 * 60 * 1000; // 2 minutes from now

  while (new Date().getTime() < endTime) {
    sendBulkRequest();
    // sendRequest();
    console.log("Refreshing...");
    Utilities.sleep(3000); // Sleep for 10 seconds
  }
}

function sendEmptyPostRequest() {
  var url = ipAddress + "/example";  // Replace with your server's URL

  var options = {
    method: "post",
    contentType: "application/json"
  };

  // Send the empty POST request to the server
  var response = UrlFetchApp.fetch(url, options);
  var responseData = response.getContentText();
  
  // Log the response data
  console.log(responseData);
}

function sendPutRequest() {
  var url = ipAddress + "/example";  // Replace with your server's URL

  var payload = {
    message: "This is an empty PUT request from AppScript."
  };

  var options = {
    method: "put",
    contentType: "application/json",
    payload: JSON.stringify(payload)
  };

  // Send the empty POST request to the server
  var response = UrlFetchApp.fetch(url, options);
  var responseData = response.getContentText();
  
  // Log the response data
  console.log(responseData);
}


function sendRequest() {
  var url = "http://34.27.249.120:80/webpricer";  // The server's URL

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  var row = 7
  // Retrieve the values from the specified cells for the given row
  var CURRENCY_PAIR = sheet.getRange(row, 2).getValue().toString();
  var MATURITY = sheet.getRange(row, 3).getValue().toString();
  var STRIKE = sheet.getRange(row, 4).getValue().toString();
  var NOTIONAL = sheet.getRange(row, 5).getValue().toString();
  var EXOTIC_TYPE = sheet.getRange(row, 6).getValue().toString();
  var EXERCISE = sheet.getRange(row, 7).getValue().toString();
  var TYPE = sheet.getRange(row, 8).getValue().toString();
  var UPPER_BARRIER = sheet.getRange(row, 9).getValue().toString();
  var LOWER_BARRIER = sheet.getRange(row, 10).getValue().toString();
  var WINDOW_START_DATE = sheet.getRange(row, 11).getValue().toString();
  var WINDOW_END_DATE = sheet.getRange(row, 12).getValue().toString();
  var SPOT = sheet.getRange(row, 13).getValue().toString();
  var VOLATILITY = sheet.getRange(row, 14).getValue().toString();

  // Construct the payload object for the row
  var payload = {
    CURRENCY_PAIR: CURRENCY_PAIR,
    MATURITY: MATURITY,
    STRIKE: STRIKE,
    NOTIONAL: NOTIONAL,
    EXOTIC_TYPE: EXOTIC_TYPE,
    EXERCISE: EXERCISE,
    TYPE: TYPE,
    UPPER_BARRIER: UPPER_BARRIER,
    LOWER_BARRIER: LOWER_BARRIER,
    WINDOW_START_DATE: WINDOW_START_DATE,
    WINDOW_END_DATE: WINDOW_END_DATE,
    SPOT: SPOT,
    VOLATILITY: VOLATILITY
  };

  // Convert the payload object to JSON string
  var payloadJson = JSON.stringify(payload);

  // Configure the options for the HTTP request
  var options = {
    method: "post",
    contentType: "application/json",
    payload: payloadJson, // payload is a json string
    muteHttpExceptions: false
  };

  // Send the HTTP request to the server
  var response = UrlFetchApp.fetch(url, options);
  var responseData = JSON.parse(response.getContentText());

  console.log(responseData[0])

  if (responseData[0].includes("RuntimeError")) {
    console.log("Entered 1");
    var RuntimeError = responseData[0];
    // console.log(RuntimeError.length);
    var cell = sheet.getRange(row, 1);
    cell.setValue(RuntimeError);
  }
  else // Retrieve the CALCULATED_FIELDS from the server's response
    {
    var optionPrice = responseData.OPTION_NPV;
    var cell = sheet.getRange(row, 15); 
    cell.setValue(optionPrice);
    var pct_notional_foreign = responseData.PREMIUM;
    var cell = sheet.getRange(row, 16); 
    cell.setValue(pct_notional_foreign);
    var delta = responseData.DELTA;
    var cell = sheet.getRange(row, 18);
    cell.setValue(delta);
    var gamma = responseData.GAMMA;
    var cell = sheet.getRange(row, 19);
    cell.setValue(gamma);
    var vega = responseData.VEGA;
    var cell = sheet.getRange(row, 20);
    cell.setValue(vega);
}
}


//  Break down sendRequest into a single row, then create a for loop which packages all json objects and then sends to server
function sendBulkRequest() {
  var url = ipAddress + "/bulkwebpricer";  // The server's URL

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();

  var row = 5;
  var cellValue = sheet.getRange(row, 2).getValue(); // B5 column value
  var payloads = [];

  // Iterate while B column is filled
  while (cellValue) {
    // Retrieve the values from the specified cells
    var CURRENCY_PAIR = sheet.getRange(row, 2).getValue();
    var MATURITY = sheet.getRange(row, 3).getValue();
    var STRIKE = sheet.getRange(row, 4).getValue();
    var NOTIONAL = sheet.getRange(row, 5).getValue();
    var EXOTIC_TYPE = sheet.getRange(row, 6).getValue();
    var EXERCISE = sheet.getRange(row, 7).getValue();
    var TYPE = sheet.getRange(row, 8).getValue();
    var UPPER_BARRIER = sheet.getRange(row, 9).getValue();
    var LOWER_BARRIER = sheet.getRange(row, 10).getValue();
    var WINDOW_START_DATE = sheet.getRange(row, 11).getValue();
    var WINDOW_END_DATE = sheet.getRange(row, 12).getValue();
    var SPOT = sheet.getRange(row, 13).getValue();
    var VOLATILITY = sheet.getRange(row, 14).getValue();

    // Construct the payload object for the row
    var payload = {
      CURRENCY_PAIR: CURRENCY_PAIR,
      MATURITY: MATURITY,
      STRIKE: STRIKE,
      NOTIONAL: NOTIONAL,
      EXOTIC_TYPE: EXOTIC_TYPE,
      EXERCISE: EXERCISE,
      TYPE: TYPE,
      UPPER_BARRIER: UPPER_BARRIER,
      LOWER_BARRIER: LOWER_BARRIER,
      WINDOW_START_DATE: WINDOW_START_DATE,
      WINDOW_END_DATE: WINDOW_END_DATE,
      SPOT: SPOT,
      VOLATILITY: VOLATILITY
    };

    // Add the payload to the payloads array
    payloads.push(payload);

    row++;
    console.log(row)
    cellValue = sheet.getRange(row, 2).getValue(); // Next B column value
  }

  // Use the payloads array as needed


  // Convert the payloads array to JSON string
  // var payloadsJson = JSON.stringify(payloads);

  // Configure the options for the HTTP request
  var options = {
    method: "post",
    contentType: "application/json",
    payload: JSON.stringify({ payloads: payloads }) // Pass payloads array directly as JSON payload
  };

  // Send the HTTP request to the server
  var response = UrlFetchApp.fetch(url, options);
  var responseData = JSON.parse(response.getContentText());
  console.log(responseData);

  var i = 0;
  var row = 5;
  while (i < responseData.length) {
    var optionValues = responseData[i];

    if (optionValues.length === 2 && optionValues[1].hasOwnProperty("RuntimeError")) {
      var runtimeError = optionValues[1].RuntimeError;
      var cell = sheet.getRange(row, 1);
      cell.setValue(runtimeError);
    } else {
      var optionPrice = optionValues[1].OPTION_NPV;
      var cell = sheet.getRange(row, 15); 
      cell.setValue(optionPrice);
      var pctNotionalForeign = optionValues[1].PREMIUM;
      var cell = sheet.getRange(row, 16); 
      cell.setValue(pctNotionalForeign);
      var delta = optionValues[1].DELTA;
      var cell = sheet.getRange(row, 18);
      cell.setValue(delta);
      var gamma = optionValues[1].GAMMA;
      var cell = sheet.getRange(row, 19);
      cell.setValue(gamma);
      var vega = optionValues[1].VEGA;
      var cell = sheet.getRange(row, 20);
      cell.setValue(vega);
    }

    i++;
    row++;
  }

}
