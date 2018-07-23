fn read<T: std::str::FromStr>() -> T {
    let mut s = String::new();
    std::io::stdin().read_line(&mut s).ok();
    s.trim().parse().ok().unwrap()
}

fn read_vec<T: std::str::FromStr>() -> Vec<T> {
    read::<String>().split_whitespace()
        .map(|e| e.parse().ok().unwrap()).collect()
}

struct UnionFindTree {
    n: usize,
    par: Vec<usize>,
    rank: Vec<usize>,
}

impl UnionFindTree {
    pub fn new(n: usize) -> UnionFindTree {
        let mut par: Vec<usize> = Vec::new();
        for i in 0..n {
            par.push(i);
        }
        let rank = vec![0; n];
        UnionFindTree{
            n: n,
            par: par,
            rank: rank,
        }
    }

    fn find(&self, x: usize) -> usize {
        let mut x = x;
        while self.par[x] != x {
            x = self.par[x];
        }
        x
    }

    fn same(&self, x: usize, y: usize) -> bool {
        self.find(x) == self.find(y)
    }

    fn unite(&mut self, x: usize, y: usize) {
        if self.same(x, y) {
            return;
        }
        let mut x = x;
        let mut y = y;
        if self.rank[y] > self.rank[x] {
            std::mem::swap(&mut x, &mut y);
        }
        self.par[x] = y;
        if self.rank[x] == self.rank[y] {
          self.rank[x] = self.rank[y] + 1;
      }
    }
}


fn main() {
    let nm: Vec<usize> = read_vec();
    let (n, m) = (nm[0], nm[1]);
    let mut p: Vec<usize> = read_vec();
    let mut uft = UnionFindTree::new(n+1);
    for _i in 0..m {
        let xy = read_vec::<usize>();
        let (x, y) = (xy[0] - 1, xy[1] - 1);
        uft.unite(x, y);
    }

    let mut ans:i32 = 0;
    for i in 0..p.len() {
        p[i] -= 0;
    }
    for i in 0..p.len() {
        if uft.same(p[i], i) {
            println!("{:?}", i);
            ans += 1;
        }
    }
    println!("{:?}", ans);
}
