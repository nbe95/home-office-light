#ifndef SRC_DEBOUNCER_H_
#define SRC_DEBOUNCER_H_

// Include necessary headers
#include "./timer.h"
#include "./helpers.h"


// Debouncer class
template<class T>
class Debouncer {
 public:
    // Constructor
    explicit Debouncer(Timer::ms threshold = 0):
    m_timer(threshold) {}

    // Updates the internal value and performs the debouncing
    void debounce(T value) {
        // Start timer on the first update
        if (!m_timer.isRunning())
            m_timer.start();

        // Reset timer upon value change
        if (value != m_value) {
            m_timer.restart();
            m_value = value;
        }

        if (m_timer.check())
            m_ready = true;

        // Fetch value changes
        m_changed = false;
        if (m_timer.check()) {
            // Set ready flag once debounced
            m_ready = true;
            if (m_debounced != m_value) {
                m_debounced = m_value;
                m_changed = true;
            }
        }
    }

    // Retreive the debounced or raw value
    T get() const { return m_debounced; }
    T getRaw() const { return m_value; }
    bool isReady() const { return m_ready; }

    // Set the debouncing threshold
    void setThreshold(Timer::ms threshold) { m_timer.setDuration(threshold); }

    // Reset internal states
    void reset() {
        m_ready = false;
        m_changed = false;
        m_timer.reset();
    }

    // Fetch any signal edge
    bool hasChanged() {
        if (m_changed) {
            m_changed = false;
            return true;
        }
        return false;
    }

 protected:
    T       m_value;
    T       m_debounced;
    bool    m_changed = false;
    bool    m_ready = false;
    Timer   m_timer;
};


// Auxiliar class for buttons, switches and binary sensors
class DebouncedSwitch: public Debouncer<bool> {
 public:
    // Constructor
    explicit DebouncedSwitch(Timer::ms threshold = 0):
    Debouncer(threshold) {}

    // Hardware setup
    void setInputPin(const pin input_pin, const bool invert = false, const bool int_pullup = true) {
        m_pin = input_pin;
        m_invert = invert;
        pinMode(input_pin, (int_pullup ? INPUT_PULLUP : INPUT));
    }
    pin getInputPin() const { return m_pin; }
    bool getInputInvert() const { return m_invert; }

    // Debouncing
    bool readStatus() const { return m_pin ? (digitalRead(m_pin) == LOW) ^ m_invert : false; }
    void debounce() { if (m_pin) Debouncer::debounce(readStatus()); }

    // Switch status
    bool isOpen() const { return get(); }
    bool isClosed() const { return get(); }

 protected:
    pin     m_pin;
    bool    m_invert;
};

#endif  // SRC_DEBOUNCER_H_
