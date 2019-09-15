#pragma once
#include <valarray>
#include <string>
#include <sstream>

template<typename T>
class Matrix
{
public:
	std::valarray<T> data;
	size_t columns = 0;
	size_t rows = 0;

	Matrix() = default;

	Matrix(std::valarray<T> data, const size_t columns)
		: data(std::move(data)),
		  columns(columns)
	{
		rows = this->data.size() / columns;
	}

	Matrix(const size_t rows, const size_t columns)
		: data(static_cast<T>(0), rows* columns),
		  columns(columns),
		  rows(rows)
	{}

	std::string to_json() const
	{
		std::stringstream os;

		os << "[";
		for (size_t row = 0; row < rows; ++row)
		{
			os << "[";
			for (size_t col = 0; col < columns; ++col)
			{
				os << (*this)(row, col);
				if (col < columns - 1)
				{
					os << ",";
				}
			}
			os << "]";

			if (row < rows - 1)
			{
				os << ",";
			}
		}
		os << "]";

		return os.str();
	}
	
	std::slice_array<T> row(const size_t row)
	{
		return data[std::slice(row * columns, columns, 1)];
	}

	std::slice_array<T> column(const size_t column)
	{
		return data[std::slice(column, rows, columns)];
	}

	T& operator()(const size_t row, const size_t column)
	{
		return data[row * columns + column];
	}
	
	const T& operator()(const size_t row, const size_t column) const
	{
		return data[row * columns + column];
	}
};

template<typename T>
std::ostream& operator<<(std::ostream& os, const Matrix<T>& mat)
{
	for (size_t row = 0; row < mat.rows; ++row)
	{
		for (size_t col = 0; col < mat.columns; ++col)
		{
			os << mat(row, col);
			if (col < mat.columns - 1)
			{
				os << ", ";
			}
		}
		os << std::endl;
	}
	
	return os;
}
