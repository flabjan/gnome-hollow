package dev.gnomehollow.village;

import dev.gnomehollow.goal.Songs;
import java.util.HashMap;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;

/** Maximaal één muzieksessie tegelijk per dorp (zoals bij de Ribbits: één band, één liedje, één leider). */
public final class MusicSessions {
	public static final int PARTS = 4;

	public static final class Session {
		public final int song;
		public final long start;
		public final long end;
		public final BlockPos spot;
		public final boolean[] taken = new boolean[PARTS];
		public int leaderId;

		Session(int song, long start, long end, BlockPos spot, int leaderId) {
			this.song = song;
			this.start = start;
			this.end = end;
			this.spot = spot;
			this.leaderId = leaderId;
		}

		public int takenCount() {
			int n = 0;
			for (boolean b : this.taken) if (b) n++;
			return n;
		}

		/** Pakt het gewenste deel of anders het eerste vrije deel. Geeft -1 als alles bezet is. */
		public int takePart(int preferred) {
			if (preferred >= 0 && preferred < PARTS && !this.taken[preferred]) {
				this.taken[preferred] = true;
				return preferred;
			}
			for (int i = 0; i < PARTS; i++) {
				if (!this.taken[i]) {
					this.taken[i] = true;
					return i;
				}
			}
			return -1;
		}

		public void release(int part) {
			if (part >= 0 && part < PARTS) this.taken[part] = false;
		}
	}

	private static final Map<ServerLevel, Map<Long, Session>> SESSIONS = new WeakHashMap<>();

	private MusicSessions() {}

	public static Session get(ServerLevel level, long villageKey) {
		Map<Long, Session> m = SESSIONS.get(level);
		if (m == null) return null;
		Session s = m.get(villageKey);
		if (s != null && level.getGameTime() >= s.end) {
			m.remove(villageKey);
			return null;
		}
		return s;
	}

	/** Start een sessie als er nog geen is. De duur wordt afgerond op hele keren het liedje. */
	public static Session create(ServerLevel level, long villageKey, BlockPos spot, int leaderId, int minTicks, int maxTicks, int song) {
		Session existing = get(level, villageKey);
		if (existing != null) return existing;
		Songs.Song s = Songs.ALL[song % Songs.ALL.length];
		long loop = (long) s.stepTicks() * s.length();
		int span = Math.max(1, maxTicks - minTicks);
		long want = minTicks + level.getRandom().nextInt(span);
		long loops = Math.max(2L, (want + loop - 1) / loop);
		long start = level.getGameTime() + 60;
		Session created = new Session(song % Songs.ALL.length, start, start + loops * loop, spot, leaderId);
		SESSIONS.computeIfAbsent(level, l -> new HashMap<>()).put(villageKey, created);
		return created;
	}
}
