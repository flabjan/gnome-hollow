package dev.gnomehollow.village;

import java.util.HashMap;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.Entity;

/** Wie zit/slaapt waar. Een claim vervalt als de gnome niet meer bestaat of na afloop van de geldigheidsduur. */
public final class Claims {
	private record Claim(int entityId, long expires) {}

	private static final Map<ServerLevel, Map<Long, Claim>> CLAIMS = new WeakHashMap<>();
	private static final long TTL = 6000L;

	private Claims() {}

	private static Map<Long, Claim> map(ServerLevel level) {
		return CLAIMS.computeIfAbsent(level, l -> new HashMap<>());
	}

	public static boolean isFree(ServerLevel level, BlockPos pos, int byEntity) {
		Claim c = map(level).get(pos.asLong());
		if (c == null || c.entityId() == byEntity || level.getGameTime() > c.expires()) return true;
		Entity e = level.getEntity(c.entityId());
		return e == null || !e.isAlive();
	}

	public static boolean claim(ServerLevel level, BlockPos pos, int byEntity) {
		if (!isFree(level, pos, byEntity)) return false;
		map(level).put(pos.asLong(), new Claim(byEntity, level.getGameTime() + TTL));
		return true;
	}

	public static void release(ServerLevel level, BlockPos pos, int byEntity) {
		Map<Long, Claim> m = map(level);
		Claim c = m.get(pos.asLong());
		if (c != null && c.entityId() == byEntity) m.remove(pos.asLong());
	}
}
