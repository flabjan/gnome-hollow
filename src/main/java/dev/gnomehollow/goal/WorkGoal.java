package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import java.util.EnumSet;
import net.minecraft.core.BlockPos;
import dev.gnomehollow.ModSounds;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.world.entity.ai.goal.Goal;

/** Gemeenschappelijke basis: zoek werkplek, loop erheen, werk, wacht, herhaal. */
public abstract class WorkGoal extends Goal {
	protected final GnomeEntity gnome;
	protected BlockPos target;
	protected BlockPos stand;
	protected int ticks;
	private int cooldown;
	private boolean started;

	protected WorkGoal(GnomeEntity gnome) {
		this.gnome = gnome;
		this.cooldown = 40 + gnome.getRandom().nextInt(100);
		this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
	}

	/** Vul target en stand. Geef false als er niets te doen is. */
	protected abstract boolean findTarget(ServerLevel level);

	protected abstract int duration();

	protected abstract String animation();

	protected abstract void work(ServerLevel level, int t);

	protected double reach() {
		return 3.0;
	}

	protected int nextCooldown() {
		return 60 + this.gnome.getRandom().nextInt(80);
	}

	protected boolean targetStillValid(ServerLevel level) {
		return true;
	}

	protected void finish(ServerLevel level, boolean completed) {}

	/** Stemgeluid bij het begin van het werk (of null). */
	protected SoundEvent workSound() {
		return null;
	}

	/** Vrolijk geluidje als het werk helemaal af is. */
	protected boolean celebrates() {
		return true;
	}

	@Override
	public boolean canUse() {
		if (!(this.gnome.level() instanceof ServerLevel level)) return false;
		if (this.cooldown > 0) {
			this.cooldown--;
			return false;
		}
		if (!this.gnome.isWorkTime() || this.gnome.getTarget() != null || this.gnome.isTrading()) return false;
		this.cooldown = this.nextCooldown();
		return this.findTarget(level);
	}

	@Override
	public boolean canContinueToUse() {
		return this.ticks < this.duration() && this.gnome.getTarget() == null && this.gnome.isWorkTime()
				&& this.gnome.level() instanceof ServerLevel level && this.targetStillValid(level);
	}

	@Override
	public void start() {
		this.ticks = 0;
		this.started = false;
		this.gnome.getNavigation().moveTo(this.stand.getX() + 0.5, this.stand.getY(), this.stand.getZ() + 0.5, 0.7);
	}

	@Override
	public void tick() {
		if (!(this.gnome.level() instanceof ServerLevel level)) return;
		double dist = this.gnome.distanceToSqr(this.target.getX() + 0.5, this.target.getY() + 0.5, this.target.getZ() + 0.5);
		if (dist > this.reach() * this.reach()) {
			if (this.gnome.getNavigation().isDone()) {
				this.gnome.getNavigation().moveTo(this.stand.getX() + 0.5, this.stand.getY(), this.stand.getZ() + 0.5, 0.7);
				this.ticks++; // voorkomt eindeloos vastzitten
			}
			return;
		}
		this.gnome.getNavigation().stop();
		this.gnome.getLookControl().setLookAt(this.target.getX() + 0.5, this.target.getY() + 0.5, this.target.getZ() + 0.5);
		if (!this.started) {
			this.started = true;
			this.ticks = 0;
			this.gnome.startAnim(this.animation());
			if (this.gnome.getRandom().nextInt(3) == 0) this.gnome.voice(this.workSound(), 0.7F);
		}
		this.work(level, this.ticks);
		this.ticks++;
	}

	@Override
	public void stop() {
		this.gnome.stopAnim();
		if (this.gnome.level() instanceof ServerLevel level) {
			boolean completed = this.started && this.ticks >= this.duration();
			this.finish(level, completed);
			if (completed && this.celebrates() && this.gnome.getRandom().nextInt(4) == 0) this.gnome.voice(ModSounds.CELEBRATE, 0.7F);
		}
		this.started = false;
	}

	@Override
	public boolean requiresUpdateEveryTick() {
		return true;
	}
}
