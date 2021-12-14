#ifndef SRC_TIMER_H_
#define SRC_TIMER_H_


// Simple timer helper class
class Timer {
 public:
    typedef    uint32_t ms;                        // Type definition for internal use of milliseconds (unsigned long)

    explicit   Timer(const ms duration = 0) :      // Constructor for a timer with or without specific duration
                  m_start_time(0), m_running(false) { setDuration(duration); }

    void       setDuration(const ms duration)      // Sets the timer duration
                   { m_duration = duration; }
    ms         getDuration() const                 // Gets the configured timer duration
                   { return m_duration; }

    void       reset()                             // Resets the timer
                   { m_start_time = 0; m_running = false; }
    bool       start()                             // Starts the timer if not done yet
                   { if (isRunning()) return false; m_start_time = millis(); m_running = true; return true; } //NOLINT
    bool       start(const Timer::ms duration)     // Sets a duration and starts the timer
                   { setDuration(duration); return start(); }
    bool       restart()                           // Resets and immediately restarts the timer
                   { reset(); start(); }

    bool       check() const                       // Checks wheter the specified duration is already expired
                   { return (isRunning() ? getElapsedTime() > getDuration() : false); }
    bool       isRunning() const                   // Checks if the timer is currently running
                   { return m_running; }
    bool       isSet() const                       // Checks if a valid duration has been set
                   { return getDuration() != 0; }
    ms         getStartTime() const                // Returns the time when the timer was started
                   { return (isRunning() ? m_start_time : 0); }
    ms         getElapsedTime() const              // Returns the amount of elapsed milliseconds
                   { return (isRunning() ? millis() - getStartTime() : 0); }
    float      getElapsedPercentage() const        // Returns the amount of elapsed time as a float value between 0 and 1
                   { if (!getDuration()) return 0; float p = (float)getElapsedTime() / getDuration(); return max(0, min(p, 1)); } //NOLINT

 private:
    bool       m_running;          // Flag indicating that the timer is running
    ms         m_start_time;       // Start time captured when the timer was started
    ms         m_duration;         // Duration of the timer
};

#endif  // SRC_TIMER_H_
