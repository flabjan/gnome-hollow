package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import java.util.EnumSet;
import net.minecraft.world.entity.ai.goal.Goal;

/** 's Nachts gaan gnomes (behalve de wachters) naar huis en blijven daar. */
public class NightHomeGoal extends Goal {
	private final GnomeEntity gnome;

	public NightHomeGoal(GnomeEntity gnome) {
		this.gnome = gnome;
		this.setFlags(EnumSet.of(Flag.MOVE));
	}

	private boolean farFromHome(double dist) {
		var h = this.gnome.home();
		return h != null && this.gnome.distanceToSqr(h.getX() + 0.5, h.getY(), h.getZ() + 0.5) > dist * dist;
	}

	@Override
	public boolean canUse() {
		return !this.gnome.isWorkTime() && this.gnome.getTarget() == null && this.farFromHome(4.0);
	}

	@Override
	public boolean canContinueToUse() {
		return !this.gnome.isWorkTime() && this.gnome.getTarget() == null && this.farFromHome(2.0);
	}

	@Override
	public void start() {
		this.moveHome();
	}

	@Override
	public void tick() {
		if (this.gnome.getNavigation().isDone()) this.moveHome();
	}

	private void moveHome() {
		var h = this.gnome.home();
		if (h != null) this.gnome.getNavigation().moveTo(h.getX() + 0.5, h.getY(), h.getZ() + 0.5, 0.7);
	}
}
