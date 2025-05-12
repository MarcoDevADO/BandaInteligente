#include <Servo.h>

unsigned long lastDebounceTime = 0;
const unsigned long debounceDelay = 50;

bool moviendoServo = false;
unsigned long tiempoInicioServo = 0;
const unsigned long duracionServo = 2000;

Servo myServo;
int servoPin = 11;
int servoPos = 0;

int boton = 2;  // Botón para parar motor (como 'P')
int valorboton;
int valanterior = HIGH;

int ledV = 8;
int ledN = 9;
int derecha = 6;
int izquierda = 7;
int enable = 4;

bool motorActivo = false;
int memoria = 1;  // Banda encendida por defecto

void setup() {
  Serial.begin(9600);
  myServo.attach(servoPin);

  pinMode(boton, INPUT_PULLUP);
  pinMode(enable, INPUT_PULLUP);

  pinMode(ledV, OUTPUT);
  pinMode(ledN, OUTPUT);
  pinMode(izquierda, OUTPUT);
  pinMode(derecha, OUTPUT);

  Serial.println("Sistema iniciado");
}

void loop() {
  // Detener motor si se presiona el botón (como 'P')
  valorboton = digitalRead(boton);
  if ((valorboton == LOW) && (valanterior == HIGH)) {
    if ((millis() - lastDebounceTime) > debounceDelay) {
      analogWrite(derecha, 0);
      analogWrite(izquierda, 0);
      motorActivo = false;
      Serial.println("PUENTE H: Banda detenida (botón)");
      lastDebounceTime = millis();
    }
  }
  valanterior = valorboton;

  // Control del servo
  if (moviendoServo && (millis() - tiempoInicioServo >= duracionServo)) {
    myServo.write(0);
    moviendoServo = false;
    Serial.println("SERVO: Movimiento completado");
  }

  // Control de la banda (si memoria = 1 y enable = LOW)
  if (memoria == 1 && digitalRead(enable) == LOW) {
    if (!motorActivo) {
      analogWrite(derecha, 180);
      Serial.println("MOTOR: Banda en movimiento");
      motorActivo = true;
    }
  } else {
    if (motorActivo) {
      analogWrite(derecha, 0);
      Serial.println("MOTOR: Banda detenida");
      motorActivo = false;
    }
  }

  // Comandos Serial
  if (Serial.available()) {
    String input = Serial.readStringUntil('\n');
    input.trim();
    input.toUpperCase();

    if (input == "D") {
      analogWrite(izquierda, 255);
      analogWrite(derecha, 0);
      Serial.println("DIRECCIÓN: Derecha");
    } else if (input == "I") {
      analogWrite(izquierda, 0);
      analogWrite(derecha, 255);
      Serial.println("DIRECCIÓN: Izquierda");
    } else if (input == "SERVO_ON") {
      myServo.write(180);
      moviendoServo = true;
      tiempoInicioServo = millis();
      Serial.println("SERVO: Activado");
    } else if (input == "LED_ON") {
      digitalWrite(ledV, HIGH);
      digitalWrite(ledN, LOW);
      Serial.println("LED: Verde encendido, Naranja apagado");
    } else if (input == "LED_OFF") {
      digitalWrite(ledV, LOW);
      digitalWrite(ledN, HIGH);
      Serial.println("LED: Verde apagado, Naranja encendido");
    } else if (input == "LED_OFFALL") {
      digitalWrite(ledV, LOW);
      digitalWrite(ledN, LOW);
      Serial.println("LED: Ambos apagados");
    } else if (input == "ENCENDER_BANDA") {
      memoria = 1;
      Serial.println("BANDA: Encendida (comando)");
    } else if (input == "DETENER_BANDA") {
      memoria = 0;
      Serial.println("BANDA: Detenida (comando)");
    } else if (input == "P") {
      analogWrite(derecha, 0);
      analogWrite(izquierda, 0);
      motorActivo = false;
      Serial.println("PUENTE H: Banda detenida (comando 'P')");
    } else {
      Serial.print("COMANDO DESCONOCIDO: ");
      Serial.println(input);
    }
  }
}