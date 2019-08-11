#include <algorithm>
#include <iostream>
#include <set>
#include <stdio.h>
#include <vector>

int main() {
  int n;
  int m;
  std::cin >> n >> m;
  std::vector<std::pair<int, int>> works;
  for (int i = 0; i < n; i++) {
    int a;
    int b;
    std::cin >> a >> b;
    works.push_back(std::make_pair(b, a));
  }
  std::sort(works.begin(), works.end());
  std::reverse(works.begin(), works.end());
  std::set<int> undecided;
  for (int i = 1; i < m + 1; i++) {
    undecided.insert(i);
  }
  int ans = 0;
  for (int i = 0; i < n; i++) {
    int a = works[i].second;
    int b = works[i].first;
    auto result = undecided.lower_bound(a);
    // std::cerr << *result << std::endl;
    if (result == undecided.end()) {
      continue;
    }
    ans += b;
    undecided.erase(result);
  }
  std::cout << ans << std::endl;
}
