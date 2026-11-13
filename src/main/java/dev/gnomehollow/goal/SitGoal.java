package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import dev.gnomehollow.village.Claims;
import dev.gnomehollow.village.VillageInfo;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;

/** Even rustig zitten op een bankje of stoel in het dorp of in het eigen huis. */
public class SitGoal extends ActivityGoal {
	private BlockPos seat;

	public SitGoal(GnomeEntity gnome) {
		super(gnome, 500);
	}

	@Override
	protected boolean allowed() {
		return this.gnome.hasVillage() && this.gnome.canLeisure();
	}

	@Override
	protected boolean choose(ServerLevel level) {
		var rnd = this.gnome.getRandom();
		if (!this.gnome.busyLeisureChance() || (this.gnome.favorite() != 5 && rnd.nextInt(3) != 0)) return false;
		VillageInfo info = VillageInfo.get(level, this.gnome.villageCenter());
		List<BlockPos> free = new ArrayList<>();
		for (BlockPos s : info.seats) {
			if (this.gnome.distanceToSqr(s.getX() + 0.5, s.getY(), s.getZ() + 0.5) < 40.0 * 40.0 && Claims.isFree(level, s, this.gnome.getId())) free.add(s);
		}
		if (free.isEmpty()) return false;
		BlockPos pick = free.get(rnd.nextInt(free.size()));
		if (!Claims.claim(level, pick, this.gnome.getId())) return false;
		this.seat = pick;
		this.dest = pick;
		this.duration = 500 + rnd.nextInt(1100);
		return true;
	}

	@Override
	protected void onArrive(ServerLevel level) {
		GnomeUtil.sitAt(this.gnome, level, this.seat, this.gnome.villageCenter());
	}

	@Override
	protected void during(ServerLevel level) {
		if (this.gnome.tickCount % 40 == 0) GnomeUtil.sitAt(this.gnome, level, this.seat, this.gnome.villageCenter());
	}

	@Override
	protected void onEnd(ServerLevel level) {
		this.gnome.stopAnim();
		if (this.seat != null) Claims.release(level, this.seat, this.gnome.getId());
		this.seat = null;
	}
}
