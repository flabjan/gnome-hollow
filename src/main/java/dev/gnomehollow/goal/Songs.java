package dev.gnomehollow.goal;

/**
 * Vier korte volksliedjes. Waarden zijn halve tonen (0 = C); R = rust.
 * Stemmen: 0 = fluit (melodie), 1 = luit (akkoorden), 2 = bas, 3 = ritme (D = trom, t = tik).
 * Fluit en luit hebben als basistoon C4, de bas C2.
 */
public final class Songs {
	public static final int R = 99;

	public record Song(int stepTicks, int[] melody, int[] harmony, int[] bass, String rhythm) {
		public int length() {
			return this.melody.length;
		}
	}

	public static final Song[] ALL = {
		// Heuvelwals (driekwartsmaat)
		new Song(5,
				new int[] {4,R,R, 7,R,R, 9,R,7, 4,R,R, 2,R,4, 0,R,R, 2,R,4, 0,R,R},
				new int[] {-12,R,-5, -5,R,-1, -3,R,0, -12,R,-5, -7,R,-3, -12,R,-8, -7,R,-3, -12,R,-5},
				new int[] {0,R,R, 7,R,R, 9,R,R, 0,R,R, 5,R,R, 0,R,R, 5,R,R, 0,R,R},
				"D.tD.tD.tD.tD.tD.tD.tD.t"),
		// Boswandeling
		new Song(4,
				new int[] {0,R,2,R, 4,R,7,R, 9,R,7,R, 4,2,0,R},
				new int[] {-12,R,-5,R, -8,R,-5,R, -3,R,0,R, -5,-8,-12,R},
				new int[] {0,R,R,R, 4,R,R,R, 9,R,R,R, 7,R,R,R},
				"D.t.D.t.D.t.D.tt"),
		// Paddenstoelpolka
		new Song(3,
				new int[] {7,9,12,9, 7,R,4,R, 7,9,12,9, 7,4,2,R},
				new int[] {-5,R,-1,R, -12,R,-8,R, -5,R,-1,R, -12,R,-5,R},
				new int[] {7,R,R,R, 0,R,R,R, 7,R,R,R, 0,R,R,R},
				"DtDtDtDtDtDtDtDD"),
		// Maanlicht (traag)
		new Song(5,
				new int[] {9,R,R,7, 4,R,R,R, 2,R,4,R, 0,R,R,R},
				new int[] {-3,R,R,R, -8,R,R,R, -10,R,-5,R, -12,R,-8,R},
				new int[] {9,R,R,R, 4,R,R,R, 2,R,R,R, 0,R,R,R},
				"D.......t......."),
	};

	private Songs() {}
}
