import java.util.Random;

public class PiBenchmark {

    static class Worker implements Runnable {

        private final long iterations;
        private long localHits;

        public Worker(long iterations) {
            this.iterations = iterations;
            this.localHits = 0;
        }

        @Override
        public void run() {

            Random random = new Random();

            for (long i = 0; i < iterations; i++) {

                double x = random.nextDouble();
                double y = random.nextDouble();

                if (x * x + y * y <= 1.0) {
                    localHits++;
                }
            }
        }

        public long getLocalHits() {
            return localHits;
        }
    }


    public static void main(String[] args) throws InterruptedException {

        final long TOTAL_POINTS = 100_000_000;

        int[] threadCounts = {1, 2, 4, 8, 16, 32};

        double baselineTime = 0;

        System.out.println("Part 3: Reduction Benchmark");
        System.out.println("---------------------------------------------");

        for (int threadCount : threadCounts) {

            Worker[] workers = new Worker[threadCount];
            Thread[] threads = new Thread[threadCount];

            long pointsPerThread = TOTAL_POINTS / threadCount;

            long startTime = System.nanoTime();

            // Create and start threads
            for (int i = 0; i < threadCount; i++) {

                workers[i] = new Worker(pointsPerThread);

                threads[i] = new Thread(workers[i]);

                threads[i].start();
            }

            // Wait for all threads
            for (Thread thread : threads) {
                thread.join();
            }

            // Reduction: combine local counters
            long totalHits = 0;

            for (Worker worker : workers) {
                totalHits += worker.getLocalHits();
            }

            long endTime = System.nanoTime();

            double runtimeMs =
                    (endTime - startTime) / 1_000_000.0;

            double pi =
                    4.0 * totalHits / TOTAL_POINTS;

            // First row becomes our baseline
            if (threadCount == 1) {
                baselineTime = runtimeMs;
            }

            double speedup =
                    baselineTime / runtimeMs;

            double efficiency =
                    speedup / threadCount * 100.0;

            System.out.printf(
                    "%2d threads | pi = %.6f | Runtime = %8.2f ms | Speedup = %.2fx | Efficiency = %.2f%%%n",
                    threadCount,
                    pi,
                    runtimeMs,
                    speedup,
                    efficiency
            );
        }
    }
}
