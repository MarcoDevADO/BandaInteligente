#define rele 12
#define boton 2
#include <Servo.h>

unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;
bool moviendoServo = false;
unsigned long tiempoInicioServo = 0;
const unsigned long duracionServo = 2000;  // 2 segundos

int servoPin = 11;
int servoPos = 0;
Servo myServo;

int on = 1;
int valorboton;
int memoria = 0;
int valanterior = 0;
int comando;
int ledV = 8;
int ledN = 9;

void setup() {
  Serial.begin(9600);
  myServo.attach(servoPin);
  pinMode(ledV, OUTPUT);
  pinMode(ledN, OUTPUT);
  pinMode(rele, OUTPUT);
  pinMode(boton, INPUT_PULLUP);

  digitalWrite(rele, LOW);
}

void loop() {

  if (moviendoServo && (millis() - tiempoInicioServo >= duracionServo)) {
    servoPos = 0;
    myServo.write(servoPos);
    moviendoServo = false; // El servo terminó su movimiento
  }
  
  valorboton = digitalRead(boton);

  // Detectar flanco de subida con antirebote
  if ((on == valorboton) && (valanterior != on)) {
    if ((millis() - lastDebounceTime) > debounceDelay) {
      memoria = 1 - memoria; // Cambiar estado
      lastDebounceTime = millis(); // Guardar el momento del cambio
    }
  }
  valanterior = valorboton;

  // Control del relé
  digitalWrite(rele, memoria);

  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim(); // Elimina espacios, saltos de línea, etc.
    input.toUpperCase(); // Asegura que sea mayúscula (opcional si quieres)

    if (input == "RELE_ON") {
      memoria = 1;
    } else if (input == "RELE_OFF") {
      memoria = 0;
    } else if (input == "SERVO_ON") {
    servoPos = 180;
    myServo.write(servoPos);
    moviendoServo = true;
    tiempoInicioServo = millis(); // Guarda el momento de inicio
    } else if (input == "LED_ON"){
      digitalWrite(ledV,HIGH);
      digitalWrite(ledN,LOW);
    } else if (input == "LED_OFF"){
      digitalWrite(ledV,LOW);
      digitalWrite(ledN,HIGH);
    }else if (input == "LED_OFFALL"){
      digitalWrite(ledV,LOW);
      digitalWrite(ledN,LOW);
    }else if (input == "DETENER_BANDA"){
      memoria = 0;
    }else if (input == "ENCENDER_BANDA"){
      memoria = 1;
    }
  }
}