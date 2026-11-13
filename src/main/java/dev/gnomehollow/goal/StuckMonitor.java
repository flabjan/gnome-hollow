package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;

/** Merkt dat een gnome niet meer vooruit komt (blijft ~8 seconden op dezelfde plek terwijl hij zou moeten lopen). */
public final class StuckMonitor {
	private double lastX, lastZ;
	private int count, tick;

	public void reset(GnomeEntity g) {
		this.lastX = g.getX();
		this.lastZ = g.getZ();
		this.count = 0;
		this.tick = 0;
	}

	public boolean check(GnomeEntity g) {
		if (++this.tick % 40 != 0) return false;
		double dx = g.getX() - this.lastX, dz = g.getZ() - this.lastZ;
		this.lastX = g.getX();
		this.lastZ = g.getZ();
		if (dx * dx + dz * dz < 0.04) this.count++;
		else this.count = 0;
		return this.count >= 4;
	}
}
