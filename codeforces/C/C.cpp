#include <cstdio>
#include <cmath>

struct object {
  int cat;
  int val;
};

struct acum {
  long long k;
  long long xy;
};

int main() {
  int N, K;
  scanf("%d %d", &N, &K);

  acum* info = new acum[K];
  object* objects = new object[N];

  for (int i = 0; i < K; ++i) {
    info[i].k = 0;
    info[i].xy = 0;
  }

  for (int i = 0; i < N; ++i) {
    scanf("%d", &(objects + i)->cat);
    objects[i].cat -= 1;
  }
  for (int i = 0; i < N; ++i) {
    scanf("%d", &(objects + i)->val);
  }

  // find mean
  long long sy = 0;
  for (int i = 0; i < N; ++i) {
    sy += objects[i].val;
  }
  long double ymean = ((long double) sy) / N;

  long double ystd = 0;
  for (int i = 0; i < N; ++i) {
    long long t = (N * objects[i].val - sy);
    ystd +=  t * t;
  }
  ystd = std::sqrt(((long double) ystd) / N) / N;

  for (int i = 0; i < N; ++i) {
    int cat = objects[i].cat;
    info[cat].k += 1;
    info[cat].xy += objects[i].val;
  }
  
  long double result = 0;
  for (int i = 0; i < K; ++i) {
    long long k = info[i].k;
    long double xy = info[i].xy;
    long double xstd = std::sqrt((k * (N - k))) / N;
    long double res = (xy - k * ymean) / N / xstd / ystd;
    result += k * res / N; 
  }

  printf("%.17Lg\n", result);

  return 0;
}
