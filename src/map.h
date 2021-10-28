#ifndef _MAP_H_
#define _MAP_H_

template<class T_KEY, class T_VALUE>
class Map
{
public:
    struct key_value
    {
        T_KEY key;
        T_VALUE value;
    };

    Map():
        m_storage(0),
        m_items(0)
    {};

    bool add(T_KEY key, T_VALUE value)
    {
        int index = getIndex(key);
        if (index < 0)
        {
            size_t new_size = (m_items + 1) * sizeof(key_value);
            void* new_pointer = realloc(m_storage, new_size);
            if (!new_pointer)
                return false;
            m_storage = (key_value*)new_pointer;
            index = m_items++;
        }
        m_storage[index].key = key;
        m_storage[index].value = value;

        return true;
    };

    bool remove(T_KEY key)
    {
        int index = getIndex(key);
        if (index < 0)
            return false;

        int j = 0;
        for (int i = 0; i < size(); i++)
            if (i != index)
                m_storage[j++] = m_storage[i];

        size_t new_size = (m_items - 1) * sizeof(key_value);
        void* new_pointer = realloc(m_storage, new_size);
        if (!new_pointer)
            return false;
        m_storage = (key_value*)new_pointer;
        m_items--;

        return true;
    }

    bool getValue(T_KEY key, T_VALUE* target) const
    {
        int index = getIndex(key);
        if (index < 0)
            return false;

        *target = m_storage[index].value;
        return true;
    }

    bool getKey(int index, T_KEY* target) const
    {
        if (index < 0)
            return false;

        *target = m_storage[index].key;
        return true;
    }

    int getIndex(T_KEY key) const
    {
        for (int i = 0; i < size(); i++)
            if (m_storage[i].key == key)
                return i;
        return -1;
    }

    int size() const
    {
        return m_items;
    }

private:
    key_value* m_storage;
    int m_items;
};

#endif /* _MAP_H_ */