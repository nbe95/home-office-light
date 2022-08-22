// Copyright (c) 2022 Niklas Bettgen

#ifndef SRC_CONTAINER_VECTOR_H_
#define SRC_CONTAINER_VECTOR_H_


// Declaration of StaticVector template class
// To prevent heap fragmentation, a StaticVector acts as a fixed size container.
// Unlike a real std::vector, data is never allocated dynamically.
template<class T>
class StaticVector {
 public:
    explicit StaticVector(
        const int capacity,
        const T& fallback = T());                           // Contructor providing explicit value initialization

    int             push(const T& value);                   // Add one item to the front of the vector
    int             pushBack(const T& value);               // Add one item to the back of the vector
    T               pop();                                  // Fetch and remove one item from the front of the vector
    T               popBack();                              // Fetch and remove one item from the back of the vector

    const T&        get(const int index) const;                                     // Fetch a read-only reference to a specific element
    bool            has(const T& value) const { return find(value) != end(); }      // Check if the vector holds a specific element

    void            clear();                                                        // Delete all items of the vector
    void            dump(Stream* const stream, const int indent = 0) const;         // Dump the vector's contents to a stream object

    using iter = const T*;                                                      // Pointer type for data iteration
    iter            begin() const           { return &m_data[0]; }              // Return a pointer to the start of the vector
    iter            end() const             { return &m_data[m_size]; }         // Return a pointer to the (current) end of the vector
    iter            find(const T& value) const;                                 // Find a specific value inside the vector

    int             size() const            { return m_size; }                  // Return the vector's current size
    int             capacity() const        { return m_capacity; }              // Return the vector's total capacity
    bool            empty() const           { return size() == 0; }             // Check whether the vector is currently empty
    bool            full() const            { return size() >= capacity(); }    // Check whether the vector is currently fully occupied
    size_t          storageSize() const     { return sizeof(T) * capacity(); }  // Retrieve the total size the vector allocates in memory

    const T&        operator[](const int index) const { return get(index); }     // Square bracket operator for read-only data access

 protected:
    const int       m_capacity;                             // Total number of items allocated in memory
    const T         m_fallback;                             // Fallback value for out-of-bounds access etc.
    int             m_size;                                 // Number of currently occupied items
    T*              m_data;                                 // Internal array of fixed size
};


// Definition of template class functions

template<class T>
StaticVector<T>::StaticVector(
    const int capacity,
    const T& fallback) :
m_capacity(capacity),
m_fallback(fallback),
m_size(0) {
    m_data = (T*)malloc(sizeof(T) * capacity);
    for (int i = 0; i < capacity; i++) {
        m_data[i] = fallback;
    }
}


template<class T>
int StaticVector<T>::push(const T& value) {
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


template<class T>
int StaticVector<T>::pushBack(const T& value) {
    // Dont' do anything if already full
    if (full())
        return -1;

    // Set last element and return index
    int index = m_size++;
    m_data[index] = value;
    return index;
}


template<class T>
T StaticVector<T>::pop() {
    // Fetch first value
    T value = m_data[0];

    // Shift forward existing items
    for (int i = 0; i < size() - 1; i++)
        m_data[i] = m_data[i + 1];

    // Decrement item count
    m_size--;
    return value;
}


template<class T>
T StaticVector<T>::popBack() {
    return m_data[--m_size];
}


template<class T>
const T& StaticVector<T>::get(const int index) const {
    if (index < 0 || index >= size())
        return m_fallback;
    return m_data[index];
}


template<class T>
void StaticVector<T>::clear() {
    m_size = 0;
}


template<class T>
void StaticVector<T>::dump(Stream* const stream, const int indent) const {
    char line[80] = {0};
    int i = 0;
    for (auto it = begin(); it < end(); it++) {
        snprintf_P(line, sizeof(line), PSTR("[%03d]  "), i++);
        for (int j = 0; j < indent; j++)
            stream->print(' ');
        stream->print(line);
        stream->println(*it);
    }

    snprintf_P(line, sizeof(line), PSTR("Size: value=%zuB, total=%zuB, %d/%d items allocated at: %p"),
        sizeof(T),
        storageSize(),
        size(),
        capacity(),
        (void*)m_data);
    for (int j = 0; j < indent; j++)
        stream->print(' ');
    stream->println(line);
}


template<class T>
typename StaticVector<T>::iter StaticVector<T>::find(const T& value) const {
    for (const T* it = begin(); it < end(); it++)
        if (*it == value)
            return it;
    return end();
}


#endif  // SRC_CONTAINER_VECTOR_H_
