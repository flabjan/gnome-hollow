package dev.gnomehollow.goal;

import dev.gnomehollow.ModSounds;
import dev.gnomehollow.entity.GnomeEntity;
import dev.gnomehollow.entity.Profession;
import java.util.EnumSet;
import java.util.List;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;
import net.minecraft.world.entity.ai.goal.Goal;

/**
 * Samen muziek maken, zoals bij de Ribbits: een Nitwit begint een liedje en andere gnomes die toevallig niets
 * te doen hebben komen erbij zitten (fluit, luit, bas, ritme). Werk in hun beroep gaat altijd voor
 * (WorkGoal heeft een hogere prioriteit en onderbreekt dit doel).
 */
public class MusicGoal extends Goal {
	private static final int MAX_MUSICIANS = 4;
	private final GnomeEntity gnome;
	private GnomeEntity leader;

	public MusicGoal(GnomeEntity gnome) {
		this.gnome = gnome;
		this.setFlags(EnumSet.of(Flag.MOVE, Flag.LOOK));
	}

	private List<GnomeEntity> musicians() {
		return this.gnome.level().getEntitiesOfClass(GnomeEntity.class, this.gnome.getBoundingBox().inflate(14.0, 4.0, 14.0),
				g -> g != this.gnome && g.isPlayingMusic());
	}

	@Override
	public boolean canUse() {
		if (!this.gnome.isWorkTime() || this.gnome.getTarget() != null || this.gnome.isTrading()) return false;
		if (this.gnome.tickCount % 10 != this.gnome.getId() % 10) return false;
		var rnd = this.gnome.getRandom();
		List<GnomeEntity> others = this.musicians();
		if (!others.isEmpty()) {
			return others.size() < MAX_MUSICIANS && rnd.nextInt(5) == 0;
		}
		return this.gnome.profession() == Profession.NITWIT && rnd.nextInt(120) == 0;
	}

	@Override
	public boolean canContinueToUse() {
		return this.gnome.isAlive() && this.gnome.isWorkTime() && this.gnome.getTarget() == null && !this.gnome.isTrading()
				&& this.gnome.level().getGameTime() < this.gnome.musicEnd();
	}

	@Override
	public void start() {
		long now = this.gnome.level().getGameTime();
		List<GnomeEntity> others = this.musicians();
		if (others.isEmpty()) {
			this.leader = null;
			this.gnome.setMusic(this.gnome.getRandom().nextInt(Songs.ALL.length), 0, now + 240 + this.gnome.getRandom().nextInt(240));
		} else {
			this.leader = others.get(0);
			boolean[] used = new boolean[MAX_MUSICIANS];
			for (GnomeEntity o : others) {
				if (o.musicPart() < MAX_MUSICIANS) used[o.musicPart()] = true;
			}
			int part = 0;
			while (part < MAX_MUSICIANS - 1 && used[part]) part++;
			this.gnome.setMusic(this.leader.musicSong(), part, this.leader.musicEnd());
		}
		this.gnome.setPlayingMusic(true);
		this.gnome.startAnim("play");
	}

	@Override
	public void tick() {
		if (!(this.gnome.level() instanceof ServerLevel level)) return;
		if (this.leader != null && this.leader.isAlive()) {
			if (this.gnome.distanceToSqr(this.leader) > 16.0) {
				this.gnome.getNavigation().moveTo(this.leader, 0.6);
			} else {
				this.gnome.getNavigation().stop();
			}
			this.gnome.getLookControl().setLookAt(this.leader);
		} else {
			this.gnome.getNavigation().stop();
		}

		Songs.Song song = Songs.ALL[this.gnome.musicSong()];
		long t = level.getGameTime();
		if (t % song.stepTicks() != 0) return;
		int step = (int) ((t / song.stepTicks()) % song.length());
		switch (this.gnome.musicPart()) {
			case 0 -> this.note(level, ModSounds.MUSIC_WHISTLE, song.melody()[step], 0.8F);
			case 1 -> this.note(level, ModSounds.MUSIC_LUTE, song.harmony()[step], 0.7F);
			case 2 -> this.note(level, ModSounds.MUSIC_BASS, song.bass()[step], 0.8F);
			default -> {
				char c = song.rhythm().charAt(step % song.rhythm().length());
				if (c == 'D') level.playSound(null, this.gnome.blockPosition(), ModSounds.MUSIC_DRUM, SoundSource.NEUTRAL, 0.7F, 1.0F);
				else if (c == 't') level.playSound(null, this.gnome.blockPosition(), ModSounds.MUSIC_TAP, SoundSource.NEUTRAL, 0.5F, 1.0F);
			}
		}
	}

	private void note(ServerLevel level, SoundEvent sound, int semitones, float volume) {
		if (semitones == Songs.R) return;
		float pitch = (float) Math.pow(2.0, semitones / 12.0);
		pitch = Math.max(0.5F, Math.min(2.0F, pitch));
		level.playSound(null, this.gnome.blockPosition(), sound, SoundSource.NEUTRAL, volume, pitch);
		if (this.gnome.getRandom().nextInt(4) == 0) {
			level.sendParticles(ParticleTypes.NOTE, this.gnome.getX(), this.gnome.getY() + 1.3, this.gnome.getZ(), 1,
					0.0, 0.0, 0.0, (semitones + 12) / 24.0);
		}
	}

	@Override
	public void stop() {
		this.leader = null;
		this.gnome.setPlayingMusic(false);
		this.gnome.stopAnim();
	}
}
