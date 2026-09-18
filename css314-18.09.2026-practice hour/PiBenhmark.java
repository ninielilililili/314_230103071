
import java.util.Random;

public class PiBenchmark {

    static long totalHits = 0;

    static synchronized void incrementHits() {
        totalHits++;
    }

    public static void main(String[] args) throws InterruptedException {

        final long TOTAL_POINTS = 50_000_000;
        final int THREADS = 4;

        // -----------------------------
        // SINGLE-THREADED VERSION
        // -----------------------------

        totalHits = 0;

        long startSingle = System.nanoTime();

        Random random = new Random();

        for (long i = 0; i < TOTAL_POINTS; i++) {

            double x = random.nextDouble();
            double y = random.nextDouble();

            if (x * x + y * y <= 1.0) {
                totalHits++;
            }
        }

        long endSingle = System.nanoTime();

        double piSingle = 4.0 * totalHits / TOTAL_POINTS;

        double singleTime =
                (endSingle - startSingle) / 1_000_000.0;

        System.out.printf(
                "Single-threaded: pi = %.6f, time = %.2f ms%n",
                piSingle, singleTime
        );


        // -----------------------------
        // SYNCHRONIZED MULTI-THREADED
        // -----------------------------

        totalHits = 0;

        Thread[] threads = new Thread[THREADS];

        long pointsPerThread = TOTAL_POINTS / THREADS;

        long startMulti = System.nanoTime();

        for (int i = 0; i < THREADS; i++) {

            threads[i] = new Thread(() -> {

                Random threadRandom = new Random();

                for (long j = 0; j < pointsPerThread; j++) {

                    double x = threadRandom.nextDouble();
                    double y = threadRandom.nextDouble();

                    if (x * x + y * y <= 1.0) {
                        incrementHits();
                    }
                }
            });

            threads[i].start();
        }

        for (Thread thread : threads) {
            thread.join();
        }

        long endMulti = System.nanoTime();

        double piMulti = 4.0 * totalHits / TOTAL_POINTS;

        double multiTime =
                (endMulti - startMulti) / 1_000_000.0;

        System.out.printf(
                "Synchronized 4-thread: pi = %.6f, time = %.2f ms%n",
                piMulti, multiTime
        );
    }
}
