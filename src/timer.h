// Copyright (c) 2022 Niklas Bettgen

#ifndef SRC_TIMER_H_
#define SRC_TIMER_H_

#include "Arduino.h"


// Timer class for easy time handling and scheduling
class Timer {
 public:
    // Type definitions
    using ms = uint32_t;

    // Constructor
    explicit    Timer(const ms duration = 0);

    // Timer setup and routines
    void        setDuration(const ms duration);
    void        reset();
    bool        start(const Timer::ms duration = 0);
    bool        restart(const Timer::ms duration = 0);

    // Timer properties and current status
    ms          getDuration() const;
    bool        check() const;
    bool        isRunning() const;
    bool        isSet() const;
    ms          getStartTime() const;
    ms          getElapsedTime() const;
    float       getElapsedPercentage() const;

 private:
    bool        m_running = false;      // Flag indicating that the timer is running
    ms          m_start_time = 0;       // Start time captured when the timer was started
    ms          m_duration = 0;         // Duration of the timer
};

#endif  // SRC_TIMER_H_
