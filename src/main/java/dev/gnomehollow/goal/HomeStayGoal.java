package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import dev.gnomehollow.village.Claims;
import java.util.ArrayList;
import java.util.List;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.level.block.Blocks;
import net.minecraft.world.level.block.StairBlock;

/** 's Nachts naar huis en slapen (in een bed als er een is), en bij onweer binnen schuilen (zitten of staan). */
public class HomeStayGoal extends ActivityGoal {
	private BlockPos bed;
	private BlockPos stand;
	private BlockPos seat;
	private boolean sleeping;

	public HomeStayGoal(GnomeEntity gnome) {
		super(gnome, 20);
	}

	@Override
	protected boolean allowed() {
		if (this.gnome.inDanger() || this.gnome.getTarget() != null || this.gnome.isTrading() || !this.gnome.hasHome()) return false;
		boolean night = this.gnome.isNight() && !this.gnome.profession().isGuard();
		return night || (this.gnome.shouldShelter() && !this.gnome.attendsEvent());
	}

	@Override
	protected int nextCooldown() {
		return 40;
	}

	@Override
	protected double speed() {
		return 0.75;
	}

	@Override
	protected boolean choose(ServerLevel level) {
		BlockPos home = this.gnome.home();
		this.bed = null;
		this.seat = null;
		this.sleeping = false;
		if (this.gnome.isNight()) {
			this.bed = GnomeUtil.findFreeBed(level, this.gnome);
			if (this.bed != null) {
				this.sleeping = true;
				this.stand = GnomeUtil.findStandNear(level, this.bed).orElse(home);
				this.dest = this.stand;
			}
		}
		if (!this.sleeping) {
			List<BlockPos> seats = new ArrayList<>();
			BlockPos.MutableBlockPos m = new BlockPos.MutableBlockPos();
			for (int dx = -5; dx <= 5; dx++) {
				for (int dz = -5; dz <= 5; dz++) {
					for (int dy = -1; dy <= 3; dy++) {
						m.set(home.getX() + dx, home.getY() + dy, home.getZ() + dz);
						if (level.hasChunkAt(m) && level.getBlockState(m).getBlock() instanceof StairBlock
								&& level.getBlockState(m.below()).is(Blocks.SPRUCE_PLANKS) && Claims.isFree(level, m, this.gnome.getId())) seats.add(m.immutable());
					}
				}
			}
			if (!seats.isEmpty()) {
				BlockPos pick = seats.get(this.gnome.getRandom().nextInt(seats.size()));
				if (Claims.claim(level, pick, this.gnome.getId())) this.seat = pick;
			}
			this.dest = this.seat != null ? this.seat : home;
		}
		this.duration = 100000;
		return true;
	}

	@Override
	protected void onArrive(ServerLevel level) {
		if (this.sleeping) GnomeUtil.sleepAt(this.gnome, level, this.bed);
		else if (this.seat != null) GnomeUtil.sitAt(this.gnome, level, this.seat, null);
	}

	@Override
	protected void during(ServerLevel level) {
		if (this.gnome.hurtTime > 0) {         // wakker worden bij pijn
			this.ticks = this.duration;
			return;
		}
		if (this.gnome.tickCount % 40 == 0) {
			if (this.sleeping) GnomeUtil.sleepAt(this.gnome, level, this.bed);
			else if (this.seat != null) GnomeUtil.sitAt(this.gnome, level, this.seat, null);
		}
	}

	@Override
	protected void onEnd(ServerLevel level) {
		this.gnome.stopAnim();
		if (this.bed != null) Claims.release(level, this.bed, this.gnome.getId());
		if (this.seat != null) Claims.release(level, this.seat, this.gnome.getId());
		if (this.sleeping && this.stand != null) this.gnome.setPos(this.stand.getX() + 0.5, this.stand.getY(), this.stand.getZ() + 0.5);   // uit bed stappen
		this.bed = null;
		this.seat = null;
		this.sleeping = false;
	}
}
