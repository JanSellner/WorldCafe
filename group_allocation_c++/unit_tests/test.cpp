#include "pch.h"
#include <algorithm>
#define PRINT_NO_PROGRESS
#include "../GroupSearch.h"

int n_unique_values(std::valarray<int> data)
{
	std::sort(std::begin(data), std::end(data));
	const auto iterator = std::unique(std::begin(data), std::end(data));
	return static_cast<int>(std::distance(std::begin(data), iterator));
}

TEST(TestGroupAllocation, TestGroupSearch) {
	const int n_groups = 3;
	const int n_users = 4;

	const std::vector<int> foreigners = { 0, 0, 1, 1};
	EXPECT_EQ(n_users, foreigners.size());
	
	GroupSearch group_search(n_groups, n_users, foreigners);
	const Matrix<int> alloc = group_search.find_best_allocation();
	
	const Matrix<int> alloc_true(std::valarray<int>({
		0, 1, 1, 0,
		1, 2, 0, 2,
		2, 0, 2, 1
	}), n_users);

	EXPECT_EQ(alloc.rows, alloc_true.rows);
	EXPECT_EQ(alloc.columns, alloc_true.columns);
	EXPECT_EQ(n_unique_values(alloc.data), n_groups);
	EXPECT_EQ(n_unique_values(alloc_true.data), n_groups);
	
	for (size_t i = 0; i < alloc.data.size(); ++i)
	{
		EXPECT_EQ(alloc.data[i], alloc_true.data[i]);
	}
}

TEST(TestGroupAllocation, TestGroupEvaluation) {
	const int n_users = 10;
	const Matrix<int> alloc_start(std::valarray<int>({
		1, 2, 4, 2, 3, 0, 3, 0, 3, 4,
		4, 0, 0, 3, 2, 4, 2, 4, 1, 1,
		0, 4, 3, 1, 0, 2, 0, 2, 0, 2,
		3, 3, 2, 0, 1, 1, 1, 3, 4, 3,
		2, 1, 1, 4, 4, 3, 4, 1, 2, 0
	}), n_users);

	const int n_groups = n_unique_values(alloc_start.data);
	const std::vector<int> foreigners = { 0, 0, 1, 1, 0, 1, 1, 1, 0, 1 };
	EXPECT_EQ(n_users, foreigners.size());

	GroupEvaluation gval(n_groups, n_users, foreigners);
	EXPECT_DOUBLE_EQ(gval.error_group_sizes(alloc_start), 0.9);
	EXPECT_DOUBLE_EQ(gval.error_meetings(alloc_start), 0.5429272594305719);
	EXPECT_DOUBLE_EQ(gval.error_foreigners(alloc_start), 1.0645929264282177);
	EXPECT_DOUBLE_EQ(gval.error_total(alloc_start), 0.8358400619529298);
}
