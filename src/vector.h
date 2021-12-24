#ifndef SRC_VECTOR_H_
#define SRC_VECTOR_H_

// Static Vector helper class
// To prevent heap fragmentation, a StaticVector acts as a fixed size container.
// Unlike a real Vector, data is not dynamically allocated.
template<class T_VALUE, int SIZE>
class StaticVector {
 public:
    // Constructor with default/fallback value
    explicit StaticVector(T_VALUE value = T_VALUE()) :
    m_items(0),
    m_size(SIZE),
    m_default_value(value) {
        for (int i = 0; i < m_size; i++) {
            m_data[i] = value;
        }
    }

    // Destructor for storage cleanup
    ~StaticVector() {
        clear();
    }

    // Adds one item to the front of the vector
    int push(T_VALUE value) {
        // Dont' do anything if already full
        if (isFull())
            return -1;

        // Shift back existing items
        for (int i = items(); i >= 1; i--)
            m_data[i] = m_data[i - 1];

        // Set first element and return index
        m_items++;
        m_data[0] = value;
        return 0;
    }

    // Adds one item to the back of the vector
    int pushBack(T_VALUE value) {
        // Dont' do anything if already full
        if (isFull())
            return -1;

        // Set last element and return index
        int index = m_items++;
        m_data[index] = value;
        return index;
    }

    // Fetches one item within the vector
    T_VALUE get(int index) const {
        // Check index
        if (index < 0 || index >= items())
            return m_default_value;

        // Return data at index
        return m_data[index];
    }

    // Fetches and removes one item from the front of the vector
    T_VALUE pop() {
        // Fetch first value
        T_VALUE value = m_data[0];

        // Shift forward existing items
        for (int i = 0; i < items() - 1; i++)
            m_data[i] = m_data[i + 1];

        // Decrement item count and return value
        m_items--;
        return value;
    }

    // Fetches and removes one item from the back of the vector
    T_VALUE popBack() {
        // Fetch and return last value
        return m_data[--m_items];
    }

    // Clears the entire content of the vector
    void clear() {
        for (int i = 0; i < size(); i++) {
            m_data[i]= m_default_value;
        }
    }

    // Retreives the number of elements currently holded by the vector
    int items() const {
        return m_items;
    }

    // Retreives the total number of elements the table can hold
    int size() const {
        return m_size;
    }

    // Indicates whether the vector is fully occupied
    bool isFull() const {
        return items() >= size();
    }

    // Indicates whether the vector is empty
    bool isEmpty() const {
        return items() == 0;
    }

    // Retreives the total storage size of the vector's content
    size_t storageSize() const {
        return sizeof(T_VALUE) * items();
    }

    // Checks if a specific value is set
    bool has(T_VALUE value) const {
        for (int i = 0; i < items(); i++)
            if (m_data[i] == value)
                return true;
        return false;
    }

    // Dumps the vector's contents to a stream object
    void dumps(Stream* const stream) {
        char line[80] = {0};
        for (int i = 0; i < size(); i++) {
            sprintf_P(line, PSTR("[%02d]  "), i);
            stream->print(line);
            stream->println(get(i));
        }

        sprintf_P(line, PSTR("Value/total size: %d/%dB, %d/%d items allocated at: %06p"),
            sizeof(T_VALUE),
            sizeof(*this),
            items(),
            size(),
            m_data);
        stream->println(line);
    }

    // Operator for getting an element via square brackets
    T_VALUE operator[](int index) const {
        return get(index);
    }

 private:
    // Private members
    const T_VALUE   m_default_value;
    T_VALUE         m_data[SIZE];
    const int       m_size;
    int             m_items;
};

#endif  // SRC_VECTOR_H_
