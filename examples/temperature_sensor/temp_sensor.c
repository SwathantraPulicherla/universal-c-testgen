#include "temp_sensor.h"
#include <math.h>

float read_temperature_celsius(int raw_adc) {
    if (raw_adc < 0 || raw_adc > 1023) {
        return -273.15f; // Error value
    }
    return (raw_adc / 1023.0f) * 165.0f - 40.0f;
}

int validate_temperature_range(float temp_c) {
    return (temp_c >= -40.0f && temp_c <= 125.0f);
}

const char* get_temperature_status(float temp_c) {
    if (temp_c < -10.0f) return "COLD";
    if (temp_c > 85.0f) return "HOT";
    if (temp_c > 120.0f) return "CRITICAL";
    return "NORMAL";
}

float celsius_to_fahrenheit(float temp_c) {
    return (temp_c * 9.0f / 5.0f) + 32.0f;
}