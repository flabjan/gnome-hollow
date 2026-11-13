package dev.gnomehollow.village;

import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.server.level.ServerLevel;

/**
 * Dagritme voor alle gnomes in een wereld. We gebruiken alleen isBrightOutside() en meten hoe lang het al licht
 * of donker is, zodat tijd overslaan (slapen, /time) het ritme niet verstoort.
 */
public final class DayTracker {
	public enum Phase { MORNING, WORK, LEISURE, EVENING, NIGHT }

	private static final class State {
		boolean bright = true;
		long since;
		long updated = -1;
	}

	private static final Map<ServerLevel, State> STATES = new WeakHashMap<>();

	private DayTracker() {}

	private static State state(ServerLevel level) {
		State s = STATES.get(level);
		if (s == null) {
			s = new State();
			s.bright = level.isBrightOutside();
			s.since = level.getGameTime() - 6000;
			STATES.put(level, s);
		}
		long t = level.getGameTime();
		if (s.updated != t) {
			s.updated = t;
			boolean b = level.isBrightOutside();
			if (b != s.bright) {
				s.bright = b;
				s.since = t;
			}
		}
		return s;
	}

	public static Phase phase(ServerLevel level) {
		State s = state(level);
		long elapsed = level.getGameTime() - s.since;
		if (!s.bright) return elapsed < 3000 ? Phase.EVENING : Phase.NIGHT;
		if (elapsed < 800) return Phase.MORNING;
		return elapsed < 9500 ? Phase.WORK : Phase.LEISURE;
	}

	/** Ticks sinds het laatst licht/donker werd. */
	public static long sinceChange(ServerLevel level) {
		return level.getGameTime() - state(level).since;
	}

	public static long dayIndex(ServerLevel level) {
		return level.getGameTime() / 24000L;
	}

	/** Gebeurtenis van vanavond voor een dorp: 0 = niets, 1 = samenkomst, 2 = muziekavond, 3 = feest. Iedereen komt op hetzelfde uit. */
	public static int eventOfTonight(ServerLevel level, long villageKey) {
		long h = (dayIndex(level) * 0x9E3779B97F4A7C15L) ^ (villageKey * 0xC2B2AE3D27D4EB4FL);
		h ^= (h >>> 29);
		int r = (int) Math.floorMod(h, 10L);
		if (r < 3) return 0;
		if (r < 5) return 1;
		if (r < 9) return 2;
		return 3;
	}
}
