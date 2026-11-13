package dev.gnomehollow.goal;

import dev.gnomehollow.GnomeConfig;
import dev.gnomehollow.entity.GnomeEntity;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;

/** Wachters patrouilleren dynamisch langs willekeurige punten in het dorp (en blijven binnen de dorpsstraal). Dreiging gaat altijd voor. */
public class GuardPatrolGoal extends ActivityGoal {
	public GuardPatrolGoal(GnomeEntity gnome) {
		super(gnome, 100);
	}

	@Override
	protected boolean allowed() {
		return GnomeConfig.get().guardsPatrol && this.gnome.hasVillage() && this.gnome.getTarget() == null
				&& !this.gnome.isTrading() && !this.gnome.shouldShelter();
	}

	@Override
	protected int nextCooldown() {
		return 40 + this.gnome.getRandom().nextInt(160);
	}

	@Override
	protected double speed() {
		return 0.55;
	}

	@Override
	protected boolean choose(ServerLevel level) {
		var rnd = this.gnome.getRandom();
		BlockPos c = this.gnome.villageCenter();
		double max = Math.min(GnomeConfig.get().villageRadius - 8.0, 28.0);
		for (int tries = 0; tries < 6; tries++) {
			double a = rnd.nextDouble() * Math.PI * 2.0;
			double d = 5.0 + rnd.nextDouble() * Math.max(4.0, max - 5.0);
			int x = c.getX() + (int) Math.round(Math.cos(a) * d);
			int z = c.getZ() + (int) Math.round(Math.sin(a) * d);
			if (!level.hasChunkAt(new BlockPos(x, c.getY(), z))) continue;
			for (int dy = 5; dy >= -6; dy--) {
				BlockPos p = new BlockPos(x, c.getY() + dy, z);
				if (GnomeUtil.isStandable(level, p)) {
					this.dest = p;
					this.duration = 60 + rnd.nextInt(140);
					return true;
				}
			}
		}
		return false;
	}

	@Override
	protected void during(ServerLevel level) {
		if (this.ticks % 60 == 0) {
			double a = this.gnome.getRandom().nextDouble() * Math.PI * 2.0;
			this.gnome.getLookControl().setLookAt(this.gnome.getX() + Math.cos(a) * 6, this.gnome.getEyeY(), this.gnome.getZ() + Math.sin(a) * 6);
		}
	}
}
