#include <iostream>
#include <vector>
#include <algorithm>
#include <queue>
#include <map>
#include <set>

// solution for https://atcoder.jp/contests/abc134/tasks/abc134_e

using namespace std;
typedef long long ll;
typedef vector<ll> vl;

int main() {
    ll n; cin >> n;
    vl a;
    for(ll i = 0; i < n; i++) {
        ll num; 
        std::cin >> num;
        a.push_back(num);
    }
    std::multiset<ll> s;
    for(ll i = 0; i < n; i++) {
        if (s.empty() || s.upper_bound(-a[i]) == s.end()) {
            ;
        } else {
            // std::cerr << "remo" << *s.upper_bound(-a[i]) << std::endl;
            s.erase(s.upper_bound(-a[i]));
        }
        s.insert(-a[i]);
    }
    cout << s.size() << endl;
}

