package dev.gnomehollow.village;

import java.util.ArrayList;
import java.util.List;
import java.util.Map;
import java.util.WeakHashMap;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.StairBlock;
import net.minecraft.world.level.block.state.BlockState;

/** Gecachete plekken in een dorp (bel, markt, bibliotheek, tuinen, zitplekken, lantaarnpalen). Alleen geladen chunks worden gelezen. */
public final class VillageInfo {
	private static final Map<ServerLevel, Map<Long, VillageInfo>> CACHE = new WeakHashMap<>();

	public final BlockPos center;
	public BlockPos bell;
	public BlockPos market;
	public BlockPos library;
	public final List<BlockPos> gardens = new ArrayList<>();
	public final List<BlockPos> seats = new ArrayList<>();
	public final List<BlockPos> lampSockets = new ArrayList<>();
	private long scanned = -1_000_000L;

	private VillageInfo(BlockPos center) {
		this.center = center;
	}

	public static long key(BlockPos center) {
		return center.asLong();
	}

	public static VillageInfo get(ServerLevel level, BlockPos center) {
		Map<Long, VillageInfo> map = CACHE.computeIfAbsent(level, l -> new java.util.HashMap<>());
		VillageInfo info = map.computeIfAbsent(key(center), k -> new VillageInfo(center));
		if (level.getGameTime() - info.scanned > 6000L) {
			info.scanned = level.getGameTime();
			info.scan(level);
		}
		return info;
	}

	public BlockPos meetingSpot() {
		return this.bell != null ? this.bell : this.center;
	}

	private static boolean groundish(BlockState s) {
		return s.is(Blocks.SPRUCE_PLANKS) || s.is(Blocks.DIRT_PATH) || s.is(Blocks.GRASS_BLOCK) || s.is(Blocks.PODZOL)
				|| s.is(Blocks.DIRT) || s.is(Blocks.COARSE_DIRT) || s.is(Blocks.MOSS_BLOCK);
	}

	private void scan(ServerLevel level) {
		this.bell = null;
		this.market = null;
		this.library = null;
		this.gardens.clear();
		this.seats.clear();
		this.lampSockets.clear();
		int r = 36;
		double bestBell = Double.MAX_VALUE, bestMarket = Double.MAX_VALUE, bestLib = Double.MAX_VALUE;
		BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
		for (int dx = -r; dx <= r; dx++) {
			for (int dz = -r; dz <= r; dz++) {
				m.set(this.center.getX() + dx, this.center.getY(), this.center.getZ() + dz);
				if (!level.hasChunkAt(m)) continue;
				for (int dy = -8; dy <= 10; dy++) {
					m.set(this.center.getX() + dx, this.center.getY() + dy, this.center.getZ() + dz);
					BlockState s = level.getBlockState(m);
					if (s.isAir()) continue;
					double d = this.center.distSqr(m);
					if (s.is(Blocks.BELL)) {
						if (d < bestBell) { bestBell = d; this.bell = m.immutable(); }
					} else if (s.is(Blocks.LOOM)) {
						if (d < bestMarket) { bestMarket = d; this.market = m.immutable(); }
					} else if (s.is(Blocks.LECTERN)) {
						if (d < bestLib) { bestLib = d; this.library = m.immutable(); }
					} else if (s.is(Blocks.COMPOSTER)) {
						if (this.gardens.size() < 8) this.gardens.add(m.immutable());
					} else if (s.getBlock() instanceof StairBlock) {
						BlockPos p = m.immutable();
						if (groundish(level.getBlockState(p.below())) && level.getBlockState(p.above()).isAir()
								&& level.getBlockState(p.above(2)).isAir() && this.seats.size() < 80) {
							this.seats.add(p);
						}
					} else if (s.is(Blocks.DARK_OAK_FENCE)) {
						BlockPos p = m.immutable();
						if (level.getBlockState(p.below()).is(Blocks.DARK_OAK_FENCE) && level.getBlockState(p.above()).isAir()
								&& this.lampSockets.size() < 24) {
							this.lampSockets.add(p.above());
						}
					}
				}
			}
		}
	}
}
