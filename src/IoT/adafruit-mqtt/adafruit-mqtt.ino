#include <ESP8266WiFi.h>
#include <AdafruitIO_WiFi.h>
#include <Adafruit_GFX.h>
#include <Adafruit_ST7735.h>
#include <Fonts/FreeSerif9pt7b.h>
#include <SPI.h>
#define WIFI_SSID       "TiNa95"
#define WIFI_PASS       "25101995"
 
#define IO_USERNAME    "quandinh10"
#define IO_KEY         "aio_zGuF35Mldcl20zVSQFWG9fOzGt8Q"
 

#define TFT_CS D2
#define TFT_RST D0
#define TFT_DC D1
Adafruit_ST7735 tft = Adafruit_ST7735(TFT_CS, TFT_DC, TFT_RST);
// Connect to Wi-Fi and Adafruit IO handel 
AdafruitIO_WiFi io(IO_USERNAME, IO_KEY, WIFI_SSID, WIFI_PASS);
 
// Create a feed object that allows us to send data to
AdafruitIO_Feed *detectFeed = io.feed("detect-signal");
AdafruitIO_Feed *faceFeed = io.feed("face-recognize");

//
#define led_red D8
#define led_green D4
void setup() 
{
  pinMode(led_red,OUTPUT);
  pinMode(led_green,OUTPUT);
  tft.initR(INITR_BLACKTAB);
  tft.setRotation(3);
  tft.fillScreen(ST7735_BLACK);
  tft.setFont(&FreeSerif9pt7b);
  tft.setTextColor(ST7735_RED);
  tft.setCursor(15, 60);
  tft.println("PRESS BUTTON");
  // Enable the serial port so we can see updates
  Serial.begin(115200);
 
  // Connect to Adafruit IO
  io.connect();
  detectFeed->onMessage(capture);
  faceFeed->onMessage(detectFace);
  // wait for a connection
  while(io.status() < AIO_CONNECTED) 
  {
    Serial.print(".");
    delay(500);
  }
  Serial.println();
  Serial.println("Connected to broker");
}
 
void loop() 
{
  io.run();
}

void capture(AdafruitIO_Data *data){
  tft.fillScreen(ST7735_BLACK);
  tft.setFont(&FreeSerif9pt7b);
  tft.setTextColor(ST7735_RED);
  tft.setCursor(10, 60);
  tft.println("CAPTURING....");
}
void detectFace(AdafruitIO_Data *data){
  if (strcmp(data->value(),"Stranger")==0){
    digitalWrite(led_red,HIGH);
    tft.fillScreen(ST7735_BLACK);
    tft.setFont(&FreeSerif9pt7b);
    tft.setTextColor(ST7735_RED);
    tft.setCursor(40, 60);
    tft.println("GET OUT");
  }
  else{
    digitalWrite(led_green,HIGH);
    tft.fillScreen(ST7735_BLACK);
    tft.setFont(&FreeSerif9pt7b);
    tft.setTextColor(ST7735_RED);
    tft.setCursor(5, 60);
    tft.println("WELCOME HOME");
    tft.setFont(&FreeSerif9pt7b);
    tft.setTextColor(ST7735_RED);
    tft.setCursor(60, 85);
    tft.println(data->value());
  }
  delay(5000);
  digitalWrite(led_red,LOW);
  digitalWrite(led_green,LOW);
  tft.fillScreen(ST7735_BLACK);
  tft.setFont(&FreeSerif9pt7b);
  tft.setTextColor(ST7735_RED);
  tft.setCursor(15, 60);
  tft.println("PRESS BUTTON");
  
}