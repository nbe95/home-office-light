#ifndef SRC_MAP_H_
#define SRC_MAP_H_

// Static Map helper class
// To prevent heap fragmentation, a StaticMap acts as a fixed size container.
// Unlike a real Map, data is not dynamically allocated.
template<class T_KEY, class T_VALUE, int SIZE>
class StaticMap {
 public:
    // Constructor with default/fallback values
    explicit StaticMap(T_KEY default_key = T_KEY(), T_VALUE default_value = T_VALUE()) :
    m_items(0),
    m_size(SIZE),
    m_default_key(default_key),
    m_default_value(default_value) {
        for (int i = 0; i < m_size; i++) {
            m_data[i].key = default_key;
            m_data[i].value = default_value;
        }
    }

    // Destructor for storage cleanup
    ~StaticMap() {
        clear();
    }

    // Adds a key-value pair to the table or updates an existing one,
    // returns the corresponding/new index
    int set(const T_KEY key, const T_VALUE value) {
        // Check if specified key already exists
        int index = getIndex(key);
        if (index < 0) {
            // Don't do anything if table is already full
            if (items() >= size())
                return -1;

            // Use first empty item
            index = m_items++;
        }
        m_data[index].key = key;
        m_data[index].value = value;
        return index;
    }

    // Fetches the numerical index (=array position) of an element identified by its key
    int getIndex(T_KEY key) const {
        for (int i = 0; i < items(); i++)
            if (m_data[i].key == key)
                return i;
        return -1;
    }

    // Fetches the value of an element identified by its key
    T_VALUE getValue(T_KEY key) const {
        return getValueByIndex(getIndex(key));
    }

    // Fetches the value of an element identified by its index
    T_VALUE getValueByIndex(int index) const {
        if (index < 0 || index >= items())
            return m_default_value;

        return m_data[index].value;
    }

    // Fetches the key of an element identified by its index
    T_KEY getKeyByIndex(int index) const {
        if (index < 0 || index >= items())
            return m_default_key;

        return m_data[index].key;
    }

    // Clears the entire content of the map
    void clear() {
        for (int i = 0; i < size(); i++) {
            m_data[i].key = m_default_key;
            m_data[i].value = m_default_value;
        }
    }

    // Retreives the number of elements currently holded by the table
    int items() const {
        return m_items;
    }

    // Retreives the total number of elements the table can hold
    int size() const {
        return m_size;
    }

    // Indicates whether the map is fully occupied
    bool isFull() const {
        return items() >= size();
    }

    // Indicates whether the map is empty
    bool isEmpty() const {
        return items() == 0;
    }

    // Retreives the total storage size of the map's content
    size_t storageSize() const {
        return sizeof(data) * items();
    }

    // Checks if a specific key is set
    bool hasKey(T_KEY key) const {
        for (int i = 0; i < items(); i++)
            if (m_data[i].key == key)
                return true;
        return false;
    }

    // Checks if a specific value is set
    bool hasValue(T_VALUE value) const {
        for (int i = 0; i < items(); i++)
            if (m_data[i].value == value)
                return true;
        return false;
    }

    // Dumps the map's contents to a stream object
    void dumps(Stream* const stream) {
        char line[80] = {0};
        for (int i = 0; i < size(); i++) {
            sprintf_P(line, PSTR("[%02d]  "), i);
            stream->print(line);
            stream->print(getKeyByIndex(i));
            stream->print(F(" -> "));
            stream->println(getValueByIndex(i));
        }

        sprintf_P(line, PSTR("Key/value/total size: %d/%d/%dB, %d/%d items allocated at: %06p"),
            sizeof(T_KEY),
            sizeof(T_VALUE),
            sizeof(*this),
            items(),
            size(),
            m_data);
        stream->println(line);
    }

    // Operator for getting an element via square brackets
    T_VALUE operator[](T_KEY key) const {
        return getValue(key);
    }

 private:
    // Definition of template data structure
    struct data {
        T_KEY key;
        T_VALUE value;
    };

    // Private members
    const T_KEY     m_default_key;
    const T_VALUE   m_default_value;
    data            m_data[SIZE];
    const int       m_size;
    int             m_items;
};

#endif  // SRC_MAP_H_
