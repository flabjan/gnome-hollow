package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import java.util.EnumSet;
import net.minecraft.core.BlockPos;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.world.entity.ai.goal.Goal;

/**
 * Basis voor tijdelijke bezigheden: kies een bestemming, loop erheen (met 'vast'-detectie en time-out),
 * doe iets, en rust daarna uit. Subklassen vullen alleen de details in.
 */
public abstract class ActivityGoal extends Goal {
	protected final GnomeEntity gnome;
	protected BlockPos dest;
	protected int ticks;
	protected int duration = 200;
	protected boolean arrived;
	private int walkTicks;
	private int cooldown;
	private final StuckMonitor stuck = new StuckMonitor();

	protected ActivityGoal(GnomeEntity gnome, int initialCooldown) {
		this.gnome = gnome;
		this.cooldown = initialCooldown + gnome.getRandom().nextInt(initialCooldown + 1);
		this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
	}

	/** Kies dest en duration. Geef false als er niets te doen is. */
	protected abstract boolean choose(ServerLevel level);

	protected boolean allowed() {
		return this.gnome.canLeisure();
	}

	protected int nextCooldown() {
		return 400 + this.gnome.getRandom().nextInt(800);
	}

	protected double arriveDist() {
		return 1.6;
	}

	protected double speed() {
		return 0.6;
	}

	/** Moet er gelopen worden? (Luisteraars en dergelijke staan al op hun plek.) */
	protected boolean needsWalk() {
		return true;
	}

	protected void refreshDest() {}

	protected void onArrive(ServerLevel level) {}

	protected void during(ServerLevel level) {}

	protected void onEnd(ServerLevel level) {}

	@Override
	public boolean canUse() {
		if (!(this.gnome.level() instanceof ServerLevel level) || !this.gnome.isAlive()) return false;
		if (this.cooldown > 0) {
			this.cooldown--;
			return false;
		}
		if (!this.allowed()) {
			this.cooldown = 40;
			return false;
		}
		if (this.choose(level)) return true;
		this.cooldown = 60;
		return false;
	}

	@Override
	public boolean canContinueToUse() {
		return this.gnome.isAlive() && this.ticks < this.duration && this.allowed();
	}

	@Override
	public void start() {
		this.ticks = 0;
		this.walkTicks = 0;
		this.arrived = false;
		this.stuck.reset(this.gnome);
		if (!this.needsWalk() || this.dest == null) {
			this.arrived = true;
			if (this.gnome.level() instanceof ServerLevel level) this.onArrive(level);
		} else {
			this.walk();
		}
	}

	protected void walk() {
		if (this.dest != null) {
			this.gnome.getNavigation().moveTo(this.dest.getX() + 0.5, this.dest.getY(), this.dest.getZ() + 0.5, this.speed());
		}
	}

	@Override
	public void tick() {
		if (!(this.gnome.level() instanceof ServerLevel level)) return;
		if (!this.arrived) {
			this.refreshDest();
			double d = this.gnome.distanceToSqr(this.dest.getX() + 0.5, this.dest.getY(), this.dest.getZ() + 0.5);
			double ad = this.arriveDist();
			if (d <= ad * ad) {
				this.arrived = true;
				this.gnome.getNavigation().stop();
				this.onArrive(level);
			} else {
				if (this.gnome.getNavigation().isDone()) this.walk();
				if (++this.walkTicks > 600 || this.stuck.check(this.gnome)) this.ticks = this.duration;   // opgeven
			}
		} else {
			this.ticks++;
			this.during(level);
		}
	}

	@Override
	public void stop() {
		if (this.gnome.level() instanceof ServerLevel level) this.onEnd(level);
		this.cooldown = this.nextCooldown();
		this.dest = null;
	}

	@Override
	public boolean requiresUpdateEveryTick() {
		return true;
	}
}
