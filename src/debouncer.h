#ifndef _DEBOUNCER_H_
#define _DEBOUNCER_H_

// Include necessary headers
#include "timer.h"
#include "helpers.h"


// Debouncer class
template<class T>
class Debouncer
{
public:
    // Constructor
    Debouncer(Timer::ms threshold = 0): m_timer(threshold) {}

    // Updates the internal value and performs the debouncing
    void debounce(T value) {
        // Start timer on the first update
        if (!m_timer.isRunning())
            m_timer.start();

        // Reset timer upon value change
        if (value != m_value)
        {
            m_timer.restart();
            m_value = value;
        }

        if (m_timer.check())
            m_valid = true;

        // Fetch value changes
        m_changed = false;
        if (m_timer.check())
        {
            // Set valid flag once debounced
            m_valid = true;
            if (m_debounced != m_value)
            {
                m_debounced = m_value;
                m_changed = true;
            }
        }
    }

    T       get() const { return m_debounced; }             // Retreive the debounced value
    T       getRaw() const { return m_value; }              // Retreive the raw value
    bool    isValid() const { return m_valid; }             // Check if the value is properly debounced
    void    reset()                                         // Reset internal states
                { m_valid = false; m_changed = false; m_timer.reset(); }
    bool    hasChanged()                                    // Fetch any edge
                { if (m_changed) { m_changed = false; return true; } return false; }
    void    setThreshold(Timer::ms threshold)               // Set the debouncing threshold
                { m_timer.setDuration(threshold); }

protected:
    T       m_value;
    T       m_debounced;
    bool    m_changed = false;
    bool    m_valid = false;
    Timer   m_timer;
};


// Debounced button auxiliar class
class DebouncedButton: public Debouncer<bool>
{
public:
    // Constructor
    DebouncedButton(Timer::ms threshold = 0) : Debouncer(threshold) {}

    // Hardware setup
    void setPin(const pin input_pin, const bool invert = false, const bool int_pullup = true)
    {
        m_pin = input_pin;
        m_invert = invert;
        pinMode(input_pin, (int_pullup ? INPUT_PULLUP : INPUT));
    }

    // Status of button
    pin getPin() const { return m_pin; }
    bool readPin() const { return digitalRead(m_pin) == m_invert ? HIGH : LOW; }
    void debounce() { Debouncer::debounce(readPin()); }
    bool isPressed() const { return get(); }

protected:
    pin     m_pin;
    bool    m_invert;
};

#endif /* _DEBOUNCER_H_ */