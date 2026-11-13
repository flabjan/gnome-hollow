package dev.gnomehollow.goal;

import dev.gnomehollow.GnomeConfig;
import dev.gnomehollow.entity.GnomeEntity;
import java.util.EnumSet;
import net.minecraft.core.BlockPos;
import net.minecraft.world.entity.ai.goal.Goal;

/** Gnomes blijven binnen de dorpsstraal; wie te ver weg dwaalt, loopt terug naar het dorp. */
public class StayNearVillageGoal extends Goal {
	private final GnomeEntity gnome;

	public StayNearVillageGoal(GnomeEntity gnome) {
		this.gnome = gnome;
		this.setFlags(EnumSet.of(Flag.MOVE));
	}

	private double limit() {
		return GnomeConfig.get().villageRadius;
	}

	@Override
	public boolean canUse() {
		return this.gnome.hasVillage() && this.gnome.getTarget() == null && this.gnome.distanceToVillageSqr() > this.limit() * this.limit();
	}

	@Override
	public boolean canContinueToUse() {
		double lim = this.limit() - 8.0;
		return this.gnome.getTarget() == null && !this.gnome.getNavigation().isDone() && this.gnome.distanceToVillageSqr() > lim * lim;
	}

	@Override
	public void start() {
		BlockPos c = this.gnome.villageCenter();
		BlockPos stand = GnomeUtil.findStandNear(this.gnome.level(), c).orElse(c);
		this.gnome.getNavigation().moveTo(stand.getX() + 0.5, stand.getY(), stand.getZ() + 0.5, 0.8);
	}
}
