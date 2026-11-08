package dev.gnomehollow.goal;

import dev.gnomehollow.entity.GnomeEntity;
import java.util.EnumSet;
import dev.gnomehollow.ModSounds;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundEvents;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.ai.goal.Goal;

/** Nitwit: speelt muziek (pentatonisch, dus het klinkt altijd leuk). Andere nitwits in de buurt doen mee. */
public class MusicGoal extends Goal {
	private static final int[] SCALE = {0, 3, 5, 7, 10, 12, 15, 17, 19, 22};
	private final GnomeEntity gnome;
	private int remaining;

	public MusicGoal(GnomeEntity gnome) {
		this.gnome = gnome;
		this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
	}

	private boolean othersPlayingNearby() {
		return !this.gnome.level().getEntitiesOfClass(GnomeEntity.class, this.gnome.getBoundingBox().inflate(10.0),
				g -> g != this.gnome && g.isPlayingMusic()).isEmpty();
	}

	@Override
	public boolean canUse() {
		if (!this.gnome.isWorkTime() || this.gnome.getTarget() != null) return false;
		var rnd = this.gnome.getRandom();
		return rnd.nextInt(220) == 0 || (rnd.nextInt(30) == 0 && this.othersPlayingNearby());
	}

	@Override
	public boolean canContinueToUse() {
		return this.remaining > 0 && this.gnome.getTarget() == null && this.gnome.isWorkTime();
	}

	@Override
	public void start() {
		this.remaining = 200 + this.gnome.getRandom().nextInt(300);
		this.gnome.setPlayingMusic(true);
		this.gnome.getNavigation().stop();
		this.gnome.startAnim("play");
		this.gnome.voice(ModSounds.LAUGH, 0.9F);
	}

	@Override
	public void tick() {
		this.remaining--;
		if (this.remaining % 12 == 0 && this.gnome.level() instanceof ServerLevel level) {
			int note = SCALE[this.gnome.getRandom().nextInt(SCALE.length)];
			float pitch = (float) Math.pow(2.0, (note - 12) / 12.0);
			SoundEvent sound = switch (this.gnome.getId() % 3) {
				case 0 -> SoundEvents.NOTE_BLOCK_FLUTE.value();
				case 1 -> SoundEvents.NOTE_BLOCK_BANJO.value();
				default -> SoundEvents.NOTE_BLOCK_BELL.value();
			};
			level.playSound(null, this.gnome.blockPosition(), sound, SoundSource.NEUTRAL, 1.0F, pitch);
			level.sendParticles(ParticleTypes.NOTE, this.gnome.getX(), this.gnome.getY() + 1.3, this.gnome.getZ(), 1,
					0.0, 0.0, 0.0, note / 24.0);
		}
	}

	@Override
	public void stop() {
		this.gnome.setPlayingMusic(false);
		this.gnome.stopAnim();
	}
}
