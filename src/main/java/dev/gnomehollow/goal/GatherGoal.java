package dev.gnomehollow.goal;

import dev.gnomehollow.GnomeConfig;
import dev.gnomehollow.entity.GnomeEntity;
import dev.gnomehollow.village.Claims;
import dev.gnomehollow.village.DayTracker;
import dev.gnomehollow.village.MusicSessions;
import dev.gnomehollow.village.VillageInfo;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;

/**
 * Gemeenschappelijke avond bij het meeting place (op vaste momenten): na zonsondergang komt het dorp samen om te zitten,
 * te kletsen en naar muziek te luisteren. Bij een muziekavond of feest spelen de muzikanten één liedje samen.
 */
public class GatherGoal extends ActivityGoal {
	private final Performer performer = new Performer();
	private BlockPos seat;

	public GatherGoal(GnomeEntity gnome) {
		super(gnome, 20);
	}

	@Override
	protected boolean allowed() {
		return this.gnome.attendsEvent() && !this.gnome.inDanger() && this.gnome.getTarget() == null && !this.gnome.isTrading();
	}

	@Override
	protected int nextCooldown() {
		return 200;
	}

	@Override
	protected boolean choose(ServerLevel level) {
		VillageInfo info = VillageInfo.get(level, this.gnome.villageCenter());
		BlockPos spot = info.meetingSpot();
		double lim = GnomeConfig.get().villageRadius + 10.0;
		if (this.gnome.distanceToSqr(spot.getX() + 0.5, spot.getY(), spot.getZ() + 0.5) > lim * lim) return false;
		this.seat = null;
		List<BlockPos> free = new ArrayList<>();
		for (BlockPos s : info.seats) {
			if (s.distSqr(spot) < 100 && Claims.isFree(level, s, this.gnome.getId())) free.add(s);
		}
		if (!free.isEmpty()) {
			BlockPos pick = free.get(this.gnome.getRandom().nextInt(free.size()));
			if (Claims.claim(level, pick, this.gnome.getId())) this.seat = pick;
		}
		this.dest = this.seat != null ? this.seat : GnomeUtil.ring(level, spot, this.gnome.getId(), 3.5 + this.gnome.getId() % 3);
		this.duration = 3200;
		return true;
	}

	@Override
	protected void onArrive(ServerLevel level) {
		BlockPos spot = VillageInfo.get(level, this.gnome.villageCenter()).meetingSpot();
		if (this.seat != null) GnomeUtil.sitAt(this.gnome, level, this.seat, spot);
		else this.gnome.getLookControl().setLookAt(spot.getX() + 0.5, spot.getY() + 1.0, spot.getZ() + 0.5);
	}

	private void maybeStartMusic(ServerLevel level) {
		int event = this.gnome.tonightsEvent();
		if (event < 2 || !this.gnome.playsMusic() || this.performer.active()) return;
		long key = this.gnome.villageCenter().asLong();
		MusicSessions.Session s = MusicSessions.get(level, key);
		if (s == null) {
			BlockPos spot = VillageInfo.get(level, this.gnome.villageCenter()).meetingSpot();
			List<GnomeEntity> near = level.getEntitiesOfClass(GnomeEntity.class, this.gnome.getBoundingBox().inflate(9.0, 4.0, 9.0), g -> g.attendsEvent());
			boolean leader = near.size() >= 2;
			for (GnomeEntity g : near) if (g.getId() < this.gnome.getId() && g.playsMusic()) leader = false;
			if (!leader || DayTracker.sinceChange(level) > 2200) return;
			int lo = (event == 3 ? 150 : 100) * 20;
			int hi = (event == 3 ? 220 : 150) * 20;
			s = MusicSessions.create(level, key, spot, this.gnome.getId(), lo, hi, this.gnome.getRandom().nextInt(Songs.ALL.length));
		}
		this.performer.tryJoin(this.gnome, s);
	}

	@Override
	protected void during(ServerLevel level) {
		if (this.gnome.tickCount % 40 == 0) {
			this.maybeStartMusic(level);
			if (this.seat != null && !this.performer.active()) GnomeUtil.sitAt(this.gnome, level, this.seat, null);
		}
		if (this.performer.active()) {
			if (!this.performer.play(level, this.gnome)) {
				this.performer.leave(this.gnome);
				if (this.seat != null) GnomeUtil.sitAt(this.gnome, level, this.seat, null);
			}
		} else if (this.seat == null && this.gnome.getRandom().nextInt(300) == 0) {
			this.gnome.oneShot("talk");
		}
	}

	@Override
	protected void onEnd(ServerLevel level) {
		this.performer.leave(this.gnome);
		this.gnome.stopAnim();
		if (this.seat != null) Claims.release(level, this.seat, this.gnome.getId());
		this.seat = null;
	}
}
