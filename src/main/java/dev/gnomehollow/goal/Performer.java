package dev.gnomehollow.goal;

import dev.gnomehollow.ModSounds;
import dev.gnomehollow.entity.GnomeEntity;
import dev.gnomehollow.village.MusicSessions;
import net.minecraft.core.particles.ParticleTypes;
import net.minecraft.server.level.ServerLevel;
import net.minecraft.sounds.SoundEvent;
import net.minecraft.sounds.SoundSource;

/** Eén muzikant in een sessie: houdt zijn deel bij, laat het juiste instrument zien en speelt in de maat van de sessie. */
public final class Performer {
	private MusicSessions.Session session;
	private int part = -1;

	public boolean active() {
		return this.part >= 0 && this.session != null;
	}

	public MusicSessions.Session session() {
		return this.session;
	}

	public boolean tryJoin(GnomeEntity g, MusicSessions.Session s) {
		int p = s.takePart(g.instrument());
		if (p < 0) return false;
		this.session = s;
		this.part = p;
		g.startAnim(g.instrumentAnim(p));   // dezelfde stem als het instrument dat hij hoort te vasthouden
		return true;
	}

	/** Speelt de noot van dit moment. Geeft false zodra de sessie voorbij is. */
	public boolean play(ServerLevel level, GnomeEntity g) {
		if (!this.active()) return false;
		long t = level.getGameTime();
		if (t >= this.session.end) return false;
		if (t < this.session.start) return true;
		Songs.Song song = Songs.ALL[this.session.song];
		long rel = t - this.session.start;
		if (rel % song.stepTicks() != 0) return true;
		int step = (int) ((rel / song.stepTicks()) % song.length());
		switch (this.part) {
			case 0 -> this.note(level, g, ModSounds.MUSIC_WHISTLE, song.melody()[step], 0.8F);
			case 1 -> this.note(level, g, ModSounds.MUSIC_LUTE, song.harmony()[step], 0.7F);
			case 2 -> this.note(level, g, ModSounds.MUSIC_BASS, song.bass()[step], 0.8F);
			default -> {
				char c = song.rhythm().charAt(step % song.rhythm().length());
				if (c == 'D') level.playSound(null, g.blockPosition(), ModSounds.MUSIC_DRUM, SoundSource.NEUTRAL, 0.7F, 1.0F);
				else if (c == 't') level.playSound(null, g.blockPosition(), ModSounds.MUSIC_TAP, SoundSource.NEUTRAL, 0.5F, 1.0F);
			}
		}
		return true;
	}

	private void note(ServerLevel level, GnomeEntity g, SoundEvent sound, int semitones, float volume) {
		if (semitones == Songs.R) return;
		float pitch = Math.max(0.5F, Math.min(2.0F, (float) Math.pow(2.0, semitones / 12.0)));
		level.playSound(null, g.blockPosition(), sound, SoundSource.NEUTRAL, volume, pitch);
		if (g.getRandom().nextInt(4) == 0) {
			level.sendParticles(ParticleTypes.NOTE, g.getX(), g.getY() + 1.4, g.getZ(), 1, 0.0, 0.0, 0.0, (semitones + 12) / 24.0);
		}
	}

	public void leave(GnomeEntity g) {
		if (this.session != null) this.session.release(this.part);
		boolean was = this.active();
		this.session = null;
		this.part = -1;
		if (was) g.stopAnim();
	}
}
