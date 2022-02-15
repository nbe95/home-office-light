// Copyright (c) 2022 Niklas Bettgen

#ifndef SRC_VECTOR_H_
#define SRC_VECTOR_H_

#include "Arduino.h"


// Declaration of StaticVector template class
// To prevent heap fragmentation, a StaticVector acts as a fixed size container.
// Unlike a real std::vector, data is never allocated dynamically.
template<class T, int CAPACITY>
class StaticVector {
 public:
    StaticVector();                                     // Default constructor
    explicit StaticVector(const T& init);               // Contructor providing explicit value initialization

    int         push(const T& value);                   // Adds one item to the front of the vector
    int         pushBack(const T& value);               // Adds one item to the back of the vector
    T           pop();                                  // Fetches and removes one item from the front of the vector
    T           popBack();                              // Fetches and removes one item from the back of the vector

    bool        has(const T& value)         { return find(value) != end(); }    // Checks if the vector holds a specific element
    T&          get(const int index)        { return m_data[index]; }           // Fetches the reference to a specific item within the vector
    T           getCopy(const int index)    { return m_data[index]; }           // Copies and returns a specific item within the vector
    T&          operator[](const int index);                                    // Operator for data access by square brackets

    void        clear();                                // Deletes all items of the vector
    void        dumps(Stream* const stream);            // Dumps the vector's contents to a stream object

    using iter = T*;                                    // Pointer type for data iteration
    iter        begin() { return &m_data[0]; }          // Returns a pointer to the start of the vector
    iter        end()   { return &m_data[m_size]; }     // Returns a pointer to the (current) end of the vector
    iter        find(const T& value);                   // Finds a specific value inside the vector

    int         size() const            { return m_size; }                  // Returns the vector's current size
    int         capacity() const        { return CAPACITY; }                // Returns the vector's total capacity
    bool        empty() const           { return size() == 0; }             // Checks whether the vector is currently empty
    bool        full() const            { return size() >= capacity(); }    // Checks whether the vector is currently fully occupied
    size_t      storageSize() const     { return sizeof(T) * size(); }      // Retreives the total size the vector allocates in memory

 protected:
    T           m_data[CAPACITY];                       // Internal array of fixed size
    int         m_size;                                 // Number of currently occupied items
};


// Definition of template class functions

template<class T, int CAPACITY>
StaticVector<T, CAPACITY>::StaticVector() :
m_size(0) {}


template<class T, int CAPACITY>
StaticVector<T, CAPACITY>::StaticVector(const T& init) :
StaticVector() {
    for (int i = 0; i < CAPACITY; i++) {
        m_data[i] = init;
    }
}


template<class T, int CAPACITY>
int StaticVector<T, CAPACITY>::push(const T& value) {
    // Dont' do anything if already full
    if (full())
        return -1;

    // Shift back existing items
    for (int i = size(); i >= 1; i--)
        m_data[i] = m_data[i - 1];

    // Set first element and return index
    m_size++;
    m_data[0] = value;
    return 0;
}


template<class T, int CAPACITY>
int StaticVector<T, CAPACITY>::pushBack(const T& value) {
    // Dont' do anything if already full
    if (full())
        return -1;

    // Set last element and return index
    int index = m_size++;
    m_data[index] = value;
    return index;
}


template<class T, int CAPACITY>
T StaticVector<T, CAPACITY>::pop() {
    // Fetch first value
    T value = m_data[0];

    // Shift forward existing items
    for (int i = 0; i < size() - 1; i++)
        m_data[i] = m_data[i + 1];

    // Decrement item count
    m_size--;
    return value;
}


template<class T, int CAPACITY>
T StaticVector<T, CAPACITY>::popBack() {
    return m_data[--m_size];
}


template<class T, int CAPACITY>
T& StaticVector<T, CAPACITY>::operator[](const int index) {
    return get(index);
}


template<class T, int CAPACITY>
void StaticVector<T, CAPACITY>::clear() {
    m_size = 0;
}


template<class T, int CAPACITY>
void StaticVector<T, CAPACITY>::dumps(Stream* const stream) {
    char line[80] = {0};
    int i = 0;
    for (T* it = begin(); it < end(); it++) {
        snprintf_P(line, sizeof(line), PSTR("[%03d]  "), i++);
        stream->print(line);
        stream->println(*it);
    }

    snprintf_P(line, sizeof(line), PSTR("Value/total size: %d/%dB, %d/%d items allocated at: 0x%04X"),
        sizeof(T),
        sizeof(*this),
        size(),
        capacity(),
        ADDR(m_data));
    stream->println(line);
}


template<class T, int CAPACITY>
typename StaticVector<T, CAPACITY>::iter StaticVector<T, CAPACITY>::find(const T& value) {
    for (const T* it = begin(); it < end(); it++)
        if (*it == value)
            return it;
    return end();
}


#endif  // SRC_VECTOR_H_
