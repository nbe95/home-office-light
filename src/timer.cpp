// Copyright (c) 2022 Niklas Bettgen

#include "./timer.h" //NOLINT

// Constructor for a timer with or without specific duration
Timer::Timer(const Timer::ms duration) {
    setDuration(duration);
}

// Sets the timer duration
void Timer::setDuration(const Timer::ms duration) {
    m_duration = duration;
}

// Resets the timer
void Timer::reset() {
    m_start_time = 0;
    m_running = false;
}

// Starts the timer if not done yet
bool Timer::start(const Timer::ms duration) {
    if (duration > 0)
        setDuration(duration);

    if (isRunning())
        return false;
    m_start_time = millis();
    m_running = true;
    return true;
}

// Resets and, if provided, restarts the timer with a new duration
bool Timer::restart(const Timer::ms duration) {
    reset();
    return start(duration);
}

// Gets the configured timer duration
Timer::ms Timer::getDuration() const {
    return m_duration;
}

// Checks wheter the specified duration is already expired
bool Timer::check() const {
    return (isRunning() ? getElapsedTime() > getDuration() : false);
}

// Checks if the timer is currently running
bool Timer::isRunning() const {
    return m_running;
}

// Checks if a valid duration has been set
bool Timer::isSet() const {
    return getDuration() != 0;
}

// Returns the time when the timer was started
Timer::ms Timer::getStartTime() const {
    return (isRunning() ? m_start_time : 0);
}

// Returns the amount of elapsed milliseconds
Timer::ms Timer::getElapsedTime() const {
    return (isRunning() ? millis() - getStartTime() : 0);
}

// Returns the amount of elapsed time as a float value between 0 and 1
float Timer::getElapsedPercentage() const {
    if (!getDuration())
        return 0;
    float p = (float)getElapsedTime() / getDuration();
    return max(0, min(p, 1)); //NOLINT
}
