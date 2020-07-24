#include "csv_reader.h"
#include <fstream>
#include <sstream>

void CsvReader::init_csv_data() {
    std::fstream fs(this->file_path);
    std::string line;
    int rowNumber = 0;
    while (std::getline(fs, line)) {
        std::string cell;
        std::stringstream ss(line);
        if (rowNumber++ == 0) {
            int index = 0;
            while (getline(ss, cell, ',')) {
                cell = cell == "" ? "index" : cell;
                columns[cell] = index++;
            }
        } else {
            std::vector<std::string> row_data;
            while (getline(ss, cell, ',')) {
                row_data.push_back(cell);
            }
            this->row_datas.push_back(row_data);
        }
    }
}

std::vector<std::string> CsvReader::getAllColumnName() {
    std::map<std::string, int>::iterator end = this->columns.end();
    std::vector<std::string> res;
    for (std::map<std::string, int>::iterator it = this->columns.begin(); it != end; it++) {
        res.push_back((*it).first);
    }
    return res;
}

template <>
std::vector<std::string> CsvReader::getColumnValues<std::string>(std::string col) {
    std::vector<std::string> res;
    std::map<std::string, int>::iterator it = this->columns.find(col);
    if (it == this->columns.end()) {
        return res;
    }
    int col_index = (*it).second;
    int row_number = this->row_datas.size();
    for (int i = 0; i < row_number; ++i) {
        res.push_back(this->row_datas[i][col_index]);
    }
    return res;
}

template <>
std::vector<double> CsvReader::getColumnValues<double>(std::string col) {
    std::vector<double> res;
    std::map<std::string, int>::iterator it = this->columns.find(col);
    if (it == this->columns.end()) {
        return res;
    }
    int col_index = (*it).second;
    int row_number = this->row_datas.size();
    for (int i = 0; i < row_number; ++i) {
        res.push_back(std::stod(this->row_datas[i][col_index]));
    }
    return res;
}
