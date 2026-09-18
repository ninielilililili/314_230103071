import java.util.Random;

public class PiBenchmark {

    static long totalHits = 0;

    public static void main(String[] args) throws InterruptedException {

        final long TOTAL_POINTS = 50_000_000;
        final int THREADS = 4;

        for (int run = 1; run <= 5; run++) {

            totalHits = 0;

            Thread[] threads = new Thread[THREADS];

            long pointsPerThread = TOTAL_POINTS / THREADS;

            long startTime = System.nanoTime();

            for (int i = 0; i < THREADS; i++) {

                threads[i] = new Thread(() -> {

                    Random random = new Random();

                    for (long j = 0; j < pointsPerThread; j++) {

                        double x = random.nextDouble();
                        double y = random.nextDouble();

                        if (x * x + y * y <= 1.0) {
                            totalHits++;
                        }
                    }
                });

                threads[i].start();
            }

            for (Thread thread : threads) {
                thread.join();
            }

            long endTime = System.nanoTime();

            double pi = 4.0 * totalHits / TOTAL_POINTS;

            double runtimeMs = (endTime - startTime) / 1_000_000.0;

            System.out.printf(
                    "Run %d: pi = %.6f, hits = %d, time = %.2f ms%n",
                    run, pi, totalHits, runtimeMs
            );
        }
    }
}