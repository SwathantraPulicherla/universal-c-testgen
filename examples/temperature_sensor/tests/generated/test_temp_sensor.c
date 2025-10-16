```c
#include "unity.h"
#include "temp_sensor.h"

void setUp(void) {
    // set stuff up here
}

void tearDown(void) {
    // clean stuff up here
}

void test_read_temperature_celsius_normal(void) {
    TEST_ASSERT_FLOAT_WITHIN(0.1, -40.0f, read_temperature_celsius(0));
    TEST_ASSERT_FLOAT_WITHIN(0.1, 8.87f, read_temperature_celsius(300));
    TEST_ASSERT_FLOAT_WITHIN(0.1, 125.0f, read_temperature_celsius(1023));
}

void test_read_temperature_celsius_edge(void) {
    TEST_ASSERT_FLOAT_WITHIN(0.1, -40.0f, read_temperature_celsius(0));
    TEST_ASSERT_FLOAT_WITHIN(0.1, 125.0f, read_temperature_celsius(1023));
}

void test_read_temperature_celsius_error(void) {
    TEST_ASSERT_EQUAL_FLOAT(-273.15f, read_temperature_celsius(-1));
    TEST_ASSERT_EQUAL_FLOAT(-273.15f, read_temperature_celsius(1024));
}

void test_validate_temperature_range_normal(void) {
    TEST_ASSERT_TRUE(validate_temperature_range(25.0f));
    TEST_ASSERT_TRUE(validate_temperature_range(-20.0f));
    TEST_ASSERT_TRUE(validate_temperature_range(100.0f));
}

void test_validate_temperature_range_edge(void) {
    TEST_ASSERT_TRUE(validate_temperature_range(-40.0f));
    TEST_ASSERT_TRUE(validate_temperature_range(125.0f));
}

void test_validate_temperature_range_out_of_range(void) {
    TEST_ASSERT_FALSE(validate_temperature_range(-41.0f));
    TEST_ASSERT_FALSE(validate_temperature_range(126.0f));
}

void test_celsius_to_fahrenheit_normal(void) {
    TEST_ASSERT_FLOAT_WITHIN(0.1, 32.0f, celsius_to_fahrenheit(0.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.1, 77.0f, celsius_to_fahrenheit(25.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.1, 212.0f, celsius_to_fahrenheit(100.0f));
}

void test_celsius_to_fahrenheit_negative(void) {
    TEST_ASSERT_FLOAT_WITHIN(0.1, -40.0f, celsius_to_fahrenheit(-40.0f));
}

void test_celsius_to_fahrenheit_edge(void) {
    TEST_ASSERT_FLOAT_WITHIN(0.1, -40.0f, celsius_to_fahrenheit(-40.0f));
    TEST_ASSERT_FLOAT_WITHIN(0.1, 257.0f, celsius_to_fahrenheit(125.0f));
}
```