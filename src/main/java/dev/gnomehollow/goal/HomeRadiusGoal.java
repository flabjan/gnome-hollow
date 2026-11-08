package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import java.util.EnumSet;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.ai.goal.Goal;

/** Keeps a gnome near its original home position, replacing the removed Mob#restrictTo API. */
public final class HomeRadiusGoal extends Goal {
	private final GnomeEntity gnome;
	private final int radius;

	public HomeRadiusGoal(GnomeEntity gnome, int radius) {
		this.gnome = gnome;
		this.radius = radius;
		this.setFlags(EnumSet.of(Flag.MOVE));
	}

	@Override
	public boolean canUse() {
		return this.gnome.getTarget() == null && this.isOutside(this.radius);
	}

	@Override
	public boolean canContinueToUse() {
		return this.gnome.getTarget() == null && this.isOutside(Math.max(4, this.radius - 4));
	}

	@Override
	public void start() {
		this.moveHome();
	}

	@Override
	public void tick() {
		if (this.gnome.getNavigation().isDone()) {
			this.moveHome();
		}
	}

	private boolean isOutside(int distance) {
		BlockPos home = this.gnome.home();
		return home != null && this.gnome.distanceToSqr(home.getX() + 0.5, home.getY(), home.getZ() + 0.5) > (double) distance * distance;
	}

	private void moveHome() {
		BlockPos home = this.gnome.home();
		if (home != null) {
			this.gnome.getNavigation().moveTo(home.getX() + 0.5, home.getY(), home.getZ() + 0.5, 0.8);
		}
	}
}
