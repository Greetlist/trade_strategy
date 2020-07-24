#ifndef __CSV_READER_H
#define __CSV_READER_H

#include <iostream>
#include <string>
#include <vector>
#include <map>

class CsvReader {
public:
    CsvReader(std::string _file_path) : file_path(_file_path) {init_csv_data();}
    ~CsvReader() {}
    template <typename T>
    std::vector<T> getColumnValues(std::string col);
private:
    std::string file_path;
    void init_csv_data();
    std::vector<std::vector<std::string>> row_datas;
    std::map<std::string, int> columns;
    std::vector<std::string> getAllColumnName();
};
#endif
