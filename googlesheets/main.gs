function onOpen() {
  let ui = SpreadsheetApp.getUi();
  ui.createMenu("Option Type")
    .addItem('Vanilla Call')
    .add
}

var ipAddress = 'http://34.132.52.185';

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

function sendRequest() {
  var url = ipAddress + "/vanillaoptionprice";  // The server's URL

  var sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  
  // Retrieve the values from the specified cells
  var maturityDate = sheet.getRange("B7").getValue();
  var calculationDate = sheet.getRange("B8").getValue();
  var spot = sheet.getRange("B9").getValue();
  var strike = sheet.getRange("B10").getValue();
  var volatility = sheet.getRange("B11").getValue();
  var dividendRate = sheet.getRange("B12").getValue();
  var riskFreeRate = sheet.getRange("B13").getValue();
  var optionType = sheet.getRange("B15").getValue();
  var dayCount = sheet.getRange("B16").getValue();
  var calendar = sheet.getRange("B17").getValue();

  // Construct the payload object
  var payload = {
    maturityDate: maturityDate,
    calculationDate: calculationDate,
    spot: spot,
    strike: strike,
    volatility: volatility,
    dividendRate: dividendRate,
    riskFreeRate: riskFreeRate,
    optionType: optionType,
    dayCount: dayCount,
    calendar: calendar
  };

  // Convert the payload object to JSON string
  var payloadJson = JSON.stringify(payload);

  // Configure the options for the HTTP request
  var options = {
    method: "post",
    contentType: "application/json",
    payload: payloadJson
  };

  // Send the HTTP request to the server
  var response = UrlFetchApp.fetch(url, options);
  var responseData = JSON.parse(response.getContentText());

  // Retrieve the option price from the server's response
  var optionPrice = responseData.option_price;

  // Set the received option price in cell B5
  var cell = sheet.getRange("B5");
  cell.setValue(optionPrice);
}
