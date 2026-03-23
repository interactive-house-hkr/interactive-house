
// ---------------------
// ----- Libraries -----
// ---------------------
#include <Wire.h>
#include <LiquidCrystal_I2C.h>
#include <Servo.h>
#include <ArduinoJson.h>

LiquidCrystal_I2C lcd(0x3F, 16, 2);
Servo doorServo;

unsigned long lastHeartbeat = 0;


// ------------------------
// ----- Device State -----
//-------------------------
bool lightPower = true;
bool fanPower = true;
int fanPin = 6;
String doorState = "open";



// ------------------------
// ----- Send Connect -----
// ------------------------
void sendConnect() {
  StaticJsonDocument<512> doc;

  doc["type"] = "CONNECT";

  JsonObject devices = doc["devices"].to<JsonObject>();

  // Controller
  JsonObject controller = devices["arduino-1"].to<JsonObject>();
  controller["device_uuid"] = "arduino-1";
  controller["type"] = "controller";
  controller["status"]["connected"] = true;

  // Light
  JsonObject light = devices["light-1"].to<JsonObject>();
  light["device_uuid"] = "light-1";
  light["type"] = "light";

  JsonObject cap = light["capabilities"].to<JsonObject>();
  cap["power"]["type"] = "boolean";
  cap["power"]["writable"] = true;

  light["state"]["power"] = lightPower;

  // Door
  JsonObject door = devices["door-1"].to<JsonObject>();
  door["device_uuid"] = "door-1";
  door["type"] = "door";

  JsonObject doorCap = door["capabilities"].to<JsonObject>();
  doorCap["open"]["type"] = "string";
  doorCap["open"]["writable"] = true;

  door["state"]["open"] = doorState;

  // Fan
  JsonObject fan = devices["fan-1"].to<JsonObject>();
  fan["device__uuid"] = "fan-1";
  fan["type"] = "fan";

  JsonObject fanCap = fan["capabilities"].to<JsonObject>;
  fanCap["power"]["type"] = "boolean";
  fanCap["power"]["writable"] = true;

  fan["state"]["power"] = fanPower;

  serializeJson(doc, Serial);
  Serial.println();
}


// --------------------------
// ----- Send Heartbeat -----
// --------------------------
void sendHeartbeat() {
  StaticJsonDocument<128> doc;
  doc["type"] = "HEARTBEAT";
  doc["device_uuid"] = "arduino-1";

  serializeJson(doc, Serial);
  Serial.println();
}


// --------------------------------
// ----- Send Acknowledgement -----
// --------------------------------

void sendAck(const char* device, JsonObject state) {
  StaticJsonDocument<256> doc;

  doc["type"] = "COMMAND_ACK";
  doc["device_uuid"] = device;
  doc["status"] = "ok";

  doc["reported_state"] = state;
  serializeJson(doc, Serial);
  Serial.println();
}

void setup() {
  pinMode(13, OUTPUT);
  pinMode(5, OUTPUT);
  pinMode(fanPin, Output)

  doorServo.attach(9);
  doorServo.write(0);

  Serial.begin(9600);

  lcd.begin();
  lcd.backlight();
  lcd.print("Smart House");

  delay(1000);
  sendConnect();
}


// ---------------------------
// ----- Recieve Command -----
// ---------------------------
void loop() {
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();

    StaticJsonDocument<256> doc;
    DeserializationError err = deserializeJson(doc, input);

    if (err) {
      Serial.println("{\"error\":\"invalid_json\"}");
      return;
    }
    
    const char* type = doc["type"];
    const char* device = doc["device_uuid"];

    // Only process commands
    if (strcmp(type, "COMMAND") == 0) {

      JsonObject state = doc["state"];
      // -----------------
      // ----- Light -----
      // -----------------
      if (strcmp(device, "light-1") == 0) {
        if (state.containsKey("power")) {
          lightPower = state["power"];

          digitalWrite(13, lightPower ? HIGH : LOW);
          digitalWrite(5, lightPower ? HIGH : LOW);

          lcd.clear();
          lcd.print(lightPower ? "Lights ON" : "Lights OFF");

          StaticJsonDocument<64> s;
          s["power"] = lightPower;
          sendAck("light-1", s.as<JsonObject>());
        }
      }
      // ----------------
      // ----- DOOR -----
      // ----------------
      if (strcmp(device, "door-1") == 0) {
        if (state.containsKey("open")) {
          doorState = state["open"].as<String>();

          if (doorState == "open") {
            doorServo.write(180);
            lcd.clear();
            lcd.print("Door OPEN");
          } else {
            doorServo.write(0);
            lcd.clear();
            lcd.print("Door CLOSED");
          }

          StaticJsonDocument<64> s;
          s["open"] = doorState;
          sendAck("door-1", s.as<JsonObject>());
        }
      }

      // Fan
      if(strcmp(device, "fan-1") == 0 ){
        if(state.containsKey("power")){
          fanPower = state["power"];

          digitalWrite(fanPin, fanPower ? HIGH : LOW);

          lcd.clear();
          lcd.print(fanPower ? "FAN ON" : "FAN OFF");

          StaticJsonDocument<64> s;
          s["power"] = fanPower;
          sendAck("fan-1", s.as<JsonObject>());
        }

      }
    }
  }
  // -----------------------------
  // ----- Heartbeat each 5s -----
  // -----------------------------
  if (millis() - lastHeartbeat > 5000) {
    sendHeartbeat();
    lastHeartbeat = millis();
  }

  delay(50);
}