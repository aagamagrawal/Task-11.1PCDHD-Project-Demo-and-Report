#include <ArduinoBLE.h>
#include <DHT.h>

// Define sensor pins
#define FLAME_SENSOR_1_PIN 12
#define FLAME_SENSOR_2_PIN 11
#define FLAME_SENSOR_3_PIN 10
#define DHT_PIN 9
#define MQ2_PIN A0
#define CO_PIN A1

// Define threshold values
#define FLAME_THRESHOLD 90
#define TEMP_THRESHOLD 38
#define MQ2_THRESHOLD 35
#define CO_THRESHOLD 55

DHT dht(DHT_PIN, DHT11);

BLEService sensorService("180C"); // Custom BLE service

BLEUnsignedCharCharacteristic flameChar("2A56", BLERead | BLENotify);
BLEFloatCharacteristic tempChar("2A6E", BLERead | BLENotify);
BLEUnsignedCharCharacteristic mq2Char("2A77", BLERead | BLENotify);
BLEUnsignedCharCharacteristic coChar("2A79", BLERead | BLENotify);

void setup() {
  Serial.begin(9600);
  while (!Serial);

  // Initialize sensors
  pinMode(FLAME_SENSOR_1_PIN, INPUT);
  pinMode(FLAME_SENSOR_2_PIN, INPUT);
  pinMode(FLAME_SENSOR_3_PIN, INPUT);
  dht.begin();

  // Initialize BLE
  if (!BLE.begin()) {
    Serial.println("starting BLE failed!");
    while (1);
  }

  BLE.setLocalName("FireDetectionRobot");
  BLE.setAdvertisedService(sensorService);

  // Add characteristics to service
  sensorService.addCharacteristic(flameChar);
  sensorService.addCharacteristic(tempChar);
  sensorService.addCharacteristic(mq2Char);
  sensorService.addCharacteristic(coChar);

  BLE.addService(sensorService);

  BLE.advertise();
  Serial.println("BLE device active, waiting for connections...");
}

void loop() {
  BLEDevice central = BLE.central();

  if (central) {
    Serial.print("Connected to central: ");
    Serial.println(central.address());

    while (central.connected()) {
      // Read sensor values
      int flame1 = analogRead(FLAME_SENSOR_1_PIN);
      int flame2 = analogRead(FLAME_SENSOR_2_PIN);
      int flame3 = analogRead(FLAME_SENSOR_3_PIN);
      float temperature = dht.readTemperature();
      int mq2 = analogRead(MQ2_PIN);
      int co = analogRead(CO_PIN);

      // Calculate average flame sensor value
      int flameAvg = (flame1 + flame2 + flame3) / 3;

      // Update characteristics
      flameChar.writeValue(flameAvg);
      tempChar.writeValue(temperature);
      mq2Char.writeValue(mq2);
      coChar.writeValue(co);

      delay(1000);
    }

    Serial.print("Disconnected from central: ");
    Serial.println(central.address());
  }
}
