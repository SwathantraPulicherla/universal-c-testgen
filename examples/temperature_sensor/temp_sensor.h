#ifndef TEMP_SENSOR_H
#define TEMP_SENSOR_H

float read_temperature_celsius(int raw_adc);
int validate_temperature_range(float temp_c);
const char* get_temperature_status(float temp_c);
float celsius_to_fahrenheit(float temp_c);

#endif