package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import java.util.EnumSet;
import net.minecraft.world.entity.ai.goal.Goal;

/** Houdt gnomes in de buurt van hun huis: dwaalt een gnome te ver weg, dan loopt hij terug. */
public class StayNearHomeGoal extends Goal {
	private final GnomeEntity gnome;
	private final double maxDistance;

	public StayNearHomeGoal(GnomeEntity gnome, double maxDistance) {
		this.gnome = gnome;
		this.maxDistance = maxDistance;
		this.setFlags(EnumSet.of(Flag.MOVE));
	}

	private double distToHomeSqr() {
		var h = this.gnome.home();
		return h == null ? 0.0 : this.gnome.distanceToSqr(h.getX() + 0.5, h.getY(), h.getZ() + 0.5);
	}

	@Override
	public boolean canUse() {
		return this.gnome.home() != null && this.gnome.getTarget() == null
				&& this.distToHomeSqr() > this.maxDistance * this.maxDistance;
	}

	@Override
	public boolean canContinueToUse() {
		return this.gnome.getTarget() == null && !this.gnome.getNavigation().isDone() && this.distToHomeSqr() > 36.0;
	}

	@Override
	public void start() {
		var h = this.gnome.home();
		if (h != null) this.gnome.getNavigation().moveTo(h.getX() + 0.5, h.getY(), h.getZ() + 0.5, 0.8);
	}
}
