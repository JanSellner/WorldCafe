#pragma once
#include <valarray>

template<typename T>
class Matrix
{
public:
	std::valarray<T> data;
	size_t columns;
	size_t rows;

	Matrix(std::valarray<T> data, const size_t columns)
		: data(std::move(data)),
		columns(columns)
	{
		rows = this->data.size() / columns;
	}

	Matrix(size_t rows, size_t columns)
		: data(static_cast<T>(0), rows* columns),
		columns(columns),
		rows(rows)
	{}

	std::slice_array<T> row(const size_t row)
	{
		return data[std::slice(row * columns, columns, 1)];
	}

	T& operator()(size_t row, size_t column)
	{
		return data[row * columns + column];
	}
};
