package dev.gnomehollow.goal;

import dev.gnomehollow.ModSounds;
import dev.gnomehollow.entity.GnomeEntity;
import java.util.EnumSet;
import net.minecraft.world.entity.ai.goal.Goal;
import net.minecraft.world.entity.monster.Monster;

/** Niet-wachters vluchten naar huis zodra er een vijand in de buurt is en blijven daar tot het veilig is. */
public class SeekSafetyGoal extends Goal {
	private final GnomeEntity gnome;
	private int calmTicks;

	public SeekSafetyGoal(GnomeEntity gnome) {
		this.gnome = gnome;
		this.setFlags(EnumSet.of(Flag.MOVE));
	}

	private boolean monsterNear() {
		return !this.gnome.level().getEntitiesOfClass(Monster.class, this.gnome.getBoundingBox().inflate(11.0, 5.0, 11.0),
				m -> m.isAlive()).isEmpty();
	}

	@Override
	public boolean canUse() {
		if (!this.gnome.hasHome() || (this.gnome.tickCount + this.gnome.getId()) % 10 != 0) return false;
		return this.monsterNear();
	}

	@Override
	public boolean canContinueToUse() {
		return this.gnome.isAlive() && this.calmTicks < 100;
	}

	@Override
	public void start() {
		this.calmTicks = 0;
		this.gnome.markDanger(200);
		this.gnome.voice(ModSounds.ALERT, 1.0F);
		this.goHome();
	}

	private void goHome() {
		var h = this.gnome.home();
		if (h != null) this.gnome.getNavigation().moveTo(h.getX() + 0.5, h.getY(), h.getZ() + 0.5, 1.25);
	}

	@Override
	public void tick() {
		if (this.gnome.tickCount % 10 == 0) {
			if (this.monsterNear()) {
				this.calmTicks = 0;
				this.gnome.markDanger(200);
			} else {
				this.calmTicks += 10;
			}
		}
		var h = this.gnome.home();
		if (h != null && this.gnome.getNavigation().isDone()
				&& this.gnome.distanceToSqr(h.getX() + 0.5, h.getY(), h.getZ() + 0.5) > 6.0) {
			this.goHome();
		}
	}
}
